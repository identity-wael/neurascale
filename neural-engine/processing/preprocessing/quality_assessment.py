"""Quality Assessment - Real-time signal quality monitoring.

This module provides comprehensive signal quality assessment metrics
and recommendations for neural signals.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from scipy import signal
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class QualityMetrics:
    """Detailed quality metrics for a signal segment."""

    # Overall metrics
    overall_score: float = 0.0  # 0-1 composite score
    snr_db: float = 0.0  # Signal-to-noise ratio in dB

    # Channel-specific metrics
    channel_scores: List[float] = field(default_factory=list)
    channel_snr: List[float] = field(default_factory=list)

    # Noise estimates
    noise_level_rms: float = 0.0  # RMS noise in microvolts
    line_noise_amplitude: float = 0.0  # 50/60 Hz noise

    # Artifact detection
    artifacts_detected: Dict[str, float] = field(default_factory=dict)
    artifact_percentage: float = 0.0  # Percentage of data with artifacts

    # Signal characteristics
    amplitude_range: Tuple[float, float] = (0.0, 0.0)  # Min, max in microvolts
    baseline_drift: float = 0.0  # Drift in microvolts/second

    # Data quality indicators
    flatline_channels: List[int] = field(default_factory=list)
    clipping_channels: List[int] = field(default_factory=list)
    high_impedance_channels: List[int] = field(default_factory=list)

    # Recommendations
    quality_issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    # Metadata
    timestamp: datetime = field(default_factory=datetime.utcnow)
    segment_duration: float = 0.0  # seconds


class QualityAssessment:
    """Signal quality assessment for neural data."""

    def __init__(self, config: Any):
        """Initialize quality assessment module.

        Args:
            config: Processing configuration
        """
        self.config = config

        # Quality thresholds
        self.good_snr_threshold = 10.0  # dB
        self.acceptable_snr_threshold = 5.0  # dB
        self.max_noise_level = 50.0  # microvolts RMS
        self.max_drift_rate = 10.0  # microvolts/second

        # Artifact thresholds
        self.amplitude_threshold = 200.0  # microvolts
        self.flatline_threshold = 0.5  # microvolts std
        self.clipping_threshold = 0.95  # percentage of range

        # Frequency bands for analysis
        self.noise_bands = {
            "line_noise": (
                (48, 52) if self.config.notch_frequencies[0] == 50 else (58, 62)
            ),
            "muscle": (20, 100),
            "low_freq": (0.1, 1),
            "high_freq": (100, None),
        }

        logger.info("QualityAssessment initialized")

    async def calculate_signal_quality(
        self, data: np.ndarray, sampling_rate: Optional[float] = None
    ) -> QualityMetrics:
        """Calculate comprehensive signal quality metrics.

        Args:
            data: Signal data (channels x samples)
            sampling_rate: Sampling rate (uses config if not provided)

        Returns:
            QualityMetrics object with detailed assessment
        """
        sampling_rate = sampling_rate or self.config.sampling_rate

        metrics = QualityMetrics()
        metrics.segment_duration = data.shape[1] / sampling_rate

        try:
            # Initialize channel-specific lists
            n_channels = data.shape[0]
            metrics.channel_scores = [0.0] * n_channels
            metrics.channel_snr = [0.0] * n_channels

            # 1. Calculate SNR for each channel
            for ch in range(n_channels):
                snr, noise_level = await self._calculate_channel_snr(
                    data[ch, :], sampling_rate
                )
                metrics.channel_snr[ch] = snr

            # Overall SNR (median of channels)
            metrics.snr_db = np.median(metrics.channel_snr)

            # 2. Estimate noise levels
            metrics.noise_level_rms = await self._estimate_noise_level(
                data, sampling_rate
            )
            metrics.line_noise_amplitude = await self._estimate_line_noise(
                data, sampling_rate
            )

            # 3. Detect artifacts
            artifact_info = await self._detect_artifacts(data, sampling_rate)
            metrics.artifacts_detected = artifact_info["types"]
            metrics.artifact_percentage = artifact_info["percentage"]

            # 4. Check signal characteristics
            metrics.amplitude_range = (np.min(data), np.max(data))
            metrics.baseline_drift = await self._calculate_baseline_drift(
                data, sampling_rate
            )

            # 5. Detect problematic channels
            metrics.flatline_channels = await self._detect_flatline_channels(data)
            metrics.clipping_channels = await self._detect_clipping_channels(data)
            metrics.high_impedance_channels = (
                await self._detect_high_impedance_channels(data)
            )

            # 6. Calculate channel quality scores
            for ch in range(n_channels):
                score = await self._calculate_channel_quality_score(ch, metrics)
                metrics.channel_scores[ch] = score

            # 7. Calculate overall quality score
            metrics.overall_score = await self._calculate_overall_score(metrics)

            # 8. Generate quality issues and recommendations
            metrics.quality_issues = await self._identify_quality_issues(metrics)
            metrics.recommendations = await self._generate_recommendations(metrics)

            logger.debug(
                f"Quality assessment complete: overall score {metrics.overall_score:.2f}"
            )

            return metrics

        except Exception as e:
            logger.error(f"Error in quality assessment: {str(e)}")
            return metrics

    async def assess_channel_quality(
        self, channel_data: np.ndarray, sampling_rate: Optional[float] = None
    ) -> float:
        """Assess quality of a single channel.

        Args:
            channel_data: 1D signal data for one channel
            sampling_rate: Sampling rate

        Returns:
            Quality score (0-1)
        """
        sampling_rate = sampling_rate or self.config.sampling_rate

        try:
            # Calculate SNR
            snr, _ = await self._calculate_channel_snr(channel_data, sampling_rate)

            # Check for flatline
            if np.std(channel_data) < self.flatline_threshold:
                return 0.0

            # Check for clipping
            data_range = np.ptp(channel_data)
            if data_range > self.amplitude_threshold * 2:
                unique_ratio = len(np.unique(channel_data)) / len(channel_data)
                if unique_ratio < 0.1:  # Few unique values suggests clipping
                    return 0.2

            # Convert SNR to quality score
            if snr >= self.good_snr_threshold:
                quality = 1.0
            elif snr >= self.acceptable_snr_threshold:
                quality = 0.5 + 0.5 * (snr - self.acceptable_snr_threshold) / (
                    self.good_snr_threshold - self.acceptable_snr_threshold
                )
            else:
                quality = 0.5 * snr / self.acceptable_snr_threshold

            return np.clip(quality, 0.0, 1.0)

        except Exception as e:
            logger.error(f"Error assessing channel quality: {str(e)}")
            return 0.5

    async def detect_signal_discontinuities(
        self, data: np.ndarray, threshold: float = 5.0
    ) -> List[int]:
        """Detect discontinuities or jumps in signal.

        Args:
            data: Signal data (channels x samples)
            threshold: Z-score threshold for discontinuity detection

        Returns:
            List of sample indices where discontinuities occur
        """
        discontinuities = []

        try:
            # Calculate first difference
            diff = np.diff(data, axis=1)

            # Calculate statistics for each channel
            for ch in range(data.shape[0]):
                ch_diff = diff[ch, :]
                mean_diff = np.mean(np.abs(ch_diff))
                std_diff = np.std(ch_diff)

                # Find outliers in difference signal
                if std_diff > 0:
                    z_scores = np.abs((ch_diff - mean_diff) / std_diff)
                    disc_indices = np.where(z_scores > threshold)[0] + 1
                    discontinuities.extend(disc_indices.tolist())

            # Remove duplicates and sort
            discontinuities = sorted(list(set(discontinuities)))

            if discontinuities:
                logger.debug(f"Detected {len(discontinuities)} discontinuities")

            return discontinuities

        except Exception as e:
            logger.error(f"Error detecting discontinuities: {str(e)}")
            return []

    async def generate_quality_report(self, metrics: QualityMetrics) -> Dict[str, Any]:
        """Generate a comprehensive quality report.

        Args:
            metrics: Quality metrics from assessment

        Returns:
            Dictionary with quality report
        """
        report = {
            "timestamp": metrics.timestamp.isoformat(),
            "duration_seconds": metrics.segment_duration,
            "overall_quality": {
                "score": metrics.overall_score,
                "rating": self._get_quality_rating(metrics.overall_score),
                "snr_db": metrics.snr_db,
            },
            "noise_analysis": {
                "noise_level_uv": metrics.noise_level_rms,
                "line_noise_uv": metrics.line_noise_amplitude,
                "noise_rating": (
                    "good" if metrics.noise_level_rms < self.max_noise_level else "poor"
                ),
            },
            "artifact_analysis": {
                "types_detected": list(metrics.artifacts_detected.keys()),
                "artifact_percentage": metrics.artifact_percentage,
                "artifact_rating": self._get_artifact_rating(
                    metrics.artifact_percentage
                ),
            },
            "channel_analysis": {
                "total_channels": len(metrics.channel_scores),
                "good_channels": sum(1 for s in metrics.channel_scores if s > 0.7),
                "acceptable_channels": sum(
                    1 for s in metrics.channel_scores if 0.4 <= s <= 0.7
                ),
                "poor_channels": sum(1 for s in metrics.channel_scores if s < 0.4),
                "flatline_channels": len(metrics.flatline_channels),
                "clipping_channels": len(metrics.clipping_channels),
                "high_impedance_channels": len(metrics.high_impedance_channels),
            },
            "signal_characteristics": {
                "amplitude_range_uv": metrics.amplitude_range,
                "baseline_drift_uv_per_sec": metrics.baseline_drift,
            },
            "quality_issues": metrics.quality_issues,
            "recommendations": metrics.recommendations,
        }

        return report

    async def _calculate_channel_snr(
        self, channel_data: np.ndarray, sampling_rate: float
    ) -> Tuple[float, float]:
        """Calculate SNR for a single channel.

        Args:
            channel_data: 1D signal data
            sampling_rate: Sampling rate

        Returns:
            Tuple of (snr_db, noise_level_rms)
        """
        try:
            # Estimate signal power in main frequency band (1-40 Hz for EEG)
            signal_band = (1, 40)
            b, a = signal.butter(
                4,
                [
                    signal_band[0] / (sampling_rate / 2),
                    signal_band[1] / (sampling_rate / 2),
                ],
                "band",
            )
            signal_filtered = signal.filtfilt(b, a, channel_data)
            signal_power = np.var(signal_filtered)

            # Estimate noise power in high frequency band
            if sampling_rate > 200:
                noise_band = (60, min(100, sampling_rate / 2 - 10))
                b, a = signal.butter(
                    4,
                    [
                        noise_band[0] / (sampling_rate / 2),
                        noise_band[1] / (sampling_rate / 2),
                    ],
                    "band",
                )
                noise_filtered = signal.filtfilt(b, a, channel_data)
                noise_power = np.var(noise_filtered)
            else:
                # Use residual after smoothing as noise estimate
                window_size = int(sampling_rate * 0.1)  # 100ms window
                smoothed = signal.savgol_filter(channel_data, window_size, 3)
                noise_power = np.var(channel_data - smoothed)

            # Calculate SNR
            if noise_power > 0:
                snr_db = 10 * np.log10(signal_power / noise_power)
            else:
                snr_db = 40.0  # High SNR if no noise detected

            noise_level_rms = np.sqrt(noise_power)

            return snr_db, noise_level_rms

        except Exception as e:
            logger.error(f"Error calculating SNR: {str(e)}")
            return 0.0, np.std(channel_data)

    async def _estimate_noise_level(
        self, data: np.ndarray, sampling_rate: float
    ) -> float:
        """Estimate overall noise level.

        Args:
            data: Signal data (channels x samples)
            sampling_rate: Sampling rate

        Returns:
            Noise level in microvolts RMS
        """
        noise_estimates = []

        for ch in range(data.shape[0]):
            _, noise_level = await self._calculate_channel_snr(
                data[ch, :], sampling_rate
            )
            noise_estimates.append(noise_level)

        return np.median(noise_estimates)

    async def _estimate_line_noise(
        self, data: np.ndarray, sampling_rate: float
    ) -> float:
        """Estimate line noise amplitude.

        Args:
            data: Signal data
            sampling_rate: Sampling rate

        Returns:
            Line noise amplitude in microvolts
        """
        # line_freq = self.config.notch_frequencies[0]  # Primary line frequency

        # Calculate power at line frequency
        freqs, psd = signal.periodogram(data, sampling_rate, axis=1)

        # Find indices for line frequency band
        freq_band = self.noise_bands["line_noise"]
        freq_mask = (freqs >= freq_band[0]) & (freqs <= freq_band[1])

        if np.any(freq_mask):
            line_power = np.mean(psd[:, freq_mask], axis=1)
            line_amplitude = np.sqrt(np.median(line_power))
            return line_amplitude

        return 0.0

    async def _detect_artifacts(
        self, data: np.ndarray, sampling_rate: float
    ) -> Dict[str, Any]:
        """Detect various types of artifacts.

        Args:
            data: Signal data
            sampling_rate: Sampling rate

        Returns:
            Dictionary with artifact information
        """
        artifact_info = {"types": {}, "percentage": 0.0}

        total_samples = data.shape[1]
        artifact_samples = np.zeros(total_samples, dtype=bool)

        # Detect amplitude artifacts
        amplitude_mask = np.any(np.abs(data) > self.amplitude_threshold, axis=0)
        if np.any(amplitude_mask):
            artifact_info["types"]["amplitude"] = np.sum(amplitude_mask) / total_samples
            artifact_samples |= amplitude_mask

        # Detect muscle artifacts (high frequency)
        for ch in range(data.shape[0]):
            hf_band = self.noise_bands["muscle"]
            b, a = signal.butter(4, hf_band[0] / (sampling_rate / 2), "high")
            hf_signal = signal.filtfilt(b, a, data[ch, :])
            hf_rms = self._moving_rms(hf_signal, int(0.1 * sampling_rate))
            muscle_mask = hf_rms > 50  # microvolts threshold

            if np.any(muscle_mask):
                artifact_samples |= muscle_mask

        if "muscle" not in artifact_info["types"] and np.any(artifact_samples):
            artifact_info["types"]["muscle"] = np.sum(artifact_samples) / total_samples

        # Calculate total artifact percentage
        artifact_info["percentage"] = np.sum(artifact_samples) / total_samples * 100

        return artifact_info

    async def _calculate_baseline_drift(
        self, data: np.ndarray, sampling_rate: float
    ) -> float:
        """Calculate baseline drift rate.

        Args:
            data: Signal data
            sampling_rate: Sampling rate

        Returns:
            Drift rate in microvolts/second
        """
        # Use low-pass filtered signal to estimate baseline
        b, a = signal.butter(4, 0.5 / (sampling_rate / 2), "low")

        drift_rates = []
        for ch in range(data.shape[0]):
            baseline = signal.filtfilt(b, a, data[ch, :])

            # Fit linear trend
            time_axis = np.arange(len(baseline)) / sampling_rate
            coeffs = np.polyfit(time_axis, baseline, 1)
            drift_rate = abs(coeffs[0])  # Slope in uV/s

            drift_rates.append(drift_rate)

        return np.median(drift_rates)

    async def _detect_flatline_channels(self, data: np.ndarray) -> List[int]:
        """Detect flatlined channels.

        Args:
            data: Signal data

        Returns:
            List of flatlined channel indices
        """
        flatline_channels = []

        for ch in range(data.shape[0]):
            if np.std(data[ch, :]) < self.flatline_threshold:
                flatline_channels.append(ch)

        return flatline_channels

    async def _detect_clipping_channels(self, data: np.ndarray) -> List[int]:
        """Detect channels with clipping.

        Args:
            data: Signal data

        Returns:
            List of clipping channel indices
        """
        clipping_channels = []

        for ch in range(data.shape[0]):
            ch_data = data[ch, :]
            data_range = np.ptp(ch_data)

            if data_range > 0:
                # Check if values cluster near extremes
                min_val, max_val = np.min(ch_data), np.max(ch_data)
                near_min = np.sum(np.abs(ch_data - min_val) < data_range * 0.05)
                near_max = np.sum(np.abs(ch_data - max_val) < data_range * 0.05)

                total_extreme = near_min + near_max
                if total_extreme / len(ch_data) > 0.1:  # >10% at extremes
                    clipping_channels.append(ch)

        return clipping_channels

    async def _detect_high_impedance_channels(self, data: np.ndarray) -> List[int]:
        """Detect channels with high impedance characteristics.

        Args:
            data: Signal data

        Returns:
            List of high impedance channel indices
        """
        high_z_channels = []

        # High impedance channels often show:
        # 1. Higher noise levels
        # 2. More susceptibility to interference

        noise_levels = []
        for ch in range(data.shape[0]):
            # High frequency noise estimate
            if self.config.sampling_rate > 200:
                b, a = signal.butter(4, 60 / (self.config.sampling_rate / 2), "high")
                hf_noise = signal.filtfilt(b, a, data[ch, :])
                noise_levels.append(np.std(hf_noise))
            else:
                noise_levels.append(np.std(data[ch, :]))

        # Channels with noise >2 std above median
        noise_median = np.median(noise_levels)
        noise_std = np.std(noise_levels)

        for ch, noise in enumerate(noise_levels):
            if noise > noise_median + 2 * noise_std:
                high_z_channels.append(ch)

        return high_z_channels

    async def _calculate_channel_quality_score(
        self, channel: int, metrics: QualityMetrics
    ) -> float:
        """Calculate quality score for a specific channel.

        Args:
            channel: Channel index
            metrics: Overall quality metrics

        Returns:
            Channel quality score (0-1)
        """
        score = 1.0

        # Penalize based on SNR
        if channel < len(metrics.channel_snr):
            snr = metrics.channel_snr[channel]
            if snr < self.acceptable_snr_threshold:
                score *= snr / self.acceptable_snr_threshold
            elif snr < self.good_snr_threshold:
                score *= 0.7 + 0.3 * (snr - self.acceptable_snr_threshold) / (
                    self.good_snr_threshold - self.acceptable_snr_threshold
                )

        # Penalize for being flagged as problematic
        if channel in metrics.flatline_channels:
            score = 0.0
        elif channel in metrics.clipping_channels:
            score *= 0.3
        elif channel in metrics.high_impedance_channels:
            score *= 0.5

        return np.clip(score, 0.0, 1.0)

    async def _calculate_overall_score(self, metrics: QualityMetrics) -> float:
        """Calculate overall quality score.

        Args:
            metrics: Quality metrics

        Returns:
            Overall score (0-1)
        """
        # Start with SNR-based score
        if metrics.snr_db >= self.good_snr_threshold:
            base_score = 1.0
        elif metrics.snr_db >= self.acceptable_snr_threshold:
            base_score = 0.5 + 0.5 * (
                metrics.snr_db - self.acceptable_snr_threshold
            ) / (self.good_snr_threshold - self.acceptable_snr_threshold)
        else:
            base_score = 0.5 * metrics.snr_db / self.acceptable_snr_threshold

        # Apply penalties
        penalties = 1.0

        # Noise penalty
        if metrics.noise_level_rms > self.max_noise_level:
            penalties *= 0.8

        # Artifact penalty
        if metrics.artifact_percentage > 10:
            penalties *= 0.7
        elif metrics.artifact_percentage > 5:
            penalties *= 0.85

        # Channel quality penalty
        good_channels = sum(1 for s in metrics.channel_scores if s > 0.7)
        channel_ratio = good_channels / len(metrics.channel_scores)
        if channel_ratio < 0.8:
            penalties *= channel_ratio

        # Drift penalty
        if metrics.baseline_drift > self.max_drift_rate:
            penalties *= 0.9

        return np.clip(base_score * penalties, 0.0, 1.0)

    async def _identify_quality_issues(self, metrics: QualityMetrics) -> List[str]:
        """Identify specific quality issues.

        Args:
            metrics: Quality metrics

        Returns:
            List of quality issues
        """
        issues = []

        if metrics.overall_score < 0.4:
            issues.append("Poor overall signal quality")

        if metrics.snr_db < self.acceptable_snr_threshold:
            issues.append(f"Low SNR: {metrics.snr_db:.1f} dB")

        if metrics.noise_level_rms > self.max_noise_level:
            issues.append(f"High noise level: {metrics.noise_level_rms:.1f} µV")

        if metrics.line_noise_amplitude > 20:
            issues.append(f"Strong line noise: {metrics.line_noise_amplitude:.1f} µV")

        if metrics.artifact_percentage > 10:
            issues.append(f"High artifact rate: {metrics.artifact_percentage:.1f}%")

        if len(metrics.flatline_channels) > 0:
            issues.append(f"Flatlined channels: {len(metrics.flatline_channels)}")

        if len(metrics.clipping_channels) > 0:
            issues.append(
                f"Clipping detected: {len(metrics.clipping_channels)} channels"
            )

        if metrics.baseline_drift > self.max_drift_rate:
            issues.append(f"Baseline drift: {metrics.baseline_drift:.1f} µV/s")

        return issues

    async def _generate_recommendations(self, metrics: QualityMetrics) -> List[str]:
        """Generate recommendations based on quality assessment.

        Args:
            metrics: Quality metrics

        Returns:
            List of recommendations
        """
        recommendations = []

        if metrics.snr_db < self.acceptable_snr_threshold:
            recommendations.append("Check electrode connections and impedances")

        if metrics.line_noise_amplitude > 20:
            recommendations.append("Enable or adjust notch filtering")
            recommendations.append("Check grounding and shielding")

        if metrics.artifact_percentage > 10:
            if "muscle" in metrics.artifacts_detected:
                recommendations.append("Ask participant to relax")
            if "amplitude" in metrics.artifacts_detected:
                recommendations.append("Check for movement or cable issues")

        if len(metrics.flatline_channels) > 0:
            recommendations.append(
                f"Reconnect flatlined channels: {metrics.flatline_channels}"
            )

        if len(metrics.high_impedance_channels) > 2:
            recommendations.append("Apply conductive gel to high impedance electrodes")

        if metrics.baseline_drift > self.max_drift_rate:
            recommendations.append("Enable high-pass filtering for drift removal")

        if not recommendations and metrics.overall_score > 0.8:
            recommendations.append("Signal quality is good")

        return recommendations

    def _get_quality_rating(self, score: float) -> str:
        """Convert numeric score to quality rating.

        Args:
            score: Quality score (0-1)

        Returns:
            Quality rating string
        """
        if score >= 0.8:
            return "excellent"
        elif score >= 0.6:
            return "good"
        elif score >= 0.4:
            return "acceptable"
        elif score >= 0.2:
            return "poor"
        else:
            return "unusable"

    def _get_artifact_rating(self, percentage: float) -> str:
        """Convert artifact percentage to rating.

        Args:
            percentage: Artifact percentage

        Returns:
            Artifact rating string
        """
        if percentage < 1:
            return "minimal"
        elif percentage < 5:
            return "low"
        elif percentage < 10:
            return "moderate"
        elif percentage < 20:
            return "high"
        else:
            return "excessive"

    def _moving_rms(self, signal_data: np.ndarray, window_size: int) -> np.ndarray:
        """Calculate moving RMS.

        Args:
            signal_data: 1D signal data
            window_size: Window size in samples

        Returns:
            Moving RMS values
        """
        return np.sqrt(
            np.convolve(signal_data**2, np.ones(window_size) / window_size, mode="same")
        )
