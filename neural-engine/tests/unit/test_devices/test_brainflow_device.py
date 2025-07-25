"""Unit tests for BrainFlow device implementation."""

import pytest
import asyncio
import numpy as np
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from datetime import datetime, timezone

from src.devices.implementations.brainflow_device import BrainFlowDevice
from src.devices.interfaces.base_device import DeviceState, DeviceCapabilities
from src.ingestion.data_types import NeuralSignalType, DataSource
from src.devices.signal_quality import SignalQualityLevel


class MockBoardShim:
    """Mock BoardShim for testing."""

    def __init__(self, board_id, params):
        self.board_id = board_id
        self.params = params
        self.is_prepared_flag = False
        self.is_streaming = False
        self.data_counter = 0

    def prepare_session(self):
        self.is_prepared_flag = True

    def release_session(self):
        self.is_prepared_flag = False

    def start_stream(self):
        self.is_streaming = True

    def stop_stream(self):
        self.is_streaming = False

    def is_prepared(self):
        return self.is_prepared_flag

    def get_board_data(self, num_samples):
        """Return mock data."""
        # Simulate different channel types
        n_channels = 10
        data = np.random.randn(n_channels, num_samples)
        # Add timestamps
        timestamps = np.arange(num_samples) + self.data_counter
        data[-1, :] = timestamps  # Last row is timestamps
        self.data_counter += num_samples
        return data

    def insert_marker(self, marker):
        pass

    @staticmethod
    def enable_dev_board_logger():
        pass

    @staticmethod
    def get_sampling_rate(board_id):
        return 250.0

    @staticmethod
    def get_eeg_channels(board_id):
        return [0, 1, 2, 3, 4, 5, 6, 7]

    @staticmethod
    def get_emg_channels(board_id):
        return []

    @staticmethod
    def get_accel_channels(board_id):
        return [8]

    @staticmethod
    def get_timestamp_channel(board_id):
        return 9

    @staticmethod
    def get_marker_channel(board_id):
        return None


