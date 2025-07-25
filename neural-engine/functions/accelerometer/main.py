"""Cloud Function for processing accelerometer data streams."""

import sys
import os
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_processor import NeuralDataProcessor  # noqa: E402
import numpy as np  # noqa: E402
from typing import Any, Dict  # noqa: E402

logger = logging.getLogger(__name__)


class AccelerometerProcessor(NeuralDataProcessor):
    """Specialized processor for accelerometer data."""

    def __init__(self) -> None:
        super().__init__('accelerometer')

    def calculate_movement_metrics(self, data: np.ndarray) -> dict:
        """Calculate movement - related metrics from accelerometer data."""
        # Assuming 3 - axis data (x, y, z)
        # If data is 1D, treat as magnitude
        if data.ndim == 1:
            magnitude = np.abs(data)
        else:
            # Calculate magnitude from 3 axes
            magnitude = np.sqrt(np.sum(data**2, axis=1))

        # Remove gravity component (assuming 1g baseline)
        magnitude_no_gravity = magnitude - 9.81

        # Calculate metrics
        metrics = {
            'mean_acceleration': float(np.mean(magnitude)),
            'peak_acceleration': float(np.max(magnitude)),
            'movement_intensity': float(np.std(magnitude)),
            'step_count_estimate': self.estimate_steps(magnitude_no_gravity)
        }

        # Detect periods of activity
        activity_threshold = 0.5  # m / s^2
        active_samples = magnitude_no_gravity > activity_threshold
        metrics['activity_percentage'] = float(np.sum(active_samples) / len(active_samples) * 100)

        return metrics

    def estimate_steps(self, magnitude: np.ndarray) -> int:
        """Simple step counting algorithm."""
        # Basic peak detection for step counting
        # More sophisticated algorithms would use adaptive thresholds
        from scipy.signal import find_peaks

        # Find peaks with minimum height and distance
        peaks, _ = find_peaks(
            magnitude,
            height=1.0,  # Minimum acceleration for a step
            distance=int(0.3 * self.config['sampling_rate'])  # Minimum 300ms between steps
        )

        return len(peaks)

    def extract_features(self, data: np.ndarray) -> Dict[str, Any]:
        """Extract accelerometer - specific features."""
        features: Dict[str, Any] = super().extract_features(data)

        # Add movement metrics
        movement_metrics = self.calculate_movement_metrics(data)
        features.update(movement_metrics)

        # Add orientation features if 3 - axis data
        if data.ndim > 1 and data.shape[1] >= 3:
            # Estimate tilt angles
            mean_x = np.mean(data[:, 0])
            mean_y = np.mean(data[:, 1])
            mean_z = np.mean(data[:, 2])

            features['tilt_x'] = float(np.arctan2(mean_x, np.sqrt(mean_y**2 + mean_z**2)) * 180 / np.pi)
            features['tilt_y'] = float(np.arctan2(mean_y, np.sqrt(mean_x**2 + mean_z**2)) * 180 / np.pi)

        return features


# Override to use AccelerometerProcessor
def process_neural_stream(cloud_event: Any) -> None:
    """Cloud Function entry point for processing accelerometer data streams."""
    import base64
    import json
    from google.cloud import error_reporting

    error_client = error_reporting.Client()

    message = cloud_event.data["message"]
    message_data = base64.b64decode(message["data"]).decode()

    try:
        data = json.loads(message_data)
        processor = AccelerometerProcessor()
        result = processor.process(data)
        logger.info(f"Accelerometer processing result: {result}")

    except Exception as e:
        logger.error(f"Fatal error in accelerometer cloud function: {str(e)}")
        error_client.report_exception()
        raise
