"""System performance metrics collection for NeuraScale Neural Engine.

This module monitors system-level performance including CPU, memory,
disk, network utilization, and application metrics.
"""

import psutil
import time
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import logging
from collections import deque
import statistics

logger = logging.getLogger(__name__)


@dataclass
class SystemMetrics:
    """System performance metrics snapshot."""

    # CPU metrics
    cpu_percent: float
    cpu_per_core: List[float]
    load_average: List[float] = field(default_factory=list)

    # Memory metrics
    memory_percent: float
    memory_available_mb: float
    memory_used_mb: float
    memory_total_mb: float
    swap_percent: float = 0.0

    # Disk metrics
    disk_usage_percent: float
    disk_free_gb: float
    disk_total_gb: float
    disk_io_read_mb: float = 0.0
    disk_io_write_mb: float = 0.0

    # Network metrics
    network_bytes_sent: float = 0.0
    network_bytes_recv: float = 0.0
    network_connections: int = 0

    # Process metrics
    process_count: int = 0
    neural_engine_cpu: float = 0.0
    neural_engine_memory_mb: float = 0.0

    # Timestamp
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary format."""
        return {
            "cpu_percent": self.cpu_percent,
            "cpu_per_core": self.cpu_per_core,
            "load_average": self.load_average,
            "memory_percent": self.memory_percent,
            "memory_available_mb": self.memory_available_mb,
            "memory_used_mb": self.memory_used_mb,
            "memory_total_mb": self.memory_total_mb,
            "swap_percent": self.swap_percent,
            "disk_usage_percent": self.disk_usage_percent,
            "disk_free_gb": self.disk_free_gb,
            "disk_total_gb": self.disk_total_gb,
            "disk_io_read_mb": self.disk_io_read_mb,
            "disk_io_write_mb": self.disk_io_write_mb,
            "network_bytes_sent": self.network_bytes_sent,
            "network_bytes_recv": self.network_bytes_recv,
            "network_connections": self.network_connections,
            "process_count": self.process_count,
            "neural_engine_cpu": self.neural_engine_cpu,
            "neural_engine_memory_mb": self.neural_engine_memory_mb,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ApplicationMetrics:
    """Neural Engine application-specific metrics."""

    # API metrics
    active_sessions: int = 0
    api_requests_per_minute: float = 0.0
    avg_response_time_ms: float = 0.0
    error_rate_percent: float = 0.0

    # Database metrics
    db_connections_active: int = 0
    db_connections_max: int = 0
    db_query_avg_time_ms: float = 0.0
    db_slow_queries: int = 0

    # Cache metrics
    cache_hit_rate: float = 0.0
    cache_size_mb: float = 0.0
    cache_evictions: int = 0

    # Processing metrics
    neural_sessions_active: int = 0
    device_connections_active: int = 0
    processing_queue_size: int = 0

    # Timestamp
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary format."""
        return {
            "active_sessions": self.active_sessions,
            "api_requests_per_minute": self.api_requests_per_minute,
            "avg_response_time_ms": self.avg_response_time_ms,
            "error_rate_percent": self.error_rate_percent,
            "db_connections_active": self.db_connections_active,
            "db_connections_max": self.db_connections_max,
            "db_query_avg_time_ms": self.db_query_avg_time_ms,
            "db_slow_queries": self.db_slow_queries,
            "cache_hit_rate": self.cache_hit_rate,
            "cache_size_mb": self.cache_size_mb,
            "cache_evictions": self.cache_evictions,
            "neural_sessions_active": self.neural_sessions_active,
            "device_connections_active": self.device_connections_active,
            "processing_queue_size": self.processing_queue_size,
            "timestamp": self.timestamp.isoformat(),
        }


