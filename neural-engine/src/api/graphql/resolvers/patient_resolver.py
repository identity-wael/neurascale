"""Patient resolver implementation."""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
import random

from ..schema.types import Patient

logger = logging.getLogger(__name__)


class PatientResolver:
    """Resolver for patient-related queries."""

    def __init__(self):
        """Initialize patient resolver."""
        self.patients_db = self._create_mock_patients()

    def _create_mock_patients(self) -> Dict[str, Patient]:
        """Create mock patients for testing."""
        patients = {}

        for i in range(50):
            patient_id = f"pat_{i + 1:03d}"

            # Generate creation date
            days_ago = random.randint(0, 365)
            created_at = datetime.utcnow() - timedelta(days=days_ago)

            patient = Patient(
                id=patient_id,
                external_id=f"EXT{i + 1:05d}",
                created_at=created_at,
                metadata={
                    "age_group": random.choice(
                        ["18-25", "26-35", "36-45", "46-55", "56-65", "65+"]
                    ),
                    "gender": random.choice(["M", "F", "O"]),
                    "study_group": random.choice(
                        ["control", "treatment_a", "treatment_b"]
                    ),
                    "consent": True,
                    "enrollment_date": created_at.isoformat(),
                },
            )
            patients[patient_id] = patient

        return patients

    async def get_patient(self, patient_id: str) -> Optional[Patient]:
        """Get a patient by ID."""
        return self.patients_db.get(patient_id)

    async def get_patient_by_external_id(self, external_id: str) -> Optional[Patient]:
        """Get a patient by external ID."""
        for patient in self.patients_db.values():
            if patient.external_id == external_id:
                return patient
        return None

    async def get_patient_sessions(self, patient_id: str) -> List[Any]:
        """Get sessions for a patient."""
        # Would be implemented with actual session data
        return []

    async def get_patient_treatments(self, patient_id: str) -> List[Any]:
        """Get treatments for a patient."""
        # Would be implemented with actual treatment data
        return []
