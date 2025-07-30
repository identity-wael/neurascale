"""Tests for Device Control MCP Server."""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime

from src.mcp.servers.device_control.server import DeviceControlMCPServer
from src.mcp.servers.device_control.handlers import DeviceControlHandlers


class TestDeviceControlMCPServer:
    """Test cases for Device Control MCP Server."""

    @pytest.fixture
    def config(self):
        """Test configuration."""
        return {
            "auth": {"enabled": False},
            "permissions": {"check_enabled": False},
            "rate_limits": {"enabled": False},
            "device_manager": {"api_url": "http://test:8000"},
        }

    @pytest.fixture
    async def server(self, config):
        """Create test server instance."""
        server = DeviceControlMCPServer(config)
        await server.register_tools()
        return server

    @pytest.mark.asyncio
    async def test_server_initialization(self, config):
        """Test server initialization."""
        server = DeviceControlMCPServer(config)
        assert server.name == "neurascale-device-control"
        assert server.version == "1.0.0"
        assert server.config == config
        assert isinstance(server.handlers, DeviceControlHandlers)

    @pytest.mark.asyncio
    async def test_register_tools(self, server):
        """Test tool registration."""
        expected_tools = [
            "list_devices",
            "get_device_info",
            "connect_device",
            "disconnect_device",
            "configure_device",
            "start_recording",
            "stop_recording",
            "check_impedance",
            "monitor_signal_quality",
            "run_device_diagnostics",
            "calibrate_device",
        ]

        for tool_name in expected_tools:
            assert tool_name in server.tools
            tool = server.tools[tool_name]
            assert "handler" in tool
            assert "description" in tool
            assert "input_schema" in tool
            assert "permissions" in tool

    @pytest.mark.asyncio
    async def test_list_devices(self, server):
        """Test list_devices tool."""
        with patch.object(
            server.handlers, "list_devices", new_callable=AsyncMock
        ) as mock_list:
            mock_list.return_value = {
                "devices": [
                    {
                        "id": "device_001",
                        "name": "NeuraLink Pro EEG-128",
                        "type": "EEG",
                        "connected": False,
                        "channel_count": 128,
                        "sampling_rate": 1000,
                    }
                ],
                "total_count": 1,
                "active_connections": 0,
            }

            result = await server._list_devices(device_type="EEG", status="all")

            assert result["total_count"] == 1
            assert len(result["devices"]) == 1
            assert result["devices"][0]["type"] == "EEG"

            mock_list.assert_called_once_with(
                device_type="EEG", status="all", location=None
            )

    @pytest.mark.asyncio
    async def test_connect_device(self, server):
        """Test connect_device tool."""
        with patch.object(
            server.handlers, "connect_device", new_callable=AsyncMock
        ) as mock_connect:
            mock_connect.return_value = {
                "device_id": "device_001",
                "status": "connected",
                "connection_info": {
                    "connected_at": datetime.utcnow().isoformat(),
                    "signal_quality": "Good",
                    "impedance_check_passed": True,
                },
                "message": "Successfully connected to NeuraLink Pro EEG-128",
            }

            result = await server._connect_device(
                device_id="device_001",
                connection_params={"port": "COM3", "baud_rate": 115200},
                verify_connection=True,
            )

            assert result["status"] == "connected"
            assert result["device_id"] == "device_001"
            assert "connection_info" in result

    @pytest.mark.asyncio
    async def test_disconnect_device(self, server):
        """Test disconnect_device tool."""
        with patch.object(
            server.handlers, "disconnect_device", new_callable=AsyncMock
        ) as mock_disconnect:
            mock_disconnect.return_value = {
                "device_id": "device_001",
                "status": "disconnected",
                "connection_duration": 3600.5,
                "session_saved": True,
                "message": "Successfully disconnected from device device_001",
            }

            result = await server._disconnect_device(
                device_id="device_001", force=False, save_session=True
            )

            assert result["status"] == "disconnected"
            assert result["session_saved"] is True

    @pytest.mark.asyncio
    async def test_configure_device(self, server):
        """Test configure_device tool."""
        with patch.object(
            server.handlers, "configure_device", new_callable=AsyncMock
        ) as mock_configure:
            mock_configure.return_value = {
                "device_id": "device_001",
                "configuration_applied": {
                    "sampling_rate": 1000,
                    "enabled_channels": [0, 1, 2, 3, 4, 5, 6, 7],
                },
                "status": "configured",
                "message": "Device configuration updated successfully",
            }

            result = await server._configure_device(
                device_id="device_001",
                sampling_rate=1000,
                channels=list(range(8)),
            )

            assert result["status"] == "configured"
            assert result["configuration_applied"]["sampling_rate"] == 1000

    @pytest.mark.asyncio
    async def test_start_recording(self, server):
        """Test start_recording tool."""
        with patch.object(
            server.handlers, "start_recording", new_callable=AsyncMock
        ) as mock_start:
            mock_start.return_value = {
                "session_id": "rec_device_001_20240115_103045",
                "device_id": "device_001",
                "status": "recording_started",
                "start_time": datetime.utcnow().isoformat(),
                "message": "Recording started on NeuraLink Pro EEG-128",
            }

            result = await server._start_recording(
                device_id="device_001",
                duration=3600,
                session_name="Test Recording",
                patient_id="patient_001",
            )

            assert result["status"] == "recording_started"
            assert "session_id" in result

    @pytest.mark.asyncio
    async def test_stop_recording(self, server):
        """Test stop_recording tool."""
        with patch.object(
            server.handlers, "stop_recording", new_callable=AsyncMock
        ) as mock_stop:
            mock_stop.return_value = {
                "status": "recording_stopped",
                "session_summary": {
                    "session_id": "rec_device_001_20240115_103045",
                    "actual_duration": 3542.7,
                    "data_saved": True,
                    "file_size_mb": 125.3,
                },
                "message": "Recording stopped successfully on device device_001",
            }

            result = await server._stop_recording(
                device_id="device_001", save_data=True, auto_analyze=False
            )

            assert result["status"] == "recording_stopped"
            assert result["session_summary"]["data_saved"] is True

    @pytest.mark.asyncio
    async def test_check_impedance(self, server):
        """Test check_impedance tool."""
        with patch.object(
            server.handlers, "check_impedance", new_callable=AsyncMock
        ) as mock_impedance:
            mock_impedance.return_value = {
                "device_id": "device_001",
                "channels_tested": 8,
                "impedances": {
                    "channel_0": 2500.0,
                    "channel_1": 3200.0,
                    "channel_2": 2800.0,
                },
                "overall_status": "passed",
                "failed_channels": [],
                "recommendations": ["All impedances within acceptable range"],
            }

            result = await server._check_impedance(
                device_id="device_001",
                channels=[0, 1, 2],
                acceptable_threshold=5000,
            )

            assert result["overall_status"] == "passed"
            assert len(result["failed_channels"]) == 0

    @pytest.mark.asyncio
    async def test_monitor_signal_quality(self, server):
        """Test monitor_signal_quality tool."""
        with patch.object(
            server.handlers, "monitor_signal_quality", new_callable=AsyncMock
        ) as mock_monitor:
            mock_monitor.return_value = {
                "monitoring_id": "mon_123",
                "device_id": "device_001",
                "overall_quality_score": 85.5,
                "quality_rating": "Good",
                "results": {
                    "snr": {"average": 25.3, "unit": "dB"},
                    "artifacts": {"total": 3, "rate": 0.3},
                    "noise_level": {"average": 2.1, "unit": "microvolts RMS"},
                },
                "recommendations": ["Signal quality is excellent"],
            }

            result = await server._monitor_signal_quality(
                device_id="device_001",
                duration=10,
                quality_metrics=["snr", "artifacts", "noise_level"],
            )

            assert result["overall_quality_score"] == 85.5
            assert result["quality_rating"] == "Good"

    @pytest.mark.asyncio
    async def test_run_device_diagnostics(self, server):
        """Test run_device_diagnostics tool."""
        with patch.object(
            server.handlers, "run_device_diagnostics", new_callable=AsyncMock
        ) as mock_diagnostics:
            mock_diagnostics.return_value = {
                "diagnostic_id": "diag_456",
                "device_id": "device_001",
                "overall_status": "passed",
                "test_results": {
                    "connectivity": {"status": "passed", "latency_ms": 2.5},
                    "firmware": {"status": "passed", "current_version": "2.1.0"},
                    "battery": {"status": "passed", "level": 85},
                },
                "tests_passed": 3,
                "tests_failed": 0,
            }

            result = await server._run_device_diagnostics(
                device_id="device_001", test_suite="basic", generate_report=True
            )

            assert result["overall_status"] == "passed"
            assert result["tests_passed"] == 3

    @pytest.mark.asyncio
    async def test_calibrate_device(self, server):
        """Test calibrate_device tool."""
        with patch.object(
            server.handlers, "calibrate_device", new_callable=AsyncMock
        ) as mock_calibrate:
            mock_calibrate.return_value = {
                "status": "calibration_completed",
                "calibration_data": {
                    "calibration_id": "cal_789",
                    "device_id": "device_001",
                    "calibration_type": "full",
                    "status": "completed",
                    "valid_until": "2024-02-15T10:30:45",
                },
                "message": "Device device_001 calibrated successfully",
            }

            result = await server._calibrate_device(
                device_id="device_001", calibration_type="full"
            )

            assert result["status"] == "calibration_completed"
            assert result["calibration_data"]["calibration_type"] == "full"


