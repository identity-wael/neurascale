"""
Prometheus metrics collection and export
"""

import logging
from typing import Dict, Optional, Any
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    CollectorRegistry,
    generate_latest,
    start_http_server,
    push_to_gateway,
)

from ..metrics.neural_metrics import NeuralMetrics
from ..metrics.device_metrics import DeviceMetrics

logger = logging.getLogger(__name__)


class PrometheusCollector:
    """Prometheus metrics collector and exporter"""

    def __init__(
        self,
        job_name: str = "neural-engine",
        port: int = 9090,
        pushgateway_url: Optional[str] = None,
    ):
        """
        Initialize Prometheus collector

        Args:
            job_name: Job name for metrics
            port: Port for metrics HTTP server
            pushgateway_url: Optional Pushgateway URL
        """
        self.job_name = job_name
        self.port = port
        self.pushgateway_url = pushgateway_url

        # Create custom registry
        self.registry = CollectorRegistry()

        # Neural processing metrics
        self.signal_processing_latency = Histogram(
            "neural_signal_processing_duration_seconds",
            "Signal processing latency in seconds",
            ["device_type"],
            registry=self.registry,
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
        )

        self.feature_extraction_time = Histogram(
            "neural_feature_extraction_duration_seconds",
            "Feature extraction time in seconds",
            registry=self.registry,
            buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
        )

        self.model_inference_latency = Histogram(
            "neural_model_inference_duration_seconds",
            "Model inference latency in seconds",
            ["model_id"],
            registry=self.registry,
            buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
        )

        self.data_quality_score = Gauge(
            "neural_data_quality_score",
            "Neural data quality score (0-1)",
            ["session_id"],
            registry=self.registry,
        )

        self.processing_accuracy = Gauge(
            "neural_processing_accuracy",
            "Neural processing accuracy (0-1)",
            registry=self.registry,
        )

        self.throughput_samples = Gauge(
            "neural_throughput_samples_per_second",
            "Neural processing throughput in samples/sec",
            registry=self.registry,
        )

        # Device metrics
        self.device_connected = Gauge(
            "neural_device_connected",
            "Device connection status (1=connected, 0=disconnected)",
            ["device_id"],
            registry=self.registry,
        )

        self.device_stability = Gauge(
            "neural_device_connection_stability",
            "Device connection stability score (0-1)",
            ["device_id"],
            registry=self.registry,
        )

        self.device_data_rate = Gauge(
            "neural_device_data_rate_hz",
            "Device data rate in Hz",
            ["device_id"],
            registry=self.registry,
        )

        self.device_signal_quality = Gauge(
            "neural_device_signal_quality",
            "Device signal quality score (0-1)",
            ["device_id"],
            registry=self.registry,
        )

        self.device_error_rate = Gauge(
            "neural_device_error_rate",
            "Device error rate per second",
            ["device_id"],
            registry=self.registry,
        )

        self.device_latency = Gauge(
            "neural_device_latency_milliseconds",
            "Device communication latency in milliseconds",
            ["device_id"],
            registry=self.registry,
        )

        self.device_packet_loss = Gauge(
            "neural_device_packet_loss_rate",
            "Device packet loss rate (0-1)",
            ["device_id"],
            registry=self.registry,
        )

        # System metrics
        self.cpu_usage = Gauge(
            "neural_cpu_usage_percent", "CPU usage percentage", registry=self.registry
        )

        self.memory_usage = Gauge(
            "neural_memory_usage_bytes", "Memory usage in bytes", registry=self.registry
        )

        self.memory_usage_percent = Gauge(
            "neural_memory_usage_percent",
            "Memory usage percentage",
            registry=self.registry,
        )

        self.disk_usage = Gauge(
            "neural_disk_usage_percent", "Disk usage percentage", registry=self.registry
        )

        self.network_bytes_sent = Counter(
            "neural_network_bytes_sent_total",
            "Total network bytes sent",
            registry=self.registry,
        )

        self.network_bytes_recv = Counter(
            "neural_network_bytes_received_total",
            "Total network bytes received",
            registry=self.registry,
        )

        self.active_connections = Gauge(
            "neural_active_connections",
            "Number of active network connections",
            registry=self.registry,
        )

        # Health metrics
        self.service_health = Gauge(
            "neural_service_health",
            "Service health status (1=healthy, 0=unhealthy)",
            ["service"],
            registry=self.registry,
        )

        # API metrics
        self.api_request_duration = Histogram(
            "neural_api_request_duration_seconds",
            "API request duration in seconds",
            ["method", "endpoint", "status"],
            registry=self.registry,
            buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
        )

        self.api_requests_total = Counter(
            "neural_api_requests_total",
            "Total API requests",
            ["method", "endpoint", "status"],
            registry=self.registry,
        )

        # Database metrics
        self.db_query_duration = Histogram(
            "neural_db_query_duration_seconds",
            "Database query duration in seconds",
            ["query_type"],
            registry=self.registry,
            buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0),
        )

        self.db_connections_active = Gauge(
            "neural_db_connections_active",
            "Active database connections",
            registry=self.registry,
        )

        self.db_connections_max = Gauge(
            "neural_db_connections_max",
            "Maximum database connections",
            registry=self.registry,
        )

        # Custom metrics
        self.sessions_active = Gauge(
            "neural_sessions_active",
            "Active neural processing sessions",
            registry=self.registry,
        )

        self.events_processed = Counter(
            "neural_events_processed_total",
            "Total neural events processed",
            ["event_type"],
            registry=self.registry,
        )

        logger.info(f"Prometheus collector initialized on port {port}")

    async def start_server(self) -> None:
        """Start Prometheus HTTP metrics server"""
        try:
            start_http_server(self.port, registry=self.registry)
            logger.info(f"Prometheus metrics server started on port {self.port}")
        except Exception as e:
            logger.error(f"Failed to start Prometheus server: {e}")
            raise

    async def stop_server(self) -> None:
        """Stop Prometheus metrics server"""
        # Note: prometheus_client doesn't provide a clean way to stop the server
        # In production, you might want to use a more sophisticated approach
        logger.info("Prometheus metrics server stop requested")

    def register_neural_metrics(self) -> None:
        """Register neural processing metrics"""
        logger.info("Neural metrics registered with Prometheus")

    def register_device_metrics(self) -> None:
        """Register device performance metrics"""
        logger.info("Device metrics registered with Prometheus")

    def register_system_metrics(self) -> None:
        """Register system resource metrics"""
        logger.info("System metrics registered with Prometheus")

    def register_health_metrics(self) -> None:
        """Register health check metrics"""
        logger.info("Health metrics registered with Prometheus")

    def record_neural_metrics(self, metrics: NeuralMetrics) -> None:
        """
        Record neural processing metrics

        Args:
            metrics: Neural metrics to record
        """
        # Convert milliseconds to seconds for Prometheus
        self.signal_processing_latency.labels(device_type="default").observe(
            metrics.signal_processing_latency / 1000.0
        )

        self.feature_extraction_time.observe(metrics.feature_extraction_time / 1000.0)

        self.model_inference_latency.labels(model_id="default").observe(
            metrics.model_inference_latency / 1000.0
        )

        self.data_quality_score.labels(session_id="current").set(
            metrics.data_quality_score
        )

        self.processing_accuracy.set(metrics.processing_accuracy)
        self.throughput_samples.set(metrics.throughput_samples_per_sec)

    def record_device_metrics(self, device_id: str, metrics: DeviceMetrics) -> None:
        """
        Record device performance metrics

        Args:
            device_id: Device identifier
            metrics: Device metrics to record
        """
        self.device_connected.labels(device_id=device_id).set(1)
        self.device_stability.labels(device_id=device_id).set(
            metrics.connection_stability
        )
        self.device_data_rate.labels(device_id=device_id).set(metrics.data_rate)
        self.device_signal_quality.labels(device_id=device_id).set(
            metrics.signal_quality
        )
        self.device_error_rate.labels(device_id=device_id).set(metrics.error_rate)
        self.device_latency.labels(device_id=device_id).set(metrics.latency)

        # Calculate packet loss rate
        total_packets = metrics.packets_received + metrics.packets_lost
        if total_packets > 0:
            packet_loss_rate = metrics.packets_lost / total_packets
        else:
            packet_loss_rate = 0.0

        self.device_packet_loss.labels(device_id=device_id).set(packet_loss_rate)

    def record_system_metrics(self, metrics: Dict[str, float]) -> None:
        """
        Record system resource metrics

        Args:
            metrics: System metrics dictionary
        """
        self.cpu_usage.set(metrics.get("cpu_usage_percent", 0))
        self.memory_usage.set(metrics.get("memory_usage_mb", 0) * 1024 * 1024)
        self.memory_usage_percent.set(metrics.get("memory_usage_percent", 0))
        self.disk_usage.set(metrics.get("disk_usage_percent", 0))
        self.active_connections.set(metrics.get("active_connections", 0))

    def record_health_status(self, health_report: Dict[str, Any]) -> None:
        """
        Record service health status

        Args:
            health_report: Health check report
        """
        for service, status in health_report.get("services", {}).items():
            health_value = 1 if status.get("status") == "healthy" else 0
            self.service_health.labels(service=service).set(health_value)

    def record_api_metrics(
        self, method: str, endpoint: str, status: int, duration: float
    ) -> None:
        """
        Record API request metrics

        Args:
            method: HTTP method
            endpoint: API endpoint
            status: Response status code
            duration: Request duration in seconds
        """
        labels = {"method": method, "endpoint": endpoint, "status": str(status)}

        self.api_request_duration.labels(**labels).observe(duration)
        self.api_requests_total.labels(**labels).inc()

    def record_db_metrics(
        self,
        query_type: str,
        duration: float,
        connections_active: int,
        connections_max: int,
    ) -> None:
        """
        Record database metrics

        Args:
            query_type: Type of database query
            duration: Query duration in seconds
            connections_active: Active connections
            connections_max: Maximum connections
        """
        self.db_query_duration.labels(query_type=query_type).observe(duration)
        self.db_connections_active.set(connections_active)
        self.db_connections_max.set(connections_max)

    def record_custom_metrics(
        self, sessions_active: int, event_type: str, events_count: int = 1
    ) -> None:
        """
        Record custom business metrics

        Args:
            sessions_active: Number of active sessions
            event_type: Type of event
            events_count: Number of events
        """
        self.sessions_active.set(sessions_active)
        self.events_processed.labels(event_type=event_type).inc(events_count)

    def push_metrics(self) -> None:
        """Push metrics to Pushgateway if configured"""
        if self.pushgateway_url:
            try:
                push_to_gateway(
                    self.pushgateway_url, job=self.job_name, registry=self.registry
                )
                logger.debug("Metrics pushed to Pushgateway")
            except Exception as e:
                logger.error(f"Failed to push metrics: {e}")

    def export_metrics(self) -> bytes:
        """
        Export metrics in Prometheus format

        Returns:
            Metrics in Prometheus text format
        """
        return bytes(generate_latest(self.registry))
