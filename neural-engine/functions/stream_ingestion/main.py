"""Cloud Function for Neural Data Stream Ingestion."""

import functions_framework
import json
import base64
from datetime import datetime
import numpy as np
import logging
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.ingestion import NeuralDataIngestion
from src.ingestion.data_types import (
    NeuralDataPacket,
    NeuralSignalType,
    DataSource,
    DeviceInfo,
    ChannelInfo,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize ingestion system (reused across invocations)
PROJECT_ID = os.environ.get("GCP_PROJECT", "neurascale")
ingestion = None


def get_ingestion_instance():
    """Get or create the ingestion instance."""
    global ingestion
    if ingestion is None:
        ingestion = NeuralDataIngestion(
            project_id=PROJECT_ID,
            enable_pubsub=True,
            enable_bigtable=True,
        )
    return ingestion


@functions_framework.cloud_event
async def process_neural_stream(cloud_event):
    """
    Process neural data stream from Pub/Sub.

    Expected message format:
    {
        "device_id": "device_001",
        "device_type": "OpenBCI",
        "signal_type": "eeg",
        "source": "openbci",
        "session_id": "session_001",
        "subject_id": "patient_001",
        "timestamp": "2024-01-01T12:00:00Z",
        "sampling_rate": 256.0,
        "data": [[...], [...]],  # 2D array: channels x samples
        "channels": [
            {"channel_id": 0, "label": "Ch1", "unit": "microvolts"},
            ...
        ]
    }
    """
    try:
        # Decode the Pub/Sub message
        message = base64.b64decode(cloud_event.data["message"]["data"]).decode()
        data = json.loads(message)

        # Log receipt
        logger.info(f"Received data from device {data['device_id']}")

        # Create device info
        channels = [
            ChannelInfo(
                channel_id=ch["channel_id"],
                label=ch["label"],
                unit=ch.get("unit", "microvolts"),
                sampling_rate=data["sampling_rate"],
            )
            for ch in data.get("channels", [])
        ]

        device_info = DeviceInfo(
            device_id=data["device_id"],
            device_type=data["device_type"],
            channels=channels,
        )

        # Convert data to numpy array
        neural_data = np.array(data["data"])

        # Create packet
        packet = NeuralDataPacket(
            timestamp=datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00")),
            data=neural_data,
            signal_type=NeuralSignalType(data["signal_type"]),
            source=DataSource(data["source"]),
            device_info=device_info,
            session_id=data["session_id"],
            subject_id=data.get("subject_id"),
            sampling_rate=data["sampling_rate"],
            data_quality=data.get("data_quality", 0.95),
        )

        # Get ingestion instance
        ing = get_ingestion_instance()

        # Ingest packet
        success = await ing.ingest_packet(packet)

        if success:
            logger.info(f"Successfully ingested packet from {data['device_id']}")
            return {"status": "success", "device_id": data["device_id"]}
        else:
            logger.error(f"Failed to ingest packet from {data['device_id']}")
            return {"status": "error", "device_id": data["device_id"]}, 500

    except Exception as e:
        logger.error(f"Error processing neural stream: {e}")
        return {"status": "error", "message": str(e)}, 500


@functions_framework.http
async def ingest_batch(request):
    """
    HTTP endpoint for batch neural data ingestion.

    Accepts POST requests with JSON body containing an array of packets.
    """
    try:
        # Parse request
        request_json = request.get_json()
        if not request_json or "packets" not in request_json:
            return {"error": "Missing 'packets' in request body"}, 400

        # Get ingestion instance
        ing = get_ingestion_instance()

        # Process each packet
        results = []
        for packet_data in request_json["packets"]:
            try:
                # Create device info
                channels = [
                    ChannelInfo(
                        channel_id=ch["channel_id"],
                        label=ch["label"],
                        unit=ch.get("unit", "microvolts"),
                        sampling_rate=packet_data["sampling_rate"],
                    )
                    for ch in packet_data.get("channels", [])
                ]

                device_info = DeviceInfo(
                    device_id=packet_data["device_id"],
                    device_type=packet_data["device_type"],
                    channels=channels,
                )

                # Convert data to numpy array
                neural_data = np.array(packet_data["data"])

                # Create packet
                packet = NeuralDataPacket(
                    timestamp=datetime.fromisoformat(
                        packet_data["timestamp"].replace("Z", "+00:00")
                    ),
                    data=neural_data,
                    signal_type=NeuralSignalType(packet_data["signal_type"]),
                    source=DataSource(packet_data["source"]),
                    device_info=device_info,
                    session_id=packet_data["session_id"],
                    subject_id=packet_data.get("subject_id"),
                    sampling_rate=packet_data["sampling_rate"],
                    data_quality=packet_data.get("data_quality", 0.95),
                )

                # Ingest packet
                success = await ing.ingest_packet(packet)
                results.append({
                    "device_id": packet_data["device_id"],
                    "timestamp": packet_data["timestamp"],
                    "success": success,
                })

            except Exception as e:
                results.append({
                    "device_id": packet_data.get("device_id", "unknown"),
                    "timestamp": packet_data.get("timestamp", "unknown"),
                    "success": False,
                    "error": str(e),
                })

        # Return results
        successful = sum(1 for r in results if r["success"])
        return {
            "status": "completed",
            "total": len(results),
            "successful": successful,
            "failed": len(results) - successful,
            "results": results,
        }

    except Exception as e:
        logger.error(f"Error in batch ingestion: {e}")
        return {"error": str(e)}, 500
