"""Lab Streaming Layer (LSL) device implementation."""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import numpy as np

try:
    from pylsl import StreamInlet, resolve_stream, StreamInfo

    LSL_AVAILABLE = True
except ImportError:
    LSL_AVAILABLE = False
    StreamInlet = None
    StreamInfo = None

from ..interfaces.base_device import BaseDevice, DeviceState, DeviceCapabilities
from ...ingestion.data_types import (
    DeviceInfo,
    ChannelInfo,
    NeuralSignalType,
    DataSource,
)

logger = logging.getLogger(__name__)


class LSLDevice(BaseDevice):
    """Lab Streaming Layer device for receiving neural data streams."""

    def __init__(
        self,
        stream_name: Optional[str] = None,
        stream_type: Optional[str] = None,
        timeout: float = 5.0,
    ):
        """
        Initialize LSL device.

        Args:
            stream_name: Name of the LSL stream to connect to
            stream_type: Type of the LSL stream (e.g., 'EEG', 'EMG')
            timeout: Timeout for stream resolution in seconds
        """
        if not LSL_AVAILABLE:
            raise ImportError("pylsl is not installed. Install with: pip install pylsl")

        device_id = f"lsl_{stream_name or 'any'}_{stream_type or 'any'}"
        super().__init__(device_id, f"LSL-{stream_name or 'Stream'}")

        self.stream_name = stream_name
        self.stream_type = stream_type
        self.timeout = timeout
        self.inlet: Optional[StreamInlet] = None
        self.stream_info: Optional[StreamInfo] = None
        self.sampling_rate: float = 256.0
        self.n_channels: int = 0
        self.channel_names: List[str] = []
        self.signal_type = NeuralSignalType.EEG  # Default, will be updated

    async def connect(self, **kwargs: Any) -> bool:
        """Connect to LSL stream."""
        try:
            self._update_state(DeviceState.CONNECTING)

            # Run stream resolution in executor to avoid blocking
            loop = asyncio.get_event_loop()
            streams = await loop.run_in_executor(None, self._resolve_streams)

            if not streams:
                raise ConnectionError("No LSL streams found matching criteria")

            # Use the first matching stream
            stream_info = streams[0]

            # Create inlet
            self.inlet = StreamInlet(stream_info, max_chunklen=1024)
            self.stream_info = stream_info

            # Extract stream information
            self.sampling_rate = stream_info.nominal_srate()
            self.n_channels = stream_info.channel_count()

            # Get channel names
            self.channel_names = []
            channels_xml = stream_info.desc().child("channels")
            if channels_xml:
                channel = channels_xml.child("channel")
                while channel:
                    label = channel.child_value("label")
                    if label:
                        self.channel_names.append(label)
                    channel = channel.next_sibling()

            # If no channel names found, create default names
            if not self.channel_names:
                self.channel_names = [f"Ch{i + 1}" for i in range(self.n_channels)]

            # Determine signal type from stream type
            stream_type_str = stream_info.type().upper()
            signal_type_map = {
                "EEG": NeuralSignalType.EEG,
                "EMG": NeuralSignalType.EMG,
                "ECG": NeuralSignalType.ECOG,
                "ACCELEROMETER": NeuralSignalType.ACCELEROMETER,
                "ACC": NeuralSignalType.ACCELEROMETER,
            }
            self.signal_type = signal_type_map.get(
                stream_type_str, NeuralSignalType.CUSTOM
            )

            # Create device info
            channels = [
                ChannelInfo(
                    channel_id=i,
                    label=(
                        self.channel_names[i]
                        if i < len(self.channel_names)
                        else f"Ch{i + 1}"
                    ),
                    unit="microvolts",
                    sampling_rate=self.sampling_rate,
                )
                for i in range(self.n_channels)
            ]

            self.device_info = DeviceInfo(
                device_id=self.device_id,
                device_type="LSL",
                manufacturer=stream_info.hostname(),
                model=stream_info.name(),
                channels=channels,
            )

            self._update_state(DeviceState.CONNECTED)
            logger.info(
                f"Connected to LSL stream: {stream_info.name()} "
                f"({self.n_channels} channels @ {self.sampling_rate}Hz)"
            )
            return True

        except Exception as e:
            self._handle_error(e)
            return False

    def _resolve_streams(self) -> List[StreamInfo]:
        """Resolve LSL streams matching criteria."""
        pred_parts = []
        if self.stream_name:
            pred_parts.append(f"name='{self.stream_name}'")
        if self.stream_type:
            pred_parts.append(f"type='{self.stream_type}'")

        predicate = " and ".join(pred_parts) if pred_parts else ""

        logger.info(f"Resolving LSL streams with predicate: {predicate or 'any'}")
        streams = resolve_stream(predicate, timeout=self.timeout)

        return list(streams)

    async def disconnect(self) -> None:
        """Disconnect from LSL stream."""
        if self.inlet:
            self.inlet.close_stream()
            self.inlet = None

        self.stream_info = None
        self._update_state(DeviceState.DISCONNECTED)
        logger.info("Disconnected from LSL stream")

    async def start_streaming(self) -> None:
        """Start streaming data from LSL."""
        if not self.is_connected():
            raise RuntimeError("Device not connected")

        if self.is_streaming():
            logger.warning("Already streaming")
            return

        self._stop_streaming.clear()
        self._update_state(DeviceState.STREAMING)

        # Start streaming task
        self._streaming_task = asyncio.create_task(self._streaming_loop())

    async def stop_streaming(self) -> None:
        """Stop streaming data."""
        if not self.is_streaming():
            return

        self._stop_streaming.set()

        if self._streaming_task:
            await self._streaming_task
            self._streaming_task = None

        self._update_state(DeviceState.CONNECTED)

    async def _streaming_loop(self) -> None:
        """Main streaming loop."""
        if not self.inlet:
            return

        chunk_size = int(self.sampling_rate * 0.05)  # 50ms chunks

        try:
            while not self._stop_streaming.is_set():
                # Pull chunk from inlet
                loop = asyncio.get_event_loop()
                samples, timestamps = await loop.run_in_executor(
                    None,
                    self.inlet.pull_chunk,
                    0.0,  # timeout
                    chunk_size,  # max samples
                )

                if samples:
                    # Convert to numpy array
                    data = np.array(samples).T  # Transpose to (channels, samples)

                    # Use the last timestamp as packet timestamp
                    timestamp = datetime.fromtimestamp(timestamps[-1], tz=timezone.utc)

                    # Create and send packet
                    packet = self._create_packet(
                        data=data,
                        timestamp=timestamp,
                        signal_type=self.signal_type,
                        source=DataSource.LSL,
                        metadata={
                            "lsl_timestamps": timestamps,
                            "stream_name": (
                                self.stream_info.name() if self.stream_info else None
                            ),
                        },
                    )

                    if self._data_callback:
                        self._data_callback(packet)

                # Small sleep to prevent busy waiting
                await asyncio.sleep(0.001)

        except Exception as e:
            self._handle_error(e)

    def get_capabilities(self) -> DeviceCapabilities:
        """Get device capabilities."""
        # LSL streams can have varying capabilities
        return DeviceCapabilities(
            supported_sampling_rates=(
                [self.sampling_rate] if self.sampling_rate else [256.0]
            ),
            max_channels=self.n_channels if self.n_channels else 64,
            signal_types=[self.signal_type],
            has_impedance_check=False,
            has_battery_monitor=False,
            has_wireless=True,  # LSL is network - based
            has_trigger_input=True,  # LSL supports markers
            has_aux_channels=True,  # Depends on stream
        )

    def configure_channels(self, channels: List[ChannelInfo]) -> bool:
        """Configure channels - not supported for LSL streams."""
        logger.warning("Channel configuration not supported for LSL streams")
        return False

    def set_sampling_rate(self, rate: float) -> bool:
        """Set sampling rate - not supported for LSL streams."""
        logger.warning("Sampling rate configuration not supported for LSL streams")
        return False

    async def get_available_streams(self) -> List[Dict[str, Any]]:
        """Get list of available LSL streams."""
        loop = asyncio.get_event_loop()
        streams = await loop.run_in_executor(
            None, lambda: resolve_stream(timeout=self.timeout)
        )

        stream_list = []
        for stream in streams:
            stream_list.append(
                {
                    "name": stream.name(),
                    "type": stream.type(),
                    "channels": stream.channel_count(),
                    "sampling_rate": stream.nominal_srate(),
                    "hostname": stream.hostname(),
                    "uid": stream.uid(),
                }
            )

        return stream_list
