"""Time-Frequency Features - Wavelet transforms and time-frequency analysis.

This module implements continuous wavelet transform, discrete wavelet transform,
Morlet wavelets, and Hilbert-Huang transform for time-frequency feature extraction.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
from scipy import signal
import pywt
import warnings

logger = logging.getLogger(__name__)


class TimeFrequencyFeatures:
    """Time-frequency feature extraction for neural signals."""

    def __init__(self, config: Any):
        """Initialize time-frequency feature extractor.

        Args:
            config: Processing configuration
        """
        self.config = config
        self.sampling_rate = config.sampling_rate

        # Wavelet parameters
        self.dwt_wavelet = "db4"  # Daubechies 4
        self.dwt_level = 5  # Decomposition levels

        # Morlet wavelet parameters
        self.morlet_width = 6.0  # Width parameter (omega0)

        # CWT parameters
        self.cwt_wavelet = "morl"  # Morlet for CWT
        self.cwt_scales = np.logspace(0, 3, 50)  # Scales for CWT

        logger.info("TimeFrequencyFeatures initialized")

    async def extract_wavelet_features(
        self, data: np.ndarray, wavelet_type: str = "db4"
    ) -> Dict[str, np.ndarray]:
        """Extract discrete wavelet transform features.

        Args:
            data: Signal data (channels x samples)
            wavelet_type: Wavelet type for DWT

        Returns:
            Dictionary of wavelet features
        """
        features = {}

        try:
            n_channels = data.shape[0]

            # Determine maximum decomposition level
            max_level = pywt.dwt_max_level(data.shape[1], wavelet_type)
            level = min(self.dwt_level, max_level)

            # Initialize feature arrays
            for i in range(level + 1):
                if i == 0:
                    features[f"dwt_approx_{level}_energy"] = np.zeros(n_channels)
                    features[f"dwt_approx_{level}_std"] = np.zeros(n_channels)
                    features[f"dwt_approx_{level}_entropy"] = np.zeros(n_channels)
                else:
                    features[f"dwt_detail_{i}_energy"] = np.zeros(n_channels)
                    features[f"dwt_detail_{i}_std"] = np.zeros(n_channels)
                    features[f"dwt_detail_{i}_entropy"] = np.zeros(n_channels)

            # Extract features for each channel
            for ch in range(n_channels):
                # Perform DWT
                coeffs = pywt.wavedec(data[ch, :], wavelet_type, level=level)

                # Process approximation coefficients
                approx = coeffs[0]
                features[f"dwt_approx_{level}_energy"][ch] = np.sum(approx**2)
                features[f"dwt_approx_{level}_std"][ch] = np.std(approx)
                features[f"dwt_approx_{level}_entropy"][ch] = (
                    await self._compute_wavelet_entropy(approx)
                )

                # Process detail coefficients
                for i, detail in enumerate(coeffs[1:], 1):
                    features[f"dwt_detail_{i}_energy"][ch] = np.sum(detail**2)
                    features[f"dwt_detail_{i}_std"][ch] = np.std(detail)
                    features[f"dwt_detail_{i}_entropy"][ch] = (
                        await self._compute_wavelet_entropy(detail)
                    )

            # Compute relative wavelet energy
            relative_energy = await self._compute_relative_wavelet_energy(
                features, level
            )
            features.update(relative_energy)

            # Wavelet packet features
            wp_features = await self._extract_wavelet_packet_features(
                data, wavelet_type
            )
            features.update(wp_features)

            logger.debug(f"Extracted {len(features)} wavelet features")

            return features

        except Exception as e:
            logger.error(f"Error extracting wavelet features: {str(e)}")
            return features

    async def extract_morlet_features(
        self, data: np.ndarray, frequencies: List[float]
    ) -> Dict[str, np.ndarray]:
        """Extract features using Morlet wavelet transform.

        Args:
            data: Signal data (channels x samples)
            frequencies: List of frequencies to analyze

        Returns:
            Dictionary of Morlet wavelet features
        """
        features = {}

        try:
            n_channels = data.shape[0]

            for freq in frequencies:
                # Initialize feature arrays for this frequency
                features[f"morlet_{freq}hz_power"] = np.zeros(n_channels)
                features[f"morlet_{freq}hz_phase_consistency"] = np.zeros(n_channels)
                features[f"morlet_{freq}hz_amplitude_std"] = np.zeros(n_channels)

                for ch in range(n_channels):
                    # Compute Morlet wavelet transform
                    scales = self._freq_to_scale(freq, self.cwt_wavelet)
                    cwt_coeffs = signal.cwt(
                        data[ch, :], signal.morlet2, [scales], w=self.morlet_width
                    )

                    # Extract amplitude and phase
                    amplitude = np.abs(cwt_coeffs[0, :])
                    phase = np.angle(cwt_coeffs[0, :])

                    # Compute features
                    features[f"morlet_{freq}hz_power"][ch] = np.mean(amplitude**2)
                    features[f"morlet_{freq}hz_amplitude_std"][ch] = np.std(amplitude)

                    # Phase consistency (mean resultant length)
                    features[f"morlet_{freq}hz_phase_consistency"][ch] = np.abs(
                        np.mean(np.exp(1j * phase))
                    )

            # Cross-frequency coupling features
            if len(frequencies) >= 2:
                cfc_features = await self._compute_cross_frequency_coupling(
                    data, frequencies
                )
                features.update(cfc_features)

            logger.debug(f"Extracted {len(features)} Morlet features")

            return features

        except Exception as e:
            logger.error(f"Error extracting Morlet features: {str(e)}")
            return features

    async def extract_hilbert_features(self, data: np.ndarray) -> Dict[str, np.ndarray]:
        """Extract features using Hilbert transform.

        Args:
            data: Signal data (channels x samples)

        Returns:
            Dictionary of Hilbert transform features
        """
        features = {}

        try:
            # Compute analytic signal
            analytic_signal = signal.hilbert(data, axis=1)

            # Instantaneous amplitude (envelope)
            inst_amplitude = np.abs(analytic_signal)

            # Instantaneous phase
            inst_phase = np.angle(analytic_signal)

            # Instantaneous frequency
            inst_freq = (
                np.diff(np.unwrap(inst_phase, axis=1), axis=1)
                * self.sampling_rate
                / (2 * np.pi)
            )

            # Features from instantaneous amplitude
            features["hilbert_amplitude_mean"] = np.mean(inst_amplitude, axis=1)
            features["hilbert_amplitude_std"] = np.std(inst_amplitude, axis=1)
            features["hilbert_amplitude_skew"] = self._safe_skew(inst_amplitude, axis=1)

            # Features from instantaneous frequency
            features["hilbert_freq_mean"] = np.mean(inst_freq, axis=1)
            features["hilbert_freq_std"] = np.std(inst_freq, axis=1)

            # Amplitude-frequency correlation
            amp_freq_corr = np.zeros(data.shape[0])
            for ch in range(data.shape[0]):
                if inst_freq.shape[1] > 0:
                    corr = np.corrcoef(inst_amplitude[ch, 1:], inst_freq[ch, :])[0, 1]
                    amp_freq_corr[ch] = corr if not np.isnan(corr) else 0
            features["hilbert_amp_freq_correlation"] = amp_freq_corr

            # Hilbert-Huang spectrum features
            hhs_features = await self._compute_hilbert_huang_features(
                data, analytic_signal
            )
            features.update(hhs_features)

            logger.debug(f"Extracted {len(features)} Hilbert features")

            return features

        except Exception as e:
            logger.error(f"Error extracting Hilbert features: {str(e)}")
            return features

    async def extract_stockwell_features(
        self, data: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """Extract features using S-transform (Stockwell transform).

        Args:
            data: Signal data (channels x samples)

        Returns:
            Dictionary of S-transform features
        """
        features = {}

        try:
            n_channels = data.shape[0]

            # Define frequency bands for S-transform analysis
            freq_bands = {
                "delta": (0.5, 4),
                "theta": (4, 8),
                "alpha": (8, 13),
                "beta": (13, 30),
                "gamma": (30, 50),
            }

            for band_name, (low_freq, high_freq) in freq_bands.items():
                features[f"stockwell_{band_name}_power"] = np.zeros(n_channels)
                features[f"stockwell_{band_name}_complexity"] = np.zeros(n_channels)

            for ch in range(n_channels):
                # Compute S-transform
                st_matrix = await self._stockwell_transform(data[ch, :])

                if st_matrix is not None:
                    freqs = np.fft.fftfreq(data.shape[1], 1 / self.sampling_rate)[
                        : data.shape[1] // 2
                    ]

                    # Extract features for each band
                    for band_name, (low_freq, high_freq) in freq_bands.items():
                        band_mask = (freqs >= low_freq) & (freqs <= high_freq)
                        if np.any(band_mask):
                            band_st = st_matrix[band_mask, :]

                            # Average power in band
                            features[f"stockwell_{band_name}_power"][ch] = np.mean(
                                np.abs(band_st) ** 2
                            )

                            # Time-frequency complexity (entropy)
                            tf_entropy = await self._compute_tf_entropy(np.abs(band_st))
                            features[f"stockwell_{band_name}_complexity"][
                                ch
                            ] = tf_entropy

            return features

        except Exception as e:
            logger.error(f"Error extracting S-transform features: {str(e)}")
            return features

    async def _compute_wavelet_entropy(self, coeffs: np.ndarray) -> float:
        """Compute wavelet entropy from coefficients.

        Args:
            coeffs: Wavelet coefficients

        Returns:
            Wavelet entropy value
        """
        # Normalize coefficients
        coeffs_squared = coeffs**2
        total_energy = np.sum(coeffs_squared)

        if total_energy == 0:
            return 0

        # Probability distribution
        p = coeffs_squared / total_energy

        # Remove zeros
        p = p[p > 0]

        # Compute entropy
        entropy = -np.sum(p * np.log(p))

        return entropy

    async def _compute_relative_wavelet_energy(
        self, features: Dict[str, np.ndarray], level: int
    ) -> Dict[str, np.ndarray]:
        """Compute relative wavelet energy across decomposition levels.

        Args:
            features: Dictionary containing wavelet energies
            level: Number of decomposition levels

        Returns:
            Dictionary of relative energy features
        """
        relative_features = {}
        n_channels = features[f"dwt_approx_{level}_energy"].shape[0]

        for ch in range(n_channels):
            # Total energy across all levels
            total_energy = features[f"dwt_approx_{level}_energy"][ch]
            for i in range(1, level + 1):
                total_energy += features[f"dwt_detail_{i}_energy"][ch]

            if total_energy > 0:
                # Relative energy for approximation
                relative_features.setdefault(
                    f"dwt_approx_{level}_rel_energy", np.zeros(n_channels)
                )
                relative_features[f"dwt_approx_{level}_rel_energy"][ch] = (
                    features[f"dwt_approx_{level}_energy"][ch] / total_energy
                )

                # Relative energy for details
                for i in range(1, level + 1):
                    key = f"dwt_detail_{i}_rel_energy"
                    relative_features.setdefault(key, np.zeros(n_channels))
                    relative_features[key][ch] = (
                        features[f"dwt_detail_{i}_energy"][ch] / total_energy
                    )

        return relative_features

    async def _extract_wavelet_packet_features(
        self, data: np.ndarray, wavelet_type: str
    ) -> Dict[str, np.ndarray]:
        """Extract wavelet packet decomposition features.

        Args:
            data: Signal data (channels x samples)
            wavelet_type: Wavelet type

        Returns:
            Dictionary of wavelet packet features
        """
        features = {}
        n_channels = data.shape[0]

        # Wavelet packet decomposition level
        wp_level = min(4, pywt.dwt_max_level(data.shape[1], wavelet_type))

        # Number of nodes at final level
        n_nodes = 2**wp_level

        # Initialize feature arrays
        features["wp_energy_distribution"] = np.zeros((n_channels, n_nodes))
        features["wp_best_basis_entropy"] = np.zeros(n_channels)

        for ch in range(n_channels):
            # Wavelet packet decomposition
            wp = pywt.WaveletPacket(data[ch, :], wavelet_type, maxlevel=wp_level)

            # Get all nodes at final level
            nodes = [node for node in wp.get_level(wp_level, "natural")]

            # Energy distribution
            for i, node in enumerate(nodes):
                if i < n_nodes:
                    features["wp_energy_distribution"][ch, i] = np.sum(node.data**2)

            # Best basis entropy
            # Find best basis using entropy criterion
            wp_best = pywt.WaveletPacket(data[ch, :], wavelet_type, maxlevel=wp_level)
            best_tree = wp_best.get_leaf_nodes()

            total_entropy = 0
            for node in best_tree:
                if len(node.data) > 0:
                    entropy = await self._compute_wavelet_entropy(node.data)
                    total_entropy += entropy

            features["wp_best_basis_entropy"][ch] = total_entropy

        # Flatten energy distribution for feature vector
        features["wp_energy_mean"] = np.mean(features["wp_energy_distribution"], axis=1)
        features["wp_energy_std"] = np.std(features["wp_energy_distribution"], axis=1)

        # Remove full distribution to save memory
        del features["wp_energy_distribution"]

        return features

    async def _compute_cross_frequency_coupling(
        self, data: np.ndarray, frequencies: List[float]
    ) -> Dict[str, np.ndarray]:
        """Compute cross-frequency coupling features.

        Args:
            data: Signal data (channels x samples)
            frequencies: List of frequencies

        Returns:
            Dictionary of CFC features
        """
        features = {}
        n_channels = data.shape[0]

        # Phase-amplitude coupling between frequency pairs
        freq_pairs = [
            (frequencies[i], frequencies[j])
            for i in range(len(frequencies))
            for j in range(i + 1, len(frequencies))
        ]

        for low_freq, high_freq in freq_pairs[:3]:  # Limit to first 3 pairs
            pac_values = np.zeros(n_channels)

            for ch in range(n_channels):
                # Extract phase of low frequency
                low_sos = signal.butter(
                    4,
                    [low_freq - 1, low_freq + 1],
                    btype="band",
                    fs=self.sampling_rate,
                    output="sos",
                )
                low_filtered = signal.sosfiltfilt(low_sos, data[ch, :])
                low_phase = np.angle(signal.hilbert(low_filtered))

                # Extract amplitude of high frequency
                high_sos = signal.butter(
                    4,
                    [high_freq - 2, high_freq + 2],
                    btype="band",
                    fs=self.sampling_rate,
                    output="sos",
                )
                high_filtered = signal.sosfiltfilt(high_sos, data[ch, :])
                high_amp = np.abs(signal.hilbert(high_filtered))

                # Compute PAC using mean vector length
                n_bins = 18
                phase_bins = np.linspace(-np.pi, np.pi, n_bins + 1)

                amp_by_phase = []
                for i in range(n_bins):
                    mask = (low_phase >= phase_bins[i]) & (
                        low_phase < phase_bins[i + 1]
                    )
                    if np.any(mask):
                        amp_by_phase.append(np.mean(high_amp[mask]))
                    else:
                        amp_by_phase.append(0)

                # Normalize and compute PAC
                amp_by_phase = np.array(amp_by_phase)
                if np.std(amp_by_phase) > 0:
                    pac_values[ch] = np.abs(
                        np.mean(
                            amp_by_phase
                            * np.exp(1j * (phase_bins[:-1] + np.diff(phase_bins) / 2))
                        )
                    ) / np.mean(amp_by_phase)

            features[f"pac_{int(low_freq)}_{int(high_freq)}hz"] = pac_values

        return features

    async def _compute_hilbert_huang_features(
        self, data: np.ndarray, analytic_signal: np.ndarray
    ) -> Dict[str, np.ndarray]:
        """Compute Hilbert-Huang spectrum features.

        Args:
            data: Original signal data
            analytic_signal: Analytic signal from Hilbert transform

        Returns:
            Dictionary of HHS features
        """
        features = {}

        # Empirical Mode Decomposition (simplified version)
        # In practice, would use PyEMD or similar library
        n_imfs = 3  # Number of intrinsic mode functions

        features["hhs_imf_energy_ratio"] = np.zeros((data.shape[0], n_imfs))
        features["hhs_marginal_spectrum_peak"] = np.zeros(data.shape[0])

        for ch in range(data.shape[0]):
            # Simplified IMF extraction using filtering
            imf_energies = []

            # Low frequency IMF
            low_sos = signal.butter(
                4, 5, btype="low", fs=self.sampling_rate, output="sos"
            )
            imf_low = signal.sosfiltfilt(low_sos, data[ch, :])
            imf_energies.append(np.sum(imf_low**2))

            # Mid frequency IMF
            mid_sos = signal.butter(
                4, [5, 20], btype="band", fs=self.sampling_rate, output="sos"
            )
            imf_mid = signal.sosfiltfilt(mid_sos, data[ch, :])
            imf_energies.append(np.sum(imf_mid**2))

            # High frequency IMF
            high_sos = signal.butter(
                4, 20, btype="high", fs=self.sampling_rate, output="sos"
            )
            imf_high = signal.sosfiltfilt(high_sos, data[ch, :])
            imf_energies.append(np.sum(imf_high**2))

            # Energy ratios
            total_energy = sum(imf_energies)
            if total_energy > 0:
                for i in range(n_imfs):
                    features["hhs_imf_energy_ratio"][ch, i] = (
                        imf_energies[i] / total_energy
                    )

            # Marginal spectrum peak (simplified)
            inst_freq = (
                np.diff(np.unwrap(np.angle(analytic_signal[ch, :])))
                * self.sampling_rate
                / (2 * np.pi)
            )
            if len(inst_freq) > 0:
                freq_hist, freq_bins = np.histogram(inst_freq, bins=50, range=(0, 50))
                peak_idx = np.argmax(freq_hist)
                features["hhs_marginal_spectrum_peak"][ch] = freq_bins[peak_idx]

        # Flatten IMF energy ratios
        features["hhs_imf1_energy"] = features["hhs_imf_energy_ratio"][:, 0]
        features["hhs_imf2_energy"] = features["hhs_imf_energy_ratio"][:, 1]
        features["hhs_imf3_energy"] = features["hhs_imf_energy_ratio"][:, 2]
        del features["hhs_imf_energy_ratio"]

        return features

    async def _stockwell_transform(
        self, signal_data: np.ndarray
    ) -> Optional[np.ndarray]:
        """Compute S-transform of a signal.

        Args:
            signal_data: 1D signal data

        Returns:
            S-transform matrix or None
        """
        try:
            n = len(signal_data)

            # FFT of signal
            fft_signal = np.fft.fft(signal_data)

            # Initialize S-transform matrix
            st_matrix = np.zeros((n // 2, n), dtype=complex)

            # Compute S-transform for each frequency
            for k in range(1, n // 2):  # Skip DC
                # Gaussian window width
                sigma = k / (2 * np.pi)

                # Generate Gaussian window
                gaussian = np.exp(-0.5 * (np.arange(n) - n // 2) ** 2 / sigma**2)
                gaussian = np.roll(gaussian, n // 2)

                # Apply window in frequency domain
                windowed_fft = fft_signal * np.fft.fft(gaussian)

                # Inverse FFT to get S-transform
                st_matrix[k, :] = np.fft.ifft(windowed_fft)

            return st_matrix

        except Exception as e:
            logger.error(f"Error in S-transform: {str(e)}")
            return None

    async def _compute_tf_entropy(self, tf_matrix: np.ndarray) -> float:
        """Compute time-frequency entropy.

        Args:
            tf_matrix: Time-frequency representation

        Returns:
            TF entropy value
        """
        # Normalize to probability distribution
        tf_power = np.abs(tf_matrix) ** 2
        total_power = np.sum(tf_power)

        if total_power == 0:
            return 0

        p = tf_power / total_power
        p = p.flatten()
        p = p[p > 0]

        # Compute entropy
        entropy = -np.sum(p * np.log(p))

        return entropy

    def _freq_to_scale(self, freq: float, wavelet: str) -> float:
        """Convert frequency to wavelet scale.

        Args:
            freq: Frequency in Hz
            wavelet: Wavelet name

        Returns:
            Corresponding scale
        """
        # For Morlet wavelet
        if "morl" in wavelet:
            # Center frequency of Morlet wavelet
            center_freq = self.morlet_width / (2 * np.pi)
            scale = center_freq * self.sampling_rate / freq
            return scale
        else:
            # For other wavelets, use pywt
            center_freq = pywt.central_frequency(wavelet)
            scale = center_freq * self.sampling_rate / freq
            return scale

    def _safe_skew(self, data: np.ndarray, axis: int = 1) -> np.ndarray:
        """Compute skewness safely handling edge cases.

        Args:
            data: Input data
            axis: Axis along which to compute skewness

        Returns:
            Skewness values
        """
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            skew_values = np.zeros(data.shape[0])
            for i in range(data.shape[0]):
                row_data = data[i, :] if axis == 1 else data[:, i]
                if np.std(row_data) > 0:
                    skew_values[i] = stats.skew(row_data)
            return skew_values

    def update_config(self, params: Dict[str, Any]) -> None:
        """Update feature extraction configuration.

        Args:
            params: Parameters to update
        """
        if "dwt_wavelet" in params:
            self.dwt_wavelet = params["dwt_wavelet"]
        if "dwt_level" in params:
            self.dwt_level = params["dwt_level"]
        if "morlet_width" in params:
            self.morlet_width = params["morlet_width"]
        if "cwt_wavelet" in params:
            self.cwt_wavelet = params["cwt_wavelet"]
