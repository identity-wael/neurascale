"""Device health monitoring and metrics collection."""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
import statistics
from collections import deque

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Device health status levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class DeviceMetrics:
    """Real-time metrics for a device."""

    device_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Connection metrics
    connection_uptime: float = 0.0  # seconds
    connection_stability: float = 1.0  # 0-1 score
    reconnection_count: int = 0
    last_error: Optional[str] = None

    # Data metrics
    packets_received: int = 0
    packets_dropped: int = 0
    data_rate_hz: float = 0.0
    latency_ms: float = 0.0

    # Signal quality metrics
    average_snr_db: float = 0.0
    channels_good_quality: int = 0
    channels_total: int = 0
    impedance_check_time: Optional[datetime] = None

    # Resource metrics
    buffer_usage_percent: float = 0.0
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0

    # Battery metrics (if applicable)
    battery_level_percent: Optional[float] = None
    battery_charging: Optional[bool] = None
    estimated_battery_minutes: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "device_id": self.device_id,
            "timestamp": self.timestamp.isoformat(),
            "connection": {
                "uptime_seconds": self.connection_uptime,
                "stability": self.connection_stability,
                "reconnections": self.reconnection_count,
                "last_error": self.last_error,
            },
            "data": {
                "packets_received": self.packets_received,
                "packets_dropped": self.packets_dropped,
                "data_rate_hz": self.data_rate_hz,
                "latency_ms": self.latency_ms,
            },
            "signal_quality": {
                "average_snr_db": self.average_snr_db,
                "channels_good": self.channels_good_quality,
                "channels_total": self.channels_total,
                "last_impedance_check": (
                    self.impedance_check_time.isoformat()
                    if self.impedance_check_time
                    else None
                ),
            },
            "resources": {
                "buffer_usage_percent": self.buffer_usage_percent,
                "cpu_usage_percent": self.cpu_usage_percent,
                "memory_usage_mb": self.memory_usage_mb,
            },
            "battery": (
                {
                    "level_percent": self.battery_level_percent,
                    "charging": self.battery_charging,
                    "estimated_minutes": self.estimated_battery_minutes,
                }
                if self.battery_level_percent is not None
                else None
            ),
        }


@dataclass
class HealthAlert:
    """Health alert for a device."""

    device_id: str
    severity: HealthStatus
    category: str
    message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


