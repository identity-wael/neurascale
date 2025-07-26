"""Time Domain Features - Statistical and temporal feature extraction.

This module implements various time-domain features including statistical
measures, complexity metrics, and amplitude-based features.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from scipy import stats, signal
from sklearn.preprocessing import StandardScaler
import warnings

logger = logging.getLogger(__name__)


class TimeDomainFeatures:
    """Time-domain feature extraction for neural signals."""

    def __init__(self, config: Any):
        """Initialize time-domain feature extractor.

        Args:
            config: Processing configuration
        """
        self.config = config
        self.sampling_rate = config.sampling_rate

        # Feature computation parameters
        self.window_size = int(0.5 * self.sampling_rate)  # 500ms windows
        self.overlap = 0.5  # 50% overlap

        # Hjorth parameters
        self.compute_hjorth = True

        # Entropy parameters
        self.entropy_bins = 50

        logger.info("TimeDomainFeatures initialized")

    async def extract_statistical_features(
        self, data: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """Extract basic statistical features.

        Args:
            data: Signal data (channels x samples)

        Returns:
            Dictionary of statistical features
        """
        features = {}

        try:
            # Mean
            features["mean"] = np.mean(data, axis=1)

            # Standard deviation
            features["std"] = np.std(data, axis=1)

            # Variance
            features["variance"] = np.var(data, axis=1)

            # Skewness
            features["skewness"] = stats.skew(data, axis=1)

            # Kurtosis
            features["kurtosis"] = stats.kurtosis(data, axis=1)

            # Percentiles
            features["percentile_25"] = np.percentile(data, 25, axis=1)
            features["percentile_75"] = np.percentile(data, 75, axis=1)
            features["iqr"] = features["percentile_75"] - features["percentile_25"]

            # Median absolute deviation
            median = np.median(data, axis=1, keepdims=True)
            features["mad"] = np.median(np.abs(data - median), axis=1)

            # Coefficient of variation
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                features["cv"] = features["std"] / (np.abs(features["mean"]) + 1e-10)

            logger.debug(f"Extracted {len(features)} statistical features")

            return features

        except Exception as e:
            logger.error(f"Error extracting statistical features: {str(e)}")
            return features

    async def extract_complexity_features(
        self, data: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """Extract signal complexity features.

        Args:
            data: Signal data (channels x samples)

        Returns:
            Dictionary of complexity features
        """
        features = {}

        try:
            # Hjorth parameters
            if self.compute_hjorth:
                hjorth_features = await self._compute_hjorth_parameters(data)
                features.update(hjorth_features)

            # Sample entropy
            sample_entropy = await self._compute_sample_entropy(data)
            features["sample_entropy"] = sample_entropy

            # Approximate entropy
            approx_entropy = await self._compute_approximate_entropy(data)
            features["approx_entropy"] = approx_entropy

            # Hurst exponent
            hurst_exp = await self._compute_hurst_exponent(data)
            features["hurst_exponent"] = hurst_exp

            # Fractal dimension (Higuchi's method)
            fractal_dim = await self._compute_fractal_dimension(data)
            features["fractal_dimension"] = fractal_dim

            # Zero crossing rate
            zcr = await self._compute_zero_crossing_rate(data)
            features["zero_crossing_rate"] = zcr

            logger.debug(f"Extracted {len(features)} complexity features")

            return features

        except Exception as e:
            logger.error(f"Error extracting complexity features: {str(e)}")
            return features

    async def extract_amplitude_features(
        self, data: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """Extract amplitude-based features.

        Args:
            data: Signal data (channels x samples)

        Returns:
            Dictionary of amplitude features
        """
        features = {}

        try:
            # Root mean square
            features["rms"] = np.sqrt(np.mean(data**2, axis=1))

            # Peak-to-peak amplitude
            features["peak_to_peak"] = np.ptp(data, axis=1)

            # Maximum absolute amplitude
            features["max_abs_amplitude"] = np.max(np.abs(data), axis=1)

            # Mean absolute amplitude
            features["mean_abs_amplitude"] = np.mean(np.abs(data), axis=1)

            # Amplitude histogram features
            hist_features = await self._compute_amplitude_histogram_features(data)
            features.update(hist_features)

            # Envelope features
            envelope_features = await self._compute_envelope_features(data)
            features.update(envelope_features)

            logger.debug(f"Extracted {len(features)} amplitude features")

            return features

        except Exception as e:
            logger.error(f"Error extracting amplitude features: {str(e)}")
            return features

    async def extract_temporal_features(
        self, data: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """Extract temporal features.

        Args:
            data: Signal data (channels x samples)

        Returns:
            Dictionary of temporal features
        """
        features = {}

        try:
            # Autocorrelation features
            autocorr_features = await self._compute_autocorrelation_features(data)
            features.update(autocorr_features)

            # Line length
            line_length = await self._compute_line_length(data)
            features["line_length"] = line_length

            # Non-linear energy
            nonlinear_energy = await self._compute_nonlinear_energy(data)
            features["nonlinear_energy"] = nonlinear_energy

            # Activity, mobility, complexity (alternative Hjorth)
            activity = np.var(data, axis=1)
            features["activity"] = activity

            # First derivative
            diff1 = np.diff(data, axis=1)
            mobility = np.sqrt(np.var(diff1, axis=1) / (activity + 1e-10))
            features["mobility"] = mobility

            # Second derivative
            diff2 = np.diff(diff1, axis=1)
            complexity = np.sqrt(
                np.var(diff2, axis=1) / (np.var(diff1, axis=1) + 1e-10)
            ) / (mobility + 1e-10)
            features["complexity"] = complexity

            logger.debug(f"Extracted {len(features)} temporal features")

            return features

        except Exception as e:
            logger.error(f"Error extracting temporal features: {str(e)}")
            return features

    async def _compute_hjorth_parameters(
        self, data: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """Compute Hjorth parameters (activity, mobility, complexity).

        Args:
            data: Signal data (channels x samples)

        Returns:
            Dictionary with Hjorth parameters
        """
        features = {}

        # Activity (variance)
        activity = np.var(data, axis=1)
        features["hjorth_activity"] = activity

        # First derivative
        diff1 = np.diff(data, axis=1)
        diff1_var = np.var(diff1, axis=1)

        # Mobility
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            mobility = np.sqrt(diff1_var / (activity + 1e-10))
        features["hjorth_mobility"] = mobility

        # Second derivative
        diff2 = np.diff(diff1, axis=1)
        diff2_var = np.var(diff2, axis=1)

        # Complexity
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            complexity = np.sqrt(diff2_var / (diff1_var + 1e-10)) / (mobility + 1e-10)
        features["hjorth_complexity"] = complexity

        return features

    async def _compute_sample_entropy(
        self, data: np.ndarray, m: int = 2, r: float = 0.2
    ) -> np.ndarray:
        """Compute sample entropy for each channel.

        Args:
            data: Signal data (channels x samples)
            m: Pattern length
            r: Tolerance for matches (fraction of std)

        Returns:
            Sample entropy values
        """
        n_channels = data.shape[0]
        sample_entropy = np.zeros(n_channels)

        for ch in range(n_channels):
            ch_data = data[ch, :]
            N = len(ch_data)

            # Tolerance based on standard deviation
            tolerance = r * np.std(ch_data)

            # Count patterns of length m
            B = 0  # matches for length m
            A = 0  # matches for length m+1

            # Limit computation for efficiency
            max_patterns = min(N - m, 100)

            for i in range(max_patterns):
                # Pattern of length m
                pattern_m = ch_data[i : i + m]

                # Count matches for length m
                for j in range(max_patterns):
                    if i != j:
                        if np.max(np.abs(ch_data[j : j + m] - pattern_m)) <= tolerance:
                            B += 1

                            # Check m+1 if within bounds
                            if i + m < N and j + m < N:
                                if np.abs(ch_data[i + m] - ch_data[j + m]) <= tolerance:
                                    A += 1

            # Calculate sample entropy
            if B > 0:
                sample_entropy[ch] = -np.log((A + 1) / (B + 1))
            else:
                sample_entropy[ch] = -np.log(1 / max_patterns)

        return sample_entropy

    async def _compute_approximate_entropy(
        self, data: np.ndarray, m: int = 2, r: float = 0.2
    ) -> np.ndarray:
        """Compute approximate entropy for each channel.

        Args:
            data: Signal data (channels x samples)
            m: Pattern length
            r: Tolerance for matches (fraction of std)

        Returns:
            Approximate entropy values
        """
        n_channels = data.shape[0]
        approx_entropy = np.zeros(n_channels)

        for ch in range(n_channels):
            ch_data = data[ch, :]
            N = len(ch_data)

            # Tolerance based on standard deviation
            tolerance = r * np.std(ch_data)

            def _count_patterns(data, m, tolerance):
                """Count matching patterns."""
                patterns = np.array([data[i : i + m] for i in range(N - m + 1)])
                count = 0

                for i in range(len(patterns)):
                    template = patterns[i]
                    matches = np.sum(
                        np.max(np.abs(patterns - template), axis=1) <= tolerance
                    )
                    count += np.log(matches / (N - m + 1))

                return count / (N - m + 1)

            # Compute for m and m+1
            phi_m = _count_patterns(ch_data, m, tolerance)
            phi_m1 = _count_patterns(ch_data, m + 1, tolerance)

            approx_entropy[ch] = phi_m - phi_m1

        return approx_entropy

    async def _compute_hurst_exponent(self, data: np.ndarray) -> np.ndarray:
        """Compute Hurst exponent using R/S analysis.

        Args:
            data: Signal data (channels x samples)

        Returns:
            Hurst exponent values
        """
        n_channels = data.shape[0]
        hurst_exp = np.zeros(n_channels)

        for ch in range(n_channels):
            ch_data = data[ch, :]

            # R/S analysis
            lags = range(2, min(100, len(ch_data) // 2))
            tau = [
                np.sqrt(np.std(np.subtract(ch_data[lag:], ch_data[:-lag])))
                for lag in lags
            ]

            # Linear fit in log-log space
            if len(tau) > 0 and all(t > 0 for t in tau):
                poly = np.polyfit(np.log(lags), np.log(tau), 1)
                hurst_exp[ch] = poly[0] * 2.0
            else:
                hurst_exp[ch] = 0.5  # Random walk

        return np.clip(hurst_exp, 0, 1)

    async def _compute_fractal_dimension(
        self, data: np.ndarray, k_max: int = 10
    ) -> np.ndarray:
        """Compute fractal dimension using Higuchi's method.

        Args:
            data: Signal data (channels x samples)
            k_max: Maximum time interval

        Returns:
            Fractal dimension values
        """
        n_channels = data.shape[0]
        fractal_dim = np.zeros(n_channels)

        for ch in range(n_channels):
            ch_data = data[ch, :]
            N = len(ch_data)

            L = []
            k_values = []

            for k in range(1, min(k_max, N // 10)):
                Lk = []

                for m in range(k):
                    Lmk = 0
                    for i in range(1, int((N - m) / k)):
                        Lmk += abs(ch_data[m + i * k] - ch_data[m + (i - 1) * k])

                    Lmk = Lmk * (N - 1) / (k * int((N - m) / k))
                    Lk.append(Lmk)

                L.append(np.mean(Lk))
                k_values.append(k)

            # Linear fit in log-log space
            if len(L) > 2 and all(l > 0 for l in L):
                poly = np.polyfit(np.log(k_values), np.log(L), 1)
                fractal_dim[ch] = -poly[0]
            else:
                fractal_dim[ch] = 1.5  # Default value

        return np.clip(fractal_dim, 1, 2)

    async def _compute_zero_crossing_rate(self, data: np.ndarray) -> np.ndarray:
        """Compute zero crossing rate.

        Args:
            data: Signal data (channels x samples)

        Returns:
            Zero crossing rate values
        """
        # Remove mean
        data_centered = data - np.mean(data, axis=1, keepdims=True)

        # Count zero crossings
        zero_crossings = np.sum(np.diff(np.sign(data_centered), axis=1) != 0, axis=1)

        # Normalize by time duration
        duration = data.shape[1] / self.sampling_rate
        zcr = zero_crossings / duration

        return zcr

    async def _compute_amplitude_histogram_features(
        self, data: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """Compute features from amplitude histogram.

        Args:
            data: Signal data (channels x samples)

        Returns:
            Dictionary of histogram features
        """
        features = {}
        n_channels = data.shape[0]

        # Histogram entropy
        hist_entropy = np.zeros(n_channels)

        for ch in range(n_channels):
            # Compute histogram
            hist, _ = np.histogram(data[ch, :], bins=self.entropy_bins)

            # Normalize
            hist = hist / np.sum(hist)

            # Compute entropy
            hist = hist[hist > 0]  # Remove zeros
            hist_entropy[ch] = -np.sum(hist * np.log(hist))

        features["histogram_entropy"] = hist_entropy

        return features

    async def _compute_envelope_features(
        self, data: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """Compute signal envelope features.

        Args:
            data: Signal data (channels x samples)

        Returns:
            Dictionary of envelope features
        """
        features = {}

        # Compute envelope using Hilbert transform
        analytic_signal = signal.hilbert(data, axis=1)
        envelope = np.abs(analytic_signal)

        # Envelope statistics
        features["envelope_mean"] = np.mean(envelope, axis=1)
        features["envelope_std"] = np.std(envelope, axis=1)
        features["envelope_skew"] = stats.skew(envelope, axis=1)

        return features

    async def _compute_autocorrelation_features(
        self, data: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """Compute autocorrelation-based features.

        Args:
            data: Signal data (channels x samples)

        Returns:
            Dictionary of autocorrelation features
        """
        features = {}
        n_channels = data.shape[0]

        # First zero crossing of autocorrelation
        first_zero = np.zeros(n_channels)

        # Autocorrelation at specific lags
        lag_10ms = int(0.01 * self.sampling_rate)
        lag_50ms = int(0.05 * self.sampling_rate)

        autocorr_10ms = np.zeros(n_channels)
        autocorr_50ms = np.zeros(n_channels)

        for ch in range(n_channels):
            # Compute autocorrelation
            ch_data = data[ch, :]
            ch_data = ch_data - np.mean(ch_data)

            if np.std(ch_data) > 0:
                autocorr = np.correlate(ch_data, ch_data, mode="full") / (
                    len(ch_data) * np.var(ch_data)
                )
                autocorr = autocorr[len(autocorr) // 2 :]

                # Find first zero crossing
                zero_crossings = np.where(np.diff(np.sign(autocorr)))[0]
                if len(zero_crossings) > 0:
                    first_zero[ch] = zero_crossings[0] / self.sampling_rate
                else:
                    first_zero[ch] = len(autocorr) / self.sampling_rate

                # Autocorrelation at specific lags
                if lag_10ms < len(autocorr):
                    autocorr_10ms[ch] = autocorr[lag_10ms]
                if lag_50ms < len(autocorr):
                    autocorr_50ms[ch] = autocorr[lag_50ms]

        features["autocorr_first_zero"] = first_zero
        features["autocorr_10ms"] = autocorr_10ms
        features["autocorr_50ms"] = autocorr_50ms

        return features

    async def _compute_line_length(self, data: np.ndarray) -> np.ndarray:
        """Compute line length (sum of absolute differences).

        Args:
            data: Signal data (channels x samples)

        Returns:
            Line length values
        """
        line_length = np.sum(np.abs(np.diff(data, axis=1)), axis=1)

        # Normalize by duration
        duration = data.shape[1] / self.sampling_rate
        line_length = line_length / duration

        return line_length

    async def _compute_nonlinear_energy(self, data: np.ndarray) -> np.ndarray:
        """Compute nonlinear energy.

        Args:
            data: Signal data (channels x samples)

        Returns:
            Nonlinear energy values
        """
        n_channels = data.shape[0]
        nonlinear_energy = np.zeros(n_channels)

        for ch in range(n_channels):
            ch_data = data[ch, :]

            # Nonlinear energy: x(n)^2 - x(n+1)*x(n-1)
            energy = 0
            for i in range(1, len(ch_data) - 1):
                energy += ch_data[i] ** 2 - ch_data[i + 1] * ch_data[i - 1]

            nonlinear_energy[ch] = energy / (len(ch_data) - 2)

        return nonlinear_energy

    def update_config(self, params: Dict[str, Any]) -> None:
        """Update feature extraction configuration.

        Args:
            params: Parameters to update
        """
        if "window_size" in params:
            self.window_size = int(params["window_size"] * self.sampling_rate)
        if "overlap" in params:
            self.overlap = params["overlap"]
        if "compute_hjorth" in params:
            self.compute_hjorth = params["compute_hjorth"]
        if "entropy_bins" in params:
            self.entropy_bins = params["entropy_bins"]
