"""Prometheus metrics collection and export for NeuraScale Neural Engine.

This module implements Prometheus integration for metrics collection,
registration, and export.
"""

from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    Summary,
    CollectorRegistry,
    generate_latest,
    start_http_server,
)
import time

# from datetime import datetime
from typing import Dict, List, Any
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MetricDefinition:
    """Definition of a Prometheus metric."""

    name: str
    help_text: str
    metric_type: str
    labels: List[str] = None

    def __post_init__(self):
        if self.labels is None:
            self.labels = []


class PrometheusCollector:
    """Prometheus metrics collector and exporter."""

    def __init__(self, config):
        """Initialize Prometheus collector.

        Args:
            config: Monitoring configuration
        """
        self.config = config
        self.registry = CollectorRegistry()

        # Metric storage
        self.counters: Dict[str, Counter] = {}
        self.gauges: Dict[str, Gauge] = {}
        self.histograms: Dict[str, Histogram] = {}
        self.summaries: Dict[str, Summary] = {}

        # HTTP server for metrics endpoint
        self.http_server = None
        self.server_started = False

        # Initialize standard neural engine metrics
        self._register_neural_metrics()

        logger.info("PrometheusCollector initialized")

    def _register_neural_metrics(self) -> None:
        """Register standard neural engine metrics."""

        # Neural processing metrics
        self._register_counter(
            "neural_signal_processing_total",
            "Total number of neural signals processed",
            ["device_type", "status"],
        )

        self._register_histogram(
            "neural_signal_processing_duration_seconds",
            "Duration of neural signal processing",
            ["device_type"],
            buckets=[0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0],
        )

        self._register_histogram(
            "neural_feature_extraction_duration_seconds",
            "Duration of neural feature extraction",
            ["session_id"],
            buckets=[0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0],
        )

        self._register_histogram(
            "neural_model_inference_duration_seconds",
            "Duration of neural model inference",
            ["model_id"],
            buckets=[0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0],
        )

        self._register_gauge(
            "neural_data_quality_score",
            "Neural data quality score (0-1)",
            ["session_id", "device_id"],
        )

        self._register_counter(
            "neural_sessions_total",
            "Total number of neural processing sessions",
            ["status"],  # started, completed, failed
        )

        self._register_gauge(
            "neural_sessions_active",
            "Number of currently active neural processing sessions",
        )

        # Device metrics
        self._register_gauge(
            "neural_device_connected",
            "Device connection status (1=connected, 0=disconnected)",
            ["device_id", "device_type"],
        )

        self._register_counter(
            "neural_device_connection_failures_total",
            "Total number of device connection failures",
            ["device_id", "device_type", "error_type"],
        )

        self._register_gauge(
            "neural_device_signal_quality",
            "Device signal quality score (0-1)",
            ["device_id", "device_type"],
        )

        self._register_gauge(
            "neural_device_data_rate_hz",
            "Device data rate in Hz",
            ["device_id", "device_type"],
        )

        self._register_histogram(
            "neural_device_latency_seconds",
            "Device communication latency",
            ["device_id", "device_type"],
            buckets=[0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0],
        )

        # API metrics
        self._register_counter(
            "neural_api_requests_total",
            "Total number of API requests",
            ["method", "endpoint", "status_code"],
        )

        self._register_histogram(
            "neural_api_request_duration_seconds",
            "API request duration",
            ["method", "endpoint"],
            buckets=[
                0.001,
                0.005,
                0.01,
                0.025,
                0.05,
                0.1,
                0.25,
                0.5,
                1.0,
                2.5,
                5.0,
                10.0,
            ],
        )

        # System metrics
        self._register_gauge("neural_system_cpu_percent", "System CPU usage percentage")

        self._register_gauge(
            "neural_system_memory_percent", "System memory usage percentage"
        )

        self._register_gauge(
            "neural_system_disk_percent", "System disk usage percentage"
        )

        # Security metrics
        self._register_counter(
            "neural_auth_attempts_total",
            "Total authentication attempts",
            ["result"],  # success, failure
        )

        self._register_counter(
            "neural_authz_checks_total",
            "Total authorization checks",
            ["granted"],  # true, false
        )

        self._register_histogram(
            "neural_encryption_duration_seconds",
            "Duration of encryption operations",
            ["operation_type"],
            buckets=[0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5],
        )

        # Neural Ledger metrics
        self._register_counter(
            "neural_ledger_events_total",
            "Total events logged to Neural Ledger",
            ["event_type", "status"],
        )

        self._register_histogram(
            "neural_ledger_event_processing_duration_seconds",
            "Duration of Neural Ledger event processing",
            buckets=[0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0],
        )

    def _register_counter(
        self, name: str, description: str, labels: List[str] = None
    ) -> None:
        """Register a counter metric."""
        labels = labels or []
        counter = Counter(
            name=name,
            documentation=description,
            labelnames=labels,
            registry=self.registry,
        )
        self.counters[name] = counter
        logger.debug(f"Registered counter: {name}")

    def _register_gauge(
        self, name: str, description: str, labels: List[str] = None
    ) -> None:
        """Register a gauge metric."""
        labels = labels or []
        gauge = Gauge(
            name=name,
            documentation=description,
            labelnames=labels,
            registry=self.registry,
        )
        self.gauges[name] = gauge
        logger.debug(f"Registered gauge: {name}")

    def _register_histogram(
        self,
        name: str,
        description: str,
        labels: List[str] = None,
        buckets: List[float] = None,
    ) -> None:
        """Register a histogram metric."""
        labels = labels or []
        histogram = Histogram(
            name=name,
            documentation=description,
            labelnames=labels,
            buckets=buckets,
            registry=self.registry,
        )
        self.histograms[name] = histogram
        logger.debug(f"Registered histogram: {name}")

    def _register_summary(
        self, name: str, description: str, labels: List[str] = None
    ) -> None:
        """Register a summary metric."""
        labels = labels or []
        summary = Summary(
            name=name,
            documentation=description,
            labelnames=labels,
            registry=self.registry,
        )
        self.summaries[name] = summary
        logger.debug(f"Registered summary: {name}")

    async def start_http_server(self) -> bool:
        """Start HTTP server for metrics endpoint.

        Returns:
            True if server started successfully
        """
        try:
            if self.server_started:
                logger.warning("HTTP server already started")
                return True

            # Start metrics server
            start_http_server(port=self.config.prometheus_port, registry=self.registry)

            self.server_started = True
            logger.info(
                f"Prometheus metrics server started on port {self.config.prometheus_port}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to start Prometheus HTTP server: {str(e)}")
            return False

    def record_signal_processing(
        self, device_type: str, duration_seconds: float, status: str = "success"
    ) -> None:
        """Record neural signal processing metrics.

        Args:
            device_type: Type of device
            duration_seconds: Processing duration
            status: Processing status (success / failure)
        """
        try:
            # Increment counter
            self.counters["neural_signal_processing_total"].labels(
                device_type=device_type, status=status
            ).inc()

            # Record duration
            self.histograms["neural_signal_processing_duration_seconds"].labels(
                device_type=device_type
            ).observe(duration_seconds)

        except Exception as e:
            logger.error(f"Failed to record signal processing metrics: {str(e)}")

    def record_feature_extraction(
        self, session_id: str, duration_seconds: float
    ) -> None:
        """Record feature extraction metrics.

        Args:
            session_id: Processing session ID
            duration_seconds: Extraction duration
        """
        try:
            self.histograms["neural_feature_extraction_duration_seconds"].labels(
                session_id=session_id
            ).observe(duration_seconds)

        except Exception as e:
            logger.error(f"Failed to record feature extraction metrics: {str(e)}")

    def record_model_inference(self, model_id: str, duration_seconds: float) -> None:
        """Record model inference metrics.

        Args:
            model_id: Model identifier
            duration_seconds: Inference duration
        """
        try:
            self.histograms["neural_model_inference_duration_seconds"].labels(
                model_id=model_id
            ).observe(duration_seconds)

        except Exception as e:
            logger.error(f"Failed to record model inference metrics: {str(e)}")

    def set_data_quality(
        self, session_id: str, device_id: str, quality_score: float
    ) -> None:
        """Set data quality score.

        Args:
            session_id: Processing session ID
            device_id: Device identifier
            quality_score: Quality score (0-1)
        """
        try:
            self.gauges["neural_data_quality_score"].labels(
                session_id=session_id, device_id=device_id
            ).set(quality_score)

        except Exception as e:
            logger.error(f"Failed to set data quality metrics: {str(e)}")

    def record_session_event(self, status: str) -> None:
        """Record neural session event.

        Args:
            status: Session status (started / completed / failed)
        """
        try:
            self.counters["neural_sessions_total"].labels(status=status).inc()

        except Exception as e:
            logger.error(f"Failed to record session event: {str(e)}")

    def set_active_sessions(self, count: int) -> None:
        """Set number of active sessions.

        Args:
            count: Number of active sessions
        """
        try:
            self.gauges["neural_sessions_active"].set(count)

        except Exception as e:
            logger.error(f"Failed to set active sessions: {str(e)}")

    def set_device_connected(
        self, device_id: str, device_type: str, connected: bool
    ) -> None:
        """Set device connection status.

        Args:
            device_id: Device identifier
            device_type: Type of device
            connected: Connection status
        """
        try:
            self.gauges["neural_device_connected"].labels(
                device_id=device_id, device_type=device_type
            ).set(1 if connected else 0)

        except Exception as e:
            logger.error(f"Failed to set device connection status: {str(e)}")

    def record_device_failure(
        self, device_id: str, device_type: str, error_type: str
    ) -> None:
        """Record device connection failure.

        Args:
            device_id: Device identifier
            device_type: Type of device
            error_type: Type of error
        """
        try:
            self.counters["neural_device_connection_failures_total"].labels(
                device_id=device_id, device_type=device_type, error_type=error_type
            ).inc()

        except Exception as e:
            logger.error(f"Failed to record device failure: {str(e)}")

    def set_device_signal_quality(
        self, device_id: str, device_type: str, quality: float
    ) -> None:
        """Set device signal quality.

        Args:
            device_id: Device identifier
            device_type: Type of device
            quality: Signal quality (0-1)
        """
        try:
            self.gauges["neural_device_signal_quality"].labels(
                device_id=device_id, device_type=device_type
            ).set(quality)

        except Exception as e:
            logger.error(f"Failed to set device signal quality: {str(e)}")

    def set_device_data_rate(
        self, device_id: str, device_type: str, rate_hz: float
    ) -> None:
        """Set device data rate.

        Args:
            device_id: Device identifier
            device_type: Type of device
            rate_hz: Data rate in Hz
        """
        try:
            self.gauges["neural_device_data_rate_hz"].labels(
                device_id=device_id, device_type=device_type
            ).set(rate_hz)

        except Exception as e:
            logger.error(f"Failed to set device data rate: {str(e)}")

    def record_device_latency(
        self, device_id: str, device_type: str, latency_seconds: float
    ) -> None:
        """Record device communication latency.

        Args:
            device_id: Device identifier
            device_type: Type of device
            latency_seconds: Latency in seconds
        """
        try:
            self.histograms["neural_device_latency_seconds"].labels(
                device_id=device_id, device_type=device_type
            ).observe(latency_seconds)

        except Exception as e:
            logger.error(f"Failed to record device latency: {str(e)}")

    def record_api_request(
        self, method: str, endpoint: str, status_code: int, duration_seconds: float
    ) -> None:
        """Record API request metrics.

        Args:
            method: HTTP method
            endpoint: API endpoint
            status_code: HTTP status code
            duration_seconds: Request duration
        """
        try:
            # Record request count
            self.counters["neural_api_requests_total"].labels(
                method=method, endpoint=endpoint, status_code=str(status_code)
            ).inc()

            # Record duration
            self.histograms["neural_api_request_duration_seconds"].labels(
                method=method, endpoint=endpoint
            ).observe(duration_seconds)

        except Exception as e:
            logger.error(f"Failed to record API request metrics: {str(e)}")

    def set_system_metrics(
        self, cpu_percent: float, memory_percent: float, disk_percent: float
    ) -> None:
        """Set system resource usage metrics.

        Args:
            cpu_percent: CPU usage percentage
            memory_percent: Memory usage percentage
            disk_percent: Disk usage percentage
        """
        try:
            self.gauges["neural_system_cpu_percent"].set(cpu_percent)
            self.gauges["neural_system_memory_percent"].set(memory_percent)
            self.gauges["neural_system_disk_percent"].set(disk_percent)

        except Exception as e:
            logger.error(f"Failed to set system metrics: {str(e)}")

    def record_auth_attempt(self, success: bool) -> None:
        """Record authentication attempt.

        Args:
            success: Whether authentication was successful
        """
        try:
            result = "success" if success else "failure"
            self.counters["neural_auth_attempts_total"].labels(result=result).inc()

        except Exception as e:
            logger.error(f"Failed to record auth attempt: {str(e)}")

    def record_authz_check(self, granted: bool) -> None:
        """Record authorization check.

        Args:
            granted: Whether authorization was granted
        """
        try:
            self.counters["neural_authz_checks_total"].labels(
                granted=str(granted).lower()
            ).inc()

        except Exception as e:
            logger.error(f"Failed to record authz check: {str(e)}")

    def record_encryption_operation(
        self, operation_type: str, duration_seconds: float
    ) -> None:
        """Record encryption operation.

        Args:
            operation_type: Type of encryption operation
            duration_seconds: Operation duration
        """
        try:
            self.histograms["neural_encryption_duration_seconds"].labels(
                operation_type=operation_type
            ).observe(duration_seconds)

        except Exception as e:
            logger.error(f"Failed to record encryption operation: {str(e)}")

    def record_ledger_event(
        self, event_type: str, status: str, duration_seconds: float
    ) -> None:
        """Record Neural Ledger event.

        Args:
            event_type: Type of event
            status: Processing status
            duration_seconds: Processing duration
        """
        try:
            # Count events
            self.counters["neural_ledger_events_total"].labels(
                event_type=event_type, status=status
            ).inc()

            # Record processing time
            self.histograms["neural_ledger_event_processing_duration_seconds"].observe(
                duration_seconds
            )

        except Exception as e:
            logger.error(f"Failed to record ledger event: {str(e)}")

    def get_metrics_text(self) -> str:
        """Get metrics in Prometheus text format.

        Returns:
            Metrics text
        """
        try:
            return generate_latest(self.registry).decode("utf-8")
        except Exception as e:
            logger.error(f"Failed to generate metrics text: {str(e)}")
            return ""

    def get_registry_info(self) -> Dict[str, Any]:
        """Get information about registered metrics.

        Returns:
            Registry information
        """
        return {
            "counters": len(self.counters),
            "gauges": len(self.gauges),
            "histograms": len(self.histograms),
            "summaries": len(self.summaries),
            "server_started": self.server_started,
            "server_port": (
                self.config.prometheus_port
                if hasattr(self.config, "prometheus_port")
                else None
            ),
            "total_metrics": len(self.counters)
            + len(self.gauges)
            + len(self.histograms)
            + len(self.summaries),
        }


# Context manager for timing operations
class PrometheusTimer:
    """Context manager for timing operations with Prometheus metrics."""

    def __init__(self, collector: PrometheusCollector, metric_name: str, **labels):
        """Initialize timer.

        Args:
            collector: PrometheusCollector instance
            metric_name: Name of histogram metric to record to
            **labels: Metric labels
        """
        self.collector = collector
        self.metric_name = metric_name
        self.labels = labels
        self.start_time = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time is not None:
            duration = time.perf_counter() - self.start_time

            if self.metric_name in self.collector.histograms:
                self.collector.histograms[self.metric_name].labels(
                    **self.labels
                ).observe(duration)
            else:
                logger.warning(f"Histogram metric {self.metric_name} not found")
