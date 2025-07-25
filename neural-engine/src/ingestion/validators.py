"""Data validation for neural signals."""

import numpy as np
import logging

from .data_types import NeuralDataPacket, ValidationResult, NeuralSignalType


logger = logging.getLogger(__name__)


class DataValidator:
    """Validates neural data packets for quality and integrity."""

    # Signal - specific validation parameters
    SIGNAL_RANGES = {
        NeuralSignalType.EEG: (-200, 200),  # microvolts
        NeuralSignalType.ECOG: (-500, 500),  # microvolts
        NeuralSignalType.LFP: (-1000, 1000),  # microvolts
        NeuralSignalType.EMG: (-5000, 5000),  # microvolts
        NeuralSignalType.SPIKES: (-100, 100),  # microvolts
        NeuralSignalType.ACCELEROMETER: (-20, 20),  # g - force
    }

    EXPECTED_SAMPLING_RATES = {
        NeuralSignalType.EEG: [125, 250, 256, 500, 512, 1000, 1024],
        NeuralSignalType.ECOG: [1000, 2000, 5000, 10000],
        NeuralSignalType.LFP: [1000, 2000, 5000],
        NeuralSignalType.EMG: [500, 1000, 2000],
        NeuralSignalType.SPIKES: [10000, 20000, 30000],
        NeuralSignalType.ACCELEROMETER: [50, 100, 200],
    }

    def __init__(self) -> None:
        """Initialize the data validator."""
        self.min_quality_threshold = 0.7
        self.max_missing_ratio = 0.1
        self.max_noise_ratio = 0.5  # Increased to be less sensitive to noise

    def validate_packet(self, packet: NeuralDataPacket) -> ValidationResult:
        """
        Validate a neural data packet.

        Args:
            packet: Neural data packet to validate

        Returns:
            ValidationResult with errors and warnings
        """
        result = ValidationResult(is_valid=True)

        # Basic structure validation
        self._validate_structure(packet, result)

        # Signal - specific validation
        self._validate_signal_properties(packet, result)

        # Data quality validation
        self._validate_data_quality(packet, result)

        # Metadata validation
        self._validate_metadata(packet, result)

        # Calculate overall quality score
        result.data_quality_score = self._calculate_quality_score(packet, result)

        return result

    def _validate_structure(
        self, packet: NeuralDataPacket, result: ValidationResult
    ) -> None:
        """Validate basic packet structure."""
        # Check data array - packet.data is always np.ndarray due to type annotation
        # No need to check for None or type

        if packet.data.ndim != 2:
            result.add_error(f"Data must be 2D array, got shape {packet.data.shape}")

        if packet.data.size == 0:
            result.add_error("Data array is empty")

        # Check required fields
        if not packet.session_id:
            result.add_error("Session ID is required")

        if not packet.device_info:
            result.add_error("Device info is required")
        elif not packet.device_info.device_id:
            result.add_error("Device ID is required")

    def _validate_signal_properties(
        self,
        packet: NeuralDataPacket,
        result: ValidationResult,
    ) -> None:
        """Validate signal - specific properties."""
        signal_type = packet.signal_type

        # Check sampling rate
        if signal_type in self.EXPECTED_SAMPLING_RATES:
            expected_rates = self.EXPECTED_SAMPLING_RATES[signal_type]
            if packet.sampling_rate not in expected_rates:
                result.add_warning(
                    f"Unusual sampling rate {packet.sampling_rate}Hz for "
                    f"{signal_type.value}. Expected one of: {expected_rates}"
                )

        # Check signal range
        if (
            signal_type in self.SIGNAL_RANGES
            and packet.data is not None
            and packet.data.size > 0
        ):
            min_val, max_val = self.SIGNAL_RANGES[signal_type]
            data_min = np.min(packet.data)
            data_max = np.max(packet.data)

            if data_min < min_val or data_max > max_val:
                result.add_warning(
                    f"Signal values [{data_min:.2f}, {data_max:.2f}] outside "
                    f"expected range [{min_val}, {max_val}] for {signal_type.value}"
                )

        # Check for NaN or infinite values
        if packet.data is not None:
            if np.any(np.isnan(packet.data)):
                result.add_error("Data contains NaN values")

            if np.any(np.isinf(packet.data)):
                result.add_error("Data contains infinite values")

    def _validate_data_quality(
        self,
        packet: NeuralDataPacket,
        result: ValidationResult,
    ) -> None:
        """Validate data quality metrics."""
        if packet.data is None or packet.data.size == 0:
            return

        # Check for flat lines (no signal)
        for ch_idx in range(packet.n_channels):
            channel_data = packet.data[ch_idx, :]
            if np.std(channel_data) < 0.01:  # Almost no variation
                result.add_warning(
                    f"Channel {ch_idx} appears to be flat / disconnected"
                )

        # Check for excessive noise
        for ch_idx in range(packet.n_channels):
            channel_data = packet.data[ch_idx, :]

            # Improved noise detection for neural signals
            if len(channel_data) > 10:
                # Use median absolute deviation for more robust noise estimation
                diff = np.diff(channel_data)
                mad = np.median(np.abs(diff - np.median(diff)))
                noise_estimate = mad * 1.4826  # Scale factor for MAD to std

                # Use robust signal estimate (IQR - based)
                q75, q25 = np.percentile(channel_data, [75, 25])
                signal_estimate = (q75 - q25) / 1.349  # Scale factor for IQR to std

                if signal_estimate > 0:
                    noise_ratio = noise_estimate / signal_estimate
                    # Only warn for very high noise ratios
                    if noise_ratio > self.max_noise_ratio:
                        result.add_warning(
                            f"Channel {ch_idx} has high noise "
                            f"(ratio: {noise_ratio:.2f})"
                        )

        # Check packet duration
        if packet.n_samples < 10:
            result.add_warning("Very short data packet (<10 samples)")

        # Check data quality score
        if packet.data_quality < self.min_quality_threshold:
            result.add_warning(f"Low data quality score: {packet.data_quality:.2f}")

    def _validate_metadata(
        self,
        packet: NeuralDataPacket,
        result: ValidationResult,
    ) -> None:
        """Validate packet metadata."""
        # Timestamp is always present due to type annotation

        # Check device channel consistency
        if packet.device_info and packet.device_info.channels:
            expected_channels = len(packet.device_info.channels)
            if packet.n_channels != expected_channels:
                result.add_error(
                    f"Channel count mismatch: data has {packet.n_channels} "
                    f"channels but device reports {expected_channels}"
                )

        # Validate subject ID format (should be anonymized)
        if packet.subject_id:
            if len(packet.subject_id) < 8:
                result.add_warning(
                    "Subject ID appears too short for proper anonymization"
                )

            # Check for potential PII
            if any(char.isalpha() for char in packet.subject_id[:4]):
                result.add_warning("Subject ID may contain non - anonymized data")

    def _calculate_quality_score(
        self,
        packet: NeuralDataPacket,
        result: ValidationResult,
    ) -> float:
        """
        Calculate overall data quality score.

        Returns:
            Quality score between 0 and 1
        """
        if not result.is_valid or packet.data is None or packet.data.size == 0:
            return 0.0

        score = 1.0

        # Penalize for errors (50% reduction each)
        score *= 0.5 ** len(result.errors)

        # Penalize for warnings (8% reduction each)
        score *= 0.92 ** len(result.warnings)

        # Factor in packet's own quality score
        score *= packet.data_quality

        # Check signal quality
        signal_scores = []
        for ch_idx in range(packet.n_channels):
            channel_data = packet.data[ch_idx, :]

            # Signal variance (too low = bad)
            variance = np.var(channel_data)
            variance_score = min(1.0, variance / 10.0)  # Normalize

            # Check for clipping
            min_val, max_val = self.SIGNAL_RANGES.get(packet.signal_type, (-1000, 1000))
            clipped_ratio = np.sum(
                (channel_data <= min_val) | (channel_data >= max_val)
            ) / len(channel_data)
            clipping_score = 1.0 - clipped_ratio

            channel_score = 0.5 * variance_score + 0.5 * clipping_score
            signal_scores.append(channel_score)

        if signal_scores:
            avg_signal_score = np.mean(signal_scores)
            score *= avg_signal_score

        return float(np.clip(score, 0.0, 1.0))
