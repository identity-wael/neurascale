"""Stream Processor - Real-time signal processing with sliding windows.

This module implements real-time stream processing with buffering,
sliding windows, and continuous feature extraction.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
import numpy as np
from collections import deque
from datetime import datetime
import time
from dataclasses import dataclass, field
import threading

from .buffer_manager import BufferManager
from .signal_processor import AdvancedSignalProcessor

logger = logging.getLogger(__name__)


@dataclass
class StreamConfig:
    """Configuration for stream processing."""

    # Buffer settings
    buffer_size_seconds: float = 10.0
    window_size_seconds: float = 2.0
    window_overlap: float = 0.5  # 50% overlap

    # Processing settings
    process_interval_ms: int = 100  # Process every 100ms
    min_samples_to_process: int = 256

    # Quality monitoring
    quality_check_interval: float = 1.0  # seconds
    min_quality_score: float = 0.5

    # Performance settings
    max_processing_queue: int = 5
    drop_on_overflow: bool = True

    # Callbacks
    on_processed: Optional[Callable] = None
    on_quality_alert: Optional[Callable] = None
    on_buffer_overflow: Optional[Callable] = None


@dataclass
class StreamMetrics:
    """Metrics for stream processing performance."""

    samples_received: int = 0
    samples_processed: int = 0
    chunks_processed: int = 0
    chunks_dropped: int = 0

    avg_processing_time_ms: float = 0.0
    max_processing_time_ms: float = 0.0

    current_buffer_fill: float = 0.0  # percentage
    buffer_overflows: int = 0

    last_quality_score: float = 1.0
    quality_alerts: int = 0

    start_time: datetime = field(default_factory=datetime.utcnow)
    last_update: datetime = field(default_factory=datetime.utcnow)


class StreamProcessor:
    """Real-time stream processor for neural signals."""

    def __init__(self, signal_processor: AdvancedSignalProcessor, config: StreamConfig):
        """Initialize stream processor.

        Args:
            signal_processor: Signal processor instance
            config: Stream processing configuration
        """
        self.processor = signal_processor
        self.config = config

        # Buffer manager
        self.buffer_manager = BufferManager(
            max_duration=config.buffer_size_seconds,
            sampling_rate=signal_processor.config.sampling_rate,
        )

        # Processing state
        self.is_running = False
        self.processing_thread = None
        self.processing_queue = asyncio.Queue(maxsize=config.max_processing_queue)

        # Sliding window
        self.window_size = int(
            config.window_size_seconds * signal_processor.config.sampling_rate
        )
        self.window_step = int(self.window_size * (1 - config.window_overlap))

        # Metrics
        self.metrics = StreamMetrics()
        self._processing_times = deque(maxlen=100)

        # Locks
        self._buffer_lock = threading.Lock()
        self._metrics_lock = threading.Lock()

        # Session management
        self.current_session_id = None

        logger.info("StreamProcessor initialized")

    async def start_stream(self, session_id: str, stream_info: Dict[str, Any]) -> bool:
        """Start processing a new stream.

        Args:
            session_id: Unique session identifier
            stream_info: Stream metadata (channels, sampling rate, etc.)

        Returns:
            Success status
        """
        try:
            # Initialize session
            self.current_session_id = session_id

            # Create stream buffer
            buffer_created = await self.buffer_manager.create_stream_buffer(
                session_id, stream_info
            )

            if not buffer_created:
                logger.error(f"Failed to create buffer for session {session_id}")
                return False

            # Initialize processor for stream
            processor_ready = await self.processor.setup_real_time_pipeline(
                session_id, stream_info
            )

            if not processor_ready:
                logger.error(f"Failed to setup processor for session {session_id}")
                return False

            # Reset metrics
            self.metrics = StreamMetrics()

            # Start processing thread
            self.is_running = True
            self.processing_thread = threading.Thread(
                target=self._run_processing_loop, daemon=True
            )
            self.processing_thread.start()

            logger.info(f"Stream processing started for session {session_id}")

            # Start quality monitoring
            asyncio.create_task(self._monitor_quality())

            return True

        except Exception as e:
            logger.error(f"Error starting stream: {str(e)}")
            return False

    async def process_chunk(
        self, chunk: np.ndarray, timestamp: Optional[float] = None
    ) -> bool:
        """Process incoming data chunk.

        Args:
            chunk: Signal data chunk (channels x samples)
            timestamp: Optional timestamp for synchronization

        Returns:
            Success status
        """
        if not self.is_running or self.current_session_id is None:
            logger.warning("Stream processor not running")
            return False

        try:
            # Add to buffer
            with self._buffer_lock:
                success = await self.buffer_manager.add_samples(
                    self.current_session_id, chunk, timestamp
                )

            if not success:
                with self._metrics_lock:
                    self.metrics.buffer_overflows += 1

                if self.config.on_buffer_overflow:
                    await self.config.on_buffer_overflow(self.current_session_id)

                if self.config.drop_on_overflow:
                    logger.warning("Buffer overflow, dropping oldest samples")
                else:
                    logger.error("Buffer overflow, rejecting new samples")
                    return False

            # Update metrics
            with self._metrics_lock:
                self.metrics.samples_received += chunk.shape[1]
                self.metrics.last_update = datetime.utcnow()

            # Check if we have enough samples to process
            buffer = self.buffer_manager.get_stream_buffer(self.current_session_id)
            if buffer and buffer.sample_count >= self.config.min_samples_to_process:
                # Trigger processing
                await self._trigger_processing()

            return True

        except Exception as e:
            logger.error(f"Error processing chunk: {str(e)}")
            return False

    async def get_latest_features(
        self, feature_types: Optional[List[str]] = None
    ) -> Optional[Dict[str, Any]]:
        """Get the latest extracted features.

        Args:
            feature_types: Specific feature types to retrieve

        Returns:
            Dictionary of latest features or None
        """
        if self.current_session_id is None:
            return None

        # Get from processor's cache
        return await self.processor.get_cached_features(
            self.current_session_id, feature_types
        )

    async def stop_stream(self) -> Dict[str, Any]:
        """Stop stream processing and return final metrics.

        Returns:
            Final processing metrics
        """
        logger.info(f"Stopping stream processing for session {self.current_session_id}")

        # Stop processing
        self.is_running = False

        # Wait for processing thread to finish
        if self.processing_thread:
            self.processing_thread.join(timeout=5.0)

        # Process any remaining data
        if self.current_session_id:
            await self._process_remaining_data()

        # Get final metrics
        with self._metrics_lock:
            metrics_dict = {
                "session_id": self.current_session_id,
                "duration_seconds": (
                    self.metrics.last_update - self.metrics.start_time
                ).total_seconds(),
                "samples_received": self.metrics.samples_received,
                "samples_processed": self.metrics.samples_processed,
                "chunks_processed": self.metrics.chunks_processed,
                "chunks_dropped": self.metrics.chunks_dropped,
                "avg_processing_time_ms": self.metrics.avg_processing_time_ms,
                "max_processing_time_ms": self.metrics.max_processing_time_ms,
                "buffer_overflows": self.metrics.buffer_overflows,
                "quality_alerts": self.metrics.quality_alerts,
            }

        # Cleanup
        if self.current_session_id:
            await self.buffer_manager.remove_stream_buffer(self.current_session_id)
            await self.processor.cleanup_session(self.current_session_id)

        self.current_session_id = None

        return metrics_dict

    def _run_processing_loop(self) -> None:
        """Main processing loop (runs in separate thread)."""
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()

        while self.is_running:
            try:
                # Process at regular intervals
                loop.run_until_complete(self._process_windows())
                time.sleep(self.config.process_interval_ms / 1000.0)

            except Exception as e:
                logger.error(f"Error in processing loop: {str(e)}")

    async def _trigger_processing(self) -> None:
        """Trigger immediate processing of available data."""
        try:
            # Add processing request to queue
            if not self.processing_queue.full():
                await self.processing_queue.put(time.time())
        except Exception:
            pass

    async def _process_windows(self) -> None:
        """Process available windows from buffer."""
        if self.current_session_id is None:
            return

        buffer = self.buffer_manager.get_stream_buffer(self.current_session_id)
        if not buffer:
            return

        # Get available windows
        with self._buffer_lock:
            windows = await self.buffer_manager.get_windows(
                self.current_session_id, self.window_size, self.window_step
            )

        if not windows:
            return

        # Process each window
        for window_data, window_info in windows:
            start_time = time.perf_counter()

            try:
                # Process window
                result = await self.processor.process_stream_chunk(
                    window_data, self.current_session_id
                )

                if result and result.success:
                    # Update metrics
                    processing_time = (time.perf_counter() - start_time) * 1000
                    self._update_processing_metrics(
                        window_data.shape[1], processing_time, result.quality_score
                    )

                    # Callback with results
                    if self.config.on_processed:
                        await self.config.on_processed(
                            self.current_session_id, result, window_info
                        )
                else:
                    with self._metrics_lock:
                        self.metrics.chunks_dropped += 1

            except Exception as e:
                logger.error(f"Error processing window: {str(e)}")
                with self._metrics_lock:
                    self.metrics.chunks_dropped += 1

    async def _process_remaining_data(self) -> None:
        """Process any remaining data in buffer."""
        if self.current_session_id is None:
            return

        buffer = self.buffer_manager.get_stream_buffer(self.current_session_id)
        if not buffer or buffer.sample_count == 0:
            return

        # Get all remaining data
        with self._buffer_lock:
            remaining_data = await self.buffer_manager.get_samples(
                self.current_session_id, buffer.sample_count
            )

        if remaining_data is not None and remaining_data.shape[1] > 0:
            try:
                # Process as final batch
                result = await self.processor.process_stream_chunk(
                    remaining_data, self.current_session_id
                )

                if result and result.success:
                    self._update_processing_metrics(
                        remaining_data.shape[1],
                        0,  # Don't track time for final batch
                        result.quality_score,
                    )

            except Exception as e:
                logger.error(f"Error processing remaining data: {str(e)}")

    async def _monitor_quality(self) -> None:
        """Monitor signal quality periodically."""
        while self.is_running:
            try:
                await asyncio.sleep(self.config.quality_check_interval)

                if self.current_session_id:
                    # Get recent quality score
                    with self._metrics_lock:
                        quality_score = self.metrics.last_quality_score

                    # Check quality threshold
                    if quality_score < self.config.min_quality_score:
                        with self._metrics_lock:
                            self.metrics.quality_alerts += 1

                        if self.config.on_quality_alert:
                            await self.config.on_quality_alert(
                                self.current_session_id, quality_score
                            )

            except Exception as e:
                logger.error(f"Error in quality monitoring: {str(e)}")

    def _update_processing_metrics(
        self, samples_processed: int, processing_time_ms: float, quality_score: float
    ) -> None:
        """Update processing metrics.

        Args:
            samples_processed: Number of samples processed
            processing_time_ms: Processing time in milliseconds
            quality_score: Signal quality score
        """
        with self._metrics_lock:
            self.metrics.samples_processed += samples_processed
            self.metrics.chunks_processed += 1
            self.metrics.last_quality_score = quality_score

            # Update processing time statistics
            self._processing_times.append(processing_time_ms)
            self.metrics.avg_processing_time_ms = np.mean(self._processing_times)
            self.metrics.max_processing_time_ms = max(
                self.metrics.max_processing_time_ms, processing_time_ms
            )

            # Update buffer fill
            if self.current_session_id:
                buffer = self.buffer_manager.get_stream_buffer(self.current_session_id)
                if buffer:
                    max_samples = int(
                        self.config.buffer_size_seconds
                        * self.processor.config.sampling_rate
                    )
                    self.metrics.current_buffer_fill = (
                        buffer.sample_count / max_samples * 100
                    )

    def get_stream_metrics(self) -> Dict[str, Any]:
        """Get current stream processing metrics.

        Returns:
            Dictionary of current metrics
        """
        with self._metrics_lock:
            return {
                "is_running": self.is_running,
                "session_id": self.current_session_id,
                "samples_received": self.metrics.samples_received,
                "samples_processed": self.metrics.samples_processed,
                "chunks_processed": self.metrics.chunks_processed,
                "chunks_dropped": self.metrics.chunks_dropped,
                "avg_processing_time_ms": round(self.metrics.avg_processing_time_ms, 2),
                "max_processing_time_ms": round(self.metrics.max_processing_time_ms, 2),
                "buffer_fill_percent": round(self.metrics.current_buffer_fill, 1),
                "buffer_overflows": self.metrics.buffer_overflows,
                "quality_score": round(self.metrics.last_quality_score, 3),
                "quality_alerts": self.metrics.quality_alerts,
                "uptime_seconds": (
                    (datetime.utcnow() - self.metrics.start_time).total_seconds()
                    if self.is_running
                    else 0
                ),
            }

    def update_config(self, params: Dict[str, Any]) -> None:
        """Update stream processor configuration.

        Args:
            params: Parameters to update
        """
        if "window_size_seconds" in params:
            self.config.window_size_seconds = params["window_size_seconds"]
            self.window_size = int(
                params["window_size_seconds"] * self.processor.config.sampling_rate
            )

        if "window_overlap" in params:
            self.config.window_overlap = params["window_overlap"]
            self.window_step = int(self.window_size * (1 - params["window_overlap"]))

        if "process_interval_ms" in params:
            self.config.process_interval_ms = params["process_interval_ms"]

        if "quality_check_interval" in params:
            self.config.quality_check_interval = params["quality_check_interval"]

        if "min_quality_score" in params:
            self.config.min_quality_score = params["min_quality_score"]
