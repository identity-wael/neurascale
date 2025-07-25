"""Unit tests for device discovery service."""

import pytest
import asyncio
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from datetime import datetime

from src.devices.device_discovery import (
    DeviceDiscoveryService,
    DiscoveredDevice,
    DeviceProtocol,
)


class TestDiscoveredDevice:
    """Test suite for DiscoveredDevice dataclass."""

    def test_discovered_device_creation(self):
        """Test creating a discovered device."""
        device = DiscoveredDevice(
            device_type="OpenBCI",
            device_name="OpenBCI Cyton",
            protocol=DeviceProtocol.SERIAL,
            connection_info={"port": "/dev/ttyUSB0"},
            metadata={"channels": 8},
        )

        assert device.device_type == "OpenBCI"
        assert device.device_name == "OpenBCI Cyton"
        assert device.protocol == DeviceProtocol.SERIAL
        assert device.connection_info["port"] == "/dev/ttyUSB0"
        assert device.metadata["channels"] == 8
        assert isinstance(device.discovered_at, datetime)

    def test_unique_id_serial(self):
        """Test unique ID generation for serial devices."""
        device = DiscoveredDevice(
            device_type="OpenBCI",
            device_name="OpenBCI Cyton",
            protocol=DeviceProtocol.SERIAL,
            connection_info={"port": "/dev/ttyUSB0"},
        )

        assert device.unique_id == "OpenBCI_/dev/ttyUSB0"

    def test_unique_id_bluetooth(self):
        """Test unique ID generation for Bluetooth devices."""
        device = DiscoveredDevice(
            device_type="Ganglion",
            device_name="OpenBCI Ganglion",
            protocol=DeviceProtocol.BLUETOOTH,
            connection_info={"address": "00:11:22:33:44:55"},
        )

        assert device.unique_id == "Ganglion_00:11:22:33:44:55"

    def test_unique_id_wifi(self):
        """Test unique ID generation for WiFi devices."""
        device = DiscoveredDevice(
            device_type="Neurosity",
            device_name="Neurosity Crown",
            protocol=DeviceProtocol.WIFI,
            connection_info={"ip": "192.168.1.100"},
        )

        assert device.unique_id == "Neurosity_192.168.1.100"

    def test_unique_id_lsl(self):
        """Test unique ID generation for LSL devices."""
        device = DiscoveredDevice(
            device_type="LSL",
            device_name="LSL Stream",
            protocol=DeviceProtocol.LSL,
            connection_info={"name": "TestStream"},
        )

        assert device.unique_id == "LSL_TestStream"


