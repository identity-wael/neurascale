"""Base processor for neural data Cloud Functions."""

import base64
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any

import functions_framework
from google.cloud import bigtable
from google.cloud import monitoring_v3
from google.cloud import error_reporting
import numpy as np

# Set up logging
logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

# Initialize clients
error_client = error_reporting.Client()
monitoring_client = monitoring_v3.MetricServiceClient()

# Environment variables
PROJECT_ID = os.environ.get("PROJECT_ID")
ENVIRONMENT = os.environ.get("ENVIRONMENT")
SIGNAL_TYPE = os.environ.get("SIGNAL_TYPE")
BIGTABLE_INSTANCE = os.environ.get("BIGTABLE_INSTANCE")


class NeuralDataProcessor:
    """Base class for processing neural data."""

    def __init__(self, signal_type: str):
        self.signal_type = signal_type
        self.bigtable_client = bigtable.Client(project=PROJECT_ID)
        self.instance = self.bigtable_client.instance(BIGTABLE_INSTANCE)
        self.time_series_table = self.instance.table("neural - time - series")
        self.sessions_table = self.instance.table("neural - sessions")
        self.devices_table = self.instance.table("neural - devices")

        # Signal - specific configuration
        self.config = self.get_signal_config(signal_type)

    def get_signal_config(self, signal_type: str) -> Dict[str, Any]:
        """Get configuration for specific signal types."""
        configs = {
            "eeg": {
                "sampling_rate": 250,
                "channels": 32,
                "voltage_range": (-100, 100),
                "filter_settings": {
                    "highpass": 0.5,
                    "lowpass": 100,
                    "notch": [50, 60],  # 50Hz for Europe, 60Hz for US
                },
            },
            "ecog": {
                "sampling_rate": 1000,
                "channels": 128,
                "voltage_range": (-500, 500),
                "filter_settings": {"highpass": 1, "lowpass": 300, "notch": [50, 60]},
            },
            "lfp": {
                "sampling_rate": 1000,
                "channels": 16,
                "voltage_range": (-1000, 1000),
                "filter_settings": {"highpass": 0.1, "lowpass": 300, "notch": [50, 60]},
            },
            "spikes": {
                "sampling_rate": 30000,
                "channels": 96,
                "voltage_range": (-200, 200),
                "filter_settings": {"highpass": 300, "lowpass": 5000, "notch": None},
            },
            "emg": {
                "sampling_rate": 1000,
                "channels": 8,
                "voltage_range": (-5000, 5000),
                "filter_settings": {"highpass": 20, "lowpass": 450, "notch": [50, 60]},
            },
            "accelerometer": {
                "sampling_rate": 100,
                "channels": 3,
                "voltage_range": (-16, 16),  # ±16g range
                "filter_settings": {"highpass": 0.1, "lowpass": 40, "notch": None},
            },
        }

        return configs.get(signal_type, configs["eeg"])

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate incoming neural data."""
        required_fields = ["session_id", "device_id", "timestamp", "data", "channel"]

        for field in required_fields:
            if field not in data:
                logger.error(f"Missing required field: {field}")
                return False

        # Check data dimensions
        neural_data = np.array(data["data"])
        if neural_data.shape[0] == 0:
            logger.error("Empty data array")
            return False

        # Check voltage range
        min_val, max_val = self.config["voltage_range"]
        if np.any(neural_data < min_val) or np.any(neural_data > max_val):
            logger.warning(f"Data outside expected range: [{min_val}, {max_val}]")

        return True

    def preprocess_data(self, data: np.ndarray) -> np.ndarray:
        """Apply basic preprocessing to neural data."""
        # Remove DC offset
        data = data - np.mean(data)

        # Apply basic artifact rejection
        if self.signal_type != "accelerometer":
            # Z - score based artifact detection
            z_scores = np.abs((data - np.mean(data)) / np.std(data))
            artifact_mask = z_scores > 5  # 5 standard deviations

            if np.any(artifact_mask):
                logger.info(f"Detected {np.sum(artifact_mask)} artifact samples")
                # Simple interpolation for artifacts
                data[artifact_mask] = np.interp(
                    np.where(artifact_mask)[0],
                    np.where(~artifact_mask)[0],
                    data[~artifact_mask],
                )

        return data

    def extract_features(self, data: np.ndarray) -> Dict[str, float]:
        """Extract basic features from neural data."""
        features = {
            "mean": float(np.mean(data)),
            "std": float(np.std(data)),
            "min": float(np.min(data)),
            "max": float(np.max(data)),
            "rms": float(np.sqrt(np.mean(data**2))),
        }

        # Signal - specific features
        if self.signal_type in ["eeg", "ecog", "lfp"]:
            # Add frequency domain features (simplified)
            fft_vals = np.fft.fft(data)
            power_spectrum = np.abs(fft_vals[: len(fft_vals) // 2]) ** 2
            features["total_power"] = float(np.sum(power_spectrum))

        elif self.signal_type == "accelerometer":
            # Add motion - specific features
            features["magnitude"] = float(np.sqrt(np.sum(data**2)))

        return features

    def store_in_bigtable(self, processed_data: Dict[str, Any]) -> bool:
        """Store processed data in Bigtable."""
        try:
            # Create row key: session_id#timestamp#channel
            row_key = f"{processed_data['session_id']}#{processed_data['timestamp']}#{processed_data['channel']}"

            row = self.time_series_table.direct_row(row_key.encode())

            # Store raw data
            row.set_cell(
                "data",
                "raw",
                json.dumps(
                    processed_data["data"].tolist()
                    if isinstance(processed_data["data"], np.ndarray)
                    else processed_data["data"]
                ),
                timestamp=datetime.utcnow(),
            )

            # Store metadata
            metadata = {
                "device_id": processed_data["device_id"],
                "signal_type": self.signal_type,
                "sampling_rate": self.config["sampling_rate"],
                "quality_score": processed_data.get("quality_score", 1.0),
            }

            row.set_cell(
                "metadata", "info", json.dumps(metadata), timestamp=datetime.utcnow()
            )

            # Store features if available
            if "features" in processed_data:
                row.set_cell(
                    "data",
                    "features",
                    json.dumps(processed_data["features"]),
                    timestamp=datetime.utcnow(),
                )

            row.commit()
            return True

        except Exception as e:
            logger.error(f"Error storing in Bigtable: {str(e)}")
            error_client.report_exception()
            return False

    def send_metrics(self, processing_time: float, success: bool) -> None:
        """Send custom metrics to Cloud Monitoring."""
        try:
            project_name = f"projects/{PROJECT_ID}"

            series = monitoring_v3.TimeSeries()
            series.metric.type = (
                f"custom.googleapis.com / neural/{self.signal_type}/processing_time"
            )
            series.metric.labels["environment"] = ENVIRONMENT
            series.metric.labels["success"] = str(success).lower()

            series.resource.type = "cloud_function"
            series.resource.labels["function_name"] = (
                f"process - neural-{self.signal_type}-{ENVIRONMENT}"
            )
            series.resource.labels["region"] = os.environ.get(
                "FUNCTION_REGION", "us - central1"
            )

            now = datetime.utcnow()
            interval = monitoring_v3.TimeInterval(
                {"end_time": {"seconds": int(now.timestamp())}}
            )

            point = monitoring_v3.Point(
                {"interval": interval, "value": {"double_value": processing_time}}
            )

            series.points = [point]

            monitoring_client.create_time_series(
                name=project_name, time_series=[series]
            )

        except Exception as e:
            logger.error(f"Error sending metrics: {str(e)}")

    def process(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main processing function."""
        start_time = datetime.utcnow()
        success = False

        try:
            # Validate data
            if not self.validate_data(message_data):
                raise ValueError("Invalid data format")

            # Extract and preprocess data
            raw_data = np.array(message_data["data"])
            processed_data = self.preprocess_data(raw_data)

            # Extract features
            features = self.extract_features(processed_data)

            # Prepare for storage
            storage_data = {
                **message_data,
                "data": processed_data,
                "features": features,
                "processed_at": datetime.utcnow().isoformat(),
            }

            # Store in Bigtable
            if self.store_in_bigtable(storage_data):
                success = True
                logger.info(
                    f"Successfully processed {self.signal_type} data for session {message_data['session_id']}"
                )

            return {
                "success": success,
                "session_id": message_data["session_id"],
                "features": features,
            }

        except Exception as e:
            logger.error(f"Processing error: {str(e)}")
            error_client.report_exception()
            return {"success": False, "error": str(e)}

        finally:
            # Send metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self.send_metrics(processing_time, success)


@functions_framework.cloud_event  # type: ignore
def process_neural_stream(cloud_event: Any) -> None:
    """Cloud Function entry point for processing neural data streams."""
    # Extract message data
    message = cloud_event.data["message"]
    message_data = base64.b64decode(message["data"]).decode()

    try:
        # Parse JSON data
        data = json.loads(message_data)

        # Initialize processor
        if SIGNAL_TYPE is None:
            raise ValueError("SIGNAL_TYPE environment variable not set")
        processor = NeuralDataProcessor(SIGNAL_TYPE)

        # Process data
        result = processor.process(data)

        logger.info(f"Processing result: {result}")

    except Exception as e:
        logger.error(f"Fatal error in cloud function: {str(e)}")
        error_client.report_exception()
        raise
