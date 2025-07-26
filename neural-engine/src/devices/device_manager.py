"""Device manager for handling multiple neural data acquisition devices."""

import asyncio
import logging
from typing import Dict, List, Optional, Callable, Any, Type, Tuple
from datetime import datetime, timezone
import uuid
from pathlib import Path

from .interfaces.base_device import BaseDevice, DeviceState
from .implementations.lsl_device import LSLDevice
from .implementations.openbci_device import OpenBCIDevice
from .implementations.brainflow_device import BrainFlowDevice
from .implementations.synthetic_device import SyntheticDevice
from .device_discovery import DeviceDiscoveryService, DiscoveredDevice, DeviceProtocol
from .signal_quality import SignalQualityMonitor  # noqa: F401
from .device_health import DeviceHealthMonitor
from .device_telemetry import (  # noqa: F401
    DeviceTelemetryCollector,
    FileTelemetryExporter,
)
from .device_notifications import DeviceNotificationService
from ..ingestion.data_types import NeuralDataPacket

logger = logging.getLogger(__name__)


class DeviceManager:
    """Manages multiple neural data acquisition devices."""

    # Device type registry
    DEVICE_TYPES: Dict[str, Type[BaseDevice]] = {
        "lsl": LSLDevice,
        "openbci": OpenBCIDevice,
        "brainflow": BrainFlowDevice,
        "synthetic": SyntheticDevice,
    }

    def __init__(self) -> None:
        """Initialize device manager."""
        self.devices: Dict[str, BaseDevice] = {}
        self.active_session_id: Optional[str] = None
        self._data_callback: Optional[Callable[[str, NeuralDataPacket], None]] = None
        self._state_callback: Optional[Callable[[str, DeviceState], None]] = None
        self._error_callback: Optional[Callable[[str, Exception], None]] = None
        self._aggregation_task: Optional[asyncio.Task] = None
        self._aggregation_queue: asyncio.Queue[Tuple[str, NeuralDataPacket]] = (
            asyncio.Queue()
        )

        # Discovery service
        self.discovery_service = DeviceDiscoveryService()
        self._discovered_devices: Dict[str, DiscoveredDevice] = {}

        # Health monitoring
        self.health_monitor = DeviceHealthMonitor(check_interval=5.0)

        # Telemetry collection
        self.telemetry_collector = DeviceTelemetryCollector(
            buffer_size=1000,
            flush_interval=60.0,
        )

        # Notification service
        self.notification_service = DeviceNotificationService()

    def register_device_type(
        self, device_type: str, device_class: Type[BaseDevice]
    ) -> None:
        """Register a custom device type."""
        self.DEVICE_TYPES[device_type] = device_class
        logger.info(f"Registered device type: {device_type}")

    async def add_device(
        self, device_id: str, device_type: str, **device_kwargs: Any
    ) -> BaseDevice:
        """
        Add a new device to the manager.

        Args:
            device_id: Unique identifier for the device
            device_type: Type of device from DEVICE_TYPES
            **device_kwargs: Device - specific initialization parameters

        Returns:
            The created device instance
        """
        if device_id in self.devices:
            raise ValueError(f"Device {device_id} already exists")

        if device_type not in self.DEVICE_TYPES:
            raise ValueError(
                f"Unknown device type: {device_type}. "
                f"Available types: {list(self.DEVICE_TYPES.keys())}"
            )

        # Create device instance
        device_class = self.DEVICE_TYPES[device_type]
        device = device_class(**device_kwargs)

        # Set up callbacks
        device.set_data_callback(
            lambda packet: self._handle_device_data(device_id, packet)
        )
        device.set_state_callback(
            lambda state: self._handle_device_state(device_id, state)
        )
        device.set_error_callback(
            lambda error: self._handle_device_error(device_id, error)
        )

        # Set session ID if active
        if self.active_session_id:
            device.set_session_id(self.active_session_id)

        self.devices[device_id] = device

        # Add to health monitoring
        self.health_monitor.add_device(device_id, device)

        # Collect device info telemetry
        asyncio.create_task(
            self.telemetry_collector.collect_device_info(
                device_id,
                {
                    "device_type": device_type,
                    "device_name": device.device_name,
                    "added_at": datetime.now(timezone.utc).isoformat(),
                },
            )
        )

        logger.info(f"Added device: {device_id} (type: {device_type})")

        return device

    async def remove_device(self, device_id: str) -> None:
        """Remove a device from the manager."""
        if device_id not in self.devices:
            return

        device = self.devices[device_id]

        # Stop and disconnect if necessary
        if device.is_streaming():
            await device.stop_streaming()
        if device.is_connected():
            await device.disconnect()

        # Remove from health monitoring
        self.health_monitor.remove_device(device_id)

        # Collect removal telemetry
        await self.telemetry_collector.collect_device_info(
            device_id,
            {
                "event": "device_removed",
                "removed_at": datetime.now(timezone.utc).isoformat(),
            },
        )

        del self.devices[device_id]
        logger.info(f"Removed device: {device_id}")

    def get_device(self, device_id: str) -> Optional[BaseDevice]:
        """Get a device by ID."""
        return self.devices.get(device_id)

    def list_devices(self) -> List[Dict[str, Any]]:
        """List all devices with their status."""
        device_list = []
        for device_id, device in self.devices.items():
            device_list.append(
                {
                    "device_id": device_id,
                    "device_name": device.device_name,
                    "state": device.state.value,
                    "connected": device.is_connected(),
                    "streaming": device.is_streaming(),
                    "capabilities": (
                        device.get_capabilities() if device.is_connected() else None
                    ),
                }
            )
        return device_list

    async def connect_device(self, device_id: str, **connect_kwargs: Any) -> bool:
        """Connect to a specific device."""
        device = self.devices.get(device_id)
        if not device:
            raise ValueError(f"Device {device_id} not found")

        return await device.connect(**connect_kwargs)

    async def disconnect_device(self, device_id: str) -> None:
        """Disconnect a specific device."""
        device = self.devices.get(device_id)
        if device:
            await device.disconnect()

    async def start_streaming(self, device_ids: Optional[List[str]] = None) -> None:
        """
        Start streaming from specified devices.

        Args:
            device_ids: List of device IDs to start streaming, or None for all
                connected devices
        """
        if device_ids is None:
            device_ids = [
                dev_id for dev_id, dev in self.devices.items() if dev.is_connected()
            ]

        # Start session if not active
        if not self.active_session_id:
            self.start_session()

        # Start streaming for each device
        tasks = []
        for device_id in device_ids:
            device = self.devices.get(device_id)
            if device and device.is_connected() and not device.is_streaming():
                tasks.append(device.start_streaming())

        if tasks:
            await asyncio.gather(*tasks)
            logger.info(f"Started streaming from {len(tasks)} devices")

    async def stop_streaming(self, device_ids: Optional[List[str]] = None) -> None:
        """
        Stop streaming from specified devices.

        Args:
            device_ids: List of device IDs to stop streaming, or None for all
                streaming devices
        """
        if device_ids is None:
            device_ids = [
                dev_id for dev_id, dev in self.devices.items() if dev.is_streaming()
            ]

        # Stop streaming for each device
        tasks = []
        for device_id in device_ids:
            device = self.devices.get(device_id)
            if device and device.is_streaming():
                tasks.append(device.stop_streaming())

        if tasks:
            await asyncio.gather(*tasks)
            logger.info(f"Stopped streaming from {len(tasks)} devices")

    def start_session(self, session_id: Optional[str] = None) -> str:
        """
        Start a new recording session.

        Args:
            session_id: Optional session ID, will be generated if not provided

        Returns:
            The session ID
        """
        self.active_session_id = session_id or (
            f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_"
            f"{uuid.uuid4().hex[:8]}"
        )

        # Update all devices with new session ID
        for device in self.devices.values():
            device.set_session_id(self.active_session_id)

        logger.info(f"Started session: {self.active_session_id}")
        return self.active_session_id

    def end_session(self) -> None:
        """End the current recording session."""
        if self.active_session_id:
            logger.info(f"Ended session: {self.active_session_id}")
            self.active_session_id = None

    def set_data_callback(
        self, callback: Callable[[str, NeuralDataPacket], None]
    ) -> None:
        """Set callback for data packets from any device."""
        self._data_callback = callback

    def set_state_callback(self, callback: Callable[[str, DeviceState], None]) -> None:
        """Set callback for device state changes."""
        self._state_callback = callback

    def set_error_callback(self, callback: Callable[[str, Exception], None]) -> None:
        """Set callback for device errors."""
        self._error_callback = callback

    def _handle_device_data(self, device_id: str, packet: NeuralDataPacket) -> None:
        """Handle data packet from a device."""
        # Add device ID to packet metadata
        if packet.metadata is None:
            packet.metadata = {}
        packet.metadata["device_id"] = device_id

        # Record packet for health monitoring
        self.health_monitor.record_packet(device_id, packet.timestamp)

        # Add to aggregation queue if aggregation is active
        if self._aggregation_task and not self._aggregation_task.done():
            try:
                self._aggregation_queue.put_nowait((device_id, packet))
            except asyncio.QueueFull:
                logger.warning(
                    f"Aggregation queue full, dropping packet from {device_id}"
                )

        # Call user callback
        if self._data_callback:
            try:
                self._data_callback(device_id, packet)
            except Exception as e:
                logger.error(f"Error in data callback: {e}")

    def _handle_device_state(self, device_id: str, state: DeviceState) -> None:
        """Handle device state change."""
        # Get previous state if available
        device = self.devices.get(device_id)
        previous_state = device.state if device else DeviceState.DISCONNECTED

        # Send WebSocket notification
        asyncio.create_task(
            self.notification_service.notify_device_state_change(
                device_id, previous_state, state
            )
        )

        # Collect telemetry for state changes
        asyncio.create_task(
            self.telemetry_collector.collect_connection_event(
                device_id,
                f"state_changed_to_{state.value}",
                {"previous_state": previous_state.value, "new_state": state.value},
            )
        )

        if self._state_callback:
            try:
                self._state_callback(device_id, state)
            except Exception as e:
                logger.error(f"Error in state callback: {e}")

    def _handle_device_error(self, device_id: str, error: Exception) -> None:
        """Handle device error."""
        logger.error(f"Device {device_id} error: {error}")

        # Send WebSocket notification for error
        asyncio.create_task(
            self.notification_service.notify_device_error(device_id, error)
        )

        # Record error for health monitoring
        self.health_monitor.record_error(device_id, error)

        # Collect error telemetry
        asyncio.create_task(
            self.telemetry_collector.collect_error(
                device_id,
                type(error).__name__,
                str(error),
            )
        )

        if self._error_callback:
            try:
                self._error_callback(device_id, error)
            except Exception as e:
                logger.error(f"Error in error callback: {e}")

    async def start_aggregation(
        self,
        window_size_ms: int = 50,
        callback: Optional[Callable[[Dict[str, NeuralDataPacket]], None]] = None,
    ) -> None:
        """
        Start aggregating data from multiple devices into synchronized windows.

        Args:
            window_size_ms: Window size in milliseconds
            callback: Callback for aggregated data windows
        """
        if self._aggregation_task and not self._aggregation_task.done():
            logger.warning("Aggregation already running")
            return

        self._aggregation_task = asyncio.create_task(
            self._aggregation_loop(window_size_ms, callback)
        )
        logger.info(f"Started data aggregation with {window_size_ms}ms windows")

    async def stop_aggregation(self) -> None:
        """Stop data aggregation."""
        if self._aggregation_task:
            self._aggregation_task.cancel()
            try:
                await self._aggregation_task
            except asyncio.CancelledError:
                pass
            self._aggregation_task = None
            logger.info("Stopped data aggregation")

    async def _aggregation_loop(
        self,
        window_size_ms: int,
        callback: Optional[Callable[[Dict[str, NeuralDataPacket]], None]],
    ) -> None:
        """Main aggregation loop."""
        window_duration = window_size_ms / 1000.0
        window_data: Dict[str, List[NeuralDataPacket]] = {}
        window_start = asyncio.get_event_loop().time()

        try:
            while True:
                try:
                    # Get packet with timeout
                    remaining_time = window_duration - (
                        asyncio.get_event_loop().time() - window_start
                    )
                    if remaining_time <= 0:
                        # Window complete, process data
                        if window_data and callback:
                            # Get latest packet from each device
                            aggregated = {
                                device_id: packets[-1]
                                for device_id, packets in window_data.items()
                            }
                            callback(aggregated)

                        # Reset window
                        window_data.clear()
                        window_start = asyncio.get_event_loop().time()
                        continue

                    # Get next packet
                    device_id, packet = await asyncio.wait_for(
                        self._aggregation_queue.get(), timeout=remaining_time
                    )

                    # Add to window
                    if device_id not in window_data:
                        window_data[device_id] = []
                    window_data[device_id].append(packet)

                except asyncio.TimeoutError:
                    # Window timeout, process what we have
                    if window_data and callback:
                        aggregated = {
                            device_id: packets[-1]
                            for device_id, packets in window_data.items()
                        }
                        callback(aggregated)

                    # Reset window
                    window_data.clear()
                    window_start = asyncio.get_event_loop().time()

        except asyncio.CancelledError:
            logger.info("Aggregation loop cancelled")
            raise

    async def auto_discover_devices(self, timeout: float = 5.0) -> List[Dict[str, Any]]:
        """
        Auto-discover available devices using the discovery service.

        Args:
            timeout: Discovery timeout in seconds

        Returns:
            List of discovered devices
        """
        # Clear previous discoveries
        self._discovered_devices.clear()

        # Set up callback to track discoveries
        def on_device_discovered(device: DiscoveredDevice):
            self._discovered_devices[device.unique_id] = device
            logger.info(f"Discovered: {device.device_name} ({device.device_type})")

            # Send WebSocket notification for device discovery
            device_info = {
                "device_id": device.unique_id,
                "device_type": device.device_type,
                "device_name": device.device_name,
                "protocol": device.protocol.value,
                "connection_info": device.connection_info,
                "metadata": device.metadata,
            }
            asyncio.create_task(
                self.notification_service.notify_device_discovered(device_info)
            )

        self.discovery_service.add_discovery_callback(on_device_discovered)

        try:
            # Perform discovery scan
            discovered_devices = await self.discovery_service.quick_scan(timeout)

            # Convert to expected format
            discovered = []
            for device in discovered_devices:
                # Map discovery device types to our device types
                device_type = self._map_device_type(device)

                if device_type:
                    discovered.append(
                        {
                            "device_type": device_type,
                            "device_id": device.unique_id,
                            "name": device.device_name,
                            "protocol": device.protocol.value,
                            "connection_info": device.connection_info,
                            "metadata": device.metadata,
                        }
                    )

            logger.info(f"Discovered {len(discovered)} devices")
            return discovered

        finally:
            # Remove callback
            self.discovery_service.remove_discovery_callback(on_device_discovered)

    def _map_device_type(self, discovered_device: DiscoveredDevice) -> Optional[str]:
        """Map discovered device to internal device type."""
        if discovered_device.device_type == "LSL":
            return "lsl"
        elif discovered_device.device_type == "OpenBCI":
            return "openbci"
        elif discovered_device.device_type in [
            "BrainFlow",
            "Muse",
            "BrainBit",
            "Neurosity",
        ]:
            return "brainflow"
        elif discovered_device.device_type == "Synthetic":
            return "synthetic"
        else:
            # Unknown device type
            return None

    async def create_device_from_discovery(
        self, discovery_id: str, device_id: Optional[str] = None
    ) -> BaseDevice:
        """
        Create a device instance from a discovered device.

        Args:
            discovery_id: The unique ID from device discovery
            device_id: Optional custom device ID (uses discovery_id if not provided)

        Returns:
            The created device instance
        """
        if discovery_id not in self._discovered_devices:
            raise ValueError(f"No discovered device with ID: {discovery_id}")

        discovered = self._discovered_devices[discovery_id]
        device_type = self._map_device_type(discovered)

        if not device_type:
            raise ValueError(f"Cannot map device type: {discovered.device_type}")

        # Use discovery ID as device ID if not provided
        if device_id is None:
            device_id = discovery_id

        # Prepare device kwargs based on type
        device_kwargs = {}

        if device_type == "lsl":
            device_kwargs = {
                "stream_name": discovered.connection_info.get("name"),
                "stream_type": discovered.connection_info.get("type"),
            }
        elif device_type == "openbci":
            device_kwargs = {
                "port": discovered.connection_info.get("port"),
            }
        elif device_type == "brainflow":
            # Map discovered device to BrainFlow board name
            board_name = self._get_brainflow_board_name(discovered)
            device_kwargs = {"board_name": board_name}

            # Add connection parameters
            if discovered.protocol == DeviceProtocol.SERIAL:
                device_kwargs["serial_port"] = discovered.connection_info.get("port")
            elif discovered.protocol == DeviceProtocol.BLUETOOTH:
                device_kwargs["mac_address"] = discovered.connection_info.get("address")
            elif discovered.protocol == DeviceProtocol.WIFI:
                device_kwargs["ip_address"] = discovered.connection_info.get("ip")
                device_kwargs["ip_port"] = discovered.connection_info.get("port")

        # Create device
        return await self.add_device(device_id, device_type, **device_kwargs)

    def _get_brainflow_board_name(self, discovered_device: DiscoveredDevice) -> str:
        """Get BrainFlow board name from discovered device."""
        device_name = discovered_device.device_name.lower()

        if "cyton" in device_name:
            return "cyton"
        elif "ganglion" in device_name:
            return "ganglion"
        elif "muse s" in device_name:
            return "muse_s"
        elif "muse 2" in device_name:
            return "muse_2"
        elif "crown" in device_name:
            return "neurosity_crown"
        elif "brainbit" in device_name:
            return "brainbit"
        elif "unicorn" in device_name:
            return "unicorn"
        elif "synthetic" in device_name:
            return "synthetic"
        else:
            # Default to synthetic if unknown
            return "synthetic"

    async def start_health_monitoring(self) -> None:
        """Start device health monitoring."""
        await self.health_monitor.start_monitoring()

    async def stop_health_monitoring(self) -> None:
        """Stop device health monitoring."""
        await self.health_monitor.stop_monitoring()

    async def start_telemetry_collection(
        self,
        output_dir: Optional[Path] = None,
        enable_cloud: bool = False,
    ):
        """
        Start telemetry collection.

        Args:
            output_dir: Directory for file telemetry export
            enable_cloud: Enable cloud telemetry export (requires GCP setup)
        """
        # Add file exporter if output directory provided
        if output_dir:
            file_exporter = FileTelemetryExporter(
                output_dir=Path(output_dir),
                compress=True,
            )
            self.telemetry_collector.add_exporter(file_exporter)

        # Add cloud exporter if enabled (placeholder for now)
        if enable_cloud:
            logger.info("Cloud telemetry export not yet implemented")

        await self.telemetry_collector.start()

    async def stop_telemetry_collection(self) -> None:
        """Stop telemetry collection."""
        await self.telemetry_collector.stop()

    def get_device_health(self, device_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get device health information.

        Args:
            device_id: Specific device ID, or None for all devices

        Returns:
            Health information dictionary
        """
        if device_id:
            return {
                "status": self.health_monitor.get_device_health(device_id).value,
                "metrics": (
                    self.health_monitor.get_device_metrics(device_id).to_dict()
                    if self.health_monitor.get_device_metrics(device_id)
                    else None
                ),
            }
        else:
            return {
                device_id: {
                    "status": status.value,
                    "metrics": (
                        self.health_monitor.get_device_metrics(device_id).to_dict()
                        if self.health_monitor.get_device_metrics(device_id)
                        else None
                    ),
                }
                for device_id, status in self.health_monitor.get_all_health_status().items()
            }

    def get_health_alerts(
        self, device_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get active health alerts."""
        alerts = self.health_monitor.get_active_alerts(device_id)
        return [
            {
                "device_id": alert.device_id,
                "severity": alert.severity.value,
                "category": alert.category,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "metadata": alert.metadata,
            }
            for alert in alerts
        ]

    def get_telemetry_statistics(self) -> Dict[str, int]:
        """Get telemetry collection statistics."""
        return self.telemetry_collector.get_statistics()

    async def start_notification_service(self) -> None:
        """Start the WebSocket notification service."""
        await self.notification_service.start()

    async def stop_notification_service(self) -> None:
        """Stop the WebSocket notification service."""
        await self.notification_service.stop()

    async def check_device_impedance(
        self, device_id: str, channel_ids: Optional[List[int]] = None
    ) -> Dict[int, float]:
        """
        Check impedance for a device and send notifications.

        Args:
            device_id: Device to check impedance for
            channel_ids: Specific channels to check, or None for all

        Returns:
            Dictionary of channel ID to impedance values
        """
        device = self.devices.get(device_id)
        if not device:
            raise ValueError(f"Device {device_id} not found")

        # Perform impedance check
        impedance_results = await device.check_impedance(channel_ids)

        # Calculate quality summary
        quality_summary = {
            "total_channels": len(impedance_results),
            "good_channels": sum(1 for v in impedance_results.values() if v < 10000),
            "fair_channels": sum(
                1 for v in impedance_results.values() if 10000 <= v < 20000
            ),
            "poor_channels": sum(1 for v in impedance_results.values() if v >= 20000),
            "average_impedance": (
                sum(impedance_results.values()) / len(impedance_results)
                if impedance_results
                else 0
            ),
        }

        # Send notification
        await self.notification_service.notify_impedance_check_complete(
            device_id, impedance_results, quality_summary
        )

        return impedance_results

    async def __aenter__(self) -> "DeviceManager":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit - cleanup all devices."""
        # Stop notification service
        await self.stop_notification_service()

        # Stop health monitoring
        await self.stop_health_monitoring()

        # Stop telemetry collection
        await self.stop_telemetry_collection()

        # Stop aggregation if running
        await self.stop_aggregation()

        # Stop all streaming
        await self.stop_streaming()

        # Disconnect all devices
        disconnect_tasks = []
        for device in self.devices.values():
            if device.is_connected():
                disconnect_tasks.append(device.disconnect())

        if disconnect_tasks:
            await asyncio.gather(*disconnect_tasks)

        # Clear devices
        self.devices.clear()
