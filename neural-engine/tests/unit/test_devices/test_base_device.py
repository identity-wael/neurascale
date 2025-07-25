"""Unit tests for base device interface."""

import pytest
import asyncio
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock, patch
import numpy as np

from src.devices.interfaces.base_device import (
    BaseDevice,
    DeviceState,
    DeviceCapabilities,
)
from src.ingestion.data_types import (
    NeuralDataPacket,
    DeviceInfo,
    ChannelInfo,
    NeuralSignalType,
    DataSource,
)


class MockDevice(BaseDevice):
    """Mock implementation of BaseDevice for testing."""

    def __init__(self, device_id: str = "test_device", device_name: str = "Test Device"):
        super().__init__(device_id, device_name)
        self.connect_called = False
        self.disconnect_called = False
        self.streaming_started = False
        self.streaming_stopped = False

    async def connect(self, **kwargs):
        self.connect_called = True
        self._update_state(DeviceState.CONNECTED)
        self.device_info = DeviceInfo(
            device_id=self.device_id,
            device_type="Mock",
            manufacturer="Test",
            model="MockDevice",
            channels=[
                ChannelInfo(
                    channel_id=0,
                    label="CH1",
                    unit="microvolts",
                    sampling_rate=256.0,
                    hardware_id="0",
                )
            ],
        )
        return True

    async def disconnect(self):
        self.disconnect_called = True
        self._update_state(DeviceState.DISCONNECTED)

    async def start_streaming(self):
        if not self.is_connected():
            raise RuntimeError("Device not connected")
        self.streaming_started = True
        self._update_state(DeviceState.STREAMING)
        self._stop_streaming.clear()
        self._streaming_task = asyncio.create_task(self._streaming_loop())

    async def stop_streaming(self):
        self.streaming_stopped = True
        self._stop_streaming.set()
        if self._streaming_task:
            await self._streaming_task
            self._streaming_task = None
        self._update_state(DeviceState.CONNECTED)

    def get_capabilities(self) -> DeviceCapabilities:
        return DeviceCapabilities(
            supported_sampling_rates=[256.0, 512.0],
            max_channels=8,
            signal_types=[NeuralSignalType.EEG],
            has_impedance_check=True,
            has_battery_monitor=False,
        )

    def configure_channels(self, channels):
        return True

    def set_sampling_rate(self, rate):
        return rate in [256.0, 512.0]

    async def _streaming_loop(self):
        """Mock streaming loop."""
        while not self._stop_streaming.is_set():
            # Generate mock data
            data = np.random.randn(1, 256)  # 1 channel, 256 samples
            timestamp = datetime.now(timezone.utc)

            packet = self._create_packet(
                data=data,
                timestamp=timestamp,
                signal_type=NeuralSignalType.EEG,
                source=DataSource.DEVICE,
            )

            if self._data_callback:
                self._data_callback(packet)

            await asyncio.sleep(0.1)  # 100ms chunks


