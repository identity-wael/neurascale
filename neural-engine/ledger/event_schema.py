"""Event schema definitions for the Neural Ledger."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional, Any
from enum import Enum
import uuid


class EventType(Enum):
    """Event types tracked by the Neural Ledger."""

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
    """Base event structure for the Neural Ledger.

    All events in the ledger follow this structure to ensure
    consistency and enable hash chain verification.
    """

    # Immutable fields
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: EventType = field(default=EventType.SESSION_CREATED)

    # Context fields
    session_id: Optional[str] = None
    device_id: Optional[str] = None
    user_id: Optional[str] = None  # Encrypted user ID

    # Event data
    data_hash: Optional[str] = None  # SHA-256 of associated data
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Chain integrity
    previous_hash: str = "0" * 64  # Hash of previous event
    event_hash: str = ""  # Hash of this event

    # Security
    signature: Optional[str] = None  # Digital signature for critical events
    signing_key_id: Optional[str] = None  # KMS key used for signing

    def __post_init__(self) -> None:
        """Ensure event_id is always a string."""
        if not self.event_id:
            self.event_id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for storage."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type.value,
            "session_id": self.session_id,
            "device_id": self.device_id,
            "user_id": self.user_id,
            "data_hash": self.data_hash,
            "metadata": self.metadata,
            "previous_hash": self.previous_hash,
            "event_hash": self.event_hash,
            "signature": self.signature,
            "signing_key_id": self.signing_key_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NeuralLedgerEvent":
        """Create event from dictionary."""
        return cls(
            event_id=data.get("event_id", str(uuid.uuid4())),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            event_type=EventType(data["event_type"]),
            session_id=data.get("session_id"),
            device_id=data.get("device_id"),
            user_id=data.get("user_id"),
            data_hash=data.get("data_hash"),
            metadata=data.get("metadata", {}),
            previous_hash=data.get("previous_hash", "0" * 64),
            event_hash=data.get("event_hash", ""),
            signature=data.get("signature"),
            signing_key_id=data.get("signing_key_id"),
        )


# Specialized event classes for different event categories


@dataclass
class SessionEvent(NeuralLedgerEvent):
    """Events related to BCI session lifecycle."""

    def __init__(self, session_id: str, event_type: EventType, **kwargs: Any) -> None:
        # Extract metadata fields
        metadata_fields = {
            "session_version": kwargs.pop("session_version", "1.0"),
            "protocol": kwargs.pop("protocol", "realtime"),
        }
        # Initialize base class with remaining kwargs
        super().__init__(event_type=event_type, session_id=session_id, **kwargs)
        # Add session-specific metadata
        self.metadata.update(metadata_fields)


@dataclass
class DataEvent(NeuralLedgerEvent):
    """Events related to neural data pipeline."""

    def __init__(
        self, session_id: str, data_hash: str, event_type: EventType, **kwargs: Any
    ) -> None:
        # Extract metadata fields
        metadata_fields = {
            "data_size_bytes": kwargs.pop("data_size_bytes", 0),
            "channel_count": kwargs.pop("channel_count", 0),
            "sampling_rate": kwargs.pop("sampling_rate", 0),
        }
        # Initialize base class with remaining kwargs
        super().__init__(
            event_type=event_type, session_id=session_id, data_hash=data_hash, **kwargs
        )
        # Add data-specific metadata
        self.metadata.update(metadata_fields)


@dataclass
class DeviceEvent(NeuralLedgerEvent):
    """Events related to device management."""

    def __init__(self, device_id: str, event_type: EventType, **kwargs: Any) -> None:
        # Extract metadata fields
        metadata_fields = {
            "device_type": kwargs.pop("device_type", "unknown"),
            "firmware_version": kwargs.pop("firmware_version", "unknown"),
            "connection_type": kwargs.pop("connection_type", "unknown"),
        }
        # Initialize base class with remaining kwargs
        super().__init__(event_type=event_type, device_id=device_id, **kwargs)
        # Add device-specific metadata
        self.metadata.update(metadata_fields)


@dataclass
class MLEvent(NeuralLedgerEvent):
    """Events related to ML operations."""

    def __init__(self, session_id: str, event_type: EventType, **kwargs: Any) -> None:
        # Extract metadata fields
        metadata_fields = {
            "model_id": kwargs.pop("model_id", "unknown"),
            "model_version": kwargs.pop("model_version", "unknown"),
            "inference_latency_ms": kwargs.pop("inference_latency_ms", 0),
        }
        # Initialize base class with remaining kwargs
        super().__init__(event_type=event_type, session_id=session_id, **kwargs)
        # Add ML-specific metadata
        self.metadata.update(metadata_fields)


@dataclass
class AccessEvent(NeuralLedgerEvent):
    """Events related to access control and security."""

    def __init__(self, user_id: str, event_type: EventType, **kwargs: Any) -> None:
        # Extract metadata fields
        metadata_fields = {
            "ip_address": kwargs.pop("ip_address", "unknown"),
            "user_agent": kwargs.pop("user_agent", "unknown"),
            "resource": kwargs.pop("resource", "unknown"),
            "action": kwargs.pop("action", "unknown"),
        }
        # Initialize base class with remaining kwargs
        super().__init__(event_type=event_type, user_id=user_id, **kwargs)
        # Add access-specific metadata
        self.metadata.update(metadata_fields)


# Critical events that require digital signatures
CRITICAL_EVENT_TYPES = {
    EventType.SESSION_CREATED,
    EventType.SESSION_ENDED,
    EventType.DATA_EXPORTED,
    EventType.AUTH_SUCCESS,
    EventType.AUTH_FAILURE,
    EventType.ACCESS_GRANTED,
    EventType.ACCESS_DENIED,
    EventType.MODEL_CALIBRATION,
}


def requires_signature(event_type: EventType) -> bool:
    """Check if an event type requires digital signature."""
    return event_type in CRITICAL_EVENT_TYPES
