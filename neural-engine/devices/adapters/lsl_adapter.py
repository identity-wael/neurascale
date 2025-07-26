"""LSL Adapter for NeuraScale Neural Engine.

This adapter provides native Lab Streaming Layer (LSL) device support
for real-time data streaming from LSL-compatible devices.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

try:
    import pylsl  # noqa: F401

    LSL_AVAILABLE = True
except ImportError:
    LSL_AVAILABLE = False

from ..base import (
    BaseDevice,
    DeviceInfo,
    DeviceType,
    DeviceStatus,
    ConnectionType,
    DataSample,
)
from ..lsl_integration import LSLIntegration, LSLStreamInfo

logger = logging.getLogger(__name__)


class LSLAdapter(BaseDevice):
    """LSL device adapter for native LSL stream integration."""

    def __init__(self, device_info: DeviceInfo, lsl_integration: LSLIntegration = None):
        """Initialize LSL adapter.

        Args:
            device_info: Device information
            lsl_integration: LSL integration service (optional)
        """
        if not LSL_AVAILABLE:
            raise ImportError("pylsl is required for LSL adapter")

        super().__init__(device_info)

        self.lsl_integration = lsl_integration or LSLIntegration()
        self.stream_name = device_info.connection_params.get(
            "stream_name", device_info.model
        )
        self.stream_type = device_info.connection_params.get("stream_type", "EEG")

        # LSL-specific state
        self.inlet_connected = False
        self.outlet_created = False
        self.stream_info: Optional[LSLStreamInfo] = None

        # Data processing
        self.sample_count = 0
        self.last_data_time = datetime.utcnow()

        # Configuration
        self.buffer_size = device_info.connection_params.get("buffer_size", 1000)
        self.timeout_seconds = device_info.connection_params.get("timeout", 1.0)

        logger.info(f"LSLAdapter initialized for stream: {self.stream_name}")

    async def connect(self) -> bool:
        """Connect to LSL stream."""
        try:
            await self.update_status(DeviceStatus.CONNECTING)

            # Start LSL integration if not running
            if not self.lsl_integration.is_running:
                await self.lsl_integration.start()

            # Discover available streams
            streams = await self.lsl_integration.discover_streams()

            # Find our target stream
            target_stream = None
            for stream in streams:
                if (
                    stream.name == self.stream_name
                    or stream.stream_type.value == self.stream_type
                ):
                    target_stream = stream
                    break

            if not target_stream:
                logger.error(f"LSL stream not found: {self.stream_name}")
                await self.update_status(DeviceStatus.ERROR)
                return False

            self.stream_info = target_stream

            # Update device info with stream details
            self.device_info.channel_count = target_stream.channel_count
            self.device_info.sampling_rate = target_stream.sampling_rate
            self.device_info.connection_type = ConnectionType.LSL

            # Create inlet
            success = await self.lsl_integration.create_inlet(
                self.stream_name, self.buffer_size, self.timeout_seconds
            )

            if success:
                self.inlet_connected = True
                self.is_connected = True

                # Register for data callbacks
                self.lsl_integration.add_data_callback(self._handle_lsl_data)

                await self.update_status(DeviceStatus.CONNECTED)
                self._emit_event("lsl_connected", {"stream_name": self.stream_name})

                logger.info(f"Connected to LSL stream: {self.stream_name}")
                return True
            else:
                await self.update_status(DeviceStatus.ERROR)
                return False

        except Exception as e:
            logger.error(f"Error connecting to LSL stream: {str(e)}")
            await self.update_status(DeviceStatus.ERROR)
            return False

    async def disconnect(self) -> bool:
        """Disconnect from LSL stream."""
        try:
            if self.inlet_connected:
                # Disconnect inlet
                success = await self.lsl_integration.disconnect_inlet(self.stream_name)
                if success:
                    self.inlet_connected = False

            self.is_connected = False
            await self.update_status(DeviceStatus.DISCONNECTED)

            self._emit_event("lsl_disconnected", {"stream_name": self.stream_name})
            logger.info(f"Disconnected from LSL stream: {self.stream_name}")
            return True

        except Exception as e:
            logger.error(f"Error disconnecting from LSL stream: {str(e)}")
            return False

    async def start_streaming(self) -> bool:
        """Start data streaming from LSL."""
        if not self.is_connected:
            logger.error("Device not connected")
            return False

        try:
            self.is_streaming = True
            await self.update_status(DeviceStatus.STREAMING)

            self._emit_event("lsl_streaming_started", {"stream_name": self.stream_name})
            logger.info(f"Started streaming from LSL: {self.stream_name}")
            return True

        except Exception as e:
            logger.error(f"Error starting LSL streaming: {str(e)}")
            return False

    async def stop_streaming(self) -> bool:
        """Stop data streaming from LSL."""
        try:
            self.is_streaming = False
            await self.update_status(DeviceStatus.CONNECTED)

            self._emit_event("lsl_streaming_stopped", {"stream_name": self.stream_name})
            logger.info(f"Stopped streaming from LSL: {self.stream_name}")
            return True

        except Exception as e:
            logger.error(f"Error stopping LSL streaming: {str(e)}")
            return False

    async def configure(self, config: Dict[str, Any]) -> bool:
        """Configure LSL adapter parameters.

        Args:
            config: Configuration parameters

        Returns:
            True if configuration successful
        """
        try:
            # Update connection parameters
            if "buffer_size" in config:
                self.buffer_size = config["buffer_size"]
                self.device_info.connection_params["buffer_size"] = self.buffer_size

            if "timeout" in config:
                self.timeout_seconds = config["timeout"]
                self.device_info.connection_params["timeout"] = self.timeout_seconds

            if "stream_name" in config:
                # old_name = self.stream_name  # Not used
                self.stream_name = config["stream_name"]
                self.device_info.connection_params["stream_name"] = self.stream_name

                # If connected, need to reconnect with new stream name
                if self.is_connected:
                    await self.disconnect()
                    await self.connect()

            # Update device configuration
            self.device_info.configuration.update(config)

            self._emit_event("lsl_configured", {"config": config})
            logger.info(f"LSL adapter configured: {config}")
            return True

        except Exception as e:
            logger.error(f"Error configuring LSL adapter: {str(e)}")
            return False

    async def get_impedance(self) -> Dict[str, float]:
        """Get electrode impedance values.

        Note: LSL streams typically don't provide impedance data directly.
        This returns simulated values or empty dict.

        Returns:
            Dictionary of channel impedance values
        """
        if not self.stream_info:
            return {}

        # LSL streams don't typically provide impedance data
        # Return empty dict or simulated values
        impedance_values = {}

        for i, label in enumerate(self.stream_info.channel_labels):
            # Simulate reasonable impedance values (5-20 kOhms)
            impedance_values[label] = 10.0 + (i % 10)

        return impedance_values

    async def perform_self_test(self) -> Dict[str, Any]:
        """Perform LSL adapter self-test.

        Returns:
            Test results and diagnostic information
        """
        test_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "test_passed": True,
            "tests": {},
        }

        try:
            # Test LSL availability
            test_results["tests"]["lsl_available"] = {
                "passed": LSL_AVAILABLE,
                "message": (
                    "pylsl library available"
                    if LSL_AVAILABLE
                    else "pylsl not available"
                ),
            }

            # Test stream discovery
            try:
                streams = await self.lsl_integration.discover_streams(timeout=2.0)
                test_results["tests"]["stream_discovery"] = {
                    "passed": True,
                    "message": f"Discovered {len(streams)} streams",
                    "streams_found": len(streams),
                }
            except Exception as e:
                test_results["tests"]["stream_discovery"] = {
                    "passed": False,
                    "message": f"Stream discovery failed: {str(e)}",
                }
                test_results["test_passed"] = False

            # Test connection if stream available
            if self.stream_info:
                test_results["tests"]["stream_available"] = {
                    "passed": True,
                    "message": f"Target stream available: {self.stream_name}",
                    "stream_info": {
                        "name": self.stream_info.name,
                        "type": self.stream_info.stream_type.value,
                        "channels": self.stream_info.channel_count,
                        "sampling_rate": self.stream_info.sampling_rate,
                    },
                }
            else:
                test_results["tests"]["stream_available"] = {
                    "passed": False,
                    "message": f"Target stream not available: {self.stream_name}",
                }
                test_results["test_passed"] = False

            # Test connection status
            test_results["tests"]["connection_status"] = {
                "passed": self.is_connected,
                "message": f"Connection status: {'connected' if self.is_connected else 'disconnected'}",
            }

            # Test data flow if streaming
            if self.is_streaming:
                time_since_data = (
                    datetime.utcnow() - self.last_data_time
                ).total_seconds()
                data_flow_ok = time_since_data < 5.0  # Data within last 5 seconds

                test_results["tests"]["data_flow"] = {
                    "passed": data_flow_ok,
                    "message": f"Data flow: {'active' if data_flow_ok else 'stale'}",
                    "last_data_seconds_ago": time_since_data,
                    "sample_count": self.sample_count,
                }

                if not data_flow_ok:
                    test_results["test_passed"] = False

        except Exception as e:
            test_results["test_passed"] = False
            test_results["error"] = str(e)
            logger.error(f"LSL self-test error: {str(e)}")

        return test_results

    def _handle_lsl_data(self, stream_id: str, data_sample: DataSample) -> None:
        """Handle data from LSL integration.

        Args:
            stream_id: Stream identifier
            data_sample: Received data sample
        """
        # Only process data from our stream
        if (
            stream_id
            != f"{self.stream_name}_{self.stream_info.source_id if self.stream_info else ''}"
        ):
            return

        if not self.is_streaming:
            return

        try:
            # Update sample tracking
            self.sample_count += 1
            self.last_data_time = datetime.utcnow()

            # Update device info
            data_sample.device_id = self.device_info.device_id
            data_sample.sampling_rate = self.device_info.sampling_rate

            # Calculate signal quality
            # Note: Can't use await in non-async function
            # Signal quality will be calculated elsewhere
            data_sample.signal_quality = {
                "overall": "unknown",
                "snr": getattr(data_sample, "snr", 0.0),
            }

            # Update device metrics
            self.device_info.data_rate_hz = self.device_info.sampling_rate
            self.device_info.last_seen = datetime.utcnow()

            # Emit data to callbacks
            self._emit_data(data_sample)

        except Exception as e:
            logger.error(f"Error handling LSL data: {str(e)}")

    @classmethod
    async def discover_devices(cls, timeout: float = 2.0) -> List[DeviceInfo]:
        """Discover available LSL devices.

        Args:
            timeout: Discovery timeout in seconds

        Returns:
            List of discovered LSL device information
        """
        if not LSL_AVAILABLE:
            logger.warning("pylsl not available for LSL device discovery")
            return []

        discovered_devices = []

        try:
            # Create temporary LSL integration for discovery
            lsl_integration = LSLIntegration()

            # Discover streams
            streams = await lsl_integration.discover_streams(timeout)

            for stream in streams:
                # Create device info for each discovered stream
                device_info = DeviceInfo(
                    device_id=f"lsl_{stream.name}_{stream.source_id}",
                    device_type=DeviceType.LSL_STREAM,
                    model=stream.name,
                    firmware_version="LSL",
                    serial_number=stream.source_id,
                    channel_count=stream.channel_count,
                    sampling_rate=stream.sampling_rate,
                    supported_sampling_rates=[stream.sampling_rate],
                    capabilities=["streaming", "real_time"],
                    connection_type=ConnectionType.LSL,
                    connection_params={
                        "stream_name": stream.name,
                        "stream_type": stream.stream_type.value,
                        "source_id": stream.source_id,
                        "buffer_size": 1000,
                        "timeout": 1.0,
                    },
                    status=DeviceStatus.DISCONNECTED,
                    metadata={
                        "lsl_stream_info": {
                            "name": stream.name,
                            "type": stream.stream_type.value,
                            "manufacturer": stream.manufacturer,
                            "channel_labels": stream.channel_labels,
                            "channel_units": stream.channel_units,
                        }
                    },
                )

                discovered_devices.append(device_info)

            logger.info(f"Discovered {len(discovered_devices)} LSL devices")

        except Exception as e:
            logger.error(f"Error discovering LSL devices: {str(e)}")

        return discovered_devices

    @classmethod
    def create_synthetic_stream(
        cls,
        name: str,
        channels: int = 8,
        sampling_rate: float = 250.0,
        stream_type: str = "EEG",
    ) -> "LSLAdapter":
        """Create a synthetic LSL stream for testing.

        Args:
            name: Stream name
            channels: Number of channels
            sampling_rate: Sampling rate in Hz
            stream_type: Type of stream

        Returns:
            LSL adapter for synthetic stream
        """
        device_info = DeviceInfo(
            device_id=f"lsl_synthetic_{name}",
            device_type=DeviceType.LSL_STREAM,
            model=f"Synthetic {name}",
            firmware_version="LSL_Synthetic",
            serial_number=f"synthetic_{name}",
            channel_count=channels,
            sampling_rate=sampling_rate,
            supported_sampling_rates=[sampling_rate],
            capabilities=["streaming", "synthetic"],
            connection_type=ConnectionType.LSL,
            connection_params={
                "stream_name": name,
                "stream_type": stream_type,
                "source_id": f"synthetic_{name}",
                "buffer_size": 1000,
                "timeout": 1.0,
            },
            status=DeviceStatus.DISCONNECTED,
            metadata={"synthetic": True, "stream_type": stream_type},
        )

        return cls(device_info)

    async def cleanup(self) -> None:
        """Clean up LSL adapter resources."""
        try:
            if self.is_streaming:
                await self.stop_streaming()

            if self.is_connected:
                await self.disconnect()

            # Clean up LSL integration if we created it
            if hasattr(self, "lsl_integration") and self.lsl_integration.is_running:
                # Only stop if we're the only user
                active_streams = await self.lsl_integration.get_active_streams()
                if len(active_streams) <= 1:  # Only our stream
                    await self.lsl_integration.stop()

            await super().cleanup()

        except Exception as e:
            logger.error(f"Error cleaning up LSL adapter: {str(e)}")

    def __str__(self) -> str:
        """String representation."""
        return f"LSLAdapter(stream={self.stream_name}, type={self.stream_type})"

    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"LSLAdapter(device_id={self.device_info.device_id}, "
            f"stream={self.stream_name}, type={self.stream_type}, "
            f"connected={self.is_connected}, streaming={self.is_streaming})"
        )
