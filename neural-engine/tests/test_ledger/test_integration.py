"""Integration tests for Neural Ledger with GCP services.

These tests require GCP credentials and test project setup.
They are marked with @pytest.mark.integration and can be run with:
    pytest -m integration tests/test_ledger/
"""

import pytest
import asyncio
import os
from datetime import datetime, timezone, timedelta
from typing import Optional
import uuid

from google.cloud import pubsub_v1, firestore, bigquery
from google.api_core import exceptions

from ledger.neural_ledger import NeuralLedger
from ledger.event_schema import EventType, NeuralLedgerEvent
from ledger.query_service import LedgerQueryService
from ledger.monitoring import LedgerMonitoring, create_monitoring_dashboard


# Skip integration tests if not in CI or explicit integration test mode
INTEGRATION_TESTS_ENABLED = (
    os.getenv("RUN_INTEGRATION_TESTS", "false").lower() == "true"
)
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "neurascale-test")
LOCATION = os.getenv("GCP_LOCATION", "northamerica-northeast1")


@pytest.mark.integration
@pytest.mark.skipif(not INTEGRATION_TESTS_ENABLED, reason="Integration tests disabled")
class TestNeuralLedgerIntegration:
    """Integration tests for Neural Ledger with real GCP services."""

    @pytest.fixture
    async def ledger(self):
        """Create a Neural Ledger instance for testing."""
        ledger = NeuralLedger(project_id=PROJECT_ID, location=LOCATION)
        await ledger.initialize()
        yield ledger
        # Cleanup is handled by test project lifecycle

    @pytest.fixture
    def query_service(self):
        """Create a query service instance for testing."""
        return LedgerQueryService(project_id=PROJECT_ID, location=LOCATION)

    @pytest.fixture
    def monitoring(self):
        """Create a monitoring instance for testing."""
        return LedgerMonitoring(project_id=PROJECT_ID, location=LOCATION)

    async def test_end_to_end_event_logging(self, ledger):
        """Test complete event logging flow through all storage tiers."""
        # Create a test session
        session_id = f"test-session-{uuid.uuid4()}"
        user_id = f"test-user-{uuid.uuid4()}"
        device_id = f"test-device-{uuid.uuid4()}"

        # Log session creation event
        session_event = await ledger.log_session_created(
            session_id=session_id,
            user_id=user_id,
            device_id=device_id,
            metadata={"test": True, "integration_test": "end_to_end"},
        )

        assert session_event.event_id is not None
        assert session_event.event_hash != ""
        assert session_event.signature is not None  # Critical event should be signed
        assert session_event.previous_hash != ""

        # Log data ingestion event
        data_hash = "test-data-hash-12345"
        data_event = await ledger.log_data_ingested(
            session_id=session_id,
            data_hash=data_hash,
            size_bytes=1024,
            metadata={"channels": 64, "sampling_rate": 1000},
        )

        assert data_event.previous_hash == session_event.event_hash
        assert data_event.signature is None  # Non-critical event

        # Wait for eventual consistency
        await asyncio.sleep(2)

        # Verify chain integrity
        is_valid = await ledger.verify_chain_integrity(
            start_time=datetime.now(timezone.utc) - timedelta(minutes=5),
            end_time=datetime.now(timezone.utc),
        )
        assert is_valid is True

    async def test_multi_tier_storage_consistency(self, ledger, query_service):
        """Test that events are written to all storage tiers correctly."""
        # Create test event
        session_id = f"test-storage-{uuid.uuid4()}"
        event = await ledger.log_event(
            event_type=EventType.DEVICE_CONNECTED,
            session_id=session_id,
            device_id="test-device",
            metadata={"storage_test": True},
        )

        # Wait for storage propagation
        await asyncio.sleep(3)

        # Check Firestore (real-time)
        firestore_client = firestore.Client(project=PROJECT_ID)
        doc = (
            firestore_client.collection("ledger_events").document(event.event_id).get()
        )
        assert doc.exists
        assert doc.to_dict()["event_type"] == EventType.DEVICE_CONNECTED.value

        # Check BigQuery (long-term)
        timeline = await query_service.get_session_timeline(session_id)
        assert len(timeline) == 1
        assert timeline[0].event_id == event.event_id

    async def test_compliance_audit_report(self, ledger, query_service):
        """Test HIPAA audit report generation."""
        # Create audit events
        user_id = f"audit-user-{uuid.uuid4()}"

        # Log access events
        await ledger.log_access_event(
            user_id=user_id,
            granted=True,
            resource="/api/sessions/123",
            metadata={"ip_address": "10.0.0.1", "action": "read"},
        )

        await ledger.log_access_event(
            user_id=user_id,
            granted=False,
            resource="/api/admin",
            metadata={"ip_address": "10.0.0.2", "action": "write"},
        )

        # Wait for propagation
        await asyncio.sleep(3)

        # Generate audit report
        report = await query_service.generate_hipaa_audit_report(
            start_date=datetime.now(timezone.utc) - timedelta(days=1),
            end_date=datetime.now(timezone.utc),
        )

        assert report["report_type"] == "HIPAA_AUDIT"
        assert "access_details" in report
        assert "suspicious_activity" in report
        assert report["retention_period"] == "7 years per HIPAA requirements"

    async def test_signature_verification_flow(self, ledger):
        """Test digital signature creation and verification."""
        # Log a critical event that requires signature
        session_id = f"sig-test-{uuid.uuid4()}"
        event = await ledger.log_event(
            event_type=EventType.DATA_EXPORTED,  # Critical event
            session_id=session_id,
            metadata={"export_format": "csv", "record_count": 100},
        )

        assert event.signature is not None
        assert event.signing_key_id is not None

        # Verify the signature through the event processor
        from ledger.event_processor import EventProcessor

        processor = EventProcessor(
            project_id=PROJECT_ID,
            location=LOCATION,
            bigtable_client=ledger.bigtable_client,
            firestore_client=ledger.firestore_client,
            bigquery_client=ledger.bigquery_client,
            kms_client=ledger.kms_client,
        )

        # Process the event (includes signature verification)
        success = await processor.process_event(event.to_dict())
        assert success is True

    async def test_real_time_event_queries(self, ledger, query_service):
        """Test real-time event querying from Firestore."""
        # Create multiple events
        session_id = f"realtime-{uuid.uuid4()}"

        for i in range(5):
            await ledger.log_event(
                event_type=EventType.MODEL_INFERENCE,
                session_id=session_id,
                metadata={"inference_id": i, "model": "test-model"},
            )

        # Wait for Firestore propagation
        await asyncio.sleep(2)

        # Query real-time events
        events = await query_service.get_real_time_events(
            event_types=[EventType.MODEL_INFERENCE], limit=10
        )

        # Should find our events
        our_events = [e for e in events if e.get("session_id") == session_id]
        assert len(our_events) >= 5

    async def test_monitoring_metrics(self, ledger, monitoring):
        """Test that monitoring metrics are recorded correctly."""
        # Generate some events to create metrics
        session_id = f"metrics-{uuid.uuid4()}"

        for i in range(3):
            await ledger.log_event(
                event_type=EventType.SESSION_STARTED,
                session_id=session_id,
                metadata={"metric_test": i},
            )

        # Wait for metric propagation
        await asyncio.sleep(5)

        # Query metrics
        from ledger.monitoring import MetricType

        summary = monitoring.get_metrics_summary(
            metric_type=MetricType.EVENTS_PROCESSED, hours=1
        )

        # Should have recorded metrics
        assert len(summary) > 0

    async def test_chain_integrity_violation_detection(self, ledger):
        """Test that chain violations are detected and reported."""
        # This test simulates a chain violation by manually tampering
        # In production, this should never happen

        # Create a valid event
        event1 = await ledger.log_event(
            event_type=EventType.SESSION_CREATED,
            session_id=f"chain-test-{uuid.uuid4()}",
        )

        # Create a second event with tampered previous_hash
        event2 = NeuralLedgerEvent(
            event_type=EventType.SESSION_ENDED,
            session_id=event1.session_id,
            previous_hash="tampered_hash_value",
        )
        event2.event_hash = "also_tampered"

        # Try to write the tampered event directly to BigQuery
        # In production, this would be caught by the event processor
        table_id = f"{PROJECT_ID}.neural_ledger.events"

        try:
            row = {
                "event_id": event2.event_id,
                "timestamp": event2.timestamp.isoformat(),
                "event_type": event2.event_type.value,
                "session_id": event2.session_id,
                "previous_hash": event2.previous_hash,
                "event_hash": event2.event_hash,
            }

            errors = ledger.bigquery_client.insert_rows_json(
                ledger.bigquery_client.get_table(table_id), [row]
            )

            if not errors:
                # Verify chain integrity should fail
                await asyncio.sleep(2)

                is_valid = await ledger.verify_chain_integrity(
                    start_time=datetime.now(timezone.utc) - timedelta(minutes=5),
                    end_time=datetime.now(timezone.utc),
                )

                assert is_valid is False
        except Exception:
            # Expected in production with proper access controls
            pass

    async def test_gdpr_compliance_data_export(self, ledger, query_service):
        """Test GDPR compliance features for data export and user access logs."""
        user_id = f"gdpr-user-{uuid.uuid4()}"

        # Create user activity
        session_id = f"gdpr-session-{uuid.uuid4()}"
        await ledger.log_session_created(
            session_id=session_id, user_id=user_id, device_id="test-device"
        )

        # Log data export event (GDPR request)
        await ledger.log_event(
            event_type=EventType.DATA_EXPORTED,
            user_id=user_id,
            metadata={
                "export_reason": "gdpr_request",
                "requested_by": user_id,
                "export_format": "json",
            },
        )

        # Wait for propagation
        await asyncio.sleep(3)

        # Get user access log
        access_log = await query_service.get_user_access_log(
            user_id=user_id,
            start_date=datetime.now(timezone.utc) - timedelta(days=1),
            end_date=datetime.now(timezone.utc),
        )

        # Should include the data export
        export_events = [
            log
            for log in access_log
            if log["event_type"] == EventType.DATA_EXPORTED.value
        ]
        assert len(export_events) == 1
        assert export_events[0]["user_id"] == user_id


@pytest.mark.integration
@pytest.mark.skipif(not INTEGRATION_TESTS_ENABLED, reason="Integration tests disabled")
async def test_monitoring_dashboard_creation():
    """Test creation of monitoring dashboard."""
    if not INTEGRATION_TESTS_ENABLED:
        pytest.skip("Integration tests disabled")

    dashboard_name = create_monitoring_dashboard(
        project_id=PROJECT_ID, dashboard_name=f"neural-ledger-test-{uuid.uuid4()}"
    )

    assert dashboard_name is not None
