"""
Real-time stream processor for neural data classification
"""

import asyncio
import time
from collections import deque
from typing import AsyncIterator, Dict, List, Set
import logging

import numpy as np

from .interfaces import BaseClassifier, BaseFeatureExtractor, BaseStreamProcessor
from .types import ClassificationResult, NeuralData
from .utils.buffer import CircularBuffer

logger = logging.getLogger(__name__)


class RealtimeClassificationProcessor(BaseStreamProcessor):
    """
    Main orchestrator for real-time classification pipeline.
    Manages multiple classifiers running concurrently on neural data streams.
    """

    def __init__(
        self, buffer_size_ms: float = 5000, classification_interval_ms: float = 100
    ):
        """
        Initialize the stream processor

        Args:
            buffer_size_ms: Size of circular buffer in milliseconds
            classification_interval_ms: How often to run classification
        """
        self.classifiers: Dict[str, BaseClassifier] = {}
        self.feature_extractors: Dict[str, BaseFeatureExtractor] = {}
        self.buffers: Dict[str, CircularBuffer] = {}
        self.active_streams: Set[str] = set()
        self.buffer_size_ms = buffer_size_ms
        self.classification_interval_ms = classification_interval_ms
        self._running = False

        # Performance tracking
        self.latency_buffer = deque(maxlen=1000)
        self.classification_count = 0
        self.error_count = 0

    async def process_stream(
        self, stream: AsyncIterator[NeuralData]
    ) -> AsyncIterator[ClassificationResult]:
        """
        Process neural data stream and yield classification results

        Args:
            stream: Async iterator of neural data

        Yields:
            Classification results from all active classifiers
        """
        stream_id = None
        buffer = None

        try:
            # Initialize stream processing
            async for data in stream:
                if stream_id is None:
                    stream_id = f"{data.device_id}_{int(time.time())}"
                    buffer = CircularBuffer(
                        channels=len(data.channels),
                        buffer_duration_ms=self.buffer_size_ms,
                        sampling_rate=data.sampling_rate,
                    )
                    self.buffers[stream_id] = buffer
                    self.active_streams.add(stream_id)
                    logger.info(f"Started processing stream {stream_id}")

                # Add data to buffer
                await buffer.add_data(data)

                # Check if it's time to classify
                if await self._should_classify(buffer):
                    # Run all classifiers concurrently
                    classification_tasks = []

                    for name, classifier in self.classifiers.items():
                        if name in self.feature_extractors:
                            task = self._classify_with_timing(
                                classifier, self.feature_extractors[name], buffer, name
                            )
                            classification_tasks.append(task)

                    if classification_tasks:
                        # Wait for all classifications to complete
                        results = await asyncio.gather(
                            *classification_tasks, return_exceptions=True
                        )

                        # Yield valid results
                        for result in results:
                            if isinstance(result, ClassificationResult):
                                self.classification_count += 1
                                yield result
                            elif isinstance(result, Exception):
                                self.error_count += 1
                                logger.error(f"Classification error: {result}")

        except Exception as e:
            logger.error(f"Stream processing error: {e}")
            raise
        finally:
            # Cleanup
            if stream_id:
                self.active_streams.discard(stream_id)
                if stream_id in self.buffers:
                    del self.buffers[stream_id]
                logger.info(f"Stopped processing stream {stream_id}")

    async def add_classifier(
        self,
        name: str,
        classifier: BaseClassifier,
        feature_extractor: BaseFeatureExtractor,
    ) -> None:
        """
        Add a classifier with its feature extractor to the pipeline

        Args:
            name: Unique name for the classifier
            classifier: Classifier instance
            feature_extractor: Feature extractor for this classifier
        """
        if name in self.classifiers:
            logger.warning(f"Replacing existing classifier: {name}")

        self.classifiers[name] = classifier
        self.feature_extractors[name] = feature_extractor
        logger.info(f"Added classifier: {name}")

    async def remove_classifier(self, name: str) -> None:
        """Remove a classifier from the pipeline"""
        if name in self.classifiers:
            del self.classifiers[name]
            del self.feature_extractors[name]
            logger.info(f"Removed classifier: {name}")

    def get_active_classifiers(self) -> List[str]:
        """Get list of active classifier names"""
        return list(self.classifiers.keys())

    async def _should_classify(self, buffer: CircularBuffer) -> bool:
        """Check if enough time has passed for classification"""
        if buffer.get_duration_ms() < self.classification_interval_ms:
            return False

        # Check if we have classified recently
        last_classification = getattr(buffer, "last_classification_time", 0)
        current_time = time.time() * 1000  # Convert to ms

        if current_time - last_classification >= self.classification_interval_ms:
            buffer.last_classification_time = current_time
            return True

        return False

    async def _classify_with_timing(
        self,
        classifier: BaseClassifier,
        feature_extractor: BaseFeatureExtractor,
        buffer: CircularBuffer,
        classifier_name: str,
    ) -> ClassificationResult:
        """Run classification with timing information"""
        start_time = time.time()

        try:
            # Get required window size
            window_size_ms = feature_extractor.get_required_window_size()

            # Get data window
            neural_data = await buffer.get_window(window_size_ms)
            if neural_data is None:
                raise ValueError(f"Insufficient data for {classifier_name}")

            # Extract features
            feature_start = time.time()
            features = await feature_extractor.extract_features(neural_data)
            feature_time = (time.time() - feature_start) * 1000

            # Classify
            classify_start = time.time()
            result = await classifier.classify(features)
            classify_time = (time.time() - classify_start) * 1000

            # Update timing information
            total_time = (time.time() - start_time) * 1000
            result.latency_ms = total_time

            if hasattr(result, "metadata") and result.metadata is not None:
                result.metadata["feature_extraction_ms"] = feature_time
                result.metadata["classification_ms"] = classify_time
                result.metadata["classifier_name"] = classifier_name

            # Track latency
            self.latency_buffer.append(total_time)

            return result

        except Exception as e:
            logger.error(f"Classification error in {classifier_name}: {e}")
            raise

    def get_performance_stats(self) -> Dict[str, float]:
        """Get performance statistics"""
        if not self.latency_buffer:
            return {
                "avg_latency_ms": 0,
                "p50_latency_ms": 0,
                "p95_latency_ms": 0,
                "p99_latency_ms": 0,
                "classification_rate_hz": 0,
                "error_rate": 0,
            }

        latencies = np.array(self.latency_buffer)

        return {
            "avg_latency_ms": float(np.mean(latencies)),
            "p50_latency_ms": float(np.percentile(latencies, 50)),
            "p95_latency_ms": float(np.percentile(latencies, 95)),
            "p99_latency_ms": float(np.percentile(latencies, 99)),
            "classification_rate_hz": self.classification_count / max(1, time.time()),
            "error_rate": self.error_count
            / max(1, self.classification_count + self.error_count),
        }

    async def shutdown(self):
        """Gracefully shutdown the processor"""
        logger.info("Shutting down stream processor")

        # Clear all buffers
        for buffer in self.buffers.values():
            buffer.clear()

        self.buffers.clear()
        self.active_streams.clear()

        logger.info("Stream processor shutdown complete")
