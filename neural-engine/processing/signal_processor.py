"""Advanced Signal Processor - Main orchestrator for signal processing pipeline.

This module coordinates all signal processing operations including preprocessing,
feature extraction, and real-time processing for BCI neural signals.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import time

from .preprocessing import PreprocessingPipeline
from .features import FeatureExtractor
from .streaming import StreamProcessor, BufferManager, RealTimeQualityMonitor

logger = logging.getLogger(__name__)


class ProcessingStage(Enum):
    """Signal processing stages."""

    PREPROCESSING = "preprocessing"
    FEATURE_EXTRACTION = "feature_extraction"
    QUALITY_ASSESSMENT = "quality_assessment"
    STREAMING = "streaming"


@dataclass
class ProcessingConfig:
    """Configuration for signal processing pipeline."""

    # Basic parameters
    sampling_rate: float
    num_channels: int
    channel_names: List[str] = field(default_factory=list)

    # Window parameters
    window_size: float = 1.0  # seconds
    overlap: float = 0.5  # percentage (0-1)

    # Processing steps
    preprocessing_steps: List[str] = field(
        default_factory=lambda: [
            "notch_filter",
            "bandpass_filter",
            "artifact_removal",
            "channel_repair",
            "spatial_filter",
        ]
    )

    # Feature extraction
    feature_types: List[str] = field(
        default_factory=lambda: ["time_domain", "frequency_domain", "time_frequency"]
    )

    # Quality parameters
    quality_threshold: float = 0.7  # 0-1 scale
    adaptive_processing: bool = True

    # Performance parameters
    use_gpu: bool = False
    parallel_channels: bool = True
    max_latency_ms: float = 20.0

    # Filter parameters
    notch_frequencies: List[float] = field(default_factory=lambda: [50.0, 100.0])  # Hz
    bandpass_low: float = 0.5  # Hz
    bandpass_high: float = 100.0  # Hz
    filter_order: int = 4

    # Artifact removal parameters
    artifact_methods: List[str] = field(default_factory=lambda: ["ica", "regression"])
    ica_components: Optional[int] = None
    eog_channels: List[int] = field(default_factory=list)

    # Spatial filtering
    spatial_filter_type: str = "car"  # common average reference
    laplacian_radius: float = 3.0  # cm

    def validate(self) -> bool:
        """Validate configuration parameters."""
        if self.sampling_rate <= 0:
            raise ValueError("Sampling rate must be positive")
        if self.num_channels <= 0:
            raise ValueError("Number of channels must be positive")
        if not 0 <= self.overlap < 1:
            raise ValueError("Overlap must be between 0 and 1")
        if self.window_size <= 0:
            raise ValueError("Window size must be positive")
        if not 0 <= self.quality_threshold <= 1:
            raise ValueError("Quality threshold must be between 0 and 1")
        return True


@dataclass
class SignalQualityMetrics:
    """Signal quality assessment results."""

    overall_quality: float  # 0-1 score
    channel_quality: List[float]  # Quality score per channel
    noise_level: float  # RMS noise estimate
    snr_db: float  # Signal-to-noise ratio in dB

    # Artifact presence (0-1 probability)
    artifact_presence: Dict[str, float] = field(default_factory=dict)

    # Bad channels
    bad_channels: List[int] = field(default_factory=list)
    interpolated_channels: List[int] = field(default_factory=list)

    # Recommendations
    recommendations: List[str] = field(default_factory=list)

    # Timing
    timestamp: datetime = field(default_factory=datetime.utcnow)
    processing_time_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "overall_quality": self.overall_quality,
            "channel_quality": self.channel_quality,
            "noise_level": self.noise_level,
            "snr_db": self.snr_db,
            "artifact_presence": self.artifact_presence,
            "bad_channels": self.bad_channels,
            "interpolated_channels": self.interpolated_channels,
            "recommendations": self.recommendations,
            "timestamp": self.timestamp.isoformat(),
            "processing_time_ms": self.processing_time_ms,
        }


@dataclass
class ProcessedSignal:
    """Result of signal processing."""

    # Processed data
    preprocessed_data: np.ndarray
    features: Dict[str, np.ndarray]

    # Metadata
    original_shape: Tuple[int, int]
    sampling_rate: float

    # Quality metrics
    quality_metrics: SignalQualityMetrics

    # Processing info
    processing_stages: List[str]
    processing_time_ms: float

    # Session info
    session_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate processed signal."""
        if self.preprocessed_data.ndim != 2:
            raise ValueError("Preprocessed data must be 2D (channels x samples)")


