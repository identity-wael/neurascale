"""Patient management module for clinical workflows."""

from .patient_service import PatientService
from .onboarding import PatientOnboarding
from .medical_history import MedicalHistoryManager
from .consent_management import ConsentManager
from .privacy_controls import PrivacyControls

__all__ = [
    "PatientService",
    "PatientOnboarding",
    "MedicalHistoryManager",
    "ConsentManager",
    "PrivacyControls",
]
