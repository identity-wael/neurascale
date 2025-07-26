"""Synthetic Adapter for NeuraScale Neural Engine.

This adapter provides synthetic data generation for testing and simulation
of BCI devices without requiring actual hardware.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
import numpy as np

import random

from ..base import (
    BaseDevice,
    DeviceInfo,
    DeviceType,
    DeviceStatus,
    ConnectionType,
    SignalQuality,
    DataSample,
    DeviceEvent,
)

logger = logging.getLogger(__name__)


class SyntheticSignalType:
    """Types of synthetic signals that can be generated."""

    SINE_WAVE = "sine_wave"
    ALPHA_WAVE = "alpha_wave"  # 8-13 Hz
    BETA_WAVE = "beta_wave"  # 13-30 Hz
    THETA_WAVE = "theta_wave"  # 4-8 Hz
    DELTA_WAVE = "delta_wave"  # 0.5-4 Hz
    NOISE = "noise"
    ERP = "erp"  # Event-Related Potential
    SSVEP = "ssvep"  # Steady-State Visual Evoked Potential
    REALISTIC_EEG = "realistic_eeg"


class SyntheticAdapter(BaseDevice):
    """Synthetic device adapter for testing and simulation."""

    def __init__(self, device_info: DeviceInfo):
        """Initialize synthetic adapter.

        Args:
            device_info: Device information
        """
        super().__init__(device_info)

        # Synthetic signal configuration
        self.signal_type = device_info.connection_params.get(
            "signal_type", SyntheticSignalType.REALISTIC_EEG
        )
        self.amplitude = device_info.connection_params.get(
            "amplitude", 50.0
        )  # microvolts
        self.noise_level = device_info.connection_params.get(
            "noise_level", 5.0
        )  # microvolts
        self.frequency = device_info.connection_params.get("frequency", 10.0)  # Hz

        # Simulation parameters
        self.simulate_artifacts = device_info.connection_params.get(
            "simulate_artifacts", True
        )
        self.artifact_probability = device_info.connection_params.get(
            "artifact_probability", 0.01
        )
        self.simulate_impedance_changes = device_info.connection_params.get(
            "simulate_impedance", True
        )
        self.simulate_connection_issues = device_info.connection_params.get(
            "simulate_issues", False
        )

        # Data generation state
        self.sample_counter = 0
        self.time_offset = 0.0
        self.streaming_task: Optional[asyncio.Task] = None

        # Signal generators
        self.channel_phases = np.random.random(device_info.channel_count) * 2 * np.pi
        self.channel_frequencies = self._generate_channel_frequencies()
        self.channel_amplitudes = self._generate_channel_amplitudes()

        # Impedance simulation
        self.impedance_values = self._generate_initial_impedance()
        self.impedance_update_counter = 0

        # Performance simulation
        self.connection_stability = 1.0
        self.packet_loss_counter = 0

        logger.info(
            f"SyntheticAdapter initialized with signal type: {self.signal_type}"
        )

    async def connect(self) -> bool:
        """Simulate device connection."""
        try:
            await self.update_status(DeviceStatus.CONNECTING)

            # Simulate connection delay
            await asyncio.sleep(0.1 + random.random() * 0.2)

            # Simulate occasional connection failures
            if self.simulate_connection_issues and random.random() < 0.1:
                logger.warning("Simulated connection failure")
                await self.update_status(DeviceStatus.ERROR)
                return False

            self.is_connected = True
            await self.update_status(DeviceStatus.CONNECTED)

            # Initialize device info
            self.device_info.last_seen = datetime.utcnow()
            self.device_info.connection_type = ConnectionType.SYNTHETIC

            self._emit_event(
                "synthetic_connected",
                {
                    "signal_type": self.signal_type,
                    "channels": self.device_info.channel_count,
                },
            )

            logger.info("Synthetic device connected")
            return True

        except Exception as e:
            logger.error(f"Error connecting synthetic device: {str(e)}")
            await self.update_status(DeviceStatus.ERROR)
            return False

    async def disconnect(self) -> bool:
        """Simulate device disconnection."""
        try:
            if self.is_streaming:
                await self.stop_streaming()

            self.is_connected = False
            await self.update_status(DeviceStatus.DISCONNECTED)

            self._emit_event("synthetic_disconnected")
            logger.info("Synthetic device disconnected")
            return True

        except Exception as e:
            logger.error(f"Error disconnecting synthetic device: {str(e)}")
            return False

    async def start_streaming(self) -> bool:
        """Start synthetic data streaming."""
        if not self.is_connected:
            logger.error("Device not connected")
            return False

        try:
            self.is_streaming = True
            await self.update_status(DeviceStatus.STREAMING)

            # Start data generation task
            self.streaming_task = asyncio.create_task(self._data_generation_loop())

            self._emit_event(
                "synthetic_streaming_started",
                {
                    "sampling_rate": self.device_info.sampling_rate,
                    "signal_type": self.signal_type,
                },
            )

            logger.info("Started synthetic data streaming")
            return True

        except Exception as e:
            logger.error(f"Error starting synthetic streaming: {str(e)}")
            return False

    async def stop_streaming(self) -> bool:
        """Stop synthetic data streaming."""
        try:
            self.is_streaming = False

            if self.streaming_task and not self.streaming_task.done():
                self.streaming_task.cancel()
                try:
                    await self.streaming_task
                except asyncio.CancelledError:
                    pass

            await self.update_status(DeviceStatus.CONNECTED)

            self._emit_event("synthetic_streaming_stopped")
            logger.info("Stopped synthetic data streaming")
            return True

        except Exception as e:
            logger.error(f"Error stopping synthetic streaming: {str(e)}")
            return False

    async def configure(self, config: Dict[str, Any]) -> bool:
        """Configure synthetic adapter parameters.

        Args:
            config: Configuration parameters

        Returns:
            True if configuration successful
        """
        try:
            # Update signal parameters
            if "signal_type" in config:
                self.signal_type = config["signal_type"]
                self.device_info.connection_params["signal_type"] = self.signal_type

            if "amplitude" in config:
                self.amplitude = float(config["amplitude"])
                self.device_info.connection_params["amplitude"] = self.amplitude
                self.channel_amplitudes = self._generate_channel_amplitudes()

            if "noise_level" in config:
                self.noise_level = float(config["noise_level"])
                self.device_info.connection_params["noise_level"] = self.noise_level
                self.device_info.noise_level = self.noise_level

            if "frequency" in config:
                self.frequency = float(config["frequency"])
                self.device_info.connection_params["frequency"] = self.frequency
                self.channel_frequencies = self._generate_channel_frequencies()

            if "sampling_rate" in config:
                self.device_info.sampling_rate = float(config["sampling_rate"])

            # Update simulation parameters
            if "simulate_artifacts" in config:
                self.simulate_artifacts = bool(config["simulate_artifacts"])
                self.device_info.connection_params["simulate_artifacts"] = (
                    self.simulate_artifacts
                )

            if "artifact_probability" in config:
                self.artifact_probability = float(config["artifact_probability"])
                self.device_info.connection_params["artifact_probability"] = (
                    self.artifact_probability
                )

            if "simulate_impedance" in config:
                self.simulate_impedance_changes = bool(config["simulate_impedance"])
                self.device_info.connection_params["simulate_impedance"] = (
                    self.simulate_impedance_changes
                )

            if "simulate_issues" in config:
                self.simulate_connection_issues = bool(config["simulate_issues"])
                self.device_info.connection_params["simulate_issues"] = (
                    self.simulate_connection_issues
                )

            # Update device configuration
            self.device_info.configuration.update(config)

            self._emit_event("synthetic_configured", {"config": config})
            logger.info(f"Synthetic adapter configured: {config}")
            return True

        except Exception as e:
            logger.error(f"Error configuring synthetic adapter: {str(e)}")
            return False

    async def get_impedance(self) -> Dict[str, float]:
        """Get simulated electrode impedance values.

        Returns:
            Dictionary of channel impedance values in kOhms
        """
        # Update impedance values periodically
        if self.simulate_impedance_changes:
            self.impedance_update_counter += 1
            if self.impedance_update_counter % 100 == 0:  # Update every 100 calls
                self._update_impedance_values()

        # Convert to channel names
        impedance_dict = {}
        for i, impedance in enumerate(self.impedance_values):
            channel_name = f"Ch{i+1}"
            impedance_dict[channel_name] = impedance

        # Update device info
        self.device_info.impedance_values = impedance_dict

        return impedance_dict

    async def perform_self_test(self) -> Dict[str, Any]:
        """Perform synthetic device self-test.

        Returns:
            Test results and diagnostic information
        """
        test_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "test_passed": True,
            "tests": {},
        }

        try:
            # Test signal generation
            test_data = self._generate_sample_data()
            test_results["tests"]["signal_generation"] = {
                "passed": test_data is not None and test_data.size > 0,
                "message": "Signal generation functional",
                "data_shape": test_data.shape if test_data is not None else None,
            }

            # Test impedance measurement
            impedance = await self.get_impedance()
            test_results["tests"]["impedance_measurement"] = {
                "passed": len(impedance) == self.device_info.channel_count,
                "message": "Impedance measurement functional",
                "channels_measured": len(impedance),
            }

            # Test configuration
            test_config = {"amplitude": self.amplitude * 1.1}
            config_success = await self.configure(test_config)
            test_results["tests"]["configuration"] = {
                "passed": config_success,
                "message": (
                    "Configuration functional"
                    if config_success
                    else "Configuration failed"
                ),
            }

            # Restore original amplitude
            await self.configure({"amplitude": self.amplitude / 1.1})

            # Test connection status
            test_results["tests"]["connection_status"] = {
                "passed": self.is_connected,
                "message": f"Connection status: {'connected' if self.is_connected else 'disconnected'}",
            }

            # Test streaming status
            test_results["tests"]["streaming_status"] = {
                "passed": True,  # Always pass for synthetic
                "message": f"Streaming status: {'active' if self.is_streaming else 'stopped'}",
                "samples_generated": self.sample_counter,
            }

            # Signal quality assessment
            if test_data is not None:
                quality = await self.calculate_signal_quality(test_data)
                test_results["tests"]["signal_quality"] = {
                    "passed": quality != SignalQuality.UNUSABLE,
                    "message": f"Signal quality: {quality.value}",
                    "quality_level": quality.value,
                }

        except Exception as e:
            test_results["test_passed"] = False
            test_results["error"] = str(e)
            logger.error(f"Synthetic self-test error: {str(e)}")

        return test_results

    def _generate_channel_frequencies(self) -> np.ndarray:
        """Generate frequencies for each channel based on signal type."""
        base_freq = self.frequency

        if self.signal_type == SyntheticSignalType.ALPHA_WAVE:
            # Alpha waves: 8-13 Hz
            frequencies = np.random.uniform(8, 13, self.device_info.channel_count)
        elif self.signal_type == SyntheticSignalType.BETA_WAVE:
            # Beta waves: 13-30 Hz
            frequencies = np.random.uniform(13, 30, self.device_info.channel_count)
        elif self.signal_type == SyntheticSignalType.THETA_WAVE:
            # Theta waves: 4-8 Hz
            frequencies = np.random.uniform(4, 8, self.device_info.channel_count)
        elif self.signal_type == SyntheticSignalType.DELTA_WAVE:
            # Delta waves: 0.5-4 Hz
            frequencies = np.random.uniform(0.5, 4, self.device_info.channel_count)
        elif self.signal_type == SyntheticSignalType.REALISTIC_EEG:
            # Mix of frequencies typical in EEG
            frequencies = []
            for i in range(self.device_info.channel_count):
                # Weighted random selection of typical EEG frequencies
                freq_type = random.choices(
                    [8, 10, 12, 15, 20, 25],  # Alpha, mu, beta frequencies
                    weights=[0.3, 0.3, 0.2, 0.1, 0.07, 0.03],
                )[0]
                frequencies.append(freq_type + random.uniform(-1, 1))
            frequencies = np.array(frequencies)
        else:
            # Default: use base frequency with slight variations
            frequencies = base_freq + np.random.uniform(
                -1, 1, self.device_info.channel_count
            )

        return frequencies

    def _generate_channel_amplitudes(self) -> np.ndarray:
        """Generate amplitudes for each channel."""
        if self.signal_type == SyntheticSignalType.REALISTIC_EEG:
            # Realistic EEG amplitudes (10-100 µV typically)
            amplitudes = (
                np.random.uniform(0.5, 2.0, self.device_info.channel_count)
                * self.amplitude
            )
        else:
            # Uniform amplitudes with small variations
            amplitudes = self.amplitude * (
                0.8 + 0.4 * np.random.random(self.device_info.channel_count)
            )

        return amplitudes

    def _generate_initial_impedance(self) -> np.ndarray:
        """Generate initial impedance values for all channels."""
        # Typical electrode impedances: 5-50 kOhms
        impedances = np.random.uniform(5, 25, self.device_info.channel_count)

        # Occasionally simulate high impedance channels
        high_impedance_mask = np.random.random(self.device_info.channel_count) < 0.1
        impedances[high_impedance_mask] = np.random.uniform(
            40, 80, np.sum(high_impedance_mask)
        )

        return impedances

    def _update_impedance_values(self) -> None:
        """Update impedance values to simulate changes over time."""
        # Small random changes
        changes = np.random.normal(0, 1, self.device_info.channel_count)
        self.impedance_values += changes

        # Keep within reasonable bounds
        self.impedance_values = np.clip(self.impedance_values, 1, 100)

        # Occasionally simulate electrode displacement
        if random.random() < 0.01:  # 1% chance
            channel_idx = random.randint(0, self.device_info.channel_count - 1)
            self.impedance_values[channel_idx] = random.uniform(50, 100)
            logger.debug(
                f"Simulated electrode displacement on channel {channel_idx + 1}"
            )

    def _generate_sample_data(self) -> np.ndarray:
        """Generate a single sample of synthetic data."""
        current_time = self.sample_counter / self.device_info.sampling_rate
        data = np.zeros(self.device_info.channel_count)

        if self.signal_type == SyntheticSignalType.SINE_WAVE:
            # Simple sine wave
            for i in range(self.device_info.channel_count):
                data[i] = self.channel_amplitudes[i] * np.sin(
                    2 * np.pi * self.channel_frequencies[i] * current_time
                    + self.channel_phases[i]
                )

        elif self.signal_type == SyntheticSignalType.NOISE:
            # White noise
            data = np.random.normal(0, self.amplitude, self.device_info.channel_count)

        elif self.signal_type == SyntheticSignalType.ERP:
            # Event-Related Potential simulation
            # Simple P300-like response
            if self.sample_counter % int(self.device_info.sampling_rate * 2) < int(
                self.device_info.sampling_rate * 0.5
            ):
                # During ERP window
                erp_time = (
                    self.sample_counter % int(self.device_info.sampling_rate * 2)
                ) / self.device_info.sampling_rate
                if 0.3 <= erp_time <= 0.4:  # P300 peak around 300-400ms
                    p300_amplitude = (
                        self.amplitude * 2 * np.exp(-((erp_time - 0.35) ** 2) / 0.01)
                    )
                    data.fill(p300_amplitude)

        elif self.signal_type == SyntheticSignalType.SSVEP:
            # Steady-State Visual Evoked Potential
            # Strong response at stimulus frequency
            stimulus_freq = self.frequency
            for i in range(self.device_info.channel_count):
                # Stronger response in posterior channels (simulated)
                response_strength = (
                    1.5 if i >= self.device_info.channel_count // 2 else 0.5
                )
                data[i] = (
                    self.channel_amplitudes[i]
                    * response_strength
                    * np.sin(
                        2 * np.pi * stimulus_freq * current_time
                        + self.channel_phases[i]
                    )
                )

        elif self.signal_type == SyntheticSignalType.REALISTIC_EEG:
            # Realistic EEG simulation
            for i in range(self.device_info.channel_count):
                # Primary frequency component
                signal = self.channel_amplitudes[i] * np.sin(
                    2 * np.pi * self.channel_frequencies[i] * current_time
                    + self.channel_phases[i]
                )

                # Add harmonics
                signal += (
                    0.3
                    * self.channel_amplitudes[i]
                    * np.sin(
                        2 * np.pi * self.channel_frequencies[i] * 2 * current_time
                        + self.channel_phases[i] * 1.5
                    )
                )

                # Add 1 / f noise (pink noise approximation)
                low_freq_noise = (
                    0.2
                    * self.channel_amplitudes[i]
                    * np.sin(
                        2 * np.pi * (self.channel_frequencies[i] / 4) * current_time
                        + random.random() * 2 * np.pi
                    )
                )

                data[i] = signal + low_freq_noise

        else:
            # Default: mixed signal
            for i in range(self.device_info.channel_count):
                data[i] = self.channel_amplitudes[i] * np.sin(
                    2 * np.pi * self.channel_frequencies[i] * current_time
                    + self.channel_phases[i]
                )

        # Add noise
        noise = np.random.normal(0, self.noise_level, self.device_info.channel_count)
        data += noise

        # Simulate artifacts
        if self.simulate_artifacts and random.random() < self.artifact_probability:
            artifact_type = random.choice(["eye_blink", "muscle", "electrode_pop"])
            data = self._add_artifact(data, artifact_type)

        # Simulate packet loss
        if (
            self.simulate_connection_issues and random.random() < 0.001
        ):  # 0.1% packet loss
            self.packet_loss_counter += 1
            return None  # Dropped packet

        self.sample_counter += 1
        return data

    def _add_artifact(self, data: np.ndarray, artifact_type: str) -> np.ndarray:
        """Add simulated artifacts to the data.

        Args:
            data: Clean signal data
            artifact_type: Type of artifact to add

        Returns:
            Data with artifact added
        """
        if artifact_type == "eye_blink":
            # Eye blink affects frontal channels most
            frontal_channels = min(2, self.device_info.channel_count)
            artifact_amplitude = self.amplitude * 5  # Large amplitude
            data[:frontal_channels] += artifact_amplitude * np.exp(-random.random())

        elif artifact_type == "muscle":
            # Muscle artifact affects all channels with high frequency
            muscle_freq = random.uniform(30, 100)  # High frequency
            current_time = self.sample_counter / self.device_info.sampling_rate
            muscle_artifact = (
                self.amplitude * 2 * np.sin(2 * np.pi * muscle_freq * current_time)
            )
            data += muscle_artifact * (
                0.5 + 0.5 * np.random.random(self.device_info.channel_count)
            )

        elif artifact_type == "electrode_pop":
            # Sudden large spike on random channel
            affected_channel = random.randint(0, self.device_info.channel_count - 1)
            data[affected_channel] += random.choice([-1, 1]) * self.amplitude * 10

        return data

    async def _data_generation_loop(self) -> None:
        """Background task for continuous data generation."""
        logger.info("Starting synthetic data generation loop")

        target_interval = 1.0 / self.device_info.sampling_rate  # Seconds per sample

        while self.is_streaming:
            try:
                loop_start = asyncio.get_event_loop().time()

                # Generate sample data
                sample_data = self._generate_sample_data()

                if sample_data is not None:  # Not dropped due to packet loss
                    # Create data sample
                    data_sample = DataSample(
                        timestamp=datetime.utcnow().timestamp(),
                        channel_data=sample_data,
                        sample_number=self.sample_counter,
                        device_id=self.device_info.device_id,
                        sampling_rate=self.device_info.sampling_rate,
                        metadata={"signal_type": self.signal_type, "synthetic": True},
                    )

                    # Calculate signal quality
                    quality = await self.calculate_signal_quality(
                        sample_data.reshape(1, -1)
                    )
                    data_sample.signal_quality = {"overall": quality.value}

                    # Update device metrics
                    self.device_info.data_rate_hz = self.device_info.sampling_rate
                    self.device_info.last_seen = datetime.utcnow()
                    self.device_info.signal_quality = quality

                    # Emit data sample
                    self._emit_data(data_sample)

                # Calculate how long to wait for next sample
                loop_duration = asyncio.get_event_loop().time() - loop_start
                sleep_time = max(0, target_interval - loop_duration)

                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                elif loop_duration > target_interval * 2:
                    # Log if we're significantly behind
                    logger.warning(
                        f"Data generation loop behind schedule: {loop_duration:.4f}s"
                    )

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in synthetic data generation: {str(e)}")
                await asyncio.sleep(0.1)

        logger.info("Synthetic data generation loop stopped")

    @classmethod
    async def discover_devices(cls) -> List[DeviceInfo]:
        """Discover available synthetic devices.

        Returns:
            List of pre-configured synthetic device options
        """
        synthetic_devices = []

        # Define various synthetic device configurations
        device_configs = [
            {
                "name": "Synthetic EEG 8-Channel",
                "channels": 8,
                "sampling_rate": 250.0,
                "signal_type": SyntheticSignalType.REALISTIC_EEG,
                "description": "Realistic 8-channel EEG simulation",
            },
            {
                "name": "Synthetic EEG 16-Channel",
                "channels": 16,
                "sampling_rate": 500.0,
                "signal_type": SyntheticSignalType.REALISTIC_EEG,
                "description": "High-density 16-channel EEG simulation",
            },
            {
                "name": "Alpha Wave Generator",
                "channels": 8,
                "sampling_rate": 250.0,
                "signal_type": SyntheticSignalType.ALPHA_WAVE,
                "description": "Pure alpha wave simulation for testing",
            },
            {
                "name": "SSVEP Stimulator",
                "channels": 8,
                "sampling_rate": 250.0,
                "signal_type": SyntheticSignalType.SSVEP,
                "description": "SSVEP response simulation",
            },
            {
                "name": "P300 Speller",
                "channels": 8,
                "sampling_rate": 250.0,
                "signal_type": SyntheticSignalType.ERP,
                "description": "P300 ERP simulation",
            },
            {
                "name": "Noise Generator",
                "channels": 8,
                "sampling_rate": 250.0,
                "signal_type": SyntheticSignalType.NOISE,
                "description": "White noise for baseline testing",
            },
        ]

        for i, config in enumerate(device_configs):
            device_info = DeviceInfo(
                device_id=f"synthetic_{i+1}",
                device_type=DeviceType.SYNTHETIC,
                model=config["name"],
                firmware_version="Synthetic_v1.0",
                serial_number=f"SYN{i+1:03d}",
                channel_count=config["channels"],
                sampling_rate=config["sampling_rate"],
                supported_sampling_rates=[125.0, 250.0, 500.0, 1000.0],
                capabilities=["streaming", "configurable", "synthetic"],
                connection_type=ConnectionType.SYNTHETIC,
                connection_params={
                    "signal_type": config["signal_type"],
                    "amplitude": 50.0,
                    "noise_level": 5.0,
                    "frequency": 10.0,
                    "simulate_artifacts": True,
                    "artifact_probability": 0.01,
                    "simulate_impedance": True,
                    "simulate_issues": False,
                },
                status=DeviceStatus.DISCONNECTED,
                metadata={
                    "synthetic": True,
                    "description": config["description"],
                    "signal_type": config["signal_type"],
                },
            )

            synthetic_devices.append(device_info)

        logger.info(f"Discovered {len(synthetic_devices)} synthetic devices")
        return synthetic_devices

    async def cleanup(self) -> None:
        """Clean up synthetic adapter resources."""
        try:
            if self.is_streaming:
                await self.stop_streaming()

            if self.is_connected:
                await self.disconnect()

            await super().cleanup()

        except Exception as e:
            logger.error(f"Error cleaning up synthetic adapter: {str(e)}")

    def __str__(self) -> str:
        """String representation."""
        return f"SyntheticAdapter(type={self.signal_type}, channels={self.device_info.channel_count})"

    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"SyntheticAdapter(device_id={self.device_info.device_id}, "
            f"signal_type={self.signal_type}, channels={self.device_info.channel_count}, "
            f"connected={self.is_connected}, streaming={self.is_streaming})"
        )