class TestBaseDevice:
    """Test suite for BaseDevice interface."""

    @pytest.fixture
    def device(self):
        """Create a mock device instance."""
        return MockDevice()

    def test_initialization(self, device):
        """Test device initialization."""
        assert device.device_id == "test_device"
        assert device.device_name == "Test Device"
        assert device.state == DeviceState.DISCONNECTED
        assert device.device_info is None
        assert device.session_id is None

    @pytest.mark.asyncio
    async def test_connect_disconnect(self, device):
        """Test device connection and disconnection."""
        # Test initial state
        assert not device.is_connected()

        # Test connect
        result = await device.connect()
        assert result is True
        assert device.connect_called
        assert device.is_connected()
        assert device.state == DeviceState.CONNECTED
        assert device.device_info is not None

        # Test disconnect
        await device.disconnect()
        assert device.disconnect_called
        assert not device.is_connected()
        assert device.state == DeviceState.DISCONNECTED

    @pytest.mark.asyncio
    async def test_streaming(self, device):
        """Test streaming functionality."""
        # Cannot stream when disconnected
        with pytest.raises(RuntimeError):
            await device.start_streaming()

        # Connect first
        await device.connect()

        # Start streaming
        await device.start_streaming()
        assert device.streaming_started
        assert device.is_streaming()
        assert device.state == DeviceState.STREAMING

        # Stop streaming
        await device.stop_streaming()
        assert device.streaming_stopped
        assert not device.is_streaming()
        assert device.state == DeviceState.CONNECTED

    def test_capabilities(self, device):
        """Test device capabilities."""
        caps = device.get_capabilities()
        assert isinstance(caps, DeviceCapabilities)
        assert 256.0 in caps.supported_sampling_rates
        assert caps.max_channels == 8
        assert NeuralSignalType.EEG in caps.signal_types
        assert caps.has_impedance_check is True
        assert caps.has_battery_monitor is False

    def test_configuration(self, device):
        """Test device configuration."""
        # Test channel configuration
        channels = [
            ChannelInfo(
                channel_id=0,
                label="Test",
                unit="microvolts",
                sampling_rate=256.0,
                hardware_id="0",
            )
        ]
        assert device.configure_channels(channels) is True

        # Test sampling rate
        assert device.set_sampling_rate(256.0) is True
        assert device.set_sampling_rate(512.0) is True
        assert device.set_sampling_rate(1000.0) is False

    def test_callbacks(self, device):
        """Test callback functionality."""
        # Test data callback
        data_callback = Mock()
        device.set_data_callback(data_callback)
        assert device._data_callback == data_callback

        # Test state callback
        state_callback = Mock()
        device.set_state_callback(state_callback)
        assert device._state_callback == state_callback

        # Test error callback
        error_callback = Mock()
        device.set_error_callback(error_callback)
        assert device._error_callback == error_callback

    def test_session_management(self, device):
        """Test session ID management."""
        session_id = "test_session_123"
        device.set_session_id(session_id)
        assert device.session_id == session_id

    @pytest.mark.asyncio
    async def test_data_streaming(self, device):
        """Test data packet generation during streaming."""
        # Set up data callback
        received_packets = []
        device.set_data_callback(lambda packet: received_packets.append(packet))

        # Set session ID (required for packet creation)
        device.set_session_id("test_session")

        # Connect and start streaming
        await device.connect()
        await device.start_streaming()

        # Wait for some data
        await asyncio.sleep(0.3)

        # Stop streaming
        await device.stop_streaming()

        # Check received packets
        assert len(received_packets) >= 2
        for packet in received_packets:
            assert isinstance(packet, NeuralDataPacket)
            assert packet.signal_type == NeuralSignalType.EEG
            assert packet.source == DataSource.DEVICE
            assert packet.session_id == "test_session"
            assert packet.data.shape == (1, 256)

    def test_state_transitions(self, device):
        """Test device state transitions."""
        # Set up state callback
        state_changes = []
        device.set_state_callback(lambda state: state_changes.append(state))

        # Trigger state changes
        device._update_state(DeviceState.CONNECTING)
        device._update_state(DeviceState.CONNECTED)
        device._update_state(DeviceState.STREAMING)
        device._update_state(DeviceState.ERROR)

        # Check state changes were recorded
        assert state_changes == [
            DeviceState.CONNECTING,
            DeviceState.CONNECTED,
            DeviceState.STREAMING,
            DeviceState.ERROR,
        ]

    def test_error_handling(self, device):
        """Test error handling."""
        # Set up error callback
        errors = []
        device.set_error_callback(lambda error: errors.append(error))

        # Trigger error
        test_error = ValueError("Test error")
        device._handle_error(test_error)

        # Check error was recorded
        assert len(errors) == 1
        assert errors[0] == test_error
        assert device.state == DeviceState.ERROR

    @pytest.mark.asyncio
    async def test_context_manager(self, device):
        """Test async context manager functionality."""
        device.set_session_id("test_session")

        async with device:
            # Device should allow connection inside context
            await device.connect()
            assert device.is_connected()

            await device.start_streaming()
            assert device.is_streaming()

        # Device should be cleaned up after context
        assert not device.is_streaming()
        assert not device.is_connected()

    def test_impedance_check_not_supported(self, device):
        """Test impedance check when not supported."""
        # Create device without impedance support
        device.get_capabilities = Mock(
            return_value=DeviceCapabilities(
                supported_sampling_rates=[256.0],
                max_channels=8,
                signal_types=[NeuralSignalType.EEG],
                has_impedance_check=False,
            )
        )

        # Should raise NotImplementedError
        with pytest.raises(NotImplementedError):
            asyncio.run(device.check_impedance())

    def test_battery_level_not_supported(self, device):
        """Test battery level when not supported."""
        # Should raise NotImplementedError
        with pytest.raises(NotImplementedError):
            asyncio.run(device.get_battery_level())

    def test_create_packet_validation(self, device):
        """Test packet creation validation."""
        # Should fail without device info
        with pytest.raises(ValueError):
            device._create_packet(
                data=np.array([]),
                timestamp=datetime.now(timezone.utc),
                signal_type=NeuralSignalType.EEG,
                source=DataSource.DEVICE,
            )

        # Set device info but not session ID
        device.device_info = DeviceInfo(
            device_id="test",
            device_type="Mock",
            manufacturer="Test",
            model="MockDevice",
            channels=[],
        )

        # Should fail without session ID
        with pytest.raises(ValueError):
            device._create_packet(
                data=np.array([]),
                timestamp=datetime.now(timezone.utc),
                signal_type=NeuralSignalType.EEG,
                source=DataSource.DEVICE,
            )