class DeviceHealthMonitor:
    """Monitor device health and collect metrics."""

    def __init__(
        self,
        check_interval: float = 5.0,
        history_window_minutes: int = 60,
    ):
        """
        Initialize health monitor.

        Args:
            check_interval: Interval between health checks in seconds
            history_window_minutes: How long to keep historical metrics
        """
        self.check_interval = check_interval
        self.history_window = timedelta(minutes=history_window_minutes)

        # Current metrics for each device
        self._current_metrics: Dict[str, DeviceMetrics] = {}

        # Historical metrics (sliding window)
        self._metrics_history: Dict[str, deque] = {}

        # Health status
        self._health_status: Dict[str, HealthStatus] = {}

        # Alerts
        self._active_alerts: Dict[str, List[HealthAlert]] = {}

        # Callbacks
        self._health_callbacks: List[Callable[[str, HealthStatus], None]] = []
        self._alert_callbacks: List[Callable[[HealthAlert], None]] = []

        # Monitoring task
        self._monitor_task: Optional[asyncio.Task] = None
        self._stop_monitoring = asyncio.Event()

        # Device references (set by DeviceManager)
        self._devices: Dict[str, Any] = {}

        # Performance tracking
        self._packet_timestamps: Dict[str, deque] = {}
        self._error_counts: Dict[str, int] = {}
        self._connection_times: Dict[str, datetime] = {}

    def add_device(self, device_id: str, device: Any):
        """Add a device to monitor."""
        self._devices[device_id] = device
        self._current_metrics[device_id] = DeviceMetrics(device_id=device_id)
        self._metrics_history[device_id] = deque()
        self._health_status[device_id] = HealthStatus.UNKNOWN
        self._active_alerts[device_id] = []
        self._packet_timestamps[device_id] = deque(maxlen=100)
        self._error_counts[device_id] = 0

        # Set connection time if device is connected
        if hasattr(device, "is_connected") and device.is_connected():
            self._connection_times[device_id] = datetime.now(timezone.utc)

    def remove_device(self, device_id: str):
        """Remove a device from monitoring."""
        self._devices.pop(device_id, None)
        self._current_metrics.pop(device_id, None)
        self._metrics_history.pop(device_id, None)
        self._health_status.pop(device_id, None)
        self._active_alerts.pop(device_id, None)
        self._packet_timestamps.pop(device_id, None)
        self._error_counts.pop(device_id, None)
        self._connection_times.pop(device_id, None)

    def add_health_callback(self, callback: Callable[[str, HealthStatus], None]):
        """Add callback for health status changes."""
        self._health_callbacks.append(callback)

    def add_alert_callback(self, callback: Callable[[HealthAlert], None]):
        """Add callback for health alerts."""
        self._alert_callbacks.append(callback)

    async def start_monitoring(self):
        """Start health monitoring."""
        if self._monitor_task and not self._monitor_task.done():
            logger.warning("Health monitoring already running")
            return

        self._stop_monitoring.clear()
        self._monitor_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Started device health monitoring")

    async def stop_monitoring(self):
        """Stop health monitoring."""
        self._stop_monitoring.set()
        if self._monitor_task:
            await self._monitor_task
            self._monitor_task = None
        logger.info("Stopped device health monitoring")

    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while not self._stop_monitoring.is_set():
            try:
                # Check health for all devices
                for device_id in list(self._devices.keys()):
                    await self._check_device_health(device_id)

                # Clean up old metrics
                self._cleanup_old_metrics()

                # Wait for next check
                await asyncio.sleep(self.check_interval)

            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")

    async def _check_device_health(self, device_id: str):  # noqa: C901
        """Check health of a specific device."""
        device = self._devices.get(device_id)
        if not device:
            return

        metrics = self._current_metrics.get(device_id)
        if not metrics:
            return

        # Update connection metrics
        if hasattr(device, "is_connected") and device.is_connected():
            if device_id in self._connection_times:
                uptime = (
                    datetime.now(timezone.utc) - self._connection_times[device_id]
                ).total_seconds()
                metrics.connection_uptime = uptime
        else:
            metrics.connection_uptime = 0.0
            self._connection_times.pop(device_id, None)

        # Update data rate metrics
        if (
            device_id in self._packet_timestamps
            and len(self._packet_timestamps[device_id]) > 1
        ):
            timestamps = list(self._packet_timestamps[device_id])
            time_span = (timestamps[-1] - timestamps[0]).total_seconds()
            if time_span > 0:
                metrics.data_rate_hz = len(timestamps) / time_span

                # Calculate latency (time between packets)
                if len(timestamps) > 1:
                    intervals = [
                        (timestamps[i] - timestamps[i - 1]).total_seconds() * 1000
                        for i in range(1, len(timestamps))
                    ]
                    metrics.latency_ms = statistics.median(intervals)

        # Update signal quality metrics if available
        if hasattr(device, "_last_quality_metrics"):
            quality_metrics = device._last_quality_metrics
            if quality_metrics:
                snr_values = [m.snr_db for m in quality_metrics.values()]
                if snr_values:
                    metrics.average_snr_db = statistics.mean(snr_values)
                    metrics.channels_good_quality = sum(
                        1 for m in quality_metrics.values() if m.is_acceptable
                    )
                    metrics.channels_total = len(quality_metrics)

        # Update battery metrics if available
        if hasattr(device, "get_battery_level"):
            try:
                battery_level = await device.get_battery_level()
                metrics.battery_level_percent = battery_level
            except Exception:
                pass

        # Calculate connection stability
        if metrics.connection_uptime > 0:
            # Stability decreases with errors and reconnections
            error_factor = 1.0 / (1.0 + self._error_counts.get(device_id, 0) * 0.1)
            reconnect_factor = 1.0 / (1.0 + metrics.reconnection_count * 0.2)
            metrics.connection_stability = error_factor * reconnect_factor

        # Store metrics in history
        self._metrics_history[device_id].append(
            {
                "timestamp": metrics.timestamp,
                "metrics": DeviceMetrics(**metrics.__dict__),  # Copy
            }
        )

        # Evaluate health status
        new_status = self._evaluate_health_status(metrics)
        old_status = self._health_status.get(device_id, HealthStatus.UNKNOWN)

        if new_status != old_status:
            self._health_status[device_id] = new_status
            self._notify_health_change(device_id, new_status)

            # Generate alert if degraded
            if new_status in [
                HealthStatus.DEGRADED,
                HealthStatus.UNHEALTHY,
                HealthStatus.CRITICAL,
            ]:
                self._generate_health_alert(device_id, metrics, new_status)

    def _evaluate_health_status(  # noqa: C901
        self, metrics: DeviceMetrics
    ) -> HealthStatus:
        """Evaluate overall health status from metrics."""
        issues = []

        # Check connection stability
        if metrics.connection_stability < 0.5:
            issues.append("poor_connection")
        elif metrics.connection_stability < 0.8:
            issues.append("unstable_connection")

        # Check data rate
        if metrics.data_rate_hz == 0 and metrics.connection_uptime > 10:
            issues.append("no_data")
        elif metrics.data_rate_hz > 0 and metrics.data_rate_hz < 10:
            issues.append("low_data_rate")

        # Check packet loss
        if metrics.packets_received > 0:
            loss_rate = metrics.packets_dropped / metrics.packets_received
            if loss_rate > 0.1:
                issues.append("high_packet_loss")
            elif loss_rate > 0.05:
                issues.append("moderate_packet_loss")

        # Check signal quality
        if metrics.channels_total > 0:
            good_ratio = metrics.channels_good_quality / metrics.channels_total
            if good_ratio < 0.5:
                issues.append("poor_signal_quality")
            elif good_ratio < 0.8:
                issues.append("degraded_signal_quality")

        # Check battery (if applicable)
        if metrics.battery_level_percent is not None:
            if metrics.battery_level_percent < 10:
                issues.append("critical_battery")
            elif metrics.battery_level_percent < 20:
                issues.append("low_battery")

        # Determine overall status
        if "no_data" in issues or "critical_battery" in issues:
            return HealthStatus.CRITICAL
        elif len(issues) >= 3 or "poor_signal_quality" in issues:
            return HealthStatus.UNHEALTHY
        elif len(issues) >= 1:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.HEALTHY

    def _generate_health_alert(
        self, device_id: str, metrics: DeviceMetrics, status: HealthStatus
    ):
        """Generate health alert for device."""
        # Determine alert message
        if status == HealthStatus.CRITICAL:
            if metrics.data_rate_hz == 0:
                message = "Device not receiving data"
            elif metrics.battery_level_percent and metrics.battery_level_percent < 10:
                message = f"Critical battery level: {metrics.battery_level_percent}%"
            else:
                message = "Device in critical state"
        elif status == HealthStatus.UNHEALTHY:
            message = f"Device unhealthy: SNR {metrics.average_snr_db:.1f} dB, {metrics.channels_good_quality}/{metrics.channels_total} good channels"
        else:
            message = f"Device degraded: stability {metrics.connection_stability:.2f}"

        alert = HealthAlert(
            device_id=device_id,
            severity=status,
            category="health",
            message=message,
            metadata={"metrics": metrics.to_dict()},
        )

        # Store alert
        self._active_alerts[device_id].append(alert)

        # Notify callbacks
        self._notify_alert(alert)

    def _notify_health_change(self, device_id: str, status: HealthStatus):
        """Notify callbacks of health status change."""
        for callback in self._health_callbacks:
            try:
                callback(device_id, status)
            except Exception as e:
                logger.error(f"Error in health callback: {e}")

    def _notify_alert(self, alert: HealthAlert):
        """Notify callbacks of health alert."""
        for callback in self._alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")

    def _cleanup_old_metrics(self):
        """Remove metrics older than history window."""
        cutoff_time = datetime.now(timezone.utc) - self.history_window

        for device_id, history in self._metrics_history.items():
            while history and history[0]["timestamp"] < cutoff_time:
                history.popleft()

    def record_packet(self, device_id: str, timestamp: Optional[datetime] = None):
        """Record packet reception for data rate calculation."""
        if device_id in self._packet_timestamps:
            if timestamp is None:
                timestamp = datetime.now(timezone.utc)
            self._packet_timestamps[device_id].append(timestamp)

            # Update packet count
            if device_id in self._current_metrics:
                self._current_metrics[device_id].packets_received += 1

    def record_error(self, device_id: str, error: Exception):
        """Record device error."""
        if device_id in self._error_counts:
            self._error_counts[device_id] += 1

        if device_id in self._current_metrics:
            self._current_metrics[device_id].last_error = str(error)

    def record_reconnection(self, device_id: str):
        """Record device reconnection."""
        if device_id in self._current_metrics:
            self._current_metrics[device_id].reconnection_count += 1

        # Reset connection time
        self._connection_times[device_id] = datetime.now(timezone.utc)

    def get_device_metrics(self, device_id: str) -> Optional[DeviceMetrics]:
        """Get current metrics for a device."""
        return self._current_metrics.get(device_id)

    def get_device_health(self, device_id: str) -> HealthStatus:
        """Get current health status for a device."""
        return self._health_status.get(device_id, HealthStatus.UNKNOWN)

    def get_all_metrics(self) -> Dict[str, DeviceMetrics]:
        """Get current metrics for all devices."""
        return self._current_metrics.copy()

    def get_all_health_status(self) -> Dict[str, HealthStatus]:
        """Get health status for all devices."""
        return self._health_status.copy()

    def get_device_history(
        self, device_id: str, minutes: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get historical metrics for a device."""
        if device_id not in self._metrics_history:
            return []

        history = self._metrics_history[device_id]

        if minutes:
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
            return [entry for entry in history if entry["timestamp"] >= cutoff_time]
        else:
            return list(history)

    def get_active_alerts(self, device_id: Optional[str] = None) -> List[HealthAlert]:
        """Get active alerts for a device or all devices."""
        if device_id:
            return self._active_alerts.get(device_id, [])
        else:
            all_alerts = []
            for alerts in self._active_alerts.values():
                all_alerts.extend(alerts)
            return all_alerts

    def clear_alerts(self, device_id: Optional[str] = None):
        """Clear alerts for a device or all devices."""
        if device_id:
            self._active_alerts[device_id] = []
        else:
            for device_id in self._active_alerts:
                self._active_alerts[device_id] = []
