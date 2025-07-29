"""Patient onboarding workflow management."""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from uuid import uuid4

from ..types import Patient, ConsentRecord, ConsentStatus, ClinicalConfig

logger = logging.getLogger(__name__)


class PatientOnboarding:
    """Manages patient registration and onboarding workflows.

    Handles multi-step onboarding process including consent collection,
    eligibility verification, and care team setup.
    """

    def __init__(self, config: ClinicalConfig):
        """Initialize onboarding service."""
        self.config = config

        # Onboarding workflow tracking
        self._onboarding_workflows: Dict[str, Dict[str, Any]] = {}

        logger.info("Patient onboarding service initialized")

    async def create_registration_workflow(
        self, patient: Patient, patient_data: dict
    ) -> str:
        """Create complete patient registration workflow.

        Args:
            patient: Patient record
            patient_data: Registration data

        Returns:
            Workflow ID for tracking
        """
        workflow_id = str(uuid4())

        workflow = {
            "workflow_id": workflow_id,
            "patient_id": patient.patient_id,
            "created_date": datetime.now(timezone.utc),
            "status": "in_progress",
            "steps": {
                "eligibility_check": {"status": "pending", "required": True},
                "consent_collection": {"status": "pending", "required": True},
                "medical_history": {"status": "pending", "required": True},
                "care_team_setup": {"status": "pending", "required": False},
                "orientation": {"status": "pending", "required": True},
            },
            "data": patient_data,
        }

        self._onboarding_workflows[workflow_id] = workflow

        # Start workflow execution
        await self._execute_workflow_step(workflow_id, "eligibility_check")

        logger.info(
            f"Registration workflow created: {workflow_id} for patient {patient.patient_id}"
        )

        return workflow_id

    async def process_consent_forms(
        self, patient_id: str, consent_data: dict
    ) -> List[ConsentRecord]:
        """Process patient consent forms.

        Args:
            patient_id: Patient identifier
            consent_data: Consent form data

        Returns:
            List of consent records created
        """
        consent_records = []

        # Required consent types for BCI treatment
        required_consents = [
            "treatment_consent",
            "data_collection_consent",
            "privacy_notice",
            "hipaa_authorization",
        ]

        # Optional consent types
        optional_consents = [
            "research_participation",
            "data_sharing",
            "marketing_communications",
        ]

        all_consents = required_consents + optional_consents

        for consent_type in all_consents:
            if consent_type in consent_data:
                consent_info = consent_data[consent_type]

                # Create consent record
                consent_record = ConsentRecord(
                    patient_id=patient_id,
                    consent_type=consent_type,
                    status=(
                        ConsentStatus.APPROVED
                        if consent_info.get("granted", False)
                        else ConsentStatus.PENDING
                    ),
                    granted_date=(
                        datetime.now(timezone.utc)
                        if consent_info.get("granted", False)
                        else None
                    ),
                    expiry_date=self._calculate_consent_expiry(consent_type),
                    consent_text=consent_info.get("text", ""),
                    signed_by=consent_info.get("signed_by", ""),
                    witness=consent_info.get("witness"),
                )

                consent_records.append(consent_record)

        # Validate required consents are granted
        missing_required = []
        for consent_type in required_consents:
            consent_granted = any(
                c.consent_type == consent_type and c.status == ConsentStatus.APPROVED
                for c in consent_records
            )
            if not consent_granted:
                missing_required.append(consent_type)

        if missing_required:
            logger.warning(
                f"Missing required consents for patient {patient_id}: {missing_required}"
            )

        logger.info(
            f"Processed {len(consent_records)} consent forms for patient {patient_id}"
        )

        return consent_records

    async def validate_medical_eligibility(self, patient_id: str) -> Dict[str, Any]:
        """Validate patient medical eligibility for BCI treatment.

        Args:
            patient_id: Patient identifier

        Returns:
            Eligibility validation result
        """
        # In a real implementation, this would integrate with clinical decision support
        # and evidence-based eligibility criteria

        result = {
            "eligible": True,
            "contraindications": [],
            "warnings": [],
            "recommendations": [],
            "reviewed_by": "system",
            "review_date": datetime.now(timezone.utc),
        }

        # Example eligibility checks (would be more comprehensive in practice)
        eligibility_checks = [
            self._check_age_eligibility,
            self._check_medical_contraindications,
            self._check_medication_interactions,
            self._check_prior_bci_experience,
        ]

        for check_func in eligibility_checks:
            check_result = await check_func(patient_id)

            if not check_result["passed"]:
                result["eligible"] = False
                result["contraindications"].extend(
                    check_result.get("contraindications", [])
                )

            result["warnings"].extend(check_result.get("warnings", []))
            result["recommendations"].extend(check_result.get("recommendations", []))

        logger.info(
            f"Medical eligibility validated for patient {patient_id}: {result['eligible']}"
        )

        return result

    async def setup_care_team_access(
        self, patient_id: str, providers: List[str]
    ) -> bool:
        """Setup care team access permissions for patient.

        Args:
            patient_id: Patient identifier
            providers: List of provider identifiers

        Returns:
            Success status
        """
        try:
            # In production, this would:
            # 1. Validate provider credentials
            # 2. Set up role-based access permissions
            # 3. Configure notification preferences
            # 4. Establish communication channels

            access_setup = {
                "patient_id": patient_id,
                "providers": providers,
                "setup_date": datetime.now(timezone.utc),
                "permissions": {
                    "view_medical_record": True,
                    "update_treatment_plan": True,
                    "schedule_sessions": True,
                    "view_session_data": True,
                    "emergency_contact": True,
                },
                "notification_preferences": {
                    "session_alerts": True,
                    "safety_alerts": True,
                    "progress_updates": True,
                },
            }

            logger.info(
                f"Care team access setup for patient {patient_id}: {access_setup}"
            )

            return True

        except Exception as e:
            logger.error(f"Care team setup failed for patient {patient_id}: {e}")
            return False

    async def complete_patient_orientation(
        self, patient_id: str, orientation_data: dict
    ) -> bool:
        """Complete patient orientation and education.

        Args:
            patient_id: Patient identifier
            orientation_data: Orientation completion data

        Returns:
            Success status
        """
        try:
            # Record orientation completion
            orientation_record = {
                "patient_id": patient_id,
                "completed_date": datetime.now(timezone.utc),
                "materials_reviewed": orientation_data.get("materials_reviewed", []),
                "competency_verified": orientation_data.get(
                    "competency_verified", False
                ),
                "questions_answered": orientation_data.get("questions_answered", []),
                "conducted_by": orientation_data.get("conducted_by", "system"),
                "duration_minutes": orientation_data.get("duration_minutes", 0),
            }

            # Verify required orientation materials were covered
            required_materials = [
                "bci_technology_overview",
                "treatment_expectations",
                "safety_procedures",
                "data_privacy_rights",
                "contact_information",
            ]

            covered_materials = orientation_record["materials_reviewed"]
            missing_materials = [
                m for m in required_materials if m not in covered_materials
            ]

            if missing_materials:
                logger.warning(
                    f"Incomplete orientation for patient {patient_id}, missing: {missing_materials}"
                )
                return False

            logger.info(f"Patient orientation completed for {patient_id}")

            return True

        except Exception as e:
            logger.error(f"Patient orientation failed for {patient_id}: {e}")
            return False

    async def get_onboarding_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get current onboarding workflow status.

        Args:
            workflow_id: Workflow identifier

        Returns:
            Workflow status information
        """
        if workflow_id not in self._onboarding_workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")

        workflow = self._onboarding_workflows[workflow_id]

        # Calculate progress
        steps = workflow["steps"]
        total_steps = len(steps)
        completed_steps = sum(
            1 for step in steps.values() if step["status"] == "completed"
        )
        progress_percent = (completed_steps / total_steps) * 100

        return {
            "workflow_id": workflow_id,
            "patient_id": workflow["patient_id"],
            "status": workflow["status"],
            "progress_percent": progress_percent,
            "completed_steps": completed_steps,
            "total_steps": total_steps,
            "steps": steps,
            "created_date": workflow["created_date"],
            "estimated_completion": self._estimate_completion_time(workflow),
        }

    async def _execute_workflow_step(self, workflow_id: str, step_name: str):
        """Execute a specific workflow step.

        Args:
            workflow_id: Workflow identifier
            step_name: Step to execute
        """
        workflow = self._onboarding_workflows[workflow_id]
        step = workflow["steps"][step_name]

        if step["status"] != "pending":
            return

        step["status"] = "in_progress"
        step["started_date"] = datetime.now(timezone.utc)

        try:
            # Execute step based on type
            if step_name == "eligibility_check":
                result = await self.validate_medical_eligibility(workflow["patient_id"])
                step["result"] = result
                step["status"] = "completed" if result["eligible"] else "failed"

            elif step_name == "consent_collection":
                # This would typically wait for external input
                step["status"] = "waiting_for_input"

            elif step_name == "medical_history":
                # Mark as completed if medical history exists
                step["status"] = "completed"  # Simplified for demo

            elif step_name == "care_team_setup":
                # Optional step
                step["status"] = "completed"

            elif step_name == "orientation":
                # This would typically wait for orientation completion
                step["status"] = "waiting_for_input"

            step["completed_date"] = datetime.now(timezone.utc)

            # Check if workflow is complete
            await self._check_workflow_completion(workflow_id)

        except Exception as e:
            step["status"] = "failed"
            step["error"] = str(e)
            logger.error(f"Workflow step failed: {workflow_id}.{step_name}: {e}")

    async def _check_workflow_completion(self, workflow_id: str):
        """Check if workflow is complete and update status."""
        workflow = self._onboarding_workflows[workflow_id]
        steps = workflow["steps"]

        # Check if all required steps are completed
        required_steps = [name for name, step in steps.items() if step["required"]]
        completed_required = [
            name for name in required_steps if steps[name]["status"] == "completed"
        ]

        if len(completed_required) == len(required_steps):
            workflow["status"] = "completed"
            workflow["completed_date"] = datetime.now(timezone.utc)
            logger.info(f"Onboarding workflow completed: {workflow_id}")

    def _calculate_consent_expiry(self, consent_type: str) -> datetime:
        """Calculate consent expiry date based on type."""
        base_date = datetime.now(timezone.utc)

        # Different consent types have different expiry periods
        expiry_periods = {
            "treatment_consent": timedelta(days=365),  # 1 year
            "data_collection_consent": timedelta(days=365),
            "privacy_notice": timedelta(days=730),  # 2 years
            "hipaa_authorization": timedelta(days=365),
            "research_participation": timedelta(days=730),
            "data_sharing": timedelta(days=365),
            "marketing_communications": timedelta(days=730),
        }

        period = expiry_periods.get(consent_type, timedelta(days=365))
        return base_date + period

    async def _check_age_eligibility(self, patient_id: str) -> Dict[str, Any]:
        """Check age-based eligibility."""
        # Simplified implementation
        return {
            "passed": True,
            "warnings": [],
            "contraindications": [],
            "recommendations": [],
        }

    async def _check_medical_contraindications(self, patient_id: str) -> Dict[str, Any]:
        """Check for medical contraindications."""
        # Simplified implementation
        return {
            "passed": True,
            "warnings": [],
            "contraindications": [],
            "recommendations": [],
        }

    async def _check_medication_interactions(self, patient_id: str) -> Dict[str, Any]:
        """Check for medication interactions."""
        # Simplified implementation
        return {
            "passed": True,
            "warnings": [],
            "contraindications": [],
            "recommendations": [],
        }

    async def _check_prior_bci_experience(self, patient_id: str) -> Dict[str, Any]:
        """Check prior BCI experience."""
        # Simplified implementation
        return {
            "passed": True,
            "warnings": [],
            "contraindications": [],
            "recommendations": [
                "Consider extended orientation for first-time BCI users"
            ],
        }

    def _estimate_completion_time(self, workflow: dict) -> Optional[datetime]:
        """Estimate workflow completion time."""
        # Simple estimation based on typical completion times
        pending_steps = [
            name
            for name, step in workflow["steps"].items()
            if step["status"] in ["pending", "in_progress", "waiting_for_input"]
        ]

        if not pending_steps:
            return None

        # Estimate 2 hours per remaining step (simplified)
        hours_remaining = len(pending_steps) * 2
        return datetime.now(timezone.utc) + timedelta(hours=hours_remaining)
