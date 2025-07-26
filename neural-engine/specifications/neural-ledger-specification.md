# Neural Ledger Implementation Specification

## Document Version

- **Version**: 1.0.0
- **Date**: January 26, 2025
- **Author**: Principal Engineer
- **Status**: Ready for Implementation

## 1. Executive Summary

The Neural Ledger is a critical compliance and audit infrastructure component for the NeuraScale Neural Engine. It provides an immutable, cryptographically-secured audit trail for all neural data operations, ensuring HIPAA compliance, data integrity, and traceability for medical-grade BCI applications.

## 2. System Context

### 2.1 Integration Points

The Neural Ledger integrates with:

- **Neural Data Ingestion Pipeline**: Logs all incoming neural data
- **Device Manager**: Tracks device connections and health
- **ML Pipeline**: Records model inferences and calibrations
- **API Layer**: Audits all data access requests
- **Session Manager**: Tracks BCI session lifecycle

### 2.2 Existing Infrastructure

- **Cloud Functions**: Already implemented for signal processing
- **Pub/Sub Topics**: Existing topics for neural data streams
- **BigQuery**: Dataset `neurascale.neural_data` already exists
- **Bigtable**: Instance `neural-signals` configured
- **Cloud KMS**: Encryption keys in `neural-engine/neural-engine/security/`

## 3. Functional Requirements

### 3.1 Core Event Tracking

The system SHALL track the following event categories:

#### 3.1.1 Session Events

- Session creation with user/device binding
- Session state changes (calibrating, active, paused, ended)
- Session errors and recovery attempts
- Session data export requests

#### 3.1.2 Data Pipeline Events

- Raw neural data ingestion (with data hash)
- Signal processing completion
- Feature extraction results
- Data storage confirmations

#### 3.1.3 Device Events

- Device discovery and pairing
- Connection establishment/loss
- Impedance check results
- Signal quality metrics

#### 3.1.4 ML Model Events

- Inference requests and results
- Model loading/unloading
- Calibration procedures
- Accuracy metrics

#### 3.1.5 Access Control Events

- Authentication attempts
- Authorization decisions
- Data access requests
- Export operations

### 3.2 Compliance Requirements

- **HIPAA**: 7-year retention for all PHI-related events
- **GDPR**: Right to audit data access within 30 days
- **FDA 21 CFR Part 11**: Electronic signatures for critical events
- **SOC 2**: Complete audit trail for security events

## 4. Technical Architecture

### 4.1 Event Schema

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, Any
from enum import Enum

class EventType(Enum):
    # Session lifecycle
    SESSION_CREATED = "session.created"
    SESSION_STARTED = "session.started"
    SESSION_PAUSED = "session.paused"
    SESSION_RESUMED = "session.resumed"
    SESSION_ENDED = "session.ended"
    SESSION_ERROR = "session.error"

    # Data pipeline
    DATA_INGESTED = "data.ingested"
    DATA_PROCESSED = "data.processed"
    DATA_STORED = "data.stored"
    DATA_QUALITY_CHECK = "data.quality_check"

    # Device management
    DEVICE_DISCOVERED = "device.discovered"
    DEVICE_PAIRED = "device.paired"
    DEVICE_CONNECTED = "device.connected"
    DEVICE_DISCONNECTED = "device.disconnected"
    DEVICE_ERROR = "device.error"
    DEVICE_IMPEDANCE_CHECK = "device.impedance_check"

    # ML operations
    MODEL_LOADED = "ml.model_loaded"
    MODEL_INFERENCE = "ml.inference"
    MODEL_CALIBRATION = "ml.calibration"
    MODEL_PERFORMANCE = "ml.performance"

    # Access control
    AUTH_SUCCESS = "auth.success"
    AUTH_FAILURE = "auth.failure"
    ACCESS_GRANTED = "access.granted"
    ACCESS_DENIED = "access.denied"
    DATA_EXPORTED = "data.exported"

