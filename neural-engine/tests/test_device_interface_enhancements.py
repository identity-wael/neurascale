"""Comprehensive tests for device interface layer enhancements."""

import pytest
import asyncio
import numpy as np
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timezone
import json

from src.devices.device_manager import DeviceManager
from src.devices.interfaces.base_device import DeviceState, DeviceCapabilities
from src.devices.implementations.brainflow_device import BrainFlowDevice
from src.devices.device_notifications import (
    DeviceNotificationService,
    NotificationType,
    DeviceNotification,
)
from src.devices.signal_quality import (
    SignalQualityMonitor,
    SignalQualityLevel,
    SignalQualityMetrics,
    ImpedanceResult,
)
from src.devices.device_discovery import (
    DeviceDiscoveryService,
    DiscoveredDevice,
    DeviceProtocol,
)


@pytest.fixture
def device_manager():
    """Create a device manager instance."""
    return DeviceManager()


@pytest.fixture
def mock_brainflow():
    """Mock BrainFlow dependencies."""
    with patch(
        "src.devices.implementations.brainflow_device.BRAINFLOW_AVAILABLE", True
    ):
        with patch(
            "src.devices.implementations.brainflow_device.BoardShim"
        ) as mock_board:
            with patch(
                "src.devices.implementations.brainflow_device.BoardIds"
            ) as mock_ids:
                mock_ids.SYNTHETIC_BOARD = -1
                mock_ids.CYTON_BOARD = 0
                mock_ids.GANGLION_BOARD = 1
                yield mock_board, mock_ids


@pytest.fixture
async def notification_service():
    """Create a notification service instance."""
    service = DeviceNotificationService()
    await service.start()
    yield service
    await service.stop()


@pytest.fixture
def signal_quality_monitor():
    """Create a signal quality monitor."""
    return SignalQualityMonitor(sampling_rate=250.0, line_freq=60.0)


class TestBrainFlowDeviceEnhancements:
    """Test BrainFlow device enhancements."""

    @pytest.mark.asyncio
    async def test_impedance_checking_cyton(self, mock_brainflow):
        """Test impedance checking for Cyton board."""
        mock_board_shim, mock_ids = mock_brainflow

        # Create device
        device = BrainFlowDevice(board_name="cyton")

        # Mock board instance
        mock_board_instance = MagicMock()
        mock_board_instance.is_prepared.return_value = True
        mock_board_instance.config_board = MagicMock()
        mock_board_instance.get_board_data.return_value = np.random.randn(32, 10)

        mock_board_shim.return_value = mock_board_instance
        mock_board_shim.get_sampling_rate.return_value = 250.0
        mock_board_shim.get_eeg_channels.return_value = list(range(8))
        mock_board_shim.get_emg_channels.return_value = []
        mock_board_shim.get_accel_channels.return_value = []
        mock_board_shim.get_timestamp_channel.return_value = 22

        # Connect device
        await device.connect()
        assert device.state == DeviceState.CONNECTED

        # Check impedance
        impedance_results = await device.check_impedance([0, 1, 2])

        # Verify results
        assert len(impedance_results) == 3
        assert all(0 < imp < 100000 for imp in impedance_results.values())

        # Verify board configuration was called
        assert mock_board_instance.config_board.called

    @pytest.mark.asyncio
    async def test_impedance_checking_ganglion(self, mock_brainflow):
        """Test impedance checking for Ganglion board."""
        mock_board_shim, mock_ids = mock_brainflow

        # Create device
        device = BrainFlowDevice(board_name="ganglion")

        # Mock board instance
        mock_board_instance = MagicMock()
        mock_board_instance.is_prepared.return_value = True
        mock_board_instance.config_board = MagicMock()
        mock_board_instance.get_board_data.return_value = np.random.randn(16, 5) * 50

        mock_board_shim.return_value = mock_board_instance
        mock_board_shim.get_sampling_rate.return_value = 200.0
        mock_board_shim.get_eeg_channels.return_value = list(range(4))
        mock_board_shim.get_emg_channels.return_value = []
        mock_board_shim.get_accel_channels.return_value = [5, 6, 7]
        mock_board_shim.get_timestamp_channel.return_value = 15

        # Connect device
        await device.connect()

        # Check impedance
        impedance_results = await device.check_impedance()

        # Verify results for all channels
        assert len(impedance_results) == 4
        assert all(isinstance(imp, float) for imp in impedance_results.values())

    @pytest.mark.asyncio
    async def test_signal_quality_monitoring(self, mock_brainflow):
        """Test signal quality monitoring."""
        mock_board_shim, mock_ids = mock_brainflow

        # Create device
        device = BrainFlowDevice(board_name="synthetic")

        # Mock board instance
        mock_board_instance = MagicMock()
        mock_board_instance.is_prepared.return_value = True

        # Generate synthetic EEG data with known characteristics
        n_channels = 8
        n_samples = 250  # 1 second at 250Hz

        # Create clean signal with some noise
        t = np.linspace(0, 1, n_samples)
        clean_signal = 50 * np.sin(2 * np.pi * 10 * t)  # 10Hz alpha
        noise = np.random.randn(n_samples) * 5
        test_data = np.zeros((32, n_samples))

        for i in range(n_channels):
            test_data[i, :] = clean_signal + noise

        mock_board_instance.get_board_data.return_value = test_data

        mock_board_shim.return_value = mock_board_instance
        mock_board_shim.get_sampling_rate.return_value = 250.0
        mock_board_shim.get_eeg_channels.return_value = list(range(n_channels))
        mock_board_shim.get_emg_channels.return_value = []
        mock_board_shim.get_accel_channels.return_value = []
        mock_board_shim.get_timestamp_channel.return_value = 22

        # Connect and start streaming
        await device.connect()
        await device.start_streaming()

        # Get signal quality
        quality_metrics = await device.get_signal_quality([0, 1])

        # Verify metrics
        assert len(quality_metrics) == 2
        for channel_id, metrics in quality_metrics.items():
            assert isinstance(metrics, SignalQualityMetrics)
            assert metrics.channel_id == channel_id
            assert metrics.snr_db > 0
            assert metrics.rms_amplitude > 0
            assert metrics.quality_level in SignalQualityLevel

        await device.stop_streaming()
        await device.disconnect()


