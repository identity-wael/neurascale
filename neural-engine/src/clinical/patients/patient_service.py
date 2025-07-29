"""Patient lifecycle management and orchestration service."""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Any
from uuid import uuid4

from ..types import (
    Patient,
    PatientDemographics,
    MedicalHistory,
    PrivacySettings,
    ClinicalConfig,
)
from .onboarding import PatientOnboarding
from .medical_history import MedicalHistoryManager
from .consent_management import ConsentManager
from .privacy_controls import PrivacyControls

logger = logging.getLogger(__name__)


class PatientService:
    """Comprehensive patient lifecycle management service.

    Orchestrates patient registration, onboarding, consent management,
    and ongoing clinical care coordination.
    """

    def __init__(self, config: ClinicalConfig):
        """Initialize patient service with clinical configuration."""
        self.config = config

        # Initialize sub-services
        self.onboarding = PatientOnboarding(config)
        self.medical_history = MedicalHistoryManager(config)
        self.consent_manager = ConsentManager(config)
        self.privacy_controls = PrivacyControls(config)

        # In-memory storage (would be replaced with database in production)
        self._patients: Dict[str, Patient] = {}

        logger.info("Patient service initialized")

    async def register_patient(self, registration_data: dict) -> Patient:
        """Register a new patient and initiate onboarding workflow.

        Args:
            registration_data: Patient registration information

        Returns:
            Created Patient record

        Raises:
            ValueError: If registration data is invalid
        """
        try:
            # Validate required fields
            required_fields = ["first_name", "last_name", "date_of_birth"]
            for field in required_fields:
                if field not in registration_data:
                    raise ValueError(f"Missing required field: {field}")

            # Generate unique patient ID and MRN
            patient_id = str(uuid4())
            mrn = self._generate_medical_record_number()

            # Create demographics
            demographics = PatientDemographics(
                first_name=registration_data["first_name"],
                last_name=registration_data["last_name"],
                date_of_birth=datetime.fromisoformat(
                    registration_data["date_of_birth"]
                ),
                gender=registration_data.get("gender", ""),
                contact_phone=registration_data.get("contact_phone"),
                contact_email=registration_data.get("contact_email"),
                emergency_contact=registration_data.get("emergency_contact"),
                preferred_language=registration_data.get("preferred_language", "en"),
            )

            # Initialize medical history
            medical_history = MedicalHistory(
                conditions=registration_data.get("conditions", []),
                medications=registration_data.get("medications", []),
                allergies=registration_data.get("allergies", []),
                contraindications=registration_data.get("contraindications", []),
                previous_bci_experience=registration_data.get(
                    "previous_bci_experience", False
                ),
                neurological_conditions=registration_data.get(
                    "neurological_conditions", []
                ),
            )

            # Initialize privacy settings with defaults
            privacy_settings = PrivacySettings(
                data_sharing_consent=registration_data.get(
                    "data_sharing_consent", False
                ),
                research_participation=registration_data.get(
                    "research_participation", False
                ),
                family_access_allowed=registration_data.get(
                    "family_access_allowed", False
                ),
                marketing_communications=registration_data.get(
                    "marketing_communications", False
                ),
            )

            # Create patient record
            patient = Patient(
                patient_id=patient_id,
                medical_record_number=mrn,
                demographics=demographics,
                medical_history=medical_history,
                privacy_preferences=privacy_settings,
                care_team=registration_data.get("care_team", []),
            )

            # Store patient
            self._patients[patient_id] = patient

            # Initiate onboarding workflow
            await self.onboarding.create_registration_workflow(
                patient, registration_data
            )

            logger.info(f"Patient registered: {patient_id} (MRN: {mrn})")

            # Log HIPAA audit trail
            await self._log_patient_access(
                user_id="system",
                patient_id=patient_id,
                action="register_patient",
                details={"mrn": mrn},
            )

            return patient

        except Exception as e:
            logger.error(f"Patient registration failed: {e}")
            raise

    async def update_patient_profile(self, patient_id: str, updates: dict) -> Patient:
        """Update patient profile information.

        Args:
            patient_id: Patient identifier
            updates: Dictionary of fields to update

        Returns:
            Updated Patient record

        Raises:
            ValueError: If patient not found or updates invalid
        """
        if patient_id not in self._patients:
            raise ValueError(f"Patient not found: {patient_id}")

        patient = self._patients[patient_id]

        try:
            # Update different sections using helper methods
            if "demographics" in updates:
                self._update_demographics(patient, updates["demographics"])

            if "medical_history" in updates:
                self._update_medical_history(patient, updates["medical_history"])

            if "privacy_preferences" in updates:
                self._update_privacy_preferences(
                    patient, updates["privacy_preferences"]
                )

            if "care_team" in updates:
                patient.care_team = updates["care_team"]

            # Update last modified timestamp
            patient.last_updated = datetime.now(timezone.utc)

            logger.info(f"Patient profile updated: {patient_id}")

            # Log HIPAA audit trail
            await self._log_patient_access(
                user_id="system",  # In production, get from context
                patient_id=patient_id,
                action="update_profile",
                details={"updated_fields": list(updates.keys())},
            )

            return patient

        except Exception as e:
            logger.error(f"Patient profile update failed: {e}")
            raise

    async def get_patient_record(
        self, patient_id: str, requesting_user: str = "system"
    ) -> Patient:
        """Retrieve patient record with access logging.

        Args:
            patient_id: Patient identifier
            requesting_user: User requesting access

        Returns:
            Patient record

        Raises:
            ValueError: If patient not found
        """
        if patient_id not in self._patients:
            raise ValueError(f"Patient not found: {patient_id}")

        patient = self._patients[patient_id]

        # Log HIPAA audit trail
        await self._log_patient_access(
            user_id=requesting_user,
            patient_id=patient_id,
            action="view_record",
            details={"access_timestamp": datetime.now(timezone.utc).isoformat()},
        )

        return patient

    async def archive_patient_record(self, patient_id: str, reason: str) -> bool:
        """Archive patient record (soft delete with retention).

        Args:
            patient_id: Patient identifier
            reason: Reason for archiving

        Returns:
            Success status
        """
        if patient_id not in self._patients:
            return False

        patient = self._patients[patient_id]

        # In production, would move to archived table instead of deleting
        # For now, just mark as archived in metadata
        if "archived" not in patient.metadata:
            patient.metadata = patient.metadata or {}

        patient.metadata["archived"] = True
        patient.metadata["archived_date"] = datetime.now(timezone.utc).isoformat()
        patient.metadata["archive_reason"] = reason

        logger.info(f"Patient record archived: {patient_id}, reason: {reason}")

        # Log HIPAA audit trail
        await self._log_patient_access(
            user_id="system",
            patient_id=patient_id,
            action="archive_record",
            details={"reason": reason},
        )

        return True

    async def search_patients(self, search_criteria: dict) -> List[Patient]:
        """Search patients by various criteria.

        Args:
            search_criteria: Search parameters

        Returns:
            List of matching patients
        """
        results = []

        for patient in self._patients.values():
            # Skip archived patients unless explicitly requested
            if patient.metadata.get("archived") and not search_criteria.get(
                "include_archived"
            ):
                continue

            match = True

            # Search by MRN
            if "mrn" in search_criteria:
                if patient.medical_record_number != search_criteria["mrn"]:
                    match = False

            # Search by name
            if "name" in search_criteria and patient.demographics:
                search_name = search_criteria["name"].lower()
                full_name = f"{patient.demographics.first_name} {patient.demographics.last_name}".lower()
                if search_name not in full_name:
                    match = False

            # Search by care team member
            if "provider_id" in search_criteria:
                if search_criteria["provider_id"] not in patient.care_team:
                    match = False

            if match:
                results.append(patient)

        # Log search access
        await self._log_patient_access(
            user_id="system",
            patient_id="*",
            action="search_patients",
            details={"criteria": search_criteria, "results_count": len(results)},
        )

        return results

    async def assign_care_team(self, patient_id: str, provider_ids: List[str]) -> bool:
        """Assign care team members to patient.

        Args:
            patient_id: Patient identifier
            provider_ids: List of provider identifiers

        Returns:
            Success status
        """
        if patient_id not in self._patients:
            return False

        patient = self._patients[patient_id]
        patient.care_team = provider_ids
        patient.last_updated = datetime.now(timezone.utc)

        logger.info(f"Care team assigned to patient {patient_id}: {provider_ids}")

        # Log assignment
        await self._log_patient_access(
            user_id="system",
            patient_id=patient_id,
            action="assign_care_team",
            details={"providers": provider_ids},
        )

        return True

    def _generate_medical_record_number(self) -> str:
        """Generate unique medical record number."""
        # Simple implementation - in production would use hospital's MRN format
        timestamp = datetime.now().strftime("%Y%m%d")
        unique_suffix = str(uuid4())[:8].upper()
        return f"MRN{timestamp}{unique_suffix}"

    def _update_demographics(self, patient: Patient, demo_updates: dict):
        """Update patient demographics."""
        if patient.demographics:
            for field, value in demo_updates.items():
                if hasattr(patient.demographics, field):
                    setattr(patient.demographics, field, value)

    def _update_medical_history(self, patient: Patient, history_updates: dict):
        """Update patient medical history."""
        if patient.medical_history:
            for field, value in history_updates.items():
                if hasattr(patient.medical_history, field):
                    setattr(patient.medical_history, field, value)
            patient.medical_history.last_updated = datetime.now(timezone.utc)

    def _update_privacy_preferences(self, patient: Patient, privacy_updates: dict):
        """Update patient privacy preferences."""
        if patient.privacy_preferences:
            for field, value in privacy_updates.items():
                if hasattr(patient.privacy_preferences, field):
                    setattr(patient.privacy_preferences, field, value)

    async def _log_patient_access(
        self, user_id: str, patient_id: str, action: str, details: dict
    ):
        """Log patient data access for HIPAA compliance.

        Args:
            user_id: User performing the action
            patient_id: Patient being accessed
            action: Type of access/action
            details: Additional context
        """
        # In production, this would write to secure audit log
        audit_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "patient_id": patient_id,
            "action": action,
            "details": details,
            "source_ip": "127.0.0.1",  # Would get from request context
            "session_id": "system",  # Would get from session context
        }

        logger.info(f"HIPAA Audit: {audit_entry}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get patient service statistics."""
        total_patients = len(self._patients)
        archived_patients = sum(
            1 for p in self._patients.values() if p.metadata.get("archived", False)
        )
        active_patients = total_patients - archived_patients

        return {
            "total_patients": total_patients,
            "active_patients": active_patients,
            "archived_patients": archived_patients,
            "patients_with_treatment_plans": sum(
                1 for p in self._patients.values() if p.treatment_plan is not None
            ),
            "patients_with_active_sessions": sum(
                1 for p in self._patients.values() if p.active_sessions
            ),
        }
