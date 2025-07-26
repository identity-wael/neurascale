"""Neural Ledger - Main implementation for HIPAA-compliant audit trail.

This module implements the core Neural Ledger functionality for the NeuraScale
Neural Engine, providing an immutable audit trail for all neural data operations.

Priority: HIGHEST (Week 1, Days 1-4)
Compliance: HIPAA, GDPR, FDA 21 CFR Part 11
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Any

from google.cloud import pubsub_v1, bigtable, firestore, bigquery
from google.cloud import kms
from google.cloud.exceptions import NotFound

from .event_schema import (
    NeuralLedgerEvent,
    EventType,
    requires_signature,
)
from .hash_chain import HashChain
from .event_processor import EventProcessor

logger = logging.getLogger(__name__)


class NeuralLedger:
    """Main Neural Ledger implementation with multi-tier storage.

    This class coordinates the entire ledger system, managing:
    - Event ingestion through Pub/Sub
    - Multi-tier storage (Bigtable, Firestore, BigQuery)
    - Hash chain integrity
    - Digital signatures for critical events
    - HIPAA-compliant audit trails
    """

    def __init__(self, project_id: str, location: str = "northamerica-northeast1"):
        """Initialize Neural Ledger with GCP services.

        Args:
            project_id: GCP project ID
            location: GCP region for services
        """
        self.project_id = project_id
        self.location = location

        # Initialize GCP clients
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient()
        self.bigtable_client = bigtable.Client(project=project_id)
        self.firestore_client = firestore.Client(project=project_id)
        self.bigquery_client = bigquery.Client(project=project_id)
        self.kms_client = kms.KeyManagementServiceClient()

        # Configuration
        self.topic_name = f"projects/{project_id}/topics/neural-ledger-events"
        self.subscription_name = (
            f"projects/{project_id}/subscriptions/neural-ledger-processor"
        )
        self.bigtable_instance_id = "neural-ledger"
        self.bigtable_table_id = "events"
        self.bigquery_dataset_id = "neural_ledger"

        # Initialize event processor
        self.event_processor = EventProcessor(
            project_id=project_id,
            location=location,
            bigtable_client=self.bigtable_client,
            firestore_client=self.firestore_client,
            bigquery_client=self.bigquery_client,
            kms_client=self.kms_client,
        )

        # Chain state
        self._last_event_hash = "0" * 64  # Genesis block

    async def initialize(self):
        """Initialize all GCP resources for the ledger."""
        logger.info("Initializing Neural Ledger infrastructure...")

        # Create Pub/Sub topic and subscription
        await self._ensure_pubsub_resources()

        # Initialize storage systems
        await self._ensure_bigtable_resources()
        await self._ensure_firestore_collections()
        await self._ensure_bigquery_resources()

        # Load last event hash for chain continuity
        await self._load_chain_state()

        logger.info("Neural Ledger initialization complete")

    async def log_event(
        self,
        event_type: EventType,
        session_id: Optional[str] = None,
        device_id: Optional[str] = None,
        user_id: Optional[str] = None,
        data_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> NeuralLedgerEvent:
        """Log an event to the Neural Ledger.

        This is the main entry point for logging events. The event will be:
        1. Added to the hash chain
        2. Digitally signed if critical
        3. Published to Pub/Sub for processing
        4. Written to multi-tier storage

        Args:
            event_type: Type of event to log
            session_id: Associated session ID
            device_id: Associated device ID
            user_id: Encrypted user ID
            data_hash: SHA-256 hash of associated data
            metadata: Event-specific metadata

        Returns:
            The logged event with hash and signature
        """
        # Create the event
        event = NeuralLedgerEvent(
            event_type=event_type,
            session_id=session_id,
            device_id=device_id,
            user_id=user_id,
            data_hash=data_hash,
            metadata=metadata or {},
            previous_hash=self._last_event_hash,
        )

        # Compute event hash
        event.event_hash = HashChain.compute_event_hash(event, event.previous_hash)

        # Add digital signature for critical events
        if requires_signature(event_type):
            await self._sign_event(event)

        # Publish to Pub/Sub for processing
        await self._publish_event(event)

        # Update chain state
        self._last_event_hash = event.event_hash

        # Log performance metrics
        logger.info(
            f"Logged event: type={event_type.value}, "
            f"id={event.event_id}, hash={event.event_hash[:8]}..."
        )

        return event

    async def log_session_created(
        self,
        session_id: str,
        user_id: str,
        device_id: str,
        metadata: Optional[Dict] = None,
    ) -> NeuralLedgerEvent:
        """Log session creation event."""
        full_metadata = {
            "device_id": device_id,
            "session_version": "1.0",
            "protocol": "realtime",
            **(metadata or {}),
        }

        return await self.log_event(
            event_type=EventType.SESSION_CREATED,
            session_id=session_id,
            user_id=user_id,
            device_id=device_id,
            metadata=full_metadata,
        )

    async def log_data_ingested(
        self,
        session_id: str,
        data_hash: str,
        size_bytes: int,
        metadata: Optional[Dict] = None,
    ) -> NeuralLedgerEvent:
        """Log data ingestion event."""
        full_metadata = {
            "data_size_bytes": size_bytes,
            "ingestion_timestamp": datetime.now(timezone.utc).isoformat(),
            **(metadata or {}),
        }

        return await self.log_event(
            event_type=EventType.DATA_INGESTED,
            session_id=session_id,
            data_hash=data_hash,
            metadata=full_metadata,
        )

    async def log_device_connected(
        self, device_id: str, device_type: str, metadata: Optional[Dict] = None
    ) -> NeuralLedgerEvent:
        """Log device connection event."""
        full_metadata = {
            "device_type": device_type,
            "connection_timestamp": datetime.now(timezone.utc).isoformat(),
            **(metadata or {}),
        }

        return await self.log_event(
            event_type=EventType.DEVICE_CONNECTED,
            device_id=device_id,
            metadata=full_metadata,
        )

    async def log_access_event(
        self,
        user_id: str,
        granted: bool,
        resource: str,
        metadata: Optional[Dict] = None,
    ) -> NeuralLedgerEvent:
        """Log access control event."""
        event_type = EventType.ACCESS_GRANTED if granted else EventType.ACCESS_DENIED

        full_metadata = {
            "resource": resource,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **(metadata or {}),
        }

        return await self.log_event(
            event_type=event_type,
            user_id=user_id,
            metadata=full_metadata,
        )

    async def verify_chain_integrity(
        self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None
    ) -> bool:
        """Verify the integrity of the hash chain.

        Args:
            start_time: Start of time range to verify
            end_time: End of time range to verify

        Returns:
            True if chain is valid, False if compromised
        """
        # Query events from BigQuery for the time range
        query = f"""
        SELECT *
        FROM `{self.project_id}.{self.bigquery_dataset_id}.events`
        WHERE timestamp BETWEEN @start_time AND @end_time
        ORDER BY timestamp ASC
        """

        if not start_time:
            start_time = datetime.now(timezone.utc) - timedelta(days=1)
        if not end_time:
            end_time = datetime.now(timezone.utc)

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("start_time", "TIMESTAMP", start_time),
                bigquery.ScalarQueryParameter("end_time", "TIMESTAMP", end_time),
            ]
        )

        # Execute query
        query_job = self.bigquery_client.query(query, job_config=job_config)
        results = query_job.result()

        # Convert to event objects
        events = []
        for row in results:
            event_data = dict(row)
            events.append(NeuralLedgerEvent.from_dict(event_data))

        # Verify chain
        is_valid = HashChain.verify_chain(events)

        if not is_valid:
            logger.error(
                f"Chain integrity violation detected between {start_time} and {end_time}"
            )
            # TODO: Trigger compliance alert

        return is_valid

    async def get_compliance_report(
        self, report_type: str, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Generate compliance report for auditing.

        Args:
            report_type: Type of report (HIPAA, GDPR, etc.)
            start_date: Report start date
            end_date: Report end date

        Returns:
            Compliance report data
        """
        if report_type == "HIPAA":
            return await self._generate_hipaa_report(start_date, end_date)
        elif report_type == "GDPR":
            return await self._generate_gdpr_report(start_date, end_date)
        else:
            raise ValueError(f"Unsupported report type: {report_type}")

    # Private methods

    async def _ensure_pubsub_resources(self):
        """Ensure Pub/Sub topic and subscription exist."""
        # Create topic if not exists
        try:
            self.publisher.create_topic(request={"name": self.topic_name})
            logger.info(f"Created Pub/Sub topic: {self.topic_name}")
        except Exception as e:
            if "already exists" not in str(e):
                raise

        # Create subscription if not exists
        try:
            self.subscriber.create_subscription(
                request={
                    "name": self.subscription_name,
                    "topic": self.topic_name,
                    "ack_deadline_seconds": 60,
                    "message_retention_duration": {
                        "seconds": 7 * 24 * 60 * 60
                    },  # 7 days
                }
            )
            logger.info(f"Created Pub/Sub subscription: {self.subscription_name}")
        except Exception as e:
            if "already exists" not in str(e):
                raise

    async def _ensure_bigtable_resources(self):
        """Ensure Bigtable instance and table exist."""
        # This would be handled by Terraform in production
        logger.info("Bigtable resources should be provisioned via Terraform")

    async def _ensure_firestore_collections(self):
        """Ensure Firestore collections exist."""
        # Collections are created automatically on first write
        logger.info("Firestore collections will be created on first write")

    async def _ensure_bigquery_resources(self):
        """Ensure BigQuery dataset and tables exist."""
        # Create dataset if not exists
        dataset_id = f"{self.project_id}.{self.bigquery_dataset_id}"
        dataset = bigquery.Dataset(dataset_id)
        dataset.location = self.location

        try:
            self.bigquery_client.create_dataset(dataset)
            logger.info(f"Created BigQuery dataset: {dataset_id}")
        except Exception as e:
            if "already exists" not in str(e):
                raise

        # Create events table if not exists
        table_id = f"{dataset_id}.events"
        schema = [
            bigquery.SchemaField("event_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("timestamp", "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("event_type", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("session_id", "STRING"),
            bigquery.SchemaField("device_id", "STRING"),
            bigquery.SchemaField("user_id", "STRING"),
            bigquery.SchemaField("data_hash", "STRING"),
            bigquery.SchemaField("metadata", "JSON"),
            bigquery.SchemaField("previous_hash", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("event_hash", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("signature", "STRING"),
            bigquery.SchemaField("signing_key_id", "STRING"),
        ]

        table = bigquery.Table(table_id, schema=schema)
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="timestamp",
        )

        try:
            self.bigquery_client.create_table(table)
            logger.info(f"Created BigQuery table: {table_id}")
        except Exception as e:
            if "already exists" not in str(e):
                raise

    async def _load_chain_state(self):
        """Load the last event hash for chain continuity."""
        query = f"""
        SELECT event_hash
        FROM `{self.project_id}.{self.bigquery_dataset_id}.events`
        ORDER BY timestamp DESC
        LIMIT 1
        """

        try:
            query_job = self.bigquery_client.query(query)
            results = list(query_job.result())

            if results:
                self._last_event_hash = results[0].event_hash
                logger.info(
                    f"Loaded chain state: last_hash={self._last_event_hash[:8]}..."
                )
            else:
                logger.info("No existing events, starting with genesis block")
        except NotFound:
            logger.info("Events table not found, starting with genesis block")

    async def _sign_event(self, event: NeuralLedgerEvent):
        """Add digital signature to critical events."""
        # TODO: Implement actual KMS signing
        # For now, use a placeholder
        event.signature = f"SIGNATURE_{event.event_hash[:16]}"
        event.signing_key_id = f"projects/{self.project_id}/locations/{self.location}/keyRings/neural-ledger/cryptoKeys/signing-key/cryptoKeyVersions/1"

    async def _publish_event(self, event: NeuralLedgerEvent):
        """Publish event to Pub/Sub for processing."""
        import json

        # Convert event to JSON
        event_data = json.dumps(event.to_dict()).encode("utf-8")

        # Publish to topic
        future = self.publisher.publish(self.topic_name, event_data)

        # Wait for publish to complete
        message_id = future.result()
        logger.debug(f"Published event {event.event_id} with message ID: {message_id}")

    async def _generate_hipaa_report(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Generate HIPAA compliance report."""
        # Query all access events
        query = f"""
        SELECT
            DATE(timestamp) as date,
            user_id,
            event_type,
            JSON_EXTRACT_SCALAR(metadata, '$.resource') as resource,
            COUNT(*) as access_count
        FROM `{self.project_id}.{self.bigquery_dataset_id}.events`
        WHERE event_type IN ('access.granted', 'access.denied', 'data.exported')
          AND DATE(timestamp) BETWEEN @start_date AND @end_date
        GROUP BY date, user_id, event_type, resource
        ORDER BY date DESC
        """

        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("start_date", "DATE", start_date.date()),
                bigquery.ScalarQueryParameter("end_date", "DATE", end_date.date()),
            ]
        )

        query_job = self.bigquery_client.query(query, job_config=job_config)
        results = list(query_job.result())

        return {
            "report_type": "HIPAA",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "access_summary": [dict(row) for row in results],
            "total_events": sum(row.access_count for row in results),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def _generate_gdpr_report(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Generate GDPR compliance report."""
        # Similar to HIPAA but focused on data exports and user requests
        # TODO: Implement GDPR-specific queries
        return {
            "report_type": "GDPR",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "data_exports": [],
            "user_requests": [],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
