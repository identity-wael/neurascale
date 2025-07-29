"""
Main performance monitoring orchestrator
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .metrics.neural_metrics import NeuralMetricsCollector, NeuralMetrics
from .metrics.device_metrics import DeviceMetricsCollector, DeviceMetrics
from .metrics.system_metrics import SystemMetricsCollector
from .collectors.prometheus_collector import PrometheusCollector
from .collectors.opentelemetry_tracer import NeuralTracer
from .collectors.health_checker import HealthChecker
from .alerting.alert_manager import AlertManager
from .dashboards.grafana_dashboards import GrafanaDashboardManager

logger = logging.getLogger(__name__)


@dataclass
class MonitoringConfig:
    """Configuration for performance monitoring"""

    # Monitoring intervals
    neural_metrics_interval_ms: int = 100
    device_metrics_interval_ms: int = 1000
    system_metrics_interval_ms: int = 5000
    health_check_interval_ms: int = 30000

    # Prometheus configuration
    prometheus_port: int = 9090
    prometheus_job_name: str = "neural-engine"

    # Grafana configuration
    grafana_url: str = "http://localhost:3000"
    grafana_api_key: Optional[str] = None

    # Jaeger configuration
    jaeger_agent_host: str = "localhost"
    jaeger_agent_port: int = 6831

    # Alert configuration
    alert_webhook_url: Optional[str] = None
    pagerduty_api_key: Optional[str] = None
    slack_webhook_url: Optional[str] = None

    # Performance thresholds
    max_processing_latency_ms: float = 100.0
    min_data_quality_score: float = 0.7
    max_device_error_rate: float = 0.01


@dataclass
class MonitoringStatus:
    """Current monitoring system status"""

    is_running: bool
    start_time: Optional[datetime]
    metrics_collected: int
    alerts_triggered: int
    active_devices: int
    system_health: str  # "healthy", "degraded", "unhealthy"
    last_health_check: Optional[datetime]


@dataclass
class PerformanceReport:
    """Comprehensive performance report"""

    time_range: tuple[datetime, datetime]
    neural_metrics: Dict[str, float]
    device_metrics: Dict[str, Dict[str, float]]
    system_metrics: Dict[str, float]
    alerts: List[Dict[str, Any]]
    recommendations: List[str]


class PerformanceMonitor:
    """Main performance monitoring orchestrator"""

    def __init__(self, config: MonitoringConfig):
        """
        Initialize performance monitor

        Args:
            config: Monitoring configuration
        """
        self.config = config
        self._running = False
        self._start_time: Optional[datetime] = None

        # Initialize collectors
        self.neural_metrics = NeuralMetricsCollector()
        self.device_metrics = DeviceMetricsCollector()
        self.system_metrics = SystemMetricsCollector()

        # Initialize Prometheus collector
        self.prometheus = PrometheusCollector(
            job_name=config.prometheus_job_name, port=config.prometheus_port
        )

        # Initialize OpenTelemetry tracer
        self.tracer = NeuralTracer(
            service_name="neural-engine",
            otlp_endpoint=f"http://{config.jaeger_agent_host}:4317",  # Use OTLP endpoint
        )

        # Initialize health checker
        self.health_checker = HealthChecker(
            ["neural-processing", "device-management", "database", "cache", "api"]
        )

        # Initialize alert manager
        self.alert_manager = AlertManager(
            webhook_url=config.alert_webhook_url,
            pagerduty_key=config.pagerduty_api_key,
            slack_webhook=config.slack_webhook_url,
        )

        # Initialize dashboard manager
        self.dashboard_manager = GrafanaDashboardManager(
            grafana_url=config.grafana_url, api_key=config.grafana_api_key
        )

        # Monitoring tasks
        self._monitoring_tasks: List[asyncio.Task] = []

        # Metrics counters
        self._metrics_collected = 0
        self._alerts_triggered = 0

        logger.info("Performance monitor initialized")

    async def start_monitoring(self) -> None:
        """Start comprehensive monitoring"""
        if self._running:
            logger.warning("Monitoring already running")
            return

        self._running = True
        self._start_time = datetime.now()

        logger.info("Starting performance monitoring")

        # Register metrics with Prometheus
        self._register_prometheus_metrics()

        # Start Prometheus HTTP server
        await self.prometheus.start_server()

        # Create monitoring dashboards
        await self._setup_dashboards()

        # Start monitoring tasks
        self._monitoring_tasks = [
            asyncio.create_task(self._monitor_neural_metrics()),
            asyncio.create_task(self._monitor_device_metrics()),
            asyncio.create_task(self._monitor_system_metrics()),
            asyncio.create_task(self._monitor_health()),
            asyncio.create_task(self._process_alerts()),
        ]

        logger.info("Performance monitoring started")

    async def stop_monitoring(self) -> None:
        """Stop all monitoring activities"""
        if not self._running:
            return

        logger.info("Stopping performance monitoring")

        self._running = False

        # Cancel all monitoring tasks
        for task in self._monitoring_tasks:
            task.cancel()

        # Wait for tasks to complete
        await asyncio.gather(*self._monitoring_tasks, return_exceptions=True)

        # Stop Prometheus server
        await self.prometheus.stop_server()

        logger.info("Performance monitoring stopped")

    def get_monitoring_status(self) -> MonitoringStatus:
        """Get current monitoring status"""
        active_devices = len(self.device_metrics.get_active_devices())

        # Determine system health
        if not self._running:
            system_health = "stopped"
        elif self._alerts_triggered > 10:
            system_health = "unhealthy"
        elif self._alerts_triggered > 5:
            system_health = "degraded"
        else:
            system_health = "healthy"

        return MonitoringStatus(
            is_running=self._running,
            start_time=self._start_time,
            metrics_collected=self._metrics_collected,
            alerts_triggered=self._alerts_triggered,
            active_devices=active_devices,
            system_health=system_health,
            last_health_check=self.health_checker.last_check_time,
        )

    async def update_configuration(self, new_config: MonitoringConfig) -> None:
        """Update monitoring configuration"""
        logger.info("Updating monitoring configuration")

        # Store old config
        old_config = self.config
        self.config = new_config

        # Update alert manager configuration
        self.alert_manager.update_config(
            webhook_url=new_config.alert_webhook_url,
            pagerduty_key=new_config.pagerduty_api_key,
            slack_webhook=new_config.slack_webhook_url,
        )

        # Update dashboard manager if Grafana settings changed
        if (
            old_config.grafana_url != new_config.grafana_url
            or old_config.grafana_api_key != new_config.grafana_api_key
        ):
            self.dashboard_manager.update_config(
                grafana_url=new_config.grafana_url, api_key=new_config.grafana_api_key
            )

        logger.info("Monitoring configuration updated")

    async def collect_neural_metrics(self, session_id: str) -> NeuralMetrics:
        """
        Collect neural processing metrics

        Args:
            session_id: Current session ID

        Returns:
            Neural processing metrics
        """
        with self.tracer.trace_neural_processing(session_id):
            metrics = await self.neural_metrics.collect_current_metrics()

            # Record in Prometheus
            self.prometheus.record_neural_metrics(metrics)

            # Check for alerts
            await self._check_neural_alerts(metrics)

            self._metrics_collected += 1

            return metrics

    async def monitor_device_performance(self, device_id: str) -> DeviceMetrics:
        """
        Monitor individual device performance

        Args:
            device_id: Device to monitor

        Returns:
            Device performance metrics
        """
        metrics = await self.device_metrics.get_device_metrics(device_id)

        # Record in Prometheus
        self.prometheus.record_device_metrics(device_id, metrics)

        # Check for device alerts
        await self._check_device_alerts(device_id, metrics)

        return metrics

    def generate_performance_report(
        self, start_time: datetime, end_time: datetime
    ) -> PerformanceReport:
        """
        Generate comprehensive performance report

        Args:
            start_time: Report start time
            end_time: Report end time

        Returns:
            Performance report
        """
        # Collect neural metrics summary
        neural_summary = self.neural_metrics.get_metrics_summary(start_time, end_time)

        # Collect device metrics
        device_summary = {}
        for device_id in self.device_metrics.get_active_devices():
            device_summary[device_id] = self.device_metrics.get_device_summary(
                device_id, start_time, end_time
            )

        # Collect system metrics
        system_summary = self.system_metrics.get_metrics_summary(start_time, end_time)

        # Get alerts in time range
        alerts = self.alert_manager.get_alerts_in_range(start_time, end_time)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            neural_summary, device_summary, system_summary
        )

        return PerformanceReport(
            time_range=(start_time, end_time),
            neural_metrics=neural_summary,
            device_metrics=device_summary,
            system_metrics=system_summary,
            alerts=alerts,
            recommendations=recommendations,
        )

    async def _monitor_neural_metrics(self) -> None:
        """Background task to monitor neural metrics"""
        while self._running:
            try:
                # Collect current metrics
                metrics = await self.neural_metrics.collect_current_metrics()

                # Record in Prometheus
                self.prometheus.record_neural_metrics(metrics)

                # Check for alerts
                await self._check_neural_alerts(metrics)

                self._metrics_collected += 1

                # Wait for next collection interval
                await asyncio.sleep(self.config.neural_metrics_interval_ms / 1000.0)

            except Exception as e:
                logger.error(f"Error monitoring neural metrics: {e}")
                await asyncio.sleep(1)  # Brief pause before retry

    async def _monitor_device_metrics(self) -> None:
        """Background task to monitor device metrics"""
        while self._running:
            try:
                # Monitor all active devices
                for device_id in self.device_metrics.get_active_devices():
                    metrics = await self.device_metrics.get_device_metrics(device_id)

                    # Record in Prometheus
                    self.prometheus.record_device_metrics(device_id, metrics)

                    # Check for device alerts
                    await self._check_device_alerts(device_id, metrics)

                # Wait for next collection interval
                await asyncio.sleep(self.config.device_metrics_interval_ms / 1000.0)

            except Exception as e:
                logger.error(f"Error monitoring device metrics: {e}")
                await asyncio.sleep(1)

    async def _monitor_system_metrics(self) -> None:
        """Background task to monitor system metrics"""
        while self._running:
            try:
                # Collect system metrics
                metrics = await self.system_metrics.collect_current_metrics()

                # Record in Prometheus
                self.prometheus.record_system_metrics(metrics)

                # Check for system alerts
                await self._check_system_alerts(metrics)

                # Wait for next collection interval
                await asyncio.sleep(self.config.system_metrics_interval_ms / 1000.0)

            except Exception as e:
                logger.error(f"Error monitoring system metrics: {e}")
                await asyncio.sleep(1)

    async def _monitor_health(self) -> None:
        """Background task to monitor overall system health"""
        while self._running:
            try:
                # Run health checks
                health_report = await self.health_checker.generate_health_report()

                # Record health status in Prometheus
                self.prometheus.record_health_status(health_report)

                # Check for health alerts
                await self._check_health_alerts(health_report)

                # Wait for next health check
                await asyncio.sleep(self.config.health_check_interval_ms / 1000.0)

            except Exception as e:
                logger.error(f"Error monitoring health: {e}")
                await asyncio.sleep(5)

    async def _process_alerts(self) -> None:
        """Background task to process and send alerts"""
        while self._running:
            try:
                # Process pending alerts
                alerts_sent = await self.alert_manager.process_pending_alerts()
                self._alerts_triggered += alerts_sent

                # Brief pause between alert processing
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Error processing alerts: {e}")
                await asyncio.sleep(5)

    def _register_prometheus_metrics(self) -> None:
        """Register all metrics with Prometheus"""
        # Neural metrics
        self.prometheus.register_neural_metrics()

        # Device metrics
        self.prometheus.register_device_metrics()

        # System metrics
        self.prometheus.register_system_metrics()

        # Health metrics
        self.prometheus.register_health_metrics()

        logger.info("Prometheus metrics registered")

    async def _setup_dashboards(self) -> None:
        """Setup monitoring dashboards in Grafana"""
        try:
            # Create neural processing dashboard
            await self.dashboard_manager.create_neural_processing_dashboard()

            # Create device monitoring dashboard
            await self.dashboard_manager.create_device_monitoring_dashboard()

            # Create system performance dashboard
            await self.dashboard_manager.create_system_performance_dashboard()

            # Create alert management dashboard
            await self.dashboard_manager.create_alert_management_dashboard()

            logger.info("Monitoring dashboards created")

        except Exception as e:
            logger.error(f"Error creating dashboards: {e}")

    async def _check_neural_alerts(self, metrics: NeuralMetrics) -> None:
        """Check neural metrics for alert conditions"""
        # Check processing latency
        if metrics.signal_processing_latency > self.config.max_processing_latency_ms:
            await self.alert_manager.trigger_alert(
                name="HighSignalProcessingLatency",
                severity="critical",
                message=f"Signal processing latency {metrics.signal_processing_latency}ms exceeds threshold",
                labels={"component": "signal-processing"},
            )

        # Check data quality
        if metrics.data_quality_score < self.config.min_data_quality_score:
            await self.alert_manager.trigger_alert(
                name="LowDataQuality",
                severity="warning",
                message=f"Data quality score {metrics.data_quality_score} below threshold",
                labels={"component": "data-quality"},
            )

    async def _check_device_alerts(
        self, device_id: str, metrics: DeviceMetrics
    ) -> None:
        """Check device metrics for alert conditions"""
        # Check connection stability
        if metrics.connection_stability < 0.9:
            await self.alert_manager.trigger_alert(
                name="DeviceConnectionUnstable",
                severity="warning",
                message=f"Device {device_id} connection stability low: {metrics.connection_stability}",
                labels={"component": "device-management", "device_id": device_id},
            )

        # Check error rate
        if metrics.error_rate > self.config.max_device_error_rate:
            await self.alert_manager.trigger_alert(
                name="HighDeviceErrorRate",
                severity="critical",
                message=f"Device {device_id} error rate high: {metrics.error_rate}",
                labels={"component": "device-management", "device_id": device_id},
            )

    async def _check_system_alerts(self, metrics: Dict[str, float]) -> None:
        """Check system metrics for alert conditions"""
        # Check memory usage
        if metrics.get("memory_usage_percent", 0) > 80:
            await self.alert_manager.trigger_alert(
                name="HighMemoryUsage",
                severity="warning",
                message=f"Memory usage at {metrics['memory_usage_percent']}%",
                labels={"component": "system"},
            )

        # Check CPU usage
        if metrics.get("cpu_usage_percent", 0) > 90:
            await self.alert_manager.trigger_alert(
                name="HighCPUUsage",
                severity="critical",
                message=f"CPU usage at {metrics['cpu_usage_percent']}%",
                labels={"component": "system"},
            )

    async def _check_health_alerts(self, health_report: Dict[str, Any]) -> None:
        """Check health status for alert conditions"""
        unhealthy_services = [
            service
            for service, status in health_report["services"].items()
            if status["status"] != "healthy"
        ]

        if unhealthy_services:
            await self.alert_manager.trigger_alert(
                name="ServiceUnhealthy",
                severity="critical",
                message=f"Services unhealthy: {', '.join(unhealthy_services)}",
                labels={"component": "health"},
            )

    def _generate_recommendations(
        self,
        neural_summary: Dict[str, float],
        device_summary: Dict[str, Dict[str, float]],
        system_summary: Dict[str, float],
    ) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []

        # Neural processing recommendations
        if neural_summary.get("avg_processing_latency", 0) > 80:
            recommendations.append(
                "Consider optimizing signal processing algorithms to reduce latency"
            )

        if neural_summary.get("avg_data_quality", 1) < 0.8:
            recommendations.append(
                "Investigate data quality issues - check device connections and signal integrity"
            )

        # Device recommendations
        for device_id, metrics in device_summary.items():
            if metrics.get("avg_error_rate", 0) > 0.005:
                recommendations.append(
                    f"Device {device_id} showing high error rate - consider maintenance"
                )

        # System recommendations
        if system_summary.get("avg_memory_usage", 0) > 70:
            recommendations.append(
                "Memory usage trending high - consider scaling resources"
            )

        if system_summary.get("avg_cpu_usage", 0) > 80:
            recommendations.append(
                "CPU usage high - review processing efficiency and consider optimization"
            )

        return recommendations
