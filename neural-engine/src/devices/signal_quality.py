"""Signal quality monitoring for neural data acquisition devices."""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SignalQualityLevel(Enum):
    """Signal quality levels."""

    EXCELLENT = "excellent"  # SNR > 20 dB, impedance < 5k
    GOOD = "good"           # SNR > 15 dB, impedance < 10k
    FAIR = "fair"           # SNR > 10 dB, impedance < 20k
    POOR = "poor"           # SNR > 5 dB, impedance < 50k
    BAD = "bad"             # SNR < 5 dB or impedance > 50k


@dataclass
class ImpedanceResult:
    """Impedance measurement result for a channel."""

    channel_id: int
    impedance_ohms: float
    timestamp: datetime
    quality_level: SignalQualityLevel

    @property
    def impedance_kohms(self) -> float:
        """Get impedance in kilohms."""
        return self.impedance_ohms / 1000.0


@dataclass
class SignalQualityMetrics:
    """Signal quality metrics for a channel."""

    channel_id: int
    snr_db: float
    rms_amplitude: float
    line_noise_power: float
    artifacts_detected: int
    quality_level: SignalQualityLevel
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def is_acceptable(self) -> bool:
        """Check if signal quality is acceptable for recording."""
        return self.quality_level in [
            SignalQualityLevel.EXCELLENT,
            SignalQualityLevel.GOOD,
            SignalQualityLevel.FAIR
        ]


