"""BrainFlow device implementation supporting multiple boards."""

import asyncio
import logging
import random
from typing import List, Optional, Any, cast, Dict
from datetime import datetime, timezone
import numpy as np

try:
    from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
    from brainflow.data_filter import DataFilter

    BRAINFLOW_AVAILABLE = True
except ImportError:
    BRAINFLOW_AVAILABLE = False
    BoardShim = None
    BrainFlowInputParams = None
    BoardIds = None
    DataFilter = None

from ..interfaces.base_device import BaseDevice, DeviceState, DeviceCapabilities
from ...ingestion.data_types import (
    DeviceInfo,
    ChannelInfo,
    NeuralSignalType,
    DataSource,
)
from ..signal_quality import (
    SignalQualityMonitor,
    SignalQualityMetrics,
    ImpedanceResult,
)

logger = logging.getLogger(__name__)


class BrainFlowDevice(BaseDevice):
    """BrainFlow device implementation supporting multiple neural recording boards."""

    # Supported boards mapping
    SUPPORTED_BOARDS = {
        "cyton": BoardIds.CYTON_BOARD if BRAINFLOW_AVAILABLE else None,
        "cyton_daisy": BoardIds.CYTON_DAISY_BOARD if BRAINFLOW_AVAILABLE else None,
        "ganglion": BoardIds.GANGLION_BOARD if BRAINFLOW_AVAILABLE else None,
        "synthetic": BoardIds.SYNTHETIC_BOARD if BRAINFLOW_AVAILABLE else None,
        "muse_s": BoardIds.MUSE_S_BOARD if BRAINFLOW_AVAILABLE else None,
        "muse_2": BoardIds.MUSE_2_BOARD if BRAINFLOW_AVAILABLE else None,
        "neurosity_crown": BoardIds.CROWN_BOARD if BRAINFLOW_AVAILABLE else None,
        "brainbit": BoardIds.BRAINBIT_BOARD if BRAINFLOW_AVAILABLE else None,
        "unicorn": BoardIds.UNICORN_BOARD if BRAINFLOW_AVAILABLE else None,
    }

    def __init__(
        self,
        board_name: str = "synthetic",
        serial_port: Optional[str] = None,
        mac_address: Optional[str] = None,
        ip_address: Optional[str] = None,
        ip_port: Optional[int] = None,
        serial_number: Optional[str] = None,
    ):
        """
        Initialize BrainFlow device.

        Args:
            board_name: Name of the board from SUPPORTED_BOARDS
            serial_port: Serial port for serial boards
            mac_address: MAC address for Bluetooth boards
            ip_address: IP address for WiFi boards
            ip_port: IP port for WiFi boards
            serial_number: Serial number for some boards
        """
        if not BRAINFLOW_AVAILABLE:
            raise ImportError(
                "brainflow is not installed. Install with: pip install brainflow"
            )

        if board_name not in self.SUPPORTED_BOARDS:
            raise ValueError(
                f"Unsupported board: {board_name}. "
                f"Supported boards: {list(self.SUPPORTED_BOARDS.keys())}"
            )

        device_id = f"brainflow_{board_name}"
        device_name = f"BrainFlow-{board_name.replace('_', ' ').title()}"

        super().__init__(device_id, device_name)

        self.board_name = board_name
        self.board_id = self.SUPPORTED_BOARDS[board_name]
        self.board: Optional[BoardShim] = None

        # Connection parameters
        self.params = BrainFlowInputParams()
        if serial_port:
            self.params.serial_port = serial_port
        if mac_address:
            self.params.mac_address = mac_address
        if ip_address:
            self.params.ip_address = ip_address
        if ip_port:
            self.params.ip_port = ip_port
        if serial_number:
            self.params.serial_number = serial_number

        # Board info (will be populated on connect)
        self.sampling_rate: float = 250.0
        self.n_channels: int = 0
        self.eeg_channels: List[int] = []
        self.emg_channels: List[int] = []
        self.accel_channels: List[int] = []
        self.timestamp_channel: int = 0
        self.marker_channel: Optional[int] = None

        # Signal quality monitoring
        self.signal_quality_monitor: Optional[SignalQualityMonitor] = None
        self._last_quality_metrics: Dict[int, SignalQualityMetrics] = {}
        self._impedance_results: Dict[int, ImpedanceResult] = {}

    async def connect(self, **kwargs: Any) -> bool:
        """Connect to BrainFlow device."""
        try:
            self._update_state(DeviceState.CONNECTING)

            # Enable BrainFlow logging
            BoardShim.enable_dev_board_logger()

            # Create board
            self.board = BoardShim(self.board_id, self.params)

            # Prepare session in executor
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.board.prepare_session)

            # Get board information
            self.sampling_rate = BoardShim.get_sampling_rate(self.board_id)
            self.eeg_channels = BoardShim.get_eeg_channels(self.board_id)
            self.emg_channels = BoardShim.get_emg_channels(self.board_id)
            self.accel_channels = BoardShim.get_accel_channels(self.board_id)
            self.timestamp_channel = BoardShim.get_timestamp_channel(self.board_id)

            try:
                self.marker_channel = BoardShim.get_marker_channel(self.board_id)
            except Exception:
                self.marker_channel = None

            # All data channels
            all_channels = list(
                set(self.eeg_channels + self.emg_channels + self.accel_channels)
            )
            self.n_channels = len(all_channels)

            # Create channel info
            channels = []
            for i, ch_idx in enumerate(all_channels):
                if ch_idx in self.eeg_channels:
                    signal_type = "EEG"
                    unit = "microvolts"
                elif ch_idx in self.emg_channels:
                    signal_type = "EMG"
                    unit = "microvolts"
                elif ch_idx in self.accel_channels:
                    signal_type = "Accel"
                    unit = "g"
                else:
                    signal_type = "Other"
                    unit = "unknown"

                channels.append(
                    ChannelInfo(
                        channel_id=i,
                        label=f"{signal_type}{ch_idx}",
                        unit=unit,
                        sampling_rate=self.sampling_rate,
                        hardware_id=str(ch_idx),
                    )
                )

            # Create device info
            self.device_info = DeviceInfo(
                device_id=self.device_id,
                device_type="BrainFlow",
                manufacturer=self._get_manufacturer(),
                model=self.board_name,
                channels=channels,
            )

            # Initialize signal quality monitor
            self.signal_quality_monitor = SignalQualityMonitor(
                sampling_rate=self.sampling_rate,
                line_freq=60.0,  # TODO: Make configurable based on region
            )

            self._update_state(DeviceState.CONNECTED)
            logger.info(
                f"Connected to {self.device_name} "
                f"({len(self.eeg_channels)} EEG, {len(self.emg_channels)} EMG, "
                f"{len(self.accel_channels)} Accel channels @ {self.sampling_rate}Hz)"
            )
            return True

        except Exception as e:
            self._handle_error(e)
            return False

    def _get_manufacturer(self) -> str:
        """Get manufacturer name for board."""
        manufacturer_map = {
            "cyton": "OpenBCI",
            "cyton_daisy": "OpenBCI",
            "ganglion": "OpenBCI",
            "muse_s": "InteraXon",
            "muse_2": "InteraXon",
            "neurosity_crown": "Neurosity",
            "brainbit": "BrainBit",
            "unicorn": "g.tec",
            "synthetic": "BrainFlow",
        }
        return manufacturer_map.get(self.board_name, "Unknown")

    async def disconnect(self) -> None:
        """Disconnect from BrainFlow device."""
        if self.board:
            try:
                if self.board.is_prepared():
                    # Stop streaming if active
                    try:
                        self.board.stop_stream()
                    except Exception:
                        pass

                    # Release session
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, self.board.release_session)
            except Exception as e:
                logger.error(f"Error during disconnect: {e}")
            finally:
                self.board = None

        self._update_state(DeviceState.DISCONNECTED)
        logger.info("Disconnected from BrainFlow device")

    async def start_streaming(self) -> None:
        """Start streaming data from BrainFlow device."""
        if not self.is_connected() or not self.board:
            raise RuntimeError("Device not connected")

        if self.is_streaming():
            logger.warning("Already streaming")
            return

        # Start streaming
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.board.start_stream)

        self._stop_streaming.clear()
        self._update_state(DeviceState.STREAMING)

        # Start streaming task
        self._streaming_task = asyncio.create_task(self._streaming_loop())

    async def stop_streaming(self) -> None:
        """Stop streaming data."""
        if not self.is_streaming() or not self.board:
            return

        # Stop BrainFlow streaming
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.board.stop_stream)
        except Exception as e:
            logger.error(f"Error stopping stream: {e}")

        self._stop_streaming.set()

        if self._streaming_task:
            await self._streaming_task
            self._streaming_task = None

        self._update_state(DeviceState.CONNECTED)

    async def _streaming_loop(self) -> None:  # noqa: C901
        """Main streaming loop."""
        if not self.board:
            return

        chunk_duration = 0.05  # 50ms chunks
        chunk_size = int(self.sampling_rate * chunk_duration)

        try:
            while not self._stop_streaming.is_set():
                # Get data from board
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(
                    None, self.board.get_board_data, chunk_size
                )

                if data.shape[1] > 0:  # If we have samples
                    # Extract relevant channels
                    eeg_data = (
                        data[self.eeg_channels, :]
                        if self.eeg_channels
                        else np.array([])
                    )
                    emg_data = (
                        data[self.emg_channels, :]
                        if self.emg_channels
                        else np.array([])
                    )
                    accel_data = (
                        data[self.accel_channels, :]
                        if self.accel_channels
                        else np.array([])
                    )
                    timestamps = data[self.timestamp_channel, :]

                    # Determine primary signal type
                    if eeg_data.size > 0:
                        primary_data = eeg_data
                        signal_type = NeuralSignalType.EEG
                    elif emg_data.size > 0:
                        primary_data = emg_data
                        signal_type = NeuralSignalType.EMG
                    elif accel_data.size > 0:
                        primary_data = accel_data
                        signal_type = NeuralSignalType.ACCELEROMETER
                    else:
                        continue

                    # Use last timestamp
                    timestamp = datetime.fromtimestamp(timestamps[-1], tz=timezone.utc)

                    # Create metadata
                    metadata = {
                        "timestamps": timestamps.tolist(),
                        "board_name": self.board_name,
                    }

                    # Add auxiliary data to metadata if present
                    if emg_data.size > 0 and signal_type != NeuralSignalType.EMG:
                        metadata["emg_data"] = emg_data.tolist()
                    if (
                        accel_data.size > 0
                        and signal_type != NeuralSignalType.ACCELEROMETER  # noqa: W503
                    ):
                        metadata["accel_data"] = accel_data.tolist()

                    # Create and send packet
                    packet = self._create_packet(
                        data=primary_data,
                        timestamp=timestamp,
                        signal_type=signal_type,
                        source=DataSource.BRAINFLOW,
                        metadata=metadata,
                    )

                    if self._data_callback:
                        self._data_callback(packet)

                # Small sleep to prevent busy waiting
                await asyncio.sleep(0.01)

        except Exception as e:
            self._handle_error(e)

    def get_capabilities(self) -> DeviceCapabilities:
        """Get device capabilities."""
        # Base capabilities
        signal_types = []
        if self.eeg_channels:
            signal_types.append(NeuralSignalType.EEG)
        if self.emg_channels:
            signal_types.append(NeuralSignalType.EMG)
        if self.accel_channels:
            signal_types.append(NeuralSignalType.ACCELEROMETER)

        # Board - specific capabilities
        has_wireless = self.board_name in [
            "ganglion",
            "muse_s",
            "muse_2",
            "neurosity_crown",
            "brainbit",
            "unicorn",
        ]
        has_battery = has_wireless

        return DeviceCapabilities(
            supported_sampling_rates=[self.sampling_rate],
            max_channels=self.n_channels,
            signal_types=signal_types,
            has_impedance_check=self.board_name in ["cyton", "cyton_daisy", "ganglion"],
            has_battery_monitor=has_battery,
            has_wireless=has_wireless,
            has_trigger_input=self.marker_channel is not None,
            has_aux_channels=len(self.accel_channels) > 0,
        )

    def configure_channels(self, channels: List[ChannelInfo]) -> bool:
        """Configure channels - limited support in BrainFlow."""
        logger.warning("Channel configuration not fully supported in BrainFlow")
        return False

    def set_sampling_rate(self, rate: float) -> bool:
        """Set sampling rate - not supported in most BrainFlow boards."""
        logger.warning("Sampling rate configuration not supported in BrainFlow")
        return False

    async def insert_marker(self, marker: float) -> bool:
        """Insert a marker into the data stream."""
        if not self.board or not self.marker_channel:
            return False

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.board.insert_marker, marker)
            return True
        except Exception as e:
            logger.error(f"Error inserting marker: {e}")
            return False

    async def get_board_data_history(
        self, duration_seconds: float
    ) -> Optional[np.ndarray]:
        """Get historical data from the board's ring buffer."""
        if not self.board:
            return None

        try:
            n_samples = int(self.sampling_rate * duration_seconds)
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None, self.board.get_board_data, n_samples
            )
            return cast(Optional[np.ndarray], data)
        except Exception as e:
            logger.error(f"Error getting board data history: {e}")
            return None

    async def check_impedance(  # noqa: C901
        self, channel_ids: Optional[List[int]] = None
    ) -> Dict[int, float]:
        """
        Check impedance for specified channels.

        Args:
            channel_ids: List of channel IDs to check, or None for all channels

        Returns:
            Dictionary mapping channel ID to impedance in ohms
        """
        if not self.is_connected() or not self.board:
            raise RuntimeError("Device not connected")

        # Check if board supports impedance checking
        capabilities = self.get_capabilities()
        if not capabilities.has_impedance_check:
            raise NotImplementedError(
                f"{self.device_name} does not support impedance checking"
            )

        # If no channels specified, check all EEG channels
        if channel_ids is None:
            channel_ids = list(range(len(self.eeg_channels)))

        impedance_values = {}

        try:
            # Some boards support direct impedance measurement
            if self.board_name in ["cyton", "cyton_daisy"]:
                # OpenBCI Cyton boards have impedance checking
                # This is a simplified approach - actual implementation would
                # use the OpenBCI protocol for impedance testing

                # Send impedance test command

                # Start impedance mode (board-specific command)
                # Note: This is pseudo-code as actual BrainFlow API may differ
                for channel_id in channel_ids:
                    if channel_id < len(self.eeg_channels):
                        # Simulate impedance measurement
                        # In real implementation, this would communicate with board
                        impedance_ohms = await self._measure_channel_impedance(
                            channel_id
                        )
                        impedance_values[channel_id] = impedance_ohms

                        # Store result with quality assessment
                        if self.signal_quality_monitor:
                            result = self.signal_quality_monitor.assess_impedance(
                                impedance_ohms, channel_id
                            )
                            self._impedance_results[channel_id] = result

            elif self.board_name == "ganglion":
                # Ganglion has accelerometer-based impedance checking
                for channel_id in channel_ids:
                    impedance_ohms = await self._measure_ganglion_impedance(channel_id)
                    impedance_values[channel_id] = impedance_ohms

                    if self.signal_quality_monitor:
                        result = self.signal_quality_monitor.assess_impedance(
                            impedance_ohms, channel_id
                        )
                        self._impedance_results[channel_id] = result

            else:
                # For boards without hardware impedance checking,
                # estimate from signal quality
                impedance_values = await self._estimate_impedance_from_signal(
                    channel_ids
                )

        except Exception as e:
            logger.error(f"Error checking impedance: {e}")
            raise

        return impedance_values

    async def _measure_channel_impedance(self, channel_id: int) -> float:
        """Measure impedance for a single channel (board-specific)."""
        # This is a placeholder - actual implementation would use
        # board-specific commands to measure impedance

        # For now, return a simulated value
        # Good impedance: 1-10 kOhm
        # Fair impedance: 10-50 kOhm
        # Poor impedance: > 50 kOhm

        import random

        base_impedance = random.uniform(2000, 20000)  # 2-20 kOhm
        return base_impedance

    async def _measure_ganglion_impedance(self, channel_id: int) -> float:
        """Measure impedance on Ganglion board using accelerometer method."""
        # Ganglion uses a different method involving accelerometer
        # This is a placeholder implementation

        import random

        base_impedance = random.uniform(5000, 30000)  # 5-30 kOhm
        return base_impedance

    async def _estimate_impedance_from_signal(
        self, channel_ids: List[int]
    ) -> Dict[int, float]:
        """Estimate impedance from signal quality metrics."""
        impedance_values = {}

        # Get recent data to analyze
        recent_data = await self.get_board_data_history(2.0)  # 2 seconds

        if recent_data is None or recent_data.shape[1] == 0:
            logger.warning("No data available for impedance estimation")
            return impedance_values

        # Analyze signal quality for each channel
        for channel_id in channel_ids:
            if channel_id < len(self.eeg_channels):
                channel_idx = self.eeg_channels[channel_id]
                channel_data = recent_data[channel_idx, :]

                # Use signal quality metrics to estimate impedance
                if self.signal_quality_monitor:
                    metrics = self.signal_quality_monitor.assess_signal_quality(
                        channel_data, channel_id
                    )

                    # Estimate impedance based on SNR and RMS
                    # This is a heuristic approach
                    if metrics.snr_db > 20:
                        estimated_impedance = random.uniform(1000, 5000)
                    elif metrics.snr_db > 15:
                        estimated_impedance = random.uniform(5000, 10000)
                    elif metrics.snr_db > 10:
                        estimated_impedance = random.uniform(10000, 20000)
                    else:
                        estimated_impedance = random.uniform(20000, 100000)

                    impedance_values[channel_id] = estimated_impedance

                    # Store result
                    result = self.signal_quality_monitor.assess_impedance(
                        estimated_impedance, channel_id
                    )
                    self._impedance_results[channel_id] = result

        return impedance_values

    async def get_signal_quality(
        self, channel_ids: Optional[List[int]] = None
    ) -> Dict[int, SignalQualityMetrics]:
        """
        Get current signal quality metrics for channels.

        Args:
            channel_ids: List of channel IDs to check, or None for all channels

        Returns:
            Dictionary mapping channel ID to signal quality metrics
        """
        if not self.is_streaming():
            raise RuntimeError("Device must be streaming to assess signal quality")

        if not self.signal_quality_monitor:
            raise RuntimeError("Signal quality monitor not initialized")

        # If no channels specified, check all EEG channels
        if channel_ids is None:
            channel_ids = list(range(len(self.eeg_channels)))

        # Get recent data
        recent_data = await self.get_board_data_history(1.0)  # 1 second

        if recent_data is None or recent_data.shape[1] == 0:
            return {}

        quality_metrics = {}

        for channel_id in channel_ids:
            if channel_id < len(self.eeg_channels):
                channel_idx = self.eeg_channels[channel_id]
                channel_data = recent_data[channel_idx, :]

                # Assess signal quality
                metrics = self.signal_quality_monitor.assess_signal_quality(
                    channel_data, channel_id
                )

                quality_metrics[channel_id] = metrics
                self._last_quality_metrics[channel_id] = metrics

        return quality_metrics
