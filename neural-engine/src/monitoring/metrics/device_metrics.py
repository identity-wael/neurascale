"""
BCI device performance metrics collection
"""

import time
import logging
from datetime import datetime
from typing import Dict, List, Set
from dataclasses import dataclass
from collections import defaultdict, deque
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class DeviceMetrics:
    """BCI device performance metrics"""

    device_id: str
    connection_stability: float  # 0-1 score
    data_rate: float  # Hz
    signal_quality: float  # 0-1 score
    error_rate: float  # errors/second
    latency: float  # milliseconds
    packets_received: int
    packets_lost: int
    last_update: datetime

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for export"""
        return {
            "connection_stability": self.connection_stability,
            "data_rate_hz": self.data_rate,
            "signal_quality": self.signal_quality,
            "error_rate": self.error_rate,
            "latency_ms": self.latency,
            "packet_loss_rate": self.packets_lost
            / max(1, self.packets_received + self.packets_lost),
        }


@dataclass
class DeviceError:
    """Device error record"""

    timestamp: datetime
    error_type: str
    error_message: str
    severity: str  # "low", "medium", "high", "critical"


class DeviceMetricsCollector:
    """Collects and tracks device performance metrics"""

    def __init__(self, stability_window_size: int = 100):
        """
        Initialize device metrics collector

        Args:
            stability_window_size: Window size for stability calculation
        """
        self.stability_window_size = stability_window_size

        # Device tracking
        self._active_devices: Set[str] = set()
        self._device_metrics: Dict[str, DeviceMetrics] = {}

        # Connection tracking
        self._connection_times: Dict[str, datetime] = {}
        self._disconnection_counts: Dict[str, int] = defaultdict(int)

        # Data rate tracking
        self._sample_counts: Dict[str, int] = defaultdict(int)
        self._rate_calc_times: Dict[str, float] = {}

        # Signal quality tracking
        self._signal_quality_history: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=stability_window_size)
        )

        # Error tracking
        self._device_errors: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self._error_counts: Dict[str, int] = defaultdict(int)
        self._error_rate_times: Dict[str, float] = {}

        # Latency tracking
        self._latency_history: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=stability_window_size)
        )

        # Packet tracking
        self._packets_received: Dict[str, int] = defaultdict(int)
        self._packets_lost: Dict[str, int] = defaultdict(int)

        logger.info("Device metrics collector initialized")

    def register_device(self, device_id: str) -> None:
        """
        Register a new device for monitoring

        Args:
            device_id: Device identifier
        """
        self._active_devices.add(device_id)
        self._connection_times[device_id] = datetime.now()
        self._rate_calc_times[device_id] = time.time()
        self._error_rate_times[device_id] = time.time()

        logger.info(f"Device {device_id} registered for monitoring")

    def unregister_device(self, device_id: str) -> None:
        """
        Unregister device from monitoring

        Args:
            device_id: Device identifier
        """
        self._active_devices.discard(device_id)

        # Clean up device data
        if device_id in self._device_metrics:
            del self._device_metrics[device_id]

        logger.info(f"Device {device_id} unregistered from monitoring")

    def monitor_device_connection(self, device_id: str) -> None:
        """
        Monitor device connection status

        Args:
            device_id: Device identifier
        """
        if device_id not in self._active_devices:
            self.register_device(device_id)

        # Update last seen time
        self._connection_times[device_id] = datetime.now()

    def record_device_disconnection(self, device_id: str) -> None:
        """
        Record device disconnection event

        Args:
            device_id: Device identifier
        """
        self._disconnection_counts[device_id] += 1
        logger.warning(f"Device {device_id} disconnected")

    def record_signal_quality(self, device_id: str, quality_score: float) -> None:
        """
        Record signal quality measurement

        Args:
            device_id: Device identifier
            quality_score: Quality score (0-1)
        """
        quality_score = max(0.0, min(1.0, quality_score))  # Clamp to [0, 1]
        self._signal_quality_history[device_id].append(quality_score)

        if quality_score < 0.5:
            logger.warning(f"Low signal quality on device {device_id}: {quality_score}")

    def track_data_rate(self, device_id: str, samples_per_second: float) -> None:
        """
        Track device data rate

        Args:
            device_id: Device identifier
            samples_per_second: Current data rate
        """
        self._sample_counts[device_id] += int(samples_per_second)

    def record_device_error(
        self,
        device_id: str,
        error_type: str,
        error_message: str = "",
        severity: str = "medium",
    ) -> None:
        """
        Record device error

        Args:
            device_id: Device identifier
            error_type: Type of error
            error_message: Error details
            severity: Error severity
        """
        error = DeviceError(
            timestamp=datetime.now(),
            error_type=error_type,
            error_message=error_message,
            severity=severity,
        )

        self._device_errors[device_id].append(error)
        self._error_counts[device_id] += 1

        if severity in ["high", "critical"]:
            logger.error(f"Device {device_id} error: {error_type} - {error_message}")

    def record_device_latency(self, device_id: str, latency_ms: float) -> None:
        """
        Record device communication latency

        Args:
            device_id: Device identifier
            latency_ms: Latency in milliseconds
        """
        self._latency_history[device_id].append(latency_ms)

        if latency_ms > 100:
            logger.warning(f"High latency on device {device_id}: {latency_ms}ms")

    def record_packet_stats(
        self, device_id: str, packets_received: int, packets_lost: int
    ) -> None:
        """
        Record packet statistics

        Args:
            device_id: Device identifier
            packets_received: Number of packets received
            packets_lost: Number of packets lost
        """
        self._packets_received[device_id] += packets_received
        self._packets_lost[device_id] += packets_lost

    def calculate_connection_stability(self, device_id: str) -> float:
        """
        Calculate connection stability score

        Args:
            device_id: Device identifier

        Returns:
            Stability score (0-1)
        """
        if device_id not in self._connection_times:
            return 0.0

        # Factor 1: Connection duration
        connection_duration = datetime.now() - self._connection_times[device_id]
        duration_score = min(
            1.0, connection_duration.total_seconds() / 3600
        )  # 1 hour = perfect

        # Factor 2: Disconnection frequency
        disconnections = self._disconnection_counts[device_id]
        disconnection_score = 1.0 / (1.0 + disconnections * 0.1)

        # Factor 3: Signal quality consistency
        if self._signal_quality_history[device_id]:
            quality_values = list(self._signal_quality_history[device_id])
            quality_std = np.std(quality_values)
            consistency_score = 1.0 - min(1.0, quality_std * 2)
        else:
            consistency_score = 0.5

        # Factor 4: Packet loss rate
        total_packets = (
            self._packets_received[device_id] + self._packets_lost[device_id]
        )
        if total_packets > 0:
            packet_loss_rate = self._packets_lost[device_id] / total_packets
            packet_score = 1.0 - packet_loss_rate
        else:
            packet_score = 1.0

        # Weighted average
        stability = (
            duration_score * 0.2
            + disconnection_score * 0.3
            + consistency_score * 0.3
            + packet_score * 0.2
        )

        return float(max(0.0, min(1.0, stability)))

    async def get_device_metrics(self, device_id: str) -> DeviceMetrics:
        """
        Get current metrics for device

        Args:
            device_id: Device identifier

        Returns:
            Device metrics
        """
        # Calculate connection stability
        stability = self.calculate_connection_stability(device_id)

        # Calculate data rate
        current_time = time.time()
        if device_id in self._rate_calc_times:
            time_diff = current_time - self._rate_calc_times[device_id]
            if time_diff > 0:
                data_rate = self._sample_counts[device_id] / time_diff
            else:
                data_rate = 0.0
        else:
            data_rate = 0.0

        # Reset counters
        self._sample_counts[device_id] = 0
        self._rate_calc_times[device_id] = current_time

        # Calculate average signal quality
        if self._signal_quality_history[device_id]:
            signal_quality = np.mean(list(self._signal_quality_history[device_id]))
        else:
            signal_quality = 0.0

        # Calculate error rate
        if device_id in self._error_rate_times:
            time_diff = current_time - self._error_rate_times[device_id]
            if time_diff > 0:
                error_rate = self._error_counts[device_id] / time_diff
            else:
                error_rate = 0.0
        else:
            error_rate = 0.0

        # Reset error counter
        self._error_counts[device_id] = 0
        self._error_rate_times[device_id] = current_time

        # Calculate average latency
        if self._latency_history[device_id]:
            latency = np.mean(list(self._latency_history[device_id]))
        else:
            latency = 0.0

        metrics = DeviceMetrics(
            device_id=device_id,
            connection_stability=stability,
            data_rate=data_rate,
            signal_quality=signal_quality,
            error_rate=error_rate,
            latency=latency,
            packets_received=self._packets_received[device_id],
            packets_lost=self._packets_lost[device_id],
            last_update=datetime.now(),
        )

        # Cache metrics
        self._device_metrics[device_id] = metrics

        return metrics

    def get_active_devices(self) -> List[str]:
        """Get list of active device IDs"""
        return list(self._active_devices)

    def get_device_summary(
        self, device_id: str, start_time: datetime, end_time: datetime
    ) -> Dict[str, float]:
        """
        Get device metrics summary for time range

        Args:
            device_id: Device identifier
            start_time: Start of time range
            end_time: End of time range

        Returns:
            Summary statistics
        """
        if device_id not in self._device_metrics:
            return {}

        # Get latest metrics as approximation
        # In production, we'd store time-series data
        metrics = self._device_metrics[device_id]

        summary = {
            "avg_stability": metrics.connection_stability,
            "avg_data_rate": metrics.data_rate,
            "avg_signal_quality": metrics.signal_quality,
            "avg_error_rate": metrics.error_rate,
            "avg_latency": metrics.latency,
            "total_packets_received": metrics.packets_received,
            "total_packets_lost": metrics.packets_lost,
            "packet_loss_rate": metrics.packets_lost / max(1, metrics.packets_received),
        }

        # Add error analysis
        if device_id in self._device_errors:
            errors = list(self._device_errors[device_id])
            error_types = [e.error_type for e in errors]

            # Count by type
            error_counts = {}
            for error_type in set(error_types):
                error_counts[f"errors_{error_type}"] = error_types.count(error_type)

            summary.update(error_counts)

        return summary

    def get_device_health_score(self, device_id: str) -> float:
        """
        Calculate overall device health score

        Args:
            device_id: Device identifier

        Returns:
            Health score (0-1)
        """
        if device_id not in self._device_metrics:
            return 0.0

        metrics = self._device_metrics[device_id]

        # Weight different factors
        health_score = (
            metrics.connection_stability * 0.3
            + metrics.signal_quality * 0.3
            + (1.0 - min(1.0, metrics.error_rate / 10)) * 0.2
            + (1.0 - min(1.0, metrics.latency / 100)) * 0.2
        )

        return max(0.0, min(1.0, health_score))

    def get_problem_devices(self, threshold: float = 0.7) -> List[str]:
        """
        Get list of devices with health score below threshold

        Args:
            threshold: Health score threshold

        Returns:
            List of problematic device IDs
        """
        problem_devices = []

        for device_id in self._active_devices:
            health_score = self.get_device_health_score(device_id)
            if health_score < threshold:
                problem_devices.append(device_id)

        return problem_devices

    def reset_device_metrics(self, device_id: str) -> None:
        """
        Reset metrics for specific device

        Args:
            device_id: Device identifier
        """
        self._sample_counts[device_id] = 0
        self._error_counts[device_id] = 0
        self._packets_received[device_id] = 0
        self._packets_lost[device_id] = 0
        self._disconnection_counts[device_id] = 0

        if device_id in self._signal_quality_history:
            self._signal_quality_history[device_id].clear()

        if device_id in self._latency_history:
            self._latency_history[device_id].clear()

        if device_id in self._device_errors:
            self._device_errors[device_id].clear()

        logger.info(f"Metrics reset for device {device_id}")