@dataclass
class NeuralLedgerEvent:
    # Immutable fields
    event_id: str                    # UUID v4
    timestamp: datetime              # UTC timestamp
    event_type: EventType           # Event category

    # Context fields
    session_id: Optional[str]       # BCI session identifier
    device_id: Optional[str]        # Device identifier
    user_id: Optional[str]          # Encrypted user ID

    # Event data
    data_hash: Optional[str]        # SHA-256 of associated data
    metadata: Dict[str, Any]        # Event-specific metadata

    # Chain integrity
    previous_hash: str              # Hash of previous event
    event_hash: str                 # Hash of this event

    # Security
    signature: Optional[str]        # Digital signature for critical events
    signing_key_id: Optional[str]   # KMS key used for signing
```

### 4.2 Storage Architecture

```yaml
# Multi-tier storage for different access patterns

1. Cloud Pub/Sub:
   - Topic: neural-ledger-events
   - Purpose: Event ingestion and distribution
   - Retention: 7 days
   - Throughput: 100,000 events/second

2. Bigtable:
   - Instance: neural-ledger
   - Table: events
   - Row key: {reversed_timestamp}#{event_id}
   - Column families:
     - event: Core event data
     - metadata: Event metadata
     - chain: Hash chain data
   - Purpose: High-frequency event queries
   - Retention: 90 days

3. Firestore:
   - Collection: ledger_sessions
   - Document ID: {session_id}
   - Purpose: Real-time session state
   - Subcollections:
     - events: Session-specific events
     - metrics: Aggregated metrics

4. BigQuery:
   - Dataset: neural_ledger
   - Tables:
     - events: All events (partitioned by date)
     - events_daily: Daily aggregates
     - compliance_reports: Generated reports
   - Purpose: Long-term storage and analytics
   - Retention: 7 years (HIPAA requirement)
```

### 4.3 Processing Pipeline

```python
# Cloud Function: neural-ledger-processor
import asyncio
from google.cloud import pubsub_v1, bigtable, firestore, bigquery
from google.cloud import kms

class LedgerProcessor:
    def __init__(self):
        self.publisher = pubsub_v1.PublisherClient()
        self.bigtable_client = bigtable.Client()
        self.firestore_client = firestore.Client()
        self.bigquery_client = bigquery.Client()
        self.kms_client = kms.KeyManagementServiceClient()

    async def process_event(self, event: NeuralLedgerEvent):
        """Process incoming ledger event with parallel writes"""

        # Step 1: Validate event integrity
        if not self.validate_hash_chain(event):
            raise ValueError("Hash chain validation failed")

        # Step 2: Add digital signature for critical events
        if self.requires_signature(event.event_type):
            event.signature = await self.sign_event(event)

        # Step 3: Parallel writes to all storage systems
        await asyncio.gather(
            self.write_to_bigtable(event),
            self.write_to_firestore(event),
            self.write_to_bigquery(event),
            self.update_metrics(event)
        )

        # Step 4: Trigger compliance checks if needed
        if self.is_compliance_event(event.event_type):
            await self.trigger_compliance_check(event)

    def validate_hash_chain(self, event: NeuralLedgerEvent) -> bool:
        """Verify the event's hash chain integrity"""
        # Implementation details in section 5.2

    async def sign_event(self, event: NeuralLedgerEvent) -> str:
        """Digitally sign critical events using Cloud KMS"""
        # Implementation details in section 5.3
```

## 5. Implementation Details

### 5.1 Hash Chain Implementation

```python
import hashlib
import json
from typing import Dict, Any

