"""Data quality validation tools for neural datasets."""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging
from scipy import signal, stats
import matplotlib.pyplot as plt
from pathlib import Path

logger = logging.getLogger(__name__)


class QualityLevel(Enum):
    """Data quality levels."""

    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNUSABLE = "unusable"


@dataclass
class QualityMetrics:
    """Data quality metrics."""

    # Signal quality
    snr_db: float  # Signal-to-noise ratio
    channel_correlations: np.ndarray  # Inter-channel correlations
    flatline_ratio: float  # Ratio of flat segments
    clipping_ratio: float  # Ratio of clipped samples

    # Artifact detection
    motion_artifacts: int  # Number of motion artifacts
    eye_artifacts: int  # Number of eye movement artifacts
    muscle_artifacts: int  # Number of muscle artifacts
    line_noise_power: float  # Power at line frequency

    # Statistical properties
    kurtosis: np.ndarray  # Per-channel kurtosis
    skewness: np.ndarray  # Per-channel skewness
    variance: np.ndarray  # Per-channel variance

    # Overall assessment
    quality_level: QualityLevel
    channel_quality: Dict[int, QualityLevel]
    issues: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "snr_db": float(self.snr_db),
            "flatline_ratio": float(self.flatline_ratio),
            "clipping_ratio": float(self.clipping_ratio),
            "motion_artifacts": int(self.motion_artifacts),
            "eye_artifacts": int(self.eye_artifacts),
            "muscle_artifacts": int(self.muscle_artifacts),
            "line_noise_power": float(self.line_noise_power),
            "quality_level": self.quality_level.value,
            "issues": self.issues,
            "channel_quality": {
                str(k): v.value for k, v in self.channel_quality.items()
            },
        }