@dataclass
class StreamProcessingResult:
    """Result of real-time stream processing."""

    chunk_id: int
    session_id: str
    timestamp: datetime

    # Processed chunk
    processed_chunk: np.ndarray
    chunk_features: Dict[str, np.ndarray]

    # Quality for this chunk
    chunk_quality: SignalQualityMetrics

    # Timing info
    latency_ms: float
    processing_time_ms: float

    # Continuity info
    samples_processed: int
    samples_dropped: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "chunk_id": self.chunk_id,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
            "chunk_shape": self.processed_chunk.shape,
            "features_computed": list(self.chunk_features.keys()),
            "quality": self.chunk_quality.to_dict(),
            "latency_ms": self.latency_ms,
            "processing_time_ms": self.processing_time_ms,
            "samples_processed": self.samples_processed,
            "samples_dropped": self.samples_dropped,
        }


class AdvancedSignalProcessor:
    """Main signal processing orchestrator for BCI neural signals."""

    def __init__(self, config: ProcessingConfig):
        """Initialize signal processor with configuration.

        Args:
            config: Processing configuration parameters
        """
        # Validate configuration
        config.validate()
        self.config = config

        # Initialize components
        self.preprocessor = PreprocessingPipeline(config)
        self.feature_extractor = FeatureExtractor(config)
        self.quality_monitor = RealTimeQualityMonitor(config)

        # Stream processing
        self.stream_processors: Dict[str, StreamProcessor] = {}
        self.buffer_managers: Dict[str, BufferManager] = {}

        # Performance tracking
        self.processing_stats = {
            "total_samples_processed": 0,
            "total_processing_time_ms": 0.0,
            "average_latency_ms": 0.0,
            "max_latency_ms": 0.0,
            "quality_scores": [],
        }

        # State
        self.is_initialized = False
        self._lock = asyncio.Lock()

        logger.info(
            f"AdvancedSignalProcessor initialized with {config.num_channels} channels "
            f"at {config.sampling_rate}Hz"
        )

    async def initialize(self) -> None:
        """Initialize all processing components."""
        async with self._lock:
            if self.is_initialized:
                return

            # Initialize preprocessing pipeline
            await self.preprocessor.initialize()

            # Initialize feature extractor
            await self.feature_extractor.initialize()

            # Initialize quality monitor
            await self.quality_monitor.initialize()

            self.is_initialized = True
            logger.info("Signal processor initialization complete")

    async def process_signal_batch(
        self, signal_data: np.ndarray, metadata: Optional[Dict[str, Any]] = None
    ) -> ProcessedSignal:
        """Process a batch of signal data through the complete pipeline.

        Args:
            signal_data: Raw signal data (channels x samples)
            metadata: Optional metadata about the signal

        Returns:
            ProcessedSignal with preprocessed data, features, and quality metrics
        """
        if not self.is_initialized:
            await self.initialize()

        start_time = time.perf_counter()

        # Validate input
        if signal_data.ndim != 2:
            raise ValueError("Signal data must be 2D (channels x samples)")

        if signal_data.shape[0] != self.config.num_channels:
            raise ValueError(
                f"Expected {self.config.num_channels} channels, "
                f"got {signal_data.shape[0]}"
            )

        original_shape = signal_data.shape
        processing_stages = []

        try:
            # Step 1: Quality assessment on raw signal
            logger.debug("Assessing raw signal quality...")
            raw_quality = await self.quality_monitor.assess_signal_quality(signal_data)
            processing_stages.append("quality_assessment_raw")

            # Step 2: Preprocessing
            logger.debug("Running preprocessing pipeline...")
            preprocessed_data, preprocessing_info = await self.preprocessor.process(
                signal_data, quality_metrics=raw_quality
            )
            processing_stages.extend(preprocessing_info["stages_applied"])

            # Step 3: Post-preprocessing quality assessment
            logger.debug("Assessing preprocessed signal quality...")
            processed_quality = await self.quality_monitor.assess_signal_quality(
                preprocessed_data
            )
            processing_stages.append("quality_assessment_processed")

            # Step 4: Feature extraction
            logger.debug("Extracting features...")
            features = await self.feature_extractor.extract_features(
                preprocessed_data, quality_score=processed_quality.overall_quality
            )
            processing_stages.append("feature_extraction")

            # Calculate processing time
            processing_time_ms = (time.perf_counter() - start_time) * 1000

            # Update quality metrics with processing time
            processed_quality.processing_time_ms = processing_time_ms

            # Update stats
            self._update_processing_stats(
                signal_data.shape[1],
                processing_time_ms,
                processed_quality.overall_quality,
            )

            # Create result
            result = ProcessedSignal(
                preprocessed_data=preprocessed_data,
                features=features,
                original_shape=original_shape,
                sampling_rate=self.config.sampling_rate,
                quality_metrics=processed_quality,
                processing_stages=processing_stages,
                processing_time_ms=processing_time_ms,
                session_id=metadata.get("session_id") if metadata else None,
            )

            logger.info(
                f"Batch processing complete: {original_shape[1]} samples in "
                f"{processing_time_ms:.2f}ms, quality: {processed_quality.overall_quality:.2f}"
            )

            return result

        except Exception as e:
            logger.error(f"Error in signal batch processing: {str(e)}")
            raise

    async def setup_real_time_pipeline(
        self, session_id: str, stream_info: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Setup real-time processing pipeline for a streaming session.

        Args:
            session_id: Unique session identifier
            stream_info: Optional stream metadata

        Returns:
            True if setup successful
        """
        if not self.is_initialized:
            await self.initialize()

        try:
            # Calculate buffer size in samples
            window_samples = int(self.config.window_size * self.config.sampling_rate)
            overlap_samples = int(window_samples * self.config.overlap)

            # Create buffer manager
            buffer_manager = BufferManager(
                window_size=window_samples,
                overlap=overlap_samples,
                num_channels=self.config.num_channels,
            )

            # Create stream processor
            stream_processor = StreamProcessor(
                config=self.config,
                preprocessor=self.preprocessor,
                feature_extractor=self.feature_extractor,
                quality_monitor=self.quality_monitor,
                buffer_manager=buffer_manager,
            )

            # Initialize stream processor
            await stream_processor.initialize()

            # Store in active sessions
            async with self._lock:
                self.stream_processors[session_id] = stream_processor
                self.buffer_managers[session_id] = buffer_manager

            logger.info(f"Real-time pipeline setup complete for session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error setting up real-time pipeline: {str(e)}")
            return False

    async def process_stream_chunk(
        self, chunk: np.ndarray, session_id: str
    ) -> StreamProcessingResult:
        """Process a chunk of streaming data in real-time.

        Args:
            chunk: Data chunk (channels x samples)
            session_id: Session identifier

        Returns:
            StreamProcessingResult with processed chunk and features
        """
        # Get stream processor
        stream_processor = self.stream_processors.get(session_id)
        if not stream_processor:
            raise ValueError(f"No active stream processor for session {session_id}")

        # Process chunk
        result = await stream_processor.process_chunk(chunk, session_id)

        # Update global stats
        self._update_processing_stats(
            chunk.shape[1],
            result.processing_time_ms,
            result.chunk_quality.overall_quality,
        )

        return result

    async def teardown_real_time_pipeline(self, session_id: str) -> bool:
        """Teardown real-time processing pipeline.

        Args:
            session_id: Session identifier

        Returns:
            True if teardown successful
        """
        try:
            async with self._lock:
                # Get processors
                stream_processor = self.stream_processors.get(session_id)
                buffer_manager = self.buffer_managers.get(session_id)

                if stream_processor:
                    # Cleanup stream processor
                    await stream_processor.cleanup()
                    del self.stream_processors[session_id]

                if buffer_manager:
                    # Cleanup buffer manager
                    buffer_manager.reset()
                    del self.buffer_managers[session_id]

            logger.info(
                f"Real-time pipeline teardown complete for session {session_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Error tearing down real-time pipeline: {str(e)}")
            return False

    def update_processing_parameters(
        self, params: Dict[str, Any], session_id: Optional[str] = None
    ) -> bool:
        """Update processing parameters dynamically.

        Args:
            params: Parameters to update
            session_id: Optional session ID for stream-specific updates

        Returns:
            True if update successful
        """
        try:
            # Update global config
            for key, value in params.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)

            # Update component configurations
            self.preprocessor.update_config(params)
            self.feature_extractor.update_config(params)
            self.quality_monitor.update_config(params)

            # Update stream processor if session specified
            if session_id and session_id in self.stream_processors:
                self.stream_processors[session_id].update_parameters(params)

            logger.info(f"Processing parameters updated: {list(params.keys())}")
            return True

        except Exception as e:
            logger.error(f"Error updating processing parameters: {str(e)}")
            return False

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing performance statistics.

        Returns:
            Dictionary of performance metrics
        """
        stats = self.processing_stats.copy()

        # Add active session info
        stats["active_sessions"] = len(self.stream_processors)
        stats["active_session_ids"] = list(self.stream_processors.keys())

        # Calculate quality statistics
        if stats["quality_scores"]:
            stats["average_quality"] = np.mean(stats["quality_scores"])
            stats["quality_std"] = np.std(stats["quality_scores"])
            stats["min_quality"] = np.min(stats["quality_scores"])
            stats["max_quality"] = np.max(stats["quality_scores"])

        return stats

    def get_processing_latency(self, session_id: Optional[str] = None) -> float:
        """Get current processing latency in milliseconds.

        Args:
            session_id: Optional session ID for session-specific latency

        Returns:
            Latency in milliseconds
        """
        if session_id and session_id in self.stream_processors:
            return self.stream_processors[session_id].get_latency()

        return self.processing_stats["average_latency_ms"]

    def _update_processing_stats(
        self, samples: int, processing_time_ms: float, quality_score: float
    ) -> None:
        """Update internal processing statistics.

        Args:
            samples: Number of samples processed
            processing_time_ms: Processing time in milliseconds
            quality_score: Signal quality score (0-1)
        """
        self.processing_stats["total_samples_processed"] += samples
        self.processing_stats["total_processing_time_ms"] += processing_time_ms

        # Update average latency
        total_samples = self.processing_stats["total_samples_processed"]
        if total_samples > 0:
            self.processing_stats["average_latency_ms"] = self.processing_stats[
                "total_processing_time_ms"
            ] / (total_samples / self.config.sampling_rate / 1000)

        # Update max latency
        if processing_time_ms > self.processing_stats["max_latency_ms"]:
            self.processing_stats["max_latency_ms"] = processing_time_ms

        # Store quality scores (keep last 1000)
        self.processing_stats["quality_scores"].append(quality_score)
        if len(self.processing_stats["quality_scores"]) > 1000:
            self.processing_stats["quality_scores"].pop(0)

    async def cleanup(self) -> None:
        """Cleanup all resources."""
        try:
            # Teardown all active sessions
            session_ids = list(self.stream_processors.keys())
            for session_id in session_ids:
                await self.teardown_real_time_pipeline(session_id)

            # Cleanup components
            await self.preprocessor.cleanup()
            await self.feature_extractor.cleanup()
            await self.quality_monitor.cleanup()

            self.is_initialized = False
            logger.info("Signal processor cleanup complete")

        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            raise

    def __str__(self) -> str:
        """String representation."""
        return (
            f"AdvancedSignalProcessor(channels={self.config.num_channels}, "
            f"sampling_rate={self.config.sampling_rate}Hz, "
            f"active_sessions={len(self.stream_processors)})"
        )

    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"AdvancedSignalProcessor(config={self.config}, "
            f"initialized={self.is_initialized}, "
            f"active_sessions={list(self.stream_processors.keys())})"
        )
