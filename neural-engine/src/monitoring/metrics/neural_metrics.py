"""
Neural processing performance metrics collection
"""

import time
import logging
from datetime import datetime
from typing import Dict, Optional
from dataclasses import dataclass
from collections import deque
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class NeuralMetrics:
    """Neural processing performance metrics"""

    signal_processing_latency: float  # milliseconds
    feature_extraction_time: float  # milliseconds
    model_inference_latency: float  # milliseconds
    data_quality_score: float  # 0-1
    processing_accuracy: float  # 0-1
    throughput_samples_per_sec: float
    timestamp: datetime

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for export"""
        return {
            "signal_processing_latency_ms": self.signal_processing_latency,
            "feature_extraction_time_ms": self.feature_extraction_time,
            "model_inference_latency_ms": self.model_inference_latency,
            "data_quality_score": self.data_quality_score,
            "processing_accuracy": self.processing_accuracy,
            "throughput_samples_per_sec": self.throughput_samples_per_sec,
        }


class NeuralMetricsCollector:
    """Collects and tracks neural processing metrics"""

    def __init__(self, history_size: int = 1000):
        """
        Initialize neural metrics collector

        Args:
            history_size: Number of historical metrics to keep
        """
        self.history_size = history_size

        # Metric histories
        self.signal_latency_history: deque = deque(maxlen=history_size)
        self.feature_time_history: deque = deque(maxlen=history_size)
        self.inference_latency_history: deque = deque(maxlen=history_size)
        self.quality_score_history: deque = deque(maxlen=history_size)
        self.accuracy_history: deque = deque(maxlen=history_size)
        self.throughput_history: deque = deque(maxlen=history_size)

        # Current batch metrics
        self._current_batch_start = time.time()
        self._samples_in_batch = 0

        # Performance timers
        self._signal_start_time: Optional[float] = None
        self._feature_start_time: Optional[float] = None
        self._inference_start_time: Optional[float] = None

        logger.info("Neural metrics collector initialized")

    def start_signal_processing(self) -> None:
        """Mark start of signal processing"""
        self._signal_start_time = time.time()

    def end_signal_processing(self) -> float:
        """
        Mark end of signal processing and record latency

        Returns:
            Processing latency in milliseconds
        """
        if self._signal_start_time is None:
            logger.warning("Signal processing end called without start")
            return 0.0

        latency_ms = (time.time() - self._signal_start_time) * 1000
        self.signal_latency_history.append(latency_ms)
        self._signal_start_time = None

        return latency_ms

    def start_feature_extraction(self) -> None:
        """Mark start of feature extraction"""
        self._feature_start_time = time.time()

    def end_feature_extraction(self) -> float:
        """
        Mark end of feature extraction and record time

        Returns:
            Feature extraction time in milliseconds
        """
        if self._feature_start_time is None:
            logger.warning("Feature extraction end called without start")
            return 0.0

        time_ms = (time.time() - self._feature_start_time) * 1000
        self.feature_time_history.append(time_ms)
        self._feature_start_time = None

        return time_ms

    def start_model_inference(self) -> None:
        """Mark start of model inference"""
        self._inference_start_time = time.time()

    def end_model_inference(self) -> float:
        """
        Mark end of model inference and record latency

        Returns:
            Inference latency in milliseconds
        """
        if self._inference_start_time is None:
            logger.warning("Model inference end called without start")
            return 0.0

        latency_ms = (time.time() - self._inference_start_time) * 1000
        self.inference_latency_history.append(latency_ms)
        self._inference_start_time = None

        return latency_ms

    def record_signal_latency(self, latency_ms: float, device_type: str) -> None:
        """
        Record signal processing latency

        Args:
            latency_ms: Latency in milliseconds
            device_type: Type of device (for categorization)
        """
        self.signal_latency_history.append(latency_ms)
        logger.debug(f"Signal latency recorded: {latency_ms}ms for {device_type}")

    def record_processing_throughput(self, samples_per_second: float) -> None:
        """
        Record processing throughput

        Args:
            samples_per_second: Number of samples processed per second
        """
        self.throughput_history.append(samples_per_second)
        self._samples_in_batch += int(samples_per_second)

    def record_feature_extraction_time(self, duration_ms: float) -> None:
        """
        Record feature extraction time

        Args:
            duration_ms: Feature extraction duration in milliseconds
        """
        self.feature_time_history.append(duration_ms)

    def record_model_inference_latency(self, model_id: str, latency_ms: float) -> None:
        """
        Record model inference latency

        Args:
            model_id: Model identifier
            latency_ms: Inference latency in milliseconds
        """
        self.inference_latency_history.append(latency_ms)
        logger.debug(f"Model {model_id} inference: {latency_ms}ms")

    def record_data_quality_score(self, session_id: str, quality: float) -> None:
        """
        Record data quality score

        Args:
            session_id: Current session ID
            quality: Quality score (0-1)
        """
        quality = max(0.0, min(1.0, quality))  # Clamp to [0, 1]
        self.quality_score_history.append(quality)

        if quality < 0.7:
            logger.warning(f"Low data quality in session {session_id}: {quality}")

    def record_processing_accuracy(self, accuracy: float) -> None:
        """
        Record processing accuracy

        Args:
            accuracy: Accuracy score (0-1)
        """
        accuracy = max(0.0, min(1.0, accuracy))  # Clamp to [0, 1]
        self.accuracy_history.append(accuracy)

    async def collect_current_metrics(self) -> NeuralMetrics:
        """
        Collect current neural processing metrics

        Returns:
            Current metrics snapshot
        """
        # Calculate averages from recent history
        signal_latency = (
            np.mean(list(self.signal_latency_history)[-10:])
            if self.signal_latency_history
            else 0.0
        )

        feature_time = (
            np.mean(list(self.feature_time_history)[-10:])
            if self.feature_time_history
            else 0.0
        )

        inference_latency = (
            np.mean(list(self.inference_latency_history)[-10:])
            if self.inference_latency_history
            else 0.0
        )

        quality_score = (
            np.mean(list(self.quality_score_history)[-10:])
            if self.quality_score_history
            else 1.0
        )

        accuracy = (
            np.mean(list(self.accuracy_history)[-10:]) if self.accuracy_history else 1.0
        )

        # Calculate throughput
        current_time = time.time()
        batch_duration = current_time - self._current_batch_start
        if batch_duration > 0:
            throughput = self._samples_in_batch / batch_duration
        else:
            throughput = 0.0

        # Reset batch counters
        self._current_batch_start = current_time
        self._samples_in_batch = 0

        return NeuralMetrics(
            signal_processing_latency=signal_latency,
            feature_extraction_time=feature_time,
            model_inference_latency=inference_latency,
            data_quality_score=quality_score,
            processing_accuracy=accuracy,
            throughput_samples_per_sec=throughput,
            timestamp=datetime.now(),
        )

    def get_metrics_summary(
        self, start_time: datetime, end_time: datetime
    ) -> Dict[str, float]:
        """
        Get metrics summary for time range

        Args:
            start_time: Start of time range
            end_time: End of time range

        Returns:
            Summary statistics
        """
        # For this implementation, we'll use all available history
        # In production, we'd filter by timestamp

        summary = {}

        # Signal processing latency stats
        if self.signal_latency_history:
            latencies = list(self.signal_latency_history)
            summary["avg_processing_latency"] = np.mean(latencies)
            summary["p95_processing_latency"] = np.percentile(latencies, 95)
            summary["max_processing_latency"] = np.max(latencies)

        # Feature extraction stats
        if self.feature_time_history:
            times = list(self.feature_time_history)
            summary["avg_feature_time"] = np.mean(times)
            summary["p95_feature_time"] = np.percentile(times, 95)

        # Inference latency stats
        if self.inference_latency_history:
            latencies = list(self.inference_latency_history)
            summary["avg_inference_latency"] = np.mean(latencies)
            summary["p95_inference_latency"] = np.percentile(latencies, 95)

        # Quality and accuracy
        if self.quality_score_history:
            summary["avg_data_quality"] = np.mean(list(self.quality_score_history))
            summary["min_data_quality"] = np.min(list(self.quality_score_history))

        if self.accuracy_history:
            summary["avg_processing_accuracy"] = np.mean(list(self.accuracy_history))

        # Throughput
        if self.throughput_history:
            summary["avg_throughput"] = np.mean(list(self.throughput_history))
            summary["max_throughput"] = np.max(list(self.throughput_history))

        return summary

    def get_latency_percentiles(self) -> Dict[str, float]:
        """
        Get latency percentiles for all metrics

        Returns:
            Dictionary of percentile values
        """
        percentiles = {}

        if self.signal_latency_history:
            latencies = list(self.signal_latency_history)
            percentiles["signal_p50"] = np.percentile(latencies, 50)
            percentiles["signal_p95"] = np.percentile(latencies, 95)
            percentiles["signal_p99"] = np.percentile(latencies, 99)

        if self.feature_time_history:
            times = list(self.feature_time_history)
            percentiles["feature_p50"] = np.percentile(times, 50)
            percentiles["feature_p95"] = np.percentile(times, 95)
            percentiles["feature_p99"] = np.percentile(times, 99)

        if self.inference_latency_history:
            latencies = list(self.inference_latency_history)
            percentiles["inference_p50"] = np.percentile(latencies, 50)
            percentiles["inference_p95"] = np.percentile(latencies, 95)
            percentiles["inference_p99"] = np.percentile(latencies, 99)

        return percentiles

    def reset_metrics(self) -> None:
        """Reset all metric histories"""
        self.signal_latency_history.clear()
        self.feature_time_history.clear()
        self.inference_latency_history.clear()
        self.quality_score_history.clear()
        self.accuracy_history.clear()
        self.throughput_history.clear()

        self._current_batch_start = time.time()
        self._samples_in_batch = 0

        logger.info("Neural metrics reset")
