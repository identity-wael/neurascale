"""Synthetic device implementation for testing and development."""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timezone
import numpy as np

from ..interfaces.base_device import BaseDevice, DeviceState, DeviceCapabilities
from ...ingestion.data_types import (
    NeuralDataPacket,
    DeviceInfo,
    ChannelInfo,
    NeuralSignalType,
    DataSource,
)

logger = logging.getLogger(__name__)


class SyntheticDevice(BaseDevice):
    """Synthetic device that generates realistic neural signals for testing."""

    # Default signal parameters
    DEFAULT_CONFIGS = {
        NeuralSignalType.EEG: {
            "n_channels": 8,
            "sampling_rate": 256.0,
            "bands": {
                "delta": (0.5, 4, 20),  # (min_freq, max_freq, amplitude)
                "theta": (4, 8, 15),
                "alpha": (8, 13, 30),
                "beta": (13, 30, 10),
                "gamma": (30, 100, 5),
            },
            "noise_level": 5.0,
            "artifact_probability": 0.01,
        },
        NeuralSignalType.EMG: {
            "n_channels": 4,
            "sampling_rate": 1000.0,
            "base_frequency": 50.0,
            "burst_probability": 0.1,
            "burst_duration": 0.5,
            "noise_level": 10.0,
        },
        NeuralSignalType.SPIKES: {
            "n_channels": 32,
            "sampling_rate": 30000.0,
            "firing_rate": 10.0,  # Hz
            "spike_amplitude": 100.0,
            "noise_level": 5.0,
        },
        NeuralSignalType.ACCELEROMETER: {
            "n_channels": 3,
            "sampling_rate": 100.0,
            "movement_frequency": 1.0,
            "noise_level": 0.01,
        },
    }

    def __init__(
        self,
        signal_type: NeuralSignalType = NeuralSignalType.EEG,
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize synthetic device.

        Args:
            signal_type: Type of signal to generate
            config: Custom configuration overriding defaults
        """
        device_id = f"synthetic_{signal_type.value}"
        device_name = f"Synthetic {signal_type.value.upper()}"

        super().__init__(device_id, device_name)

        self.signal_type = signal_type

        # Merge default config with custom config
        default_config = self.DEFAULT_CONFIGS.get(
            signal_type, self.DEFAULT_CONFIGS[NeuralSignalType.EEG]
        )
        self.config: Dict[str, Any] = (
            dict(default_config) if isinstance(default_config, dict) else {}
        )
        if config:
            self.config.update(config)

        self.n_channels: int = self.config["n_channels"]
        self.sampling_rate: float = self.config["sampling_rate"]

        # State for signal generation
        self.time_offset = 0.0
        self.spike_times: Dict[int, List[float]] = {
            i: [] for i in range(self.n_channels)
        }
        self.emg_burst_state: Dict[int, bool] = {
            i: False for i in range(self.n_channels)
        }
        self.emg_burst_start: Dict[int, float] = {
            i: 0.0 for i in range(self.n_channels)
        }

    async def connect(self, **kwargs: Any) -> bool:
        """Connect to synthetic device (always succeeds)."""
        try:
            self._update_state(DeviceState.CONNECTING)

            # Simulate connection delay
            await asyncio.sleep(0.5)

            # Create channel info
            channels = []
            for i in range(self.n_channels):
                unit = "microvolts"
                if self.signal_type == NeuralSignalType.ACCELEROMETER:
                    unit = "g"
                    labels = ["X", "Y", "Z"]
                    label = f"Accel_{labels[i % 3]}"
                else:
                    label = f"Ch{i + 1}"

                channels.append(
                    ChannelInfo(
                        channel_id=i,
                        label=label,
                        unit=unit,
                        sampling_rate=self.sampling_rate,
                    )
                )

            # Create device info
            self.device_info = DeviceInfo(
                device_id=self.device_id,
                device_type="Synthetic",
                manufacturer="NeuraScale",
                model=f"Synthetic_{self.signal_type.value}",
                firmware_version="1.0.0",
                channels=channels,
            )

            self._update_state(DeviceState.CONNECTED)
            logger.info(
                f"Connected to {self.device_name} "
                f"({self.n_channels} channels @ {self.sampling_rate}Hz)"
            )
            return True

        except Exception as e:
            self._handle_error(e)
            return False

    async def disconnect(self) -> None:
        """Disconnect from synthetic device."""
        self._update_state(DeviceState.DISCONNECTED)
        logger.info("Disconnected from synthetic device")

    async def start_streaming(self) -> None:
        """Start streaming synthetic data."""
        if not self.is_connected():
            raise RuntimeError("Device not connected")

        if self.is_streaming():
            logger.warning("Already streaming")
            return

        self._stop_streaming.clear()
        self._update_state(DeviceState.STREAMING)

        # Reset time offset
        self.time_offset = 0.0

        # Start streaming task
        self._streaming_task = asyncio.create_task(self._streaming_loop())

    async def stop_streaming(self) -> None:
        """Stop streaming synthetic data."""
        if not self.is_streaming():
            return

        self._stop_streaming.set()

        if self._streaming_task:
            await self._streaming_task
            self._streaming_task = None

        self._update_state(DeviceState.CONNECTED)

    async def _streaming_loop(self) -> None:
        """Main streaming loop for synthetic data."""
        chunk_duration = 0.05  # 50ms chunks
        chunk_samples = int(self.sampling_rate * chunk_duration)

        try:
            while not self._stop_streaming.is_set():
                # Generate synthetic data based on signal type
                if self.signal_type == NeuralSignalType.EEG:
                    data = self._generate_eeg_data(chunk_samples)
                elif self.signal_type == NeuralSignalType.EMG:
                    data = self._generate_emg_data(chunk_samples)
                elif self.signal_type == NeuralSignalType.SPIKES:
                    data = self._generate_spike_data(chunk_samples)
                elif self.signal_type == NeuralSignalType.ACCELEROMETER:
                    data = self._generate_accelerometer_data(chunk_samples)
                else:
                    data = self._generate_random_data(chunk_samples)

                # Create and send packet
                packet = self._create_packet(
                    data=data,
                    timestamp=datetime.now(timezone.utc),
                    signal_type=self.signal_type,
                    source=DataSource.SYNTHETIC,
                    metadata={"synthetic": True, "time_offset": self.time_offset},
                )

                if self._data_callback:
                    self._data_callback(packet)

                # Update time offset
                self.time_offset += chunk_duration

                # Sleep to maintain real - time streaming
                await asyncio.sleep(chunk_duration)

        except Exception as e:
            self._handle_error(e)

    def _generate_eeg_data(self, n_samples: int) -> np.ndarray:
        """Generate realistic EEG data with frequency bands."""
        t = np.linspace(
            self.time_offset,
            self.time_offset + n_samples / self.sampling_rate,
            n_samples,
        )
        data = np.zeros((self.n_channels, n_samples))

        for ch in range(self.n_channels):
            # Add frequency band components
            for band_name, (min_freq, max_freq, amplitude) in self.config[
                "bands"
            ].items():
                # Random frequency within band
                freq = np.random.uniform(min_freq, max_freq)
                phase = np.random.uniform(0, 2 * np.pi)

                # Add some amplitude variation
                amp_variation = 1 + 0.2 * np.sin(2 * np.pi * 0.1 * t)
                data[ch] += (
                    amplitude * amp_variation * np.sin(2 * np.pi * freq * t + phase)
                )

            # Add pink noise (1 / f)
            noise = self._generate_pink_noise(n_samples) * self.config["noise_level"]
            data[ch] += noise

            # Add occasional artifacts
            if np.random.random() < self.config["artifact_probability"]:
                artifact_start = np.random.randint(0, n_samples - 10)
                artifact_amplitude = np.random.uniform(50, 200)
                data[ch, artifact_start : artifact_start + 10] += artifact_amplitude

        return data

    def _generate_emg_data(self, n_samples: int) -> np.ndarray:
        """Generate realistic EMG data with muscle activation bursts."""
        t = np.linspace(
            self.time_offset,
            self.time_offset + n_samples / self.sampling_rate,
            n_samples,
        )
        data = np.zeros((self.n_channels, n_samples))

        for ch in range(self.n_channels):
            # Check for burst state
            if not self.emg_burst_state[ch]:
                # Potentially start a burst
                if (
                    np.random.random()
                    < self.config["burst_probability"] * n_samples / self.sampling_rate
                ):
                    self.emg_burst_state[ch] = True
                    self.emg_burst_start[ch] = self.time_offset
            else:
                # Check if burst should end
                burst_duration = self.time_offset - self.emg_burst_start[ch]
                if burst_duration > self.config["burst_duration"]:
                    self.emg_burst_state[ch] = False

            # Generate signal
            if self.emg_burst_state[ch]:
                # Active muscle signal
                base_freq = self.config["base_frequency"]
                for harmonic in range(1, 5):
                    freq = base_freq * harmonic
                    amplitude = 100 / harmonic  # Decreasing amplitude with harmonics
                    data[ch] += amplitude * np.sin(2 * np.pi * freq * t)

                # Add high - frequency components
                hf_noise = np.random.randn(n_samples) * 50
                data[ch] += hf_noise

            # Always add baseline noise
            data[ch] += np.random.randn(n_samples) * self.config["noise_level"]

        return data

    def _generate_spike_data(self, n_samples: int) -> np.ndarray:
        """Generate synthetic spike train data."""
        data = np.random.randn(self.n_channels, n_samples) * self.config["noise_level"]

        # Time array
        # t = np.arange(n_samples) / self.sampling_rate  # Unused for now

        for ch in range(self.n_channels):
            # Generate spikes based on Poisson process
            firing_rate = self.config["firing_rate"] * (
                1 + 0.5 * np.sin(2 * np.pi * 0.5 * self.time_offset)
            )

            # Check existing spike times and remove old ones
            self.spike_times[ch] = [
                st for st in self.spike_times[ch] if st > self.time_offset - 0.1
            ]

            # Generate new spikes
            n_spikes = np.random.poisson(firing_rate * n_samples / self.sampling_rate)
            new_spike_times = np.sort(
                np.random.uniform(0, n_samples / self.sampling_rate, n_spikes)
            )

            # Add spikes to data
            for spike_time in new_spike_times:
                spike_idx = int(spike_time * self.sampling_rate)
                if spike_idx < n_samples:
                    # Simple spike waveform (2ms duration)
                    spike_duration = int(0.002 * self.sampling_rate)
                    spike_waveform = self._create_spike_waveform(spike_duration)

                    end_idx = min(spike_idx + spike_duration, n_samples)
                    waveform_end = end_idx - spike_idx
                    data[ch, spike_idx:end_idx] += (
                        spike_waveform[:waveform_end] * self.config["spike_amplitude"]
                    )

                # Store spike time for refractory period
                self.spike_times[ch].append(self.time_offset + spike_time)

        return data  # type: ignore[no - any - return]

    def _create_spike_waveform(self, duration: int) -> np.ndarray:
        """Create a realistic spike waveform."""
        t = np.linspace(0, 1, duration)
        # Biphasic spike shape
        waveform = np.exp(-10 * t) * np.sin(2 * np.pi * 5 * t)
        return waveform  # type: ignore[no - any - return]

    def _generate_accelerometer_data(self, n_samples: int) -> np.ndarray:
        """Generate synthetic accelerometer data."""
        t = np.linspace(
            self.time_offset,
            self.time_offset + n_samples / self.sampling_rate,
            n_samples,
        )
        data = np.zeros((self.n_channels, n_samples))

        # Simulate periodic movement
        movement_freq = self.config["movement_frequency"]

        # X - axis: forward - backward movement
        data[0] = 0.1 * np.sin(2 * np.pi * movement_freq * t)

        # Y - axis: side - to - side movement
        data[1] = 0.05 * np.sin(2 * np.pi * movement_freq * 2 * t + np.pi / 4)

        # Z - axis: up - down movement + gravity
        data[2] = 1.0 + 0.02 * np.sin(2 * np.pi * movement_freq * 4 * t)

        # Add noise to all channels
        for ch in range(self.n_channels):
            data[ch] += np.random.randn(n_samples) * self.config["noise_level"]

        return data

    def _generate_pink_noise(self, n_samples: int) -> np.ndarray:
        """Generate pink (1 / f) noise."""
        # Simple approximation using filtered white noise
        white = np.random.randn(n_samples)

        # Apply multiple first - order filters
        pink = np.zeros(n_samples)
        pink[0] = white[0]

        for i in range(1, n_samples):
            pink[i] = 0.99 * pink[i - 1] + white[i]

        # Normalize
        pink = pink / np.std(pink)
        return pink

    def _generate_random_data(self, n_samples: int) -> np.ndarray:
        """Generate random data for unknown signal types."""
        return np.random.randn(self.n_channels, n_samples) * 10

    def get_capabilities(self) -> DeviceCapabilities:
        """Get device capabilities."""
        return DeviceCapabilities(
            supported_sampling_rates=[
                125.0,
                250.0,
                256.0,
                500.0,
                512.0,
                1000.0,
                2000.0,
            ],
            max_channels=64,
            signal_types=list(self.DEFAULT_CONFIGS.keys()),
            has_impedance_check=True,
            has_battery_monitor=True,
            has_wireless=True,
            has_trigger_input=True,
            has_aux_channels=True,
            supported_gains=[1, 2, 4, 8, 12, 24],
            supported_filters={
                "notch": [50, 60],
                "highpass": [0.1, 0.5, 1.0],
                "lowpass": [30, 50, 100],
            },
        )

    def configure_channels(self, channels: List[ChannelInfo]) -> bool:
        """Configure channels for synthetic device."""
        self.n_channels = len(channels)
        # Update device info channels
        if self.device_info:
            self.device_info.channels = channels
        return True

    def set_sampling_rate(self, rate: float) -> bool:
        """Set sampling rate for synthetic device."""
        self.sampling_rate = rate
        self.config["sampling_rate"] = rate
        # Update channel sampling rates
        if self.device_info and self.device_info.channels:
            for channel in self.device_info.channels:
                channel.sampling_rate = rate
        return True

    async def check_impedance(
        self, channel_ids: Optional[List[int]] = None
    ) -> Dict[int, float]:
        """Simulate impedance check."""
        await asyncio.sleep(0.5)  # Simulate measurement time

        if channel_ids is None:
            channel_ids = list(range(self.n_channels))

        # Generate realistic impedance values
        impedances = {}
        for ch_id in channel_ids:
            # Most channels have good impedance
            if np.random.random() < 0.8:
                impedance = np.random.uniform(1000, 5000)  # 1 - 5 kΩ
            else:
                # Some channels have higher impedance
                impedance = np.random.uniform(5000, 20000)  # 5 - 20 kΩ
            impedances[ch_id] = impedance

        return impedances

    async def get_battery_level(self) -> float:
        """Simulate battery level."""
        # Decrease over time
        hours_running = self.time_offset / 3600
        battery = max(0, 100 - hours_running * 10)  # 10% per hour
        return battery
