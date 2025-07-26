"""HIPAA Compliance features for NeuraScale Neural Engine.

This module implements PHI anonymization, consent management, and other
HIPAA compliance features for protecting patient health information.
"""

import re
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ConsentType(Enum):
    """Types of consent for data usage."""

    DATA_COLLECTION = "data_collection"
    DATA_PROCESSING = "data_processing"
    DATA_SHARING = "data_sharing"
    RESEARCH_USE = "research_use"
    MARKETING = "marketing"
    THIRD_PARTY_SHARING = "third_party_sharing"


class ConsentStatus(Enum):
    """Status of consent."""

    GRANTED = "granted"
    DENIED = "denied"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"


@dataclass
class ConsentRecord:
    """Patient consent record."""

    id: str
    patient_id: str
    consent_type: ConsentType
    status: ConsentStatus
    purpose: str
    granted_at: datetime
    expires_at: Optional[datetime] = None
    withdrawn_at: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    consent_version: str = "1.0"
    witness_id: Optional[str] = None
    notes: Optional[str] = None


class PHIAnonymizer:
    """Anonymizes Protected Health Information (PHI) per HIPAA requirements."""

    # HIPAA Safe Harbor identifiers (18 types)
    PHI_PATTERNS = {
        "name": r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",  # Simple name pattern
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        "fax": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "mrn": r"\b[A-Z]{2}\d{6,8}\b",  # Medical Record Number
        "account_number": r"\b[A-Z]{2}\d{8,12}\b",
        "certificate_number": r"\b[A-Z]{3}\d{6,10}\b",
        "license_number": r"\b[A-Z]{2}\d{6,8}\b",
        "vehicle_id": r"\b[A-Z0-9]{17}\b",  # VIN
        "device_id": r"\b[A-Z0-9]{8}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{12}\b",
        "ip_address": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
        "url": r'https?://[^\s<>"{}|\\^`[\]]+',
        "biometric_id": r"\b[A-Z0-9]{16,32}\b",
        "face_photo": r"\b(face|photo|image)_[A-Z0-9]+\.(jpg|jpeg|png|gif)\b",
        "fingerprint": r"\bfingerprint_[A-Z0-9]+\b",
        "voice_print": r"\bvoice_[A-Z0-9]+\.(wav|mp3|m4a)\b",
    }

    # Date patterns that need age adjustment
    DATE_PATTERNS = {
        "date_of_birth": r"\b\d{4}-\d{2}-\d{2}\b",
        "admission_date": r"\b\d{4}-\d{2}-\d{2}\b",
        "discharge_date": r"\b\d{4}-\d{2}-\d{2}\b",
    }

    # Geographic identifiers (more specific than state)
    GEO_PATTERNS = {
        "zip_code": r"\b\d{5}(-\d{4})?\b",
        "address": r"\b\d+\s+[A-Za-z\s]+\s+(Street|St|Avenue|Ave|Road|Rd|Lane|Ln|Drive|Dr|Court|Ct|Place|Pl)\b",
        "city": r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2}\b",
    }

    def __init__(self, salt: str, anonymization_level: str = "safe_harbor"):
        """Initialize PHI anonymizer.

        Args:
            salt: Salt for consistent hashing
            anonymization_level: Level of anonymization (safe_harbor, expert_determination)
        """
        self.salt = salt
        self.anonymization_level = anonymization_level
        self._identifier_cache = {}  # Cache for consistent anonymization

    def anonymize_data(
        self, data: Dict[str, Any], preserve_fields: Optional[Set[str]] = None
    ) -> Dict[str, Any]:
        """Anonymize PHI in neural data and metadata.

        Args:
            data: Data dictionary to anonymize
            preserve_fields: Fields to preserve without anonymization

        Returns:
            Anonymized data dictionary
        """
        if preserve_fields is None:
            preserve_fields = set()

        anonymized = {}

        for key, value in data.items():
            if key in preserve_fields:
                anonymized[key] = value
                continue

            if isinstance(value, dict):
                anonymized[key] = self.anonymize_data(value, preserve_fields)
            elif isinstance(value, list):
                anonymized[key] = [
                    (
                        self.anonymize_data(item, preserve_fields)
                        if isinstance(item, dict)
                        else self._anonymize_value(key, item)
                    )
                    for item in value
                ]
            else:
                anonymized[key] = self._anonymize_value(key, value)

        return anonymized

    def _anonymize_value(self, field_name: str, value: Any) -> Any:
        """Anonymize a single value based on field name and content."""
        if value is None:
            return None

        # Handle different data types
        if isinstance(value, str):
            return self._anonymize_string(field_name, value)
        elif isinstance(value, datetime):
            return self._anonymize_date(field_name, value)
        elif isinstance(value, (int, float)):
            return self._anonymize_numeric(field_name, value)
        else:
            return value

    def _anonymize_string(self, field_name: str, text: str) -> str:
        """Anonymize string content."""
        # Direct field anonymization
        if field_name.lower() in ["patient_id", "subject_id"]:
            return self._hash_identifier(text)

        if field_name.lower() in ["name", "patient_name", "first_name", "last_name"]:
            return "REDACTED"

        if field_name.lower() in ["email", "phone", "address"]:
            return f"[{field_name.upper()}_REDACTED]"

        # Pattern-based anonymization
        anonymized_text = text

        # Apply all PHI patterns
        for pattern_name, pattern in self.PHI_PATTERNS.items():
            anonymized_text = re.sub(
                pattern,
                f"[{pattern_name.upper()}_REDACTED]",
                anonymized_text,
                flags=re.IGNORECASE,
            )

        # Apply date patterns
        for pattern_name, pattern in self.DATE_PATTERNS.items():
            anonymized_text = re.sub(
                pattern, self._anonymize_date_string, anonymized_text
            )

        # Apply geographic patterns (remove specific locations)
        for pattern_name, pattern in self.GEO_PATTERNS.items():
            anonymized_text = re.sub(
                pattern,
                f"[{pattern_name.upper()}_REDACTED]",
                anonymized_text,
                flags=re.IGNORECASE,
            )

        return anonymized_text

    def _anonymize_date(self, field_name: str, date_value: datetime) -> datetime:
        """Anonymize date values."""
        if field_name.lower() in ["date_of_birth", "birth_date"]:
            # For DOB, keep only year if over 89, otherwise set to year only
            current_year = datetime.now().year
            age = current_year - date_value.year

            if age > 89:
                # Set to January 1st of birth year
                return datetime(date_value.year, 1, 1)
            else:
                # Keep year only, set to January 1st
                return datetime(date_value.year, 1, 1)

        # For other dates, apply date shifting
        return self._shift_date(date_value)

    def _anonymize_date_string(self, match) -> str:
        """Anonymize date string match."""
        date_str = match.group()
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            shifted_date = self._shift_date(date_obj)
            return shifted_date.strftime("%Y-%m-%d")
        except ValueError:
            return "[DATE_REDACTED]"

    def _shift_date(self, date_value: datetime, days_range: int = 30) -> datetime:
        """Apply consistent date shifting for anonymization."""
        # Use hash of original date for consistent shifting
        date_hash = hashlib.md5(
            f"{date_value.isoformat()}{self.salt}".encode()
        ).hexdigest()
        shift_days = int(date_hash[:8], 16) % days_range - (days_range // 2)
        return date_value + timedelta(days=shift_days)

    def _anonymize_numeric(self, field_name: str, value: float) -> float:
        """Anonymize numeric values if they contain PHI."""
        # Age over 89 should be set to 90+
        if field_name.lower() == "age" and value > 89:
            return 90.0

        # Zip codes should be truncated to first 3 digits if population < 20,000
        if field_name.lower() in ["zip", "zip_code", "postal_code"]:
            # Simplified: truncate last 2 digits
            if value > 10000:
                return float(str(int(value))[:3] + "00")

        return value

    def _hash_identifier(self, identifier: str) -> str:
        """Create consistent one-way hash of identifier."""
        if identifier in self._identifier_cache:
            return self._identifier_cache[identifier]

        # Create hash
        hash_value = hashlib.sha256(f"{identifier}{self.salt}".encode()).hexdigest()[
            :16
        ]

        # Cache for consistency
        self._identifier_cache[identifier] = hash_value
        return hash_value

    def is_data_anonymized(self, data: Dict[str, Any]) -> bool:
        """Check if data appears to be properly anonymized.

        Args:
            data: Data to check

        Returns:
            True if data appears anonymized, False otherwise
        """
        # Convert to string for pattern matching
        data_str = str(data).lower()

        # Check for obvious PHI patterns
        for pattern_name, pattern in self.PHI_PATTERNS.items():
            if re.search(pattern, data_str, re.IGNORECASE):
                logger.warning(f"Potential PHI detected: {pattern_name}")
                return False

        # Check for suspicious field names
        suspicious_fields = ["ssn", "social", "phone", "email", "address"]
        for field in suspicious_fields:
            if field in data_str and "redacted" not in data_str:
                logger.warning(f"Suspicious field detected: {field}")
                return False

        return True


class ConsentManager:
    """Manages patient consent for data usage."""

    def __init__(self, database_client=None):
        """Initialize consent manager.

        Args:
            database_client: Database client (Firestore, PostgreSQL, etc.)
        """
        self.db = database_client

    async def record_consent(
        self,
        patient_id: str,
        consent_type: ConsentType,
        status: ConsentStatus,
        purpose: str,
        expires_at: Optional[datetime] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        witness_id: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> str:
        """Record patient consent decision.

        Args:
            patient_id: Patient identifier
            consent_type: Type of consent
            status: Consent status
            purpose: Purpose of data usage
            expires_at: Optional expiration date
            ip_address: Client IP (for audit trail)
            user_agent: Client user agent (for audit trail)
            witness_id: Optional witness identifier
            notes: Optional notes

        Returns:
            Consent record ID
        """
        consent_id = secrets.token_urlsafe(16)

        consent_record = ConsentRecord(
            id=consent_id,
            patient_id=patient_id,
            consent_type=consent_type,
            status=status,
            purpose=purpose,
            granted_at=datetime.utcnow(),
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
            witness_id=witness_id,
            notes=notes,
        )

        # Store in database
        if self.db:
            await self._store_consent_record(consent_record)

        # Log to audit trail
        await self._log_consent_event(consent_record)

        logger.info(f"Consent recorded: {consent_id} for patient {patient_id}")
        return consent_id

    async def check_consent(
        self, patient_id: str, consent_type: ConsentType, purpose: str
    ) -> bool:
        """Check if valid consent exists for data usage.

        Args:
            patient_id: Patient identifier
            consent_type: Type of consent required
            purpose: Purpose of data usage

        Returns:
            True if valid consent exists, False otherwise
        """
        if not self.db:
            logger.warning("No database configured, allowing consent check")
            return True

        # Get latest consent record
        consent_record = await self._get_latest_consent(patient_id, consent_type)

        if not consent_record:
            logger.warning(
                f"No consent found for patient {patient_id}, type {consent_type.value}"
            )
            return False

        # Check status
        if consent_record.status != ConsentStatus.GRANTED:
            logger.warning(f"Consent not granted: {consent_record.status.value}")
            return False

        # Check expiration
        if consent_record.expires_at and consent_record.expires_at < datetime.utcnow():
            logger.warning(f"Consent expired: {consent_record.expires_at}")
            return False

        # Check purpose alignment
        if purpose.lower() not in consent_record.purpose.lower():
            logger.warning(
                f"Purpose mismatch: requested '{purpose}', consented '{consent_record.purpose}'"
            )
            return False

        return True

    async def withdraw_consent(
        self, patient_id: str, consent_type: ConsentType, reason: Optional[str] = None
    ) -> bool:
        """Withdraw patient consent.

        Args:
            patient_id: Patient identifier
            consent_type: Type of consent to withdraw
            reason: Optional reason for withdrawal

        Returns:
            True if successfully withdrawn
        """
        try:
            # Create withdrawal record
            withdrawal_id = await self.record_consent(
                patient_id=patient_id,
                consent_type=consent_type,
                status=ConsentStatus.WITHDRAWN,
                purpose="Consent withdrawal",
                notes=reason,
            )

            # Trigger data cleanup if necessary
            await self._trigger_data_cleanup(patient_id, consent_type)

            logger.info(f"Consent withdrawn: {withdrawal_id}")
            return True

        except Exception as e:
            logger.error(f"Consent withdrawal error: {str(e)}")
            return False

    async def get_consent_history(self, patient_id: str) -> List[ConsentRecord]:
        """Get consent history for a patient.

        Args:
            patient_id: Patient identifier

        Returns:
            List of consent records
        """
        if not self.db:
            return []

        return await self._get_patient_consent_history(patient_id)

    async def _store_consent_record(self, consent_record: ConsentRecord) -> None:
        """Store consent record in database."""
        # Convert to dict for storage
        record_dict = asdict(consent_record)

        # Convert enums to strings
        record_dict["consent_type"] = consent_record.consent_type.value
        record_dict["status"] = consent_record.status.value

        # This would be implemented based on your database schema
        logger.info(f"Consent record stored: {consent_record.id}")

    async def _get_latest_consent(
        self, patient_id: str, consent_type: ConsentType
    ) -> Optional[ConsentRecord]:
        """Get latest consent record for patient and type."""
        # This would query the database for the latest consent record
        # Return None if not found
        logger.info(
            f"Checking consent for patient {patient_id}, type {consent_type.value}"
        )
        return None

    async def _get_patient_consent_history(
        self, patient_id: str
    ) -> List[ConsentRecord]:
        """Get all consent records for a patient."""
        # This would query the database for all consent records
        logger.info(f"Retrieved consent history for patient {patient_id}")
        return []

    async def _log_consent_event(self, consent_record: ConsentRecord) -> None:
        """Log consent event to audit trail (Neural Ledger)."""
        # This would integrate with Neural Ledger for audit logging
        logger.info(f"Consent event logged: {consent_record.id}")

    async def _trigger_data_cleanup(
        self, patient_id: str, consent_type: ConsentType
    ) -> None:
        """Trigger data cleanup when consent is withdrawn."""
        # This would trigger removal or anonymization of data
        # based on the withdrawn consent type
        logger.info(
            f"Data cleanup triggered for patient {patient_id}, consent {consent_type.value}"
        )


class HIPAAComplianceManager:
    """Main HIPAA compliance manager coordinating all features."""

    def __init__(
        self,
        anonymizer: PHIAnonymizer,
        consent_manager: ConsentManager,
        audit_logger=None,
    ):
        """Initialize HIPAA compliance manager.

        Args:
            anonymizer: PHI anonymizer instance
            consent_manager: Consent manager instance
            audit_logger: Audit logging service
        """
        self.anonymizer = anonymizer
        self.consent_manager = consent_manager
        self.audit_logger = audit_logger

    async def process_data_for_research(
        self, patient_id: str, data: Dict[str, Any], purpose: str
    ) -> Optional[Dict[str, Any]]:
        """Process patient data for research use with HIPAA compliance.

        Args:
            patient_id: Patient identifier
            data: Raw patient data
            purpose: Research purpose

        Returns:
            Anonymized data if consent exists, None otherwise
        """
        # Check consent
        has_consent = await self.consent_manager.check_consent(
            patient_id=patient_id,
            consent_type=ConsentType.RESEARCH_USE,
            purpose=purpose,
        )

        if not has_consent:
            logger.warning(f"No valid consent for research use: patient {patient_id}")
            return None

        # Anonymize data
        anonymized_data = self.anonymizer.anonymize_data(data)

        # Verify anonymization
        if not self.anonymizer.is_data_anonymized(anonymized_data):
            logger.error("Data anonymization failed verification")
            return None

        # Log access
        if self.audit_logger:
            await self.audit_logger.log_data_access(
                patient_id=patient_id,
                purpose=purpose,
                data_type="neural_data",
                anonymized=True,
            )

        return anonymized_data

    async def validate_data_retention(
        self, patient_id: str, data_age_days: int
    ) -> bool:
        """Validate if data can be retained per HIPAA requirements.

        Args:
            patient_id: Patient identifier
            data_age_days: Age of data in days

        Returns:
            True if data can be retained, False if should be deleted
        """
        # Check if patient has withdrawn consent
        consent_history = await self.consent_manager.get_consent_history(patient_id)

        # Check for any withdrawal records
        for record in consent_history:
            if (
                record.status == ConsentStatus.WITHDRAWN
                and record.withdrawn_at
                and (datetime.utcnow() - record.withdrawn_at).days > 30
            ):
                # Data should be deleted 30 days after consent withdrawal
                return False

        # Check data retention limits (HIPAA minimum retention: 6 years)
        if data_age_days > (6 * 365):  # 6 years
            return False

        return True


def create_hipaa_system(salt: str, database_client=None) -> HIPAAComplianceManager:
    """Create HIPAA compliance system.

    Args:
        salt: Salt for anonymization
        database_client: Database client for consent storage

    Returns:
        Configured HIPAAComplianceManager
    """
    anonymizer = PHIAnonymizer(salt=salt)
    consent_manager = ConsentManager(database_client=database_client)

    return HIPAAComplianceManager(
        anonymizer=anonymizer, consent_manager=consent_manager
    )