@pytest.mark.skipif(
    not BrainFlowDevice,
    reason="BrainFlow not available"
)
class TestBrainFlowDevice:
    """Test suite for BrainFlow device implementation."""

    @pytest.fixture
    def mock_brainflow(self):
        """Mock BrainFlow imports."""
        with patch("src.devices.implementations.brainflow_device.BRAINFLOW_AVAILABLE", True):
            with patch("src.devices.implementations.brainflow_device.BoardShim", MockBoardShim):
                # Mock BoardIds enum
                board_ids = MagicMock()
                board_ids.SYNTHETIC_BOARD = 0
                board_ids.CYTON_BOARD = 1
                board_ids.CYTON_DAISY_BOARD = 2
                board_ids.GANGLION_BOARD = 3

                with patch("src.devices.implementations.brainflow_device.BoardIds", board_ids):
                    yield

    @pytest.fixture
    def device(self, mock_brainflow):
        """Create a BrainFlow device instance."""
        return BrainFlowDevice(board_name="synthetic")

    def test_initialization(self, device):
        """Test device initialization."""
        assert device.board_name == "synthetic"
        assert device.device_id == "brainflow_synthetic"
        assert device.device_name == "BrainFlow-Synthetic"
        assert device.board is None
        assert device.state == DeviceState.DISCONNECTED

    def test_supported_boards(self, mock_brainflow):
        """Test supported board types."""
        # Test creating devices with different boards
        for board_name in ["synthetic", "cyton", "ganglion"]:
            device = BrainFlowDevice(board_name=board_name)
            assert device.board_name == board_name

    def test_unsupported_board(self, mock_brainflow):
        """Test error on unsupported board."""
        with pytest.raises(ValueError, match="Unsupported board"):
            BrainFlowDevice(board_name="invalid_board")

    @pytest.mark.asyncio
    async def test_connect(self, device):
        """Test device connection."""
        # Connect to device
        result = await device.connect()

        assert result is True
        assert device.is_connected()
        assert device.state == DeviceState.CONNECTED
        assert device.board is not None
        assert device.device_info is not None
        assert device.sampling_rate == 250.0
        assert len(device.eeg_channels) == 8
        assert device.signal_quality_monitor is not None

    @pytest.mark.asyncio
    async def test_disconnect(self, device):
        """Test device disconnection."""
        # Connect first
        await device.connect()
        assert device.is_connected()

        # Disconnect
        await device.disconnect()

        assert not device.is_connected()
        assert device.state == DeviceState.DISCONNECTED
        assert device.board is None

    @pytest.mark.asyncio
    async def test_streaming(self, device):
        """Test data streaming."""
        # Set up data callback
        received_packets = []
        device.set_data_callback(lambda packet: received_packets.append(packet))
        device.set_session_id("test_session")

        # Connect and start streaming
        await device.connect()
        await device.start_streaming()

        assert device.is_streaming()
        assert device.state == DeviceState.STREAMING

        # Wait for some data
        await asyncio.sleep(0.3)

        # Stop streaming
        await device.stop_streaming()

        assert not device.is_streaming()
        assert device.state == DeviceState.CONNECTED
        assert len(received_packets) > 0

        # Check packet properties
        for packet in received_packets:
            assert packet.signal_type == NeuralSignalType.EEG
            assert packet.source == DataSource.BRAINFLOW
            assert packet.session_id == "test_session"
            assert packet.data.shape[0] == 8  # 8 EEG channels

    def test_capabilities(self, device):
        """Test device capabilities."""
        # Connect first to initialize channels
        asyncio.run(device.connect())

        caps = device.get_capabilities()

        assert isinstance(caps, DeviceCapabilities)
        assert device.sampling_rate in caps.supported_sampling_rates
        assert caps.max_channels == 9  # 8 EEG + 1 accel
        assert NeuralSignalType.EEG in caps.signal_types
        assert NeuralSignalType.ACCELEROMETER in caps.signal_types

    def test_capabilities_board_specific(self, mock_brainflow):
        """Test board-specific capabilities."""
        # Test Cyton (has impedance check)
        cyton = BrainFlowDevice(board_name="cyton")
        asyncio.run(cyton.connect())
        caps = cyton.get_capabilities()
        assert caps.has_impedance_check is True

        # Test synthetic (no impedance check)
        synthetic = BrainFlowDevice(board_name="synthetic")
        asyncio.run(synthetic.connect())
        caps = synthetic.get_capabilities()
        assert caps.has_impedance_check is False

    @pytest.mark.asyncio
    async def test_impedance_checking(self, mock_brainflow):
        """Test impedance checking functionality."""
        # Create Cyton device (supports impedance)
        device = BrainFlowDevice(board_name="cyton")
        await device.connect()

        # Check impedance
        impedances = await device.check_impedance()

        assert isinstance(impedances, dict)
        assert len(impedances) > 0

        # Check stored results
        assert len(device._impedance_results) > 0
        for channel_id, result in device._impedance_results.items():
            assert result.channel_id == channel_id
            assert result.impedance_ohms > 0
            assert result.quality_level in SignalQualityLevel

    @pytest.mark.asyncio
    async def test_impedance_not_supported(self, device):
        """Test impedance checking on unsupported device."""
        await device.connect()

        # Synthetic board doesn't support impedance
        with pytest.raises(NotImplementedError):
            await device.check_impedance()

    @pytest.mark.asyncio
    async def test_signal_quality_assessment(self, device):
        """Test signal quality assessment."""
        await device.connect()
        await device.start_streaming()

        # Wait for some data
        await asyncio.sleep(0.2)

        # Get signal quality
        quality_metrics = await device.get_signal_quality()

        assert isinstance(quality_metrics, dict)
        assert len(quality_metrics) > 0

        for channel_id, metrics in quality_metrics.items():
            assert metrics.channel_id == channel_id
            assert metrics.snr_db is not None
            assert metrics.quality_level in SignalQualityLevel

        await device.stop_streaming()

    @pytest.mark.asyncio
    async def test_signal_quality_not_streaming(self, device):
        """Test signal quality when not streaming."""
        await device.connect()

        # Should raise error when not streaming
        with pytest.raises(RuntimeError, match="must be streaming"):
            await device.get_signal_quality()

    @pytest.mark.asyncio
    async def test_insert_marker(self, device):
        """Test marker insertion."""
        await device.connect()
        await device.start_streaming()

        # Insert marker
        result = await device.insert_marker(123.0)

        # Synthetic board doesn't have marker channel
        assert result is False

        await device.stop_streaming()

    @pytest.mark.asyncio
    async def test_get_board_data_history(self, device):
        """Test getting historical data."""
        await device.connect()
        await device.start_streaming()

        # Wait for some data
        await asyncio.sleep(0.5)

        # Get historical data
        history = await device.get_board_data_history(1.0)

        assert history is not None
        assert isinstance(history, np.ndarray)
        assert history.shape[1] > 0  # Should have samples

        await device.stop_streaming()

    @pytest.mark.asyncio
    async def test_connection_parameters(self, mock_brainflow):
        """Test different connection parameters."""
        # Test serial port
        device = BrainFlowDevice(
            board_name="cyton",
            serial_port="/dev/ttyUSB0"
        )
        assert device.params.serial_port == "/dev/ttyUSB0"

        # Test Bluetooth
        device = BrainFlowDevice(
            board_name="ganglion",
            mac_address="00:11:22:33:44:55"
        )
        assert device.params.mac_address == "00:11:22:33:44:55"

        # Test WiFi
        device = BrainFlowDevice(
            board_name="cyton",
            ip_address="192.168.1.100",
            ip_port=3000
        )
        assert device.params.ip_address == "192.168.1.100"
        assert device.params.ip_port == 3000

    @pytest.mark.asyncio
    async def test_error_handling(self, device):
        """Test error handling during operations."""
        # Try to start streaming without connection
        with pytest.raises(RuntimeError):
            await device.start_streaming()

        # Connect device
        await device.connect()

        # Mock board error
        device.board.get_board_data = Mock(side_effect=Exception("Board error"))

        # Set error callback
        errors = []
        device.set_error_callback(lambda err: errors.append(err))

        # Start streaming - should handle error
        await device.start_streaming()
        await asyncio.sleep(0.2)
        await device.stop_streaming()

        # Should have caught errors
        assert len(errors) > 0
        assert device.state == DeviceState.ERROR

    def test_configure_channels_not_supported(self, device):
        """Test that channel configuration is not supported."""
        result = device.configure_channels([])
        assert result is False

    def test_set_sampling_rate_not_supported(self, device):
        """Test that sampling rate configuration is not supported."""
        result = device.set_sampling_rate(512.0)
        assert result is False

    def test_manufacturer_mapping(self, mock_brainflow):
        """Test manufacturer name mapping."""
        test_cases = {
            "cyton": "OpenBCI",
            "ganglion": "OpenBCI",
            "muse_s": "InteraXon",
            "synthetic": "BrainFlow",
        }

        for board_name, expected_manufacturer in test_cases.items():
            device = BrainFlowDevice(board_name=board_name)
            asyncio.run(device.connect())
            assert device.device_info.manufacturer == expected_manufacturer

    @pytest.mark.asyncio
    async def test_no_brainflow_import(self):
        """Test behavior when BrainFlow is not installed."""
        with patch("src.devices.implementations.brainflow_device.BRAINFLOW_AVAILABLE", False):
            with pytest.raises(ImportError, match="brainflow is not installed"):
                BrainFlowDevice()
