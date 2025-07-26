"""Custom business metrics collection for NeuraScale Neural Engine.

This module handles application-specific metrics that don't fit into
standard categories but are important for business monitoring.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of custom metrics."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class CustomMetric:
    """Custom business metric definition."""

    name: str
    metric_type: MetricType
    description: str
    unit: str
    tags: Dict[str, str] = field(default_factory=dict)

    # Current values
    value: Union[float, int] = 0
    count: int = 0

    # For histogram / timer metrics
    min_value: float = float("in")
    max_value: float = float("-in")
    sum_value: float = 0.0

    # Timestamps
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary format."""
        return {
            "name": self.name,
            "type": self.metric_type.value,
            "description": self.description,
            "unit": self.unit,
            "tags": self.tags,
            "value": self.value,
            "count": self.count,
            "min_value": self.min_value if self.min_value != float("in") else None,
            "max_value": self.max_value if self.max_value != float("-in") else None,
            "sum_value": self.sum_value,
            "average_value": self.sum_value / self.count if self.count > 0 else 0,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
        }


@dataclass
class MetricEvent:
    """Individual metric event / measurement."""

    metric_name: str
    value: Union[float, int]
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class CustomMetricsCollector:
    """Collects and manages custom business metrics."""

    def __init__(self, config):
        """Initialize custom metrics collector.

        Args:
            config: Monitoring configuration
        """
        self.config = config

        # Metrics storage
        self.metrics: Dict[str, CustomMetric] = {}
        self.metric_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))

        # Pre-defined neural engine metrics
        self._initialize_neural_metrics()

        # Collection statistics
        self.total_events_recorded = 0
        self.collection_errors = 0

        logger.info("CustomMetricsCollector initialized")

    def _initialize_neural_metrics(self) -> None:
        """Initialize standard neural engine metrics."""

        # Neural processing metrics
        self.register_metric(
            "neural_sessions_started",
            MetricType.COUNTER,
            "Total number of neural processing sessions started",
            "count",
        )

        self.register_metric(
            "neural_sessions_completed",
            MetricType.COUNTER,
            "Total number of neural processing sessions completed successfully",
            "count",
        )

        self.register_metric(
            "neural_sessions_failed",
            MetricType.COUNTER,
            "Total number of neural processing sessions that failed",
            "count",
        )

        self.register_metric(
            "neural_data_processed_mb",
            MetricType.COUNTER,
            "Total amount of neural data processed in megabytes",
            "MB",
        )

        self.register_metric(
            "active_neural_sessions",
            MetricType.GAUGE,
            "Number of currently active neural processing sessions",
            "count",
        )

        # Device management metrics
        self.register_metric(
            "devices_connected",
            MetricType.GAUGE,
            "Number of currently connected BCI devices",
            "count",
        )

        self.register_metric(
            "device_connections_total",
            MetricType.COUNTER,
            "Total number of device connection attempts",
            "count",
        )

        self.register_metric(
            "device_connection_failures",
            MetricType.COUNTER,
            "Total number of device connection failures",
            "count",
        )

        # User engagement metrics
        self.register_metric(
            "user_sessions_active",
            MetricType.GAUGE,
            "Number of currently active user sessions",
            "count",
        )

        self.register_metric(
            "user_logins_total",
            MetricType.COUNTER,
            "Total number of user login attempts",
            "count",
        )

        self.register_metric(
            "user_login_failures",
            MetricType.COUNTER,
            "Total number of failed login attempts",
            "count",
        )

        # Business metrics
        self.register_metric(
            "neural_insights_generated",
            MetricType.COUNTER,
            "Total number of neural insights generated for users",
            "count",
        )

        self.register_metric(
            "session_duration",
            MetricType.HISTOGRAM,
            "Duration of neural processing sessions",
            "seconds",
        )

        self.register_metric(
            "user_satisfaction_score",
            MetricType.GAUGE,
            "Average user satisfaction score",
            "score",
        )

    def register_metric(
        self,
        name: str,
        metric_type: MetricType,
        description: str,
        unit: str,
        tags: Optional[Dict[str, str]] = None,
    ) -> bool:
        """Register a new custom metric.

        Args:
            name: Unique metric name
            metric_type: Type of metric
            description: Human-readable description
            unit: Unit of measurement
            tags: Optional tags for the metric

        Returns:
            True if registration successful
        """
        try:
            if name in self.metrics:
                logger.warning(f"Metric {name} already exists")
                return False

            metric = CustomMetric(
                name=name,
                metric_type=metric_type,
                description=description,
                unit=unit,
                tags=tags or {},
            )

            self.metrics[name] = metric
            logger.info(f"Registered custom metric: {name}")
            return True

        except Exception as e:
            logger.error(f"Failed to register metric {name}: {str(e)}")
            self.collection_errors += 1
            return False

    def increment_counter(
        self,
        name: str,
        value: Union[float, int] = 1,
        tags: Optional[Dict[str, str]] = None,
    ) -> bool:
        """Increment a counter metric.

        Args:
            name: Metric name
            value: Value to increment by
            tags: Optional tags for this measurement

        Returns:
            True if increment successful
        """
        try:
            if name not in self.metrics:
                logger.warning(f"Metric {name} not found")
                return False

            metric = self.metrics[name]

            if metric.metric_type != MetricType.COUNTER:
                logger.error(f"Metric {name} is not a counter")
                return False

            # Update metric
            metric.value += value
            metric.count += 1
            metric.last_updated = datetime.utcnow()

            # Record event
            event = MetricEvent(
                metric_name=name,
                value=value,
                timestamp=datetime.utcnow(),
                tags=tags or {},
            )

            self.metric_history[name].append(event)
            self.total_events_recorded += 1

            return True

        except Exception as e:
            logger.error(f"Failed to increment counter {name}: {str(e)}")
            self.collection_errors += 1
            return False

    def set_gauge(
        self, name: str, value: Union[float, int], tags: Optional[Dict[str, str]] = None
    ) -> bool:
        """Set a gauge metric value.

        Args:
            name: Metric name
            value: Value to set
            tags: Optional tags for this measurement

        Returns:
            True if set successful
        """
        try:
            if name not in self.metrics:
                logger.warning(f"Metric {name} not found")
                return False

            metric = self.metrics[name]

            if metric.metric_type != MetricType.GAUGE:
                logger.error(f"Metric {name} is not a gauge")
                return False

            # Update metric
            metric.value = value
            metric.count += 1
            metric.last_updated = datetime.utcnow()

            # Record event
            event = MetricEvent(
                metric_name=name,
                value=value,
                timestamp=datetime.utcnow(),
                tags=tags or {},
            )

            self.metric_history[name].append(event)
            self.total_events_recorded += 1

            return True

        except Exception as e:
            logger.error(f"Failed to set gauge {name}: {str(e)}")
            self.collection_errors += 1
            return False

    def record_histogram(
        self, name: str, value: Union[float, int], tags: Optional[Dict[str, str]] = None
    ) -> bool:
        """Record a value in a histogram metric.

        Args:
            name: Metric name
            value: Value to record
            tags: Optional tags for this measurement

        Returns:
            True if record successful
        """
        try:
            if name not in self.metrics:
                logger.warning(f"Metric {name} not found")
                return False

            metric = self.metrics[name]

            if metric.metric_type != MetricType.HISTOGRAM:
                logger.error(f"Metric {name} is not a histogram")
                return False

            # Update metric statistics
            metric.count += 1
            metric.sum_value += value
            metric.value = metric.sum_value / metric.count  # Running average

            if value < metric.min_value:
                metric.min_value = value
            if value > metric.max_value:
                metric.max_value = value

            metric.last_updated = datetime.utcnow()

            # Record event
            event = MetricEvent(
                metric_name=name,
                value=value,
                timestamp=datetime.utcnow(),
                tags=tags or {},
            )

            self.metric_history[name].append(event)
            self.total_events_recorded += 1

            return True

        except Exception as e:
            logger.error(f"Failed to record histogram {name}: {str(e)}")
            self.collection_errors += 1
            return False

    def start_timer(self, name: str) -> Optional[str]:
        """Start a timer for a timer metric.

        Args:
            name: Metric name

        Returns:
            Timer ID if successful, None otherwise
        """
        try:
            if name not in self.metrics:
                logger.warning(f"Metric {name} not found")
                return None

            metric = self.metrics[name]

            if metric.metric_type != MetricType.TIMER:
                logger.error(f"Metric {name} is not a timer")
                return None

            # Create timer ID and store start time
            import uuid

            timer_id = str(uuid.uuid4())

            if not hasattr(self, "_active_timers"):
                self._active_timers = {}

            self._active_timers[timer_id] = {
                "metric_name": name,
                "start_time": datetime.utcnow(),
            }

            return timer_id

        except Exception as e:
            logger.error(f"Failed to start timer {name}: {str(e)}")
            self.collection_errors += 1
            return None

    def stop_timer(
        self, timer_id: str, tags: Optional[Dict[str, str]] = None
    ) -> Optional[float]:
        """Stop a timer and record the duration.

        Args:
            timer_id: Timer ID returned by start_timer
            tags: Optional tags for this measurement

        Returns:
            Duration in seconds if successful, None otherwise
        """
        try:
            if (
                not hasattr(self, "_active_timers")
                or timer_id not in self._active_timers
            ):
                logger.warning(f"Timer {timer_id} not found")
                return None

            timer_info = self._active_timers.pop(timer_id)
            name = timer_info["metric_name"]
            start_time = timer_info["start_time"]

            # Calculate duration
            duration = (datetime.utcnow() - start_time).total_seconds()

            # Record as histogram value
            self.record_histogram(name, duration, tags)

            return duration

        except Exception as e:
            logger.error(f"Failed to stop timer {timer_id}: {str(e)}")
            self.collection_errors += 1
            return None

    def get_metric(self, name: str) -> Optional[CustomMetric]:
        """Get a metric by name.

        Args:
            name: Metric name

        Returns:
            CustomMetric object or None if not found
        """
        return self.metrics.get(name)

    def get_all_metrics(self) -> List[CustomMetric]:
        """Get all registered metrics.

        Returns:
            List of CustomMetric objects
        """
        return list(self.metrics.values())

    def get_metric_summary(
        self, name: str, time_window_minutes: int = 60
    ) -> Dict[str, Any]:
        """Get summary statistics for a metric over a time window.

        Args:
            name: Metric name
            time_window_minutes: Time window for summary

        Returns:
            Summary statistics
        """
        try:
            if name not in self.metrics:
                return {"error": f"Metric {name} not found"}

            metric = self.metrics[name]

            # Get recent events
            cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)
            recent_events = [
                event
                for event in self.metric_history[name]
                if event.timestamp >= cutoff_time
            ]

            if not recent_events:
                return {
                    "metric_name": name,
                    "metric_type": metric.metric_type.value,
                    "time_window_minutes": time_window_minutes,
                    "events_count": 0,
                    "message": "No recent events",
                }

            values = [event.value for event in recent_events]

            summary = {
                "metric_name": name,
                "metric_type": metric.metric_type.value,
                "description": metric.description,
                "unit": metric.unit,
                "time_window_minutes": time_window_minutes,
                "events_count": len(recent_events),
                "current_value": metric.value,
            }

            if metric.metric_type in [MetricType.HISTOGRAM, MetricType.TIMER]:
                summary.update(
                    {
                        "min_value": min(values),
                        "max_value": max(values),
                        "average_value": statistics.mean(values),
                        "median_value": statistics.median(values),
                        "total_sum": sum(values),
                    }
                )

                if len(values) > 1:
                    summary["std_deviation"] = statistics.stdev(values)

            elif metric.metric_type == MetricType.COUNTER:
                summary.update(
                    {
                        "total_increments": len(recent_events),
                        "sum_increments": sum(values),
                        "rate_per_minute": (
                            sum(values) / time_window_minutes
                            if time_window_minutes > 0
                            else 0
                        ),
                    }
                )

            elif metric.metric_type == MetricType.GAUGE:
                summary.update(
                    {
                        "latest_value": values[-1] if values else None,
                        "min_value": min(values),
                        "max_value": max(values),
                        "average_value": statistics.mean(values),
                    }
                )

            return summary

        except Exception as e:
            logger.error(f"Failed to get metric summary for {name}: {str(e)}")
            return {"error": str(e)}

    def get_business_dashboard_data(self) -> Dict[str, Any]:  # noqa: C901
        """Get key business metrics for dashboard display.

        Returns:
            Business metrics summary
        """
        try:
            dashboard_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "neural_processing": {},
                "device_management": {},
                "user_engagement": {},
                "system_health": {},
            }

            # Neural processing metrics
            neural_metrics = [
                "neural_sessions_started",
                "neural_sessions_completed",
                "neural_sessions_failed",
                "active_neural_sessions",
                "neural_data_processed_mb",
            ]

            for metric_name in neural_metrics:
                if metric_name in self.metrics:
                    metric = self.metrics[metric_name]
                    dashboard_data["neural_processing"][metric_name] = {
                        "value": metric.value,
                        "unit": metric.unit,
                        "last_updated": metric.last_updated.isoformat(),
                    }

            # Device management metrics
            device_metrics = [
                "devices_connected",
                "device_connections_total",
                "device_connection_failures",
            ]

            for metric_name in device_metrics:
                if metric_name in self.metrics:
                    metric = self.metrics[metric_name]
                    dashboard_data["device_management"][metric_name] = {
                        "value": metric.value,
                        "unit": metric.unit,
                        "last_updated": metric.last_updated.isoformat(),
                    }

            # User engagement metrics
            user_metrics = [
                "user_sessions_active",
                "user_logins_total",
                "user_login_failures",
                "user_satisfaction_score",
            ]

            for metric_name in user_metrics:
                if metric_name in self.metrics:
                    metric = self.metrics[metric_name]
                    dashboard_data["user_engagement"][metric_name] = {
                        "value": metric.value,
                        "unit": metric.unit,
                        "last_updated": metric.last_updated.isoformat(),
                    }

            # Calculate derived metrics
            total_sessions = (
                dashboard_data["neural_processing"]
                .get("neural_sessions_started", {})
                .get("value", 0)
            )
            completed_sessions = (
                dashboard_data["neural_processing"]
                .get("neural_sessions_completed", {})
                .get("value", 0)
            )

            if total_sessions > 0:
                success_rate = (completed_sessions / total_sessions) * 100
                dashboard_data["neural_processing"]["success_rate"] = {
                    "value": success_rate,
                    "unit": "percent",
                }

            # Device connection success rate
            total_connections = (
                dashboard_data["device_management"]
                .get("device_connections_total", {})
                .get("value", 0)
            )
            failed_connections = (
                dashboard_data["device_management"]
                .get("device_connection_failures", {})
                .get("value", 0)
            )

            if total_connections > 0:
                connection_success_rate = (
                    (total_connections - failed_connections) / total_connections
                ) * 100
                dashboard_data["device_management"]["connection_success_rate"] = {
                    "value": connection_success_rate,
                    "unit": "percent",
                }

            return dashboard_data

        except Exception as e:
            logger.error(f"Failed to get business dashboard data: {str(e)}")
            return {"error": str(e)}

    def get_collector_stats(self) -> Dict[str, Any]:
        """Get collector performance statistics.

        Returns:
            Collector statistics
        """
        active_timers = 0
        if hasattr(self, "_active_timers"):
            active_timers = len(self._active_timers)

        return {
            "total_events_recorded": self.total_events_recorded,
            "collection_errors": self.collection_errors,
            "registered_metrics": len(self.metrics),
            "active_timers": active_timers,
            "metric_history_size": sum(
                len(history) for history in self.metric_history.values()
            ),
        }
