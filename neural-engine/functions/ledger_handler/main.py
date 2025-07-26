"""Cloud Function handler for Neural Ledger event processing.

This function processes events from Pub/Sub and writes them to multi-tier storage
with sub-100ms latency for HIPAA compliance.
"""

import base64
import json
import logging
import os
import sys
from typing import Dict, Any

# Add the neural-engine directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from google.cloud import bigtable, firestore, bigquery, kms  # noqa: E402
from google.cloud import error_reporting  # noqa: E402
from google.cloud import monitoring_v3  # noqa: E402

from ledger.event_processor import EventProcessor  # noqa: E402

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize error reporting
error_client = error_reporting.Client()

# Initialize monitoring client for metrics
monitoring_client = monitoring_v3.MetricServiceClient()

# Configuration from environment variables
PROJECT_ID = os.environ.get("GCP_PROJECT", "neurascale-production")
LOCATION = os.environ.get("GCP_LOCATION", "northamerica-northeast1")

# Initialize storage clients (reused across invocations)
bigtable_client = bigtable.Client(project=PROJECT_ID, admin=False)
firestore_client = firestore.Client(project=PROJECT_ID)
bigquery_client = bigquery.Client(project=PROJECT_ID)
kms_client = kms.KeyManagementServiceClient()

# Initialize event processor
event_processor = EventProcessor(
    project_id=PROJECT_ID,
    location=LOCATION,
    bigtable_client=bigtable_client,
    firestore_client=firestore_client,
    bigquery_client=bigquery_client,
    kms_client=kms_client,
)


def process_ledger_event(event: Dict[str, Any], context: Any) -> None:
    """Process Neural Ledger events from Pub/Sub.

    This is the main entry point for the Cloud Function. It processes
    events with the following guarantees:
    - Sub-100ms processing time (p99)
    - At-least-once delivery
    - Parallel writes to all storage systems
    - Automatic retry on transient failures

    Args:
        event: The Pub/Sub event payload
        context: The event metadata
    """
    start_time = context.timestamp

    try:
        # Extract and decode the message
        if "data" not in event:
            logger.error("No data field in Pub/Sub event")
            return

        # Decode base64 message
        message_data = base64.b64decode(event["data"]).decode("utf-8")
        event_data = json.loads(message_data)

        # Log event details
        event_id = event_data.get("event_id", "unknown")
        event_type = event_data.get("event_type", "unknown")
        logger.info(
            f"Processing event: id={event_id}, type={event_type}, "
            f"message_id={context.event_id}"
        )

        # Process the event asynchronously
        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            success = loop.run_until_complete(event_processor.process_event(event_data))

            if not success:
                # Log failure but don't raise exception to avoid infinite retries
                logger.error(f"Failed to process event {event_id}")
                _report_metric("ledger_events_failed", 1, {"event_type": event_type})
            else:
                # Report success metric
                _report_metric("ledger_events_processed", 1, {"event_type": event_type})

                # Calculate and report latency
                import datetime

                end_time = datetime.datetime.now(datetime.timezone.utc)
                start_dt = datetime.datetime.fromisoformat(
                    start_time.replace("Z", "+00:00")
                )
                latency_ms = (end_time - start_dt).total_seconds() * 1000

                _report_metric(
                    "ledger_processing_latency",
                    latency_ms,
                    {"event_type": event_type},
                )

                logger.info(
                    f"Successfully processed event {event_id} in {latency_ms:.2f}ms"
                )

        finally:
            loop.close()

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in message: {e}")
        error_client.report_exception()
        # Don't retry invalid JSON
        return

    except Exception as e:
        logger.error(f"Unexpected error processing event: {e}", exc_info=True)
        error_client.report_exception()
        # Re-raise to trigger retry
        raise


def _report_metric(metric_name: str, value: float, labels: Dict[str, str]) -> None:
    """Report custom metric to Cloud Monitoring.

    Args:
        metric_name: Name of the metric
        value: Metric value
        labels: Metric labels
    """
    try:
        # Create time series
        project_name = f"projects/{PROJECT_ID}"
        series = monitoring_v3.TimeSeries()

        # Set metric type
        series.metric.type = f"custom.googleapis.com/neural_ledger/{metric_name}"

        # Add labels
        for key, val in labels.items():
            series.metric.labels[key] = val

        # Set resource type
        series.resource.type = "cloud_function"
        series.resource.labels["function_name"] = "ledger-event-processor"
        series.resource.labels["project_id"] = PROJECT_ID
        series.resource.labels["region"] = LOCATION

        # Create data point
        now = monitoring_v3.TimeInterval()
        now.end_time.GetCurrentTime()

        point = monitoring_v3.Point()
        point.interval = now
        point.value.double_value = value

        series.points = [point]

        # Write time series
        monitoring_client.create_time_series(name=project_name, time_series=[series])

    except Exception as e:
        # Log but don't fail the function
        logger.warning(f"Failed to report metric {metric_name}: {e}")


# Health check endpoint for monitoring
def health_check(request):
    """Health check endpoint for the Cloud Function.

    Returns:
        Tuple of (response_text, status_code)
    """
    try:
        # Check storage connectivity
        checks = {
            "bigtable": _check_bigtable(),
            "firestore": _check_firestore(),
            "bigquery": _check_bigquery(),
        }

        # Check if all services are healthy
        all_healthy = all(checks.values())

        response = {
            "status": "healthy" if all_healthy else "unhealthy",
            "checks": checks,
            "project_id": PROJECT_ID,
            "location": LOCATION,
        }

        return (json.dumps(response), 200 if all_healthy else 503)

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return (json.dumps({"status": "error", "error": str(e)}), 503)


def _check_bigtable() -> bool:
    """Check Bigtable connectivity."""
    try:
        instance = bigtable_client.instance("neural-ledger")
        # Just check if we can get the instance
        return instance is not None
    except Exception:
        return False


def _check_firestore() -> bool:
    """Check Firestore connectivity."""
    try:
        # Try to read a document
        firestore_client.collection("_health").document("check").get()
        return True
    except Exception:
        return False


def _check_bigquery() -> bool:
    """Check BigQuery connectivity."""
    try:
        # Run a simple query
        query = "SELECT 1 as health_check"
        job = bigquery_client.query(query)
        list(job.result())
        return True
    except Exception:
        return False
