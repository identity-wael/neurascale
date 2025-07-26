"""Serial Communication Protocol for BCI Devices.

This module provides low-level serial communication capabilities
for devices that connect via RS-232, USB-Serial, or other serial interfaces.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass
from enum import Enum
import threading
import queue
import time

try:
    import serial
    import serial.tools.list_ports

    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

logger = logging.getLogger(__name__)


class SerialParity(Enum):
    """Serial parity options."""

    NONE = "none"
    EVEN = "even"
    ODD = "odd"
    MARK = "mark"
    SPACE = "space"


class SerialStopBits(Enum):
    """Serial stop bits options."""

    ONE = 1
    ONE_POINT_FIVE = 1.5
    TWO = 2


@dataclass
class SerialConfig:
    """Serial port configuration."""

    # Connection parameters
    port: str = ""  # e.g., "/dev / ttyUSB0", "COM3"
    baudrate: int = 115200
    bytesize: int = 8
    parity: SerialParity = SerialParity.NONE
    stopbits: SerialStopBits = SerialStopBits.ONE

    # Timeouts
    timeout: float = 1.0
    write_timeout: float = 1.0

    # Flow control
    rtscts: bool = False  # Hardware flow control
    dsrdtr: bool = False  # Hardware flow control
    xonxoff: bool = False  # Software flow control

    # Buffer settings
    buffer_size: int = 8192

    # Protocol settings
    line_ending: str = "\n"
    encoding: str = "utf-8"


@dataclass
class SerialStats:
    """Serial communication statistics."""

    bytes_sent: int = 0
    bytes_received: int = 0
    messages_sent: int = 0
    messages_received: int = 0
    errors: int = 0
    timeouts: int = 0
    connection_time: Optional[datetime] = None
    last_activity: Optional[datetime] = None


class SerialProtocol:
    """High-level serial communication protocol handler."""

    def __init__(self, config: SerialConfig = None):
        """Initialize serial protocol.

        Args:
            config: Serial configuration
        """
        if not SERIAL_AVAILABLE:
            raise ImportError("pyserial is required for serial communication")

        self.config = config or SerialConfig()

        # Connection state
        self.serial_port: Optional[serial.Serial] = None
        self.is_connected = False
        self.is_reading = False

        # Threading for async operations
        self.read_thread: Optional[threading.Thread] = None
        self.write_thread: Optional[threading.Thread] = None
        self.thread_stop_event = threading.Event()

        # Data queues
        self.incoming_queue = queue.Queue(maxsize=1000)
        self.outgoing_queue = queue.Queue(maxsize=1000)

        # Callbacks
        self.data_callbacks: List[Callable[[bytes], None]] = []
        self.message_callbacks: List[Callable[[str], None]] = []
        self.error_callbacks: List[Callable[[Exception], None]] = []

        # Statistics
        self.stats = SerialStats()

        logger.info(f"SerialProtocol initialized for port: {self.config.port}")

    async def connect(self) -> bool:
        """Connect to serial port.

        Returns:
            True if connection successful
        """
        if self.is_connected:
            logger.warning("Already connected to serial port")
            return True

        try:
            # Convert enum values to pyserial constants
            parity_map = {
                SerialParity.NONE: serial.PARITY_NONE,
                SerialParity.EVEN: serial.PARITY_EVEN,
                SerialParity.ODD: serial.PARITY_ODD,
                SerialParity.MARK: serial.PARITY_MARK,
                SerialParity.SPACE: serial.PARITY_SPACE,
            }

            stopbits_map = {
                SerialStopBits.ONE: serial.STOPBITS_ONE,
                SerialStopBits.ONE_POINT_FIVE: serial.STOPBITS_ONE_POINT_FIVE,
                SerialStopBits.TWO: serial.STOPBITS_TWO,
            }

            # Create serial connection
            self.serial_port = serial.Serial(
                port=self.config.port,
                baudrate=self.config.baudrate,
                bytesize=self.config.bytesize,
                parity=parity_map[self.config.parity],
                stopbits=stopbits_map[self.config.stopbits],
                timeout=self.config.timeout,
                write_timeout=self.config.write_timeout,
                rtscts=self.config.rtscts,
                dsrdtr=self.config.dsrdtr,
                xonxoff=self.config.xonxoff,
            )

            # Test connection
            if not self.serial_port.is_open:
                self.serial_port.open()

            # Clear buffers
            self.serial_port.reset_input_buffer()
            self.serial_port.reset_output_buffer()

            self.is_connected = True
            self.stats.connection_time = datetime.utcnow()

            # Start communication threads
            self._start_communication_threads()

            logger.info(f"Connected to serial port: {self.config.port}")
            return True

        except Exception as e:
            logger.error(
                f"Failed to connect to serial port {self.config.port}: {str(e)}"
            )
            self._handle_error(e)
            return False

    async def disconnect(self) -> bool:
        """Disconnect from serial port.

        Returns:
            True if disconnection successful
        """
        if not self.is_connected:
            return True

        try:
            # Stop communication threads
            self._stop_communication_threads()

            # Close serial port
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()

            self.is_connected = False

            logger.info(f"Disconnected from serial port: {self.config.port}")
            return True

        except Exception as e:
            logger.error(f"Error disconnecting from serial port: {str(e)}")
            self._handle_error(e)
            return False

    async def send_data(self, data: Union[str, bytes]) -> bool:
        """Send data over serial connection.

        Args:
            data: Data to send (string or bytes)

        Returns:
            True if data sent successfully
        """
        if not self.is_connected:
            logger.error("Not connected to serial port")
            return False

        try:
            # Convert string to bytes if necessary
            if isinstance(data, str):
                data_bytes = data.encode(self.config.encoding)
            else:
                data_bytes = data

            # Add to outgoing queue
            self.outgoing_queue.put_nowait(data_bytes)

            return True

        except queue.Full:
            logger.error("Outgoing queue full")
            return False
        except Exception as e:
            logger.error(f"Error sending data: {str(e)}")
            self._handle_error(e)
            return False

    async def send_command(self, command: str) -> bool:
        """Send a command with line ending.

        Args:
            command: Command string to send

        Returns:
            True if command sent successfully
        """
        full_command = command + self.config.line_ending
        return await self.send_data(full_command)

    async def read_data(self, timeout: float = None) -> Optional[bytes]:
        """Read raw data from serial port.

        Args:
            timeout: Read timeout in seconds

        Returns:
            Received data or None if timeout / error
        """
        try:
            # Use provided timeout or default
            read_timeout = timeout or self.config.timeout

            return self.incoming_queue.get(timeout=read_timeout)

        except queue.Empty:
            return None
        except Exception as e:
            logger.error(f"Error reading data: {str(e)}")
            self._handle_error(e)
            return None

    async def read_message(self, timeout: float = None) -> Optional[str]:
        """Read a complete message (until line ending).

        Args:
            timeout: Read timeout in seconds

        Returns:
            Received message or None if timeout / error
        """
        data = await self.read_data(timeout)
        if data:
            try:
                message = data.decode(self.config.encoding).strip()
                return message
            except UnicodeDecodeError as e:
                logger.error(f"Error decoding message: {str(e)}")
                return None
        return None

    async def send_and_receive(
        self, command: str, timeout: float = None, expect_response: bool = True
    ) -> Optional[str]:
        """Send command and wait for response.

        Args:
            command: Command to send
            timeout: Response timeout
            expect_response: Whether to wait for a response

        Returns:
            Response message or None
        """
        # Send command
        success = await self.send_command(command)
        if not success:
            return None

        # Wait for response if expected
        if expect_response:
            return await self.read_message(timeout)

        return ""

    def add_data_callback(self, callback: Callable[[bytes], None]) -> None:
        """Add callback for raw data reception.

        Args:
            callback: Function to call when data is received
        """
        self.data_callbacks.append(callback)

    def add_message_callback(self, callback: Callable[[str], None]) -> None:
        """Add callback for message reception.

        Args:
            callback: Function to call when messages are received
        """
        self.message_callbacks.append(callback)

    def add_error_callback(self, callback: Callable[[Exception], None]) -> None:
        """Add callback for error handling.

        Args:
            callback: Function to call when errors occur
        """
        self.error_callbacks.append(callback)

    def get_stats(self) -> SerialStats:
        """Get communication statistics.

        Returns:
            Current statistics
        """
        return self.stats

    def is_port_available(self, port: str) -> bool:
        """Check if a serial port is available.

        Args:
            port: Port name to check

        Returns:
            True if port is available
        """
        try:
            available_ports = [p.device for p in serial.tools.list_ports.comports()]
            return port in available_ports
        except Exception:
            return False

    @staticmethod
    def list_available_ports() -> List[Dict[str, str]]:
        """List all available serial ports.

        Returns:
            List of port information dictionaries
        """
        if not SERIAL_AVAILABLE:
            return []

        ports = []
        try:
            for port in serial.tools.list_ports.comports():
                ports.append(
                    {
                        "device": port.device,
                        "name": port.name,
                        "description": port.description or "",
                        "manufacturer": port.manufacturer or "",
                        "serial_number": port.serial_number or "",
                        "vid": port.vid,
                        "pid": port.pid,
                    }
                )
        except Exception as e:
            logger.error(f"Error listing serial ports: {str(e)}")

        return ports

    # Private methods

    def _start_communication_threads(self) -> None:
        """Start background communication threads."""
        self.thread_stop_event.clear()

        # Start read thread
        self.read_thread = threading.Thread(
            target=self._read_thread_worker,
            daemon=True,
            name=f"SerialRead_{self.config.port}",
        )
        self.read_thread.start()

        # Start write thread
        self.write_thread = threading.Thread(
            target=self._write_thread_worker,
            daemon=True,
            name=f"SerialWrite_{self.config.port}",
        )
        self.write_thread.start()

        self.is_reading = True
        logger.debug("Started serial communication threads")

    def _stop_communication_threads(self) -> None:
        """Stop background communication threads."""
        self.thread_stop_event.set()
        self.is_reading = False

        # Wait for threads to finish
        if self.read_thread and self.read_thread.is_alive():
            self.read_thread.join(timeout=2.0)

        if self.write_thread and self.write_thread.is_alive():
            self.write_thread.join(timeout=2.0)

        logger.debug("Stopped serial communication threads")

    def _read_thread_worker(self) -> None:
        """Worker thread for reading serial data."""
        logger.debug("Serial read thread started")

        buffer = b""
        line_ending_bytes = self.config.line_ending.encode(self.config.encoding)

        while not self.thread_stop_event.is_set() and self.is_connected:
            try:
                if self.serial_port and self.serial_port.is_open:
                    # Read available data
                    if self.serial_port.in_waiting > 0:
                        chunk = self.serial_port.read(self.serial_port.in_waiting)
                        if chunk:
                            buffer += chunk
                            self.stats.bytes_received += len(chunk)
                            self.stats.last_activity = datetime.utcnow()

                            # Call raw data callbacks
                            for callback in self.data_callbacks:
                                try:
                                    callback(chunk)
                                except Exception as e:
                                    logger.error(f"Error in data callback: {str(e)}")

                            # Process complete messages
                            while line_ending_bytes in buffer:
                                message_bytes, buffer = buffer.split(
                                    line_ending_bytes, 1
                                )

                                try:
                                    # Add to incoming queue
                                    self.incoming_queue.put_nowait(message_bytes)

                                    # Decode and call message callbacks
                                    message = message_bytes.decode(self.config.encoding)
                                    self.stats.messages_received += 1

                                    for callback in self.message_callbacks:
                                        try:
                                            callback(message)
                                        except Exception as e:
                                            logger.error(
                                                f"Error in message callback: {str(e)}"
                                            )

                                except queue.Full:
                                    logger.warning(
                                        "Incoming queue full, dropping message"
                                    )
                                except UnicodeDecodeError as e:
                                    logger.error(f"Error decoding message: {str(e)}")

                # Small delay to prevent excessive CPU usage
                time.sleep(0.001)  # 1ms

            except Exception as e:
                logger.error(f"Error in serial read thread: {str(e)}")
                self._handle_error(e)
                time.sleep(0.1)

        logger.debug("Serial read thread stopped")

    def _write_thread_worker(self) -> None:
        """Worker thread for writing serial data."""
        logger.debug("Serial write thread started")

        while not self.thread_stop_event.is_set() and self.is_connected:
            try:
                # Get data from outgoing queue
                try:
                    data = self.outgoing_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                # Write data to serial port
                if self.serial_port and self.serial_port.is_open:
                    bytes_written = self.serial_port.write(data)
                    self.serial_port.flush()  # Ensure data is sent immediately

                    self.stats.bytes_sent += bytes_written
                    self.stats.messages_sent += 1
                    self.stats.last_activity = datetime.utcnow()

                self.outgoing_queue.task_done()

            except Exception as e:
                logger.error(f"Error in serial write thread: {str(e)}")
                self._handle_error(e)
                time.sleep(0.1)

        logger.debug("Serial write thread stopped")

    def _handle_error(self, error: Exception) -> None:
        """Handle communication errors.

        Args:
            error: Exception that occurred
        """
        self.stats.errors += 1

        # Call error callbacks
        for callback in self.error_callbacks:
            try:
                callback(error)
            except Exception as e:
                logger.error(f"Error in error callback: {str(e)}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.is_connected:
            # Use asyncio.run for cleanup if in sync context
            try:

                asyncio.run(self.disconnect())
            except Exception:
                # Fallback to direct disconnection
                self._stop_communication_threads()
                if self.serial_port and self.serial_port.is_open:
                    self.serial_port.close()

    def __str__(self) -> str:
        """String representation."""
        return (
            f"SerialProtocol(port={self.config.port}, baudrate={self.config.baudrate})"
        )

    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"SerialProtocol(port={self.config.port}, baudrate={self.config.baudrate}, "
            f"connected={self.is_connected}, reading={self.is_reading})"
        )
