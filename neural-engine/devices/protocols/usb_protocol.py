"""USB Communication Protocol for BCI Devices.

This module provides USB communication capabilities for devices
that connect via USB HID, USB CDC, or other USB interfaces.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass
from enum import Enum
import threading
import queue

try:
    import usb.core
    import usb.util

    USB_AVAILABLE = True
except ImportError:
    USB_AVAILABLE = False

logger = logging.getLogger(__name__)


class USBInterfaceType(Enum):
    """USB interface types."""

    HID = "hid"
    CDC = "cdc"
    BULK = "bulk"
    INTERRUPT = "interrupt"


@dataclass
class USBConfig:
    """USB configuration."""

    # Device identification
    vendor_id: int = 0x0000
    product_id: int = 0x0000
    serial_number: str = ""

    # Interface settings
    interface_type: USBInterfaceType = USBInterfaceType.HID
    endpoint_in: int = 0x81
    endpoint_out: int = 0x01

    # Communication settings
    timeout: int = 1000  # milliseconds
    buffer_size: int = 64

    # Data handling
    encoding: str = "utf-8"


@dataclass
class USBStats:
    """USB communication statistics."""

    bytes_sent: int = 0
    bytes_received: int = 0
    messages_sent: int = 0
    messages_received: int = 0
    errors: int = 0
    connection_time: Optional[datetime] = None
    last_activity: Optional[datetime] = None


class USBProtocol:
    """USB communication protocol handler."""

    def __init__(self, config: USBConfig = None):
        """Initialize USB protocol.

        Args:
            config: USB configuration
        """
        if not USB_AVAILABLE:
            raise ImportError("pyusb is required for USB communication")

        self.config = config or USBConfig()

        # Connection state
        self.device: Optional[Any] = None
        self.is_connected = False

        # Threading for async operations
        self.read_thread: Optional[threading.Thread] = None
        self.thread_stop_event = threading.Event()

        # Data queues
        self.incoming_queue = queue.Queue(maxsize=1000)
        self.outgoing_queue = queue.Queue(maxsize=1000)

        # Callbacks
        self.data_callbacks: List[Callable[[bytes], None]] = []
        self.message_callbacks: List[Callable[[str], None]] = []
        self.error_callbacks: List[Callable[[Exception], None]] = []

        # Statistics
        self.stats = USBStats()

        logger.info(
            f"USBProtocol initialized for VID:{self.config.vendor_id:04X} PID:{self.config.product_id:04X}"
        )

    async def connect(self) -> bool:
        """Connect to USB device.

        Returns:
            True if connection successful
        """
        # Placeholder implementation - actual USB implementation would be complex
        logger.warning("USB protocol is not fully implemented yet")
        return False

    async def disconnect(self) -> bool:
        """Disconnect from USB device.

        Returns:
            True if disconnection successful
        """
        logger.info("USB protocol disconnection")
        return True

    async def send_data(self, data: Union[str, bytes]) -> bool:
        """Send data over USB connection.

        Args:
            data: Data to send

        Returns:
            True if data sent successfully
        """
        logger.debug(f"USB send data: {data}")
        return False

    @staticmethod
    def list_usb_devices() -> List[Dict[str, Any]]:
        """List available USB devices.

        Returns:
            List of USB device information
        """
        if not USB_AVAILABLE:
            return []

        devices = []
        try:
            for device in usb.core.find(find_all=True):
                devices.append(
                    {
                        "vendor_id": device.idVendor,
                        "product_id": device.idProduct,
                        "manufacturer": (
                            usb.util.get_string(device, device.iManufacturer)
                            if device.iManufacturer
                            else ""
                        ),
                        "product": (
                            usb.util.get_string(device, device.iProduct)
                            if device.iProduct
                            else ""
                        ),
                        "serial_number": (
                            usb.util.get_string(device, device.iSerialNumber)
                            if device.iSerialNumber
                            else ""
                        ),
                    }
                )
        except Exception as e:
            logger.error(f"Error listing USB devices: {str(e)}")

        return devices

    def __str__(self) -> str:
        """String representation."""
        return f"USBProtocol(VID:{self.config.vendor_id:04X}, PID:{self.config.product_id:04X})"
