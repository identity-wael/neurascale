"""Cloud Function for Neural Data Stream Ingestion."""

import functions_framework
import json
import base64
from datetime import datetime
import logging
import os
# from google.cloud import pubsub_v1  # Unused import
from google.cloud import bigtable
# from google.cloud.bigtable import column_family  # Unused import
# from google.cloud.bigtable import row_filters  # Unused import
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
PROJECT_ID = os.environ.get('GCP_PROJECT', 'staging-neurascale')
ENVIRONMENT = os.environ.get('ENVIRONMENT', 'staging')
BIGTABLE_INSTANCE = f'neural-data-{ENVIRONMENT}'
BIGTABLE_TABLE = 'neural-time-series'


@functions_framework.cloud_event  # type: ignore
def process_neural_stream(cloud_event: Any) -> None:
    """Process neural data stream from Pub/Sub."""
    try:
        # Decode the Pub/Sub message
        pubsub_message = base64.b64decode(cloud_event.data["message"]["data"]).decode()
        data = json.loads(pubsub_message)

        logger.info(f"Processing neural data from device: {data.get('device_id')}")

        # Extract data fields
        device_id = data.get('device_id')
        signal_type = data.get('signal_type')
        timestamp = data.get('timestamp', datetime.utcnow().isoformat())
        sampling_rate = data.get('sampling_rate')
        channels = data.get('channels', [])
        samples = data.get('data', [])

        # Validate data
        if not device_id or not signal_type:
            logger.error("Missing required fields: device_id or signal_type")
            return

        # Log data info
        logger.info(
            f"Signal type: {signal_type}, Channels: {len(channels)}, "
            f"Samples: {len(samples)}, Sampling rate: {sampling_rate}Hz"
        )

        # Store in Bigtable (simplified for now)
        try:
            # Initialize Bigtable client
            client = bigtable.Client(project=PROJECT_ID, admin=True)
            instance = client.instance(BIGTABLE_INSTANCE)
            table = instance.table(BIGTABLE_TABLE)

            # Create row key: device_id#timestamp
            row_key = f"{device_id}#{timestamp}".encode()

            # Create row
            row = table.direct_row(row_key)

            # Add data to columns
            row.set_cell('metadata', 'device_id', device_id)
            row.set_cell('metadata', 'signal_type', signal_type)
            row.set_cell('metadata', 'timestamp', timestamp)
            row.set_cell('metadata', 'sampling_rate', str(sampling_rate))
            row.set_cell('metadata', 'channel_count', str(len(channels)))

            # Store sample data as JSON (simplified)
            row.set_cell('data', 'samples', json.dumps(samples))
            row.set_cell('data', 'channels', json.dumps(channels))

            # Commit the row
            row.commit()

            logger.info(f"Successfully stored data for device {device_id} at {timestamp}")

        except Exception as e:
            logger.error(f"Failed to store data in Bigtable: {str(e)}")
            # Continue processing even if storage fails

        # TODO: Add real-time processing, quality checks, etc.

        logger.info("Neural data processing completed successfully")

    except Exception as e:
        logger.error(f"Error processing neural data: {str(e)}")
        raise