class TestDeviceNotifications:
    """Test device notification system."""

    @pytest.mark.asyncio
    async def test_notification_service_lifecycle(self, notification_service):
        """Test notification service start/stop."""
        assert notification_service._is_running
        assert notification_service._broadcast_task is not None

        await notification_service.stop()
        assert not notification_service._is_running

    @pytest.mark.asyncio
    async def test_device_state_notifications(self, notification_service):
        """Test device state change notifications."""
        # Mock WebSocket
        mock_websocket = AsyncMock()
        await notification_service.connect(mock_websocket)

        # Send state change notification
        await notification_service.notify_device_state_change(
            "test_device", DeviceState.DISCONNECTED, DeviceState.CONNECTED
        )

        # Allow time for notification to be sent
        await asyncio.sleep(0.1)

        # Verify notification was sent
        mock_websocket.send_text.assert_called()
        sent_data = json.loads(mock_websocket.send_text.call_args[0][0])
        assert sent_data["type"] == NotificationType.DEVICE_CONNECTED.value
        assert sent_data["device_id"] == "test_device"

    @pytest.mark.asyncio
    async def test_impedance_notification(self, notification_service):
        """Test impedance check completion notification."""
        mock_websocket = AsyncMock()
        await notification_service.connect(mock_websocket)

        impedance_results = {0: 5000.0, 1: 8000.0, 2: 15000.0}
        quality_summary = {
            "total_channels": 3,
            "good_channels": 2,
            "fair_channels": 1,
            "poor_channels": 0,
        }

        await notification_service.notify_impedance_check_complete(
            "test_device", impedance_results, quality_summary
        )

        await asyncio.sleep(0.1)

        mock_websocket.send_text.assert_called()
        sent_data = json.loads(mock_websocket.send_text.call_args[0][0])
        assert sent_data["type"] == NotificationType.IMPEDANCE_CHECK_COMPLETE.value
        assert sent_data["data"]["impedance_values"] == impedance_results

    @pytest.mark.asyncio
    async def test_error_notifications(self, notification_service):
        """Test error notifications."""
        mock_websocket = AsyncMock()
        await notification_service.connect(mock_websocket)

        test_error = RuntimeError("Device communication error")

        await notification_service.notify_device_error(
            "test_device", test_error, {"context": "during_streaming"}
        )

        await asyncio.sleep(0.1)

        mock_websocket.send_text.assert_called()
        sent_data = json.loads(mock_websocket.send_text.call_args[0][0])
        assert sent_data["type"] == NotificationType.DEVICE_ERROR.value
        assert sent_data["severity"] == "error"
        assert "RuntimeError" in sent_data["data"]["error_type"]


