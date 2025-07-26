"""Neural processing metrics collection for NeuraScale Neural Engine.

This module collects and tracks neural processing performance metrics
including signal processing latency, data quality, and throughput.
"""

import time
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging

from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of neural metrics."""

    SIGNAL_PROCESSING = "signal_processing"
    FEATURE_EXTRACTION = "feature_extraction"
    MODEL_INFERENCE = "model_inference"
    DATA_QUALITY = "data_quality"
    THROUGHPUT = "throughput"
    LATENCY = "latency"


@dataclass
class NeuralMetrics:
    """Neural processing performance metrics."""

    # Timing metrics (milliseconds)
    signal_processing_latency: float
    feature_extraction_time: float
    model_inference_latency: float
    total_processing_time: float

    # Quality metrics (0-1 scores)
    data_quality_score: float
    processing_accuracy: float
    signal_quality: float

    # Throughput metrics
    samples_processed_per_second: float
    features_extracted_per_second: float
    predictions_per_second: float

    # Session information
    session_id: str
    device_id: Optional[str] = None
    model_id: Optional[str] = None

    # Metadata
    timestamp: datetime = field(default_factory=datetime.utcnow)
    processing_stage: str = "complete"
    error_count: int = 0
    warning_count: int = 0

    # Additional context
    channel_count: int = 0
    sampling_rate: float = 0.0
    window_size_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary format."""
        return {
            "signal_processing_latency_ms": self.signal_processing_latency,
            "feature_extraction_time_ms": self.feature_extraction_time,
            "model_inference_latency_ms": self.model_inference_latency,
            "total_processing_time_ms": self.total_processing_time,
            "data_quality_score": self.data_quality_score,
            "processing_accuracy": self.processing_accuracy,
            "signal_quality": self.signal_quality,
            "samples_per_second": self.samples_processed_per_second,
            "features_per_second": self.features_extracted_per_second,
            "predictions_per_second": self.predictions_per_second,
            "session_id": self.session_id,
            "device_id": self.device_id,
            "model_id": self.model_id,
            "timestamp": self.timestamp.isoformat(),
            "processing_stage": self.processing_stage,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "channel_count": self.channel_count,
            "sampling_rate_hz": self.sampling_rate,
            "window_size_ms": self.window_size_ms,
        }


@dataclass
class MetricAggregation:
    """Aggregated metrics over a time period."""

    count: int = 0
    sum: float = 0.0
    min: float = float("in")
    max: float = float("-in")
    mean: float = 0.0
    p50: float = 0.0
    p95: float = 0.0
    p99: float = 0.0

    def update(self, value: float) -> None:
        """Update aggregation with new value."""
        self.count += 1
        self.sum += value
        self.min = min(self.min, value)
        self.max = max(self.max, value)
        self.mean = self.sum / self.count


