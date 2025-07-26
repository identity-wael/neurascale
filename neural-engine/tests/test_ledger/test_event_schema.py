"""Tests for event schema definitions."""

import pytest
from datetime import datetime
import json

from ledger.event_schema import (
    EventType,
    NeuralLedgerEvent,
    SessionEvent,
    DataEvent,
    DeviceEvent,
    MLEvent,
    AccessEvent,
    requires_signature,
    CRITICAL_EVENT_TYPES,
)


class TestEventSchema:
    """Test suite for event schema functionality."""

    def test_event_type_enum(self):
        """Test EventType enum values."""
        # Verify key event types exist
        assert EventType.SESSION_CREATED.value == "session.created"
        assert EventType.DATA_INGESTED.value == "data.ingested"
        assert EventType.ACCESS_GRANTED.value == "access.granted"

        # Verify all event types have proper naming convention
        for event_type in EventType:
            assert "." in event_type.value
            category, action = event_type.value.split(".")
            assert category in ["session", "data", "device", "ml", "auth", "access"]

    def test_neural_ledger_event_creation(self):
        """Test basic event creation."""
        event = NeuralLedgerEvent(
            event_type=EventType.SESSION_CREATED,
            session_id="test-session",
            user_id="encrypted-user",
            metadata={"key": "value"},
        )

        assert event.event_id is not None
        assert len(event.event_id) == 36  # UUID format
        assert event.timestamp is not None
        assert event.event_type == EventType.SESSION_CREATED
        assert event.session_id == "test-session"
        assert event.user_id == "encrypted-user"
        assert event.metadata == {"key": "value"}
        assert event.previous_hash == "0" * 64
        assert event.event_hash == ""

    def test_event_to_dict(self):
        """Test event serialization to dictionary."""
        timestamp = datetime(2025, 1, 1, 12, 0, 0)
        event = NeuralLedgerEvent(
            event_id="test-123",
            timestamp=timestamp,
            event_type=EventType.DATA_INGESTED,
            session_id="session-456",
            data_hash="hash-789",
            metadata={"size": 1024},
            event_hash="event-hash",
            signature="signature",
            signing_key_id="key-id",
        )

        event_dict = event.to_dict()

        assert event_dict["event_id"] == "test-123"
        assert event_dict["timestamp"] == timestamp.isoformat()
        assert event_dict["event_type"] == "data.ingested"
        assert event_dict["session_id"] == "session-456"
        assert event_dict["data_hash"] == "hash-789"
        assert event_dict["metadata"] == {"size": 1024}
        assert event_dict["event_hash"] == "event-hash"
        assert event_dict["signature"] == "signature"
        assert event_dict["signing_key_id"] == "key-id"

    def test_event_from_dict(self):
        """Test event deserialization from dictionary."""
        event_data = {
            "event_id": "test-123",
            "timestamp": "2025-01-01T12:00:00",
            "event_type": "session.created",
            "session_id": "session-456",
            "user_id": "user-789",
            "metadata": {"protocol": "realtime"},
            "previous_hash": "prev-hash",
            "event_hash": "event-hash",
        }

        event = NeuralLedgerEvent.from_dict(event_data)

        assert event.event_id == "test-123"
        assert event.timestamp == datetime(2025, 1, 1, 12, 0, 0)
        assert event.event_type == EventType.SESSION_CREATED
        assert event.session_id == "session-456"
        assert event.user_id == "user-789"
        assert event.metadata == {"protocol": "realtime"}
        assert event.previous_hash == "prev-hash"
        assert event.event_hash == "event-hash"

    def test_session_event(self):
        """Test SessionEvent specialized class."""
        event = SessionEvent(
            session_id="session-123",
            event_type=EventType.SESSION_STARTED,
            session_version="2.0",
            protocol="batch",
        )

        assert event.session_id == "session-123"
        assert event.event_type == EventType.SESSION_STARTED
        assert event.metadata["session_version"] == "2.0"
        assert event.metadata["protocol"] == "batch"

    def test_data_event(self):
        """Test DataEvent specialized class."""
        event = DataEvent(
            session_id="session-123",
            data_hash="hash-456",
            event_type=EventType.DATA_INGESTED,
            data_size_bytes=2048,
            channel_count=64,
            sampling_rate=1000,
        )

        assert event.session_id == "session-123"
        assert event.data_hash == "hash-456"
        assert event.event_type == EventType.DATA_INGESTED
        assert event.metadata["data_size_bytes"] == 2048
        assert event.metadata["channel_count"] == 64
        assert event.metadata["sampling_rate"] == 1000

    def test_device_event(self):
        """Test DeviceEvent specialized class."""
        event = DeviceEvent(
            device_id="device-123",
            event_type=EventType.DEVICE_CONNECTED,
            device_type="BrainFlow",
            firmware_version="1.2.3",
            connection_type="bluetooth",
        )

        assert event.device_id == "device-123"
        assert event.event_type == EventType.DEVICE_CONNECTED
        assert event.metadata["device_type"] == "BrainFlow"
        assert event.metadata["firmware_version"] == "1.2.3"
        assert event.metadata["connection_type"] == "bluetooth"

    def test_ml_event(self):
        """Test MLEvent specialized class."""
        event = MLEvent(
            session_id="session-123",
            event_type=EventType.MODEL_INFERENCE,
            model_id="transformer-v2",
            model_version="2.1.0",
            inference_latency_ms=45,
        )

        assert event.session_id == "session-123"
        assert event.event_type == EventType.MODEL_INFERENCE
        assert event.metadata["model_id"] == "transformer-v2"
        assert event.metadata["model_version"] == "2.1.0"
        assert event.metadata["inference_latency_ms"] == 45

    def test_access_event(self):
        """Test AccessEvent specialized class."""
        event = AccessEvent(
            user_id="user-123",
            event_type=EventType.ACCESS_GRANTED,
            ip_address="192.168.1.1",
            user_agent="NeuralClient/1.0",
            resource="/api/sessions/456",
            action="read",
        )

        assert event.user_id == "user-123"
        assert event.event_type == EventType.ACCESS_GRANTED
        assert event.metadata["ip_address"] == "192.168.1.1"
        assert event.metadata["user_agent"] == "NeuralClient/1.0"
        assert event.metadata["resource"] == "/api/sessions/456"
        assert event.metadata["action"] == "read"

    def test_requires_signature(self):
        """Test signature requirement logic."""
        # Critical events require signature
        assert requires_signature(EventType.SESSION_CREATED) is True
        assert requires_signature(EventType.SESSION_ENDED) is True
        assert requires_signature(EventType.DATA_EXPORTED) is True
        assert requires_signature(EventType.ACCESS_GRANTED) is True
        assert requires_signature(EventType.AUTH_FAILURE) is True

        # Non-critical events don't require signature
        assert requires_signature(EventType.DATA_INGESTED) is False
        assert requires_signature(EventType.DEVICE_CONNECTED) is False
        assert requires_signature(EventType.MODEL_INFERENCE) is False

    def test_critical_event_types_coverage(self):
        """Test that all critical event types are properly defined."""
        # Verify critical events include all security-related events
        security_events = [
            EventType.AUTH_SUCCESS,
            EventType.AUTH_FAILURE,
            EventType.ACCESS_GRANTED,
            EventType.ACCESS_DENIED,
        ]

        for event in security_events:
            assert event in CRITICAL_EVENT_TYPES

        # Verify critical events include data export
        assert EventType.DATA_EXPORTED in CRITICAL_EVENT_TYPES

    def test_event_json_serialization(self):
        """Test that events can be JSON serialized."""
        event = NeuralLedgerEvent(
            event_type=EventType.SESSION_CREATED,
            metadata={"complex": {"nested": ["data", 123, True]}},
        )

        # Should serialize without errors
        json_str = json.dumps(event.to_dict())

        # Should deserialize back
        loaded_data = json.loads(json_str)
        restored_event = NeuralLedgerEvent.from_dict(loaded_data)

        assert restored_event.event_type == event.event_type
        assert restored_event.metadata == event.metadata