class SignalQualityMonitor:
    """Monitor and assess signal quality for neural data."""

    def __init__(
        self,
        sampling_rate: float,
        line_freq: float = 60.0,  # 60 Hz for US, 50 Hz for EU
        window_duration: float = 1.0  # 1 second window
    ):
        """
        Initialize signal quality monitor.

        Args:
            sampling_rate: Sampling rate in Hz
            line_freq: Power line frequency (50 or 60 Hz)
            window_duration: Duration of analysis window in seconds
        """
        self.sampling_rate = sampling_rate
        self.line_freq = line_freq
        self.window_duration = window_duration
        self.window_size = int(sampling_rate * window_duration)

        # Thresholds for quality assessment
        self.snr_thresholds = {
            SignalQualityLevel.EXCELLENT: 20.0,
            SignalQualityLevel.GOOD: 15.0,
            SignalQualityLevel.FAIR: 10.0,
            SignalQualityLevel.POOR: 5.0,
        }

        self.impedance_thresholds = {
            SignalQualityLevel.EXCELLENT: 5000,   # 5 kOhm
            SignalQualityLevel.GOOD: 10000,       # 10 kOhm
            SignalQualityLevel.FAIR: 20000,       # 20 kOhm
            SignalQualityLevel.POOR: 50000,       # 50 kOhm
        }

    def assess_signal_quality(
        self,
        signal: np.ndarray,
        channel_id: int
    ) -> SignalQualityMetrics:
        """
        Assess signal quality for a single channel.

        Args:
            signal: Signal data (1D array)
            channel_id: Channel identifier

        Returns:
            Signal quality metrics
        """
        # Calculate basic metrics
        rms = np.sqrt(np.mean(signal ** 2))

        # Calculate SNR
        snr_db = self._calculate_snr(signal)

        # Detect line noise
        line_noise_power = self._calculate_line_noise_power(signal)

        # Detect artifacts
        artifacts = self._detect_artifacts(signal)

        # Determine quality level
        quality_level = self._determine_quality_level_from_snr(snr_db)

        return SignalQualityMetrics(
            channel_id=channel_id,
            snr_db=snr_db,
            rms_amplitude=rms,
            line_noise_power=line_noise_power,
            artifacts_detected=artifacts,
            quality_level=quality_level
        )

    def assess_impedance(
        self,
        impedance_ohms: float,
        channel_id: int
    ) -> ImpedanceResult:
        """
        Assess impedance measurement.

        Args:
            impedance_ohms: Measured impedance in ohms
            channel_id: Channel identifier

        Returns:
            Impedance assessment result
        """
        # Determine quality level based on impedance
        quality_level = SignalQualityLevel.BAD

        for level, threshold in self.impedance_thresholds.items():
            if impedance_ohms <= threshold:
                quality_level = level
                break

        return ImpedanceResult(
            channel_id=channel_id,
            impedance_ohms=impedance_ohms,
            timestamp=datetime.now(timezone.utc),
            quality_level=quality_level
        )

    def _calculate_snr(self, signal: np.ndarray) -> float:
        """Calculate signal-to-noise ratio in dB."""
        # Simple SNR estimation using signal power vs high-frequency noise
        # This is a simplified approach - more sophisticated methods exist

        # Apply high-pass filter to estimate noise
        nyquist = self.sampling_rate / 2
        high_cutoff = min(40.0, nyquist * 0.8)  # 40 Hz or 80% of Nyquist

        # Simple differencing as high-pass filter
        noise = np.diff(signal)

        # Calculate powers
        signal_power = np.mean(signal ** 2)
        noise_power = np.mean(noise ** 2)

        # Avoid log(0)
        if noise_power == 0:
            return 40.0  # Return high SNR if no noise detected

        # Calculate SNR in dB
        snr_db = 10 * np.log10(signal_power / noise_power)

        return snr_db

    def _calculate_line_noise_power(self, signal: np.ndarray) -> float:
        """Calculate power at line frequency."""
        # FFT to get frequency spectrum
        fft = np.fft.rfft(signal)
        freqs = np.fft.rfftfreq(len(signal), 1 / self.sampling_rate)

        # Find indices around line frequency (±2 Hz)
        line_mask = np.abs(freqs - self.line_freq) <= 2.0

        # Calculate power in line frequency band
        line_power = np.mean(np.abs(fft[line_mask]) ** 2)
        total_power = np.mean(np.abs(fft) ** 2)

        # Return relative power (0-1)
        return line_power / total_power if total_power > 0 else 0.0

    def _detect_artifacts(self, signal: np.ndarray) -> int:
        """Detect number of artifacts in signal."""
        # Simple artifact detection based on amplitude threshold
        # Artifacts are defined as samples exceeding 3 standard deviations

        mean = np.mean(signal)
        std = np.std(signal)

        # Count samples outside 3 sigma
        artifacts = np.sum(np.abs(signal - mean) > 3 * std)

        return artifacts

    def _determine_quality_level_from_snr(self, snr_db: float) -> SignalQualityLevel:
        """Determine quality level from SNR."""
        for level, threshold in self.snr_thresholds.items():
            if snr_db >= threshold:
                return level
        return SignalQualityLevel.BAD

    def assess_multi_channel(
        self,
        signals: np.ndarray,
        channel_ids: Optional[List[int]] = None
    ) -> List[SignalQualityMetrics]:
        """
        Assess signal quality for multiple channels.

        Args:
            signals: Multi-channel signal data (channels x samples)
            channel_ids: List of channel IDs (default: 0 to n_channels-1)

        Returns:
            List of signal quality metrics for each channel
        """
        n_channels = signals.shape[0]

        if channel_ids is None:
            channel_ids = list(range(n_channels))

        metrics = []
        for i, channel_id in enumerate(channel_ids):
            if i < n_channels:
                channel_metrics = self.assess_signal_quality(
                    signals[i, :],
                    channel_id
                )
                metrics.append(channel_metrics)

        return metrics

    def get_overall_quality(
        self,
        metrics: List[SignalQualityMetrics]
    ) -> Tuple[SignalQualityLevel, Dict[str, float]]:
        """
        Get overall quality assessment from multiple channels.

        Args:
            metrics: List of channel metrics

        Returns:
            Overall quality level and summary statistics
        """
        if not metrics:
            return SignalQualityLevel.BAD, {}

        # Calculate summary statistics
        snr_values = [m.snr_db for m in metrics]
        quality_levels = [m.quality_level for m in metrics]

        avg_snr = np.mean(snr_values)
        min_snr = np.min(snr_values)

        # Count channels at each quality level
        level_counts = {
            level: quality_levels.count(level)
            for level in SignalQualityLevel
        }

        # Determine overall quality (conservative approach - use worst case)
        overall_quality = min(quality_levels, key=lambda x: list(SignalQualityLevel).index(x))

        summary = {
            "avg_snr_db": avg_snr,
            "min_snr_db": min_snr,
            "n_excellent": level_counts[SignalQualityLevel.EXCELLENT],
            "n_good": level_counts[SignalQualityLevel.GOOD],
            "n_fair": level_counts[SignalQualityLevel.FAIR],
            "n_poor": level_counts[SignalQualityLevel.POOR],
            "n_bad": level_counts[SignalQualityLevel.BAD],
        }

        return overall_quality, summary
