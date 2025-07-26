"""Tests for hash chain integrity system."""

import pytest
from datetime import datetime
import hashlib

from ledger.hash_chain import HashChain
from ledger.event_schema import NeuralLedgerEvent, EventType


class TestHashChain:
    """Test suite for hash chain functionality."""

    def test_compute_event_hash(self):
        """Test event hash computation."""
        event = NeuralLedgerEvent(
            event_id="test-123",
            event_type=EventType.SESSION_CREATED,
            timestamp=datetime(2025, 1, 1, 12, 0, 0),
            session_id="session-456",
        )

        previous_hash = "0" * 64
        hash_result = HashChain.compute_event_hash(event, previous_hash)

        # Verify hash is 64 characters (SHA-256)
        assert len(hash_result) == 64
        assert all(c in "0123456789abcde" for c in hash_result)

    def test_compute_data_hash(self):
        """Test data hash computation."""
        test_data = b"Neural data packet 12345"
        hash_result = HashChain.compute_data_hash(test_data)

        # Verify against known SHA-256
        expected_hash = hashlib.sha256(test_data).hexdigest()
        assert hash_result == expected_hash

    def test_verify_event_valid(self):
        """Test verification of valid event."""
        event = NeuralLedgerEvent(
            event_id="test-123",
            event_type=EventType.DATA_INGESTED,
            timestamp=datetime(2025, 1, 1, 12, 0, 0),
        )

        previous_hash = "0" * 64
        event.event_hash = HashChain.compute_event_hash(event, previous_hash)

        # Should verify successfully
        assert HashChain.verify_event(event, previous_hash) is True

    def test_verify_event_invalid(self):
        """Test verification of tampered event."""
        event = NeuralLedgerEvent(
            event_id="test-123",
            event_type=EventType.DATA_INGESTED,
        )

        previous_hash = "0" * 64
        event.event_hash = "invalid_hash"

        # Should fail verification
        assert HashChain.verify_event(event, previous_hash) is False

    def test_verify_chain_valid(self):
        """Test verification of valid event chain."""
        events = []
        previous_hash = "0" * 64

        # Create chain of 5 events
        for i in range(5):
            event = NeuralLedgerEvent(
                event_id=f"event-{i}",
                event_type=EventType.SESSION_CREATED,
                timestamp=datetime(2025, 1, 1, 12, i, 0),
                previous_hash=previous_hash,
            )
            event.event_hash = HashChain.compute_event_hash(event, previous_hash)
            events.append(event)
            previous_hash = event.event_hash

        # Should verify successfully
        assert HashChain.verify_chain(events) is True

    def test_verify_chain_broken(self):
        """Test detection of broken chain."""
        events = []
        previous_hash = "0" * 64

        # Create valid chain
        for i in range(5):
            event = NeuralLedgerEvent(
                event_id=f"event-{i}",
                event_type=EventType.SESSION_CREATED,
                timestamp=datetime(2025, 1, 1, 12, i, 0),
                previous_hash=previous_hash,
            )
            event.event_hash = HashChain.compute_event_hash(event, previous_hash)
            events.append(event)
            previous_hash = event.event_hash

        # Tamper with middle event
        events[2].metadata["tampered"] = True

        # Should fail verification
        assert HashChain.verify_chain(events) is False

    def test_find_chain_break(self):
        """Test finding location of chain break."""
        events = []
        previous_hash = "0" * 64

        # Create chain with break at index 3
        for i in range(5):
            event = NeuralLedgerEvent(
                event_id=f"event-{i}",
                event_type=EventType.SESSION_CREATED,
                timestamp=datetime(2025, 1, 1, 12, i, 0),
                previous_hash=previous_hash,
            )

            if i == 3:
                # Introduce break by using wrong previous hash
                event.previous_hash = "wrong_hash"

            event.event_hash = HashChain.compute_event_hash(event, event.previous_hash)
            events.append(event)
            previous_hash = event.event_hash if i < 3 else previous_hash

        # Should find break at index 3
        break_index = HashChain.find_chain_break(events)
        assert break_index == 3

    def test_repair_chain(self):
        """Test chain repair functionality."""
        # Create broken chain
        events = []
        for i in range(3):
            event = NeuralLedgerEvent(
                event_id=f"event-{i}",
                event_type=EventType.SESSION_CREATED,
                timestamp=datetime(2025, 1, 1, 12, i, 0),
                previous_hash="invalid",
                event_hash="invalid",
            )
            events.append(event)

        # Repair the chain
        repaired_events = HashChain.repair_chain(events)

        # Verify repaired chain
        assert HashChain.verify_chain(repaired_events) is True
        assert len(repaired_events) == len(events)

    def test_compute_merkle_root(self):
        """Test Merkle root computation."""
        events = []
        for i in range(8):
            event = NeuralLedgerEvent(
                event_id=f"event-{i}",
                event_type=EventType.SESSION_CREATED,
            )
            event.event_hash = f"hash_{i:064}"
            events.append(event)

        merkle_root = HashChain.compute_merkle_root(events)

        # Verify Merkle root properties
        assert len(merkle_root) == 64
        assert merkle_root != events[0].event_hash

        # Same events should produce same root
        merkle_root2 = HashChain.compute_merkle_root(events)
        assert merkle_root == merkle_root2

    def test_empty_chain_verification(self):
        """Test verification of empty chain."""
        assert HashChain.verify_chain([]) is True
        assert HashChain.find_chain_break([]) is None
        assert HashChain.compute_merkle_root([]) == "0" * 64
