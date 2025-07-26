"""Device Manager for orchestrating BCI device operations.

This module provides the central coordinator for all device lifecycle management,
connection pooling, event dispatching, and error handling.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

from .base import (
    BaseDevice,
    DeviceInfo,
    DeviceType,
    DeviceStatus,
    DeviceEvent,
    DataSample,
)
from .device_registry import DeviceRegistry
from .health_monitor import HealthMonitor

logger = logging.getLogger(__name__)


class DiscoveryMethod(Enum):
    """Device discovery methods."""

    SERIAL_SCAN = "serial_scan"
    USB_SCAN = "usb_scan"
    BLUETOOTH_SCAN = "bluetooth_scan"
    LSL_DISCOVERY = "lsl_discovery"
    BRAINFLOW_SCAN = "brainflow_scan"
    MANUAL_REGISTRATION = "manual_registration"


@dataclass
class DeviceManagerConfig:
    """Configuration for DeviceManager."""

    # Discovery settings
    auto_discovery_enabled: bool = True
    discovery_interval_seconds: int = 30
    discovery_methods: List[DiscoveryMethod] = field(
        default_factory=lambda: [
            DiscoveryMethod.LSL_DISCOVERY,
            DiscoveryMethod.SERIAL_SCAN,
            DiscoveryMethod.BRAINFLOW_SCAN,
        ]
    )

    # Connection management
    max_concurrent_connections: int = 10
    connection_timeout_seconds: int = 30
    reconnection_attempts: int = 3
    reconnection_delay_seconds: int = 5

    # Health monitoring
    health_check_interval_seconds: int = 60
    device_timeout_seconds: int = 300  # 5 minutes

    # Event handling
    event_queue_max_size: int = 1000
    enable_event_logging: bool = True


@dataclass
class DeviceManagerStats:
    """Device manager operational statistics."""

    # Device counts
    total_devices: int = 0
    connected_devices: int = 0
    streaming_devices: int = 0
    error_devices: int = 0

    # Operations
    discovery_runs: int = 0
    connection_attempts: int = 0
    successful_connections: int = 0
    failed_connections: int = 0

    # Events
    events_processed: int = 0
    data_samples_processed: int = 0

    # Performance
    uptime_seconds: float = 0.0
    last_discovery: Optional[datetime] = None
    last_health_check: Optional[datetime] = None


class DeviceManager:
    """Central orchestrator for all BCI device operations."""

    def __init__(
        self,
        config: DeviceManagerConfig = None,
        registry: DeviceRegistry = None,
        health_monitor: HealthMonitor = None,
    ):
        """Initialize DeviceManager.

        Args:
            config: Manager configuration
            registry: Device registry instance
            health_monitor: Health monitoring instance
        """
        self.config = config or DeviceManagerConfig()
        self.registry = registry or DeviceRegistry()
        self.health_monitor = health_monitor or HealthMonitor()

        # Device management
        self.devices: Dict[str, BaseDevice] = {}
        self.device_adapters: Dict[DeviceType, type] = {}

        # Async task management
        self.background_tasks: List[asyncio.Task] = []
        self.is_running = False
        self._shutdown_event = asyncio.Event()

        # Event handling
        self.event_callbacks: List[Callable[[DeviceEvent], None]] = []
        self.data_callbacks: List[Callable[[DataSample], None]] = []
        self.event_queue: asyncio.Queue = asyncio.Queue(
            maxsize=self.config.event_queue_max_size
        )

        # Statistics
        self.stats = DeviceManagerStats()
        self.start_time = datetime.utcnow()

        logger.info("DeviceManager initialized")

    async def start(self) -> None:
        """Start the device manager and background tasks."""
        if self.is_running:
            logger.warning("DeviceManager already running")
            return

        logger.info("Starting DeviceManager...")
        self.is_running = True
        self._shutdown_event.clear()

        # Start background tasks
        if self.config.auto_discovery_enabled:
            task = asyncio.create_task(self._discovery_loop())
            self.background_tasks.append(task)

        task = asyncio.create_task(self._health_monitoring_loop())
        self.background_tasks.append(task)

        task = asyncio.create_task(self._event_processing_loop())
        self.background_tasks.append(task)

        # Start health monitor
        await self.health_monitor.start()

        logger.info("DeviceManager started successfully")

    async def stop(self) -> None:
        """Stop the device manager and cleanup resources."""
        if not self.is_running:
            return

        logger.info("Stopping DeviceManager...")
        self.is_running = False
        self._shutdown_event.set()

        # Disconnect all devices
        await self.disconnect_all_devices()

        # Cancel background tasks
        for task in self.background_tasks:
            if not task.done():
                task.cancel()

        # Wait for tasks to complete
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)

        self.background_tasks.clear()

        # Stop health monitor
        await self.health_monitor.stop()

        logger.info("DeviceManager stopped")

    def register_device_adapter(
        self, device_type: DeviceType, adapter_class: type
    ) -> None:
        """Register a device adapter for a specific device type.

        Args:
            device_type: Type of device
            adapter_class: Adapter class for the device type
        """
        self.device_adapters[device_type] = adapter_class
        logger.info(
            f"Registered adapter for {device_type.value}: {adapter_class.__name__}"
        )

    async def discover_devices(
        self, methods: List[DiscoveryMethod] = None
    ) -> List[DeviceInfo]:
        """Discover available BCI devices.

        Args:
            methods: Discovery methods to use (defaults to config methods)

        Returns:
            List of discovered device information
        """
        methods = methods or self.config.discovery_methods
        discovered_devices: List[DeviceInfo] = []

        logger.info(
            f"Starting device discovery with methods: {[m.value for m in methods]}"
        )

        for method in methods:
            try:
                devices = await self._discover_by_method(method)
                discovered_devices.extend(devices)
                logger.info(f"Discovered {len(devices)} devices using {method.value}")

            except Exception as e:
                logger.error(f"Error in discovery method {method.value}: {str(e)}")

        # Remove duplicates based on device_id
        unique_devices = {}
        for device in discovered_devices:
            unique_devices[device.device_id] = device

        discovered_devices = list(unique_devices.values())

        # Register discovered devices
        for device_info in discovered_devices:
            await self.registry.register_device(device_info)

        self.stats.discovery_runs += 1
        self.stats.last_discovery = datetime.utcnow()

        logger.info(
            f"Discovery completed: {len(discovered_devices)} unique devices found"
        )
        return discovered_devices

    async def register_device(self, device_info: DeviceInfo) -> str:
        """Register a device manually.

        Args:
            device_info: Device information

        Returns:
            Device ID
        """
        device_id = await self.registry.register_device(device_info)
        self.stats.total_devices += 1

        self._emit_event(
            "device_registered",
            {"device_id": device_id, "device_type": device_info.device_type.value},
        )

        logger.info(f"Manually registered device: {device_id}")
        return device_id

    async def connect_device(self, device_id: str) -> bool:
        """Connect to a specific device.

        Args:
            device_id: Device identifier

        Returns:
            True if connection successful
        """
        if device_id in self.devices:
            device = self.devices[device_id]
            if device.is_connected:
                logger.warning(f"Device {device_id} already connected")
                return True

        # Get device info from registry
        device_info = await self.registry.get_device(device_id)
        if not device_info:
            logger.error(f"Device {device_id} not found in registry")
            return False

        # Check connection limits
        connected_count = len([d for d in self.devices.values() if d.is_connected])
        if connected_count >= self.config.max_concurrent_connections:
            logger.error(
                f"Maximum concurrent connections ({self.config.max_concurrent_connections}) reached"
            )
            return False

        try:
            self.stats.connection_attempts += 1

            # Create device instance
            device = await self._create_device_instance(device_info)
            if not device:
                return False

            # Setup event handling
            device.add_event_callback(self._handle_device_event)
            device.add_data_callback(self._handle_device_data)

            # Attempt connection
            success = await asyncio.wait_for(
                device.connect(), timeout=self.config.connection_timeout_seconds
            )

            if success:
                self.devices[device_id] = device
                await self.registry.update_device_status(
                    device_id, DeviceStatus.CONNECTED
                )

                # Start health monitoring for this device
                await self.health_monitor.start_monitoring_device(device_id)

                self.stats.successful_connections += 1
                self.stats.connected_devices += 1

                self._emit_event("device_connected", {"device_id": device_id})
                logger.info(f"Successfully connected to device: {device_id}")
                return True
            else:
                self.stats.failed_connections += 1
                logger.error(f"Failed to connect to device: {device_id}")
                return False

        except asyncio.TimeoutError:
            self.stats.failed_connections += 1
            logger.error(f"Connection timeout for device: {device_id}")
            return False
        except Exception as e:
            self.stats.failed_connections += 1
            logger.error(f"Error connecting to device {device_id}: {str(e)}")
            return False

    async def disconnect_device(self, device_id: str) -> bool:
        """Disconnect from a specific device.

        Args:
            device_id: Device identifier

        Returns:
            True if disconnection successful
        """
        if device_id not in self.devices:
            logger.warning(f"Device {device_id} not connected")
            return True

        try:
            device = self.devices[device_id]

            # Stop health monitoring
            await self.health_monitor.stop_monitoring_device(device_id)

            # Disconnect device
            success = await device.disconnect()

            # Cleanup
            await device.cleanup()
            del self.devices[device_id]

            # Update registry
            await self.registry.update_device_status(
                device_id, DeviceStatus.DISCONNECTED
            )

            self.stats.connected_devices = max(0, self.stats.connected_devices - 1)

            self._emit_event("device_disconnected", {"device_id": device_id})
            logger.info(f"Disconnected device: {device_id}")

            return success

        except Exception as e:
            logger.error(f"Error disconnecting device {device_id}: {str(e)}")
            return False

    async def disconnect_all_devices(self) -> None:
        """Disconnect all connected devices."""
        device_ids = list(self.devices.keys())

        for device_id in device_ids:
            await self.disconnect_device(device_id)

        logger.info("Disconnected all devices")

    async def start_streaming(self, device_id: str) -> bool:
        """Start data streaming from a device.

        Args:
            device_id: Device identifier

        Returns:
            True if streaming started successfully
        """
        if device_id not in self.devices:
            logger.error(f"Device {device_id} not connected")
            return False

        try:
            device = self.devices[device_id]
            success = await device.start_streaming()

            if success:
                await self.registry.update_device_status(
                    device_id, DeviceStatus.STREAMING
                )
                self.stats.streaming_devices += 1

                self._emit_event("streaming_started", {"device_id": device_id})
                logger.info(f"Started streaming from device: {device_id}")

            return success

        except Exception as e:
            logger.error(f"Error starting streaming for device {device_id}: {str(e)}")
            return False

    async def stop_streaming(self, device_id: str) -> bool:
        """Stop data streaming from a device.

        Args:
            device_id: Device identifier

        Returns:
            True if streaming stopped successfully
        """
        if device_id not in self.devices:
            logger.error(f"Device {device_id} not connected")
            return False

        try:
            device = self.devices[device_id]
            success = await device.stop_streaming()

            if success:
                await self.registry.update_device_status(
                    device_id, DeviceStatus.CONNECTED
                )
                self.stats.streaming_devices = max(0, self.stats.streaming_devices - 1)

                self._emit_event("streaming_stopped", {"device_id": device_id})
                logger.info(f"Stopped streaming from device: {device_id}")

            return success

        except Exception as e:
            logger.error(f"Error stopping streaming for device {device_id}: {str(e)}")
            return False

    async def configure_device(self, device_id: str, config: Dict[str, Any]) -> bool:
        """Configure a device.

        Args:
            device_id: Device identifier
            config: Configuration parameters

        Returns:
            True if configuration successful
        """
        if device_id not in self.devices:
            logger.error(f"Device {device_id} not connected")
            return False

        try:
            device = self.devices[device_id]
            success = await device.configure(config)

            if success:
                # Update registry with new configuration
                device_info = await self.registry.get_device(device_id)
                if device_info:
                    device_info.configuration.update(config)
                    await self.registry.update_device(device_info)

                self._emit_event(
                    "device_configured", {"device_id": device_id, "config": config}
                )
                logger.info(f"Configured device: {device_id}")

            return success

        except Exception as e:
            logger.error(f"Error configuring device {device_id}: {str(e)}")
            return False

    async def get_device_status(self, device_id: str) -> Optional[DeviceStatus]:
        """Get device status.

        Args:
            device_id: Device identifier

        Returns:
            Device status or None if not found
        """
        if device_id in self.devices:
            return await self.devices[device_id].get_status()

        # Check registry
        device_info = await self.registry.get_device(device_id)
        return device_info.status if device_info else None

    async def get_connected_devices(self) -> List[str]:
        """Get list of connected device IDs.

        Returns:
            List of connected device IDs
        """
        return list(self.devices.keys())

    async def get_all_devices(self) -> List[DeviceInfo]:
        """Get all registered devices.

        Returns:
            List of all device information
        """
        return await self.registry.get_all_devices()

    def add_event_callback(self, callback: Callable[[DeviceEvent], None]) -> None:
        """Add callback for device manager events.

        Args:
            callback: Function to call when events occur
        """
        self.event_callbacks.append(callback)

    def add_data_callback(self, callback: Callable[[DataSample], None]) -> None:
        """Add callback for device data.

        Args:
            callback: Function to call when data is received
        """
        self.data_callbacks.append(callback)

    async def get_stats(self) -> DeviceManagerStats:
        """Get device manager statistics.

        Returns:
            Current statistics
        """
        self.stats.uptime_seconds = (
            datetime.utcnow() - self.start_time
        ).total_seconds()
        self.stats.total_devices = len(await self.registry.get_all_devices())
        self.stats.connected_devices = len(self.devices)
        self.stats.streaming_devices = len(
            [
                d
                for d in self.devices.values()
                if d.device_info.status == DeviceStatus.STREAMING
            ]
        )

        return self.stats

    # Private methods

    async def _create_device_instance(
        self, device_info: DeviceInfo
    ) -> Optional[BaseDevice]:
        """Create device instance from device info.

        Args:
            device_info: Device information

        Returns:
            Device instance or None if adapter not found
        """
        adapter_class = self.device_adapters.get(device_info.device_type)
        if not adapter_class:
            logger.error(
                f"No adapter registered for device type: {device_info.device_type.value}"
            )
            return None

        try:
            return adapter_class(device_info)
        except Exception as e:
            logger.error(f"Error creating device instance: {str(e)}")
            return None

    async def _discover_by_method(
        self, method: DiscoveryMethod
    ) -> List[DeviceInfo]:  # noqa: C901
        """Discover devices using a specific method.

        Args:
            method: Discovery method

        Returns:
            List of discovered devices
        """
        discovered = []

        # Import adapters dynamically to avoid circular imports
        if method == DiscoveryMethod.LSL_DISCOVERY:
            try:
                from .adapters.lsl_adapter import LSLAdapter

                discovered = await LSLAdapter.discover_devices()
            except ImportError as e:
                logger.warning(f"LSL adapter not available: {str(e)}")

        elif method == DiscoveryMethod.BRAINFLOW_SCAN:
            try:
                from .adapters.brainflow_adapter import BrainFlowAdapter

                discovered = await BrainFlowAdapter.discover_devices()
            except ImportError as e:
                logger.warning(f"BrainFlow adapter not available: {str(e)}")

        elif method == DiscoveryMethod.SERIAL_SCAN:
            try:
                from .adapters.openbci_adapter import OpenBCIAdapter

                discovered = await OpenBCIAdapter.discover_devices()
            except ImportError as e:
                logger.warning(f"OpenBCI adapter not available: {str(e)}")

        return discovered

    async def _discovery_loop(self) -> None:
        """Background task for periodic device discovery."""
        logger.info("Starting device discovery loop")

        while not self._shutdown_event.is_set():
            try:
                await self.discover_devices()
            except Exception as e:
                logger.error(f"Error in discovery loop: {str(e)}")

            # Wait for next discovery cycle
            try:
                await asyncio.wait_for(
                    self._shutdown_event.wait(),
                    timeout=self.config.discovery_interval_seconds,
                )
                break  # Shutdown requested
            except asyncio.TimeoutError:
                continue  # Continue discovery

        logger.info("Device discovery loop stopped")

    async def _health_monitoring_loop(self) -> None:
        """Background task for device health monitoring."""
        logger.info("Starting health monitoring loop")

        while not self._shutdown_event.is_set():
            try:
                for device_id in list(self.devices.keys()):
                    await self._check_device_health(device_id)

                self.stats.last_health_check = datetime.utcnow()

            except Exception as e:
                logger.error(f"Error in health monitoring loop: {str(e)}")

            # Wait for next health check cycle
            try:
                await asyncio.wait_for(
                    self._shutdown_event.wait(),
                    timeout=self.config.health_check_interval_seconds,
                )
                break  # Shutdown requested
            except asyncio.TimeoutError:
                continue  # Continue monitoring

        logger.info("Health monitoring loop stopped")

    async def _check_device_health(self, device_id: str) -> None:
        """Check health of a specific device.

        Args:
            device_id: Device identifier
        """
        if device_id not in self.devices:
            return

        device = self.devices[device_id]

        # Check if device is responsive
        try:
            await asyncio.wait_for(device.get_status(), timeout=5.0)  # 5 second timeout

            # Update last seen time
            device.device_info.last_seen = datetime.utcnow()

        except asyncio.TimeoutError:
            logger.warning(f"Device {device_id} health check timeout")
            self._emit_event("device_unresponsive", {"device_id": device_id}, "warning")

        except Exception as e:
            logger.error(f"Device {device_id} health check error: {str(e)}")
            self._emit_event(
                "device_error", {"device_id": device_id, "error": str(e)}, "error"
            )

    async def _event_processing_loop(self) -> None:
        """Background task for processing device events."""
        logger.info("Starting event processing loop")

        while not self._shutdown_event.is_set():
            try:
                # Process events from queue
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)

                await self._process_event(event)
                self.stats.events_processed += 1

            except asyncio.TimeoutError:
                continue  # No events in queue
            except Exception as e:
                logger.error(f"Error processing event: {str(e)}")

        logger.info("Event processing loop stopped")

    async def _process_event(self, event: DeviceEvent) -> None:
        """Process a device event.

        Args:
            event: Device event to process
        """
        # Log event if enabled
        if self.config.enable_event_logging:
            logger.info(f"Device event: {event.event_type} from {event.device_id}")

        # Call registered callbacks
        for callback in self.event_callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in event callback: {str(e)}")

    def _handle_device_event(self, event: DeviceEvent) -> None:
        """Handle events from devices.

        Args:
            event: Device event
        """
        try:
            self.event_queue.put_nowait(event)
        except asyncio.QueueFull:
            logger.warning("Event queue full, dropping event")

    def _handle_device_data(self, sample: DataSample) -> None:
        """Handle data samples from devices.

        Args:
            sample: Data sample
        """
        self.stats.data_samples_processed += 1

        # Call registered data callbacks
        for callback in self.data_callbacks:
            try:
                callback(sample)
            except Exception as e:
                logger.error(f"Error in data callback: {str(e)}")

    def _emit_event(
        self, event_type: str, data: Dict[str, Any] = None, severity: str = "info"
    ) -> None:
        """Emit a device manager event.

        Args:
            event_type: Type of event
            data: Event data
            severity: Event severity
        """
        event = DeviceEvent(
            event_type=event_type,
            device_id="device_manager",
            timestamp=datetime.utcnow(),
            data=data or {},
            severity=severity,
        )

        self._handle_device_event(event)
