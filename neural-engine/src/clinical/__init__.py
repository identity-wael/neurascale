"""Clinical workflow management module for NeuraScale Neural Engine.

This module provides comprehensive clinical workflow management including:
- Patient lifecycle management and onboarding
- Clinical session orchestration and monitoring
- Treatment planning and protocol execution
- External system integration (EMR/FHIR)
- Clinical reporting and compliance

Designed for healthcare deployment with HIPAA compliance and safety protocols.
"""

from .patients.patient_service import PatientService
from .sessions.session_manager import SessionManager
from .workflows.treatment_planner import TreatmentPlanner
from .workflows.protocol_engine import ProtocolEngine
from .workflows.decision_support import ClinicalDecisionSupport

__version__ = "1.0.0"
__all__ = [
    "PatientService",
    "SessionManager",
    "TreatmentPlanner",
    "ProtocolEngine",
    "ClinicalDecisionSupport",
    "ClinicalWorkflowManager",
]


class ClinicalWorkflowManager:
    """Main clinical workflow orchestrator.

    Coordinates patient management, session execution, treatment planning,
    and safety monitoring for clinical BCI deployments.
    """

    def __init__(self, config):
        """Initialize clinical workflow manager with configuration."""
        self.config = config
        self.patient_service = PatientService(config)
        self.session_manager = SessionManager(config)
        self.treatment_planner = TreatmentPlanner(config)
        self.protocol_engine = ProtocolEngine(config)
        self.decision_support = ClinicalDecisionSupport(config)

    async def onboard_patient(self, patient_data: dict):
        """Complete patient onboarding workflow."""
        return await self.patient_service.register_patient(patient_data)

    async def schedule_session(self, patient_id: str, session_request):
        """Schedule and prepare clinical session."""
        return await self.session_manager.create_session(patient_id, session_request)

    async def start_clinical_session(self, session_id: str):
        """Initiate clinical BCI session with safety checks."""
        return await self.session_manager.start_session(session_id)

    async def monitor_session_safety(self, session_id: str):
        """Real-time safety monitoring during session."""
        return await self.session_manager.monitor_session_progress(session_id)
