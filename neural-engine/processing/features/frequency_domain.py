"""Frequency Domain Features - Spectral analysis and frequency-based features.

This module implements power spectral density, band powers, spectral entropy,
and other frequency-domain features for neural signals.
"""

import logging
from typing import Dict, Any, Optional, Tuple
import numpy as np
from scipy import signal
from scipy.integrate import simps
import warnings

logger = logging.getLogger(__name__)


class FrequencyDomainFeatures:
    """Frequency-domain feature extraction for neural signals."""

    def __init__(self, config: Any):
        """Initialize frequency-domain feature extractor.

        Args:
            config: Processing configuration
        """
        self.config = config
        self.sampling_rate = config.sampling_rate

        # FFT parameters
        self.nperseg = int(2 * self.sampling_rate)  # 2 second windows
        self.noverlap = int(0.5 * self.nperseg)  # 50% overlap
        self.nfft = None  # Auto-determine

        # Standard EEG frequency bands
        self.default_bands = {
            "delta": (0.5, 4),
            "theta": (4, 8),
            "alpha": (8, 13),
            "beta": (13, 30),
            "low_gamma": (30, 50),
            "high_gamma": (50, 100),
        }

        # Spectral parameters
        self.max_frequency = min(100, self.sampling_rate / 2)

        logger.info("FrequencyDomainFeatures initialized")

    async def extract_power_spectral_density(
        self,
        data: np.ndarray,
        freq_bands: Optional[Dict[str, Tuple[float, float]]] = None,
    ) -> Dict[str, np.ndarray]:
        """Extract power spectral density features.

        Args:
            data: Signal data (channels x samples)
            freq_bands: Frequency bands for power computation

        Returns:
            Dictionary of PSD features
        """
        features = {}
        freq_bands = freq_bands or self.default_bands

        try:
            # Compute PSD for each channel
            n_channels = data.shape[0]

            # Initialize band power arrays
            for band_name in freq_bands:
                features[f"{band_name}_power"] = np.zeros(n_channels)
                features[f"{band_name}_relative_power"] = np.zeros(n_channels)

            # Additional spectral features
            features["total_power"] = np.zeros(n_channels)
            features["peak_frequency"] = np.zeros(n_channels)
            features["spectral_centroid"] = np.zeros(n_channels)
            features["spectral_bandwidth"] = np.zeros(n_channels)
            features["spectral_edge_95"] = np.zeros(n_channels)

            for ch in range(n_channels):
                # Compute PSD using Welch's method
                freqs, psd = signal.welch(
                    data[ch, :],
                    fs=self.sampling_rate,
                    window="hann",
                    nperseg=self.nperseg,
                    noverlap=self.noverlap,
                    nfft=self.nfft,
                    scaling="density",
                )

                # Limit to max frequency
                freq_mask = freqs <= self.max_frequency
                freqs = freqs[freq_mask]
                psd = psd[freq_mask]

                # Total power
                total_power = simps(psd, freqs)
                features["total_power"][ch] = total_power

                # Band powers
                for band_name, (low_freq, high_freq) in freq_bands.items():
                    band_mask = (freqs >= low_freq) & (freqs <= high_freq)
                    if np.any(band_mask):
                        band_power = simps(psd[band_mask], freqs[band_mask])
                        features[f"{band_name}_power"][ch] = band_power

                        # Relative power
                        if total_power > 0:
                            features[f"{band_name}_relative_power"][ch] = (
                                band_power / total_power
                            )

                # Peak frequency
                if len(psd) > 0:
                    peak_idx = np.argmax(psd)
                    features["peak_frequency"][ch] = freqs[peak_idx]

                # Spectral centroid
                if total_power > 0:
                    features["spectral_centroid"][ch] = np.sum(freqs * psd) / np.sum(
                        psd
                    )

                # Spectral bandwidth
                centroid = features["spectral_centroid"][ch]
                if total_power > 0:
                    features["spectral_bandwidth"][ch] = np.sqrt(
                        np.sum(((freqs - centroid) ** 2) * psd) / np.sum(psd)
                    )

                # Spectral edge (95% of power)
                cumsum_psd = np.cumsum(psd)
                if cumsum_psd[-1] > 0:
                    edge_idx = np.where(cumsum_psd >= 0.95 * cumsum_psd[-1])[0]
                    if len(edge_idx) > 0:
                        features["spectral_edge_95"][ch] = freqs[edge_idx[0]]

            # Band power ratios
            band_ratios = await self._compute_band_ratios(features, freq_bands)
            features.update(band_ratios)

            logger.debug(f"Extracted {len(features)} PSD features")

            return features

        except Exception as e:
            logger.error(f"Error extracting PSD features: {str(e)}")
            return features

    async def extract_spectral_entropy(self, data: np.ndarray) -> np.ndarray:
        """Extract spectral entropy for each channel.

        Args:
            data: Signal data (channels x samples)

        Returns:
            Spectral entropy values
        """
        n_channels = data.shape[0]
        spectral_entropy = np.zeros(n_channels)

        try:
            for ch in range(n_channels):
                # Compute PSD
                freqs, psd = signal.welch(
                    data[ch, :],
                    fs=self.sampling_rate,
                    window="hann",
                    nperseg=self.nperseg,
                    noverlap=self.noverlap,
                )

                # Normalize PSD to get probability distribution
                psd_norm = psd / np.sum(psd)

                # Remove zero values
                psd_norm = psd_norm[psd_norm > 0]

                # Compute entropy
                if len(psd_norm) > 0:
                    spectral_entropy[ch] = -np.sum(psd_norm * np.log(psd_norm))

            return spectral_entropy

        except Exception as e:
            logger.error(f"Error extracting spectral entropy: {str(e)}")
            return spectral_entropy

    async def extract_phase_features(self, data: np.ndarray) -> Dict[str, np.ndarray]:
        """Extract phase-related features.

        Args:
            data: Signal data (channels x samples)

        Returns:
            Dictionary of phase features
        """
        features = {}

        try:
            # Phase synchronization features
            phase_sync = await self._compute_phase_synchronization(data)
            features.update(phase_sync)

            # Instantaneous phase features
            inst_phase_features = await self._compute_instantaneous_phase_features(data)
            features.update(inst_phase_features)

            logger.debug(f"Extracted {len(features)} phase features")

            return features

        except Exception as e:
            logger.error(f"Error extracting phase features: {str(e)}")
            return features

    async def extract_coherence_features(
        self,
        data: np.ndarray,
        freq_bands: Optional[Dict[str, Tuple[float, float]]] = None,
    ) -> Dict[str, np.ndarray]:
        """Extract coherence features between channels.

        Args:
            data: Signal data (channels x samples)
            freq_bands: Frequency bands for coherence computation

        Returns:
            Dictionary of coherence features
        """
        features = {}
        freq_bands = freq_bands or self.default_bands

        try:
            n_channels = data.shape[0]

            if n_channels < 2:
                logger.warning("Need at least 2 channels for coherence computation")
                return features

            # Compute pairwise coherence for each band
            for band_name, (low_freq, high_freq) in freq_bands.items():
                coherence_matrix = np.zeros((n_channels, n_channels))

                for i in range(n_channels):
                    for j in range(i + 1, n_channels):
                        # Compute coherence
                        freqs, coh = signal.coherence(
                            data[i, :],
                            data[j, :],
                            fs=self.sampling_rate,
                            window="hann",
                            nperseg=self.nperseg,
                            noverlap=self.noverlap,
                        )

                        # Average coherence in band
                        band_mask = (freqs >= low_freq) & (freqs <= high_freq)
                        if np.any(band_mask):
                            band_coherence = np.mean(coh[band_mask])
                            coherence_matrix[i, j] = band_coherence
                            coherence_matrix[j, i] = band_coherence

                # Extract features from coherence matrix
                # Mean coherence
                upper_triangle = coherence_matrix[np.triu_indices(n_channels, k=1)]
                features[f"{band_name}_coherence_mean"] = np.mean(upper_triangle)
                features[f"{band_name}_coherence_std"] = np.std(upper_triangle)

            logger.debug(f"Extracted {len(features)} coherence features")

            return features

        except Exception as e:
            logger.error(f"Error extracting coherence features: {str(e)}")
            return features

    async def extract_spectral_asymmetry(
        self, data: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """Extract spectral asymmetry features (for paired channels).

        Args:
            data: Signal data (channels x samples)

        Returns:
            Dictionary of asymmetry features
        """
        features = {}

        try:
            n_channels = data.shape[0]

            # Assume paired channels (e.g., left-right hemisphere)
            n_pairs = n_channels // 2

            if n_pairs > 0:
                for band_name, (low_freq, high_freq) in self.default_bands.items():
                    asymmetry = np.zeros(n_pairs)

                    for pair in range(n_pairs):
                        ch1 = pair * 2
                        ch2 = pair * 2 + 1

                        if ch2 < n_channels:
                            # Compute band power for each channel
                            _, psd1 = signal.welch(data[ch1, :], fs=self.sampling_rate)
                            _, psd2 = signal.welch(data[ch2, :], fs=self.sampling_rate)

                            freqs = np.linspace(0, self.sampling_rate / 2, len(psd1))
                            band_mask = (freqs >= low_freq) & (freqs <= high_freq)

                            if np.any(band_mask):
                                power1 = np.sum(psd1[band_mask])
                                power2 = np.sum(psd2[band_mask])

                                # Asymmetry index
                                if power1 + power2 > 0:
                                    asymmetry[pair] = (power1 - power2) / (
                                        power1 + power2
                                    )

                    features[f"{band_name}_asymmetry"] = asymmetry

            return features

        except Exception as e:
            logger.error(f"Error extracting spectral asymmetry: {str(e)}")
            return features

    async def _compute_band_ratios(
        self,
        features: Dict[str, np.ndarray],
        freq_bands: Dict[str, Tuple[float, float]],
    ) -> Dict[str, np.ndarray]:
        """Compute ratios between frequency bands.

        Args:
            features: Dictionary containing band powers
            freq_bands: Frequency band definitions

        Returns:
            Dictionary of band ratio features
        """
        ratios = {}

        # Common ratios
        if "theta_power" in features and "alpha_power" in features:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                ratios["theta_alpha_ratio"] = features["theta_power"] / (
                    features["alpha_power"] + 1e-10
                )

        if "theta_power" in features and "beta_power" in features:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                ratios["theta_beta_ratio"] = features["theta_power"] / (
                    features["beta_power"] + 1e-10
                )

        if "alpha_power" in features and "beta_power" in features:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                ratios["alpha_beta_ratio"] = features["alpha_power"] / (
                    features["beta_power"] + 1e-10
                )

        if "delta_power" in features and "total_power" in features:
            slow_wave_power = features["delta_power"]
            if "theta_power" in features:
                slow_wave_power = slow_wave_power + features["theta_power"]

            fast_wave_power = 0
            if "alpha_power" in features:
                fast_wave_power += features["alpha_power"]
            if "beta_power" in features:
                fast_wave_power += features["beta_power"]

            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                ratios["slow_fast_ratio"] = slow_wave_power / (fast_wave_power + 1e-10)

        return ratios

    async def _compute_phase_synchronization(
        self, data: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """Compute phase synchronization features.

        Args:
            data: Signal data (channels x samples)

        Returns:
            Dictionary of phase synchronization features
        """
        features = {}
        n_channels = data.shape[0]

        if n_channels < 2:
            return features

        # Use Hilbert transform to get instantaneous phase
        analytic_signal = signal.hilbert(data, axis=1)
        phase = np.angle(analytic_signal)

        # Phase locking value (PLV)
        plv_matrix = np.zeros((n_channels, n_channels))

        for i in range(n_channels):
            for j in range(i + 1, n_channels):
                # Phase difference
                phase_diff = phase[i, :] - phase[j, :]

                # PLV
                plv = np.abs(np.mean(np.exp(1j * phase_diff)))
                plv_matrix[i, j] = plv
                plv_matrix[j, i] = plv

        # Extract features from PLV matrix
        upper_triangle = plv_matrix[np.triu_indices(n_channels, k=1)]
        features["plv_mean"] = np.mean(upper_triangle)
        features["plv_std"] = np.std(upper_triangle)
        features["plv_max"] = np.max(upper_triangle)

        return features

    async def _compute_instantaneous_phase_features(
        self, data: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """Compute instantaneous phase features.

        Args:
            data: Signal data (channels x samples)

        Returns:
            Dictionary of instantaneous phase features
        """
        features = {}

        # Filter data into frequency bands
        for band_name, (low_freq, high_freq) in self.default_bands.items():
            # Skip if frequency band is outside Nyquist
            if low_freq >= self.sampling_rate / 2:
                continue

            # Design bandpass filter
            sos = signal.butter(
                4,
                [low_freq, min(high_freq, self.sampling_rate / 2 - 1)],
                btype="band",
                fs=self.sampling_rate,
                output="sos",
            )

            # Filter signal
            filtered = signal.sosfiltfilt(sos, data, axis=1)

            # Get instantaneous phase
            analytic = signal.hilbert(filtered, axis=1)
            inst_phase = np.angle(analytic)

            # Phase statistics
            # Circular mean
            circular_mean = np.angle(np.mean(np.exp(1j * inst_phase), axis=1))
            features[f"{band_name}_phase_mean"] = circular_mean

            # Phase entropy
            phase_entropy = np.zeros(data.shape[0])
            for ch in range(data.shape[0]):
                # Bin phases
                hist, _ = np.histogram(
                    inst_phase[ch, :], bins=20, range=(-np.pi, np.pi)
                )
                hist = hist / np.sum(hist)
                hist = hist[hist > 0]

                if len(hist) > 0:
                    phase_entropy[ch] = -np.sum(hist * np.log(hist))

            features[f"{band_name}_phase_entropy"] = phase_entropy

        return features

    def update_config(self, params: Dict[str, Any]) -> None:
        """Update feature extraction configuration.

        Args:
            params: Parameters to update
        """
        if "nperseg" in params:
            self.nperseg = int(params["nperseg"] * self.sampling_rate)
        if "noverlap" in params:
            self.noverlap = int(params["noverlap"] * self.sampling_rate)
        if "max_frequency" in params:
            self.max_frequency = min(params["max_frequency"], self.sampling_rate / 2)
        if "frequency_bands" in params:
            self.default_bands.update(params["frequency_bands"])
