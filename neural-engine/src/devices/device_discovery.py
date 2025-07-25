"""Device discovery service for automatic detection of neural devices."""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import serial
import serial.tools.list_ports

try:
    from zeroconf import ServiceBrowser, Zeroconf, ServiceInfo

    ZEROCONF_AVAILABLE = True
except ImportError:
    ZEROCONF_AVAILABLE = False
    ServiceBrowser = None
    Zeroconf = None
    ServiceInfo = None

try:
    import bluetooth

    BLUETOOTH_AVAILABLE = True
except ImportError:
    BLUETOOTH_AVAILABLE = False
    bluetooth = None

try:
    from pylsl import resolve_streams

    LSL_AVAILABLE = True
except ImportError:
    LSL_AVAILABLE = False
    resolve_streams = None

try:
    from brainflow.board_shim import BoardShim, BoardIds

    BRAINFLOW_AVAILABLE = True
except ImportError:
    BRAINFLOW_AVAILABLE = False
    BoardShim = None

logger = logging.getLogger(__name__)


class DeviceProtocol(Enum):
    """Supported device communication protocols."""

    SERIAL = "serial"
    BLUETOOTH = "bluetooth"
    WIFI = "wifi"
    LSL = "lsl"
    USB = "usb"


@dataclass
class DiscoveredDevice:
    """Information about a discovered device."""

    device_type: str  # e.g., "OpenBCI", "LSL", "BrainFlow"
    device_name: str
    protocol: DeviceProtocol
    connection_info: Dict[str, Any]
    discovered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def unique_id(self) -> str:
        """Generate unique ID for device."""
        if self.protocol == DeviceProtocol.SERIAL:
            return f"{self.device_type}_{self.connection_info.get('port', 'unknown')}"
        elif self.protocol == DeviceProtocol.BLUETOOTH:
            return (
                f"{self.device_type}_{self.connection_info.get('address', 'unknown')}"
            )
        elif self.protocol == DeviceProtocol.WIFI:
            return f"{self.device_type}_{self.connection_info.get('ip', 'unknown')}"
        elif self.protocol == DeviceProtocol.LSL:
            return f"{self.device_type}_{self.connection_info.get('name', 'unknown')}"
        else:
            return f"{self.device_type}_{self.device_name}"


