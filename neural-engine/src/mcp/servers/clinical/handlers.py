"""Clinical data handlers for MCP server operations."""

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import random


class ClinicalHandlers:
    """Handles clinical operations for MCP server."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize clinical handlers.

        Args:
            config: Clinical system configuration
        """
        self.config = config
        self.api_url = config.get("api_url", "http://localhost:8000")

        # Mock data for demonstration
        self._mock_patients = {}
        self._mock_treatment_plans = {}
        self._mock_sessions = {}
        self._mock_outcomes = {}
        self._mock_adverse_events = []
        self._init_mock_data()

    def _init_mock_data(self):
        """Initialize mock clinical data."""
        # Create some sample patients
        for i in range(5):
            patient_id = f"patient_{i + 1:03d}"
            self._mock_patients[patient_id] = {
                "id": patient_id,
                "external_id": f"MRN{1000 + i}",
                "demographics": {
                    "date_of_birth": f"19{70 + i * 5}-01-15",
                    "gender": ["male", "female"][i % 2],
                    "height_cm": 170 + i * 5,
                    "weight_kg": 70 + i * 3,
                },
                "medical_history": {
                    "diagnoses": [
                        "Depression",
                        "Anxiety",
                        "PTSD",
                        "Chronic Pain",
                        "Migraine",
                    ][i],
                    "medications": (
                        [
                            {
                                "name": "Sertraline",
                                "dosage": "50mg",
                                "frequency": "daily",
                            },
                            {
                                "name": "Alprazolam",
                                "dosage": "0.5mg",
                                "frequency": "as needed",
                            },
                        ]
                        if i % 2 == 0
                        else []
                    ),
                    "allergies": ["Penicillin"] if i == 2 else [],
                },
                "consent": {
                    "data_collection": True,
                    "research_participation": i % 2 == 0,
                    "consent_date": datetime.utcnow().isoformat(),
                },
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }

    async def create_patient_record(
        self,
        external_id: str,
        demographics: Dict[str, Any],
        consent: Dict[str, Any],
        medical_history: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a new patient record.

        Args:
            external_id: External patient ID
            demographics: Patient demographics
            consent: Consent information
            medical_history: Medical history

        Returns:
            Created patient record
        """
        patient_id = f"patient_{len(self._mock_patients) + 1:03d}"

        patient_record = {
            "id": patient_id,
            "external_id": external_id,
            "demographics": demographics,
            "medical_history": medical_history,
            "consent": consent,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "status": "active",
        }

        self._mock_patients[patient_id] = patient_record

        return {
            "patient_id": patient_id,
            "external_id": external_id,
            "status": "created",
            "message": "Patient record created successfully",
            "created_at": patient_record["created_at"],
        }

    async def get_patient_record(
        self,
        patient_id: str,
        include_history: bool = True,
        include_sessions: bool = True,
        include_treatments: bool = True,
    ) -> Dict[str, Any]:
        """Retrieve patient record.

        Args:
            patient_id: Patient identifier
            include_history: Include medical history
            include_sessions: Include session records
            include_treatments: Include treatment records

        Returns:
            Patient record with requested information
        """
        patient = self._mock_patients.get(patient_id)
        if not patient:
            raise ValueError(f"Patient not found: {patient_id}")

        result = patient.copy()

        if not include_history:
            result.pop("medical_history", None)

        if include_sessions:
            # Get patient sessions
            patient_sessions = [
                s
                for s in self._mock_sessions.values()
                if s.get("patient_id") == patient_id
            ]
            result["sessions"] = {
                "count": len(patient_sessions),
                "recent": patient_sessions[-5:] if patient_sessions else [],
            }

        if include_treatments:
            # Get patient treatment plans
            patient_treatments = [
                t
                for t in self._mock_treatment_plans.values()
                if t.get("patient_id") == patient_id
            ]
            result["treatments"] = {
                "active": [
                    t for t in patient_treatments if t.get("status") == "active"
                ],
                "completed": [
                    t for t in patient_treatments if t.get("status") == "completed"
                ],
            }

        return result

    async def update_patient_record(
        self, patient_id: str, updates: Dict[str, Any], reason: str
    ) -> Dict[str, Any]:
        """Update patient record.

        Args:
            patient_id: Patient identifier
            updates: Fields to update
            reason: Reason for update

        Returns:
            Update confirmation
        """
        patient = self._mock_patients.get(patient_id)
        if not patient:
            raise ValueError(f"Patient not found: {patient_id}")

        # Update fields
        for key, value in updates.items():
            if key in ["demographics", "medical_history"]:
                patient[key].update(value)
            else:
                patient[key] = value

        patient["updated_at"] = datetime.utcnow().isoformat()

        # Add audit log entry (in production, would be stored separately)
        if "audit_log" not in patient:
            patient["audit_log"] = []

        patient["audit_log"].append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "action": "update",
                "reason": reason,
                "fields_updated": list(updates.keys()),
            }
        )

        return {
            "patient_id": patient_id,
            "status": "updated",
            "updated_fields": list(updates.keys()),
            "updated_at": patient["updated_at"],
            "message": f"Patient record updated: {reason}",
        }

    async def create_treatment_plan(
        self,
        patient_id: str,
        treatment_type: str,
        protocol: Dict[str, Any],
        start_date: str,
        physician_id: str,
    ) -> Dict[str, Any]:
        """Create treatment plan.

        Args:
            patient_id: Patient identifier
            treatment_type: Type of treatment
            protocol: Treatment protocol details
            start_date: Start date
            physician_id: Prescribing physician

        Returns:
            Created treatment plan
        """
        if patient_id not in self._mock_patients:
            raise ValueError(f"Patient not found: {patient_id}")

        plan_id = f"plan_{len(self._mock_treatment_plans) + 1:03d}"

        # Calculate end date based on protocol
        start = datetime.fromisoformat(start_date)
        total_weeks = protocol["total_sessions"] / protocol["sessions_per_week"]
        end_date = start + timedelta(weeks=total_weeks)

        treatment_plan = {
            "id": plan_id,
            "patient_id": patient_id,
            "treatment_type": treatment_type,
            "protocol": protocol,
            "start_date": start_date,
            "end_date": end_date.isoformat(),
            "physician_id": physician_id,
            "status": "active",
            "sessions_completed": 0,
            "sessions_scheduled": protocol["total_sessions"],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        self._mock_treatment_plans[plan_id] = treatment_plan

        return {
            "treatment_plan_id": plan_id,
            "patient_id": patient_id,
            "status": "created",
            "start_date": start_date,
            "end_date": end_date.isoformat(),
            "total_sessions": protocol["total_sessions"],
            "message": f"Treatment plan created: {protocol['name']}",
        }

    async def record_treatment_session(
        self,
        treatment_plan_id: str,
        session_date: str,
        duration_minutes: int,
        parameters_used: Dict[str, Any],
        outcomes: Dict[str, Any],
        adverse_events: List[Dict[str, Any]],
        notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Record treatment session.

        Args:
            treatment_plan_id: Treatment plan ID
            session_date: Session date
            duration_minutes: Session duration
            parameters_used: Treatment parameters
            outcomes: Session outcomes
            adverse_events: Any adverse events
            notes: Session notes

        Returns:
            Recorded session information
        """
        plan = self._mock_treatment_plans.get(treatment_plan_id)
        if not plan:
            raise ValueError(f"Treatment plan not found: {treatment_plan_id}")

        session_id = f"session_{len(self._mock_sessions) + 1:04d}"

        session = {
            "id": session_id,
            "treatment_plan_id": treatment_plan_id,
            "patient_id": plan["patient_id"],
            "session_date": session_date,
            "duration_minutes": duration_minutes,
            "parameters_used": parameters_used,
            "outcomes": outcomes,
            "adverse_events": adverse_events,
            "notes": notes,
            "recorded_at": datetime.utcnow().isoformat(),
            "session_number": plan["sessions_completed"] + 1,
        }

        self._mock_sessions[session_id] = session

        # Update treatment plan
        plan["sessions_completed"] += 1
        plan["updated_at"] = datetime.utcnow().isoformat()

        # Record any adverse events
        for event in adverse_events:
            self._mock_adverse_events.append(
                {
                    **event,
                    "session_id": session_id,
                    "patient_id": plan["patient_id"],
                    "reported_date": datetime.utcnow().isoformat(),
                }
            )

        return {
            "session_id": session_id,
            "treatment_plan_id": treatment_plan_id,
            "session_number": session["session_number"],
            "sessions_remaining": plan["sessions_scheduled"]
            - plan["sessions_completed"],
            "adverse_events_recorded": len(adverse_events),
            "status": "recorded",
            "message": f"Session {session['session_number']} recorded successfully",
        }

    async def generate_clinical_report(
        self,
        patient_id: str,
        report_type: str,
        date_range: Dict[str, str],
        include_sections: List[str],
        format: str,
    ) -> Dict[str, Any]:
        """Generate clinical report.

        Args:
            patient_id: Patient identifier
            report_type: Type of report
            date_range: Date range for report
            include_sections: Sections to include
            format: Report format

        Returns:
            Generated report information
        """
        patient = self._mock_patients.get(patient_id)
        if not patient:
            raise ValueError(f"Patient not found: {patient_id}")

        report_id = str(uuid.uuid4())

        # Gather data for report
        start_date = datetime.fromisoformat(date_range["start_date"])
        end_date = datetime.fromisoformat(date_range["end_date"])

        # Get sessions in date range
        patient_sessions = [
            s
            for s in self._mock_sessions.values()
            if s.get("patient_id") == patient_id
            and start_date <= datetime.fromisoformat(s["session_date"]) <= end_date
        ]

        # Get treatment plans
        patient_treatments = [
            t
            for t in self._mock_treatment_plans.values()
            if t.get("patient_id") == patient_id
        ]

        # Generate report content (mock)
        report_content = {
            "report_id": report_id,
            "report_type": report_type,
            "patient_id": patient_id,
            "date_range": date_range,
            "generated_at": datetime.utcnow().isoformat(),
        }

        if "demographics" in include_sections:
            report_content["demographics"] = patient["demographics"]

        if "diagnosis" in include_sections:
            report_content["diagnosis"] = patient["medical_history"].get(
                "diagnoses", []
            )

        if "treatment_history" in include_sections:
            report_content["treatment_history"] = {
                "plans": patient_treatments,
                "sessions_count": len(patient_sessions),
                "total_duration_minutes": sum(
                    s["duration_minutes"] for s in patient_sessions
                ),
            }

        if "outcomes" in include_sections:
            # Calculate outcome summary
            outcomes_data = self._calculate_outcome_summary(patient_id, date_range)
            report_content["outcomes"] = outcomes_data

        # Generate file URL (mock)
        file_url = f"/reports/{report_id}.{format}"

        return {
            "report_id": report_id,
            "patient_id": patient_id,
            "report_type": report_type,
            "format": format,
            "file_url": file_url,
            "file_size_kb": random.randint(100, 500),
            "sections_included": include_sections,
            "generation_time_seconds": round(random.uniform(1, 5), 2),
            "status": "generated",
            "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        }

    async def record_clinical_outcome(
        self,
        patient_id: str,
        assessment_type: str,
        assessment_date: str,
        scores: Dict[str, Any],
        interpretation: Optional[str] = None,
        administered_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Record clinical outcome.

        Args:
            patient_id: Patient identifier
            assessment_type: Type of assessment
            assessment_date: Date of assessment
            scores: Assessment scores
            interpretation: Clinical interpretation
            administered_by: Clinician who administered

        Returns:
            Recorded outcome information
        """
        if patient_id not in self._mock_patients:
            raise ValueError(f"Patient not found: {patient_id}")

        outcome_id = f"outcome_{len(self._mock_outcomes) + 1:04d}"

        outcome = {
            "id": outcome_id,
            "patient_id": patient_id,
            "assessment_type": assessment_type,
            "assessment_date": assessment_date,
            "scores": scores,
            "interpretation": interpretation,
            "administered_by": administered_by,
            "recorded_at": datetime.utcnow().isoformat(),
        }

        # Calculate severity/risk level based on assessment type
        if assessment_type == "PHQ-9":
            total_score = sum(scores.values()) if isinstance(scores, dict) else scores
            if total_score < 5:
                outcome["severity"] = "minimal"
            elif total_score < 10:
                outcome["severity"] = "mild"
            elif total_score < 15:
                outcome["severity"] = "moderate"
            elif total_score < 20:
                outcome["severity"] = "moderately_severe"
            else:
                outcome["severity"] = "severe"

        self._mock_outcomes[outcome_id] = outcome

        return {
            "outcome_id": outcome_id,
            "patient_id": patient_id,
            "assessment_type": assessment_type,
            "severity": outcome.get("severity", "not_calculated"),
            "status": "recorded",
            "message": f"{assessment_type} outcome recorded successfully",
        }

    async def track_patient_progress(
        self,
        patient_id: str,
        metrics: List[str],
        time_period: str,
        comparison_baseline: str,
    ) -> Dict[str, Any]:
        """Track patient progress.

        Args:
            patient_id: Patient identifier
            metrics: Metrics to track
            time_period: Time period for tracking
            comparison_baseline: Baseline for comparison

        Returns:
            Progress tracking data
        """
        if patient_id not in self._mock_patients:
            raise ValueError(f"Patient not found: {patient_id}")

        # Calculate time range
        end_date = datetime.utcnow()
        if time_period == "week":
            start_date = end_date - timedelta(weeks=1)
        elif time_period == "month":
            start_date = end_date - timedelta(days=30)
        elif time_period == "quarter":
            start_date = end_date - timedelta(days=90)
        elif time_period == "year":
            start_date = end_date - timedelta(days=365)
        else:  # all_time
            start_date = datetime(2020, 1, 1)

        # Get patient outcomes in time period (currently not used in mock data)
        # patient_outcomes = [
        #     o
        #     for o in self._mock_outcomes.values()
        #     if o.get("patient_id") == patient_id
        #     and start_date <= datetime.fromisoformat(o["assessment_date"]) <= end_date
        # ]

        # Generate mock progress data
        progress_data = {
            "patient_id": patient_id,
            "time_period": time_period,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "metrics": {},
            "overall_trend": random.choice(["improving", "stable", "declining"]),
        }

        for metric in metrics:
            # Generate mock trend data
            data_points = []
            current_date = start_date
            baseline_value = random.uniform(50, 80)

            while current_date <= end_date:
                value = baseline_value + random.uniform(-10, 20)
                data_points.append(
                    {
                        "date": current_date.isoformat(),
                        "value": round(value, 1),
                    }
                )
                current_date += timedelta(days=7)

            progress_data["metrics"][metric] = {
                "data_points": data_points,
                "current_value": data_points[-1]["value"] if data_points else 0,
                "baseline_value": baseline_value,
                "change_percent": round(
                    (
                        (
                            (data_points[-1]["value"] - baseline_value)
                            / baseline_value
                            * 100
                        )
                        if data_points
                        else 0
                    ),
                    1,
                ),
                "trend": (
                    "improving"
                    if data_points and data_points[-1]["value"] > baseline_value
                    else "declining"
                ),
            }

        return progress_data

    async def get_clinical_protocols(
        self,
        condition: Optional[str] = None,
        treatment_type: Optional[str] = None,
        evidence_level: Optional[str] = None,
        approved_only: bool = True,
    ) -> Dict[str, Any]:
        """Get clinical protocols.

        Args:
            condition: Filter by condition
            treatment_type: Filter by treatment type
            evidence_level: Minimum evidence level
            approved_only: Only approved protocols

        Returns:
            List of matching protocols
        """
        # Mock protocol database
        protocols = [
            {
                "id": "protocol_001",
                "name": "TMS for Treatment-Resistant Depression",
                "condition": "Depression",
                "treatment_type": "neurostimulation",
                "evidence_level": "A",
                "approved": True,
                "description": "High-frequency rTMS to left DLPFC",
                "sessions": 30,
                "frequency": "5 sessions/week",
            },
            {
                "id": "protocol_002",
                "name": "Neurofeedback for ADHD",
                "condition": "ADHD",
                "treatment_type": "neurofeedback",
                "evidence_level": "B",
                "approved": True,
                "description": "Theta/beta ratio training",
                "sessions": 40,
                "frequency": "2 sessions/week",
            },
            {
                "id": "protocol_003",
                "name": "tDCS for Chronic Pain",
                "condition": "Chronic Pain",
                "treatment_type": "neurostimulation",
                "evidence_level": "B",
                "approved": True,
                "description": "Anodal stimulation over M1",
                "sessions": 20,
                "frequency": "3 sessions/week",
            },
        ]

        # Filter protocols
        filtered = protocols

        if condition:
            filtered = [
                p for p in filtered if p["condition"].lower() == condition.lower()
            ]

        if treatment_type:
            filtered = [p for p in filtered if p["treatment_type"] == treatment_type]

        if evidence_level:
            # Filter by minimum evidence level
            level_order = {"A": 4, "B": 3, "C": 2, "D": 1, "experimental": 0}
            min_level = level_order.get(evidence_level, 0)
            filtered = [
                p
                for p in filtered
                if level_order.get(p["evidence_level"], 0) >= min_level
            ]

        if approved_only:
            filtered = [p for p in filtered if p["approved"]]

        return {
            "protocols": filtered,
            "total_count": len(filtered),
            "filters_applied": {
                "condition": condition,
                "treatment_type": treatment_type,
                "evidence_level": evidence_level,
                "approved_only": approved_only,
            },
        }

    async def check_treatment_compliance(
        self,
        patient_id: str,
        treatment_plan_id: Optional[str] = None,
        time_period: str = "month",
    ) -> Dict[str, Any]:
        """Check treatment compliance.

        Args:
            patient_id: Patient identifier
            treatment_plan_id: Specific treatment plan
            time_period: Time period to check

        Returns:
            Compliance data
        """
        if patient_id not in self._mock_patients:
            raise ValueError(f"Patient not found: {patient_id}")

        # Get treatment plans
        if treatment_plan_id:
            plans = [self._mock_treatment_plans.get(treatment_plan_id)]
            plans = [p for p in plans if p]  # Remove None
        else:
            plans = [
                p
                for p in self._mock_treatment_plans.values()
                if p["patient_id"] == patient_id
            ]

        compliance_data = {
            "patient_id": patient_id,
            "time_period": time_period,
            "treatment_plans": [],
            "overall_compliance": 0,
        }

        for plan in plans:
            # Calculate expected vs actual sessions
            weeks_elapsed = (
                datetime.utcnow() - datetime.fromisoformat(plan["start_date"])
            ).days / 7
            expected_sessions = min(
                int(weeks_elapsed * plan["protocol"]["sessions_per_week"]),
                plan["sessions_scheduled"],
            )
            actual_sessions = plan["sessions_completed"]

            compliance_rate = (
                (actual_sessions / expected_sessions * 100)
                if expected_sessions > 0
                else 100
            )

            plan_compliance = {
                "treatment_plan_id": plan["id"],
                "treatment_type": plan["treatment_type"],
                "expected_sessions": expected_sessions,
                "completed_sessions": actual_sessions,
                "missed_sessions": max(0, expected_sessions - actual_sessions),
                "compliance_rate": round(compliance_rate, 1),
                "status": "on_track" if compliance_rate >= 80 else "at_risk",
            }

            compliance_data["treatment_plans"].append(plan_compliance)

        # Calculate overall compliance
        if compliance_data["treatment_plans"]:
            overall_rates = [
                p["compliance_rate"] for p in compliance_data["treatment_plans"]
            ]
            compliance_data["overall_compliance"] = round(
                sum(overall_rates) / len(overall_rates), 1
            )

        return compliance_data

    async def report_adverse_event(
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
        """Report adverse event.

        Args:
            patient_id: Patient identifier
            event_date: Date of event
            event_description: Event description
            severity: Event severity
            reported_by: Reporter
            treatment_related: Related to treatment
            action_taken: Action taken
            outcome: Event outcome

        Returns:
            Adverse event report confirmation
        """
        if patient_id not in self._mock_patients:
            raise ValueError(f"Patient not found: {patient_id}")

        event_id = f"ae_{len(self._mock_adverse_events) + 1:04d}"

        adverse_event = {
            "id": event_id,
            "patient_id": patient_id,
            "event_date": event_date,
            "event_description": event_description,
            "severity": severity,
            "reported_by": reported_by,
            "treatment_related": treatment_related,
            "action_taken": action_taken,
            "outcome": outcome or "ongoing",
            "reported_date": datetime.utcnow().isoformat(),
            "status": "reported",
        }

        self._mock_adverse_events.append(adverse_event)

        # Determine if immediate action needed
        requires_immediate_action = severity in ["severe", "life_threatening"]

        return {
            "event_id": event_id,
            "patient_id": patient_id,
            "severity": severity,
            "status": "reported",
            "requires_immediate_action": requires_immediate_action,
            "notification_sent": requires_immediate_action,
            "message": (
                "Adverse event reported. Immediate action required!"
                if requires_immediate_action
                else "Adverse event recorded successfully"
            ),
        }

    def _calculate_outcome_summary(
        self, patient_id: str, date_range: Dict[str, str]
    ) -> Dict[str, Any]:
        """Calculate outcome summary for patient.

        Args:
            patient_id: Patient identifier
            date_range: Date range for calculation

        Returns:
            Outcome summary data
        """
        start_date = datetime.fromisoformat(date_range["start_date"])
        end_date = datetime.fromisoformat(date_range["end_date"])

        # Get outcomes in date range
        patient_outcomes = [
            o
            for o in self._mock_outcomes.values()
            if o.get("patient_id") == patient_id
            and start_date <= datetime.fromisoformat(o["assessment_date"]) <= end_date
        ]

        if not patient_outcomes:
            return {"message": "No outcome data available for this period"}

        # Group by assessment type
        by_type = {}
        for outcome in patient_outcomes:
            assessment_type = outcome["assessment_type"]
            if assessment_type not in by_type:
                by_type[assessment_type] = []
            by_type[assessment_type].append(outcome)

        # Calculate trends
        summary = {}
        for assessment_type, outcomes in by_type.items():
            outcomes_sorted = sorted(outcomes, key=lambda x: x["assessment_date"])

            first_score = sum(outcomes_sorted[0]["scores"].values())
            last_score = sum(outcomes_sorted[-1]["scores"].values())
            change = last_score - first_score
            change_percent = (change / first_score * 100) if first_score != 0 else 0

            summary[assessment_type] = {
                "assessments_count": len(outcomes),
                "first_score": first_score,
                "last_score": last_score,
                "change": change,
                "change_percent": round(change_percent, 1),
                "trend": (
                    "improving" if change < 0 else "worsening"
                ),  # Lower scores usually indicate improvement
                "latest_severity": outcomes_sorted[-1].get("severity", "unknown"),
            }

        return summary
