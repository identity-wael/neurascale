"""Device performance metrics collection for NeuraScale Neural Engine.

This module monitors BCI device performance including connection stability,
data rates, signal quality, and error rates.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)


class DeviceStatus(Enum):
    """Device connection status."""

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    ERROR = "error"
    UNKNOWN = "unknown"


class ConnectionType(Enum):
    """Device connection types."""

    USB = "usb"
    BLUETOOTH = "bluetooth"
    WIFI = "wifi"
    LSL = "lsl"
    SERIAL = "serial"


@dataclass
class DeviceMetrics:
    """BCI device performance metrics."""

    # Device identification
    device_id: str
    device_type: str
    connection_type: ConnectionType

    # Connection metrics
    connection_stability: float  # 0-1 score
    uptime_seconds: float
    reconnection_count: int = 0

    # Data flow metrics
    data_rate: float  # Hz (samples per second)
    expected_data_rate: float  # Expected Hz
    data_loss_percent: float = 0.0

    # Signal quality metrics
    signal_quality: float  # 0-1 score
    noise_level: float = 0.0
    artifact_count: int = 0

    # Error metrics
    error_rate: float  # errors per second
    total_errors: int = 0
    last_error_time: Optional[datetime] = None

    # Latency metrics (milliseconds)
    latency: float = 0.0
    latency_jitter: float = 0.0

    # Timestamps
    last_update: datetime = field(default_factory=datetime.utcnow)
    connected_at: Optional[datetime] = None

    # Additional metadata
    firmware_version: Optional[str] = None
    battery_level: Optional[float] = None
    temperature: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary format."""
        return {
            "device_id": self.device_id,
            "device_type": self.device_type,
            "connection_type": self.connection_type.value,
            "connection_stability": self.connection_stability,
            "uptime_seconds": self.uptime_seconds,
            "reconnection_count": self.reconnection_count,
            "data_rate_hz": self.data_rate,
            "expected_data_rate_hz": self.expected_data_rate,
            "data_loss_percent": self.data_loss_percent,
            "signal_quality": self.signal_quality,
            "noise_level": self.noise_level,
            "artifact_count": self.artifact_count,
            "error_rate": self.error_rate,
            "total_errors": self.total_errors,
            "last_error_time": (
                self.last_error_time.isoformat() if self.last_error_time else None
            ),
            "latency_ms": self.latency,
            "latency_jitter_ms": self.latency_jitter,
            "last_update": self.last_update.isoformat(),
            "connected_at": (
                self.connected_at.isoformat() if self.connected_at else None
            ),
            "firmware_version": self.firmware_version,
            "battery_level": self.battery_level,
            "temperature_c": self.temperature,
        }


@dataclass
class DeviceHealthStatus:
    """Overall device health assessment."""

    device_id: str
    overall_health: float  # 0-1 score
    status: DeviceStatus
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    last_check: datetime = field(default_factory=datetime.utcnow)