class DeviceDiscoveryService:
    """Service for discovering neural data acquisition devices."""

    def __init__(self) -> None:
        """Initialize device discovery service."""
        self._discovered_devices: Dict[str, DiscoveredDevice] = {}
        self._discovery_callbacks: List[Callable[[DiscoveredDevice], None]] = []
        self._is_scanning = False
        self._scan_task: Optional[asyncio.Task] = None

        # Zeroconf for mDNS/Bonjour discovery
        self._zeroconf: Optional[Zeroconf] = None
        self._browser: Optional[ServiceBrowser] = None

    def add_discovery_callback(self, callback: Callable[[DiscoveredDevice], None]) -> None:
        """Add callback for device discovery events."""
        self._discovery_callbacks.append(callback)

    def remove_discovery_callback(self, callback: Callable[[DiscoveredDevice], None]) -> None:
        """Remove discovery callback."""
        if callback in self._discovery_callbacks:
            self._discovery_callbacks.remove(callback)

    async def start_discovery(
        self, protocols: Optional[List[DeviceProtocol]] = None
    ) -> None:
        """
        Start device discovery.

        Args:
            protocols: List of protocols to scan, or None for all
        """
        if self._is_scanning:
            logger.warning("Discovery already in progress")
            return

        self._is_scanning = True

        if protocols is None:
            protocols = list(DeviceProtocol)

        # Start discovery tasks
        tasks = []

        if DeviceProtocol.SERIAL in protocols:
            tasks.append(self._discover_serial_devices())

        if DeviceProtocol.BLUETOOTH in protocols and BLUETOOTH_AVAILABLE:
            tasks.append(self._discover_bluetooth_devices())

        if DeviceProtocol.WIFI in protocols and ZEROCONF_AVAILABLE:
            tasks.append(self._discover_wifi_devices())

        if DeviceProtocol.LSL in protocols and LSL_AVAILABLE:
            tasks.append(self._discover_lsl_devices())

        if BRAINFLOW_AVAILABLE:
            tasks.append(self._discover_brainflow_devices())

        # Run all discovery tasks
        self._scan_task = asyncio.create_task(self._run_discovery(tasks))

    async def stop_discovery(self) -> None:
        """Stop device discovery."""
        self._is_scanning = False

        if self._scan_task:
            self._scan_task.cancel()
            try:
                await self._scan_task
            except asyncio.CancelledError:
                pass
            self._scan_task = None

        # Cleanup Zeroconf
        if self._browser:
            self._browser.cancel()
            self._browser = None

        if self._zeroconf:
            self._zeroconf.close()
            self._zeroconf = None

    async def _run_discovery(self, tasks: List[asyncio.Task]) -> None:
        """Run discovery tasks."""
        try:
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error during discovery: {e}")

    def get_discovered_devices(self) -> List[DiscoveredDevice]:
        """Get list of discovered devices."""
        return list(self._discovered_devices.values())

    def _notify_device_discovered(self, device: DiscoveredDevice) -> None:
        """Notify callbacks about discovered device."""
        # Check if device already discovered
        if device.unique_id in self._discovered_devices:
            return

        self._discovered_devices[device.unique_id] = device

        # Notify callbacks
        for callback in self._discovery_callbacks:
            try:
                callback(device)
            except Exception as e:
                logger.error(f"Error in discovery callback: {e}")

    async def _discover_serial_devices(self) -> None:
        """Discover devices connected via serial ports."""
        logger.info("Scanning for serial devices...")

        try:
            # List all serial ports
            ports = serial.tools.list_ports.comports()

            for port in ports:
                # Check if it might be a neural device
                device_type = None
                device_name = port.description

                # OpenBCI detection
                if any(
                    keyword in port.description.lower()
                    for keyword in ["openbci", "ftdi", "ch340"]
                ):
                    device_type = "OpenBCI"

                    # Try to identify specific OpenBCI board
                    if "cyton" in port.description.lower():
                        device_name = "OpenBCI Cyton"
                    elif "ganglion" in port.description.lower():
                        device_name = "OpenBCI Ganglion"
                    else:
                        device_name = "OpenBCI Device"

                # Generic FTDI/Arduino detection (could be custom BCI)
                elif (
                    "ftdi" in port.description.lower()
                    or "arduino" in port.description.lower()
                ):
                    device_type = "Serial BCI"
                    device_name = f"Serial Device ({port.description})"

                if device_type:
                    device = DiscoveredDevice(
                        device_type=device_type,
                        device_name=device_name,
                        protocol=DeviceProtocol.SERIAL,
                        connection_info={
                            "port": port.device,
                            "description": port.description,
                            "hwid": port.hwid,
                            "vid": port.vid,
                            "pid": port.pid,
                        },
                        metadata={
                            "manufacturer": port.manufacturer,
                            "product": port.product,
                            "serial_number": port.serial_number,
                        },
                    )

                    self._notify_device_discovered(device)

        except Exception as e:
            logger.error(f"Error scanning serial devices: {e}")

    async def _discover_bluetooth_devices(self):  # noqa: C901
        """Discover Bluetooth devices."""
        if not BLUETOOTH_AVAILABLE:
            logger.warning("Bluetooth module not available")
            return

        logger.info("Scanning for Bluetooth devices...")

        try:
            # Discover Bluetooth devices
            devices = bluetooth.discover_devices(duration=8, lookup_names=True)

            for addr, name in devices:
                device_type = None
                device_name = name

                # Check for known BCI devices
                if name:
                    name_lower = name.lower()

                    if "ganglion" in name_lower:
                        device_type = "OpenBCI"
                        device_name = "OpenBCI Ganglion"
                    elif "muse" in name_lower:
                        device_type = "Muse"
                        device_name = f"Muse ({name})"
                    elif "brainbit" in name_lower:
                        device_type = "BrainBit"
                        device_name = f"BrainBit ({name})"
                    elif "crown" in name_lower or "neurosity" in name_lower:
                        device_type = "Neurosity"
                        device_name = "Neurosity Crown"
                    elif any(
                        keyword in name_lower for keyword in ["eeg", "bci", "brain"]
                    ):
                        device_type = "Bluetooth BCI"
                        device_name = name

                if device_type:
                    device = DiscoveredDevice(
                        device_type=device_type,
                        device_name=device_name,
                        protocol=DeviceProtocol.BLUETOOTH,
                        connection_info={
                            "address": addr,
                            "name": name,
                        },
                    )

                    self._notify_device_discovered(device)

        except Exception as e:
            logger.error(f"Error scanning Bluetooth devices: {e}")

    async def _discover_wifi_devices(self) -> None:
        """Discover WiFi devices using mDNS/Bonjour."""
        if not ZEROCONF_AVAILABLE:
            logger.warning("Zeroconf module not available")
            return

        logger.info("Scanning for WiFi devices...")

        try:
            # Initialize Zeroconf
            self._zeroconf = Zeroconf()

            # Service types to look for
            service_types = [
                "_openbci._tcp.local.",
                "_neurosity._tcp.local.",
                "_bci._tcp.local.",
                "_eeg._tcp.local.",
            ]

            # Create browser for each service type
            browsers = []
            for service_type in service_types:
                browser = ServiceBrowser(
                    self._zeroconf,
                    service_type,
                    handlers=[self._on_service_state_change],
                )
                browsers.append(browser)

            # Let it scan for 5 seconds
            await asyncio.sleep(5)

            # Cancel browsers
            for browser in browsers:
                browser.cancel()

        except Exception as e:
            logger.error(f"Error scanning WiFi devices: {e}")

    def _on_service_state_change(self, zeroconf, service_type, name, state_change) -> None:
        """Handle mDNS service discovery."""
        if state_change == "added":
            info = zeroconf.get_service_info(service_type, name)
            if info:
                # Parse service info
                device_type = "WiFi BCI"
                device_name = name.split(".")[0]

                if "openbci" in name.lower():
                    device_type = "OpenBCI"
                    device_name = "OpenBCI WiFi Shield"
                elif "neurosity" in name.lower():
                    device_type = "Neurosity"
                    device_name = "Neurosity Crown"

                # Get IP address
                addresses = info.parsed_addresses()
                ip_address = addresses[0] if addresses else "unknown"

                device = DiscoveredDevice(
                    device_type=device_type,
                    device_name=device_name,
                    protocol=DeviceProtocol.WIFI,
                    connection_info={
                        "ip": ip_address,
                        "port": info.port,
                        "hostname": info.server,
                    },
                    metadata={
                        "properties": info.properties,
                    },
                )

                self._notify_device_discovered(device)

    async def _discover_lsl_devices(self) -> None:
        """Discover LSL streams."""
        if not LSL_AVAILABLE:
            logger.warning("LSL module not available")
            return

        logger.info("Scanning for LSL streams...")

        try:
            # Resolve LSL streams
            streams = resolve_streams(wait_time=3.0)

            for stream in streams:
                # Get stream info
                info = stream

                device = DiscoveredDevice(
                    device_type="LSL",
                    device_name=f"LSL Stream: {info.name()}",
                    protocol=DeviceProtocol.LSL,
                    connection_info={
                        "name": info.name(),
                        "type": info.type(),
                        "hostname": info.hostname(),
                        "uid": info.uid(),
                    },
                    metadata={
                        "channel_count": info.channel_count(),
                        "sampling_rate": info.nominal_srate(),
                        "channel_format": info.channel_format(),
                    },
                )

                self._notify_device_discovered(device)

        except Exception as e:
            logger.error(f"Error scanning LSL streams: {e}")

    async def _discover_brainflow_devices(self) -> None:
        """Discover devices supported by BrainFlow."""
        if not BRAINFLOW_AVAILABLE:
            return

        logger.info("Checking for BrainFlow synthetic device...")

        # BrainFlow always has synthetic board available
        device = DiscoveredDevice(
            device_type="BrainFlow",
            device_name="BrainFlow Synthetic Board",
            protocol=DeviceProtocol.USB,  # Synthetic device
            connection_info={
                "board_id": (
                    BoardIds.SYNTHETIC_BOARD.value
                    if hasattr(BoardIds, "SYNTHETIC_BOARD")
                    else -1
                ),
            },
            metadata={
                "is_synthetic": True,
            },
        )

        self._notify_device_discovered(device)

    async def quick_scan(self, timeout: float = 10.0) -> List[DiscoveredDevice]:
        """
        Perform a quick scan for devices.

        Args:
            timeout: Maximum time to scan in seconds

        Returns:
            List of discovered devices
        """
        # Clear previous results
        self._discovered_devices.clear()

        # Start discovery
        await self.start_discovery()

        # Wait for timeout
        await asyncio.sleep(timeout)

        # Stop discovery
        await self.stop_discovery()

        return self.get_discovered_devices()