class NeuralMetricsCollector:
    """Collects and aggregates neural processing metrics."""

    def __init__(self, config):
        """Initialize neural metrics collector.

        Args:
            config: Monitoring configuration
        """
        self.config = config
        self.metrics_buffer: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.session_metrics: Dict[str, List[NeuralMetrics]] = defaultdict(list)
        self.aggregated_metrics: Dict[str, Dict[str, MetricAggregation]] = defaultdict(
            lambda: defaultdict(MetricAggregation)
        )

        # Timing tracking
        self._timing_stack: Dict[str, List[float]] = defaultdict(list)
        self._session_timers: Dict[str, Dict[str, float]] = defaultdict(dict)

        # Performance counters
        self.total_metrics_collected = 0
        self.collection_errors = 0

        logger.info("NeuralMetricsCollector initialized")

    def start_timing(self, session_id: str, metric_type: MetricType) -> None:
        """Start timing measurement for a processing stage.

        Args:
            session_id: Processing session identifier
            metric_type: Type of metric being timed
        """
        current_time = time.perf_counter()
        timer_key = f"{session_id}_{metric_type.value}"
        self._session_timers[session_id][metric_type.value] = current_time

    def end_timing(self, session_id: str, metric_type: MetricType) -> float:
        """End timing measurement and return duration.

        Args:
            session_id: Processing session identifier
            metric_type: Type of metric being timed

        Returns:
            Duration in milliseconds
        """
        current_time = time.perf_counter()
        timer_key = metric_type.value

        if (
            session_id in self._session_timers
            and timer_key in self._session_timers[session_id]
        ):
            start_time = self._session_timers[session_id][timer_key]
            duration_ms = (current_time - start_time) * 1000  # Convert to milliseconds

            # Clean up timer
            del self._session_timers[session_id][timer_key]

            return duration_ms
        else:
            logger.warning(f"No timer found for {session_id}:{timer_key}")
            return 0.0

    def record_signal_latency(
        self, latency_ms: float, device_type: str = "unknown"
    ) -> None:
        """Record signal processing latency.

        Args:
            latency_ms: Latency in milliseconds
            device_type: Type of device
        """
        try:
            metric_key = f"signal_latency_{device_type}"
            self.metrics_buffer[metric_key].append(
                {
                    "value": latency_ms,
                    "timestamp": datetime.utcnow(),
                    "device_type": device_type,
                }
            )

            # Update aggregation
            self.aggregated_metrics[device_type]["signal_latency"].update(latency_ms)

        except Exception as e:
            logger.error(f"Failed to record signal latency: {str(e)}")
            self.collection_errors += 1

    def record_processing_throughput(
        self, samples_per_second: float, session_id: str = "default"
    ) -> None:
        """Record processing throughput.

        Args:
            samples_per_second: Samples processed per second
            session_id: Processing session identifier
        """
        try:
            self.metrics_buffer["throughput"].append(
                {
                    "value": samples_per_second,
                    "timestamp": datetime.utcnow(),
                    "session_id": session_id,
                }
            )

            # Update aggregation
            self.aggregated_metrics[session_id]["throughput"].update(samples_per_second)

        except Exception as e:
            logger.error(f"Failed to record throughput: {str(e)}")
            self.collection_errors += 1

    def record_feature_extraction_time(
        self, duration_ms: float, session_id: str = "default"
    ) -> None:
        """Record feature extraction duration.

        Args:
            duration_ms: Duration in milliseconds
            session_id: Processing session identifier
        """
        try:
            self.metrics_buffer["feature_extraction"].append(
                {
                    "value": duration_ms,
                    "timestamp": datetime.utcnow(),
                    "session_id": session_id,
                }
            )

            # Update aggregation
            self.aggregated_metrics[session_id]["feature_extraction"].update(
                duration_ms
            )

        except Exception as e:
            logger.error(f"Failed to record feature extraction time: {str(e)}")
            self.collection_errors += 1

    def record_model_inference_latency(
        self, model_id: str, latency_ms: float, session_id: str = "default"
    ) -> None:
        """Record model inference latency.

        Args:
            model_id: Model identifier
            latency_ms: Latency in milliseconds
            session_id: Processing session identifier
        """
        try:
            metric_key = f"inference_{model_id}"
            self.metrics_buffer[metric_key].append(
                {
                    "value": latency_ms,
                    "timestamp": datetime.utcnow(),
                    "model_id": model_id,
                    "session_id": session_id,
                }
            )

            # Update aggregation
            self.aggregated_metrics[model_id]["inference_latency"].update(latency_ms)

        except Exception as e:
            logger.error(f"Failed to record inference latency: {str(e)}")
            self.collection_errors += 1

    def record_data_quality_score(
        self, session_id: str, quality: float, details: Optional[Dict] = None
    ) -> None:
        """Record data quality assessment.

        Args:
            session_id: Processing session identifier
            quality: Quality score (0-1)
            details: Optional quality details
        """
        try:
            if not 0.0 <= quality <= 1.0:
                logger.warning(f"Invalid quality score: {quality}")
                quality = max(0.0, min(1.0, quality))

            self.metrics_buffer["data_quality"].append(
                {
                    "value": quality,
                    "timestamp": datetime.utcnow(),
                    "session_id": session_id,
                    "details": details or {},
                }
            )

            # Update aggregation
            self.aggregated_metrics[session_id]["data_quality"].update(quality)

        except Exception as e:
            logger.error(f"Failed to record data quality: {str(e)}")
            self.collection_errors += 1

    async def collect_session_metrics(self, session_id: str) -> Optional[NeuralMetrics]:
        """Collect comprehensive metrics for a processing session.

        Args:
            session_id: Processing session identifier

        Returns:
            NeuralMetrics object or None if collection fails
        """
        try:
            # Get aggregated metrics for this session
            session_agg = self.aggregated_metrics.get(session_id, {})

            # Create metrics object with available data
            metrics = NeuralMetrics(
                session_id=session_id,
                signal_processing_latency=session_agg.get(
                    "signal_latency", MetricAggregation()
                ).mean,
                feature_extraction_time=session_agg.get(
                    "feature_extraction", MetricAggregation()
                ).mean,
                model_inference_latency=session_agg.get(
                    "inference_latency", MetricAggregation()
                ).mean,
                total_processing_time=self._calculate_total_processing_time(session_id),
                data_quality_score=session_agg.get(
                    "data_quality", MetricAggregation()
                ).mean
                or 0.0,
                processing_accuracy=self._calculate_processing_accuracy(session_id),
                signal_quality=self._calculate_signal_quality(session_id),
                samples_processed_per_second=session_agg.get(
                    "throughput", MetricAggregation()
                ).mean,
                features_extracted_per_second=self._calculate_feature_throughput(
                    session_id
                ),
                predictions_per_second=self._calculate_prediction_throughput(
                    session_id
                ),
            )

            # Store metrics
            self.session_metrics[session_id].append(metrics)
            self.total_metrics_collected += 1

            return metrics

        except Exception as e:
            logger.error(
                f"Failed to collect session metrics for {session_id}: {str(e)}"
            )
            self.collection_errors += 1
            return None

    def get_metric_summary(
        self, metric_type: str, time_window_minutes: int = 60
    ) -> Dict[str, Any]:
        """Get summary statistics for a metric type.

        Args:
            metric_type: Type of metric to summarize
            time_window_minutes: Time window for summary

        Returns:
            Summary statistics dictionary
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)

            # Get recent metrics
            recent_metrics = []
            if metric_type in self.metrics_buffer:
                for metric in self.metrics_buffer[metric_type]:
                    if metric["timestamp"] >= cutoff_time:
                        recent_metrics.append(metric["value"])

            if not recent_metrics:
                return {"count": 0, "message": "No recent metrics available"}

            # Calculate statistics
            values = np.array(recent_metrics)

            return {
                "count": len(values),
                "mean": float(np.mean(values)),
                "median": float(np.median(values)),
                "std": float(np.std(values)),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
                "p95": float(np.percentile(values, 95)),
                "p99": float(np.percentile(values, 99)),
                "time_window_minutes": time_window_minutes,
            }

        except Exception as e:
            logger.error(f"Failed to get metric summary for {metric_type}: {str(e)}")
            return {"error": str(e)}

    def get_session_history(
        self, session_id: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get metrics history for a session.

        Args:
            session_id: Processing session identifier
            limit: Maximum number of metrics to return

        Returns:
            List of metric dictionaries
        """
        try:
            session_history = self.session_metrics.get(session_id, [])

            # Return recent metrics (up to limit)
            recent_metrics = session_history[-limit:] if session_history else []

            return [metric.to_dict() for metric in recent_metrics]

        except Exception as e:
            logger.error(f"Failed to get session history for {session_id}: {str(e)}")
            return []

    def clear_session_metrics(self, session_id: str) -> bool:
        """Clear metrics for a specific session.

        Args:
            session_id: Processing session identifier

        Returns:
            True if cleared successfully
        """
        try:
            if session_id in self.session_metrics:
                del self.session_metrics[session_id]

            if session_id in self.aggregated_metrics:
                del self.aggregated_metrics[session_id]

            if session_id in self._session_timers:
                del self._session_timers[session_id]

            logger.info(f"Cleared metrics for session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to clear session metrics: {str(e)}")
            return False

    def get_collector_stats(self) -> Dict[str, Any]:
        """Get collector performance statistics.

        Returns:
            Collector statistics dictionary
        """
        return {
            "total_metrics_collected": self.total_metrics_collected,
            "collection_errors": self.collection_errors,
            "active_sessions": len(self.session_metrics),
            "buffer_sizes": {
                key: len(buffer) for key, buffer in self.metrics_buffer.items()
            },
            "aggregation_count": sum(
                len(session_agg) for session_agg in self.aggregated_metrics.values()
            ),
        }

    def _calculate_total_processing_time(self, session_id: str) -> float:
        """Calculate total processing time for a session."""
        session_agg = self.aggregated_metrics.get(session_id, {})

        signal_time = session_agg.get("signal_latency", MetricAggregation()).mean or 0.0
        feature_time = (
            session_agg.get("feature_extraction", MetricAggregation()).mean or 0.0
        )
        inference_time = (
            session_agg.get("inference_latency", MetricAggregation()).mean or 0.0
        )

        return signal_time + feature_time + inference_time

    def _calculate_processing_accuracy(self, session_id: str) -> float:
        """Calculate processing accuracy for a session."""
        # This would be based on validation against ground truth
        # For now, return a placeholder based on data quality
        session_agg = self.aggregated_metrics.get(session_id, {})
        quality = session_agg.get("data_quality", MetricAggregation()).mean or 0.0
        return min(1.0, quality * 1.1)  # Slight boost over quality score

    def _calculate_signal_quality(self, session_id: str) -> float:
        """Calculate signal quality for a session."""
        session_agg = self.aggregated_metrics.get(session_id, {})
        return session_agg.get("data_quality", MetricAggregation()).mean or 0.0

    def _calculate_feature_throughput(self, session_id: str) -> float:
        """Calculate feature extraction throughput."""
        session_agg = self.aggregated_metrics.get(session_id, {})

        # Estimate based on overall throughput and feature extraction time
        throughput = session_agg.get("throughput", MetricAggregation()).mean or 0.0
        feature_time = (
            session_agg.get("feature_extraction", MetricAggregation()).mean or 1.0
        )

        if feature_time > 0:
            return throughput * (1000.0 / feature_time)  # Convert ms to features / sec
        return 0.0

    def _calculate_prediction_throughput(self, session_id: str) -> float:
        """Calculate prediction throughput."""
        session_agg = self.aggregated_metrics.get(session_id, {})

        # Estimate based on inference latency
        inference_time = (
            session_agg.get("inference_latency", MetricAggregation()).mean or 1.0
        )

        if inference_time > 0:
            return 1000.0 / inference_time  # predictions per second
        return 0.0
