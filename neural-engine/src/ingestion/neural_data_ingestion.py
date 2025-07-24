"""Main neural data ingestion class for handling multiple BCI sources."""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
import numpy as np
import json
import hashlib

# Optional imports for Google Cloud services
try:
    from google.cloud import pubsub_v1, bigtable
    from google.cloud.bigtable import row_filters

    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    pubsub_v1 = None
    bigtable = None
    row_filters = None

from .data_types import (
    NeuralDataPacket,
    NeuralSignalType,
    DataSource,
    ValidationResult,
    DeviceInfo,
)
from .validators import DataValidator
from .anonymizer import DataAnonymizer


logger = logging.getLogger(__name__)


class NeuralDataIngestion:
    """
    Main class for ingesting neural data from multiple sources.

    Supports real-time streaming via LSL, batch uploads, and various
    BCI devices through unified interface.
    """

    def __init__(
        self,
        project_id: str,
        instance_id: str = "neural-data",
        table_id: str = "time-series",
        enable_pubsub: bool = True,
        enable_bigtable: bool = True,
    ):
        """
        Initialize the neural data ingestion system.

        Args:
            project_id: Google Cloud project ID
            instance_id: Bigtable instance ID
            table_id: Bigtable table ID
            enable_pubsub: Whether to publish to Pub/Sub
            enable_bigtable: Whether to store in Bigtable
        """
        self.project_id = project_id
        self.instance_id = instance_id
        self.table_id = table_id
        self.enable_pubsub = enable_pubsub
        self.enable_bigtable = enable_bigtable

        # Initialize components
        self.validator = DataValidator()
        self.anonymizer = DataAnonymizer()

        # Data source handlers
        self._source_handlers: Dict[DataSource, Callable] = {}
        self._active_streams: Dict[str, asyncio.Task] = {}

        # Initialize Google Cloud clients
        self._init_gcp_clients()

        # Metrics
        self.metrics = {
            "packets_received": 0,
            "packets_validated": 0,
            "packets_stored": 0,
            "validation_errors": 0,
            "storage_errors": 0,
        }

    def _init_gcp_clients(self):
        """Initialize Google Cloud clients."""
        if self.enable_pubsub:
            if not GOOGLE_CLOUD_AVAILABLE:
                logger.warning(
                    "Google Cloud Pub/Sub not available - install google-cloud-pubsub"
                )
                self.enable_pubsub = False
            else:
                self.publisher = pubsub_v1.PublisherClient()
                self.topic_paths = {
                    signal_type: self.publisher.topic_path(
                        self.project_id, f"neural-data-{signal_type.value}"
                    )
                    for signal_type in NeuralSignalType
                }

        if self.enable_bigtable:
            if not GOOGLE_CLOUD_AVAILABLE:
                logger.warning(
                    "Google Cloud Bigtable not available - install google-cloud-bigtable"
                )
                self.enable_bigtable = False
            else:
                self.bt_client = bigtable.Client(project=self.project_id, admin=True)
                self.bt_instance = self.bt_client.instance(self.instance_id)
                self.bt_table = self.bt_instance.table(self.table_id)

    async def ingest_packet(self, packet: NeuralDataPacket) -> bool:
        """
        Ingest a single neural data packet.

        Args:
            packet: Neural data packet to ingest

        Returns:
            True if successfully ingested, False otherwise
        """
        try:
            self.metrics["packets_received"] += 1

            # Validate data
            validation_result = await self._validate_packet(packet)
            if not validation_result.is_valid:
                logger.error(
                    f"Validation failed for packet {packet.session_id}: "
                    f"{validation_result.errors}"
                )
                self.metrics["validation_errors"] += 1
                return False

            self.metrics["packets_validated"] += 1

            # Anonymize data
            anonymized_packet = await self._anonymize_packet(packet)

            # Store data
            storage_tasks = []

            if self.enable_pubsub:
                storage_tasks.append(self._publish_to_pubsub(anonymized_packet))

            if self.enable_bigtable:
                storage_tasks.append(self._store_in_bigtable(anonymized_packet))

            # Execute storage operations
            results = await asyncio.gather(*storage_tasks, return_exceptions=True)

            # Check for errors
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Storage error: {result}")
                    self.metrics["storage_errors"] += 1
                    return False

            self.metrics["packets_stored"] += 1
            return True

        except Exception as e:
            logger.error(f"Error ingesting packet: {e}")
            return False

    async def _validate_packet(self, packet: NeuralDataPacket) -> ValidationResult:
        """Validate a neural data packet."""
        return self.validator.validate_packet(packet)

    async def _anonymize_packet(self, packet: NeuralDataPacket) -> NeuralDataPacket:
        """Anonymize sensitive information in the packet."""
        return self.anonymizer.anonymize_packet(packet)

    async def _publish_to_pubsub(self, packet: NeuralDataPacket):
        """Publish packet to appropriate Pub/Sub topic."""
        topic_path = self.topic_paths[packet.signal_type]

        # Serialize packet for Pub/Sub
        message_data = self._serialize_packet(packet)

        # Publish with attributes
        future = self.publisher.publish(
            topic_path,
            message_data,
            signal_type=packet.signal_type.value,
            source=packet.source.value,
            session_id=packet.session_id,
            timestamp=packet.timestamp.isoformat(),
        )

        # Wait for publish to complete
        message_id = await asyncio.get_event_loop().run_in_executor(None, future.result)

        logger.debug(f"Published packet to {topic_path}: {message_id}")

    async def _store_in_bigtable(self, packet: NeuralDataPacket):
        """Store packet in Bigtable for time-series analysis."""
        # Create row key: session_id#timestamp#channel
        row_key = f"{packet.session_id}#{packet.timestamp.timestamp()}"

        # Store each channel as a separate column
        rows = []
        row = self.bt_table.direct_row(row_key.encode())

        # Store metadata
        metadata = {
            "signal_type": packet.signal_type.value,
            "source": packet.source.value,
            "device_id": packet.device_info.device_id,
            "sampling_rate": packet.sampling_rate,
            "data_quality": packet.data_quality,
        }

        row.set_cell(
            "metadata",
            "info",
            json.dumps(metadata).encode(),
            timestamp=datetime.utcnow(),
        )

        # Store channel data
        for channel_idx in range(packet.n_channels):
            channel_data = packet.data[channel_idx, :].tobytes()
            column_name = f"ch_{channel_idx:03d}"

            row.set_cell(
                "data",
                column_name,
                channel_data,
                timestamp=datetime.utcnow(),
            )

        # Commit row
        await asyncio.get_event_loop().run_in_executor(None, row.commit)

        logger.debug(f"Stored packet in Bigtable: {row_key}")

    def _serialize_packet(self, packet: NeuralDataPacket) -> bytes:
        """Serialize packet for transmission."""
        # Convert numpy array to list for JSON serialization
        data_dict = {
            "timestamp": packet.timestamp.isoformat(),
            "signal_type": packet.signal_type.value,
            "source": packet.source.value,
            "session_id": packet.session_id,
            "subject_id": packet.subject_id,
            "device_info": {
                "device_id": packet.device_info.device_id,
                "device_type": packet.device_info.device_type,
            },
            "sampling_rate": packet.sampling_rate,
            "data_quality": packet.data_quality,
            "shape": packet.data.shape,
            "data": packet.data.tolist(),  # Convert to list for JSON
        }

        return json.dumps(data_dict).encode()

    def register_source_handler(
        self,
        source: DataSource,
        handler: Callable[[Dict[str, Any]], NeuralDataPacket],
    ):
        """
        Register a handler for a specific data source.

        Args:
            source: Data source type
            handler: Function that converts source data to NeuralDataPacket
        """
        self._source_handlers[source] = handler
        logger.info(f"Registered handler for {source.value}")

    async def start_stream(
        self,
        stream_id: str,
        source: DataSource,
        source_config: Dict[str, Any],
    ):
        """
        Start ingesting from a streaming source.

        Args:
            stream_id: Unique identifier for this stream
            source: Data source type
            source_config: Configuration for the source
        """
        if stream_id in self._active_streams:
            logger.warning(f"Stream {stream_id} already active")
            return

        if source not in self._source_handlers:
            raise ValueError(f"No handler registered for source {source.value}")

        # Create stream task
        stream_task = asyncio.create_task(
            self._stream_worker(stream_id, source, source_config)
        )

        self._active_streams[stream_id] = stream_task
        logger.info(f"Started stream {stream_id} from {source.value}")

    async def stop_stream(self, stream_id: str):
        """Stop an active stream."""
        if stream_id not in self._active_streams:
            logger.warning(f"Stream {stream_id} not found")
            return

        task = self._active_streams[stream_id]
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

        del self._active_streams[stream_id]
        logger.info(f"Stopped stream {stream_id}")

    async def _stream_worker(
        self,
        stream_id: str,
        source: DataSource,
        source_config: Dict[str, Any],
    ):
        """Worker coroutine for processing streaming data."""
        handler = self._source_handlers[source]

        try:
            while True:
                # Get data from source (implementation depends on source type)
                # This is a placeholder - actual implementation would use
                # source-specific libraries (pylsl, brainflow, etc.)
                raw_data = await self._get_source_data(source, source_config)

                if raw_data is None:
                    await asyncio.sleep(0.01)  # Small delay if no data
                    continue

                # Convert to NeuralDataPacket
                packet = handler(raw_data)

                # Ingest packet
                success = await self.ingest_packet(packet)

                if not success:
                    logger.error(f"Failed to ingest packet from stream {stream_id}")

        except asyncio.CancelledError:
            logger.info(f"Stream {stream_id} cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in stream {stream_id}: {e}")
            raise

    async def _get_source_data(
        self,
        source: DataSource,
        config: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Get data from source (placeholder for actual implementations).

        Real implementation would interface with:
        - LSL: pylsl library
        - OpenBCI: openbci-python
        - BrainFlow: brainflow library
        """
        # This is a placeholder - actual implementation needed
        await asyncio.sleep(0.1)
        return None

    def get_metrics(self) -> Dict[str, int]:
        """Get current ingestion metrics."""
        return self.metrics.copy()

    async def close(self):
        """Clean up resources."""
        # Stop all active streams
        stream_ids = list(self._active_streams.keys())
        for stream_id in stream_ids:
            await self.stop_stream(stream_id)

        # Close Google Cloud clients
        if hasattr(self, "publisher"):
            self.publisher.transport.close()

        logger.info("Neural data ingestion system closed")
