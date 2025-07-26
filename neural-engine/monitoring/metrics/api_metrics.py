"""API performance metrics collection for NeuraScale Neural Engine.

This module tracks API endpoint performance including response times,
error rates, and throughput metrics.
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, DefaultDict
from dataclasses import dataclass, field
from collections import defaultdict, deque
import logging
import statistics

logger = logging.getLogger(__name__)


@dataclass
class APIMetrics:
    """API endpoint performance metrics."""

    endpoint: str
    method: str

    # Request metrics
    total_requests: int = 0
    requests_per_minute: float = 0.0

    # Response time metrics (milliseconds)
    avg_response_time: float = 0.0
    min_response_time: float = float("inf")
    max_response_time: float = 0.0
    p50_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0

    # Status code distribution
    status_2xx: int = 0
    status_3xx: int = 0
    status_4xx: int = 0
    status_5xx: int = 0

    # Error metrics
    error_rate: float = 0.0
    error_count: int = 0

    # Timestamps
    first_request: Optional[datetime] = None
    last_request: Optional[datetime] = None
    last_updated: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary format."""
        return {
            "endpoint": self.endpoint,
            "method": self.method,
            "total_requests": self.total_requests,
            "requests_per_minute": self.requests_per_minute,
            "avg_response_time_ms": self.avg_response_time,
            "min_response_time_ms": (
                self.min_response_time if self.min_response_time != float("inf") else 0
            ),
            "max_response_time_ms": self.max_response_time,
            "p50_response_time_ms": self.p50_response_time,
            "p95_response_time_ms": self.p95_response_time,
            "p99_response_time_ms": self.p99_response_time,
            "status_2xx": self.status_2xx,
            "status_3xx": self.status_3xx,
            "status_4xx": self.status_4xx,
            "status_5xx": self.status_5xx,
            "error_rate": self.error_rate,
            "error_count": self.error_count,
            "first_request": (
                self.first_request.isoformat() if self.first_request else None
            ),
            "last_request": (
                self.last_request.isoformat() if self.last_request else None
            ),
            "last_updated": self.last_updated.isoformat(),
        }


@dataclass
class RequestEvent:
    """Individual API request event."""

    timestamp: datetime
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_size: Optional[int] = None
    response_size: Optional[int] = None


