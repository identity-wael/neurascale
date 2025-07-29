"""
Feature extraction for motor imagery classification
"""

import logging
from typing import Dict, List, Optional
import numpy as np
from scipy import signal, linalg

from ..interfaces import BaseFeatureExtractor
from ..types import NeuralData, FeatureVector

logger = logging.getLogger(__name__)


class MotorImageryFeatureExtractor(BaseFeatureExtractor):
    """
    Extract features for motor imagery BCI control.

    Features include:
    - Band power in mu (8-12 Hz) and beta (13-30 Hz) rhythms
    - Event-Related Desynchronization (ERD)
    - Common Spatial Patterns (CSP)
    - Hemisphere-specific features
    """

    def __init__(self, window_size_ms: float = 1000.0):
        """
        Initialize motor imagery feature extractor

        Args:
            window_size_ms: Window size in milliseconds
        """
        self.window_size_ms = window_size_ms

        # Motor-relevant frequency bands
        self.freq_bands = {
            "mu": (8, 12),
            "beta": (13, 30),
            "low_beta": (13, 20),
            "high_beta": (20, 30),
            "smr": (12, 15),  # Sensorimotor rhythm
        }

        # Channel mapping for hemispheres
        self.hemisphere_channels = {
            "left": ["C3", "CP3", "FC3", "C1", "CP1", "FC1"],
            "right": ["C4", "CP4", "FC4", "C2", "CP2", "FC2"],
            "central": ["Cz", "CPz", "FCz"],
            "frontocentral": ["FC1", "FC2", "FCz"],
        }

        # Baseline storage for ERD calculation
        self.baseline_features: Optional[Dict[str, np.ndarray]] = None
        self.baseline_window_count = 0
        self.baseline_stable = False

        # CSP filters (would be loaded from training)
        self.csp_filters: Optional[np.ndarray] = None

    async def extract_features(self, data: NeuralData) -> FeatureVector:
        """
        Extract motor imagery features from neural data

        Args:
            data: Raw neural data

        Returns:
            Extracted feature vector
        """
        try:
            features = {}

            # Convert to numpy array
            signal_data = data.data
            sampling_rate = data.sampling_rate
            channels = data.channels

            # Extract band power features
            band_features = await self._extract_band_power(
                signal_data, sampling_rate, channels
            )
            features.update(band_features)

            # Extract hemisphere-specific features
            hemisphere_features = await self._extract_hemisphere_features(
                signal_data, sampling_rate, channels
            )
            features.update(hemisphere_features)

            # Extract ERD/ERS features
            erd_features = await self._extract_erd_features(band_features)
            features.update(erd_features)

            # Extract CSP features if filters available
            if self.csp_filters is not None:
                csp_features = await self._extract_csp_features(signal_data)
                features.update(csp_features)

            # Extract spatial patterns
            spatial_features = await self._extract_spatial_features(
                signal_data, channels
            )
            features.update(spatial_features)

            # Update baseline if in calibration phase
            if not self.baseline_stable:
                await self._update_baseline(band_features)

            return FeatureVector(
                features=features,
                timestamp=data.timestamp,
                window_size_ms=self.window_size_ms,
                metadata={
                    "extractor": "MotorImageryFeatureExtractor",
                    "baseline_stable": self.baseline_stable,
                    "csp_enabled": self.csp_filters is not None,
                },
            )

        except Exception as e:
            logger.error(f"Feature extraction error: {e}")
            raise

    async def _extract_band_power(
        self, data: np.ndarray, sampling_rate: float, channels: List[str]
    ) -> Dict[str, np.ndarray]:
        """Extract band power features"""
        features = {}

        for band_name, (low_freq, high_freq) in self.freq_bands.items():
            band_powers = []

            for channel_data in data:
                # Compute power spectral density
                freqs, psd = signal.welch(
                    channel_data, fs=sampling_rate, nperseg=min(256, len(channel_data))
                )

                # Extract band power
                band_mask = (freqs >= low_freq) & (freqs <= high_freq)
                band_power = np.trapz(psd[band_mask], freqs[band_mask])
                band_powers.append(band_power)

            features[f"{band_name}_power"] = np.array(band_powers)

        # Calculate band power ratios
        if "beta_power" in features and "alpha_power" in features:
            features["beta_alpha_ratio"] = features["beta_power"] / (
                features["alpha_power"] + 1e-6
            )

        if "mu_power" in features and "beta_power" in features:
            features["mu_beta_ratio"] = features["mu_power"] / (
                features["beta_power"] + 1e-6
            )

        return features

    async def _extract_hemisphere_features(
        self, data: np.ndarray, sampling_rate: float, channels: List[str]
    ) -> Dict[str, np.ndarray]:
        """Extract hemisphere-specific features"""
        features = {}

        # Create channel index mapping
        channel_indices = {ch: i for i, ch in enumerate(channels)}

        # Extract features for each hemisphere
        for hemisphere, hemisphere_channels in self.hemisphere_channels.items():
            # Find indices of channels in this hemisphere
            indices = []
            for ch in hemisphere_channels:
                if ch in channel_indices:
                    indices.append(channel_indices[ch])

            if not indices:
                continue

            # Extract hemisphere-specific data
            hemisphere_data = data[indices]

            # Compute mu and beta power for this hemisphere
            for band_name, (low_freq, high_freq) in [
                ("mu", (8, 12)),
                ("beta", (13, 30)),
            ]:
                powers = []

                for channel_data in hemisphere_data:
                    freqs, psd = signal.welch(
                        channel_data,
                        fs=sampling_rate,
                        nperseg=min(256, len(channel_data)),
                    )

                    band_mask = (freqs >= low_freq) & (freqs <= high_freq)
                    band_power = np.trapz(psd[band_mask], freqs[band_mask])
                    powers.append(band_power)

                # Average power across hemisphere
                features[f"{hemisphere}_hemisphere_{band_name}_power"] = np.array(
                    [np.mean(powers)]
                )

        # Calculate interhemispheric differences
        if (
            "left_hemisphere_mu_power" in features
            and "right_hemisphere_mu_power" in features
        ):
            features["mu_lateralization"] = (
                features["right_hemisphere_mu_power"]
                - features["left_hemisphere_mu_power"]
            )

        if (
            "left_hemisphere_beta_power" in features
            and "right_hemisphere_beta_power" in features
        ):
            features["beta_lateralization"] = (
                features["right_hemisphere_beta_power"]
                - features["left_hemisphere_beta_power"]
            )

        return features

    async def _extract_erd_features(
        self, band_features: Dict[str, np.ndarray]
    ) -> Dict[str, np.ndarray]:
        """Extract Event-Related Desynchronization features"""
        features = {}

        if self.baseline_features is None or not self.baseline_stable:
            # Return neutral ERD values if no baseline
            features["mu_erd"] = np.zeros(1)
            features["beta_erd"] = np.zeros(1)
            features["baseline_mu_power"] = band_features.get("mu_power", np.ones(1))
            features["baseline_beta_power"] = band_features.get(
                "beta_power", np.ones(1)
            )
            return features

        # Calculate ERD for mu rhythm
        if "mu_power" in band_features and "mu_power" in self.baseline_features:
            current_mu = np.mean(band_features["mu_power"])
            baseline_mu = np.mean(self.baseline_features["mu_power"])

            if baseline_mu > 0:
                mu_erd = (current_mu - baseline_mu) / baseline_mu
            else:
                mu_erd = 0

            features["mu_erd"] = np.array([mu_erd])
            features["baseline_mu_power"] = self.baseline_features["mu_power"]

        # Calculate ERD for beta rhythm
        if "beta_power" in band_features and "beta_power" in self.baseline_features:
            current_beta = np.mean(band_features["beta_power"])
            baseline_beta = np.mean(self.baseline_features["beta_power"])

            if baseline_beta > 0:
                beta_erd = (current_beta - baseline_beta) / baseline_beta
            else:
                beta_erd = 0

            features["beta_erd"] = np.array([beta_erd])
            features["baseline_beta_power"] = self.baseline_features["beta_power"]

        return features

    async def _extract_csp_features(self, data: np.ndarray) -> Dict[str, np.ndarray]:
        """Extract Common Spatial Pattern features"""
        features: Dict[str, np.ndarray] = {}

        if self.csp_filters is None:
            return features

        # Apply CSP filters
        # In practice, this would use pre-trained CSP filters
        n_components = min(6, self.csp_filters.shape[0])

        # Project data onto CSP components
        csp_data = np.dot(self.csp_filters[:n_components], data)

        # Calculate log variance for each component
        csp_features = np.log(np.var(csp_data, axis=1) + 1e-8)

        features["csp_features"] = csp_features
        features["raw_data"] = data  # For spatial pattern extraction

        return features

    async def _extract_spatial_features(
        self, data: np.ndarray, channels: List[str]
    ) -> Dict[str, np.ndarray]:
        """Extract spatial distribution features"""
        features = {}

        # Calculate spatial covariance
        covariance = np.cov(data)

        # Extract eigenvalues for spatial complexity
        eigenvalues = linalg.eigvalsh(covariance)

        # Spatial complexity (normalized eigenvalue spread)
        if len(eigenvalues) > 1:
            spatial_complexity = np.std(eigenvalues) / np.mean(eigenvalues)
        else:
            spatial_complexity = 0

        features["spatial_complexity"] = np.array([spatial_complexity])

        # Spatial focus (ratio of largest eigenvalue to total)
        if np.sum(eigenvalues) > 0:
            spatial_focus = np.max(eigenvalues) / np.sum(eigenvalues)
        else:
            spatial_focus = 0

        features["spatial_focus"] = np.array([spatial_focus])

        return features

    async def _update_baseline(self, band_features: Dict[str, np.ndarray]) -> None:
        """Update baseline features for ERD calculation"""
        if self.baseline_features is None:
            self.baseline_features = {}

        # Update baseline with exponential moving average
        alpha = 0.1  # Learning rate

        for key in ["mu_power", "beta_power", "smr_power"]:
            if key in band_features:
                if key in self.baseline_features:
                    self.baseline_features[key] = (1 - alpha) * self.baseline_features[
                        key
                    ] + alpha * band_features[key]
                else:
                    self.baseline_features[key] = band_features[key].copy()

        # Increment window count
        self.baseline_window_count += 1

        # Consider baseline stable after 10 windows (10 seconds)
        if self.baseline_window_count >= 10:
            self.baseline_stable = True
            logger.info("Baseline stabilized for ERD calculation")

    async def reset_baseline(self) -> None:
        """Reset baseline for new recording session"""
        self.baseline_features = None
        self.baseline_window_count = 0
        self.baseline_stable = False
        logger.info("Baseline reset for new session")

    async def set_csp_filters(self, filters: np.ndarray) -> None:
        """Set pre-trained CSP filters"""
        self.csp_filters = filters
        logger.info(f"CSP filters set: shape {filters.shape}")

    def get_feature_names(self) -> List[str]:
        """Get list of all feature names"""
        return [
            # Band power features
            "mu_power",
            "beta_power",
            "low_beta_power",
            "high_beta_power",
            "smr_power",
            "beta_alpha_ratio",
            "mu_beta_ratio",
            # Hemisphere features
            "left_hemisphere_mu_power",
            "right_hemisphere_mu_power",
            "left_hemisphere_beta_power",
            "right_hemisphere_beta_power",
            "central_mu_power",
            "central_beta_power",
            "frontocentral_beta_power",
            "mu_lateralization",
            "beta_lateralization",
            # ERD features
            "mu_erd",
            "beta_erd",
            "baseline_mu_power",
            "baseline_beta_power",
            # CSP features
            "csp_features",
            # Spatial features
            "spatial_complexity",
            "spatial_focus",
        ]
