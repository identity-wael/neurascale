"""Advanced Signal Processing Module for NeuraScale Neural Engine.

This module provides real-time signal processing capabilities for BCI neural signals,
including artifact removal, feature extraction, and signal quality enhancement.
"""

from .signal_processor import (
    AdvancedSignalProcessor,
    ProcessingConfig,
    ProcessedSignal,
    StreamProcessingResult,
    SignalQualityMetrics,
)

from .stream_processor import StreamProcessor, StreamConfig, StreamMetrics

from .buffer_manager import BufferManager, StreamBuffer

from .quality_monitor import (
    QualityMonitor,
    QualityThresholds,
    QualityAlert,
    QualityTrend,
)

__all__ = [
    # Core processors
    "AdvancedSignalProcessor",
    "ProcessingConfig",
    "ProcessedSignal",
    "StreamProcessingResult",
    "SignalQualityMetrics",
    # Stream processing
    "StreamProcessor",
    "StreamConfig",
    "StreamMetrics",
    # Buffer management
    "BufferManager",
    "StreamBuffer",
    # Quality monitoring
    "QualityMonitor",
    "QualityThresholds",
    "QualityAlert",
    "QualityTrend",
]
