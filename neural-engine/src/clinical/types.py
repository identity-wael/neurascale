"""Clinical workflow data types and models."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import uuid4


class SessionType(Enum):
    """Types of clinical BCI sessions."""

    ASSESSMENT = "assessment"
    TREATMENT = "treatment"
    FOLLOW_UP = "follow_up"
    EMERGENCY = "emergency"
    RESEARCH = "research"


class SessionStatus(Enum):
    """Clinical session status."""

    SCHEDULED = "scheduled"
    PREPARING = "preparing"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"


class SafetyLevel(Enum):
    """Safety alert levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ConsentStatus(Enum):
    """Patient consent status."""

    PENDING = "pending"
    APPROVED = "approved"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"


@dataclass
class PatientDemographics:
    """Patient demographic information."""

    first_name: str
    last_name: str
    date_of_birth: datetime
    gender: str
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    emergency_contact: Optional[Dict[str, str]] = None
    preferred_language: str = "en"


@dataclass
class MedicalHistory:
    """Patient medical history record."""

    conditions: List[str] = field(default_factory=list)
    medications: List[Dict[str, Any]] = field(default_factory=list)
    allergies: List[str] = field(default_factory=list)
    contraindications: List[str] = field(default_factory=list)
    previous_bci_experience: bool = False
    neurological_conditions: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ConsentRecord:
    """Patient consent record."""

    consent_id: str = field(default_factory=lambda: str(uuid4()))
    patient_id: str = ""
    consent_type: str = ""
    status: ConsentStatus = ConsentStatus.PENDING
    granted_date: Optional[datetime] = None
    withdrawn_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    consent_text: str = ""
    signed_by: str = ""
    witness: Optional[str] = None


@dataclass
class PrivacySettings:
    """Patient privacy preferences."""

    data_sharing_consent: bool = False
    research_participation: bool = False
    family_access_allowed: bool = False
    marketing_communications: bool = False
    data_retention_preference: str = "minimum"  # minimum, standard, extended
    anonymization_level: str = "full"  # none, partial, full


@dataclass
class TreatmentPlan:
    """Patient treatment plan."""

    plan_id: str = field(default_factory=lambda: str(uuid4()))
    patient_id: str = ""
    created_by: str = ""
    created_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    treatment_goals: List[str] = field(default_factory=list)
    protocols: List[str] = field(default_factory=list)
    session_frequency: str = "weekly"  # daily, weekly, biweekly, monthly
    duration_weeks: int = 12
    progress_milestones: List[Dict[str, Any]] = field(default_factory=list)
    notes: str = ""
    status: str = "active"  # active, paused, completed, cancelled


@dataclass
class Patient:
    """Clinical patient record."""

    patient_id: str = field(default_factory=lambda: str(uuid4()))
    medical_record_number: str = ""
    demographics: Optional[PatientDemographics] = None
    medical_history: Optional[MedicalHistory] = None
    consent_status: Optional[ConsentRecord] = None
    privacy_preferences: Optional[PrivacySettings] = None
    treatment_plan: Optional[TreatmentPlan] = None
    active_sessions: List[str] = field(default_factory=list)
    care_team: List[str] = field(default_factory=list)
    created_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class DeviceConfig:
    """Clinical session device configuration."""

    device_type: str
    device_id: str
    sampling_rate: float
    channels: List[str]
    calibration_settings: Dict[str, Any] = field(default_factory=dict)
    safety_thresholds: Dict[str, float] = field(default_factory=dict)


@dataclass
class ClinicalNote:
    """Clinical session note."""

    note_id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    provider_id: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    note_type: str = "general"  # general, assessment, adverse_event, safety
    content: str = ""
    assessment_scores: Dict[str, float] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)


@dataclass
class SafetyEvent:
    """Clinical safety event record."""

    event_id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_type: str = ""
    severity: SafetyLevel = SafetyLevel.LOW
    description: str = ""
    response_taken: str = ""
    resolved: bool = False
    reported_by: str = ""


@dataclass
class OutcomeMeasure:
    """Clinical outcome measurement."""

    measure_id: str = field(default_factory=lambda: str(uuid4()))
    session_id: str = ""
    measure_type: str = ""
    value: float = 0.0
    unit: str = ""
    reference_range: Optional[str] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    notes: str = ""


@dataclass
class ClinicalSession:
    """BCI clinical session record."""

    session_id: str = field(default_factory=lambda: str(uuid4()))
    patient_id: str = ""
    provider_id: str = ""
    session_type: SessionType = SessionType.TREATMENT
    protocol_id: str = ""
    scheduled_start: Optional[datetime] = None
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    duration_minutes: int = 60
    device_configuration: Optional[DeviceConfig] = None
    clinical_notes: List[ClinicalNote] = field(default_factory=list)
    safety_events: List[SafetyEvent] = field(default_factory=list)
    outcomes: List[OutcomeMeasure] = field(default_factory=list)
    status: SessionStatus = SessionStatus.SCHEDULED
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClinicalProtocol:
    """Clinical treatment protocol."""

    protocol_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    description: str = ""
    version: str = "1.0"
    protocol_type: str = ""
    target_conditions: List[str] = field(default_factory=list)
    session_parameters: Dict[str, Any] = field(default_factory=dict)
    safety_requirements: Dict[str, Any] = field(default_factory=dict)
    outcome_measures: List[str] = field(default_factory=list)
    evidence_level: str = "experimental"  # experimental, clinical_trial, approved
    created_by: str = ""
    created_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ClinicalConfig:
    """Clinical workflow configuration."""

    # Database settings
    database_url: str = ""

    # Security settings
    encryption_key: str = ""
    hipaa_compliance_mode: bool = True
    audit_logging: bool = True

    # Integration settings
    emr_integration_enabled: bool = False
    fhir_server_url: Optional[str] = None

    # Safety settings
    safety_monitoring_enabled: bool = True
    emergency_contact_required: bool = True

    # Session settings
    default_session_duration: int = 60
    max_concurrent_sessions: int = 5

    # Compliance settings
    data_retention_days: int = 2555  # 7 years
    consent_expiry_days: int = 365
    audit_retention_days: int = 2555
