"""
System resource metrics collection
"""

import psutil
import time
import logging
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass
from collections import deque
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class SystemMetrics:
    """System resource metrics"""

    cpu_usage_percent: float
    memory_usage_mb: float
    memory_usage_percent: float
    disk_usage_percent: float
    network_bytes_sent: int
    network_bytes_recv: int
    active_connections: int
    thread_count: int
    process_count: int
    timestamp: datetime

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for export"""
        return {
            "cpu_usage_percent": self.cpu_usage_percent,
            "memory_usage_mb": self.memory_usage_mb,
            "memory_usage_percent": self.memory_usage_percent,
            "disk_usage_percent": self.disk_usage_percent,
            "network_bytes_sent": self.network_bytes_sent,
            "network_bytes_recv": self.network_bytes_recv,
            "active_connections": self.active_connections,
            "thread_count": self.thread_count,
            "process_count": self.process_count,
        }


class SystemMetricsCollector:
    """Collects and tracks system resource metrics"""

    def __init__(self, history_size: int = 1000):
        """
        Initialize system metrics collector

        Args:
            history_size: Number of historical metrics to keep
        """
        self.history_size = history_size

        # Metric histories
        self.cpu_history: deque = deque(maxlen=history_size)
        self.memory_history: deque = deque(maxlen=history_size)
        self.disk_history: deque = deque(maxlen=history_size)
        self.network_sent_history: deque = deque(maxlen=history_size)
        self.network_recv_history: deque = deque(maxlen=history_size)

        # Network baseline for rate calculation
        self._last_network_sent = 0
        self._last_network_recv = 0
        self._last_network_time = time.time()

        # Process tracking
        self._process = psutil.Process()

        # Initialize CPU percent (requires interval)
        self._process.cpu_percent(interval=None)

        logger.info("System metrics collector initialized")

    def collect_cpu_metrics(self) -> float:
        """
        Collect CPU usage metrics

        Returns:
            CPU usage percentage
        """
        # System-wide CPU usage
        cpu_percent = psutil.cpu_percent(interval=0.1)

        # Process-specific CPU usage (initialize tracking)
        self._process.cpu_percent(interval=None)

        self.cpu_history.append(cpu_percent)

        if cpu_percent > 80:
            logger.warning(f"High CPU usage detected: {cpu_percent}%")

        return float(cpu_percent)

    def collect_memory_metrics(self) -> tuple[float, float]:
        """
        Collect memory usage metrics

        Returns:
            Tuple of (memory_mb, memory_percent)
        """
        # System memory
        memory = psutil.virtual_memory()

        # Process memory
        process_memory = self._process.memory_info()

        memory_mb = process_memory.rss / 1024 / 1024
        memory_percent = memory.percent

        self.memory_history.append((memory_mb, memory_percent))

        if memory_percent > 80:
            logger.warning(f"High memory usage: {memory_percent}%")

        return memory_mb, memory_percent

    def collect_disk_metrics(self) -> float:
        """
        Collect disk usage metrics

        Returns:
            Disk usage percentage
        """
        # Get disk usage for root partition
        disk = psutil.disk_usage("/")
        disk_percent = disk.percent

        self.disk_history.append(disk_percent)

        if disk_percent > 90:
            logger.warning(f"High disk usage: {disk_percent}%")

        return float(disk_percent)

    def collect_network_metrics(self) -> tuple[int, int]:
        """
        Collect network usage metrics

        Returns:
            Tuple of (bytes_sent, bytes_recv)
        """
        # Get network counters
        net_io = psutil.net_io_counters()

        bytes_sent = net_io.bytes_sent
        bytes_recv = net_io.bytes_recv

        # Calculate rates
        current_time = time.time()
        time_diff = current_time - self._last_network_time

        if time_diff > 0:
            send_rate = (bytes_sent - self._last_network_sent) / time_diff
            recv_rate = (bytes_recv - self._last_network_recv) / time_diff

            self.network_sent_history.append(send_rate)
            self.network_recv_history.append(recv_rate)

        self._last_network_sent = bytes_sent
        self._last_network_recv = bytes_recv
        self._last_network_time = current_time

        return bytes_sent, bytes_recv

    def collect_connection_metrics(self) -> int:
        """
        Collect network connection metrics

        Returns:
            Number of active connections
        """
        connections = psutil.net_connections()
        active_connections = len([c for c in connections if c.status == "ESTABLISHED"])

        return active_connections

    def collect_process_metrics(self) -> tuple[int, int]:
        """
        Collect process and thread metrics

        Returns:
            Tuple of (thread_count, process_count)
        """
        # Current process threads
        thread_count = self._process.num_threads()

        # System-wide process count
        process_count = len(psutil.pids())

        return thread_count, process_count

    async def collect_current_metrics(self) -> SystemMetrics:
        """
        Collect all current system metrics

        Returns:
            Current system metrics snapshot
        """
        # Collect all metrics
        cpu_percent = self.collect_cpu_metrics()
        memory_mb, memory_percent = self.collect_memory_metrics()
        disk_percent = self.collect_disk_metrics()
        bytes_sent, bytes_recv = self.collect_network_metrics()
        active_connections = self.collect_connection_metrics()
        thread_count, process_count = self.collect_process_metrics()

        return SystemMetrics(
            cpu_usage_percent=cpu_percent,
            memory_usage_mb=memory_mb,
            memory_usage_percent=memory_percent,
            disk_usage_percent=disk_percent,
            network_bytes_sent=bytes_sent,
            network_bytes_recv=bytes_recv,
            active_connections=active_connections,
            thread_count=thread_count,
            process_count=process_count,
            timestamp=datetime.now(),
        )

    def get_metrics_summary(
        self, start_time: datetime, end_time: datetime
    ) -> Dict[str, float]:
        """
        Get system metrics summary for time range

        Args:
            start_time: Start of time range
            end_time: End of time range

        Returns:
            Summary statistics
        """
        summary = {}

        # CPU statistics
        if self.cpu_history:
            cpu_values = list(self.cpu_history)
            summary["avg_cpu_usage"] = np.mean(cpu_values)
            summary["max_cpu_usage"] = np.max(cpu_values)
            summary["p95_cpu_usage"] = np.percentile(cpu_values, 95)

        # Memory statistics
        if self.memory_history:
            memory_values = [m[1] for m in self.memory_history]  # percent values
            memory_mb_values = [m[0] for m in self.memory_history]
            summary["avg_memory_usage"] = np.mean(memory_values)
            summary["max_memory_usage"] = np.max(memory_values)
            summary["avg_memory_mb"] = np.mean(memory_mb_values)
            summary["max_memory_mb"] = np.max(memory_mb_values)

        # Disk statistics
        if self.disk_history:
            disk_values = list(self.disk_history)
            summary["avg_disk_usage"] = np.mean(disk_values)
            summary["max_disk_usage"] = np.max(disk_values)

        # Network statistics
        if self.network_sent_history:
            sent_values = list(self.network_sent_history)
            recv_values = list(self.network_recv_history)
            summary["avg_network_send_rate"] = np.mean(sent_values)
            summary["max_network_send_rate"] = np.max(sent_values)
            summary["avg_network_recv_rate"] = np.mean(recv_values)
            summary["max_network_recv_rate"] = np.max(recv_values)

        return summary

    def get_resource_alerts(self) -> List[Dict[str, Any]]:
        """
        Check for resource constraint alerts

        Returns:
            List of resource alerts
        """
        alerts = []

        # Check current metrics
        current_cpu = psutil.cpu_percent(interval=0.1)
        current_memory = psutil.virtual_memory().percent
        current_disk = psutil.disk_usage("/").percent

        # CPU alert
        if current_cpu > 90:
            alerts.append(
                {
                    "type": "cpu",
                    "severity": "critical",
                    "message": f"CPU usage critical: {current_cpu}%",
                    "value": current_cpu,
                }
            )
        elif current_cpu > 80:
            alerts.append(
                {
                    "type": "cpu",
                    "severity": "warning",
                    "message": f"CPU usage high: {current_cpu}%",
                    "value": current_cpu,
                }
            )

        # Memory alert
        if current_memory > 90:
            alerts.append(
                {
                    "type": "memory",
                    "severity": "critical",
                    "message": f"Memory usage critical: {current_memory}%",
                    "value": current_memory,
                }
            )
        elif current_memory > 80:
            alerts.append(
                {
                    "type": "memory",
                    "severity": "warning",
                    "message": f"Memory usage high: {current_memory}%",
                    "value": current_memory,
                }
            )

        # Disk alert
        if current_disk > 95:
            alerts.append(
                {
                    "type": "disk",
                    "severity": "critical",
                    "message": f"Disk usage critical: {current_disk}%",
                    "value": current_disk,
                }
            )
        elif current_disk > 90:
            alerts.append(
                {
                    "type": "disk",
                    "severity": "warning",
                    "message": f"Disk usage high: {current_disk}%",
                    "value": current_disk,
                }
            )

        return alerts

    def get_performance_recommendations(self) -> List[str]:
        """
        Generate system performance recommendations

        Returns:
            List of recommendations
        """
        recommendations = []

        # Analyze CPU trends
        if self.cpu_history:
            avg_cpu = np.mean(list(self.cpu_history))
            if avg_cpu > 70:
                recommendations.append(
                    "Consider optimizing CPU-intensive operations or scaling compute resources"
                )

        # Analyze memory trends
        if self.memory_history:
            memory_percents = [m[1] for m in self.memory_history]
            avg_memory = np.mean(memory_percents)
            if avg_memory > 70:
                recommendations.append(
                    "Memory usage trending high - review memory allocation and consider optimization"
                )

        # Check for memory leaks
        if len(self.memory_history) > 100:
            recent_memory = [m[0] for m in list(self.memory_history)[-100:]]
            memory_trend = np.polyfit(range(len(recent_memory)), recent_memory, 1)[0]
            if memory_trend > 0.1:  # Growing by >0.1MB per sample
                recommendations.append(
                    "Potential memory leak detected - memory usage increasing steadily"
                )

        # Network recommendations
        if self.network_sent_history:
            avg_send_rate = np.mean(list(self.network_sent_history))
            if avg_send_rate > 10_000_000:  # 10MB/s
                recommendations.append(
                    "High network output detected - consider data compression or batching"
                )

        return recommendations

    def reset_metrics(self) -> None:
        """Reset all metric histories"""
        self.cpu_history.clear()
        self.memory_history.clear()
        self.disk_history.clear()
        self.network_sent_history.clear()
        self.network_recv_history.clear()

        # Reset network baselines
        net_io = psutil.net_io_counters()
        self._last_network_sent = net_io.bytes_sent
        self._last_network_recv = net_io.bytes_recv
        self._last_network_time = time.time()

        logger.info("System metrics reset")