class TestDeviceDiscoveryEnhancements:
    """Test device discovery enhancements."""

    @pytest.mark.asyncio
    async def test_serial_device_discovery(self):
        """Test serial device discovery."""
        discovery_service = DeviceDiscoveryService()

        # Mock serial ports
        with patch("serial.tools.list_ports.comports") as mock_comports:
            mock_port = MagicMock()
            mock_port.device = "/dev/ttyUSB0"
            mock_port.description = "OpenBCI Cyton"
            mock_port.hwid = "USB VID:PID=0403:6015"
            mock_port.vid = 0x0403
            mock_port.pid = 0x6015
            mock_port.manufacturer = "FTDI"
            mock_port.product = "FT231X USB UART"
            mock_port.serial_number = "12345"

            mock_comports.return_value = [mock_port]

            # Discover devices
            devices = await discovery_service.quick_scan(timeout=1.0)

            # Verify discovery
            assert len(devices) >= 1  # At least our mocked device

            # Find our device
            openbci_devices = [d for d in devices if d.device_type == "OpenBCI"]
            assert len(openbci_devices) == 1

            device = openbci_devices[0]
            assert device.protocol == DeviceProtocol.SERIAL
            assert device.connection_info["port"] == "/dev/ttyUSB0"

    @pytest.mark.asyncio
    async def test_bluetooth_device_discovery(self):
        """Test Bluetooth device discovery."""
        discovery_service = DeviceDiscoveryService()

        # Mock Bluetooth discovery
        with patch("src.devices.device_discovery.BLUETOOTH_AVAILABLE", True):
            with patch(
                "src.devices.device_discovery.bluetooth.discover_devices"
            ) as mock_discover:
                mock_discover.return_value = [
                    ("00:11:22:33:44:55", "Ganglion-1234"),
                    ("AA:BB:CC:DD:EE:FF", "Muse-5678"),
                ]

                # Discover devices
                await discovery_service._discover_bluetooth_devices()
                devices = discovery_service.get_discovered_devices()

                # Verify Bluetooth devices found
                bt_devices = [
                    d for d in devices if d.protocol == DeviceProtocol.BLUETOOTH
                ]
                assert len(bt_devices) == 2

                # Check device types
                device_types = {d.device_type for d in bt_devices}
                assert "OpenBCI" in device_types  # Ganglion
                assert "Muse" in device_types


class TestSignalQualityMonitor:
    """Test signal quality monitoring."""

    def test_snr_calculation(self, signal_quality_monitor):
        """Test SNR calculation."""
        # Generate test signal
        fs = 250
        duration = 1
        t = np.linspace(0, duration, fs * duration)

        # Clean signal (10 Hz)
        signal = 100 * np.sin(2 * np.pi * 10 * t)
        # Add noise
        noise = np.random.randn(len(signal)) * 10
        noisy_signal = signal + noise

        metrics = signal_quality_monitor.assess_signal_quality(noisy_signal, 0)

        assert metrics.snr_db > 10  # Should have reasonable SNR
        assert metrics.channel_id == 0
        assert metrics.quality_level != SignalQualityLevel.BAD

    def test_impedance_assessment(self, signal_quality_monitor):
        """Test impedance quality assessment."""
        # Test various impedance values
        test_cases = [
            (2000, SignalQualityLevel.EXCELLENT),
            (8000, SignalQualityLevel.GOOD),
            (15000, SignalQualityLevel.FAIR),
            (30000, SignalQualityLevel.POOR),
            (60000, SignalQualityLevel.BAD),
        ]

        for impedance, expected_level in test_cases:
            result = signal_quality_monitor.assess_impedance(impedance, 0)
            assert result.impedance_ohms == impedance
            assert result.quality_level == expected_level
            assert result.channel_id == 0

    def test_line_noise_detection(self, signal_quality_monitor):
        """Test line noise detection."""
        fs = 250
        duration = 1
        t = np.linspace(0, duration, fs * duration)

        # Signal with strong 60Hz component
        signal = 50 * np.sin(2 * np.pi * 10 * t)  # 10Hz base
        line_noise = 100 * np.sin(2 * np.pi * 60 * t)  # Strong 60Hz
        noisy_signal = signal + line_noise

        metrics = signal_quality_monitor.assess_signal_quality(noisy_signal, 0)

        # Should detect high line noise
        assert metrics.line_noise_power > 0.1  # Significant line noise