class APIMetricsCollector:
    """Collects and analyzes API performance metrics."""

    def __init__(self, config):
        """Initialize API metrics collector.

        Args:
            config: Monitoring configuration
        """
        self.config = config

        # Metrics storage
        self.endpoint_metrics: Dict[str, APIMetrics] = {}
        self.request_history: deque = deque(maxlen=10000)
        self.response_times: DefaultDict[str, deque] = defaultdict(
            lambda: deque(maxlen=1000)
        )

        # Real-time tracking
        self.active_requests: Dict[str, float] = {}  # request_id -> start_time
        self.request_counter = 0

        # Collection statistics
        self.total_requests_tracked = 0
        self.collection_errors = 0

        logger.info("APIMetricsCollector initialized")

    def start_request_tracking(
        self, request_id: str, endpoint: str, method: str
    ) -> None:
        """Start tracking a request.

        Args:
            request_id: Unique request identifier
            endpoint: API endpoint path
            method: HTTP method
        """
        try:
            self.active_requests[request_id] = time.perf_counter()
            self.request_counter += 1

        except Exception as e:
            logger.error(f"Failed to start request tracking: {str(e)}")
            self.collection_errors += 1

    def end_request_tracking(
        self,
        request_id: str,
        endpoint: str,
        method: str,
        status_code: int,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_size: Optional[int] = None,
        response_size: Optional[int] = None,
    ) -> Optional[float]:
        """End tracking a request and record metrics.

        Args:
            request_id: Unique request identifier
            endpoint: API endpoint path
            method: HTTP method
            status_code: HTTP response status code
            user_id: Optional user identifier
            ip_address: Optional client IP
            user_agent: Optional user agent string
            request_size: Optional request body size
            response_size: Optional response body size

        Returns:
            Response time in milliseconds or None if tracking failed
        """
        try:
            if request_id not in self.active_requests:
                logger.warning(f"Request {request_id} not found in active tracking")
                return None

            # Calculate response time
            start_time = self.active_requests.pop(request_id)
            response_time_ms = (time.perf_counter() - start_time) * 1000

            # Create request event
            event = RequestEvent(
                timestamp=datetime.utcnow(),
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                response_time_ms=response_time_ms,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                request_size=request_size,
                response_size=response_size,
            )

            # Store in history
            self.request_history.append(event)

            # Update endpoint metrics
            self._update_endpoint_metrics(event)

            # Store response time for percentile calculations
            endpoint_key = f"{method} {endpoint}"
            self.response_times[endpoint_key].append(response_time_ms)

            self.total_requests_tracked += 1

            return response_time_ms

        except Exception as e:
            logger.error(f"Failed to end request tracking: {str(e)}")
            self.collection_errors += 1
            return None

    def record_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        response_time_ms: float,
        timestamp: Optional[datetime] = None,
        **kwargs,
    ) -> None:
        """Record a completed request directly.

        Args:
            endpoint: API endpoint path
            method: HTTP method
            status_code: HTTP response status code
            response_time_ms: Response time in milliseconds
            timestamp: Optional timestamp (defaults to now)
            **kwargs: Additional request metadata
        """
        try:
            if timestamp is None:
                timestamp = datetime.utcnow()

            event = RequestEvent(
                timestamp=timestamp,
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                response_time_ms=response_time_ms,
                user_id=kwargs.get("user_id"),
                ip_address=kwargs.get("ip_address"),
                user_agent=kwargs.get("user_agent"),
                request_size=kwargs.get("request_size"),
                response_size=kwargs.get("response_size"),
            )

            # Store in history
            self.request_history.append(event)

            # Update endpoint metrics
            self._update_endpoint_metrics(event)

            # Store response time for percentile calculations
            endpoint_key = f"{method} {endpoint}"
            self.response_times[endpoint_key].append(response_time_ms)

            self.total_requests_tracked += 1

        except Exception as e:
            logger.error(f"Failed to record request: {str(e)}")
            self.collection_errors += 1

    def get_endpoint_metrics(self, endpoint: str, method: str) -> Optional[APIMetrics]:
        """Get metrics for a specific endpoint.

        Args:
            endpoint: API endpoint path
            method: HTTP method

        Returns:
            APIMetrics object or None if not found
        """
        endpoint_key = f"{method} {endpoint}"
        return self.endpoint_metrics.get(endpoint_key)

    def get_all_endpoint_metrics(self) -> List[APIMetrics]:
        """Get metrics for all tracked endpoints.

        Returns:
            List of APIMetrics objects
        """
        return list(self.endpoint_metrics.values())

    def get_endpoint_summary(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Get summary of API performance over a time window.

        Args:
            time_window_minutes: Time window for summary

        Returns:
            Summary statistics
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)

            # Filter recent requests
            recent_requests = [
                req for req in self.request_history if req.timestamp >= cutoff_time
            ]

            if not recent_requests:
                return {"message": "No recent requests"}

            # Calculate overall statistics
            total_requests = len(recent_requests)
            avg_response_time = statistics.mean(
                [req.response_time_ms for req in recent_requests]
            )

            # Status code distribution
            status_counts = defaultdict(int)
            for req in recent_requests:
                status_family = f"{req.status_code // 100}xx"
                status_counts[status_family] += 1

            # Error rate
            error_requests = [req for req in recent_requests if req.status_code >= 400]
            error_rate = (
                (len(error_requests) / total_requests * 100)
                if total_requests > 0
                else 0
            )

            # Requests per minute
            time_span_minutes = max(1, time_window_minutes)
            requests_per_minute = total_requests / time_span_minutes

            # Top endpoints by request count
            endpoint_counts = defaultdict(int)
            for req in recent_requests:
                endpoint_key = f"{req.method} {req.endpoint}"
                endpoint_counts[endpoint_key] += 1

            top_endpoints = sorted(
                endpoint_counts.items(), key=lambda x: x[1], reverse=True
            )[:10]

            # Slowest endpoints
            endpoint_response_times = defaultdict(list)
            for req in recent_requests:
                endpoint_key = f"{req.method} {req.endpoint}"
                endpoint_response_times[endpoint_key].append(req.response_time_ms)

            slowest_endpoints = []
            for endpoint, times in endpoint_response_times.items():
                if times:
                    avg_time = statistics.mean(times)
                    slowest_endpoints.append((endpoint, avg_time))

            slowest_endpoints.sort(key=lambda x: x[1], reverse=True)
            slowest_endpoints = slowest_endpoints[:10]

            return {
                "time_window_minutes": time_window_minutes,
                "total_requests": total_requests,
                "requests_per_minute": requests_per_minute,
                "avg_response_time_ms": avg_response_time,
                "error_rate_percent": error_rate,
                "status_distribution": dict(status_counts),
                "top_endpoints": top_endpoints,
                "slowest_endpoints": slowest_endpoints,
            }

        except Exception as e:
            logger.error(f"Failed to get endpoint summary: {str(e)}")
            return {"error": str(e)}

    def get_error_analysis(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Analyze API errors over a time window.

        Args:
            time_window_minutes: Time window for analysis

        Returns:
            Error analysis results
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)

            # Filter recent error requests
            error_requests = [
                req
                for req in self.request_history
                if req.timestamp >= cutoff_time and req.status_code >= 400
            ]

            if not error_requests:
                return {"message": "No recent errors"}

            # Group errors by status code
            status_groups = defaultdict(list)
            for req in error_requests:
                status_groups[req.status_code].append(req)

            # Group errors by endpoint
            endpoint_groups = defaultdict(list)
            for req in error_requests:
                endpoint_key = f"{req.method} {req.endpoint}"
                endpoint_groups[endpoint_key].append(req)

            # Error patterns by time
            error_timeline = defaultdict(int)
            for req in error_requests:
                # Group by hour
                hour_key = req.timestamp.replace(minute=0, second=0, microsecond=0)
                error_timeline[hour_key] += 1

            return {
                "time_window_minutes": time_window_minutes,
                "total_errors": len(error_requests),
                "errors_by_status": {
                    status: len(requests) for status, requests in status_groups.items()
                },
                "errors_by_endpoint": {
                    endpoint: len(requests)
                    for endpoint, requests in endpoint_groups.items()
                },
                "error_timeline": {
                    hour.isoformat(): count for hour, count in error_timeline.items()
                },
                "most_common_errors": [
                    (status, len(requests))
                    for status, requests in sorted(
                        status_groups.items(), key=lambda x: len(x[1]), reverse=True
                    )[:5]
                ],
            }

        except Exception as e:
            logger.error(f"Failed to analyze errors: {str(e)}")
            return {"error": str(e)}

    def get_performance_alerts(self) -> List[Dict[str, Any]]:
        """Check for performance-related alerts.

        Returns:
            List of performance alerts
        """
        alerts = []

        try:
            # Check recent requests (last 5 minutes)
            cutoff_time = datetime.utcnow() - timedelta(minutes=5)
            recent_requests = [
                req for req in self.request_history if req.timestamp >= cutoff_time
            ]

            if not recent_requests:
                return alerts

            # High error rate alert
            error_requests = [req for req in recent_requests if req.status_code >= 400]
            error_rate = (
                (len(error_requests) / len(recent_requests) * 100)
                if recent_requests
                else 0
            )

            if error_rate > 10:  # More than 10% errors
                alerts.append(
                    {
                        "type": "high_error_rate",
                        "severity": "critical" if error_rate > 25 else "warning",
                        "message": f"High API error rate: {error_rate:.1f}%",
                        "value": error_rate,
                        "threshold": 10,
                    }
                )

            # High response time alert
            avg_response_time = statistics.mean(
                [req.response_time_ms for req in recent_requests]
            )
            if avg_response_time > 1000:  # More than 1 second
                alerts.append(
                    {
                        "type": "high_response_time",
                        "severity": (
                            "critical" if avg_response_time > 5000 else "warning"
                        ),
                        "message": f"High average response time: {avg_response_time:.0f}ms",
                        "value": avg_response_time,
                        "threshold": 1000,
                    }
                )

            # Check for endpoint-specific issues
            endpoint_groups = defaultdict(list)
            for req in recent_requests:
                endpoint_key = f"{req.method} {req.endpoint}"
                endpoint_groups[endpoint_key].append(req)

            for endpoint, requests in endpoint_groups.items():
                if len(requests) >= 5:  # Only check endpoints with sufficient traffic
                    endpoint_errors = [
                        req for req in requests if req.status_code >= 400
                    ]
                    endpoint_error_rate = len(endpoint_errors) / len(requests) * 100

                    if endpoint_error_rate > 20:
                        alerts.append(
                            {
                                "type": "endpoint_high_error_rate",
                                "severity": "warning",
                                "message": f"High error rate for {endpoint}: {endpoint_error_rate:.1f}%",
                                "endpoint": endpoint,
                                "value": endpoint_error_rate,
                                "threshold": 20,
                            }
                        )

        except Exception as e:
            logger.error(f"Failed to check performance alerts: {str(e)}")
            alerts.append(
                {
                    "type": "monitoring_error",
                    "severity": "error",
                    "message": f"Failed to check performance alerts: {str(e)}",
                }
            )

        return alerts

    def get_collector_stats(self) -> Dict[str, Any]:
        """Get collector performance statistics.

        Returns:
            Collector statistics
        """
        return {
            "total_requests_tracked": self.total_requests_tracked,
            "collection_errors": self.collection_errors,
            "active_requests": len(self.active_requests),
            "request_history_size": len(self.request_history),
            "tracked_endpoints": len(self.endpoint_metrics),
            "response_time_buffers": len(self.response_times),
        }

    def _update_endpoint_metrics(self, event: RequestEvent) -> None:
        """Update metrics for an endpoint based on a request event."""
        endpoint_key = f"{event.method} {event.endpoint}"

        if endpoint_key not in self.endpoint_metrics:
            self.endpoint_metrics[endpoint_key] = APIMetrics(
                endpoint=event.endpoint,
                method=event.method,
                first_request=event.timestamp,
            )

        metrics = self.endpoint_metrics[endpoint_key]

        # Update basic counters
        metrics.total_requests += 1
        metrics.last_request = event.timestamp
        metrics.last_updated = datetime.utcnow()

        # Update response time metrics
        if event.response_time_ms < metrics.min_response_time:
            metrics.min_response_time = event.response_time_ms
        if event.response_time_ms > metrics.max_response_time:
            metrics.max_response_time = event.response_time_ms

        # Update average (simple moving average)
        if metrics.total_requests == 1:
            metrics.avg_response_time = event.response_time_ms
        else:
            # Exponential moving average with alpha=0.1
            metrics.avg_response_time = (0.9 * metrics.avg_response_time) + (
                0.1 * event.response_time_ms
            )

        # Update status code counters
        status_family = event.status_code // 100
        if status_family == 2:
            metrics.status_2xx += 1
        elif status_family == 3:
            metrics.status_3xx += 1
        elif status_family == 4:
            metrics.status_4xx += 1
        elif status_family == 5:
            metrics.status_5xx += 1

        # Update error metrics
        if event.status_code >= 400:
            metrics.error_count += 1

        metrics.error_rate = (
            (metrics.error_count / metrics.total_requests * 100)
            if metrics.total_requests > 0
            else 0
        )

        # Calculate requests per minute
        if metrics.first_request:
            time_diff = (event.timestamp - metrics.first_request).total_seconds() / 60
            if time_diff > 0:
                metrics.requests_per_minute = metrics.total_requests / time_diff

        # Update percentiles if we have enough data
        if (
            endpoint_key in self.response_times
            and len(self.response_times[endpoint_key]) >= 10
        ):
            times = list(self.response_times[endpoint_key])
            times.sort()

            n = len(times)
            metrics.p50_response_time = times[int(n * 0.5)]
            metrics.p95_response_time = times[int(n * 0.95)]
            metrics.p99_response_time = times[int(n * 0.99)]