class DeviceMetricsCollector:
    """Collects and analyzes device performance metrics."""

    def __init__(self, config):
        """Initialize device metrics collector.

        Args:
            config: Monitoring configuration
        """
        self.config = config

        # Device tracking
        self.active_devices: Dict[str, DeviceMetrics] = {}
        self.device_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.connection_events: Dict[str, List[Dict]] = defaultdict(list)

        # Performance tracking
        self.data_rate_history: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=100)
        )
        self.latency_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.error_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))

        # Statistics
        self.total_devices_monitored = 0
        self.collection_errors = 0

        logger.info("DeviceMetricsCollector initialized")

    async def register_device(
        self,
        device_id: str,
        device_type: str,
        connection_type: ConnectionType,
        expected_rate: float = 250.0,
    ) -> bool:
        """Register a device for monitoring.

        Args:
            device_id: Unique device identifier
            device_type: Type of device (e.g., "OpenBCI_Cyton")
            connection_type: How device connects
            expected_rate: Expected data rate in Hz

        Returns:
            True if registration successful
        """
        try:
            # Create initial metrics
            metrics = DeviceMetrics(
                device_id=device_id,
                device_type=device_type,
                connection_type=connection_type,
                connection_stability=0.0,
                uptime_seconds=0.0,
                data_rate=0.0,
                expected_data_rate=expected_rate,
                signal_quality=0.0,
                error_rate=0.0,
                latency=0.0,
                connected_at=datetime.utcnow(),
            )

            self.active_devices[device_id] = metrics
            self.total_devices_monitored += 1

            # Log connection event
            self.connection_events[device_id].append(
                {
                    "event": "registered",
                    "timestamp": datetime.utcnow(),
                    "device_type": device_type,
                    "connection_type": connection_type.value,
                }
            )

            logger.info(f"Device {device_id} registered for monitoring")
            return True

        except Exception as e:
            logger.error(f"Failed to register device {device_id}: {str(e)}")
            self.collection_errors += 1
            return False

    async def unregister_device(self, device_id: str) -> bool:
        """Unregister a device from monitoring.

        Args:
            device_id: Device identifier to unregister

        Returns:
            True if unregistration successful
        """
        try:
            if device_id in self.active_devices:
                # Log disconnection event
                self.connection_events[device_id].append(
                    {
                        "event": "unregistered",
                        "timestamp": datetime.utcnow(),
                    }
                )

                # Archive final metrics
                final_metrics = self.active_devices[device_id]
                self.device_history[device_id].append(final_metrics.to_dict())

                # Remove from active monitoring
                del self.active_devices[device_id]

                logger.info(f"Device {device_id} unregistered")
                return True
            else:
                logger.warning(f"Device {device_id} not found for unregistration")
                return False

        except Exception as e:
            logger.error(f"Failed to unregister device {device_id}: {str(e)}")
            return False

    def monitor_device_connection(self, device_id: str, is_connected: bool) -> None:
        """Monitor device connection status.

        Args:
            device_id: Device identifier
            is_connected: Current connection status
        """
        try:
            if device_id not in self.active_devices:
                logger.warning(f"Device {device_id} not registered")
                return

            metrics = self.active_devices[device_id]
            now = datetime.utcnow()

            if is_connected:
                # Update uptime
                if metrics.connected_at:
                    metrics.uptime_seconds = (
                        now - metrics.connected_at
                    ).total_seconds()

                # Calculate connection stability (simple moving average)
                self._update_connection_stability(device_id, 1.0)

            else:
                # Log disconnection
                self.connection_events[device_id].append(
                    {
                        "event": "disconnected",
                        "timestamp": now,
                    }
                )

                metrics.reconnection_count += 1
                metrics.connected_at = None
                self._update_connection_stability(device_id, 0.0)

            metrics.last_update = now

        except Exception as e:
            logger.error(f"Failed to monitor connection for {device_id}: {str(e)}")
            self.collection_errors += 1

    def record_signal_quality(self, device_id: str, quality_score: float) -> None:
        """Record signal quality assessment.

        Args:
            device_id: Device identifier
            quality_score: Quality score (0-1)
        """
        try:
            if device_id not in self.active_devices:
                logger.warning(f"Device {device_id} not registered")
                return

            # Validate quality score
            quality_score = max(0.0, min(1.0, quality_score))

            metrics = self.active_devices[device_id]
            metrics.signal_quality = quality_score
            metrics.last_update = datetime.utcnow()

        except Exception as e:
            logger.error(f"Failed to record signal quality for {device_id}: {str(e)}")
            self.collection_errors += 1

    def track_data_rate(self, device_id: str, samples_per_second: float) -> None:
        """Track device data rate.

        Args:
            device_id: Device identifier
            samples_per_second: Current data rate in Hz
        """
        try:
            if device_id not in self.active_devices:
                logger.warning(f"Device {device_id} not registered")
                return

            metrics = self.active_devices[device_id]
            metrics.data_rate = samples_per_second

            # Calculate data loss percentage
            if metrics.expected_data_rate > 0:
                loss_percent = max(
                    0.0,
                    (metrics.expected_data_rate - samples_per_second)
                    / metrics.expected_data_rate
                    * 100,
                )
                metrics.data_loss_percent = loss_percent

            # Store in history for trend analysis
            self.data_rate_history[device_id].append(
                {
                    "rate": samples_per_second,
                    "timestamp": datetime.utcnow(),
                }
            )

            metrics.last_update = datetime.utcnow()

        except Exception as e:
            logger.error(f"Failed to track data rate for {device_id}: {str(e)}")
            self.collection_errors += 1

    def record_device_error(
        self, device_id: str, error_type: str, error_details: Optional[str] = None
    ) -> None:
        """Record device error.

        Args:
            device_id: Device identifier
            error_type: Type of error
            error_details: Optional error details
        """
        try:
            if device_id not in self.active_devices:
                logger.warning(f"Device {device_id} not registered")
                return

            metrics = self.active_devices[device_id]
            metrics.total_errors += 1
            metrics.last_error_time = datetime.utcnow()

            # Store error in history
            self.error_history[device_id].append(
                {
                    "type": error_type,
                    "details": error_details,
                    "timestamp": datetime.utcnow(),
                }
            )

            # Calculate error rate (errors per minute over last 5 minutes)
            recent_errors = [
                error
                for error in self.error_history[device_id]
                if (datetime.utcnow() - error["timestamp"]).total_seconds() <= 300
            ]
            metrics.error_rate = len(recent_errors) / 5.0  # errors per minute

            metrics.last_update = datetime.utcnow()

            logger.warning(f"Device error recorded for {device_id}: {error_type}")

        except Exception as e:
            logger.error(f"Failed to record error for {device_id}: {str(e)}")
            self.collection_errors += 1

    def record_latency(self, device_id: str, latency_ms: float) -> None:
        """Record device communication latency.

        Args:
            device_id: Device identifier
            latency_ms: Latency in milliseconds
        """
        try:
            if device_id not in self.active_devices:
                logger.warning(f"Device {device_id} not registered")
                return

            metrics = self.active_devices[device_id]
            metrics.latency = latency_ms

            # Store in history for jitter calculation
            self.latency_history[device_id].append(
                {
                    "latency": latency_ms,
                    "timestamp": datetime.utcnow(),
                }
            )

            # Calculate jitter (standard deviation of recent latencies)
            if len(self.latency_history[device_id]) >= 10:
                recent_latencies = [
                    entry["latency"]
                    for entry in list(self.latency_history[device_id])[-20:]
                ]
                metrics.latency_jitter = statistics.stdev(recent_latencies)

            metrics.last_update = datetime.utcnow()

        except Exception as e:
            logger.error(f"Failed to record latency for {device_id}: {str(e)}")
            self.collection_errors += 1

    def calculate_connection_stability(self, device_id: str) -> float:
        """Calculate connection stability score.

        Args:
            device_id: Device identifier

        Returns:
            Stability score (0-1)
        """
        try:
            if device_id not in self.active_devices:
                return 0.0

            # Look at connection events in the last hour
            cutoff_time = datetime.utcnow() - timedelta(hours=1)
            recent_events = [
                event
                for event in self.connection_events[device_id]
                if event["timestamp"] >= cutoff_time
            ]

            if not recent_events:
                return 1.0  # No recent events = stable

            # Count disconnection events
            disconnections = [
                event
                for event in recent_events
                if event["event"] in ["disconnected", "error"]
            ]

            # Stability decreases with more disconnections
            if len(disconnections) == 0:
                return 1.0
            elif len(disconnections) <= 2:
                return 0.8
            elif len(disconnections) <= 5:
                return 0.5
            else:
                return 0.2

        except Exception as e:
            logger.error(f"Failed to calculate stability for {device_id}: {str(e)}")
            return 0.0

    async def collect_device_metrics(self, device_id: str) -> Optional[DeviceMetrics]:
        """Collect current metrics for a device.

        Args:
            device_id: Device identifier

        Returns:
            DeviceMetrics object or None if not found
        """
        try:
            if device_id not in self.active_devices:
                logger.warning(f"Device {device_id} not found")
                return None

            metrics = self.active_devices[device_id]

            # Update calculated fields
            metrics.connection_stability = self.calculate_connection_stability(
                device_id
            )

            # Update uptime if connected
            if metrics.connected_at:
                metrics.uptime_seconds = (
                    datetime.utcnow() - metrics.connected_at
                ).total_seconds()

            return metrics

        except Exception as e:
            logger.error(f"Failed to collect metrics for {device_id}: {str(e)}")
            self.collection_errors += 1
            return None

    async def assess_device_health(  # noqa: C901
        self, device_id: str
    ) -> Optional[DeviceHealthStatus]:
        """Assess overall device health.

        Args:
            device_id: Device identifier

        Returns:
            DeviceHealthStatus or None if device not found
        """
        try:
            metrics = await self.collect_device_metrics(device_id)
            if not metrics:
                return None

            # Calculate overall health score
            health_factors = []
            issues = []
            recommendations = []

            # Connection stability (30% weight)
            health_factors.append(metrics.connection_stability * 0.3)
            if metrics.connection_stability < 0.8:
                issues.append("Poor connection stability")
                recommendations.append("Check device connection and cables")

            # Signal quality (25% weight)
            health_factors.append(metrics.signal_quality * 0.25)
            if metrics.signal_quality < 0.7:
                issues.append("Low signal quality")
                recommendations.append("Check electrode impedance and placement")

            # Data rate performance (20% weight)
            rate_performance = (
                min(1.0, metrics.data_rate / metrics.expected_data_rate)
                if metrics.expected_data_rate > 0
                else 0.0
            )
            health_factors.append(rate_performance * 0.2)
            if rate_performance < 0.9:
                issues.append("Data rate below expected")
                recommendations.append("Check device configuration and connection")

            # Error rate (15% weight)
            error_factor = max(
                0.0, 1.0 - (metrics.error_rate / 10.0)
            )  # 10 errors / min = 0 health
            health_factors.append(error_factor * 0.15)
            if metrics.error_rate > 1.0:
                issues.append("High error rate")
                recommendations.append("Check device logs and connection")

            # Latency (10% weight)
            latency_factor = max(
                0.0, 1.0 - (metrics.latency / 1000.0)
            )  # 1000ms = 0 health
            health_factors.append(latency_factor * 0.1)
            if metrics.latency > 100:
                issues.append("High latency")
                recommendations.append(
                    "Check network connection and device responsiveness"
                )

            # Calculate overall health
            overall_health = sum(health_factors)

            # Determine status
            if overall_health >= 0.8:
                status = DeviceStatus.CONNECTED
            elif overall_health >= 0.5:
                status = DeviceStatus.CONNECTED  # Connected but with issues
            else:
                status = DeviceStatus.ERROR

            return DeviceHealthStatus(
                device_id=device_id,
                overall_health=overall_health,
                status=status,
                issues=issues,
                recommendations=recommendations,
            )

        except Exception as e:
            logger.error(f"Failed to assess health for {device_id}: {str(e)}")
            return None

    def get_all_devices(self) -> List[str]:
        """Get list of all monitored devices.

        Returns:
            List of device IDs
        """
        return list(self.active_devices.keys())

    def get_device_summary(self) -> Dict[str, Any]:
        """Get summary of all devices.

        Returns:
            Summary statistics
        """
        try:
            connected_count = len(
                [
                    device
                    for device in self.active_devices.values()
                    if device.connected_at is not None
                ]
            )

            avg_stability = (
                statistics.mean(
                    [
                        device.connection_stability
                        for device in self.active_devices.values()
                    ]
                )
                if self.active_devices
                else 0.0
            )

            avg_quality = (
                statistics.mean(
                    [device.signal_quality for device in self.active_devices.values()]
                )
                if self.active_devices
                else 0.0
            )

            total_errors = sum(
                [device.total_errors for device in self.active_devices.values()]
            )

            return {
                "total_devices": len(self.active_devices),
                "connected_devices": connected_count,
                "average_stability": avg_stability,
                "average_signal_quality": avg_quality,
                "total_errors": total_errors,
                "collection_errors": self.collection_errors,
            }

        except Exception as e:
            logger.error(f"Failed to get device summary: {str(e)}")
            return {"error": str(e)}

    def _update_connection_stability(
        self, device_id: str, stability_sample: float
    ) -> None:
        """Update connection stability using exponential moving average."""
        if device_id in self.active_devices:
            current = self.active_devices[device_id].connection_stability
            # Use exponential moving average with alpha=0.1
            self.active_devices[device_id].connection_stability = (0.9 * current) + (
                0.1 * stability_sample
            )
