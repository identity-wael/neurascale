"""Preprocessing Pipeline - Orchestrates all preprocessing steps.

This module coordinates the preprocessing workflow including artifact removal,
filtering, channel repair, and spatial filtering.
"""

import logging
from typing import Dict, Optional, Any, Tuple
import numpy as np
import time

from .artifact_removal import ArtifactRemover
from .filtering import AdvancedFilters
from .channel_repair import ChannelRepair
from .spatial_filtering import SpatialFilters
from .quality_assessment import QualityAssessment

logger = logging.getLogger(__name__)


class PreprocessingPipeline:
    """Orchestrates preprocessing steps for neural signals."""

    def __init__(self, config: Any):
        """Initialize preprocessing pipeline.

        Args:
            config: Processing configuration
        """
        self.config = config

        # Initialize components
        self.artifact_remover = ArtifactRemover(config)
        self.filters = AdvancedFilters(config)
        self.channel_repair = ChannelRepair(config)
        self.spatial_filters = SpatialFilters(config)
        self.quality_assessment = QualityAssessment(config)

        # Processing state
        self.is_initialized = False
        self._preprocessing_cache = {}

        logger.info("PreprocessingPipeline initialized")

    async def initialize(self) -> None:
        """Initialize all preprocessing components."""
        if self.is_initialized:
            return

        # Initialize components that need setup
        await self.artifact_remover.initialize()
        await self.channel_repair.initialize()

        self.is_initialized = True
        logger.info("Preprocessing pipeline initialization complete")

    async def process(
        self, signal_data: np.ndarray, quality_metrics: Optional[Any] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Process signal through preprocessing pipeline.

        Args:
            signal_data: Raw signal data (channels x samples)
            quality_metrics: Optional quality metrics from initial assessment

        Returns:
            Tuple of (preprocessed_data, preprocessing_info)
        """
        if not self.is_initialized:
            await self.initialize()

        start_time = time.perf_counter()
        stages_applied = []
        processing_info = {
            "stages_applied": stages_applied,
            "artifacts_removed": {},
            "channels_repaired": [],
            "filters_applied": [],
            "timing": {},
        }

        # Work on a copy to preserve original
        data = signal_data.copy()

        try:
            # Step 1: Notch filtering (remove power line noise)
            if "notch_filter" in self.config.preprocessing_steps:
                stage_start = time.perf_counter()

                for freq in self.config.notch_frequencies:
                    data = await self._apply_notch_filter(data, freq)
                    processing_info["filters_applied"].append(f"notch_{freq}Hz")

                processing_info["timing"]["notch_filter"] = (
                    time.perf_counter() - stage_start
                ) * 1000
                stages_applied.append("notch_filter")
                logger.debug(
                    f"Applied notch filters at {self.config.notch_frequencies} Hz"
                )

            # Step 2: Bandpass filtering
            if "bandpass_filter" in self.config.preprocessing_steps:
                stage_start = time.perf_counter()

                data = await self._apply_bandpass_filter(
                    data, self.config.bandpass_low, self.config.bandpass_high
                )
                processing_info["filters_applied"].append(
                    f"bandpass_{self.config.bandpass_low}-{self.config.bandpass_high}Hz"
                )

                processing_info["timing"]["bandpass_filter"] = (
                    time.perf_counter() - stage_start
                ) * 1000
                stages_applied.append("bandpass_filter")
                logger.debug(
                    f"Applied bandpass filter {self.config.bandpass_low}-{self.config.bandpass_high} Hz"
                )

            # Step 3: Artifact removal
            if "artifact_removal" in self.config.preprocessing_steps:
                stage_start = time.perf_counter()

                data, artifacts_info = await self._remove_artifacts(data)
                processing_info["artifacts_removed"] = artifacts_info

                processing_info["timing"]["artifact_removal"] = (
                    time.perf_counter() - stage_start
                ) * 1000
                stages_applied.append("artifact_removal")
                logger.debug(f"Removed artifacts using {self.config.artifact_methods}")

            # Step 4: Channel repair
            if "channel_repair" in self.config.preprocessing_steps:
                stage_start = time.perf_counter()

                # Detect bad channels
                bad_channels = await self.channel_repair.detect_bad_channels(
                    data, quality_metrics=quality_metrics
                )

                if bad_channels:
                    # Repair bad channels
                    data = await self.channel_repair.interpolate_channels(
                        data,
                        bad_channels,
                        method=(
                            "spherical"
                            if len(self.config.channel_names) > 32
                            else "linear"
                        ),
                    )
                    processing_info["channels_repaired"] = bad_channels
                    logger.debug(f"Repaired {len(bad_channels)} bad channels")

                processing_info["timing"]["channel_repair"] = (
                    time.perf_counter() - stage_start
                ) * 1000
                stages_applied.append("channel_repair")

            # Step 5: Spatial filtering
            if "spatial_filter" in self.config.preprocessing_steps:
                stage_start = time.perf_counter()

                if self.config.spatial_filter_type == "car":
                    data = await self.spatial_filters.common_average_reference(
                        data,
                        exclude_channels=processing_info.get("channels_repaired", []),
                    )
                elif self.config.spatial_filter_type == "laplacian":
                    data = await self.spatial_filters.laplacian_filter(data)

                processing_info["timing"]["spatial_filter"] = (
                    time.perf_counter() - stage_start
                ) * 1000
                stages_applied.append(
                    f"spatial_filter_{self.config.spatial_filter_type}"
                )
                logger.debug(
                    f"Applied {self.config.spatial_filter_type} spatial filter"
                )

            # Calculate total preprocessing time
            total_time_ms = (time.perf_counter() - start_time) * 1000
            processing_info["timing"]["total"] = total_time_ms

            logger.info(
                f"Preprocessing complete in {total_time_ms:.2f}ms, "
                f"stages: {stages_applied}"
            )

            return data, processing_info

        except Exception as e:
            logger.error(f"Error in preprocessing pipeline: {str(e)}")
            raise

    async def _apply_notch_filter(
        self, data: np.ndarray, frequency: float
    ) -> np.ndarray:
        """Apply notch filter at specified frequency.

        Args:
            data: Signal data
            frequency: Notch frequency in Hz

        Returns:
            Filtered data
        """
        return await self.filters.notch_filter(
            data, frequency, sampling_rate=self.config.sampling_rate, quality_factor=30
        )

    async def _apply_bandpass_filter(
        self, data: np.ndarray, low_freq: float, high_freq: float
    ) -> np.ndarray:
        """Apply bandpass filter.

        Args:
            data: Signal data
            low_freq: Low cutoff frequency
            high_freq: High cutoff frequency

        Returns:
            Filtered data
        """
        return await self.filters.butterworth_bandpass(
            data,
            low_freq,
            high_freq,
            sampling_rate=self.config.sampling_rate,
            order=self.config.filter_order,
        )

    async def _remove_artifacts(
        self, data: np.ndarray
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Remove artifacts from signal.

        Args:
            data: Signal data

        Returns:
            Tuple of (cleaned_data, artifacts_info)
        """
        artifacts_info = {}
        cleaned_data = data.copy()

        # Apply artifact removal methods
        for method in self.config.artifact_methods:
            if method == "ica":
                # ICA-based artifact removal
                cleaned_data, ica_info = (
                    await self.artifact_remover.remove_artifacts_ica(
                        cleaned_data, n_components=self.config.ica_components
                    )
                )
                artifacts_info["ica"] = ica_info

            elif method == "regression" and self.config.eog_channels:
                # Regression-based EOG artifact removal
                cleaned_data, regression_info = (
                    await self.artifact_remover.remove_eog_regression(
                        cleaned_data, eog_channels=self.config.eog_channels
                    )
                )
                artifacts_info["regression"] = regression_info

        return cleaned_data, artifacts_info

    def update_config(self, params: Dict[str, Any]) -> None:
        """Update preprocessing configuration.

        Args:
            params: Parameters to update
        """
        # Update relevant parameters
        for key, value in params.items():
            if key in [
                "notch_frequencies",
                "bandpass_low",
                "bandpass_high",
                "filter_order",
                "spatial_filter_type",
                "preprocessing_steps",
            ]:
                setattr(self.config, key, value)

        # Update component configurations
        self.filters.update_config(params)
        self.artifact_remover.update_config(params)
        self.channel_repair.update_config(params)
        self.spatial_filters.update_config(params)

    async def cleanup(self) -> None:
        """Cleanup preprocessing resources."""
        # Cleanup components
        await self.artifact_remover.cleanup()
        await self.channel_repair.cleanup()

        # Clear cache
        self._preprocessing_cache.clear()

        self.is_initialized = False
        logger.info("Preprocessing pipeline cleanup complete")
