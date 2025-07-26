"""Preprocessing module for signal processing pipeline.

This module provides artifact removal, filtering, channel repair,
and spatial filtering capabilities for neural signals.
"""

from .preprocessing_pipeline import PreprocessingPipeline
from .artifact_removal import ArtifactRemover
from .filtering import AdvancedFilters
from .channel_repair import ChannelRepair
from .spatial_filtering import SpatialFilters
from .quality_assessment import QualityAssessment

__all__ = [
    "PreprocessingPipeline",
    "ArtifactRemover",
    "AdvancedFilters",
    "ChannelRepair",
    "SpatialFilters",
    "QualityAssessment",
]
