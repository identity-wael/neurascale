"""Device Control MCP Server implementation."""

from typing import Dict, Any, List, Optional

from ...core.base_server import BaseNeuralMCPServer
from ...utils.validators import validate_device_params
from .handlers import DeviceControlHandlers


class DeviceControlMCPServer(BaseNeuralMCPServer):
    """MCP server for BCI device control and monitoring."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize Device Control MCP server.
        
        Args:
            config: Server configuration
        """
        super().__init__("neurascale-device-control", "1.0.0", config)
        
        # Initialize handlers
        self.handlers = DeviceControlHandlers(config.get("device_manager", {}))

    async def register_tools(self) -> None:
        """Register all device control tools."""
        
        # Device Discovery and Management
        self.register_tool(
            name="list_devices",
            handler=self._list_devices,
            description="List all available BCI devices with their current status",
            input_schema={
                "type": "object",
                "properties": {
                    "device_type": {
                        "type": "string",
                        "enum": ["EEG", "EMG", "ECG", "fNIRS", "TMS", "tDCS", "HYBRID"],
                        "description": "Filter by device type"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["connected", "disconnected", "all"],
                        "default": "all",
                        "description": "Filter by connection status"
                    },
                    "location": {
                        "type": "string",
                        "description": "Filter by device location/room"
                    }
                },
                "required": []
            },
            permissions=["devices.list", "devices.read"]
        )

        self.register_tool(
            name="get_device_info",
            handler=self._get_device_info,
            description="Get detailed information about a specific device",
            input_schema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "Device identifier"
                    },
                    "include_capabilities": {
                        "type": "boolean",
                        "default": true,
                        "description": "Include device capabilities information"
                    },
                    "include_history": {
                        "type": "boolean",
                        "default": false,
                        "description": "Include recent usage history"
                    }
                },
                "required": ["device_id"]
            },
            permissions=["devices.read"]
        )

        # Device Connection Management
        self.register_tool(
            name="connect_device",
            handler=self._connect_device,
            description="Connect to a BCI device",
            input_schema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "Device identifier"
                    },
                    "connection_params": {
                        "type": "object",
                        "properties": {
                            "port": {"type": "string"},
                            "baud_rate": {"type": "integer"},
                            "timeout": {"type": "number"},
                            "auto_start": {"type": "boolean", "default": false}
                        },
                        "description": "Device-specific connection parameters"
                    },
                    "verify_connection": {
                        "type": "boolean",
                        "default": true,
                        "description": "Verify connection after establishing"
                    }
                },
                "required": ["device_id"]
            },
            permissions=["devices.connect", "devices.control"]
        )

        self.register_tool(
            name="disconnect_device",
            handler=self._disconnect_device,
            description="Disconnect from a BCI device",
            input_schema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "Device identifier"
                    },
                    "force": {
                        "type": "boolean",
                        "default": false,
                        "description": "Force disconnection even if recording"
                    },
                    "save_session": {
                        "type": "boolean",
                        "default": true,
                        "description": "Save any ongoing session before disconnect"
                    }
                },
                "required": ["device_id"]
            },
            permissions=["devices.disconnect", "devices.control"]
        )

        # Device Configuration
        self.register_tool(
            name="configure_device",
            handler=self._configure_device,
            description="Configure device settings and parameters",
            input_schema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "Device identifier"
                    },
                    "sampling_rate": {
                        "type": "integer",
                        "minimum": 100,
                        "maximum": 10000,
                        "description": "Sampling rate in Hz"
                    },
                    "channels": {
                        "type": "array",
                        "items": {"type": "integer", "minimum": 0},
                        "description": "Channels to enable"
                    },
                    "filters": {
                        "type": "object",
                        "properties": {
                            "highpass": {"type": "number", "minimum": 0.1},
                            "lowpass": {"type": "number", "maximum": 1000},
                            "notch": {"type": "number"}
                        },
                        "description": "Hardware filter settings"
                    },
                    "gain": {
                        "type": "number",
                        "minimum": 1,
                        "maximum": 1000,
                        "description": "Amplification gain"
                    }
                },
                "required": ["device_id"]
            },
            permissions=["devices.configure", "devices.control"]
        )

        # Recording Control
        self.register_tool(
            name="start_recording",
            handler=self._start_recording,
            description="Start neural data recording",
            input_schema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "Device identifier"
                    },
                    "duration": {
                        "type": "number",
                        "minimum": 1,
                        "maximum": 7200,
                        "description": "Recording duration in seconds (optional)"
                    },
                    "session_name": {
                        "type": "string",
                        "description": "Name for the recording session"
                    },
                    "patient_id": {
                        "type": "string",
                        "description": "Patient identifier"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Additional session metadata"
                    }
                },
                "required": ["device_id"]
            },
            permissions=["recording.start", "devices.control"]
        )

        self.register_tool(
            name="stop_recording",
            handler=self._stop_recording,
            description="Stop neural data recording",
            input_schema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "Device identifier"
                    },
                    "save_data": {
                        "type": "boolean",
                        "default": true,
                        "description": "Save recorded data"
                    },
                    "auto_analyze": {
                        "type": "boolean",
                        "default": false,
                        "description": "Start automatic analysis after recording"
                    }
                },
                "required": ["device_id"]
            },
            permissions=["recording.stop", "devices.control"]
        )

        # Device Monitoring and Diagnostics
        self.register_tool(
            name="check_impedance",
            handler=self._check_impedance,
            description="Check electrode impedances",
            input_schema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "Device identifier"
                    },
                    "channels": {
                        "type": "array",
                        "items": {"type": "integer", "minimum": 0},
                        "description": "Specific channels to check (optional)"
                    },
                    "test_frequency": {
                        "type": "number",
                        "default": 10,
                        "description": "Test frequency in Hz"
                    },
                    "acceptable_threshold": {
                        "type": "number",
                        "default": 5000,
                        "description": "Acceptable impedance threshold in ohms"
                    }
                },
                "required": ["device_id"]
            },
            permissions=["devices.test", "impedance.check"]
        )

        self.register_tool(
            name="monitor_signal_quality",
            handler=self._monitor_signal_quality,
            description="Monitor real-time signal quality",
            input_schema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "Device identifier"
                    },
                    "duration": {
                        "type": "number",
                        "minimum": 1,
                        "maximum": 300,
                        "default": 10,
                        "description": "Monitoring duration in seconds"
                    },
                    "channels": {
                        "type": "array",
                        "items": {"type": "integer", "minimum": 0},
                        "description": "Channels to monitor"
                    },
                    "quality_metrics": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["snr", "artifacts", "drift", "saturation", "noise_level"]
                        },
                        "default": ["snr", "artifacts", "noise_level"],
                        "description": "Quality metrics to calculate"
                    }
                },
                "required": ["device_id"]
            },
            permissions=["devices.monitor", "signal_quality.check"]
        )

        self.register_tool(
            name="run_device_diagnostics",
            handler=self._run_device_diagnostics,
            description="Run comprehensive device diagnostics",
            input_schema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "Device identifier"
                    },
                    "test_suite": {
                        "type": "string",
                        "enum": ["basic", "extended", "full"],
                        "default": "basic",
                        "description": "Diagnostic test suite to run"
                    },
                    "generate_report": {
                        "type": "boolean",
                        "default": true,
                        "description": "Generate diagnostic report"
                    }
                },
                "required": ["device_id"]
            },
            permissions=["devices.diagnose", "devices.test"]
        )

        # Device Calibration
        self.register_tool(
            name="calibrate_device",
            handler=self._calibrate_device,
            description="Calibrate device settings",
            input_schema={
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "Device identifier"
                    },
                    "calibration_type": {
                        "type": "string",
                        "enum": ["offset", "gain", "full", "channel_specific"],
                        "default": "full",
                        "description": "Type of calibration to perform"
                    },
                    "reference_signal": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["internal", "external", "known"]},
                            "amplitude": {"type": "number"},
                            "frequency": {"type": "number"}
                        },
                        "description": "Reference signal for calibration"
                    },
                    "channels": {
                        "type": "array",
                        "items": {"type": "integer", "minimum": 0},
                        "description": "Channels to calibrate"
                    }
                },
                "required": ["device_id"]
            },
            permissions=["devices.calibrate", "devices.control"]
        )

    # Tool Implementation Methods
    async def _list_devices(self, device_type: Optional[str] = None,
                          status: str = "all",
                          location: Optional[str] = None) -> Dict[str, Any]:
        """List available devices."""
        # Validate device parameters
        params = {"status": status}
        if device_type:
            params["device_type"] = device_type
        validate_device_params(params)
        
        return await self.handlers.list_devices(
            device_type=device_type,
            status=status,
            location=location
        )

    async def _get_device_info(self, device_id: str,
                             include_capabilities: bool = True,
                             include_history: bool = False) -> Dict[str, Any]:
        """Get detailed device information."""
        return await self.handlers.get_device_info(
            device_id=device_id,
            include_capabilities=include_capabilities,
            include_history=include_history
        )

    async def _connect_device(self, device_id: str,
                            connection_params: Optional[Dict[str, Any]] = None,
                            verify_connection: bool = True) -> Dict[str, Any]:
        """Connect to a device."""
        return await self.handlers.connect_device(
            device_id=device_id,
            connection_params=connection_params or {},
            verify_connection=verify_connection
        )

    async def _disconnect_device(self, device_id: str,
                               force: bool = False,
                               save_session: bool = True) -> Dict[str, Any]:
        """Disconnect from a device."""
        return await self.handlers.disconnect_device(
            device_id=device_id,
            force=force,
            save_session=save_session
        )

    async def _configure_device(self, device_id: str,
                              sampling_rate: Optional[int] = None,
                              channels: Optional[List[int]] = None,
                              filters: Optional[Dict[str, float]] = None,
                              gain: Optional[float] = None) -> Dict[str, Any]:
        """Configure device settings."""
        return await self.handlers.configure_device(
            device_id=device_id,
            sampling_rate=sampling_rate,
            channels=channels,
            filters=filters,
            gain=gain
        )

    async def _start_recording(self, device_id: str,
                             duration: Optional[float] = None,
                             session_name: Optional[str] = None,
                             patient_id: Optional[str] = None,
                             metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Start recording session."""
        return await self.handlers.start_recording(
            device_id=device_id,
            duration=duration,
            session_name=session_name,
            patient_id=patient_id,
            metadata=metadata or {}
        )

    async def _stop_recording(self, device_id: str,
                            save_data: bool = True,
                            auto_analyze: bool = False) -> Dict[str, Any]:
        """Stop recording session."""
        return await self.handlers.stop_recording(
            device_id=device_id,
            save_data=save_data,
            auto_analyze=auto_analyze
        )

    async def _check_impedance(self, device_id: str,
                             channels: Optional[List[int]] = None,
                             test_frequency: float = 10,
                             acceptable_threshold: float = 5000) -> Dict[str, Any]:
        """Check electrode impedances."""
        return await self.handlers.check_impedance(
            device_id=device_id,
            channels=channels,
            test_frequency=test_frequency,
            acceptable_threshold=acceptable_threshold
        )

    async def _monitor_signal_quality(self, device_id: str,
                                    duration: float = 10,
                                    channels: Optional[List[int]] = None,
                                    quality_metrics: List[str] = None) -> Dict[str, Any]:
        """Monitor signal quality."""
        if quality_metrics is None:
            quality_metrics = ["snr", "artifacts", "noise_level"]
            
        return await self.handlers.monitor_signal_quality(
            device_id=device_id,
            duration=duration,
            channels=channels,
            quality_metrics=quality_metrics
        )

    async def _run_device_diagnostics(self, device_id: str,
                                    test_suite: str = "basic",
                                    generate_report: bool = True) -> Dict[str, Any]:
        """Run device diagnostics."""
        return await self.handlers.run_device_diagnostics(
            device_id=device_id,
            test_suite=test_suite,
            generate_report=generate_report
        )

    async def _calibrate_device(self, device_id: str,
                              calibration_type: str = "full",
                              reference_signal: Optional[Dict[str, Any]] = None,
                              channels: Optional[List[int]] = None) -> Dict[str, Any]:
        """Calibrate device."""
        return await self.handlers.calibrate_device(
            device_id=device_id,
            calibration_type=calibration_type,
            reference_signal=reference_signal,
            channels=channels
        )