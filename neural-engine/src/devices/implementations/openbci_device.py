"""OpenBCI device implementation for Cyton and Ganglion boards."""

import asyncio
import logging
import serial
import serial.tools.list_ports
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import numpy as np
import struct

from ..interfaces.base_device import BaseDevice, DeviceState, DeviceCapabilities
from ...ingestion.data_types import (
    DeviceInfo,
    ChannelInfo,
    NeuralSignalType,
    DataSource,
)

logger = logging.getLogger(__name__)


class OpenBCIDevice(BaseDevice):
    """OpenBCI device implementation for Cyton (8/16 channel) and Ganglion (4 channel) boards."""

    # OpenBCI protocol constants
    BYTE_START = 0xA0
    BYTE_END = 0xC0

    # Commands
    CMD_STOP = b"s"
    CMD_START = b"b"
    CMD_RESET = b"v"
    CMD_QUERY = b"?"
    CMD_CHANNEL_OFF = {i: f"{i}".encode() for i in range(1, 17)}
    CMD_CHANNEL_ON = {i: chr(ord("!") + i - 1).encode() for i in range(1, 17)}

    # Sampling rates
    CYTON_SAMPLING_RATE = 250.0
    GANGLION_SAMPLING_RATE = 200.0

    # Scale factors
    CYTON_SCALE_FACTOR = 4.5 / 24 / (2**23 - 1) * 1e6  # Convert to microvolts
    GANGLION_SCALE_FACTOR = 1.2 / 51.0 * 1e6  # Convert to microvolts

    def __init__(
        self, port: Optional[str] = None, board_type: str = "cyton", daisy: bool = False
    ):
        """
        Initialize OpenBCI device.

        Args:
            port: Serial port (e.g., '/dev / ttyUSB0' or 'COM3')
            board_type: Board type ('cyton' or 'ganglion')
            daisy: Whether Cyton daisy module is attached (16 channels)
        """
        self.board_type = board_type.lower()
        self.daisy = daisy

        if self.board_type == "cyton":
            n_channels = 16 if daisy else 8
            sampling_rate = self.CYTON_SAMPLING_RATE
            self.scale_factor = self.CYTON_SCALE_FACTOR
        elif self.board_type == "ganglion":
            n_channels = 4
            sampling_rate = self.GANGLION_SAMPLING_RATE
            self.scale_factor = self.GANGLION_SCALE_FACTOR
            if daisy:
                logger.warning("Ganglion does not support daisy module")
                daisy = False
        else:
            raise ValueError(f"Unknown board type: {board_type}")

        device_id = f"openbci_{board_type}_{port or 'auto'}"
        device_name = f"OpenBCI {board_type.capitalize()}"
        if daisy:
            device_name += " + Daisy"

        super().__init__(device_id, device_name)

        self.port = port
        self.n_channels = n_channels
        self.sampling_rate = sampling_rate
        self.serial: Optional[serial.Serial] = None
        self.packet_id = 0
        self.last_packet_id = -1
        self.buffer = bytearray()

    async def connect(self, **kwargs: Any) -> bool:
        """Connect to OpenBCI device."""
        try:
            self._update_state(DeviceState.CONNECTING)

            # Find serial port if not specified
            if not self.port:
                self.port = self._find_openbci_port()
                if not self.port:
                    raise ConnectionError("No OpenBCI device found")

            # Open serial connection
            self.serial = serial.Serial(port=self.port, baudrate=115200, timeout=1.0)

            # Reset board
            await self._send_command(self.CMD_RESET)
            await asyncio.sleep(0.5)

            # Stop streaming if already running
            await self._send_command(self.CMD_STOP)
            await asyncio.sleep(0.1)

            # Query board info
            await self._send_command(self.CMD_QUERY)
            await asyncio.sleep(0.1)

            # Read and log board response
            if self.serial.in_waiting:
                response = self.serial.read(self.serial.in_waiting)
                logger.info(
                    f"Board response: {response.decode('utf - 8', errors='ignore')}"
                )

            # Create device info
            channels = [
                ChannelInfo(
                    channel_id=i,
                    label=f"Ch{i + 1}",
                    unit="microvolts",
                    sampling_rate=self.sampling_rate,
                    hardware_id=f"N{i}P" if i < 8 else f"N{i - 8}P_DAISY",
                )
                for i in range(self.n_channels)
            ]

            self.device_info = DeviceInfo(
                device_id=self.device_id,
                device_type="OpenBCI",
                manufacturer="OpenBCI",
                model=(
                    f"{self.board_type.capitalize()}"
                    f"{' + Daisy' if self.daisy else ''}"
                ),
                firmware_version="3.0",  # Would need to parse from query response
                channels=channels,
            )

            self._update_state(DeviceState.CONNECTED)
            logger.info(f"Connected to {self.device_name} on {self.port}")
            return True

        except Exception as e:
            self._handle_error(e)
            return False

    def _find_openbci_port(self) -> Optional[str]:
        """Find OpenBCI serial port automatically."""
        ports = serial.tools.list_ports.comports()

        for port in ports:
            # OpenBCI boards typically show up with these identifiers
            if any(
                id_str in str(port.description).lower()
                for id_str in ["openbci", "ftdi", "serial"]
            ):
                logger.info(
                    f"Found potential OpenBCI device: "
                    f"{port.device} - {port.description}"
                )
                return str(port.device)

        return None

    async def _send_command(self, command: bytes) -> None:
        """Send command to OpenBCI board."""
        if self.serial:
            self.serial.write(command)
            await asyncio.sleep(0.01)  # Small delay for command processing

    async def disconnect(self) -> None:
        """Disconnect from OpenBCI device."""
        if self.serial:
            try:
                # Stop streaming
                await self._send_command(self.CMD_STOP)
                await asyncio.sleep(0.1)

                # Close serial connection
                self.serial.close()
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
            finally:
                self.serial = None

        self._update_state(DeviceState.DISCONNECTED)
        logger.info("Disconnected from OpenBCI device")

    async def start_streaming(self) -> None:
        """Start streaming data from OpenBCI."""
        if not self.is_connected():
            raise RuntimeError("Device not connected")

        if self.is_streaming():
            logger.warning("Already streaming")
            return

        # Start streaming command
        await self._send_command(self.CMD_START)

        self._stop_streaming.clear()
        self._update_state(DeviceState.STREAMING)

        # Start streaming task
        self._streaming_task = asyncio.create_task(self._streaming_loop())

    async def stop_streaming(self) -> None:
        """Stop streaming data."""
        if not self.is_streaming():
            return

        # Stop streaming command
        await self._send_command(self.CMD_STOP)

        self._stop_streaming.set()

        if self._streaming_task:
            await self._streaming_task
            self._streaming_task = None

        self._update_state(DeviceState.CONNECTED)

    async def _streaming_loop(self) -> None:  # noqa: C901
        """Main streaming loop."""
        if not self.serial:
            return

        samples_buffer = []
        packet_size = 33  # Standard OpenBCI packet size

        try:
            while not self._stop_streaming.is_set():
                # Read available data
                if self.serial.in_waiting:
                    data = self.serial.read(self.serial.in_waiting)
                    self.buffer.extend(data)

                # Process complete packets
                while len(self.buffer) >= packet_size:
                    # Look for start byte
                    start_idx = self.buffer.find(self.BYTE_START)
                    if start_idx == -1:
                        self.buffer.clear()
                        break

                    # Remove data before start byte
                    if start_idx > 0:
                        self.buffer = self.buffer[start_idx:]

                    # Check if we have a complete packet
                    if (
                        len(self.buffer) >= packet_size
                        and self.buffer[packet_size - 1] == self.BYTE_END
                    ):
                        packet = self.buffer[:packet_size]
                        self.buffer = self.buffer[packet_size:]

                        # Parse packet
                        sample = self._parse_packet(packet)
                        if sample is not None:
                            samples_buffer.append(sample)

                            # Send data in chunks (every 50ms worth of samples)
                            chunk_size = int(self.sampling_rate * 0.05)
                            if len(samples_buffer) >= chunk_size:
                                # Convert to numpy array
                                data = np.array(samples_buffer[:chunk_size]).T
                                samples_buffer = samples_buffer[chunk_size:]

                                # Create packet
                                data_packet = self._create_packet(
                                    data=data,
                                    timestamp=datetime.now(timezone.utc),
                                    signal_type=NeuralSignalType.EEG,
                                    source=DataSource.OPENBCI,
                                    metadata={
                                        "board_type": self.board_type,
                                        "daisy": self.daisy,
                                    },
                                )

                                if self._data_callback:
                                    self._data_callback(data_packet)
                    else:
                        # Incomplete packet, wait for more data
                        break

                # Small sleep to prevent busy waiting
                await asyncio.sleep(0.001)

        except Exception as e:
            self._handle_error(e)

    def _parse_packet(self, packet: bytes) -> Optional[List[float]]:
        """Parse OpenBCI packet and return channel values."""
        if len(packet) != 33:
            return None

        # Check start and end bytes
        if packet[0] != self.BYTE_START or packet[32] != self.BYTE_END:
            return None

        # Extract packet ID
        packet_id = packet[1]

        # Check for dropped packets
        expected_id = (self.last_packet_id + 1) % 256
        if self.last_packet_id != -1 and packet_id != expected_id:
            logger.warning(
                f"Dropped packet(s): expected {expected_id}, got {packet_id}"
            )
        self.last_packet_id = packet_id

        # Parse channel data (3 bytes per channel, 24 - bit signed)
        channel_data = []
        for i in range(8):  # First 8 channels
            raw = struct.unpack(">I", b"\x00" + packet[2 + i * 3 : 5 + i * 3])[0]
            if raw & 0x800000:  # Check sign bit
                raw = raw - 0x1000000
            channel_data.append(raw * self.scale_factor)

        # If daisy module, we'd need to handle alternating packets
        # For now, just duplicate channels if daisy is enabled
        if self.daisy:
            channel_data.extend(channel_data)  # Simplified for demo

        return channel_data[: self.n_channels]

    def get_capabilities(self) -> DeviceCapabilities:
        """Get device capabilities."""
        if self.board_type == "cyton":
            return DeviceCapabilities(
                supported_sampling_rates=[
                    250.0,
                    500.0,
                    1000.0,
                    2000.0,
                    4000.0,
                    8000.0,
                    16000.0,
                ],
                max_channels=16 if self.daisy else 8,
                signal_types=[NeuralSignalType.EEG, NeuralSignalType.EMG],
                has_impedance_check=True,
                has_battery_monitor=True,
                has_wireless=True,  # With WiFi shield
                has_trigger_input=True,
                has_aux_channels=True,
                supported_gains=[1, 2, 4, 6, 8, 12, 24],
            )
        else:  # Ganglion
            return DeviceCapabilities(
                supported_sampling_rates=[200.0],
                max_channels=4,
                signal_types=[NeuralSignalType.EEG, NeuralSignalType.EMG],
                has_impedance_check=True,
                has_battery_monitor=True,
                has_wireless=True,  # Bluetooth
                has_trigger_input=False,
                has_aux_channels=False,
                supported_gains=[1, 2, 4, 6, 8, 12, 24, 51],
            )

    def configure_channels(self, channels: List[ChannelInfo]) -> bool:
        """Configure OpenBCI channels."""
        if not self.is_connected():
            return False

        try:
            # Turn off all channels first
            for i in range(1, self.n_channels + 1):
                asyncio.create_task(self._send_command(self.CMD_CHANNEL_OFF[i]))

            # Turn on specified channels
            for channel in channels:
                if 0 <= channel.channel_id < self.n_channels:
                    asyncio.create_task(
                        self._send_command(self.CMD_CHANNEL_ON[channel.channel_id + 1])
                    )

            return True
        except Exception as e:
            logger.error(f"Error configuring channels: {e}")
            return False

    def set_sampling_rate(self, rate: float) -> bool:
        """Set sampling rate - limited support on OpenBCI."""
        if self.board_type == "ganglion":
            logger.warning("Ganglion does not support changing sampling rate")
            return False

        # Cyton supports different rates through ADS1299 register settings
        # This would require more complex register programming
        logger.warning("Sampling rate change not fully implemented")
        return False

    async def check_impedance(
        self, channel_ids: Optional[List[int]] = None
    ) -> Dict[int, float]:
        """Check impedance for channels."""
        # OpenBCI impedance checking requires special commands
        # and switching to impedance mode
        impedances = {}

        if channel_ids is None:
            channel_ids = list(range(self.n_channels))

        # Simplified - would need full implementation
        for ch_id in channel_ids:
            impedances[ch_id] = 5000.0  # 5kΩ placeholder

        return impedances
