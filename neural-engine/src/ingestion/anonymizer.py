"""Data anonymization for HIPAA compliance."""

import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
import uuid
import logging
from dataclasses import replace

from .data_types import NeuralDataPacket, DeviceInfo


logger = logging.getLogger(__name__)


class DataAnonymizer:
    """
    Anonymizes neural data packets for HIPAA compliance.

    Implements:
    - Subject ID anonymization with consistent mapping
    - Timestamp fuzzing for additional privacy
    - Removal of potentially identifying metadata
    - Audit logging for compliance
    """

    def __init__(self, secret_key: Optional[str] = None):
        """
        Initialize the anonymizer.

        Args:
            secret_key: Secret key for HMAC-based ID generation.
                       If None, generates a random key (not recommended for production)
        """
        if secret_key is None:
            logger.warning(
                "Using random secret key - IDs won't be consistent across sessions"
            )
            self.secret_key = str(uuid.uuid4()).encode()
        else:
            self.secret_key = secret_key.encode()

        # Cache for subject ID mappings (in production, use persistent storage)
        self._subject_id_cache: Dict[str, str] = {}

        # Audit log (in production, use proper audit logging service)
        self._audit_log = []

    def anonymize_packet(self, packet: NeuralDataPacket) -> NeuralDataPacket:
        """
        Anonymize a neural data packet.

        Args:
            packet: Original packet with potential PII

        Returns:
            Anonymized packet safe for storage/transmission
        """
        # Create a copy to avoid modifying original
        anonymized = replace(packet)

        # Anonymize subject ID
        if packet.subject_id:
            anonymized.subject_id = self._anonymize_subject_id(packet.subject_id)

        # Anonymize device info
        anonymized.device_info = self._anonymize_device_info(packet.device_info)

        # Fuzz timestamp for additional privacy
        anonymized.timestamp = self._fuzz_timestamp(packet.timestamp)

        # Remove or sanitize metadata
        if packet.metadata:
            anonymized.metadata = self._sanitize_metadata(packet.metadata)

        # Log anonymization event
        self._log_anonymization(packet, anonymized)

        return anonymized

    def _anonymize_subject_id(self, original_id: str) -> str:
        """
        Generate consistent anonymized subject ID.

        Uses HMAC to ensure:
        - Same input always produces same output
        - Cannot reverse to get original ID
        - Different secret keys produce different mappings
        """
        # Check cache first
        if original_id in self._subject_id_cache:
            return self._subject_id_cache[original_id]

        # Generate anonymized ID using HMAC
        h = hmac.new(self.secret_key, original_id.encode(), hashlib.sha256)

        # Take first 16 characters of hex digest for readable ID
        anon_id = f"ANON_{h.hexdigest()[:16].upper()}"

        # Cache the mapping
        self._subject_id_cache[original_id] = anon_id

        return anon_id

    def _anonymize_device_info(self, device_info: DeviceInfo) -> DeviceInfo:
        """Anonymize device information."""
        if not device_info:
            return device_info

        # Create anonymized copy
        anon_info = replace(device_info)

        # Remove potentially identifying information
        anon_info.serial_number = None  # Remove serial numbers

        # Anonymize device ID if it contains identifying info
        if device_info.device_id and len(device_info.device_id) > 8:
            # Keep device type prefix but anonymize the rest
            prefix = device_info.device_id[:4]
            h = hashlib.sha256(device_info.device_id.encode()).hexdigest()[:8]
            anon_info.device_id = f"{prefix}_{h}"

        # Remove hardware IDs from channels
        if anon_info.channels:
            for channel in anon_info.channels:
                channel.hardware_id = None

        return anon_info

    def _fuzz_timestamp(self, timestamp: datetime) -> datetime:
        """
        Add small random offset to timestamp for privacy.

        Adds up to ±5 seconds to prevent exact time correlation
        while maintaining relative timing for analysis.
        """
        # Use hash of timestamp for consistent fuzzing
        hash_val = int(hashlib.md5(str(timestamp).encode()).hexdigest()[:8], 16)

        # Generate offset between -5 and +5 seconds
        offset_seconds = (hash_val % 11) - 5

        return timestamp + timedelta(seconds=offset_seconds)

    def _sanitize_metadata(self, metadata: Dict) -> Dict:
        """Remove or sanitize potentially identifying metadata fields."""
        if not metadata:
            return metadata

        # Create sanitized copy
        sanitized = metadata.copy()

        # Remove PII fields
        self._remove_pii_fields(sanitized)

        # Sanitize nested dictionaries
        for key, value in list(sanitized.items()):
            if isinstance(value, dict):
                sanitized[key] = self._sanitize_metadata(value)

        # Convert age to age range if present
        self._convert_age_to_range(metadata, sanitized)

        return sanitized

    def _remove_pii_fields(self, data: Dict) -> None:
        """Remove PII fields from dictionary."""
        pii_fields = [
            "name",
            "patient_name",
            "subject_name",
            "email",
            "phone",
            "address",
            "location",
            "ip_address",
            "mac_address",
            "birth_date",
            "dob",
            "age",  # Keep general age ranges only
            "ssn",
            "mrn",
            "patient_id",  # Medical record numbers
        ]

        for field in pii_fields:
            data.pop(field, None)
            data.pop(field.upper(), None)
            data.pop(field.lower(), None)

    def _convert_age_to_range(self, original: Dict, sanitized: Dict) -> None:
        """Convert age to age range."""
        if "age" in original:
            age = original["age"]
            if isinstance(age, (int, float)):
                # Convert to age range
                if age < 18:
                    sanitized["age_range"] = "under_18"
                elif age < 30:
                    sanitized["age_range"] = "18-29"
                elif age < 50:
                    sanitized["age_range"] = "30-49"
                elif age < 70:
                    sanitized["age_range"] = "50-69"
                else:
                    sanitized["age_range"] = "70+"

    def _log_anonymization(
        self,
        original: NeuralDataPacket,
        anonymized: NeuralDataPacket,
    ):
        """Log anonymization event for audit trail."""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": original.session_id,
            "original_subject_id": bool(original.subject_id),
            "anonymized_subject_id": bool(anonymized.subject_id),
            "metadata_sanitized": original.metadata != anonymized.metadata,
            "timestamp_fuzzed": original.timestamp != anonymized.timestamp,
        }

        self._audit_log.append(log_entry)

        # In production, write to secure audit log service
        logger.debug(f"Anonymization logged: {log_entry}")

    def get_audit_log(self) -> list:
        """Get anonymization audit log."""
        return self._audit_log.copy()

    def export_mappings(self) -> Dict[str, str]:
        """
        Export subject ID mappings for authorized personnel.

        Returns:
            Dictionary of original -> anonymized ID mappings

        Note: This should only be accessible to authorized personnel
        with proper access controls in production.
        """
        return self._subject_id_cache.copy()
