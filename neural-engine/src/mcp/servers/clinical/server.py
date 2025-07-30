"""Clinical MCP Server implementation."""

from typing import Dict, Any, List, Optional

from ...core.base_server import BaseNeuralMCPServer
from ...utils.validators import (
    validate_patient_params,
    validate_treatment_params,
    validate_report_params,
)
from .handlers import ClinicalHandlers


class ClinicalMCPServer(BaseNeuralMCPServer):
    """MCP server for clinical data management and patient care."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize Clinical MCP server.

        Args:
            config: Server configuration
        """
        super().__init__("neurascale-clinical", "1.0.0", config)

        # Initialize handlers
        self.handlers = ClinicalHandlers(config.get("clinical_system", {}))

    async def register_tools(self) -> None:
        """Register all clinical tools."""

        # Patient Management Tools
        self.register_tool(
            name="create_patient_record",
            handler=self._create_patient_record,
            description="Create a new patient record in the clinical system",
            input_schema={
                "type": "object",
                "properties": {
                    "external_id": {
                        "type": "string",
                        "description": "External patient identifier (e.g., MRN)",
                    },
                    "demographics": {
                        "type": "object",
                        "properties": {
                            "date_of_birth": {
                                "type": "string",
                                "format": "date",
                                "description": "Patient date of birth",
                            },
                            "gender": {
                                "type": "string",
                                "enum": [
                                    "male",
                                    "female",
                                    "other",
                                    "prefer_not_to_say",
                                ],
                            },
                            "height_cm": {"type": "number", "minimum": 0},
                            "weight_kg": {"type": "number", "minimum": 0},
                        },
                        "required": ["date_of_birth"],
                        "description": "Patient demographic information",
                    },
                    "medical_history": {
                        "type": "object",
                        "properties": {
                            "diagnoses": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of diagnoses",
                            },
                            "medications": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "dosage": {"type": "string"},
                                        "frequency": {"type": "string"},
                                    },
                                },
                                "description": "Current medications",
                            },
                            "allergies": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Known allergies",
                            },
                        },
                        "description": "Medical history information",
                    },
                    "consent": {
                        "type": "object",
                        "properties": {
                            "data_collection": {"type": "boolean"},
                            "research_participation": {"type": "boolean"},
                            "consent_date": {"type": "string", "format": "date-time"},
                        },
                        "required": ["data_collection", "consent_date"],
                        "description": "Consent information",
                    },
                },
                "required": ["external_id", "demographics", "consent"],
            },
            permissions=["patient.create", "clinical.write"],
        )

        self.register_tool(
            name="get_patient_record",
            handler=self._get_patient_record,
            description="Retrieve patient clinical record",
            input_schema={
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "Patient identifier",
                    },
                    "include_history": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include medical history",
                    },
                    "include_sessions": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include recording sessions",
                    },
                    "include_treatments": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include treatment records",
                    },
                },
                "required": ["patient_id"],
            },
            permissions=["patient.read", "clinical.read"],
        )

        self.register_tool(
            name="update_patient_record",
            handler=self._update_patient_record,
            description="Update patient clinical information",
            input_schema={
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "Patient identifier",
                    },
                    "updates": {
                        "type": "object",
                        "properties": {
                            "demographics": {"type": "object"},
                            "medical_history": {"type": "object"},
                            "notes": {"type": "string"},
                        },
                        "description": "Fields to update",
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for update",
                    },
                },
                "required": ["patient_id", "updates", "reason"],
            },
            permissions=["patient.update", "clinical.write"],
        )

        # Treatment Management
        self.register_tool(
            name="create_treatment_plan",
            handler=self._create_treatment_plan,
            description="Create a treatment plan for a patient",
            input_schema={
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "Patient identifier",
                    },
                    "treatment_type": {
                        "type": "string",
                        "enum": [
                            "neurostimulation",
                            "neurofeedback",
                            "medication",
                            "therapy",
                            "combined",
                        ],
                        "description": "Type of treatment",
                    },
                    "protocol": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "sessions_per_week": {"type": "integer", "minimum": 1},
                            "total_sessions": {"type": "integer", "minimum": 1},
                            "session_duration_minutes": {
                                "type": "integer",
                                "minimum": 5,
                            },
                            "parameters": {
                                "type": "object",
                                "description": "Treatment-specific parameters",
                            },
                        },
                        "required": ["name", "sessions_per_week", "total_sessions"],
                    },
                    "start_date": {
                        "type": "string",
                        "format": "date",
                        "description": "Treatment start date",
                    },
                    "physician_id": {
                        "type": "string",
                        "description": "Prescribing physician identifier",
                    },
                },
                "required": [
                    "patient_id",
                    "treatment_type",
                    "protocol",
                    "start_date",
                    "physician_id",
                ],
            },
            permissions=["treatment.create", "clinical.write"],
        )

        self.register_tool(
            name="record_treatment_session",
            handler=self._record_treatment_session,
            description="Record a treatment session",
            input_schema={
                "type": "object",
                "properties": {
                    "treatment_plan_id": {
                        "type": "string",
                        "description": "Treatment plan identifier",
                    },
                    "session_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Session date and time",
                    },
                    "duration_minutes": {
                        "type": "integer",
                        "minimum": 1,
                        "description": "Actual session duration",
                    },
                    "parameters_used": {
                        "type": "object",
                        "description": "Parameters used in this session",
                    },
                    "outcomes": {
                        "type": "object",
                        "properties": {
                            "patient_reported": {
                                "type": "object",
                                "description": "Patient-reported outcomes",
                            },
                            "clinician_observed": {
                                "type": "object",
                                "description": "Clinician observations",
                            },
                            "objective_measures": {
                                "type": "object",
                                "description": "Objective measurements",
                            },
                        },
                    },
                    "adverse_events": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "event": {"type": "string"},
                                "severity": {
                                    "type": "string",
                                    "enum": ["mild", "moderate", "severe"],
                                },
                                "action_taken": {"type": "string"},
                            },
                        },
                        "description": "Any adverse events during session",
                    },
                    "notes": {
                        "type": "string",
                        "description": "Session notes",
                    },
                },
                "required": ["treatment_plan_id", "session_date", "duration_minutes"],
            },
            permissions=["treatment.record", "clinical.write"],
        )

        # Clinical Reports
        self.register_tool(
            name="generate_clinical_report",
            handler=self._generate_clinical_report,
            description="Generate clinical reports for patients",
            input_schema={
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "Patient identifier",
                    },
                    "report_type": {
                        "type": "string",
                        "enum": [
                            "progress_summary",
                            "treatment_outcome",
                            "assessment_results",
                            "discharge_summary",
                            "referral_letter",
                        ],
                        "description": "Type of report to generate",
                    },
                    "date_range": {
                        "type": "object",
                        "properties": {
                            "start_date": {"type": "string", "format": "date"},
                            "end_date": {"type": "string", "format": "date"},
                        },
                        "required": ["start_date", "end_date"],
                        "description": "Date range for report",
                    },
                    "include_sections": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": [
                                "demographics",
                                "diagnosis",
                                "treatment_history",
                                "session_data",
                                "outcomes",
                                "recommendations",
                                "visualizations",
                            ],
                        },
                        "default": [
                            "demographics",
                            "diagnosis",
                            "treatment_history",
                            "outcomes",
                        ],
                        "description": "Sections to include in report",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["pdf", "html", "json", "docx"],
                        "default": "pdf",
                        "description": "Report format",
                    },
                },
                "required": ["patient_id", "report_type", "date_range"],
            },
            permissions=["report.generate", "clinical.read"],
        )

        # Outcome Tracking
        self.register_tool(
            name="record_clinical_outcome",
            handler=self._record_clinical_outcome,
            description="Record clinical outcome measures",
            input_schema={
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "Patient identifier",
                    },
                    "assessment_type": {
                        "type": "string",
                        "description": "Type of assessment (e.g., PHQ-9, GAD-7, custom)",
                    },
                    "assessment_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Date of assessment",
                    },
                    "scores": {
                        "type": "object",
                        "description": "Assessment scores/results",
                    },
                    "interpretation": {
                        "type": "string",
                        "description": "Clinical interpretation of results",
                    },
                    "administered_by": {
                        "type": "string",
                        "description": "Clinician who administered assessment",
                    },
                },
                "required": [
                    "patient_id",
                    "assessment_type",
                    "assessment_date",
                    "scores",
                ],
            },
            permissions=["outcome.record", "clinical.write"],
        )

        self.register_tool(
            name="track_patient_progress",
            handler=self._track_patient_progress,
            description="Track patient progress over time",
            input_schema={
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "Patient identifier",
                    },
                    "metrics": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Metrics to track",
                    },
                    "time_period": {
                        "type": "string",
                        "enum": ["week", "month", "quarter", "year", "all_time"],
                        "default": "month",
                        "description": "Time period for tracking",
                    },
                    "comparison_baseline": {
                        "type": "string",
                        "enum": ["pre_treatment", "first_session", "custom_date"],
                        "default": "pre_treatment",
                        "description": "Baseline for comparison",
                    },
                },
                "required": ["patient_id", "metrics"],
            },
            permissions=["patient.read", "outcome.read"],
        )

        # Clinical Protocols
        self.register_tool(
            name="get_clinical_protocols",
            handler=self._get_clinical_protocols,
            description="Retrieve available clinical protocols",
            input_schema={
                "type": "object",
                "properties": {
                    "condition": {
                        "type": "string",
                        "description": "Filter by condition/diagnosis",
                    },
                    "treatment_type": {
                        "type": "string",
                        "description": "Filter by treatment type",
                    },
                    "evidence_level": {
                        "type": "string",
                        "enum": ["A", "B", "C", "D", "experimental"],
                        "description": "Minimum evidence level",
                    },
                    "approved_only": {
                        "type": "boolean",
                        "default": True,
                        "description": "Only show approved protocols",
                    },
                },
                "required": [],
            },
            permissions=["protocol.read"],
        )

        # Compliance and Safety
        self.register_tool(
            name="check_treatment_compliance",
            handler=self._check_treatment_compliance,
            description="Check patient compliance with treatment plan",
            input_schema={
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "Patient identifier",
                    },
                    "treatment_plan_id": {
                        "type": "string",
                        "description": "Treatment plan identifier (optional)",
                    },
                    "time_period": {
                        "type": "string",
                        "enum": ["week", "month", "all"],
                        "default": "month",
                        "description": "Time period to check",
                    },
                },
                "required": ["patient_id"],
            },
            permissions=["treatment.read", "compliance.read"],
        )

        self.register_tool(
            name="report_adverse_event",
            handler=self._report_adverse_event,
            description="Report an adverse event",
            input_schema={
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "Patient identifier",
                    },
                    "event_date": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Date/time of event",
                    },
                    "event_description": {
                        "type": "string",
                        "description": "Detailed description of event",
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["mild", "moderate", "severe", "life_threatening"],
                        "description": "Event severity",
                    },
                    "treatment_related": {
                        "type": "boolean",
                        "description": "Is event related to treatment?",
                    },
                    "action_taken": {
                        "type": "string",
                        "description": "Action taken in response",
                    },
                    "outcome": {
                        "type": "string",
                        "enum": ["resolved", "resolving", "ongoing", "unknown"],
                        "description": "Event outcome",
                    },
                    "reported_by": {
                        "type": "string",
                        "description": "Person reporting the event",
                    },
                },
                "required": [
                    "patient_id",
                    "event_date",
                    "event_description",
                    "severity",
                    "reported_by",
                ],
            },
            permissions=["adverse_event.report", "clinical.write"],
        )

    # Tool Implementation Methods
    async def _create_patient_record(
        self,
        external_id: str,
        demographics: Dict[str, Any],
        consent: Dict[str, Any],
        medical_history: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new patient record."""
        # Validate parameters
        validate_patient_params(
            {
                "external_id": external_id,
                "demographics": demographics,
                "consent": consent,
            }
        )

        return await self.handlers.create_patient_record(
            external_id=external_id,
            demographics=demographics,
            consent=consent,
            medical_history=medical_history or {},
        )

    async def _get_patient_record(
        self,
        patient_id: str,
        include_history: bool = True,
        include_sessions: bool = True,
        include_treatments: bool = True,
    ) -> Dict[str, Any]:
        """Retrieve patient record."""
        return await self.handlers.get_patient_record(
            patient_id=patient_id,
            include_history=include_history,
            include_sessions=include_sessions,
            include_treatments=include_treatments,
        )

    async def _update_patient_record(
        self, patient_id: str, updates: Dict[str, Any], reason: str
    ) -> Dict[str, Any]:
        """Update patient record."""
        return await self.handlers.update_patient_record(
            patient_id=patient_id, updates=updates, reason=reason
        )

    async def _create_treatment_plan(
        self,
        patient_id: str,
        treatment_type: str,
        protocol: Dict[str, Any],
        start_date: str,
        physician_id: str,
    ) -> Dict[str, Any]:
        """Create treatment plan."""
        # Validate parameters
        validate_treatment_params(
            {
                "treatment_type": treatment_type,
                "protocol": protocol,
                "start_date": start_date,
            }
        )

        return await self.handlers.create_treatment_plan(
            patient_id=patient_id,
            treatment_type=treatment_type,
            protocol=protocol,
            start_date=start_date,
            physician_id=physician_id,
        )

    async def _record_treatment_session(
        self,
        treatment_plan_id: str,
        session_date: str,
        duration_minutes: int,
        parameters_used: Optional[Dict[str, Any]] = None,
        outcomes: Optional[Dict[str, Any]] = None,
        adverse_events: Optional[List[Dict[str, Any]]] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Record treatment session."""
        return await self.handlers.record_treatment_session(
            treatment_plan_id=treatment_plan_id,
            session_date=session_date,
            duration_minutes=duration_minutes,
            parameters_used=parameters_used or {},
            outcomes=outcomes or {},
            adverse_events=adverse_events or [],
            notes=notes,
        )

    async def _generate_clinical_report(
        self,
        patient_id: str,
        report_type: str,
        date_range: Dict[str, str],
        include_sections: List[str] = None,
        format: str = "pdf",
    ) -> Dict[str, Any]:
        """Generate clinical report."""
        # Validate parameters
        validate_report_params(
            {"report_type": report_type, "date_range": date_range, "format": format}
        )

        if include_sections is None:
            include_sections = [
                "demographics",
                "diagnosis",
                "treatment_history",
                "outcomes",
            ]

        return await self.handlers.generate_clinical_report(
            patient_id=patient_id,
            report_type=report_type,
            date_range=date_range,
            include_sections=include_sections,
            format=format,
        )

    async def _record_clinical_outcome(
        self,
        patient_id: str,
        assessment_type: str,
        assessment_date: str,
        scores: Dict[str, Any],
        interpretation: Optional[str] = None,
        administered_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Record clinical outcome."""
        return await self.handlers.record_clinical_outcome(
            patient_id=patient_id,
            assessment_type=assessment_type,
            assessment_date=assessment_date,
            scores=scores,
            interpretation=interpretation,
            administered_by=administered_by,
        )

    async def _track_patient_progress(
        self,
        patient_id: str,
        metrics: List[str],
        time_period: str = "month",
        comparison_baseline: str = "pre_treatment",
    ) -> Dict[str, Any]:
        """Track patient progress."""
        return await self.handlers.track_patient_progress(
            patient_id=patient_id,
            metrics=metrics,
            time_period=time_period,
            comparison_baseline=comparison_baseline,
        )

    async def _get_clinical_protocols(
        self,
        condition: Optional[str] = None,
        treatment_type: Optional[str] = None,
        evidence_level: Optional[str] = None,
        approved_only: bool = True,
    ) -> Dict[str, Any]:
        """Get clinical protocols."""
        return await self.handlers.get_clinical_protocols(
            condition=condition,
            treatment_type=treatment_type,
            evidence_level=evidence_level,
            approved_only=approved_only,
        )

    async def _check_treatment_compliance(
        self,
        patient_id: str,
        treatment_plan_id: Optional[str] = None,
        time_period: str = "month",
    ) -> Dict[str, Any]:
        """Check treatment compliance."""
        return await self.handlers.check_treatment_compliance(
            patient_id=patient_id,
            treatment_plan_id=treatment_plan_id,
            time_period=time_period,
        )

    async def _report_adverse_event(
        self,
        patient_id: str,
        event_date: str,
        event_description: str,
        severity: str,
        reported_by: str,
        treatment_related: Optional[bool] = None,
        action_taken: Optional[str] = None,
        outcome: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Report adverse event."""
        return await self.handlers.report_adverse_event(
            patient_id=patient_id,
            event_date=event_date,
            event_description=event_description,
            severity=severity,
            reported_by=reported_by,
            treatment_related=treatment_related,
            action_taken=action_taken,
            outcome=outcome,
        )
