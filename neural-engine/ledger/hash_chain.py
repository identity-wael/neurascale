"""Hash chain implementation for Neural Ledger integrity."""

import hashlib
import json
from typing import List, Optional
import logging

from .event_schema import NeuralLedgerEvent

logger = logging.getLogger(__name__)


class HashChain:
    """Implements cryptographic hash chain for event integrity.

    The hash chain ensures that events cannot be tampered with
    by creating a linked chain where each event's hash includes
    the previous event's hash.
    """

    @staticmethod
    def compute_event_hash(event: NeuralLedgerEvent, previous_hash: str) -> str:
        """Compute SHA-256 hash for event integrity.

        Args:
            event: The event to hash
            previous_hash: Hash of the previous event in the chain

        Returns:
            SHA-256 hash as hex string
        """
        # Create deterministic JSON representation
        event_data = {
            "event_id": event.event_id,
            "timestamp": event.timestamp.isoformat(),
            "event_type": event.event_type.value,
            "session_id": event.session_id,
            "device_id": event.device_id,
            "user_id": event.user_id,
            "data_hash": event.data_hash,
            "metadata": event.metadata,
            "previous_hash": previous_hash,
        }

        # Remove None values for consistent hashing
        event_data = {k: v for k, v in event_data.items() if v is not None}

        # Sort keys for deterministic hashing
        canonical_json = json.dumps(event_data, sort_keys=True)

        # Compute SHA-256 hash
        return hashlib.sha256(canonical_json.encode()).hexdigest()

    @staticmethod
    def compute_data_hash(data: bytes) -> str:
        """Compute SHA-256 hash of raw data.

        Args:
            data: Raw data bytes

        Returns:
            SHA-256 hash as hex string
        """
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def verify_event(event: NeuralLedgerEvent, previous_hash: str) -> bool:
        """Verify a single event's hash.

        Args:
            event: Event to verify
            previous_hash: Expected previous hash

        Returns:
            True if event hash is valid
        """
        expected_hash = HashChain.compute_event_hash(event, previous_hash)
        return event.event_hash == expected_hash

    @staticmethod
    def verify_chain(events: List[NeuralLedgerEvent]) -> bool:
        """Verify integrity of event chain.

        Args:
            events: List of events in chronological order

        Returns:
            True if entire chain is valid
        """
        if not events:
            return True

        # Genesis block has all-zero previous hash
        previous_hash = "0" * 64

        for i, event in enumerate(events):
            # Verify event's previous_hash matches
            if event.previous_hash != previous_hash:
                logger.error(
                    f"Chain broken at event {i}: "
                    f"expected previous_hash={previous_hash}, "
                    f"got={event.previous_hash}"
                )
                return False

            # Verify event's hash
            expected_hash = HashChain.compute_event_hash(event, previous_hash)
            if event.event_hash != expected_hash:
                logger.error(
                    f"Invalid hash at event {i}: "
                    f"expected={expected_hash}, "
                    f"got={event.event_hash}"
                )
                return False

            previous_hash = event.event_hash

        return True

    @staticmethod
    def find_chain_break(events: List[NeuralLedgerEvent]) -> Optional[int]:
        """Find the index where the chain breaks.

        Args:
            events: List of events in chronological order

        Returns:
            Index of first invalid event, or None if chain is valid
        """
        if not events:
            return None

        previous_hash = "0" * 64

        for i, event in enumerate(events):
            # Check previous hash
            if event.previous_hash != previous_hash:
                return i

            # Check event hash
            expected_hash = HashChain.compute_event_hash(event, previous_hash)
            if event.event_hash != expected_hash:
                return i

            previous_hash = event.event_hash

        return None

    @staticmethod
    def repair_chain(events: List[NeuralLedgerEvent]) -> List[NeuralLedgerEvent]:
        """Attempt to repair a broken chain by recomputing hashes.

        This should only be used in development / testing. In production,
        a broken chain indicates tampering and should be investigated.

        Args:
            events: List of events in chronological order

        Returns:
            List of events with corrected hashes
        """
        if not events:
            return events

        previous_hash = "0" * 64
        repaired_events = []

        for event in events:
            # Create a copy to avoid modifying original
            repaired_event = NeuralLedgerEvent.from_dict(event.to_dict())

            # Fix the chain
            repaired_event.previous_hash = previous_hash
            repaired_event.event_hash = HashChain.compute_event_hash(
                repaired_event, previous_hash
            )

            repaired_events.append(repaired_event)
            previous_hash = repaired_event.event_hash

        return repaired_events

    @staticmethod
    def compute_merkle_root(events: List[NeuralLedgerEvent]) -> str:
        """Compute Merkle tree root for a batch of events.

        This can be used for efficient verification of large event sets.

        Args:
            events: List of events

        Returns:
            Merkle root hash as hex string
        """
        if not events:
            return "0" * 64

        # Start with event hashes
        hashes = [event.event_hash for event in events]

        # Build Merkle tree
        while len(hashes) > 1:
            # Ensure even number of hashes
            if len(hashes) % 2 == 1:
                hashes.append(hashes[-1])

            # Compute next level
            next_level = []
            for i in range(0, len(hashes), 2):
                combined = hashes[i] + hashes[i + 1]
                next_hash = hashlib.sha256(combined.encode()).hexdigest()
                next_level.append(next_hash)

            hashes = next_level

        return hashes[0]
