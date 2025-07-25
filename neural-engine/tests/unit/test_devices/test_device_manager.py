"""Unit tests for device manager."""

import pytest
import asyncio
from unittest.mock import Mock, patch

from src.devices.device_manager import DeviceManager
from src.devices.interfaces.base_device import BaseDevice, DeviceState
from src.devices.device_discovery import DiscoveredDevice, DeviceProtocol
from src.ingestion.data_types import NeuralDataPacket, NeuralSignalType


class MockDevice(BaseDevice):
    """Mock device for testing."""

    def __init__(self, device_id="mock", device_name="Mock Device"):
        super().__init__(device_id, device_name)
        self.connect_called = False
        self.disconnect_called = False
        self.streaming = False

    async def connect(self, **kwargs):
        self.connect_called = True
        self._update_state(DeviceState.CONNECTED)
        return True

    async def disconnect(self):
        self.disconnect_called = True
        self._update_state(DeviceState.DISCONNECTED)

    async def start_streaming(self):
        self.streaming = True
        self._update_state(DeviceState.STREAMING)

    async def stop_streaming(self):
        self.streaming = False
        self._update_state(DeviceState.CONNECTED)

    def get_capabilities(self):
        from src.devices.interfaces.base_device import DeviceCapabilities

        return DeviceCapabilities(
            supported_sampling_rates=[256.0],
            max_channels=8,
            signal_types=[NeuralSignalType.EEG],
        )

    def configure_channels(self, channels):
        return True

    def set_sampling_rate(self, rate):
        return True


