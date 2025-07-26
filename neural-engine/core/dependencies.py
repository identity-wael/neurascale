"""Dependencies for dependency injection in FastAPI.

This module provides singleton instances and dependency functions
for the signal processing components.
"""

from typing import Optional
import logging

from ..processing.signal_processor import AdvancedSignalProcessor, ProcessingConfig
from ..processing.stream_processor import StreamProcessor, StreamConfig
from ..processing.quality_monitor import QualityMonitor, QualityThresholds
from ..processing.preprocessing.quality_assessment import QualityAssessment

logger = logging.getLogger(__name__)

# Singleton instances
_processor_instance: Optional[AdvancedSignalProcessor] = None
_stream_processor_instance: Optional[StreamProcessor] = None
_quality_monitor_instance: Optional[QualityMonitor] = None


def get_processor() -> AdvancedSignalProcessor:
    """Get or create signal processor instance.

    Returns:
        AdvancedSignalProcessor instance
    """
    global _processor_instance

    if _processor_instance is None:
        # Create default configuration
        config = ProcessingConfig(
            sampling_rate=1000.0,
            num_channels=32,
            preprocessing_steps=[
                "artifact_removal",
                "advanced_filtering",
                "channel_repair",
                "spatial_filtering",
                "quality_assessment",
            ],
            feature_types=[
                "time_domain",
                "frequency_domain",
                "time_frequency",
                "spatial",
                "connectivity",
            ],
        )

        _processor_instance = AdvancedSignalProcessor(config)
        logger.info("Created signal processor instance")

    return _processor_instance


def get_stream_processor() -> StreamProcessor:
    """Get or create stream processor instance.

    Returns:
        StreamProcessor instance
    """
    global _stream_processor_instance

    if _stream_processor_instance is None:
        # Get signal processor
        processor = get_processor()

        # Create stream configuration
        stream_config = StreamConfig(
            buffer_size_seconds=10.0,
            window_size_seconds=2.0,
            window_overlap=0.5,
            process_interval_ms=100,
            min_samples_to_process=256,
            quality_check_interval=1.0,
            min_quality_score=0.5,
        )

        _stream_processor_instance = StreamProcessor(processor, stream_config)
        logger.info("Created stream processor instance")

    return _stream_processor_instance


async def get_quality_monitor() -> QualityMonitor:
    """Get or create quality monitor instance.

    Returns:
        QualityMonitor instance
    """
    global _quality_monitor_instance

    if _quality_monitor_instance is None:
        # Get processor config
        processor = get_processor()

        # Create quality assessment
        quality_assessment = QualityAssessment(processor.config)

        # Create quality thresholds
        thresholds = QualityThresholds(
            min_overall_score=0.6,
            critical_overall_score=0.4,
            min_snr=5.0,
            critical_snr=3.0,
            max_noise_level=50.0,
            critical_noise_level=100.0,
            max_artifact_percentage=10.0,
            critical_artifact_percentage=20.0,
        )

        _quality_monitor_instance = QualityMonitor(quality_assessment, thresholds)
        logger.info("Created quality monitor instance")

    return _quality_monitor_instance


def reset_instances():
    """Reset all singleton instances.

    This is useful for testing or reconfiguration.
    """
    global _processor_instance, _stream_processor_instance, _quality_monitor_instance

    _processor_instance = None
    _stream_processor_instance = None
    _quality_monitor_instance = None

    logger.info("Reset all processing instances")


def update_processor_config(config: ProcessingConfig):
    """Update the processor configuration.

    Args:
        config: New processing configuration
    """
    global _processor_instance

    _processor_instance = AdvancedSignalProcessor(config)

    # Reset dependent instances
    global _stream_processor_instance, _quality_monitor_instance
    _stream_processor_instance = None
    _quality_monitor_instance = None

    logger.info("Updated processor configuration")