class DataQualityValidator:
    """Validator for neural data quality assessment."""

    def __init__(
        self,
        sampling_rate: float,
        line_freq: float = 60.0,
        amplitude_range: Tuple[float, float] = (-200, 200),  # microvolts
        min_snr_db: float = 10.0,
        max_correlation: float = 0.95,
        max_flatline_ratio: float = 0.1,
        max_clipping_ratio: float = 0.01,
    ):
        """
        Initialize data quality validator.

        Args:
            sampling_rate: Sampling rate in Hz
            line_freq: Power line frequency (50 or 60 Hz)
            amplitude_range: Expected amplitude range in microvolts
            min_snr_db: Minimum acceptable SNR
            max_correlation: Maximum acceptable channel correlation
            max_flatline_ratio: Maximum ratio of flat segments
            max_clipping_ratio: Maximum ratio of clipped samples
        """
        self.sampling_rate = sampling_rate
        self.line_freq = line_freq
        self.amplitude_range = amplitude_range
        self.min_snr_db = min_snr_db
        self.max_correlation = max_correlation
        self.max_flatline_ratio = max_flatline_ratio
        self.max_clipping_ratio = max_clipping_ratio

    def validate(
        self, data: np.ndarray, channel_names: Optional[List[str]] = None
    ) -> QualityMetrics:
        """
        Validate data quality.

        Args:
            data: Neural data array (n_samples, n_channels) or (n_epochs, n_channels, n_samples)
            channel_names: Optional channel names

        Returns:
            Quality metrics
        """
        # Reshape to 2D if needed
        if data.ndim == 3:
            # Concatenate epochs
            n_epochs, n_channels, n_samples = data.shape
            data = data.transpose(1, 0, 2).reshape(n_channels, -1).T
        elif data.ndim == 2:
            pass
        else:
            raise ValueError(f"Invalid data shape: {data.shape}")

        n_samples, n_channels = data.shape

        # Calculate metrics
        snr_db = self._calculate_snr(data)
        channel_correlations = self._calculate_correlations(data)
        flatline_ratio = self._detect_flatlines(data)
        clipping_ratio = self._detect_clipping(data)

        # Detect artifacts
        motion_artifacts = self._detect_motion_artifacts(data)
        eye_artifacts = self._detect_eye_artifacts(data, channel_names)
        muscle_artifacts = self._detect_muscle_artifacts(data)
        line_noise_power = self._calculate_line_noise(data)

        # Statistical properties
        kurtosis = stats.kurtosis(data, axis=0)
        skewness = stats.skew(data, axis=0)
        variance = np.var(data, axis=0)

        # Assess quality per channel
        channel_quality = self._assess_channel_quality(
            data, snr_db, channel_correlations, flatline_ratio, clipping_ratio
        )

        # Overall quality assessment
        quality_level, issues = self._assess_overall_quality(
            snr_db,
            channel_correlations,
            flatline_ratio,
            clipping_ratio,
            line_noise_power,
            channel_quality,
        )

        return QualityMetrics(
            snr_db=snr_db,
            channel_correlations=channel_correlations,
            flatline_ratio=flatline_ratio,
            clipping_ratio=clipping_ratio,
            motion_artifacts=motion_artifacts,
            eye_artifacts=eye_artifacts,
            muscle_artifacts=muscle_artifacts,
            line_noise_power=line_noise_power,
            kurtosis=kurtosis,
            skewness=skewness,
            variance=variance,
            quality_level=quality_level,
            channel_quality=channel_quality,
            issues=issues,
        )

    def _calculate_snr(self, data: np.ndarray) -> float:
        """Calculate signal-to-noise ratio."""
        # Estimate signal power (low frequency)
        b, a = signal.butter(4, 30 / (self.sampling_rate / 2), "low")
        signal_filtered = signal.filtfilt(b, a, data, axis=0)
        signal_power = np.mean(signal_filtered**2)

        # Estimate noise power (high frequency)
        b, a = signal.butter(4, 40 / (self.sampling_rate / 2), "high")
        noise_filtered = signal.filtfilt(b, a, data, axis=0)
        noise_power = np.mean(noise_filtered**2)

        # Calculate SNR
        if noise_power > 0:
            snr = 10 * np.log10(signal_power / noise_power)
        else:
            snr = float("inf")

        return snr

    def _calculate_correlations(self, data: np.ndarray) -> np.ndarray:
        """Calculate inter-channel correlations."""
        return np.corrcoef(data.T)

    def _detect_flatlines(self, data: np.ndarray) -> float:
        """Detect flat line segments."""
        # Calculate derivative
        diff = np.diff(data, axis=0)

        # Count samples with very small changes
        flat_threshold = 0.1  # microvolts
        flat_samples = np.sum(np.abs(diff) < flat_threshold)
        total_samples = diff.size

        return flat_samples / total_samples

    def _detect_clipping(self, data: np.ndarray) -> float:
        """Detect clipped samples."""
        # Check for samples at amplitude limits
        clipped = np.logical_or(
            data <= self.amplitude_range[0] * 0.95,
            data >= self.amplitude_range[1] * 0.95,
        )

        return np.sum(clipped) / data.size

    def _detect_motion_artifacts(self, data: np.ndarray) -> int:
        """Detect motion artifacts."""
        # Motion artifacts typically have large, slow deflections
        # Use low-frequency filter and detect outliers

        b, a = signal.butter(2, 2 / (self.sampling_rate / 2), "low")
        low_freq = signal.filtfilt(b, a, data, axis=0)

        # Detect large deflections
        threshold = 3 * np.std(low_freq)
        artifacts = np.abs(low_freq) > threshold

        # Count artifact segments
        artifact_diff = np.diff(np.any(artifacts, axis=1).astype(int))
        n_artifacts = np.sum(artifact_diff == 1)

        return n_artifacts

    def _detect_eye_artifacts(
        self, data: np.ndarray, channel_names: Optional[List[str]]
    ) -> int:
        """Detect eye movement artifacts."""
        # Eye artifacts are most prominent in frontal channels
        frontal_channels = []

        if channel_names:
            for i, name in enumerate(channel_names):
                if any(
                    front in name.upper()
                    for front in ["FP", "F3", "F4", "F7", "F8", "FZ"]
                ):
                    frontal_channels.append(i)
        else:
            # Use first few channels as proxy
            frontal_channels = list(range(min(4, data.shape[1])))

        if not frontal_channels:
            return 0

        # Eye blinks have characteristic shape in 1-15 Hz range
        b, a = signal.butter(2, [1, 15] / (self.sampling_rate / 2), "band")
        frontal_data = data[:, frontal_channels]
        filtered = signal.filtfilt(b, a, frontal_data, axis=0)

        # Detect peaks
        threshold = 2.5 * np.std(filtered)
        peaks = []
        for ch in range(filtered.shape[1]):
            ch_peaks, _ = signal.find_peaks(
                np.abs(filtered[:, ch]),
                height=threshold,
                distance=int(0.3 * self.sampling_rate),
            )
            peaks.extend(ch_peaks)

        # Cluster peaks that are close in time
        peaks = np.unique(peaks)
        if len(peaks) > 1:
            peak_diff = np.diff(peaks)
            n_artifacts = np.sum(peak_diff > 0.5 * self.sampling_rate) + 1
        else:
            n_artifacts = len(peaks)

        return n_artifacts

    def _detect_muscle_artifacts(self, data: np.ndarray) -> int:
        """Detect muscle artifacts."""
        # Muscle artifacts have high frequency content (>20 Hz)
        if self.sampling_rate > 50:
            b, a = signal.butter(
                4,
                [20, min(40, self.sampling_rate / 2.1)] / (self.sampling_rate / 2),
                "band",
            )
            high_freq = signal.filtfilt(b, a, data, axis=0)

            # Calculate envelope
            envelope = np.abs(signal.hilbert(high_freq, axis=0))

            # Detect sustained high-frequency activity
            threshold = 2 * np.median(envelope)
            artifacts = envelope > threshold

            # Count artifact segments
            artifact_any = np.any(artifacts, axis=1)
            artifact_diff = np.diff(artifact_any.astype(int))
            n_artifacts = np.sum(artifact_diff == 1)

            return n_artifacts
        else:
            return 0

    def _calculate_line_noise(self, data: np.ndarray) -> float:
        """Calculate power at line frequency."""
        # Compute PSD
        freqs, psd = signal.welch(data, fs=self.sampling_rate, axis=0)

        # Find power at line frequency
        line_idx = np.argmin(np.abs(freqs - self.line_freq))
        line_power = np.mean(psd[line_idx, :])

        # Compare to surrounding frequencies
        surrounding_idx = [
            idx
            for idx in range(len(freqs))
            if abs(freqs[idx] - self.line_freq) > 2
            and abs(freqs[idx] - self.line_freq) < 10
        ]

        if surrounding_idx:
            surrounding_power = np.mean(psd[surrounding_idx, :])
            relative_power = line_power / (surrounding_power + 1e-10)
        else:
            relative_power = line_power

        return relative_power

    def _assess_channel_quality(
        self,
        data: np.ndarray,
        snr_db: float,
        correlations: np.ndarray,
        flatline_ratio: float,
        clipping_ratio: float,
    ) -> Dict[int, QualityLevel]:
        """Assess quality for each channel."""
        n_channels = data.shape[1]
        channel_quality = {}

        for ch in range(n_channels):
            # Channel-specific metrics
            ch_var = np.var(data[:, ch])
            ch_flat = np.sum(np.abs(np.diff(data[:, ch])) < 0.1) / len(data)

            # Check for issues

            if ch_var < 1e-6:  # Nearly flat
                quality = QualityLevel.UNUSABLE
            elif ch_flat > 0.5:  # Too many flat segments
                quality = QualityLevel.POOR
            elif ch_var > 1e6:  # Extremely high variance
                quality = QualityLevel.POOR
            else:
                # Check correlations with other channels
                ch_corr = correlations[ch, :]
                ch_corr[ch] = 0  # Ignore self-correlation
                max_corr = np.max(np.abs(ch_corr))

                if max_corr > 0.98:  # Nearly identical to another channel
                    quality = QualityLevel.POOR
                elif max_corr > 0.9:
                    quality = QualityLevel.FAIR
                elif snr_db > 20 and ch_flat < 0.05:
                    quality = QualityLevel.EXCELLENT
                elif snr_db > 15 and ch_flat < 0.1:
                    quality = QualityLevel.GOOD
                else:
                    quality = QualityLevel.FAIR

            channel_quality[ch] = quality

        return channel_quality

    def _assess_overall_quality(  # noqa: C901
        self,
        snr_db: float,
        correlations: np.ndarray,
        flatline_ratio: float,
        clipping_ratio: float,
        line_noise_power: float,
        channel_quality: Dict[int, QualityLevel],
    ) -> Tuple[QualityLevel, List[str]]:
        """Assess overall data quality."""
        issues = []

        # Check each metric
        if snr_db < self.min_snr_db:
            issues.append(f"Low SNR: {snr_db:.1f} dB")

        if flatline_ratio > self.max_flatline_ratio:
            issues.append(f"High flatline ratio: {flatline_ratio:.2%}")

        if clipping_ratio > self.max_clipping_ratio:
            issues.append(f"Clipping detected: {clipping_ratio:.2%}")

        if line_noise_power > 10:
            issues.append(f"High line noise: {line_noise_power:.1f}x baseline")

        # Check channel correlations
        np.fill_diagonal(correlations, 0)
        if np.max(np.abs(correlations)) > self.max_correlation:
            issues.append("Highly correlated channels detected")

        # Count bad channels
        quality_counts = {
            level: sum(1 for q in channel_quality.values() if q == level)
            for level in QualityLevel
        }

        bad_channels = (
            quality_counts[QualityLevel.UNUSABLE] + quality_counts[QualityLevel.POOR]
        )
        if bad_channels > len(channel_quality) * 0.3:
            issues.append(f"{bad_channels} bad channels")

        # Determine overall quality
        if quality_counts[QualityLevel.UNUSABLE] > 0 or len(issues) >= 3:
            quality = QualityLevel.UNUSABLE
        elif (
            quality_counts[QualityLevel.POOR] > len(channel_quality) * 0.2
            or len(issues) >= 2
        ):
            quality = QualityLevel.POOR
        elif (
            quality_counts[QualityLevel.FAIR] > len(channel_quality) * 0.5
            or len(issues) >= 1
        ):
            quality = QualityLevel.FAIR
        elif quality_counts[QualityLevel.EXCELLENT] > len(channel_quality) * 0.7:
            quality = QualityLevel.EXCELLENT
        else:
            quality = QualityLevel.GOOD

        return quality, issues

    def generate_report(
        self,
        metrics: QualityMetrics,
        output_path: Optional[Path] = None,
        include_plots: bool = True,
    ) -> str:
        """
        Generate quality assessment report.

        Args:
            metrics: Quality metrics
            output_path: Optional path to save report
            include_plots: Whether to include plots

        Returns:
            Report as string
        """
        report = []
        report.append("=" * 60)
        report.append("Data Quality Assessment Report")
        report.append("=" * 60)
        report.append("")

        # Overall assessment
        report.append(f"Overall Quality: {metrics.quality_level.value.upper()}")
        report.append(f"SNR: {metrics.snr_db:.1f} dB")
        report.append("")

        # Issues
        if metrics.issues:
            report.append("Issues Detected:")
            for issue in metrics.issues:
                report.append(f"  - {issue}")
            report.append("")

        # Artifact summary
        report.append("Artifact Summary:")
        report.append(f"  - Motion artifacts: {metrics.motion_artifacts}")
        report.append(f"  - Eye artifacts: {metrics.eye_artifacts}")
        report.append(f"  - Muscle artifacts: {metrics.muscle_artifacts}")
        report.append(f"  - Line noise power: {metrics.line_noise_power:.1f}x baseline")
        report.append("")

        # Data quality metrics
        report.append("Data Quality Metrics:")
        report.append(f"  - Flatline ratio: {metrics.flatline_ratio:.2%}")
        report.append(f"  - Clipping ratio: {metrics.clipping_ratio:.2%}")
        report.append("")

        # Channel quality summary
        report.append("Channel Quality Summary:")
        quality_counts = {}
        for ch, quality in metrics.channel_quality.items():
            quality_counts[quality] = quality_counts.get(quality, 0) + 1

        for quality_level in QualityLevel:
            count = quality_counts.get(quality_level, 0)
            report.append(f"  - {quality_level.value}: {count} channels")

        # Statistical properties
        report.append("")
        report.append("Statistical Properties:")
        report.append(f"  - Mean kurtosis: {np.mean(metrics.kurtosis):.2f}")
        report.append(f"  - Mean skewness: {np.mean(metrics.skewness):.2f}")
        report.append(f"  - Mean variance: {np.mean(metrics.variance):.2e}")

        report_text = "\n".join(report)

        # Save report if path provided
        if output_path:
            output_path.write_text(report_text)
            logger.info(f"Quality report saved to {output_path}")

        return report_text

    def plot_quality_summary(
        self, metrics: QualityMetrics, save_path: Optional[Path] = None
    ):
        """Plot quality assessment summary."""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))

        # Channel quality distribution
        ax = axes[0, 0]
        quality_counts = {}
        for quality in metrics.channel_quality.values():
            quality_counts[quality.value] = quality_counts.get(quality.value, 0) + 1

        ax.bar(quality_counts.keys(), quality_counts.values())
        ax.set_xlabel("Quality Level")
        ax.set_ylabel("Number of Channels")
        ax.set_title("Channel Quality Distribution")

        # Channel correlations heatmap
        ax = axes[0, 1]
        im = ax.imshow(metrics.channel_correlations, cmap="RdBu_r", vmin=-1, vmax=1)
        ax.set_xlabel("Channel")
        ax.set_ylabel("Channel")
        ax.set_title("Channel Correlations")
        plt.colorbar(im, ax=ax)

        # Statistical properties
        ax = axes[1, 0]
        n_channels = len(metrics.kurtosis)
        x = np.arange(n_channels)
        ax.bar(x - 0.2, metrics.kurtosis, 0.4, label="Kurtosis")
        ax.bar(x + 0.2, metrics.skewness, 0.4, label="Skewness")
        ax.set_xlabel("Channel")
        ax.set_ylabel("Value")
        ax.set_title("Statistical Properties")
        ax.legend()

        # Variance by channel
        ax = axes[1, 1]
        ax.semilogy(metrics.variance, "o-")
        ax.set_xlabel("Channel")
        ax.set_ylabel("Variance")
        ax.set_title("Channel Variance")
        ax.grid(True)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            logger.info(f"Quality plot saved to {save_path}")
        else:
            plt.show()

        plt.close()