class HashChain:
    @staticmethod
    def compute_event_hash(event: Dict[str, Any], previous_hash: str) -> str:
        """Compute SHA-256 hash for event integrity"""
        # Create deterministic JSON representation
        event_data = {
            'event_id': event['event_id'],
            'timestamp': event['timestamp'].isoformat(),
            'event_type': event['event_type'],
            'session_id': event.get('session_id'),
            'device_id': event.get('device_id'),
            'data_hash': event.get('data_hash'),
            'previous_hash': previous_hash
        }

        # Sort keys for deterministic hashing
        canonical_json = json.dumps(event_data, sort_keys=True)

        # Compute SHA-256 hash
        return hashlib.sha256(canonical_json.encode()).hexdigest()

    @staticmethod
    def verify_chain(events: List[Dict[str, Any]]) -> bool:
        """Verify integrity of event chain"""
        previous_hash = "0" * 64  # Genesis block

        for event in events:
            expected_hash = HashChain.compute_event_hash(event, previous_hash)
            if event['event_hash'] != expected_hash:
                return False
            previous_hash = event['event_hash']

        return True
```

### 5.2 Digital Signature for Critical Events

```python
from google.cloud import kms
import base64

class EventSigner:
    def __init__(self, project_id: str, location: str, keyring: str, key: str):
        self.kms_client = kms.KeyManagementServiceClient()
        self.key_name = f"projects/{project_id}/locations/{location}/keyRings/{keyring}/cryptoKeys/{key}/cryptoKeyVersions/1"

    async def sign_event(self, event: NeuralLedgerEvent) -> str:
        """Sign critical events for non-repudiation"""
        # Create signing payload
        payload = {
            'event_id': event.event_id,
            'event_type': event.event_type.value,
            'timestamp': event.timestamp.isoformat(),
            'user_id': event.user_id,
            'data_hash': event.data_hash
        }

        # Convert to canonical JSON
        message = json.dumps(payload, sort_keys=True).encode()

        # Create digest
        digest = {'sha256': hashlib.sha256(message).digest()}

        # Sign with KMS
        response = self.kms_client.asymmetric_sign(
            request={
                'name': self.key_name,
                'digest': digest
            }
        )

        # Return base64 encoded signature
        return base64.b64encode(response.signature).decode()