class TestDeviceControlHandlers:
    """Test cases for Device Control Handlers."""

    @pytest.fixture
    def handlers(self):
        """Create test handlers instance."""
        config = {"api_url": "http://test:8000"}
        return DeviceControlHandlers(config)

    @pytest.mark.asyncio
    async def test_list_devices_filtering(self, handlers):
        """Test device listing with filters."""
        result = await handlers.list_devices(device_type="EEG", status="connected")

        assert "devices" in result
        assert "total_count" in result
        assert "active_connections" in result

    @pytest.mark.asyncio
    async def test_connect_device_already_connected(self, handlers):
        """Test connecting an already connected device."""
        # First connect
        await handlers.connect_device("device_001", {})

        # Try to connect again
        with pytest.raises(ValueError) as exc_info:
            await handlers.connect_device("device_001", {})

        assert "already connected" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_disconnect_device_not_connected(self, handlers):
        """Test disconnecting a device that's not connected."""
        with pytest.raises(ValueError) as exc_info:
            await handlers.disconnect_device("device_999")

        assert "not connected" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_start_recording_already_recording(self, handlers):
        """Test starting recording on a device that's already recording."""
        # Connect device first
        await handlers.connect_device("device_001", {})

        # Start recording
        await handlers.start_recording("device_001")

        # Try to start again
        with pytest.raises(ValueError) as exc_info:
            await handlers.start_recording("device_001")

        assert "already recording" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_stop_recording_no_active_recording(self, handlers):
        """Test stopping recording when there's no active recording."""
        # Connect device but don't start recording
        await handlers.connect_device("device_001", {})

        with pytest.raises(ValueError) as exc_info:
            await handlers.stop_recording("device_001")

        assert "No active recording" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_configure_device_invalid_sampling_rate(self, handlers):
        """Test configuring device with invalid sampling rate."""
        # Connect device
        await handlers.connect_device("device_001", {})

        # Invalid rate not in supported rates
        invalid_rate = 9999  # Not in supported rates

        with pytest.raises(ValueError) as exc_info:
            await handlers.configure_device("device_001", sampling_rate=invalid_rate)

        assert "Unsupported sampling rate" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_impedance_check_statistics(self, handlers):
        """Test impedance check returns proper statistics."""
        # Connect device
        await handlers.connect_device("device_001", {})

        result = await handlers.check_impedance("device_001")

        assert "statistics" in result
        assert "mean" in result["statistics"]
        assert "median" in result["statistics"]
        assert "min" in result["statistics"]
        assert "max" in result["statistics"]
        assert "std" in result["statistics"]

    @pytest.mark.asyncio
    async def test_signal_quality_metrics(self, handlers):
        """Test signal quality monitoring metrics."""
        # Connect device
        await handlers.connect_device("device_001", {})

        metrics = ["snr", "artifacts", "drift", "saturation", "noise_level"]
        result = await handlers.monitor_signal_quality(
            "device_001", duration=5, quality_metrics=metrics
        )

        assert "results" in result
        for metric in metrics:
            assert metric in result["results"]

    @pytest.mark.asyncio
    async def test_diagnostics_test_suites(self, handlers):
        """Test different diagnostic test suites."""
        # Connect device
        await handlers.connect_device("device_001", {})

        # Test basic suite
        basic_result = await handlers.run_device_diagnostics(
            "device_001", test_suite="basic"
        )
        assert "connectivity" in basic_result["test_results"]
        assert "firmware" in basic_result["test_results"]
        assert "battery" in basic_result["test_results"]

        # Test extended suite
        extended_result = await handlers.run_device_diagnostics(
            "device_001", test_suite="extended"
        )
        assert "channels" in extended_result["test_results"]
        assert "sampling" in extended_result["test_results"]

        # Test full suite
        full_result = await handlers.run_device_diagnostics(
            "device_001", test_suite="full"
        )
        assert "noise" in full_result["test_results"]
        assert "filters" in full_result["test_results"]
        assert "memory" in full_result["test_results"]

    @pytest.mark.asyncio
    async def test_calibration_types(self, handlers):
        """Test different calibration types."""
        # Connect device
        await handlers.connect_device("device_001", {})

        # Test offset calibration
        offset_result = await handlers.calibrate_device(
            "device_001", calibration_type="offset"
        )
        assert "offset" in offset_result["calibration_data"]["calibration_values"]

        # Test gain calibration
        gain_result = await handlers.calibrate_device(
            "device_001", calibration_type="gain"
        )
        assert "gain" in gain_result["calibration_data"]["calibration_values"]

        # Test full calibration
        full_result = await handlers.calibrate_device(
            "device_001", calibration_type="full"
        )
        assert "offset" in full_result["calibration_data"]["calibration_values"]
        assert "gain" in full_result["calibration_data"]["calibration_values"]
        assert "linearity" in full_result["calibration_data"]["calibration_values"]

    @pytest.mark.asyncio
    async def test_device_capabilities_by_type(self, handlers):
        """Test device capabilities are correct for each device type."""
        device_types = ["EEG", "EMG", "ECG", "fNIRS", "TMS", "tDCS", "HYBRID"]

        for device_type in device_types:
            # Find a device of this type
            devices = await handlers.list_devices(device_type=device_type)
            if devices["devices"]:
                device_id = devices["devices"][0]["id"]
                info = await handlers.get_device_info(
                    device_id, include_capabilities=True
                )

                assert "capabilities" in info
                capabilities = info["capabilities"]

                # Check type-specific capabilities
                if device_type == "EEG":
                    assert "impedance_check" in capabilities
                    assert "reference_types" in capabilities
                elif device_type == "EMG":
                    assert "wireless_range_m" in capabilities
                    assert "battery_life_hours" in capabilities
                elif device_type == "fNIRS":
                    assert "wavelengths_nm" in capabilities
                    assert "source_detector_pairs" in capabilities


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
