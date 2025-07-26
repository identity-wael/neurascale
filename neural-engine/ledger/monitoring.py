"""Cloud Monitoring integration for Neural Ledger.

This module provides metrics collection and monitoring for the Neural Ledger system,
including performance metrics, compliance alerts, and operational dashboards.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum

from google.cloud import monitoring_v3
from google.api_core import retry
import google.api_core.exceptions

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Custom metric types for Neural Ledger monitoring."""

    # Performance metrics
    EVENT_PROCESSING_LATENCY = "neural_ledger / event_processing_latency"
    STORAGE_WRITE_LATENCY = "neural_ledger / storage_write_latency"
    SIGNATURE_VERIFICATION_TIME = "neural_ledger / signature_verification_time"

    # Throughput metrics
    EVENTS_PROCESSED = "neural_ledger / events_processed"
    EVENTS_FAILED = "neural_ledger / events_failed"
    STORAGE_WRITES = "neural_ledger / storage_writes"

    # Integrity metrics
    CHAIN_VIOLATIONS = "neural_ledger / chain_violations"
    SIGNATURE_FAILURES = "neural_ledger / signature_failures"

    # Compliance metrics
    COMPLIANCE_EVENTS = "neural_ledger / compliance_events"
    AUDIT_REQUESTS = "neural_ledger / audit_requests"
    DATA_EXPORTS = "neural_ledger / data_exports"

    # Resource metrics
    STORAGE_SIZE_BYTES = "neural_ledger / storage_size_bytes"
    ACTIVE_SESSIONS = "neural_ledger / active_sessions"