class TestDeviceDiscoveryService:
    """Test suite for DeviceDiscoveryService."""

    @pytest.fixture
    def discovery_service(self):
        """Create a discovery service instance."""
        return DeviceDiscoveryService()

    def test_initialization(self, discovery_service):
        """Test discovery service initialization."""
        assert len(discovery_service._discovered_devices) == 0
        assert len(discovery_service._discovery_callbacks) == 0
        assert discovery_service._is_scanning is False
        assert discovery_service._scan_task is None

    def test_add_remove_callbacks(self, discovery_service):
        """Test adding and removing discovery callbacks."""
        callback1 = Mock()
        callback2 = Mock()

        # Add callbacks
        discovery_service.add_discovery_callback(callback1)
        discovery_service.add_discovery_callback(callback2)
        assert len(discovery_service._discovery_callbacks) == 2

        # Remove callback
        discovery_service.remove_discovery_callback(callback1)
        assert len(discovery_service._discovery_callbacks) == 1
        assert callback2 in discovery_service._discovery_callbacks

    def test_notify_device_discovered(self, discovery_service):
        """Test device discovery notification."""
        callback = Mock()
        discovery_service.add_discovery_callback(callback)

        device = DiscoveredDevice(
            device_type="Test",
            device_name="Test Device",
            protocol=DeviceProtocol.USB,
            connection_info={},
        )

        discovery_service._notify_device_discovered(device)

        # Check callback was called
        callback.assert_called_once_with(device)

        # Check device was stored
        assert device.unique_id in discovery_service._discovered_devices
        assert discovery_service._discovered_devices[device.unique_id] == device

    def test_notify_duplicate_device(self, discovery_service):
        """Test that duplicate devices are not notified twice."""
        callback = Mock()
        discovery_service.add_discovery_callback(callback)

        device = DiscoveredDevice(
            device_type="Test",
            device_name="Test Device",
            protocol=DeviceProtocol.USB,
            connection_info={},
        )

        # Notify twice
        discovery_service._notify_device_discovered(device)
        discovery_service._notify_device_discovered(device)

        # Callback should only be called once
        callback.assert_called_once()

    def test_get_discovered_devices(self, discovery_service):
        """Test getting list of discovered devices."""
        devices = [
            DiscoveredDevice(
                device_type=f"Type{i}",
                device_name=f"Device{i}",
                protocol=DeviceProtocol.USB,
                connection_info={},
            )
            for i in range(3)
        ]

        for device in devices:
            discovery_service._notify_device_discovered(device)

        discovered = discovery_service.get_discovered_devices()
        assert len(discovered) == 3
        assert all(d in discovered for d in devices)

    @pytest.mark.asyncio
    async def test_discover_serial_devices(self, discovery_service):
        """Test serial device discovery."""
        # Mock serial ports
        mock_port1 = MagicMock()
        mock_port1.device = "/dev/ttyUSB0"
        mock_port1.description = "OpenBCI Cyton"
        mock_port1.hwid = "USB VID:PID=0403:6001"
        mock_port1.vid = 0x0403
        mock_port1.pid = 0x6001
        mock_port1.manufacturer = "FTDI"
        mock_port1.product = "FT232R"
        mock_port1.serial_number = "A1234567"

        mock_port2 = MagicMock()
        mock_port2.device = "/dev/ttyUSB1"
        mock_port2.description = "Arduino Uno"
        mock_port2.hwid = "USB VID:PID=2341:0043"
        mock_port2.vid = 0x2341
        mock_port2.pid = 0x0043
        mock_port2.manufacturer = "Arduino"
        mock_port2.product = "Arduino Uno"
        mock_port2.serial_number = "B7654321"

        with patch(
            "serial.tools.list_ports.comports", return_value=[mock_port1, mock_port2]
        ):
            await discovery_service._discover_serial_devices()

        devices = discovery_service.get_discovered_devices()
        assert len(devices) >= 2

        # Check OpenBCI device
        openbci_devices = [d for d in devices if d.device_type == "OpenBCI"]
        assert len(openbci_devices) > 0
        assert openbci_devices[0].protocol == DeviceProtocol.SERIAL
        assert openbci_devices[0].connection_info["port"] == "/dev/ttyUSB0"

    @pytest.mark.asyncio
    @patch("src.devices.device_discovery.BLUETOOTH_AVAILABLE", True)
    async def test_discover_bluetooth_devices(self, discovery_service):
        """Test Bluetooth device discovery."""
        # Mock bluetooth discovery
        mock_devices = [
            ("00:11:22:33:44:55", "Ganglion-1234"),
            ("AA:BB:CC:DD:EE:FF", "Muse-S-5678"),
            ("11:22:33:44:55:66", "Random Device"),
        ]

        with patch("bluetooth.discover_devices", return_value=mock_devices):
            await discovery_service._discover_bluetooth_devices()

        devices = discovery_service.get_discovered_devices()

        # Check Ganglion device
        ganglion_devices = [d for d in devices if "Ganglion" in d.device_name]
        assert len(ganglion_devices) == 1
        assert ganglion_devices[0].protocol == DeviceProtocol.BLUETOOTH
        assert ganglion_devices[0].connection_info["address"] == "00:11:22:33:44:55"

        # Check Muse device
        muse_devices = [d for d in devices if "Muse" in d.device_name]
        assert len(muse_devices) == 1
        assert muse_devices[0].protocol == DeviceProtocol.BLUETOOTH

    @pytest.mark.asyncio
    @patch("src.devices.device_discovery.LSL_AVAILABLE", True)
    async def test_discover_lsl_devices(self, discovery_service):
        """Test LSL stream discovery."""
        # Mock LSL stream info
        mock_stream1 = MagicMock()
        mock_stream1.name.return_value = "TestEEG"
        mock_stream1.type.return_value = "EEG"
        mock_stream1.hostname.return_value = "localhost"
        mock_stream1.uid.return_value = "uid123"
        mock_stream1.channel_count.return_value = 8
        mock_stream1.nominal_srate.return_value = 256.0
        mock_stream1.channel_format.return_value = "float32"

        with patch("pylsl.resolve_streams", return_value=[mock_stream1]):
            await discovery_service._discover_lsl_devices()

        devices = discovery_service.get_discovered_devices()
        lsl_devices = [d for d in devices if d.device_type == "LSL"]

        assert len(lsl_devices) == 1
        assert lsl_devices[0].protocol == DeviceProtocol.LSL
        assert lsl_devices[0].connection_info["name"] == "TestEEG"
        assert lsl_devices[0].metadata["channel_count"] == 8
        assert lsl_devices[0].metadata["sampling_rate"] == 256.0

    @pytest.mark.asyncio
    @patch("src.devices.device_discovery.BRAINFLOW_AVAILABLE", True)
    async def test_discover_brainflow_devices(self, discovery_service):
        """Test BrainFlow device discovery."""
        await discovery_service._discover_brainflow_devices()

        devices = discovery_service.get_discovered_devices()
        brainflow_devices = [d for d in devices if d.device_type == "BrainFlow"]

        # Should always find synthetic board
        assert len(brainflow_devices) >= 1
        synthetic = [d for d in brainflow_devices if "Synthetic" in d.device_name]
        assert len(synthetic) == 1
        assert synthetic[0].metadata.get("is_synthetic") is True

    @pytest.mark.asyncio
    async def test_start_stop_discovery(self, discovery_service):
        """Test starting and stopping discovery."""
        # Start discovery
        await discovery_service.start_discovery()
        assert discovery_service._is_scanning is True
        assert discovery_service._scan_task is not None

        # Try to start again (should log warning)
        await discovery_service.start_discovery()

        # Stop discovery
        await discovery_service.stop_discovery()
        assert discovery_service._is_scanning is False
        assert discovery_service._scan_task is None

    @pytest.mark.asyncio
    async def test_quick_scan(self, discovery_service):
        """Test quick scan functionality."""
        # Mock some discoveries
        with patch.object(
            discovery_service, "_discover_serial_devices", new_callable=AsyncMock
        ):
            with patch.object(
                discovery_service, "_discover_brainflow_devices", new_callable=AsyncMock
            ):
                devices = await discovery_service.quick_scan(timeout=0.1)

        # Should clear previous devices and return new ones
        assert isinstance(devices, list)

    @pytest.mark.asyncio
    async def test_discovery_with_specific_protocols(self, discovery_service):
        """Test discovery with specific protocols only."""
        # Mock discovery methods
        mock_serial = AsyncMock()
        mock_bluetooth = AsyncMock()

        discovery_service._discover_serial_devices = mock_serial
        discovery_service._discover_bluetooth_devices = mock_bluetooth

        # Start discovery with only serial protocol
        await discovery_service.start_discovery(protocols=[DeviceProtocol.SERIAL])
        await asyncio.sleep(0.1)
        await discovery_service.stop_discovery()

        # Only serial discovery should be called
        mock_serial.assert_called()
        mock_bluetooth.assert_not_called()

    def test_callback_error_handling(self, discovery_service):
        """Test that callback errors don't break discovery."""
        # Add callback that raises exception
        bad_callback = Mock(side_effect=ValueError("Test error"))
        good_callback = Mock()

        discovery_service.add_discovery_callback(bad_callback)
        discovery_service.add_discovery_callback(good_callback)

        device = DiscoveredDevice(
            device_type="Test",
            device_name="Test Device",
            protocol=DeviceProtocol.USB,
            connection_info={},
        )

        # Should handle error and still call good callback
        discovery_service._notify_device_discovered(device)

        bad_callback.assert_called_once()
        good_callback.assert_called_once()

        # Device should still be registered
        assert device.unique_id in discovery_service._discovered_devices
