"""Feature Extractor - Main orchestrator for feature extraction.

This module coordinates the extraction of various features from
preprocessed neural signals.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
import numpy as np
import time

from .time_domain import TimeDomainFeatures
from .frequency_domain import FrequencyDomainFeatures
from .time_frequency import TimeFrequencyFeatures
from .spatial_features import SpatialFeatures
from .connectivity import ConnectivityFeatures

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """Main feature extraction orchestrator."""

    def __init__(self, config: Any):
        """Initialize feature extractor.

        Args:
            config: Processing configuration
        """
        self.config = config

        # Initialize feature extractors
        self.time_domain = TimeDomainFeatures(config)
        self.frequency_domain = FrequencyDomainFeatures(config)
        self.time_frequency = TimeFrequencyFeatures(config)
        self.spatial_features = SpatialFeatures(config)
        self.connectivity = ConnectivityFeatures(config)

        # Feature selection
        self.enabled_features = set(config.feature_types)

        # Performance tracking
        self.extraction_times = {}

        logger.info(
            f"FeatureExtractor initialized with features: {self.enabled_features}"
        )

    async def initialize(self) -> None:
        """Initialize all feature extraction components."""
        # Initialize components that need setup
        if "connectivity" in self.enabled_features:
            await self.connectivity.initialize()

        logger.info("Feature extractor initialization complete")

    async def extract_features(
        self, data: np.ndarray, quality_score: float = 1.0
    ) -> Dict[str, np.ndarray]:
        """Extract all enabled features from signal data.

        Args:
            data: Preprocessed signal data (channels x samples)
            quality_score: Signal quality score (0-1) for adaptive extraction

        Returns:
            Dictionary of feature_name -> feature_array
        """
        features = {}

        try:
            # Parallel feature extraction for efficiency
            tasks = []

            if "time_domain" in self.enabled_features:
                tasks.append(self._extract_time_features(data, quality_score))

            if "frequency_domain" in self.enabled_features:
                tasks.append(self._extract_frequency_features(data, quality_score))

            if "time_frequency" in self.enabled_features:
                tasks.append(self._extract_time_frequency_features(data, quality_score))

            if "spatial" in self.enabled_features:
                tasks.append(self._extract_spatial_features(data, quality_score))

            if "connectivity" in self.enabled_features:
                tasks.append(self._extract_connectivity_features(data, quality_score))

            # Execute all feature extractions in parallel
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Merge results
                for result in results:
                    if isinstance(result, dict):
                        features.update(result)
                    elif isinstance(result, Exception):
                        logger.error(f"Feature extraction error: {str(result)}")

            # Log extraction performance
            total_features = sum(
                len(v) if isinstance(v, dict) else v.shape[-1]
                for v in features.values()
                if v is not None
            )
            logger.debug(
                f"Extracted {total_features} features from {len(features)} categories"
            )

            return features

        except Exception as e:
            logger.error(f"Error in feature extraction: {str(e)}")
            return features

    async def _extract_time_features(
        self, data: np.ndarray, quality_score: float
    ) -> Dict[str, np.ndarray]:
        """Extract time-domain features.

        Args:
            data: Signal data
            quality_score: Quality score

        Returns:
            Dictionary of time-domain features
        """
        start_time = time.perf_counter()
        features = {}

        try:
            # Statistical features
            stat_features = await self.time_domain.extract_statistical_features(data)
            features.update(stat_features)

            # Complexity features (only if good quality)
            if quality_score > 0.7:
                complexity_features = (
                    await self.time_domain.extract_complexity_features(data)
                )
                features.update(complexity_features)

            # Amplitude features
            amp_features = await self.time_domain.extract_amplitude_features(data)
            features.update(amp_features)

            # Temporal features
            temp_features = await self.time_domain.extract_temporal_features(data)
            features.update(temp_features)

            self.extraction_times["time_domain"] = (
                time.perf_counter() - start_time
            ) * 1000

        except Exception as e:
            logger.error(f"Error extracting time-domain features: {str(e)}")

        return features

    async def _extract_frequency_features(
        self, data: np.ndarray, quality_score: float
    ) -> Dict[str, np.ndarray]:
        """Extract frequency-domain features.

        Args:
            data: Signal data
            quality_score: Quality score

        Returns:
            Dictionary of frequency-domain features
        """
        start_time = time.perf_counter()
        features = {}

        try:
            # Define frequency bands
            freq_bands = {
                "delta": (0.5, 4),
                "theta": (4, 8),
                "alpha": (8, 13),
                "beta": (13, 30),
                "gamma": (30, 100),
            }

            # Power spectral density features
            psd_features = await self.frequency_domain.extract_power_spectral_density(
                data, freq_bands
            )
            features.update(psd_features)

            # Spectral entropy (if good quality)
            if quality_score > 0.6:
                entropy_features = await self.frequency_domain.extract_spectral_entropy(
                    data
                )
                features["spectral_entropy"] = entropy_features

            # Phase features
            phase_features = await self.frequency_domain.extract_phase_features(data)
            features.update(phase_features)

            self.extraction_times["frequency_domain"] = (
                time.perf_counter() - start_time
            ) * 1000

        except Exception as e:
            logger.error(f"Error extracting frequency-domain features: {str(e)}")

        return features

    async def _extract_time_frequency_features(
        self, data: np.ndarray, quality_score: float
    ) -> Dict[str, np.ndarray]:
        """Extract time-frequency features.

        Args:
            data: Signal data
            quality_score: Quality score

        Returns:
            Dictionary of time-frequency features
        """
        start_time = time.perf_counter()
        features = {}

        try:
            # Wavelet features
            wavelet_features = await self.time_frequency.extract_wavelet_features(
                data, wavelet_type="db4"
            )
            features.update(wavelet_features)

            # Morlet wavelet features for specific frequencies
            if quality_score > 0.7:
                frequencies = [10, 20, 30]  # Alpha, beta peaks
                morlet_features = await self.time_frequency.extract_morlet_features(
                    data, frequencies
                )
                features.update(morlet_features)

            # Hilbert transform features
            hilbert_features = await self.time_frequency.extract_hilbert_features(data)
            features.update(hilbert_features)

            self.extraction_times["time_frequency"] = (
                time.perf_counter() - start_time
            ) * 1000

        except Exception as e:
            logger.error(f"Error extracting time-frequency features: {str(e)}")

        return features

    async def _extract_spatial_features(
        self, data: np.ndarray, quality_score: float
    ) -> Dict[str, np.ndarray]:
        """Extract spatial features.

        Args:
            data: Signal data
            quality_score: Quality score

        Returns:
            Dictionary of spatial features
        """
        start_time = time.perf_counter()
        features = {}

        try:
            # Only extract spatial features if enough channels and good quality
            if data.shape[0] >= 4 and quality_score > 0.6:
                # Common spatial patterns (if labels available)
                # Note: CSP requires labeled data, so skipping for now

                # Spatial complexity
                spatial_complexity = (
                    await self.spatial_features.extract_spatial_complexity(data)
                )
                features["spatial_complexity"] = spatial_complexity

                # Channel correlation features
                correlation_features = (
                    await self.spatial_features.extract_correlation_features(data)
                )
                features.update(correlation_features)

            self.extraction_times["spatial"] = (time.perf_counter() - start_time) * 1000

        except Exception as e:
            logger.error(f"Error extracting spatial features: {str(e)}")

        return features

    async def _extract_connectivity_features(
        self, data: np.ndarray, quality_score: float
    ) -> Dict[str, np.ndarray]:
        """Extract connectivity features.

        Args:
            data: Signal data
            quality_score: Quality score

        Returns:
            Dictionary of connectivity features
        """
        start_time = time.perf_counter()
        features = {}

        try:
            # Only extract connectivity if enough channels and excellent quality
            if data.shape[0] >= 8 and quality_score > 0.8:
                # Coherence features
                coherence_features = await self.connectivity.extract_coherence_features(
                    data, freq_bands={"alpha": (8, 13), "beta": (13, 30)}
                )
                features.update(coherence_features)

                # Phase-amplitude coupling
                pac_features = await self.connectivity.extract_phase_amplitude_coupling(
                    data, phase_freq=(4, 8), amp_freq=(30, 50)
                )
                features["phase_amplitude_coupling"] = pac_features

            self.extraction_times["connectivity"] = (
                time.perf_counter() - start_time
            ) * 1000

        except Exception as e:
            logger.error(f"Error extracting connectivity features: {str(e)}")

        return features

    def get_feature_info(self) -> Dict[str, Any]:
        """Get information about available features.

        Returns:
            Dictionary with feature information
        """
        info = {
            "enabled_features": list(self.enabled_features),
            "available_features": [
                "time_domain",
                "frequency_domain",
                "time_frequency",
                "spatial",
                "connectivity",
            ],
            "extraction_times_ms": self.extraction_times,
            "feature_descriptions": {
                "time_domain": "Statistical, complexity, amplitude, and temporal features",
                "frequency_domain": "Power spectral density, spectral entropy, phase features",
                "time_frequency": "Wavelet transforms, Morlet wavelets, Hilbert transform",
                "spatial": "Spatial complexity, channel correlations",
                "connectivity": "Coherence, phase-amplitude coupling, network metrics",
            },
        }

        return info

    def update_config(self, params: Dict[str, Any]) -> None:
        """Update feature extraction configuration.

        Args:
            params: Parameters to update
        """
        if "feature_types" in params:
            self.enabled_features = set(params["feature_types"])
            logger.info(f"Updated enabled features: {self.enabled_features}")

        # Update component configurations
        self.time_domain.update_config(params)
        self.frequency_domain.update_config(params)
        self.time_frequency.update_config(params)
        self.spatial_features.update_config(params)
        self.connectivity.update_config(params)

    async def cleanup(self) -> None:
        """Cleanup feature extraction resources."""
        # Cleanup components
        await self.connectivity.cleanup()

        # Clear timing data
        self.extraction_times.clear()

        logger.info("Feature extractor cleanup complete")
