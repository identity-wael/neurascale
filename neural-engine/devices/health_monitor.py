"""Health Monitor for BCI device status tracking and management.

This module provides comprehensive device health monitoring capabilities
including status tracking, performance metrics, and automated diagnostics.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import statistics

from .base import DeviceInfo, DeviceStatus, DeviceEvent, SignalQuality

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Device health status levels."""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNRESPONSIVE = "unresponsive"
    UNKNOWN = "unknown"


class AlertType(Enum):
    """Health alert types."""

    DEVICE_UNRESPONSIVE = "device_unresponsive"
    HIGH_LATENCY = "high_latency"
    PACKET_LOSS = "packet_loss"
    POOR_SIGNAL_QUALITY = "poor_signal_quality"
    HIGH_IMPEDANCE = "high_impedance"
    DEVICE_ERROR = "device_error"
    CONNECTION_UNSTABLE = "connection_unstable"


@dataclass
class HealthMetrics:
    """Device health metrics and statistics."""

    # Connectivity metrics
    uptime_seconds: float = 0.0
    connection_stability: float = 100.0  # Percentage
    last_seen: datetime = field(default_factory=datetime.utcnow)
    response_time_ms: float = 0.0

    # Performance metrics
    avg_latency_ms: float = 0.0
    packet_loss_rate: float = 0.0
    data_rate_hz: float = 0.0
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0

    # Signal quality metrics
    signal_quality: SignalQuality = SignalQuality.POOR
    avg_signal_strength: float = 0.0
    noise_level: float = 0.0
    artifact_rate: float = 0.0

    # Hardware metrics
    temperature_celsius: float = 0.0
    battery_level: float = 100.0
    impedance_quality: float = 100.0

    # Error tracking
    error_count: int = 0
    warning_count: int = 0
    last_error: Optional[str] = None

    # Health assessment
    overall_health: HealthStatus = HealthStatus.UNKNOWN
    health_score: float = 0.0  # 0-100


@dataclass
class HealthAlert:
    """Health monitoring alert."""

    alert_type: AlertType
    device_id: str
    severity: str  # info, warning, error, critical
    message: str
    timestamp: datetime
    metrics: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class HealthMonitorConfig:
    """Configuration for HealthMonitor."""

    # Monitoring intervals
    health_check_interval_seconds: int = 30
    metrics_collection_interval_seconds: int = 10

    # Alert thresholds
    response_timeout_seconds: float = 10.0
    high_latency_threshold_ms: float = 100.0
    packet_loss_threshold_percent: float = 5.0
    low_signal_quality_threshold: SignalQuality = SignalQuality.FAIR
    high_impedance_threshold_kohms: float = 50.0

    # Health assessment
    health_history_size: int = 100
    min_health_score: float = 70.0

    # Alert management
    alert_cooldown_seconds: int = 300  # 5 minutes
    max_alerts_per_device: int = 50


