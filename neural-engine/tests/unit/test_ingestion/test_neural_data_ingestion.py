"""Tests for the main neural data ingestion class."""

import pytest
import asyncio
import numpy as np
from datetime import datetime, timezone
from unittest.mock import Mock, patch, AsyncMock

from src.ingestion import NeuralDataIngestion
from src.ingestion.data_types import (
    NeuralDataPacket,
    NeuralSignalType,
    DataSource,
    DeviceInfo,
    ChannelInfo,
)


class TestNeuralDataIngestion:
    """Test NeuralDataIngestion class."""

    @pytest.fixture
    def ingestion(self):
        """Create ingestion instance with GCP disabled."""
        return NeuralDataIngestion(
            project_id="test - project",
            enable_pubsub=False,
            enable_bigtable=False,
        )

    @pytest.fixture
    def test_packet(self):
        """Create a test data packet."""
        device_info = DeviceInfo(
            device_id="test_device",
            device_type="OpenBCI",
            channels=[
                ChannelInfo(i, f"Ch{i + 1}", "microvolts", 256.0) for i in range(8)
            ],
        )

        return NeuralDataPacket(
            timestamp=datetime.now(timezone.utc),
            data=np.random.randn(8, 256) * 50,
            signal_type=NeuralSignalType.EEG,
            source=DataSource.OPENBCI,
            device_info=device_info,
            session_id="test_session",
            subject_id="test_subject",
            sampling_rate=256.0,
            data_quality=0.95,
        )

    @pytest.mark.asyncio
    async def test_ingest_packet_success(self, ingestion, test_packet):
        """Test successful packet ingestion."""
        success = await ingestion.ingest_packet(test_packet)

        assert success
        assert ingestion.metrics["packets_received"] == 1
        assert ingestion.metrics["packets_validated"] == 1
        assert ingestion.metrics["packets_stored"] == 1
        assert ingestion.metrics["validation_errors"] == 0
        assert ingestion.metrics["storage_errors"] == 0

    @pytest.mark.asyncio
    async def test_ingest_packet_validation_failure(self, ingestion):
        """Test packet ingestion with validation failure."""
        # Create invalid packet with NaN values
        bad_packet = NeuralDataPacket(
            timestamp=datetime.now(timezone.utc),
            data=np.full((8, 256), np.nan),  # All NaN values
            signal_type=NeuralSignalType.EEG,
            source=DataSource.SYNTHETIC,
            device_info=DeviceInfo("test", "test"),
            session_id="test",
        )

        success = await ingestion.ingest_packet(bad_packet)

        assert not success
        assert ingestion.metrics["packets_received"] == 1
        assert ingestion.metrics["validation_errors"] == 1
        assert ingestion.metrics["packets_stored"] == 0

    @pytest.mark.asyncio
    async def test_ingest_multiple_packets(self, ingestion, test_packet):
        """Test ingesting multiple packets."""
        num_packets = 10

        for i in range(num_packets):
            # Modify packet slightly
            test_packet.timestamp = datetime.now(timezone.utc)
            success = await ingestion.ingest_packet(test_packet)
            assert success

        assert ingestion.metrics["packets_received"] == num_packets
        assert ingestion.metrics["packets_validated"] == num_packets
        assert ingestion.metrics["packets_stored"] == num_packets

    def test_register_source_handler(self, ingestion):
        """Test registering a source handler."""

        def mock_handler(data):
            return NeuralDataPacket(
                timestamp=datetime.now(timezone.utc),
                data=data["samples"],
                signal_type=NeuralSignalType.EEG,
                source=DataSource.LSL,
                device_info=DeviceInfo("lsl", "LSL"),
                session_id="lsl_session",
            )

        ingestion.register_source_handler(DataSource.LSL, mock_handler)

        assert DataSource.LSL in ingestion._source_handlers
        assert ingestion._source_handlers[DataSource.LSL] == mock_handler

    @pytest.mark.asyncio
    async def test_start_stop_stream(self, ingestion):
        """Test starting and stopping a stream."""
        # Register a mock handler
        mock_handler = Mock(return_value=None)
        ingestion.register_source_handler(DataSource.LSL, mock_handler)

        # Mock the stream worker to avoid infinite loop
        async def mock_stream_worker(*args):
            await asyncio.sleep(0.1)

        ingestion._stream_worker = mock_stream_worker

        # Start stream
        await ingestion.start_stream("test_stream", DataSource.LSL, {"port": 12345})

        assert "test_stream" in ingestion._active_streams

        # Stop stream
        await ingestion.stop_stream("test_stream")

        assert "test_stream" not in ingestion._active_streams

    @pytest.mark.asyncio
    async def test_close(self, ingestion):
        """Test closing the ingestion system."""
        # Add a mock stream
        mock_task = asyncio.create_task(asyncio.sleep(10))
        ingestion._active_streams["test_stream"] = mock_task

        # Close should stop all streams
        await ingestion.close()

        assert len(ingestion._active_streams) == 0
        assert mock_task.cancelled()

    def test_get_metrics(self, ingestion):
        """Test getting metrics."""
        # Modify metrics
        ingestion.metrics["packets_received"] = 100

        metrics = ingestion.get_metrics()

        # Should return a copy
        assert metrics["packets_received"] == 100
        metrics["packets_received"] = 200
        assert ingestion.metrics["packets_received"] == 100  # Original unchanged

    @pytest.mark.asyncio
    async def test_anonymization(self, ingestion, test_packet):
        """Test that packets are anonymized during ingestion."""
        # Store original subject ID
        original_subject_id = test_packet.subject_id

        # Ingest packet
        success = await ingestion.ingest_packet(test_packet)
        assert success

        # Access the anonymizer to check if subject was anonymized
        mappings = ingestion.anonymizer.export_mappings()
        assert original_subject_id in mappings
        assert mappings[original_subject_id].startswith("ANON_")

    @pytest.mark.asyncio
    async def test_pubsub_integration(self):
        """Test Pub / Sub integration when enabled."""
        with patch("src.ingestion.neural_data_ingestion.GOOGLE_CLOUD_AVAILABLE", True):
            with patch("src.ingestion.neural_data_ingestion.pubsub_v1") as mock_pubsub:
                # Setup mocks
                mock_publisher = Mock()
                mock_future = Mock()
                mock_future.result.return_value = "message - id - 123"
                mock_publisher.publish.return_value = mock_future
                mock_pubsub.PublisherClient.return_value = mock_publisher

                # Create ingestion with Pub / Sub enabled
                ingestion = NeuralDataIngestion(
                    project_id="test - project",
                    enable_pubsub=True,
                    enable_bigtable=False,
                )

                # Create and ingest packet
                packet = NeuralDataPacket(
                    timestamp=datetime.now(timezone.utc),
                    data=np.zeros((8, 256)),
                    signal_type=NeuralSignalType.EEG,
                    source=DataSource.SYNTHETIC,
                    device_info=DeviceInfo("test", "test"),
                    session_id="test",
                )

                success = await ingestion.ingest_packet(packet)

                assert success
                assert mock_publisher.publish.called

    def test_serialize_packet(self, ingestion, test_packet):
        """Test packet serialization."""
        serialized = ingestion._serialize_packet(test_packet)

        assert isinstance(serialized, bytes)

        # Deserialize and check
        import json

        data = json.loads(serialized.decode())

        assert data["session_id"] == test_packet.session_id
        assert data["signal_type"] == test_packet.signal_type.value
        assert data["source"] == test_packet.source.value
        assert data["shape"] == list(test_packet.data.shape)
        assert len(data["data"]) == test_packet.n_channels