class TestDeviceManager:
    """Test suite for DeviceManager."""

    @pytest.fixture
    def manager(self):
        """Create a device manager instance."""
        return DeviceManager()

    def test_initialization(self, manager):
        """Test device manager initialization."""
        assert len(manager.devices) == 0
        assert manager.active_session_id is None
        assert isinstance(manager.discovery_service, object)
        assert len(manager._discovered_devices) == 0

    def test_register_device_type(self, manager):
        """Test registering custom device types."""
        manager.register_device_type("custom", MockDevice)
        assert "custom" in manager.DEVICE_TYPES
        assert manager.DEVICE_TYPES["custom"] == MockDevice

    @pytest.mark.asyncio
    async def test_add_device(self, manager):
        """Test adding devices."""
        # Register mock device type
        manager.register_device_type("mock", MockDevice)

        # Add device
        device = await manager.add_device("device1", "mock")

        assert isinstance(device, MockDevice)
        assert "device1" in manager.devices
        assert manager.devices["device1"] == device

    @pytest.mark.asyncio
    async def test_add_duplicate_device(self, manager):
        """Test adding duplicate device ID."""
        manager.register_device_type("mock", MockDevice)

        await manager.add_device("device1", "mock")

        # Should raise error for duplicate ID
        with pytest.raises(ValueError, match="already exists"):
            await manager.add_device("device1", "mock")

    @pytest.mark.asyncio
    async def test_add_unknown_device_type(self, manager):
        """Test adding device with unknown type."""
        with pytest.raises(ValueError, match="Unknown device type"):
            await manager.add_device("device1", "unknown_type")

    @pytest.mark.asyncio
    async def test_remove_device(self, manager):
        """Test removing devices."""
        manager.register_device_type("mock", MockDevice)

        # Add and connect device
        device = await manager.add_device("device1", "mock")
        await device.connect()
        await device.start_streaming()

        # Remove device
        await manager.remove_device("device1")

        assert "device1" not in manager.devices
        assert device.disconnect_called

    def test_get_device(self, manager):
        """Test getting device by ID."""
        manager.register_device_type("mock", MockDevice)

        # Add device
        device = asyncio.run(manager.add_device("device1", "mock"))

        # Get device
        retrieved = manager.get_device("device1")
        assert retrieved == device

        # Get non-existent device
        assert manager.get_device("nonexistent") is None

    @pytest.mark.asyncio
    async def test_list_devices(self, manager):
        """Test listing devices."""
        manager.register_device_type("mock", MockDevice)

        # Add multiple devices
        device1 = await manager.add_device("device1", "mock")
        device2 = await manager.add_device("device2", "mock")

        await device1.connect()
        await device2.connect()
        await device2.start_streaming()

        # List devices
        devices = manager.list_devices()

        assert len(devices) == 2

        # Check device1 info
        dev1_info = next(d for d in devices if d["device_id"] == "device1")
        assert dev1_info["state"] == "connected"
        assert dev1_info["connected"] is True
        assert dev1_info["streaming"] is False

        # Check device2 info
        dev2_info = next(d for d in devices if d["device_id"] == "device2")
        assert dev2_info["state"] == "streaming"
        assert dev2_info["connected"] is True
        assert dev2_info["streaming"] is True

    @pytest.mark.asyncio
    async def test_connect_disconnect_device(self, manager):
        """Test connecting and disconnecting specific devices."""
        manager.register_device_type("mock", MockDevice)

        device = await manager.add_device("device1", "mock")

        # Connect
        result = await manager.connect_device("device1")
        assert result is True
        assert device.connect_called

        # Disconnect
        await manager.disconnect_device("device1")
        assert device.disconnect_called

    @pytest.mark.asyncio
    async def test_connect_nonexistent_device(self, manager):
        """Test connecting non-existent device."""
        with pytest.raises(ValueError, match="not found"):
            await manager.connect_device("nonexistent")

    @pytest.mark.asyncio
    async def test_start_stop_streaming(self, manager):
        """Test starting and stopping streaming."""
        manager.register_device_type("mock", MockDevice)

        # Add and connect devices
        device1 = await manager.add_device("device1", "mock")
        device2 = await manager.add_device("device2", "mock")

        await device1.connect()
        await device2.connect()

        # Start streaming on all devices
        await manager.start_streaming()

        assert device1.streaming is True
        assert device2.streaming is True
        assert manager.active_session_id is not None

        # Stop streaming
        await manager.stop_streaming()

        assert device1.streaming is False
        assert device2.streaming is False

    @pytest.mark.asyncio
    async def test_start_streaming_specific_devices(self, manager):
        """Test starting streaming on specific devices."""
        manager.register_device_type("mock", MockDevice)

        device1 = await manager.add_device("device1", "mock")
        device2 = await manager.add_device("device2", "mock")

        await device1.connect()
        await device2.connect()

        # Start streaming only on device1
        await manager.start_streaming(["device1"])

        assert device1.streaming is True
        assert device2.streaming is False

    def test_session_management(self, manager):
        """Test session management."""
        # Start session with auto-generated ID
        session_id = manager.start_session()

        assert session_id is not None
        assert manager.active_session_id == session_id
        assert "session_" in session_id

        # Start session with custom ID
        custom_id = "custom_session_123"
        session_id = manager.start_session(custom_id)

        assert session_id == custom_id
        assert manager.active_session_id == custom_id

        # End session
        manager.end_session()
        assert manager.active_session_id is None

    def test_callbacks(self, manager):
        """Test callback management."""
        data_callback = Mock()
        state_callback = Mock()
        error_callback = Mock()

        manager.set_data_callback(data_callback)
        manager.set_state_callback(state_callback)
        manager.set_error_callback(error_callback)

        # Test data callback
        packet = Mock(spec=NeuralDataPacket)
        packet.metadata = {}
        manager._handle_device_data("device1", packet)
        data_callback.assert_called_once_with("device1", packet)

        # Test state callback
        manager._handle_device_state("device1", DeviceState.CONNECTED)
        state_callback.assert_called_once_with("device1", DeviceState.CONNECTED)

        # Test error callback
        error = ValueError("Test error")
        manager._handle_device_error("device1", error)
        error_callback.assert_called_once_with("device1", error)

    @pytest.mark.asyncio
    async def test_data_aggregation(self, manager):
        """Test data aggregation functionality."""
        aggregated_windows = []

        def aggregation_callback(window):
            aggregated_windows.append(window)

        # Start aggregation
        await manager.start_aggregation(
            window_size_ms=50, callback=aggregation_callback
        )

        # Simulate data from devices
        packet1 = Mock(spec=NeuralDataPacket)
        packet1.metadata = {}
        packet2 = Mock(spec=NeuralDataPacket)
        packet2.metadata = {}

        manager._handle_device_data("device1", packet1)
        manager._handle_device_data("device2", packet2)

        # Wait for aggregation window
        await asyncio.sleep(0.1)

        # Stop aggregation
        await manager.stop_aggregation()

        # Should have received aggregated windows
        assert len(aggregated_windows) > 0

    @pytest.mark.asyncio
    async def test_auto_discover_devices(self, manager):
        """Test device auto-discovery."""
        # Mock discovered devices
        mock_devices = [
            DiscoveredDevice(
                device_type="LSL",
                device_name="Test LSL Stream",
                protocol=DeviceProtocol.LSL,
                connection_info={"name": "TestStream"},
            ),
            DiscoveredDevice(
                device_type="OpenBCI",
                device_name="OpenBCI Cyton",
                protocol=DeviceProtocol.SERIAL,
                connection_info={"port": "/dev/ttyUSB0"},
            ),
        ]

        # Mock discovery service
        with patch.object(
            manager.discovery_service, "quick_scan", return_value=mock_devices
        ):
            discovered = await manager.auto_discover_devices(timeout=1.0)

        assert len(discovered) >= 2

        # Check discovered devices
        lsl_devices = [d for d in discovered if d["device_type"] == "lsl"]
        assert len(lsl_devices) == 1
        assert lsl_devices[0]["name"] == "Test LSL Stream"

        openbci_devices = [d for d in discovered if d["device_type"] == "openbci"]
        assert len(openbci_devices) == 1
        assert openbci_devices[0]["connection_info"]["port"] == "/dev/ttyUSB0"

    @pytest.mark.asyncio
    async def test_create_device_from_discovery(self, manager):
        """Test creating device from discovery."""
        # Add discovered device
        discovered = DiscoveredDevice(
            device_type="LSL",
            device_name="Test LSL Stream",
            protocol=DeviceProtocol.LSL,
            connection_info={
                "name": "TestStream",
                "type": "EEG",
            },
        )

        manager._discovered_devices[discovered.unique_id] = discovered

        # Create device from discovery
        with patch("src.devices.implementations.lsl_device.LSLDevice") as MockLSL:
            mock_device = MockDevice()
            MockLSL.return_value = mock_device

            device = await manager.create_device_from_discovery(discovered.unique_id)

            assert device == mock_device
            assert discovered.unique_id in manager.devices

    def test_map_device_type(self, manager):
        """Test device type mapping."""
        test_cases = [
            (DiscoveredDevice("LSL", "Stream", DeviceProtocol.LSL, {}), "lsl"),
            (
                DiscoveredDevice("OpenBCI", "Cyton", DeviceProtocol.SERIAL, {}),
                "openbci",
            ),
            (
                DiscoveredDevice("BrainFlow", "Synthetic", DeviceProtocol.USB, {}),
                "brainflow",
            ),
            (
                DiscoveredDevice("Muse", "Muse S", DeviceProtocol.BLUETOOTH, {}),
                "brainflow",
            ),
            (DiscoveredDevice("Unknown", "Device", DeviceProtocol.USB, {}), None),
        ]

        for discovered, expected in test_cases:
            assert manager._map_device_type(discovered) == expected

    def test_get_brainflow_board_name(self, manager):
        """Test BrainFlow board name mapping."""
        test_cases = [
            ("OpenBCI Cyton", "cyton"),
            ("OpenBCI Ganglion", "ganglion"),
            ("Muse S", "muse_s"),
            ("Muse 2", "muse_2"),
            ("Neurosity Crown", "neurosity_crown"),
            ("BrainBit", "brainbit"),
            ("g.tec Unicorn", "unicorn"),
            ("BrainFlow Synthetic", "synthetic"),
            ("Unknown Device", "synthetic"),  # Default
        ]

        for device_name, expected_board in test_cases:
            discovered = DiscoveredDevice(
                device_type="BrainFlow",
                device_name=device_name,
                protocol=DeviceProtocol.USB,
                connection_info={},
            )
            assert manager._get_brainflow_board_name(discovered) == expected_board

    @pytest.mark.asyncio
    async def test_context_manager(self, manager):
        """Test async context manager functionality."""
        manager.register_device_type("mock", MockDevice)

        async with manager:
            # Add and connect device
            device = await manager.add_device("device1", "mock")
            await device.connect()
            await device.start_streaming()

            # Start aggregation
            await manager.start_aggregation()

        # After context, everything should be cleaned up
        assert device.disconnect_called
        assert device.streaming is False
        assert manager._aggregation_task is None
        assert len(manager.devices) == 0

    @pytest.mark.asyncio
    async def test_error_handling_in_callbacks(self, manager):
        """Test that errors in callbacks don't break the manager."""
        # Set callback that raises exception
        bad_callback = Mock(side_effect=ValueError("Callback error"))
        manager.set_data_callback(bad_callback)

        # Should handle error gracefully
        packet = Mock(spec=NeuralDataPacket)
        packet.metadata = {}

        # This should not raise
        manager._handle_device_data("device1", packet)

        bad_callback.assert_called_once()