class SystemMetricsCollector:
    """Collects system and application performance metrics."""

    def __init__(self, config):
        """Initialize system metrics collector.

        Args:
            config: Monitoring configuration
        """
        self.config = config

        # Metrics history
        self.system_history: deque = deque(maxlen=1000)
        self.app_history: deque = deque(maxlen=1000)

        # Previous values for delta calculations
        self._prev_disk_io = None
        self._prev_network_io = None
        self._prev_timestamp = None

        # Process tracking
        self._neural_engine_process = None
        self._find_neural_engine_process()

        # Collection statistics
        self.collection_count = 0
        self.collection_errors = 0

        logger.info("SystemMetricsCollector initialized")

    def _find_neural_engine_process(self) -> None:
        """Find the Neural Engine process for monitoring."""
        try:
            current_process = psutil.Process()
            self._neural_engine_process = current_process
            logger.info(f"Neural Engine process found: PID {current_process.pid}")
        except Exception as e:
            logger.warning(f"Could not find Neural Engine process: {str(e)}")

    async def collect_system_metrics(self) -> Optional[SystemMetrics]:
        """Collect current system metrics.

        Returns:
            SystemMetrics object or None if collection fails
        """
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_per_core = psutil.cpu_percent(interval=0.1, percpu=True)

            # Load average (Unix-like systems)
            load_avg = []
            try:
                load_avg = list(psutil.getloadavg())
            except AttributeError:
                # Windows doesn't have load average
                pass

            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()

            # Disk metrics
            disk_usage = psutil.disk_usage("/")

            # Disk I/O metrics
            disk_io_read_mb = 0.0
            disk_io_write_mb = 0.0
            try:
                disk_io = psutil.disk_io_counters()
                if disk_io and self._prev_disk_io and self._prev_timestamp:
                    time_delta = time.time() - self._prev_timestamp
                    if time_delta > 0:
                        read_delta = disk_io.read_bytes - self._prev_disk_io.read_bytes
                        write_delta = (
                            disk_io.write_bytes - self._prev_disk_io.write_bytes
                        )
                        disk_io_read_mb = (read_delta / time_delta) / (1024 * 1024)
                        disk_io_write_mb = (write_delta / time_delta) / (1024 * 1024)
                self._prev_disk_io = disk_io
            except Exception as e:
                logger.debug(f"Could not get disk I/O metrics: {str(e)}")

            # Network metrics
            network_bytes_sent = 0.0
            network_bytes_recv = 0.0
            try:
                network_io = psutil.net_io_counters()
                if network_io and self._prev_network_io and self._prev_timestamp:
                    time_delta = time.time() - self._prev_timestamp
                    if time_delta > 0:
                        sent_delta = (
                            network_io.bytes_sent - self._prev_network_io.bytes_sent
                        )
                        recv_delta = (
                            network_io.bytes_recv - self._prev_network_io.bytes_recv
                        )
                        network_bytes_sent = sent_delta / time_delta
                        network_bytes_recv = recv_delta / time_delta
                self._prev_network_io = network_io
            except Exception as e:
                logger.debug(f"Could not get network I/O metrics: {str(e)}")

            # Network connections
            network_connections = len(psutil.net_connections())

            # Process metrics
            process_count = len(psutil.pids())
            neural_engine_cpu = 0.0
            neural_engine_memory_mb = 0.0

            if self._neural_engine_process:
                try:
                    neural_engine_cpu = self._neural_engine_process.cpu_percent()
                    neural_engine_memory_mb = (
                        self._neural_engine_process.memory_info().rss / (1024 * 1024)
                    )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    # Process may have died, try to find it again
                    self._find_neural_engine_process()

            # Update timestamp
            self._prev_timestamp = time.time()

            # Create metrics object
            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                cpu_per_core=cpu_per_core,
                load_average=load_avg,
                memory_percent=memory.percent,
                memory_available_mb=memory.available / (1024 * 1024),
                memory_used_mb=memory.used / (1024 * 1024),
                memory_total_mb=memory.total / (1024 * 1024),
                swap_percent=swap.percent,
                disk_usage_percent=disk_usage.percent,
                disk_free_gb=disk_usage.free / (1024 * 1024 * 1024),
                disk_total_gb=disk_usage.total / (1024 * 1024 * 1024),
                disk_io_read_mb=disk_io_read_mb,
                disk_io_write_mb=disk_io_write_mb,
                network_bytes_sent=network_bytes_sent,
                network_bytes_recv=network_bytes_recv,
                network_connections=network_connections,
                process_count=process_count,
                neural_engine_cpu=neural_engine_cpu,
                neural_engine_memory_mb=neural_engine_memory_mb,
            )

            # Store in history
            self.system_history.append(metrics.to_dict())
            self.collection_count += 1

            return metrics

        except Exception as e:
            logger.error(f"Failed to collect system metrics: {str(e)}")
            self.collection_errors += 1
            return None

    async def collect_application_metrics(self) -> Optional[ApplicationMetrics]:
        """Collect application-specific metrics.

        Returns:
            ApplicationMetrics object or None if collection fails
        """
        try:
            # These would typically be collected from the application itself
            # For now, we'll return placeholder metrics

            metrics = ApplicationMetrics(
                active_sessions=0,  # Would be provided by session manager
                api_requests_per_minute=0.0,  # Would be tracked by API layer
                avg_response_time_ms=0.0,  # Would be tracked by middleware
                error_rate_percent=0.0,  # Would be calculated from error logs
                db_connections_active=0,  # Would be provided by database pool
                db_connections_max=100,  # Configuration value
                db_query_avg_time_ms=0.0,  # Would be tracked by ORM/database
                db_slow_queries=0,  # Would be tracked by database monitoring
                cache_hit_rate=0.0,  # Would be provided by cache layer
                cache_size_mb=0.0,  # Would be provided by cache layer
                cache_evictions=0,  # Would be tracked by cache
                neural_sessions_active=0,  # Would be provided by neural processing
                device_connections_active=0,  # Would be provided by device manager
                processing_queue_size=0,  # Would be provided by processing queue
            )

            # Store in history
            self.app_history.append(metrics.to_dict())

            return metrics

        except Exception as e:
            logger.error(f"Failed to collect application metrics: {str(e)}")
            self.collection_errors += 1
            return None

    async def collect_all_metrics(self) -> Dict[str, Any]:
        """Collect both system and application metrics.

        Returns:
            Combined metrics dictionary
        """
        try:
            system_metrics = await self.collect_system_metrics()
            app_metrics = await self.collect_application_metrics()

            result = {
                "collection_timestamp": datetime.utcnow().isoformat(),
                "system_metrics": system_metrics.to_dict() if system_metrics else None,
                "application_metrics": app_metrics.to_dict() if app_metrics else None,
            }

            return result

        except Exception as e:
            logger.error(f"Failed to collect all metrics: {str(e)}")
            return {"error": str(e)}

    def get_system_summary(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Get system performance summary over a time window.

        Args:
            time_window_minutes: Time window for summary

        Returns:
            Summary statistics
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)

            # Filter recent metrics
            recent_metrics = [
                metric
                for metric in self.system_history
                if datetime.fromisoformat(metric["timestamp"]) >= cutoff_time
            ]

            if not recent_metrics:
                return {"message": "No recent metrics available"}

            # Calculate averages
            avg_cpu = statistics.mean([m["cpu_percent"] for m in recent_metrics])
            avg_memory = statistics.mean([m["memory_percent"] for m in recent_metrics])
            avg_disk = statistics.mean(
                [m["disk_usage_percent"] for m in recent_metrics]
            )

            # Calculate peaks
            max_cpu = max([m["cpu_percent"] for m in recent_metrics])
            max_memory = max([m["memory_percent"] for m in recent_metrics])

            # Neural Engine specific
            avg_neural_cpu = statistics.mean(
                [m["neural_engine_cpu"] for m in recent_metrics]
            )
            avg_neural_memory = statistics.mean(
                [m["neural_engine_memory_mb"] for m in recent_metrics]
            )

            return {
                "time_window_minutes": time_window_minutes,
                "metrics_count": len(recent_metrics),
                "cpu_average": avg_cpu,
                "cpu_peak": max_cpu,
                "memory_average": avg_memory,
                "memory_peak": max_memory,
                "disk_usage": avg_disk,
                "neural_engine_cpu_average": avg_neural_cpu,
                "neural_engine_memory_mb_average": avg_neural_memory,
                "collection_count": self.collection_count,
                "collection_errors": self.collection_errors,
            }

        except Exception as e:
            logger.error(f"Failed to get system summary: {str(e)}")
            return {"error": str(e)}

    def check_resource_alerts(self) -> List[Dict[str, Any]]:
        """Check for resource utilization alerts.

        Returns:
            List of alert conditions
        """
        alerts = []

        try:
            if not self.system_history:
                return alerts

            # Get latest metrics
            latest = self.system_history[-1]

            # CPU alerts
            if latest["cpu_percent"] > self.config.max_cpu_usage_percent:
                alerts.append(
                    {
                        "type": "high_cpu_usage",
                        "severity": "warning",
                        "message": f"CPU usage at {latest['cpu_percent']:.1f}%",
                        "threshold": self.config.max_cpu_usage_percent,
                        "current_value": latest["cpu_percent"],
                    }
                )

            # Memory alerts
            if latest["memory_percent"] > self.config.max_memory_usage_percent:
                alerts.append(
                    {
                        "type": "high_memory_usage",
                        "severity": "warning",
                        "message": f"Memory usage at {latest['memory_percent']:.1f}%",
                        "threshold": self.config.max_memory_usage_percent,
                        "current_value": latest["memory_percent"],
                    }
                )

            # Disk space alerts
            if latest["disk_usage_percent"] > 90:
                alerts.append(
                    {
                        "type": "low_disk_space",
                        "severity": "critical",
                        "message": f"Disk usage at {latest['disk_usage_percent']:.1f}%",
                        "threshold": 90,
                        "current_value": latest["disk_usage_percent"],
                    }
                )

            # Neural Engine specific alerts
            if latest["neural_engine_cpu"] > 80:
                alerts.append(
                    {
                        "type": "high_neural_engine_cpu",
                        "severity": "warning",
                        "message": f"Neural Engine CPU usage at {latest['neural_engine_cpu']:.1f}%",
                        "threshold": 80,
                        "current_value": latest["neural_engine_cpu"],
                    }
                )

        except Exception as e:
            logger.error(f"Failed to check resource alerts: {str(e)}")
            alerts.append(
                {
                    "type": "monitoring_error",
                    "severity": "error",
                    "message": f"Failed to check alerts: {str(e)}",
                }
            )

        return alerts

    def get_performance_trends(
        self, metric_name: str, hours: int = 24
    ) -> Dict[str, Any]:
        """Get performance trends for a specific metric.

        Args:
            metric_name: Name of the metric to analyze
            hours: Number of hours to analyze

        Returns:
            Trend analysis results
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)

            # Filter recent metrics
            recent_metrics = [
                metric
                for metric in self.system_history
                if datetime.fromisoformat(metric["timestamp"]) >= cutoff_time
                and metric_name in metric
            ]

            if len(recent_metrics) < 2:
                return {"message": "Insufficient data for trend analysis"}

            values = [metric[metric_name] for metric in recent_metrics]
            timestamps = [
                datetime.fromisoformat(metric["timestamp"]) for metric in recent_metrics
            ]

            # Simple trend analysis
            first_half = values[: len(values) // 2]
            second_half = values[len(values) // 2 :]

            first_avg = statistics.mean(first_half)
            second_avg = statistics.mean(second_half)

            trend_direction = "increasing" if second_avg > first_avg else "decreasing"
            trend_magnitude = (
                abs(second_avg - first_avg) / first_avg * 100 if first_avg > 0 else 0
            )

            return {
                "metric_name": metric_name,
                "time_period_hours": hours,
                "data_points": len(values),
                "min_value": min(values),
                "max_value": max(values),
                "average_value": statistics.mean(values),
                "trend_direction": trend_direction,
                "trend_magnitude_percent": trend_magnitude,
                "first_period_average": first_avg,
                "second_period_average": second_avg,
            }

        except Exception as e:
            logger.error(f"Failed to get performance trends: {str(e)}")
            return {"error": str(e)}

    def get_collector_stats(self) -> Dict[str, Any]:
        """Get collector performance statistics.

        Returns:
            Collector statistics
        """
        return {
            "collection_count": self.collection_count,
            "collection_errors": self.collection_errors,
            "system_history_size": len(self.system_history),
            "app_history_size": len(self.app_history),
            "neural_engine_process_found": self._neural_engine_process is not None,
        }
