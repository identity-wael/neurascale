"""Medical history management for clinical workflows."""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Any

from ..types import MedicalHistory, ClinicalConfig

logger = logging.getLogger(__name__)


class MedicalHistoryManager:
    """Manages patient medical history and clinical assessments.

    Handles comprehensive medical history tracking, contraindication
    monitoring, and clinical assessment integration.
    """

    def __init__(self, config: ClinicalConfig):
        """Initialize medical history manager."""
        self.config = config

        # Clinical assessment templates
        self.assessment_templates = self._load_assessment_templates()

        logger.info("Medical history manager initialized")

    async def record_medical_history(
        self, patient_id: str, history: dict
    ) -> MedicalHistory:
        """Record comprehensive medical history for patient.

        Args:
            patient_id: Patient identifier
            history: Medical history data

        Returns:
            Created MedicalHistory record
        """
        try:
            # Validate and normalize history data
            normalized_history = self._normalize_history_data(history)

            # Create medical history record
            medical_history = MedicalHistory(
                conditions=normalized_history.get("conditions", []),
                medications=normalized_history.get("medications", []),
                allergies=normalized_history.get("allergies", []),
                contraindications=normalized_history.get("contraindications", []),
                previous_bci_experience=normalized_history.get(
                    "previous_bci_experience", False
                ),
                neurological_conditions=normalized_history.get(
                    "neurological_conditions", []
                ),
                last_updated=datetime.now(timezone.utc),
            )

            # Validate medical history for BCI eligibility
            validation_result = await self._validate_bci_eligibility(medical_history)

            if validation_result["has_contraindications"]:
                logger.warning(
                    f"BCI contraindications found for patient {patient_id}: {validation_result['contraindications']}"
                )

            logger.info(f"Medical history recorded for patient {patient_id}")

            return medical_history

        except Exception as e:
            logger.error(
                f"Failed to record medical history for patient {patient_id}: {e}"
            )
            raise

    async def update_clinical_assessments(
        self, patient_id: str, assessment: dict
    ) -> Dict[str, Any]:
        """Update clinical assessments and evaluations.

        Args:
            patient_id: Patient identifier
            assessment: Assessment data

        Returns:
            Assessment summary
        """
        try:
            assessment_record = {
                "patient_id": patient_id,
                "assessment_date": datetime.now(timezone.utc),
                "assessment_type": assessment.get("type", "general"),
                "conducted_by": assessment.get("conducted_by", ""),
                "scores": assessment.get("scores", {}),
                "observations": assessment.get("observations", ""),
                "recommendations": assessment.get("recommendations", []),
                "follow_up_required": assessment.get("follow_up_required", False),
                "next_assessment_date": assessment.get("next_assessment_date"),
            }

            # Validate assessment scores
            validation_result = self._validate_assessment_scores(assessment_record)

            if not validation_result["valid"]:
                logger.warning(
                    f"Assessment validation failed for patient {patient_id}: {validation_result['errors']}"
                )

            # Calculate assessment summary
            summary = self._calculate_assessment_summary(assessment_record)

            logger.info(f"Clinical assessment updated for patient {patient_id}")

            return {
                "assessment_record": assessment_record,
                "validation": validation_result,
                "summary": summary,
            }

        except Exception as e:
            logger.error(
                f"Failed to update clinical assessment for patient {patient_id}: {e}"
            )
            raise

    async def track_contraindications(
        self, patient_id: str, contraindications: List[str]
    ) -> Dict[str, Any]:
        """Track and monitor patient contraindications.

        Args:
            patient_id: Patient identifier
            contraindications: List of contraindications

        Returns:
            Contraindication tracking result
        """
        # Categorize contraindications by severity
        contraindication_categories = {"absolute": [], "relative": [], "temporary": []}

        # Clinical contraindications database (would be externalized)
        contraindication_db = {
            "active_psychosis": {"category": "absolute", "reason": "Safety risk"},
            "uncontrolled_epilepsy": {
                "category": "absolute",
                "reason": "Neurological interference",
            },
            "severe_depression": {
                "category": "relative",
                "reason": "Treatment effectiveness",
            },
            "recent_head_injury": {
                "category": "temporary",
                "reason": "Healing period required",
            },
            "pregnancy": {"category": "absolute", "reason": "Unknown fetal effects"},
            "pacemaker": {"category": "absolute", "reason": "Device interaction risk"},
            "metal_implants": {"category": "relative", "reason": "Signal interference"},
            "cognitive_impairment": {
                "category": "relative",
                "reason": "Consent capacity",
            },
        }

        for contraindication in contraindications:
            contraindication_info = contraindication_db.get(contraindication.lower())
            if contraindication_info:
                category = contraindication_info["category"]
                contraindication_categories[category].append(
                    {
                        "contraindication": contraindication,
                        "reason": contraindication_info["reason"],
                    }
                )

        # Determine overall eligibility
        has_absolute = len(contraindication_categories["absolute"]) > 0
        eligibility_status = (
            "ineligible" if has_absolute else "eligible_with_conditions"
        )

        tracking_result = {
            "patient_id": patient_id,
            "assessment_date": datetime.now(timezone.utc),
            "contraindications": contraindication_categories,
            "eligibility_status": eligibility_status,
            "recommendations": self._generate_contraindication_recommendations(
                contraindication_categories
            ),
            "monitoring_required": len(contraindication_categories["relative"]) > 0
            or len(contraindication_categories["temporary"]) > 0,
        }

        logger.info(
            f"Contraindications tracked for patient {patient_id}: {eligibility_status}"
        )

        return tracking_result

    async def generate_clinical_summary(self, patient_id: str) -> Dict[str, Any]:
        """Generate comprehensive clinical summary for patient.

        Args:
            patient_id: Patient identifier

        Returns:
            Clinical summary report
        """
        # In production, this would query patient data from database
        # For now, return a structured summary template

        summary = {
            "patient_id": patient_id,
            "generated_date": datetime.now(timezone.utc),
            "summary_type": "comprehensive",
            "sections": {
                "demographics": {"completed": True, "notes": "Demographics on file"},
                "medical_history": {
                    "completed": True,
                    "key_conditions": [],
                    "risk_factors": [],
                    "notes": "Medical history documented",
                },
                "medications": {
                    "completed": True,
                    "current_medications": [],
                    "drug_interactions": [],
                    "notes": "Medication list current",
                },
                "assessments": {
                    "baseline_completed": False,
                    "recent_scores": {},
                    "trends": {},
                    "notes": "Baseline assessment pending",
                },
                "contraindications": {
                    "absolute": [],
                    "relative": [],
                    "temporary": [],
                    "overall_eligibility": "pending_review",
                },
                "care_plan": {
                    "treatment_goals": [],
                    "planned_interventions": [],
                    "monitoring_requirements": [],
                    "notes": "Care plan to be developed",
                },
            },
            "clinical_recommendations": [
                "Complete baseline neuropsychological assessment",
                "Verify current medication list",
                "Obtain clearance from primary care physician",
                "Schedule pre-treatment consultation",
            ],
            "generated_by": "system",
            "next_review_date": datetime.now(timezone.utc),
        }

        return summary

    def _normalize_history_data(self, history: dict) -> dict:
        """Normalize and validate medical history data."""
        normalized = {}

        normalized["conditions"] = self._normalize_conditions(
            history.get("conditions", [])
        )
        normalized["medications"] = self._normalize_medications(
            history.get("medications", [])
        )
        normalized["allergies"] = self._normalize_allergies(
            history.get("allergies", [])
        )
        normalized["contraindications"] = history.get("contraindications", [])
        normalized["previous_bci_experience"] = history.get(
            "previous_bci_experience", False
        )
        normalized["neurological_conditions"] = history.get(
            "neurological_conditions", []
        )

        return normalized

    def _normalize_conditions(self, conditions) -> List[str]:
        """Normalize conditions field."""
        if isinstance(conditions, str):
            return [c.strip() for c in conditions.split(",")]
        elif isinstance(conditions, list):
            return [str(c).strip() for c in conditions]
        return []

    def _normalize_medications(self, medications) -> List[dict]:
        """Normalize medications field."""
        if not isinstance(medications, list):
            return []

        normalized = []
        for med in medications:
            if isinstance(med, str):
                normalized.append(
                    {
                        "name": med,
                        "dosage": "",
                        "frequency": "",
                        "start_date": None,
                        "prescriber": "",
                    }
                )
            elif isinstance(med, dict):
                normalized.append(med)
        return normalized

    def _normalize_allergies(self, allergies) -> List[str]:
        """Normalize allergies field."""
        if isinstance(allergies, str):
            return [a.strip() for a in allergies.split(",")]
        elif isinstance(allergies, list):
            return [str(a).strip() for a in allergies]
        return []

    async def _validate_bci_eligibility(
        self, medical_history: MedicalHistory
    ) -> Dict[str, Any]:
        """Validate medical history for BCI treatment eligibility."""
        validation_result = {
            "eligible": True,
            "has_contraindications": False,
            "contraindications": [],
            "warnings": [],
            "recommendations": [],
        }

        # Check for absolute contraindications
        absolute_contraindications = [
            "active_psychosis",
            "uncontrolled_epilepsy",
            "pregnancy",
            "pacemaker",
        ]

        for condition in medical_history.conditions:
            condition_lower = condition.lower()
            for contraindication in absolute_contraindications:
                if contraindication in condition_lower:
                    validation_result["eligible"] = False
                    validation_result["has_contraindications"] = True
                    validation_result["contraindications"].append(contraindication)

        # Check medications for interactions
        for medication in medical_history.medications:
            med_name = medication.get("name", "").lower()
            if "anticoagulant" in med_name or "warfarin" in med_name:
                validation_result["warnings"].append(
                    "Anticoagulant medication - monitor for bleeding risk"
                )

        return validation_result

    def _validate_assessment_scores(self, assessment: dict) -> Dict[str, Any]:
        """Validate clinical assessment scores."""
        validation_result = {"valid": True, "errors": [], "warnings": []}

        scores = assessment.get("scores", {})
        assessment_type = assessment.get("assessment_type", "")

        # Validate score ranges based on assessment type
        if assessment_type == "cognitive":
            for score_name, score_value in scores.items():
                if not isinstance(score_value, (int, float)):
                    validation_result["valid"] = False
                    validation_result["errors"].append(
                        f"Invalid score type for {score_name}"
                    )
                elif score_value < 0 or score_value > 100:
                    validation_result["warnings"].append(
                        f"Score {score_name} outside normal range"
                    )

        return validation_result

    def _calculate_assessment_summary(self, assessment: dict) -> Dict[str, Any]:
        """Calculate assessment summary and trends."""
        scores = assessment.get("scores", {})

        if not scores:
            return {"status": "no_scores", "summary": "No scores available"}

        # Calculate basic statistics
        score_values = [v for v in scores.values() if isinstance(v, (int, float))]

        if score_values:
            summary = {
                "status": "complete",
                "total_scores": len(score_values),
                "average_score": sum(score_values) / len(score_values),
                "min_score": min(score_values),
                "max_score": max(score_values),
                "score_range": max(score_values) - min(score_values),
            }
        else:
            summary = {"status": "invalid_scores", "summary": "No valid scores found"}

        return summary

    def _generate_contraindication_recommendations(
        self, contraindications: dict
    ) -> List[str]:
        """Generate clinical recommendations based on contraindications."""
        recommendations = []

        if contraindications["absolute"]:
            recommendations.append(
                "Patient is not eligible for BCI treatment due to absolute contraindications"
            )
            recommendations.append("Consider alternative treatment options")

        if contraindications["relative"]:
            recommendations.append(
                "Enhanced monitoring required due to relative contraindications"
            )
            recommendations.append("Consider modified treatment protocol")

        if contraindications["temporary"]:
            recommendations.append(
                "Reassess eligibility after temporary contraindications resolve"
            )
            recommendations.append("Establish follow-up timeline for reassessment")

        if not any(contraindications.values()):
            recommendations.append("No significant contraindications identified")
            recommendations.append("Patient may be suitable for standard BCI protocol")

        return recommendations

    def _load_assessment_templates(self) -> Dict[str, Any]:
        """Load clinical assessment templates."""
        # In production, this would load from database or configuration files
        return {
            "cognitive": {
                "domains": ["attention", "memory", "executive_function", "language"],
                "score_ranges": {"min": 0, "max": 100},
                "normal_ranges": {"min": 85, "max": 115},
            },
            "neuropsychological": {
                "domains": ["mood", "anxiety", "motivation", "coping"],
                "score_ranges": {"min": 0, "max": 50},
                "normal_ranges": {"min": 10, "max": 30},
            },
            "functional": {
                "domains": ["mobility", "self_care", "communication", "social"],
                "score_ranges": {"min": 0, "max": 10},
                "normal_ranges": {"min": 7, "max": 10},
            },
        }
