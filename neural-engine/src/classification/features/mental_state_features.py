"""
Feature extraction for mental state classification
"""

import logging
from typing import Dict, List
import numpy as np
from scipy import signal

from ..interfaces import BaseFeatureExtractor
from ..types import FeatureVector, NeuralData

logger = logging.getLogger(__name__)


class MentalStateFeatureExtractor(BaseFeatureExtractor):
    """
    Extract features for mental state classification from EEG data.

    Features include:
    - Power spectral density in different frequency bands
    - Band power ratios (beta/alpha, theta/beta)
    - Frontal asymmetry measures
    - Spectral entropy
    - Signal complexity measures
    """

    def __init__(self, window_size_ms: float = 2000.0):
        """
        Initialize feature extractor

        Args:
            window_size_ms: Window size for feature extraction in milliseconds
        """
        self.window_size_ms = window_size_ms

        # Frequency bands (Hz)
        self.bands = {
            "delta": (0.5, 4),
            "theta": (4, 8),
            "alpha": (8, 13),
            "beta": (13, 30),
            "gamma": (30, 45),
        }

        # Channel groups for spatial features
        self.channel_groups = {
            "frontal": ["Fp1", "Fp2", "F3", "F4", "Fz"],
            "central": ["C3", "C4", "Cz"],
            "parietal": ["P3", "P4", "Pz"],
            "occipital": ["O1", "O2"],
            "temporal": ["T3", "T4", "T5", "T6"],
        }

        self.feature_names = []
        self._build_feature_names()

    def _build_feature_names(self):
        """Build list of feature names"""
        # Band powers
        for band in self.bands:
            self.feature_names.append(f"{band}_power")

        # Band ratios
        self.feature_names.extend(
            ["beta_alpha_ratio", "theta_beta_ratio", "alpha_theta_ratio"]
        )

        # Spatial features
        self.feature_names.extend(
            [
                "frontal_theta",
                "frontal_alpha_asymmetry",
                "alpha_asymmetry",
                "frontal_beta",
            ]
        )

        # Complexity measures
        self.feature_names.extend(
            [
                "spectral_entropy",
                "attention_index",
                "relaxation_index",
                "signal_quality",
            ]
        )

    async def extract_features(self, data: NeuralData) -> FeatureVector:
        """
        Extract features from neural data

        Args:
            data: Neural data to process

        Returns:
            Extracted feature vector
        """
        try:
            features = {}

            # Calculate power spectral density
            psd_features = self._calculate_psd_features(data.data, data.sampling_rate)
            features.update(psd_features)

            # Calculate band ratios
            ratio_features = self._calculate_band_ratios(psd_features)
            features.update(ratio_features)

            # Calculate spatial features
            spatial_features = self._calculate_spatial_features(
                data.data, data.channels, data.sampling_rate
            )
            features.update(spatial_features)

            # Calculate complexity measures
            complexity_features = self._calculate_complexity_features(
                data.data, data.sampling_rate
            )
            features.update(complexity_features)

            # Add signal quality assessment
            features["signal_quality"] = self._assess_signal_quality(data.data)

            return FeatureVector(
                features=features,
                timestamp=data.timestamp,
                window_size_ms=self.window_size_ms,
                metadata={
                    "n_channels": len(data.channels),
                    "sampling_rate": data.sampling_rate,
                    "n_samples": data.data.shape[1],
                },
            )

        except Exception as e:
            logger.error(f"Feature extraction error: {e}")
            raise

    def _calculate_psd_features(
        self, eeg_data: np.ndarray, fs: float
    ) -> Dict[str, np.ndarray]:
        """Calculate power spectral density features"""
        features = {}

        # Calculate PSD for each channel
        n_channels = eeg_data.shape[0]

        for band_name, (low_freq, high_freq) in self.bands.items():
            band_powers = []

            for ch in range(n_channels):
                # Compute PSD using Welch's method
                freqs, psd = signal.welch(
                    eeg_data[ch, :],
                    fs=fs,
                    nperseg=min(256, eeg_data.shape[1] // 4),
                    noverlap=None,
                    nfft=None,
                    detrend="constant",
                )

                # Extract band power
                band_mask = (freqs >= low_freq) & (freqs <= high_freq)
                band_power = np.trapz(psd[band_mask], freqs[band_mask])
                band_powers.append(band_power)

            features[f"{band_name}_power"] = np.array(band_powers)

        return features

    def _calculate_band_ratios(
        self, psd_features: Dict[str, np.ndarray]
    ) -> Dict[str, np.ndarray]:
        """Calculate band power ratios"""
        features = {}

        # Beta/Alpha ratio (indicator of alertness)
        if "beta_power" in psd_features and "alpha_power" in psd_features:
            features["beta_alpha_ratio"] = psd_features["beta_power"] / (
                psd_features["alpha_power"] + 1e-10
            )

        # Theta/Beta ratio (indicator of attention)
        if "theta_power" in psd_features and "beta_power" in psd_features:
            features["theta_beta_ratio"] = psd_features["theta_power"] / (
                psd_features["beta_power"] + 1e-10
            )

        # Alpha/Theta ratio (relaxation indicator)
        if "alpha_power" in psd_features and "theta_power" in psd_features:
            features["alpha_theta_ratio"] = psd_features["alpha_power"] / (
                psd_features["theta_power"] + 1e-10
            )

        return features

    def _calculate_spatial_features(
        self, eeg_data: np.ndarray, channel_names: List[str], fs: float
    ) -> Dict[str, np.ndarray]:
        """Calculate spatial features based on channel locations"""
        features = {}

        # Create channel index mapping
        ch_indices = {ch: i for i, ch in enumerate(channel_names)}

        # Frontal theta (associated with concentration)
        frontal_channels = [
            ch for ch in self.channel_groups["frontal"] if ch in ch_indices
        ]
        if frontal_channels:
            frontal_idx = [ch_indices[ch] for ch in frontal_channels]
            frontal_data = eeg_data[frontal_idx, :]

            # Calculate frontal theta power
            freqs, psd = signal.welch(
                frontal_data.mean(axis=0),  # Average across frontal channels
                fs=fs,
                nperseg=min(256, eeg_data.shape[1] // 4),
            )
            theta_mask = (freqs >= 4) & (freqs <= 8)
            frontal_theta = np.trapz(psd[theta_mask], freqs[theta_mask])
            features["frontal_theta"] = np.array([frontal_theta])

        # Frontal alpha asymmetry (emotional valence)
        if "F3" in ch_indices and "F4" in ch_indices:
            f3_idx = ch_indices["F3"]
            f4_idx = ch_indices["F4"]

            # Calculate alpha power for each hemisphere
            freqs_f3, psd_f3 = signal.welch(
                eeg_data[f3_idx, :], fs=fs, nperseg=min(256, eeg_data.shape[1] // 4)
            )
            freqs_f4, psd_f4 = signal.welch(
                eeg_data[f4_idx, :], fs=fs, nperseg=min(256, eeg_data.shape[1] // 4)
            )

            alpha_mask = (freqs_f3 >= 8) & (freqs_f3 <= 13)
            alpha_f3 = np.trapz(psd_f3[alpha_mask], freqs_f3[alpha_mask])
            alpha_f4 = np.trapz(psd_f4[alpha_mask], freqs_f4[alpha_mask])

            # Asymmetry: ln(right) - ln(left)
            features["frontal_alpha_asymmetry"] = np.array(
                [np.log(alpha_f4 + 1e-10) - np.log(alpha_f3 + 1e-10)]
            )

        # General alpha asymmetry
        features["alpha_asymmetry"] = self._calculate_hemispheric_asymmetry(
            eeg_data, channel_names, fs, "alpha"
        )

        # Frontal beta (stress/anxiety indicator)
        if frontal_channels:
            frontal_beta = []
            for ch in frontal_channels:
                idx = ch_indices[ch]
                freqs, psd = signal.welch(
                    eeg_data[idx, :], fs=fs, nperseg=min(256, eeg_data.shape[1] // 4)
                )
                beta_mask = (freqs >= 13) & (freqs <= 30)
                beta_power = np.trapz(psd[beta_mask], freqs[beta_mask])
                frontal_beta.append(beta_power)

            features["frontal_beta"] = np.array([np.mean(frontal_beta)])

        return features

    def _calculate_hemispheric_asymmetry(
        self, eeg_data: np.ndarray, channel_names: List[str], fs: float, band: str
    ) -> np.ndarray:
        """Calculate hemispheric asymmetry for a given frequency band"""
        # Define hemisphere pairs
        hemisphere_pairs = [
            ("F3", "F4"),
            ("C3", "C4"),
            ("P3", "P4"),
            ("T3", "T4"),
            ("O1", "O2"),
        ]

        ch_indices = {ch: i for i, ch in enumerate(channel_names)}
        asymmetries = []

        for left, right in hemisphere_pairs:
            if left in ch_indices and right in ch_indices:
                left_idx = ch_indices[left]
                right_idx = ch_indices[right]

                # Calculate band power for each hemisphere
                freqs_l, psd_l = signal.welch(
                    eeg_data[left_idx, :],
                    fs=fs,
                    nperseg=min(256, eeg_data.shape[1] // 4),
                )
                freqs_r, psd_r = signal.welch(
                    eeg_data[right_idx, :],
                    fs=fs,
                    nperseg=min(256, eeg_data.shape[1] // 4),
                )

                # Get band frequencies
                low_freq, high_freq = self.bands[band]
                band_mask = (freqs_l >= low_freq) & (freqs_l <= high_freq)

                power_l = np.trapz(psd_l[band_mask], freqs_l[band_mask])
                power_r = np.trapz(psd_r[band_mask], freqs_r[band_mask])

                # Calculate asymmetry
                asymmetry = (power_r - power_l) / (power_r + power_l + 1e-10)
                asymmetries.append(asymmetry)

        return np.array([np.mean(asymmetries)]) if asymmetries else np.array([0.0])

    def _calculate_complexity_features(
        self, eeg_data: np.ndarray, fs: float
    ) -> Dict[str, np.ndarray]:
        """Calculate signal complexity features"""
        features = {}

        # Spectral entropy (measure of signal complexity)
        spectral_entropies = []

        for ch in range(eeg_data.shape[0]):
            freqs, psd = signal.welch(
                eeg_data[ch, :], fs=fs, nperseg=min(256, eeg_data.shape[1] // 4)
            )

            # Normalize PSD to get probability distribution
            psd_norm = psd / (np.sum(psd) + 1e-10)

            # Calculate Shannon entropy
            spectral_entropy = -np.sum(psd_norm * np.log2(psd_norm + 1e-10))
            spectral_entropies.append(spectral_entropy)

        features["spectral_entropy"] = np.array(spectral_entropies)

        # Attention index (theta + beta) / (alpha)
        if hasattr(self, "_last_psd_features"):
            theta = self._last_psd_features.get("theta_power", np.array([1]))
            beta = self._last_psd_features.get("beta_power", np.array([1]))
            alpha = self._last_psd_features.get("alpha_power", np.array([1]))

            attention_index = (theta + beta) / (alpha + 1e-10)
            features["attention_index"] = attention_index.mean(keepdims=True)
        else:
            features["attention_index"] = np.array([0.5])

        # Relaxation index (alpha / (alpha + beta))
        if hasattr(self, "_last_psd_features"):
            alpha = self._last_psd_features.get("alpha_power", np.array([1]))
            beta = self._last_psd_features.get("beta_power", np.array([1]))

            relaxation_index = alpha / (alpha + beta + 1e-10)
            features["relaxation_index"] = relaxation_index.mean(keepdims=True)
        else:
            features["relaxation_index"] = np.array([0.5])

        return features

    def _assess_signal_quality(self, eeg_data: np.ndarray) -> np.ndarray:
        """Assess signal quality based on artifacts and noise"""
        quality_scores = []

        for ch in range(eeg_data.shape[0]):
            signal_ch = eeg_data[ch, :]

            # Check for flat lines (bad electrode contact)
            if np.std(signal_ch) < 0.1:
                quality_scores.append(0.0)
                continue

            # Check for excessive amplitude (movement artifacts)
            if np.max(np.abs(signal_ch)) > 200:  # μV
                quality_scores.append(0.3)
                continue

            # Check for 50/60 Hz noise
            freqs, psd = signal.welch(signal_ch, fs=250, nperseg=256)
            noise_50hz = psd[(freqs >= 48) & (freqs <= 52)].mean()
            noise_60hz = psd[(freqs >= 58) & (freqs <= 62)].mean()
            total_power = psd.mean()

            noise_ratio = (noise_50hz + noise_60hz) / (total_power + 1e-10)

            if noise_ratio > 0.2:
                quality_scores.append(0.5)
            else:
                quality_scores.append(1.0)

        return np.array([np.mean(quality_scores)])

    def get_feature_names(self) -> List[str]:
        """Get list of feature names"""
        return self.feature_names

    def get_required_window_size(self) -> float:
        """Get required window size in milliseconds"""
        return self.window_size_ms