```

### 5.3 Query Interface

```python
class LedgerQueryService:
    """High-level query interface for audit and compliance"""

    async def get_session_timeline(self, session_id: str) -> List[NeuralLedgerEvent]:
        """Get complete timeline of events for a session"""
        query = """
        SELECT * FROM `neurascale.neural_ledger.events`
        WHERE session_id = @session_id
        ORDER BY timestamp ASC
        """

    async def get_user_access_log(self, user_id: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get all data access events for a user in date range"""
        query = """
        SELECT
            timestamp,
            event_type,
            JSON_EXTRACT_SCALAR(metadata, '$.resource') as resource,
            JSON_EXTRACT_SCALAR(metadata, '$.action') as action,
            JSON_EXTRACT_SCALAR(metadata, '$.ip_address') as ip_address
        FROM `neurascale.neural_ledger.events`
        WHERE user_id = @user_id
          AND event_type IN ('access.granted', 'access.denied', 'data.exported')
          AND DATE(timestamp) BETWEEN @start_date AND @end_date
        ORDER BY timestamp DESC
        """

    async def verify_data_integrity(self, session_id: str, data_hash: str) -> bool:
        """Verify that data hasn't been tampered with"""
        # Query for the original ingestion event
        # Verify hash chain from ingestion to current state

    async def generate_hipaa_audit_report(self, start_date: datetime, end_date: datetime) -> Dict:
        """Generate HIPAA-compliant audit report"""
        # Include all PHI access events
        # Include authorization failures
        # Include data exports
        # Group by user and resource
```

## 6. Performance Requirements

### 6.1 Latency Targets

- Event ingestion: < 10ms (p99)
- Hash computation: < 1ms
- Digital signature: < 50ms
- Bigtable write: < 5ms
- BigQuery streaming insert: < 100ms

### 6.2 Throughput Targets

- Sustained: 10,000 events/second
- Peak: 100,000 events/second
- Query response: < 2 seconds for 1 million events

### 6.3 Availability

- 99.99% uptime for write operations
- 99.9% uptime for query operations
- RPO: 1 second
- RTO: 5 minutes

## 7. Security Considerations

### 7.1 Encryption

- All events encrypted at rest using Google-managed encryption keys
- User IDs hashed using PBKDF2 with salt
- Sensitive metadata encrypted using Cloud KMS

### 7.2 Access Control

- Service account for ledger processor with minimal permissions
- Separate read-only service account for queries
- IAM policies enforced at resource level

### 7.3 Network Security

- All traffic over TLS 1.3
- Private Google Access for GCP services
- No public IPs on compute resources

## 8. Monitoring and Alerting

### 8.1 Key Metrics

```yaml
# Custom metrics to track
- neural_ledger_events_processed_total
- neural_ledger_event_processing_duration_seconds
- neural_ledger_hash_validation_failures_total
- neural_ledger_storage_write_failures_total
- neural_ledger_signature_operations_total
- neural_ledger_compliance_checks_triggered_total
```

### 8.2 Alerts

```yaml
# Critical alerts
- Event processing latency > 50ms (p99)
- Hash validation failure rate > 0.1%
- Storage write failure rate > 1%
- No events processed for 5 minutes
```

### 8.3 Dashboards

- Real-time event processing rate
- Event type distribution
- Storage system health
- Compliance report generation status

## 9. Testing Requirements

### 9.1 Unit Tests

- Hash chain computation and validation
- Event signature generation and verification
- Schema validation for all event types
- Query interface methods

### 9.2 Integration Tests

- End-to-end event processing
- Multi-storage write consistency
- Hash chain integrity under load
- Compliance report generation

### 9.3 Load Tests

- 100,000 events/second sustained for 1 hour
- 1 million event query performance
- Storage system failover behavior

### 9.4 Compliance Tests

- HIPAA audit report accuracy
- Data retention policy enforcement
- Access control verification

## 10. Migration and Rollout Plan

### 10.1 Phase 1: Infrastructure Setup (Day 1)

- Deploy Cloud Function for event processor
- Configure Pub/Sub topic and subscriptions
- Set up Bigtable instance and schema
- Configure BigQuery dataset and tables

### 10.2 Phase 2: Core Implementation (Day 2)

- Implement hash chain logic
- Integrate Cloud KMS for signatures
- Deploy parallel write logic
- Add basic monitoring

### 10.3 Phase 3: Integration (Day 3)

- Integrate with neural data ingestion
- Add device manager hooks
- Connect to session management
- Enable API audit logging

### 10.4 Phase 4: Validation (Day 4)

- Run compliance tests
- Perform load testing
- Verify hash chain integrity
- Generate sample audit reports

## 11. Cost Estimation (Monthly)

```yaml
# Based on 10M events/day average
Pub/Sub: $50 (ingestion + delivery)
Bigtable: $800 (3 nodes for HA)
Firestore: $200 (10GB storage + reads)
BigQuery: $300 (1TB storage + queries)
Cloud Functions: $100 (compute + invocations)
Cloud KMS: $50 (signature operations)
Total: ~$1,500/month
```

## 12. Success Criteria

1. **Functional**

   - All event types successfully captured
   - Hash chain validates 100% of events
   - Audit reports generate in < 5 minutes

2. **Performance**

   - Meets all latency targets at 2x expected load
   - Zero data loss during failover tests
   - Query performance within targets

3. **Compliance**
   - Passes HIPAA audit requirements
   - Meets GDPR data access requirements
   - Satisfies FDA 21 CFR Part 11 for digital signatures

## 13. Appendices

### A. Event Type Examples

[Detailed examples of each event type with metadata]

### B. BigQuery Schema

[Complete DDL for all BigQuery tables]

### C. IAM Policies

[Detailed IAM roles and permissions]

### D. Monitoring Queries

[PromQL queries for all metrics]
