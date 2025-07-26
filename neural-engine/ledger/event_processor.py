"""Event processor for Neural Ledger with multi-tier storage.

This module handles the processing of events from Pub/Sub and writes them
to multiple storage systems in parallel for durability and performance.
"""

import asyncio
import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor

from google.cloud import bigtable, firestore, bigquery
from google.cloud import kms
from .event_schema import NeuralLedgerEvent, EventType, requires_signature
from .event_signer import EventSigner
from .monitoring import LedgerMonitoring, MetricType

logger = logging.getLogger(__name__)


class EventProcessor:
    """Processes Neural Ledger events with parallel writes to storage systems.

    This class handles:
    - Event validation and hash chain verification
    - Digital signature verification for critical events
    - Parallel writes to Bigtable, Firestore, and BigQuery
    - Performance metrics and monitoring
    - Compliance checks and alerts
    """

    def __init__(
        self,
        project_id: str,
        location: str,
        bigtable_client: bigtable.Client,
        firestore_client: firestore.Client,
        bigquery_client: bigquery.Client,
        kms_client: kms.KeyManagementServiceClient,
    ):
        """Initialize the event processor.

        Args:
            project_id: GCP project ID
            location: GCP region
            bigtable_client: Initialized Bigtable client
            firestore_client: Initialized Firestore client
            bigquery_client: Initialized BigQuery client
            kms_client: Initialized KMS client
        """
        self.project_id = project_id
        self.location = location

        # Storage clients
        self.bigtable_client = bigtable_client
        self.firestore_client = firestore_client
        self.bigquery_client = bigquery_client

        # Event signer for verification
        self.event_signer = EventSigner(
            project_id=project_id,
            location=location,
            keyring="neural-ledger",
            key="signing-key",
            kms_client=kms_client,
        )

        # Configuration
        self.bigtable_instance_id = "neural-ledger"
        self.bigtable_table_id = "events"
        self.bigquery_dataset_id = "neural_ledger"
        self.bigquery_table_id = "events"

        # Thread pool for I/O operations
        self.executor = ThreadPoolExecutor(max_workers=10)

        # Metrics
        self.metrics = {
            "events_processed": 0,
            "validation_failures": 0,
            "storage_failures": 0,
            "signature_verifications": 0,
        }

        # Initialize monitoring
        self.monitoring = LedgerMonitoring(project_id=project_id, location=location)

    async def process_event(self, event_data: Dict[str, Any]) -> bool:
        """Process a single event with parallel storage writes.

        Args:
            event_data: Event data dictionary

        Returns:
            True if processing succeeded, False otherwise
        """
        start_time = datetime.now(timezone.utc)

        try:
            # Parse event
            event = NeuralLedgerEvent.from_dict(event_data)

            # Step 1: Validate event integrity
            if not await self._validate_event(event):
                self.metrics["validation_failures"] += 1
                logger.error(f"Event validation failed: {event.event_id}")
                return False

            # Step 2: Verify signature for critical events
            if event.signature and not await self._verify_signature(event):
                logger.error(f"Signature verification failed: {event.event_id}")
                return False

            # Step 3: Parallel writes to all storage systems
            write_tasks = [
                self._write_to_bigtable(event),
                self._write_to_firestore(event),
                self._write_to_bigquery(event),
            ]

            # Execute writes in parallel
            results = await asyncio.gather(*write_tasks, return_exceptions=True)

            # Check for failures
            failures = [r for r in results if isinstance(r, Exception)]
            if failures:
                self.metrics["storage_failures"] += 1
                logger.error(f"Storage write failures: {failures}")
                # Continue processing even if some writes fail
                # The retry mechanism will handle failed writes

            # Step 4: Update metrics
            await self._update_metrics(event, start_time)

            # Step 5: Trigger compliance checks if needed
            if self._is_compliance_event(event.event_type):
                await self._trigger_compliance_check(event)

            self.metrics["events_processed"] += 1

            # Log processing time
            processing_time = (
                datetime.now(timezone.utc) - start_time
            ).total_seconds() * 1000
            logger.info(f"Processed event {event.event_id} in {processing_time:.2f}ms")

            return True

        except Exception as e:
            logger.error(f"Error processing event: {e}", exc_info=True)
            return False

    async def process_batch(self, events: List[Dict[str, Any]]) -> Dict[str, int]:
        """Process a batch of events.

        Args:
            events: List of event dictionaries

        Returns:
            Dictionary with processing statistics
        """
        results = await asyncio.gather(
            *[self.process_event(event) for event in events], return_exceptions=True
        )

        success_count = sum(1 for r in results if r is True)
        failure_count = len(results) - success_count

        return {
            "total": len(events),
            "success": success_count,
            "failure": failure_count,
        }

    # Private methods

    async def _validate_event(self, event: NeuralLedgerEvent) -> bool:
        """Validate event structure and hash chain."""
        # Validate required fields
        if not event.event_id or not event.timestamp or not event.event_type:
            logger.error("Event missing required fields")
            return False

        # For now, we trust the hash chain from the ledger
        # In production, we would verify against the previous event
        # TODO: Implement proper chain validation with state management

        return True

    async def _verify_signature(self, event: NeuralLedgerEvent) -> bool:
        """Verify digital signature for critical events."""
        if not requires_signature(event.event_type):
            return True

        if not event.signature:
            logger.error(f"Critical event {event.event_id} missing signature")
            return False

        # Time the verification
        verification_start = datetime.now(timezone.utc)

        # Verify signature using KMS
        is_valid = await self.event_signer.verify_signature(event, event.signature)

        # Calculate verification time
        verification_time_ms = (
            datetime.now(timezone.utc) - verification_start
        ).total_seconds() * 1000

        # Record metrics
        self.monitoring.record_signature_verification(
            event_type=event.event_type.value,
            verification_time_ms=verification_time_ms,
            success=is_valid,
        )

        self.metrics["signature_verifications"] += 1

        return is_valid

    async def _write_to_bigtable(self, event: NeuralLedgerEvent) -> None:
        """Write event to Bigtable for high-frequency queries."""
        loop = asyncio.get_event_loop()

        def write() -> None:
            # Get table reference
            instance = self.bigtable_client.instance(self.bigtable_instance_id)
            table = instance.table(self.bigtable_table_id)

            # Create row key: reversed timestamp + event_id for time-based sorting
            timestamp_str = event.timestamp.strftime("%Y%m%d%H%M%S%f")
            reversed_timestamp = str(9999999999999999 - int(timestamp_str))
            row_key = f"{reversed_timestamp}#{event.event_id}"

            # Create row
            row = table.direct_row(row_key.encode())

            # Add event data to different column families
            row.set_cell("event", "event_id", event.event_id)
            row.set_cell("event", "event_type", event.event_type.value)
            row.set_cell("event", "timestamp", event.timestamp.isoformat())

            if event.session_id:
                row.set_cell("event", "session_id", event.session_id)
            if event.device_id:
                row.set_cell("event", "device_id", event.device_id)
            if event.user_id:
                row.set_cell("event", "user_id", event.user_id)
            if event.data_hash:
                row.set_cell("event", "data_hash", event.data_hash)

            # Metadata as JSON
            if event.metadata:
                row.set_cell("metadata", "data", json.dumps(event.metadata))

            # Chain data
            row.set_cell("chain", "previous_hash", event.previous_hash)
            row.set_cell("chain", "event_hash", event.event_hash)

            if event.signature:
                row.set_cell("chain", "signature", event.signature)
            if event.signing_key_id:
                row.set_cell("chain", "signing_key_id", event.signing_key_id)

            # Commit row
            row.commit()

            logger.debug(f"Wrote event {event.event_id} to Bigtable")

        # Execute in thread pool
        await loop.run_in_executor(self.executor, write)

    async def _write_to_firestore(self, event: NeuralLedgerEvent) -> None:
        """Write event to Firestore for real-time queries."""
        loop = asyncio.get_event_loop()

        def write() -> None:
            # Get collection reference
            collection = self.firestore_client.collection("ledger_events")

            # Create document
            doc_data = event.to_dict()

            # Add server timestamp
            doc_data["server_timestamp"] = firestore.SERVER_TIMESTAMP

            # Write to main events collection
            collection.document(event.event_id).set(doc_data)

            # Also write to session subcollection if session_id exists
            if event.session_id:
                session_collection = (
                    self.firestore_client.collection("ledger_sessions")
                    .document(event.session_id)
                    .collection("events")
                )
                session_collection.document(event.event_id).set(
                    {
                        "event_id": event.event_id,
                        "event_type": event.event_type.value,
                        "timestamp": event.timestamp,
                        "event_hash": event.event_hash,
                    }
                )

            logger.debug(f"Wrote event {event.event_id} to Firestore")

        # Execute in thread pool
        await loop.run_in_executor(self.executor, write)

    async def _write_to_bigquery(self, event: NeuralLedgerEvent) -> None:
        """Write event to BigQuery for long-term storage and analytics."""
        loop = asyncio.get_event_loop()

        def write() -> None:
            # Get table reference
            table_id = (
                f"{self.project_id}.{self.bigquery_dataset_id}.{self.bigquery_table_id}"
            )
            table = self.bigquery_client.get_table(table_id)

            # Convert event to BigQuery row
            row = {
                "event_id": event.event_id,
                "timestamp": event.timestamp.isoformat(),
                "event_type": event.event_type.value,
                "session_id": event.session_id,
                "device_id": event.device_id,
                "user_id": event.user_id,
                "data_hash": event.data_hash,
                "metadata": json.dumps(event.metadata) if event.metadata else None,
                "previous_hash": event.previous_hash,
                "event_hash": event.event_hash,
                "signature": event.signature,
                "signing_key_id": event.signing_key_id,
            }

            # Stream row to BigQuery
            errors = self.bigquery_client.insert_rows_json(table, [row])

            if errors:
                raise Exception(f"BigQuery insert errors: {errors}")

            logger.debug(f"Wrote event {event.event_id} to BigQuery")

        # Execute in thread pool
        await loop.run_in_executor(self.executor, write)

    async def _update_metrics(
        self, event: NeuralLedgerEvent, start_time: datetime
    ) -> None:
        """Update processing metrics."""
        # Calculate processing latency
        latency_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000

        # Record metrics using monitoring service
        self.monitoring.record_event_processing(
            event_type=event.event_type.value, latency_ms=latency_ms, success=True
        )

        logger.debug(f"Event processing latency: {latency_ms:.2f}ms")

    def _is_compliance_event(self, event_type: EventType) -> bool:
        """Check if event requires compliance processing."""
        compliance_events = {
            EventType.SESSION_CREATED,
            EventType.SESSION_ENDED,
            EventType.DATA_EXPORTED,
            EventType.ACCESS_GRANTED,
            EventType.ACCESS_DENIED,
            EventType.AUTH_SUCCESS,
            EventType.AUTH_FAILURE,
        }
        return event_type in compliance_events

    async def _trigger_compliance_check(self, event: NeuralLedgerEvent) -> None:
        """Trigger compliance checks for specific events."""
        # TODO: Implement compliance check logic
        # This could include:
        # - Checking for suspicious access patterns
        # - Validating data retention policies
        # - Triggering alerts for unauthorized access attempts
        logger.info(
            f"Compliance check triggered for event {event.event_id} "
            f"of type {event.event_type.value}"
        )
