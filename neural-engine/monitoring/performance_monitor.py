"""Main Performance Monitor orchestrator for NeuraScale Neural Engine.

This module coordinates all monitoring activities including metrics collection,
alerting, and dashboard management.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class MonitoringStatus(Enum):
    """Monitoring system status."""

    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    ERROR = "error"
    STOPPING = "stopping"


@dataclass
class MonitoringConfig:
    """Configuration for performance monitoring system."""

    # Metrics collection
    metrics_collection_interval: int = 10  # seconds
    neural_metrics_enabled: bool = True
    device_metrics_enabled: bool = True
    system_metrics_enabled: bool = True

    # Storage and retention
    metrics_retention_days: int = 30
    high_frequency_retention_hours: int = 24

    # Alerting
    alerting_enabled: bool = True
    alert_evaluation_interval: int = 30  # seconds

    # Performance thresholds
    max_signal_processing_latency_ms: float = 100.0
    max_device_connection_failures: int = 3
    min_data_quality_score: float = 0.7
    max_memory_usage_percent: float = 80.0
    max_cpu_usage_percent: float = 75.0

    # Exporters
    prometheus_enabled: bool = True
    prometheus_port: int = 8000
    jaeger_enabled: bool = True
    jaeger_endpoint: str = "http://localhost:14268 / api / traces"

    # Neural Ledger integration
    ledger_logging_enabled: bool = True

    # Dashboard configuration
    grafana_enabled: bool = True
    dashboard_refresh_interval: int = 5  # seconds


@dataclass
class MonitoringStats:
    """Current monitoring system statistics."""

    status: MonitoringStatus
    uptime: timedelta
    metrics_collected: int = 0
    alerts_triggered: int = 0
    health_checks_performed: int = 0
    errors_encountered: int = 0
    last_collection_time: Optional[datetime] = None
    active_sessions: int = 0
    connected_devices: int = 0


class PerformanceMonitor:
    """Main performance monitoring orchestrator."""

    def __init__(self, config: MonitoringConfig):
        """Initialize the performance monitor.

        Args:
            config: Monitoring configuration
        """
        self.config = config
        self.status = MonitoringStatus.STOPPED
        self.start_time: Optional[datetime] = None
        self.stats = MonitoringStats(status=self.status, uptime=timedelta(0))

        # Component references (initialized in setup)
        self.neural_metrics_collector = None
        self.device_metrics_collector = None
        self.system_metrics_collector = None
        self.health_checker = None
        self.alert_manager = None
        self.prometheus_exporter = None
        self.jaeger_exporter = None

        # Monitoring tasks
        self._monitoring_tasks: List[asyncio.Task] = []
        self._shutdown_event = asyncio.Event()

        logger.info("PerformanceMonitor initialized")

    async def start_monitoring(self) -> None:
        """Start comprehensive monitoring system."""
        if self.status != MonitoringStatus.STOPPED:
            logger.warning(f"Monitoring already in state: {self.status}")
            return

        logger.info("Starting NeuraScale performance monitoring...")
        self.status = MonitoringStatus.STARTING
        self.start_time = datetime.utcnow()
        self.stats.status = self.status

        try:
            # Initialize components
            await self._initialize_components()

            # Start collection tasks
            await self._start_collection_tasks()

            # Start exporters
            await self._start_exporters()

            self.status = MonitoringStatus.RUNNING
            self.stats.status = self.status

            logger.info("Performance monitoring started successfully")

        except Exception as e:
            self.status = MonitoringStatus.ERROR
            self.stats.status = self.status
            self.stats.errors_encountered += 1
            logger.error(f"Failed to start monitoring: {str(e)}")
            raise

    async def stop_monitoring(self) -> None:
        """Stop all monitoring activities."""
        if self.status == MonitoringStatus.STOPPED:
            return

        logger.info("Stopping performance monitoring...")
        self.status = MonitoringStatus.STOPPING
        self.stats.status = self.status

        try:
            # Signal shutdown
            self._shutdown_event.set()

            # Cancel all tasks
            for task in self._monitoring_tasks:
                if not task.done():
                    task.cancel()

            # Wait for tasks to complete
            if self._monitoring_tasks:
                await asyncio.gather(*self._monitoring_tasks, return_exceptions=True)

            # Stop exporters
            await self._stop_exporters()

            self.status = MonitoringStatus.STOPPED
            self.stats.status = self.status

            logger.info("Performance monitoring stopped")

        except Exception as e:
            self.status = MonitoringStatus.ERROR
            self.stats.status = self.status
            logger.error(f"Error stopping monitoring: {str(e)}")

    async def get_monitoring_status(self) -> MonitoringStats:
        """Get current monitoring system status.

        Returns:
            Current monitoring statistics
        """
        if self.start_time:
            self.stats.uptime = datetime.utcnow() - self.start_time

        return self.stats

    async def update_configuration(self, new_config: MonitoringConfig) -> bool:
        """Update monitoring configuration.

        Args:
            new_config: New monitoring configuration

        Returns:
            True if update successful
        """
        try:
            # Validate configuration
            if not self._validate_config(new_config):
                return False

            # Update configuration
            old_config = self.config
            self.config = new_config

            # Restart components if necessary
            if self.status == MonitoringStatus.RUNNING:
                await self._handle_config_update(old_config, new_config)

            logger.info("Monitoring configuration updated")
            return True

        except Exception as e:
            logger.error(f"Failed to update configuration: {str(e)}")
            return False

    async def collect_neural_metrics(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Collect neural processing metrics for a session.

        Args:
            session_id: Neural processing session ID

        Returns:
            Neural metrics dictionary or None if collection fails
        """
        if not self.neural_metrics_collector:
            logger.warning("Neural metrics collector not initialized")
            return None

        try:
            metrics = await self.neural_metrics_collector.collect_session_metrics(
                session_id
            )
            self.stats.metrics_collected += 1
            self.stats.last_collection_time = datetime.utcnow()
            return metrics

        except Exception as e:
            logger.error(
                f"Failed to collect neural metrics for session {session_id}: {str(e)}"
            )
            self.stats.errors_encountered += 1
            return None

    async def monitor_device_performance(
        self, device_id: str
    ) -> Optional[Dict[str, Any]]:
        """Monitor individual device performance.

        Args:
            device_id: Device identifier

        Returns:
            Device performance metrics or None if monitoring fails
        """
        if not self.device_metrics_collector:
            logger.warning("Device metrics collector not initialized")
            return None

        try:
            metrics = await self.device_metrics_collector.collect_device_metrics(
                device_id
            )
            self.stats.metrics_collected += 1
            return metrics

        except Exception as e:
            logger.error(f"Failed to monitor device {device_id}: {str(e)}")
            self.stats.errors_encountered += 1
            return None

    async def perform_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive system health check.

        Returns:
            Health check results
        """
        if not self.health_checker:
            return {"status": "error", "message": "Health checker not initialized"}

        try:
            health_report = await self.health_checker.perform_comprehensive_check()
            self.stats.health_checks_performed += 1
            return health_report

        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            self.stats.errors_encountered += 1
            return {"status": "error", "message": str(e)}

    async def trigger_manual_alert(
        self, alert_type: str, message: str, severity: str = "warning"
    ) -> bool:
        """Trigger a manual alert.

        Args:
            alert_type: Type of alert
            message: Alert message
            severity: Alert severity level

        Returns:
            True if alert triggered successfully
        """
        if not self.alert_manager:
            logger.warning("Alert manager not initialized")
            return False

        try:
            await self.alert_manager.trigger_manual_alert(alert_type, message, severity)
            self.stats.alerts_triggered += 1
            return True

        except Exception as e:
            logger.error(f"Failed to trigger manual alert: {str(e)}")
            return False

    async def _initialize_components(self) -> None:
        """Initialize all monitoring components."""
        # Import here to avoid circular imports
        from .metrics.neural_metrics import NeuralMetricsCollector
        from .metrics.device_metrics import DeviceMetricsCollector
        from .metrics.system_metrics import SystemMetricsCollector
        from .collectors.health_checker import HealthChecker
        from .alerting.alert_manager import AlertManager

        # Initialize collectors
        if self.config.neural_metrics_enabled:
            self.neural_metrics_collector = NeuralMetricsCollector(self.config)

        if self.config.device_metrics_enabled:
            self.device_metrics_collector = DeviceMetricsCollector(self.config)

        if self.config.system_metrics_enabled:
            self.system_metrics_collector = SystemMetricsCollector(self.config)

        # Initialize health checker
        self.health_checker = HealthChecker(self.config)

        # Initialize alert manager
        if self.config.alerting_enabled:
            self.alert_manager = AlertManager(self.config)

        logger.info("Monitoring components initialized")

    async def _start_collection_tasks(self) -> None:
        """Start background metric collection tasks."""
        self._monitoring_tasks = []

        # Metrics collection task
        if (
            self.config.neural_metrics_enabled
            or self.config.device_metrics_enabled
            or self.config.system_metrics_enabled
        ):
            task = asyncio.create_task(self._metrics_collection_loop())
            self._monitoring_tasks.append(task)

        # Health monitoring task
        task = asyncio.create_task(self._health_monitoring_loop())
        self._monitoring_tasks.append(task)

        # Alert evaluation task
        if self.config.alerting_enabled:
            task = asyncio.create_task(self._alert_evaluation_loop())
            self._monitoring_tasks.append(task)

        logger.info(f"Started {len(self._monitoring_tasks)} monitoring tasks")

    async def _start_exporters(self) -> None:
        """Start metric exporters."""
        if self.config.prometheus_enabled:
            from .exporters.prometheus_exporter import PrometheusExporter

            self.prometheus_exporter = PrometheusExporter(self.config)
            await self.prometheus_exporter.start()

        if self.config.jaeger_enabled:
            from .exporters.jaeger_exporter import JaegerExporter

            self.jaeger_exporter = JaegerExporter(self.config)
            await self.jaeger_exporter.start()

        logger.info("Metric exporters started")

    async def _stop_exporters(self) -> None:
        """Stop metric exporters."""
        if self.prometheus_exporter:
            await self.prometheus_exporter.stop()

        if self.jaeger_exporter:
            await self.jaeger_exporter.stop()

    async def _metrics_collection_loop(self) -> None:
        """Background task for periodic metrics collection."""
        logger.info("Starting metrics collection loop")

        while not self._shutdown_event.is_set():
            try:
                # Collect system metrics
                if self.system_metrics_collector:
                    await self.system_metrics_collector.collect_all_metrics()

                self.stats.metrics_collected += 1
                self.stats.last_collection_time = datetime.utcnow()

            except Exception as e:
                logger.error(f"Error in metrics collection: {str(e)}")
                self.stats.errors_encountered += 1

            # Wait for next collection interval
            try:
                await asyncio.wait_for(
                    self._shutdown_event.wait(),
                    timeout=self.config.metrics_collection_interval,
                )
                break  # Shutdown requested
            except asyncio.TimeoutError:
                continue  # Continue collecting

        logger.info("Metrics collection loop stopped")

    async def _health_monitoring_loop(self) -> None:
        """Background task for health monitoring."""
        logger.info("Starting health monitoring loop")

        while not self._shutdown_event.is_set():
            try:
                if self.health_checker:
                    await self.health_checker.perform_routine_checks()
                    self.stats.health_checks_performed += 1

            except Exception as e:
                logger.error(f"Error in health monitoring: {str(e)}")
                self.stats.errors_encountered += 1

            # Wait for next check interval (use same as metrics for now)
            try:
                await asyncio.wait_for(
                    self._shutdown_event.wait(),
                    timeout=self.config.metrics_collection_interval * 2,
                )
                break
            except asyncio.TimeoutError:
                continue

        logger.info("Health monitoring loop stopped")

    async def _alert_evaluation_loop(self) -> None:
        """Background task for alert evaluation."""
        logger.info("Starting alert evaluation loop")

        while not self._shutdown_event.is_set():
            try:
                if self.alert_manager:
                    alerts_triggered = await self.alert_manager.evaluate_all_rules()
                    self.stats.alerts_triggered += alerts_triggered

            except Exception as e:
                logger.error(f"Error in alert evaluation: {str(e)}")
                self.stats.errors_encountered += 1

            # Wait for next evaluation interval
            try:
                await asyncio.wait_for(
                    self._shutdown_event.wait(),
                    timeout=self.config.alert_evaluation_interval,
                )
                break
            except asyncio.TimeoutError:
                continue

        logger.info("Alert evaluation loop stopped")

    def _validate_config(self, config: MonitoringConfig) -> bool:
        """Validate monitoring configuration.

        Args:
            config: Configuration to validate

        Returns:
            True if configuration is valid
        """
        try:
            # Basic validation
            if config.metrics_collection_interval <= 0:
                logger.error("Invalid metrics collection interval")
                return False

            if config.alert_evaluation_interval <= 0:
                logger.error("Invalid alert evaluation interval")
                return False

            if config.prometheus_port <= 0 or config.prometheus_port > 65535:
                logger.error("Invalid Prometheus port")
                return False

            return True

        except Exception as e:
            logger.error(f"Configuration validation error: {str(e)}")
            return False

    async def _handle_config_update(
        self, old_config: MonitoringConfig, new_config: MonitoringConfig
    ) -> None:
        """Handle configuration updates while running.

        Args:
            old_config: Previous configuration
            new_config: New configuration
        """
        # For now, restart monitoring if significant changes
        restart_required = (
            old_config.metrics_collection_interval
            != new_config.metrics_collection_interval
            or old_config.prometheus_enabled != new_config.prometheus_enabled
            or old_config.jaeger_enabled != new_config.jaeger_enabled
        )

        if restart_required:
            logger.info("Configuration change requires restart")
            await self.stop_monitoring()
            await self.start_monitoring()
        else:
            logger.info("Configuration updated without restart")


def create_performance_monitor(
    config: Optional[MonitoringConfig] = None,
) -> PerformanceMonitor:
    """Create a performance monitor instance.

    Args:
        config: Optional monitoring configuration

    Returns:
        PerformanceMonitor instance
    """
    if config is None:
        config = MonitoringConfig()

    return PerformanceMonitor(config)