class TestDeviceManagerIntegration:
    """Test device manager integration with enhancements."""

    @pytest.mark.asyncio
    async def test_device_impedance_with_notifications(self, device_manager):
        """Test impedance checking with notifications."""
        # Start notification service
        await device_manager.start_notification_service()

        # Add synthetic device
        with patch(
            "src.devices.implementations.brainflow_device.BRAINFLOW_AVAILABLE", True
        ):
            device = await device_manager.add_device(
                "test_device", "brainflow", board_name="synthetic"
            )

            # Mock device methods
            device.check_impedance = AsyncMock(return_value={0: 5000, 1: 8000})
            device.is_connected = Mock(return_value=True)

            # Perform impedance check
            results = await device_manager.check_device_impedance("test_device")

            assert len(results) == 2
            assert results[0] == 5000
            assert results[1] == 8000

        await device_manager.stop_notification_service()

    @pytest.mark.asyncio
    async def test_device_discovery_integration(self, device_manager):
        """Test device discovery with notifications."""
        # Mock discovery results
        with patch.object(device_manager.discovery_service, "quick_scan") as mock_scan:
            mock_device = DiscoveredDevice(
                device_type="OpenBCI",
                device_name="OpenBCI Cyton",
                protocol=DeviceProtocol.SERIAL,
                connection_info={"port": "/dev/ttyUSB0"},
            )
            mock_scan.return_value = [mock_device]

            # Discover devices
            discovered = await device_manager.auto_discover_devices(timeout=1.0)

            assert len(discovered) == 1
            assert discovered[0]["device_type"] == "openbci"
            assert discovered[0]["protocol"] == "serial"

    @pytest.mark.asyncio
    async def test_health_monitoring_integration(self, device_manager):
        """Test health monitoring with device manager."""
        # Add device
        with patch("src.devices.implementations.synthetic_device.SyntheticDevice"):
            await device_manager.add_device("test_device", "synthetic")

            # Start health monitoring
            await device_manager.start_health_monitoring()

            # Get health status
            health = device_manager.get_device_health("test_device")

            assert "status" in health
            assert health["status"] in ["healthy", "degraded", "unhealthy"]

            await device_manager.stop_health_monitoring()


@pytest.mark.asyncio
async def test_full_device_lifecycle():
    """Test complete device lifecycle with all enhancements."""
    async with DeviceManager() as manager:
        # Start services
        await manager.start_notification_service()
        await manager.start_health_monitoring()

        # Mock BrainFlow
        with patch(
            "src.devices.implementations.brainflow_device.BRAINFLOW_AVAILABLE", True
        ):
            # Add device
            device = await manager.add_device(
                "test_device", "brainflow", board_name="synthetic"
            )

            # Mock device methods
            device.connect = AsyncMock(return_value=True)
            device.is_connected = Mock(return_value=True)
            device.get_capabilities = Mock(
                return_value=DeviceCapabilities(
                    supported_sampling_rates=[250.0],
                    max_channels=8,
                    signal_types=[],
                    has_impedance_check=True,
                )
            )
            device.check_impedance = AsyncMock(
                return_value={i: 5000 + i * 1000 for i in range(8)}
            )
            device.start_streaming = AsyncMock()
            device.stop_streaming = AsyncMock()
            device.disconnect = AsyncMock()

            # Connect
            await manager.connect_device("test_device")

            # Check impedance
            impedance = await manager.check_device_impedance("test_device")
            assert len(impedance) == 8

            # Start streaming
            await manager.start_streaming(["test_device"])

            # Stop streaming
            await manager.stop_streaming(["test_device"])

            # Disconnect
            await manager.disconnect_device("test_device")

            # Remove device
            await manager.remove_device("test_device")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