class LedgerMonitoring:
    """Monitoring service for Neural Ledger with Cloud Monitoring integration."""

    def __init__(self, project_id: str, location: str = "northamerica-northeast1"):
        """Initialize monitoring service.

        Args:
            project_id: GCP project ID
            location: GCP region
        """
        self.project_id = project_id
        self.location = location
        self.client = monitoring_v3.MetricServiceClient()
        self.project_name = f"projects/{project_id}"

        # Initialize metric descriptors
        self._ensure_metric_descriptors()

    def _ensure_metric_descriptors(self):
        """Ensure all custom metric descriptors exist."""
        for metric_type in MetricType:
            self._create_metric_descriptor(metric_type)

    def _create_metric_descriptor(self, metric_type: MetricType):
        """Create a metric descriptor if it doesn't exist.

        Args:
            metric_type: The metric type to create
        """
        descriptor = monitoring_v3.MetricDescriptor()
        descriptor.type = f"custom.googleapis.com/{metric_type.value}"
        descriptor.metric_kind = monitoring_v3.MetricDescriptor.MetricKind.GAUGE
        descriptor.value_type = monitoring_v3.MetricDescriptor.ValueType.DOUBLE

        # Set display name and description based on metric type
        if "latency" in metric_type.value or "time" in metric_type.value:
            descriptor.display_name = metric_type.value.replace("_", " ").title()
            descriptor.description = f"Latency metric for {metric_type.value}"
            descriptor.unit = "ms"
        elif "bytes" in metric_type.value:
            descriptor.display_name = metric_type.value.replace("_", " ").title()
            descriptor.description = f"Size metric for {metric_type.value}"
            descriptor.unit = "By"
        else:
            descriptor.display_name = metric_type.value.replace("_", " ").title()
            descriptor.description = f"Count metric for {metric_type.value}"
            descriptor.unit = "1"

        # Add labels
        descriptor.labels.append(
            monitoring_v3.LabelDescriptor(
                key="event_type",
                value_type=monitoring_v3.LabelDescriptor.ValueType.STRING,
                description="Type of event being processed",
            )
        )
        descriptor.labels.append(
            monitoring_v3.LabelDescriptor(
                key="storage_tier",
                value_type=monitoring_v3.LabelDescriptor.ValueType.STRING,
                description="Storage tier (bigtable, firestore, bigquery)",
            )
        )

        try:
            self.client.create_metric_descriptor(
                name=self.project_name,
                metric_descriptor=descriptor,
                retry=retry.Retry(deadline=30.0),
            )
            logger.info(f"Created metric descriptor: {descriptor.type}")
        except google.api_core.exceptions.AlreadyExists:
            logger.debug(f"Metric descriptor already exists: {descriptor.type}")
        except Exception as e:
            logger.error(f"Failed to create metric descriptor {descriptor.type}: {e}")

    def record_metric(
        self,
        metric_type: MetricType,
        value: float,
        labels: Optional[Dict[str, str]] = None,
        resource_type: str = "cloud_function",
        resource_labels: Optional[Dict[str, str]] = None,
    ):
        """Record a custom metric value.

        Args:
            metric_type: Type of metric to record
            value: Metric value
            labels: Metric labels
            resource_type: Resource type (default: cloud_function)
            resource_labels: Resource labels
        """
        try:
            series = monitoring_v3.TimeSeries()
            series.metric.type = f"custom.googleapis.com/{metric_type.value}"

            # Add metric labels
            if labels:
                for key, val in labels.items():
                    series.metric.labels[key] = val

            # Set resource
            series.resource.type = resource_type
            if resource_labels:
                for key, val in resource_labels.items():
                    series.resource.labels[key] = val
            else:
                # Default resource labels for cloud function
                series.resource.labels["function_name"] = "ledger-event-processor"
                series.resource.labels["project_id"] = self.project_id
                series.resource.labels["region"] = self.location

            # Create data point
            now = monitoring_v3.TimeInterval()
            now.end_time.GetCurrentTime()

            point = monitoring_v3.Point()
            point.interval = now
            point.value.double_value = value

            series.points = [point]

            # Write time series
            self.client.create_time_series(
                name=self.project_name,
                time_series=[series],
                retry=retry.Retry(deadline=30.0),
            )

            logger.debug(f"Recorded metric {metric_type.value}: {value}")

        except Exception as e:
            logger.error(f"Failed to record metric {metric_type.value}: {e}")

    def record_event_processing(
        self, event_type: str, latency_ms: float, success: bool = True
    ):
        """Record event processing metrics.

        Args:
            event_type: Type of event processed
            latency_ms: Processing latency in milliseconds
            success: Whether processing succeeded
        """
        # Record latency
        self.record_metric(
            MetricType.EVENT_PROCESSING_LATENCY,
            latency_ms,
            labels={"event_type": event_type, "storage_tier": "all"},
        )

        # Record count
        metric_type = (
            MetricType.EVENTS_PROCESSED if success else MetricType.EVENTS_FAILED
        )
        self.record_metric(
            metric_type, 1, labels={"event_type": event_type, "storage_tier": "all"}
        )

    def record_storage_write(
        self, storage_tier: str, latency_ms: float, event_type: str
    ):
        """Record storage write metrics.

        Args:
            storage_tier: Storage tier (bigtable, firestore, bigquery)
            latency_ms: Write latency in milliseconds
            event_type: Type of event written
        """
        self.record_metric(
            MetricType.STORAGE_WRITE_LATENCY,
            latency_ms,
            labels={"event_type": event_type, "storage_tier": storage_tier},
        )

        self.record_metric(
            MetricType.STORAGE_WRITES,
            1,
            labels={"event_type": event_type, "storage_tier": storage_tier},
        )

    def record_chain_violation(self, event_type: str):
        """Record a hash chain violation.

        Args:
            event_type: Type of event that violated the chain
        """
        self.record_metric(
            MetricType.CHAIN_VIOLATIONS,
            1,
            labels={"event_type": event_type, "storage_tier": "all"},
        )

        # This is critical - also log it
        logger.critical(f"Hash chain violation detected for event type: {event_type}")

    def record_signature_verification(
        self, event_type: str, verification_time_ms: float, success: bool
    ):
        """Record signature verification metrics.

        Args:
            event_type: Type of event verified
            verification_time_ms: Verification time in milliseconds
            success: Whether verification succeeded
        """
        self.record_metric(
            MetricType.SIGNATURE_VERIFICATION_TIME,
            verification_time_ms,
            labels={"event_type": event_type, "storage_tier": "all"},
        )

        if not success:
            self.record_metric(
                MetricType.SIGNATURE_FAILURES,
                1,
                labels={"event_type": event_type, "storage_tier": "all"},
            )

    def record_compliance_event(self, event_type: str, action: str):
        """Record a compliance-related event.

        Args:
            event_type: Type of compliance event
            action: Action taken (e.g., 'audit_request', 'data_export')
        """
        self.record_metric(
            MetricType.COMPLIANCE_EVENTS,
            1,
            labels={"event_type": event_type, "storage_tier": action},
        )

        if action == "audit_request":
            self.record_metric(
                MetricType.AUDIT_REQUESTS,
                1,
                labels={"event_type": event_type, "storage_tier": "all"},
            )
        elif action == "data_export":
            self.record_metric(
                MetricType.DATA_EXPORTS,
                1,
                labels={"event_type": event_type, "storage_tier": "all"},
            )

    def get_metrics_summary(
        self, metric_type: MetricType, hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get summary of metrics for the specified time period.

        Args:
            metric_type: Type of metric to query
            hours: Number of hours to look back

        Returns:
            List of metric data points
        """
        try:
            # Build the filter
            interval = monitoring_v3.TimeInterval()
            now = datetime.now(timezone.utc)
            interval.end_time.seconds = int(now.timestamp())
            interval.start_time.seconds = int(
                (now - timedelta(hours=hours)).timestamp()
            )

            # Create the request
            request = monitoring_v3.ListTimeSeriesRequest(
                name=self.project_name,
                filter=f'metric.type="custom.googleapis.com/{metric_type.value}"',
                interval=interval,
                view=monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
            )

            # Execute the request
            results = self.client.list_time_series(request=request)

            # Process results
            summary = []
            for result in results:
                for point in result.points:
                    summary.append(
                        {
                            "timestamp": datetime.fromtimestamp(
                                point.interval.end_time.seconds, tz=timezone.utc
                            ),
                            "value": point.value.double_value,
                            "labels": dict(result.metric.labels),
                        }
                    )

            return summary

        except Exception as e:
            logger.error(f"Failed to get metrics summary for {metric_type.value}: {e}")
            return []


def create_monitoring_dashboard(project_id: str, dashboard_name: str = "neural-ledger"):
    """Create a Cloud Monitoring dashboard for Neural Ledger.

    Args:
        project_id: GCP project ID
        dashboard_name: Name of the dashboard
    """
    client = monitoring_v3.DashboardsServiceClient()
    project_name = f"projects/{project_id}"

    # Define dashboard configuration
    dashboard = monitoring_v3.Dashboard()
    dashboard.display_name = "Neural Ledger Monitoring"
    dashboard.mql_dashboard = monitoring_v3.Dashboard.MqlDashboard()

    # Add dashboard panels
    dashboard.mql_dashboard.tiles.extend(
        [
            # Event Processing Latency
            monitoring_v3.Dashboard.MqlDashboard.Tile(
                width=6,
                height=4,
                widget=monitoring_v3.Dashboard.MqlDashboard.Tile.Widget(
                    title="Event Processing Latency (p99)",
                    scorecard=monitoring_v3.Dashboard.MqlDashboard.Tile.Widget.Scorecard(
                        time_series_query=monitoring_v3.Dashboard.MqlDashboard.Tile.Widget.TimeSeriesQuery(
                            query="""
                        fetch cloud_function
                        | metric 'custom.googleapis.com / neural_ledger / event_processing_latency'
                        | group_by 1m, [value_percentile99: percentile(value.event_processing_latency, 99)]
                        | every 1m
                        """
                        ),
                        spark_chart_view=monitoring_v3.Dashboard.MqlDashboard.Tile.Widget.SparkChartView(
                            spark_chart_type=monitoring_v3.Dashboard.MqlDashboard.Tile.Widget.SparkChartView.SparkChartType.SPARK_LINE
                        ),
                    ),
                ),
            ),
            # Events Processed Rate
            monitoring_v3.Dashboard.MqlDashboard.Tile(
                width=6,
                height=4,
                widget=monitoring_v3.Dashboard.MqlDashboard.Tile.Widget(
                    title="Events Processed per Minute",
                    xy_chart=monitoring_v3.Dashboard.MqlDashboard.Tile.Widget.XyChart(
                        time_series_query=monitoring_v3.Dashboard.MqlDashboard.Tile.Widget.TimeSeriesQuery(
                            query="""
                        fetch cloud_function
                        | metric 'custom.googleapis.com / neural_ledger / events_processed'
                        | group_by 1m, [value_sum: sum(value.events_processed)]
                        | every 1m
                        """
                        )
                    ),
                ),
            ),
            # Chain Violations Alert
            monitoring_v3.Dashboard.MqlDashboard.Tile(
                width=12,
                height=2,
                widget=monitoring_v3.Dashboard.MqlDashboard.Tile.Widget(
                    title="Hash Chain Violations",
                    scorecard=monitoring_v3.Dashboard.MqlDashboard.Tile.Widget.Scorecard(
                        time_series_query=monitoring_v3.Dashboard.MqlDashboard.Tile.Widget.TimeSeriesQuery(
                            query="""
                        fetch cloud_function
                        | metric 'custom.googleapis.com / neural_ledger / chain_violations'
                        | group_by 1h, [value_sum: sum(value.chain_violations)]
                        | every 1h
                        """
                        ),
                        thresholds=[
                            monitoring_v3.Dashboard.MqlDashboard.Tile.Widget.Scorecard.Threshold(
                                value=0,
                                color=monitoring_v3.Dashboard.MqlDashboard.Tile.Widget.Scorecard.Threshold.Color.RED,
                            )
                        ],
                    ),
                ),
            ),
            # Storage Write Latency by Tier
            monitoring_v3.Dashboard.MqlDashboard.Tile(
                width=12,
                height=4,
                widget=monitoring_v3.Dashboard.MqlDashboard.Tile.Widget(
                    title="Storage Write Latency by Tier",
                    xy_chart=monitoring_v3.Dashboard.MqlDashboard.Tile.Widget.XyChart(
                        time_series_query=monitoring_v3.Dashboard.MqlDashboard.Tile.Widget.TimeSeriesQuery(
                            query="""
                        fetch cloud_function
                        | metric 'custom.googleapis.com / neural_ledger / storage_write_latency'
                        | group_by 1m, [storage_tier], [value_mean: mean(value.storage_write_latency)]
                        | every 1m
                        """
                        )
                    ),
                ),
            ),
        ]
    )

    try:
        # Create the dashboard
        created_dashboard = client.create_dashboard(
            parent=project_name, dashboard=dashboard
        )
        logger.info(f"Created dashboard: {created_dashboard.name}")
        return created_dashboard.name
    except Exception as e:
        logger.error(f"Failed to create dashboard: {e}")
        return None