class HealthMonitor:
    """Comprehensive device health monitoring and management."""

    def __init__(self, config: HealthMonitorConfig = None):
        """Initialize HealthMonitor.

        Args:
            config: Health monitoring configuration
        """
        self.config = config or HealthMonitorConfig()

        # Device tracking
        self.monitored_devices: Set[str] = set()
        self.device_metrics: Dict[str, HealthMetrics] = {}
        self.device_history: Dict[str, List[HealthMetrics]] = {}

        # Alert management
        self.active_alerts: Dict[str, List[HealthAlert]] = {}
        self.alert_callbacks: List[Callable[[HealthAlert], None]] = []

        # Background tasks
        self.background_tasks: List[asyncio.Task] = []
        self.is_running = False
        self._shutdown_event = asyncio.Event()

        # Performance tracking
        self.monitoring_stats = {
            "health_checks_performed": 0,
            "alerts_generated": 0,
            "devices_monitored": 0,
            "uptime_seconds": 0.0,
        }
        self.start_time = datetime.utcnow()

        logger.info("HealthMonitor initialized")

    async def start(self) -> None:
        """Start health monitoring services."""
        if self.is_running:
            logger.warning("HealthMonitor already running")
            return

        logger.info("Starting HealthMonitor...")
        self.is_running = True
        self._shutdown_event.clear()

        # Start background monitoring tasks
        task = asyncio.create_task(self._health_monitoring_loop())
        self.background_tasks.append(task)

        task = asyncio.create_task(self._metrics_collection_loop())
        self.background_tasks.append(task)

        task = asyncio.create_task(self._alert_management_loop())
        self.background_tasks.append(task)

        logger.info("HealthMonitor started successfully")

    async def stop(self) -> None:
        """Stop health monitoring services."""
        if not self.is_running:
            return

        logger.info("Stopping HealthMonitor...")
        self.is_running = False
        self._shutdown_event.set()

        # Cancel background tasks
        for task in self.background_tasks:
            if not task.done():
                task.cancel()

        # Wait for tasks to complete
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)

        self.background_tasks.clear()
        logger.info("HealthMonitor stopped")

    async def start_monitoring_device(self, device_id: str) -> None:
        """Start monitoring a specific device.

        Args:
            device_id: Device identifier
        """
        if device_id in self.monitored_devices:
            logger.debug(f"Device {device_id} already being monitored")
            return

        self.monitored_devices.add(device_id)
        self.device_metrics[device_id] = HealthMetrics()
        self.device_history[device_id] = []
        self.active_alerts[device_id] = []

        self.monitoring_stats["devices_monitored"] = len(self.monitored_devices)

        logger.info(f"Started monitoring device: {device_id}")

    async def stop_monitoring_device(self, device_id: str) -> None:
        """Stop monitoring a specific device.

        Args:
            device_id: Device identifier
        """
        if device_id not in self.monitored_devices:
            logger.debug(f"Device {device_id} not being monitored")
            return

        self.monitored_devices.discard(device_id)

        # Clean up data (optional - keep for historical analysis)
        # del self.device_metrics[device_id]
        # del self.device_history[device_id]
        # del self.active_alerts[device_id]

        self.monitoring_stats["devices_monitored"] = len(self.monitored_devices)

        logger.info(f"Stopped monitoring device: {device_id}")

    async def update_device_metrics(
        self, device_id: str, metrics_update: Dict[str, Any]
    ) -> None:
        """Update device health metrics.

        Args:
            device_id: Device identifier
            metrics_update: Metrics to update
        """
        if device_id not in self.monitored_devices:
            logger.warning(
                f"Attempt to update metrics for unmonitored device: {device_id}"
            )
            return

        metrics = self.device_metrics[device_id]

        # Update metrics from provided data
        for key, value in metrics_update.items():
            if hasattr(metrics, key):
                setattr(metrics, key, value)

        # Update last seen time
        metrics.last_seen = datetime.utcnow()

        # Calculate health score
        await self._calculate_health_score(device_id)

        # Store in history
        await self._store_metrics_history(device_id)

        # Check for alerts
        await self._check_device_alerts(device_id)

    async def get_device_health(self, device_id: str) -> Optional[HealthMetrics]:
        """Get current health metrics for a device.

        Args:
            device_id: Device identifier

        Returns:
            Current health metrics or None if not monitored
        """
        return self.device_metrics.get(device_id)

    async def get_device_health_history(
        self, device_id: str, hours: int = 24
    ) -> List[HealthMetrics]:
        """Get historical health metrics for a device.

        Args:
            device_id: Device identifier
            hours: Number of hours of history to return

        Returns:
            List of historical health metrics
        """
        if device_id not in self.device_history:
            return []

        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        history = self.device_history[device_id]

        return [metrics for metrics in history if metrics.last_seen >= cutoff_time]

    async def get_active_alerts(self, device_id: str = None) -> List[HealthAlert]:
        """Get active alerts.

        Args:
            device_id: Device identifier (optional, returns all if None)

        Returns:
            List of active alerts
        """
        if device_id:
            return [
                alert
                for alert in self.active_alerts.get(device_id, [])
                if not alert.resolved
            ]

        all_alerts = []
        for alerts in self.active_alerts.values():
            all_alerts.extend([alert for alert in alerts if not alert.resolved])

        return all_alerts

    async def resolve_alert(self, device_id: str, alert_type: AlertType) -> bool:
        """Resolve an active alert.

        Args:
            device_id: Device identifier
            alert_type: Type of alert to resolve

        Returns:
            True if alert was resolved
        """
        if device_id not in self.active_alerts:
            return False

        for alert in self.active_alerts[device_id]:
            if alert.alert_type == alert_type and not alert.resolved:
                alert.resolved = True
                alert.resolved_at = datetime.utcnow()
                logger.info(f"Resolved alert {alert_type.value} for device {device_id}")
                return True

        return False

    def add_alert_callback(self, callback: Callable[[HealthAlert], None]) -> None:
        """Add callback for health alerts.

        Args:
            callback: Function to call when alerts are generated
        """
        self.alert_callbacks.append(callback)

    async def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get health monitoring statistics.

        Returns:
            Monitoring statistics
        """
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        self.monitoring_stats["uptime_seconds"] = uptime

        return {
            **self.monitoring_stats,
            "monitored_devices": len(self.monitored_devices),
            "total_active_alerts": len(await self.get_active_alerts()),
            "average_health_score": await self._calculate_average_health_score(),
        }

    # Private methods

    async def _health_monitoring_loop(self) -> None:
        """Background task for device health monitoring."""
        logger.info("Starting health monitoring loop")

        while not self._shutdown_event.is_set():
            try:
                for device_id in list(self.monitored_devices):
                    await self._perform_health_check(device_id)
                    self.monitoring_stats["health_checks_performed"] += 1

            except Exception as e:
                logger.error(f"Error in health monitoring loop: {str(e)}")

            # Wait for next health check cycle
            try:
                await asyncio.wait_for(
                    self._shutdown_event.wait(),
                    timeout=self.config.health_check_interval_seconds,
                )
                break  # Shutdown requested
            except asyncio.TimeoutError:
                continue  # Continue monitoring

        logger.info("Health monitoring loop stopped")

    async def _metrics_collection_loop(self) -> None:
        """Background task for metrics collection."""
        logger.info("Starting metrics collection loop")

        while not self._shutdown_event.is_set():
            try:
                for device_id in list(self.monitored_devices):
                    await self._collect_device_metrics(device_id)

            except Exception as e:
                logger.error(f"Error in metrics collection loop: {str(e)}")

            # Wait for next collection cycle
            try:
                await asyncio.wait_for(
                    self._shutdown_event.wait(),
                    timeout=self.config.metrics_collection_interval_seconds,
                )
                break  # Shutdown requested
            except asyncio.TimeoutError:
                continue  # Continue collection

        logger.info("Metrics collection loop stopped")

    async def _alert_management_loop(self) -> None:
        """Background task for alert management."""
        logger.info("Starting alert management loop")

        while not self._shutdown_event.is_set():
            try:
                await self._manage_alerts()

            except Exception as e:
                logger.error(f"Error in alert management loop: {str(e)}")

            # Wait for next management cycle
            try:
                await asyncio.wait_for(
                    self._shutdown_event.wait(),
                    timeout=60,  # Check alerts every minute
                )
                break  # Shutdown requested
            except asyncio.TimeoutError:
                continue  # Continue management

        logger.info("Alert management loop stopped")

    async def _perform_health_check(self, device_id: str) -> None:
        """Perform comprehensive health check on a device.

        Args:
            device_id: Device identifier
        """
        if device_id not in self.device_metrics:
            return

        metrics = self.device_metrics[device_id]

        # Check if device is responsive
        try:
            start_time = datetime.utcnow()
            # In a real implementation, this would ping the actual device
            # For now, we'll simulate based on last_seen time

            time_since_last_seen = (
                datetime.utcnow() - metrics.last_seen
            ).total_seconds()

            if time_since_last_seen > self.config.response_timeout_seconds:
                metrics.overall_health = HealthStatus.UNRESPONSIVE
                await self._generate_alert(
                    device_id,
                    AlertType.DEVICE_UNRESPONSIVE,
                    "error",
                    f"Device has not responded for {time_since_last_seen:.1f} seconds",
                )
            else:
                response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                metrics.response_time_ms = response_time

                if response_time > self.config.high_latency_threshold_ms:
                    await self._generate_alert(
                        device_id,
                        AlertType.HIGH_LATENCY,
                        "warning",
                        f"High response time: {response_time:.1f}ms",
                    )

        except Exception as e:
            logger.error(f"Error checking device {device_id} health: {str(e)}")
            await self._generate_alert(
                device_id,
                AlertType.DEVICE_ERROR,
                "error",
                f"Health check failed: {str(e)}",
            )

    async def _collect_device_metrics(self, device_id: str) -> None:
        """Collect detailed metrics for a device.

        Args:
            device_id: Device identifier
        """
        if device_id not in self.device_metrics:
            return

        metrics = self.device_metrics[device_id]

        # Update uptime
        if metrics.last_seen:
            metrics.uptime_seconds = (
                datetime.utcnow() - metrics.last_seen
            ).total_seconds()

        # In a real implementation, this would collect actual device metrics
        # For now, we'll simulate some basic metrics collection

        # Calculate connection stability based on recent history
        history = self.device_history.get(device_id, [])
        if len(history) > 10:
            recent_metrics = history[-10:]
            responsive_count = sum(
                1
                for m in recent_metrics
                if m.overall_health != HealthStatus.UNRESPONSIVE
            )
            metrics.connection_stability = (
                responsive_count / len(recent_metrics)
            ) * 100

    async def _calculate_health_score(self, device_id: str) -> None:
        """Calculate overall health score for a device.

        Args:
            device_id: Device identifier
        """
        if device_id not in self.device_metrics:
            return

        metrics = self.device_metrics[device_id]
        score = 100.0  # Start with perfect score

        # Deduct points based on various factors
        if metrics.overall_health == HealthStatus.UNRESPONSIVE:
            score = 0.0
        elif metrics.overall_health == HealthStatus.CRITICAL:
            score = min(score, 25.0)
        elif metrics.overall_health == HealthStatus.WARNING:
            score = min(score, 60.0)

        # Factor in connection stability
        score *= metrics.connection_stability / 100.0

        # Factor in packet loss
        if metrics.packet_loss_rate > self.config.packet_loss_threshold_percent:
            score *= 1.0 - metrics.packet_loss_rate / 100.0

        # Factor in signal quality
        quality_scores = {
            SignalQuality.EXCELLENT: 1.0,
            SignalQuality.GOOD: 0.9,
            SignalQuality.FAIR: 0.7,
            SignalQuality.POOR: 0.4,
            SignalQuality.UNUSABLE: 0.1,
        }
        score *= quality_scores.get(metrics.signal_quality, 0.5)

        # Factor in latency
        if metrics.avg_latency_ms > self.config.high_latency_threshold_ms:
            latency_factor = max(0.5, 1.0 - (metrics.avg_latency_ms / 1000.0))
            score *= latency_factor

        metrics.health_score = max(0.0, min(100.0, score))

        # Update overall health status based on score
        if metrics.health_score >= 90:
            metrics.overall_health = HealthStatus.HEALTHY
        elif metrics.health_score >= 70:
            metrics.overall_health = HealthStatus.WARNING
        else:
            metrics.overall_health = HealthStatus.CRITICAL

    async def _store_metrics_history(self, device_id: str) -> None:
        """Store current metrics in device history.

        Args:
            device_id: Device identifier
        """
        if device_id not in self.device_metrics:
            return

        # Create a copy of current metrics
        current_metrics = self.device_metrics[device_id]

        # Store in history
        if device_id not in self.device_history:
            self.device_history[device_id] = []

        self.device_history[device_id].append(current_metrics)

        # Limit history size
        if len(self.device_history[device_id]) > self.config.health_history_size:
            self.device_history[device_id] = self.device_history[device_id][
                -self.config.health_history_size :
            ]

    async def _check_device_alerts(self, device_id: str) -> None:
        """Check for alert conditions on a device.

        Args:
            device_id: Device identifier
        """
        if device_id not in self.device_metrics:
            return

        metrics = self.device_metrics[device_id]

        # Check packet loss
        if metrics.packet_loss_rate > self.config.packet_loss_threshold_percent:
            await self._generate_alert(
                device_id,
                AlertType.PACKET_LOSS,
                "warning",
                f"High packet loss: {metrics.packet_loss_rate:.1f}%",
            )

        # Check signal quality
        quality_threshold = self.config.low_signal_quality_threshold
        if metrics.signal_quality.value < quality_threshold.value:
            await self._generate_alert(
                device_id,
                AlertType.POOR_SIGNAL_QUALITY,
                "warning",
                f"Poor signal quality: {metrics.signal_quality.value}",
            )

        # Check impedance (if available)
        if metrics.impedance_quality < 80.0:  # Below 80% impedance quality
            await self._generate_alert(
                device_id,
                AlertType.HIGH_IMPEDANCE,
                "warning",
                f"High impedance detected: {100 - metrics.impedance_quality:.1f}% above threshold",
            )

    async def _generate_alert(
        self,
        device_id: str,
        alert_type: AlertType,
        severity: str,
        message: str,
        metrics: Dict[str, Any] = None,
    ) -> None:
        """Generate a health alert.

        Args:
            device_id: Device identifier
            alert_type: Type of alert
            severity: Alert severity
            message: Alert message
            metrics: Additional metrics data
        """
        # Check for alert cooldown
        if device_id in self.active_alerts:
            recent_alerts = [
                alert
                for alert in self.active_alerts[device_id]
                if (
                    alert.alert_type == alert_type
                    and not alert.resolved
                    and (datetime.utcnow() - alert.timestamp).total_seconds()
                    < self.config.alert_cooldown_seconds
                )
            ]

            if recent_alerts:
                return  # Skip duplicate alert within cooldown period

        # Create alert
        alert = HealthAlert(
            alert_type=alert_type,
            device_id=device_id,
            severity=severity,
            message=message,
            timestamp=datetime.utcnow(),
            metrics=metrics or {},
        )

        # Store alert
        if device_id not in self.active_alerts:
            self.active_alerts[device_id] = []

        self.active_alerts[device_id].append(alert)

        # Limit alerts per device
        if len(self.active_alerts[device_id]) > self.config.max_alerts_per_device:
            self.active_alerts[device_id] = self.active_alerts[device_id][
                -self.config.max_alerts_per_device :
            ]

        self.monitoring_stats["alerts_generated"] += 1

        # Call alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {str(e)}")

        logger.warning(f"Health alert for {device_id}: {alert_type.value} - {message}")

    async def _manage_alerts(self) -> None:
        """Manage and cleanup alerts."""
        current_time = datetime.utcnow()

        for device_id, alerts in self.active_alerts.items():
            # Auto-resolve old alerts
            for alert in alerts:
                if (
                    not alert.resolved
                    and (current_time - alert.timestamp).total_seconds() > 3600
                ):  # 1 hour
                    alert.resolved = True
                    alert.resolved_at = current_time
                    logger.info(
                        f"Auto-resolved old alert {alert.alert_type.value} for device {device_id}"
                    )

    async def _calculate_average_health_score(self) -> float:
        """Calculate average health score across all monitored devices.

        Returns:
            Average health score (0-100)
        """
        if not self.device_metrics:
            return 0.0

        scores = [metrics.health_score for metrics in self.device_metrics.values()]
        return statistics.mean(scores) if scores else 0.0
