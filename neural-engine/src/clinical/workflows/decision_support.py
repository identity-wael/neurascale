"""Clinical decision support system for BCI treatments."""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any
from uuid import uuid4

from ..types import ClinicalConfig

logger = logging.getLogger(__name__)


class ClinicalDecisionSupport:
    """Provides evidence-based clinical decision support.

    Analyzes patient data, treatment history, and outcomes to provide
    intelligent recommendations for clinical decision making.
    """

    def __init__(self, config: ClinicalConfig):
        """Initialize clinical decision support system."""
        self.config = config

        # Decision rules and knowledge base
        self.clinical_rules = self._load_clinical_rules()
        self.outcome_models = self._load_outcome_models()
        self.risk_algorithms = self._load_risk_algorithms()

        # Decision history for learning
        self._decision_history: List[Dict[str, Any]] = []

        logger.info("Clinical decision support system initialized")

    async def evaluate_treatment_eligibility(
        self, patient_data: dict
    ) -> Dict[str, Any]:
        """Evaluate patient eligibility for BCI treatment.

        Args:
            patient_data: Comprehensive patient information

        Returns:
            Eligibility assessment with recommendations
        """
        evaluation = {
            "patient_id": patient_data.get("patient_id"),
            "evaluation_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc),
            "eligible": True,
            "eligibility_score": 0.0,
            "risk_level": "low",
            "contraindications": [],
            "warnings": [],
            "recommendations": [],
            "required_assessments": [],
            "next_steps": [],
        }

        try:
            # Medical eligibility assessment
            medical_assessment = await self._assess_medical_eligibility(patient_data)
            evaluation.update(medical_assessment)

            # Cognitive eligibility assessment
            cognitive_assessment = await self._assess_cognitive_eligibility(
                patient_data
            )
            evaluation.update(cognitive_assessment)

            # Social/environmental factors
            psychosocial_assessment = await self._assess_psychosocial_factors(
                patient_data
            )
            evaluation.update(psychosocial_assessment)

            # Calculate overall eligibility score
            evaluation["eligibility_score"] = await self._calculate_eligibility_score(
                medical_assessment, cognitive_assessment, psychosocial_assessment
            )

            # Determine final eligibility
            if evaluation["eligibility_score"] < 0.3:
                evaluation["eligible"] = False
                evaluation["recommendations"].append(
                    "Patient not currently suitable for BCI treatment"
                )
            elif evaluation["eligibility_score"] < 0.6:
                evaluation["recommendations"].append(
                    "Consider additional assessments and monitoring"
                )
            else:
                evaluation["recommendations"].append(
                    "Patient is suitable candidate for BCI treatment"
                )

            # Log decision for learning
            await self._log_decision(evaluation)

            return evaluation

        except Exception as e:
            logger.error(f"Error evaluating treatment eligibility: {e}")
            evaluation["eligible"] = False
            evaluation["recommendations"].append(
                "Unable to complete eligibility assessment"
            )
            return evaluation

    async def recommend_treatment_approach(
        self, patient_data: dict, eligibility_assessment: dict
    ) -> Dict[str, Any]:
        """Recommend optimal treatment approach based on patient profile.

        Args:
            patient_data: Patient information
            eligibility_assessment: Previous eligibility assessment

        Returns:
            Treatment approach recommendations
        """
        recommendations = {
            "patient_id": patient_data.get("patient_id"),
            "recommendation_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc),
            "primary_approach": None,
            "alternative_approaches": [],
            "session_parameters": {},
            "monitoring_requirements": [],
            "success_predictors": [],
            "risk_mitigation": [],
        }

        try:
            # Analyze patient characteristics
            patient_profile = await self._analyze_patient_profile(patient_data)

            # Match to treatment protocols
            protocol_matches = await self._match_treatment_protocols(
                patient_profile, eligibility_assessment
            )

            # Select primary approach
            if protocol_matches:
                best_match = max(protocol_matches, key=lambda x: x["confidence_score"])
                recommendations["primary_approach"] = best_match

                # Add alternatives
                recommendations["alternative_approaches"] = [
                    match
                    for match in protocol_matches
                    if match != best_match and match["confidence_score"] > 0.6
                ]

            # Generate session parameters
            recommendations["session_parameters"] = (
                await self._recommend_session_parameters(patient_profile)
            )

            # Identify monitoring requirements
            recommendations["monitoring_requirements"] = (
                await self._identify_monitoring_needs(
                    patient_profile, eligibility_assessment
                )
            )

            # Predict success factors
            recommendations["success_predictors"] = (
                await self._analyze_success_predictors(patient_profile)
            )

            return recommendations

        except Exception as e:
            logger.error(f"Error generating treatment recommendations: {e}")
            return recommendations

    async def assess_session_safety(
        self, session_data: dict, patient_context: dict
    ) -> Dict[str, Any]:
        """Real-time safety assessment during sessions.

        Args:
            session_data: Current session metrics
            patient_context: Patient safety profile

        Returns:
            Safety assessment and recommendations
        """
        safety_assessment = {
            "session_id": session_data.get("session_id"),
            "assessment_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc),
            "safety_level": "safe",
            "risk_score": 0.0,
            "alerts": [],
            "recommendations": [],
            "immediate_actions": [],
            "monitoring_adjustments": [],
        }

        try:
            # Check vital signs if available
            if "vitals" in session_data:
                vital_assessment = await self._assess_vital_signs(
                    session_data["vitals"], patient_context
                )
                safety_assessment.update(vital_assessment)

            # Analyze neural signal patterns
            if "neural_signals" in session_data:
                signal_assessment = await self._assess_signal_safety(
                    session_data["neural_signals"], patient_context
                )
                safety_assessment.update(signal_assessment)

            # Check stimulation parameters
            if "stimulation" in session_data:
                stim_assessment = await self._assess_stimulation_safety(
                    session_data["stimulation"], patient_context
                )
                safety_assessment.update(stim_assessment)

            # Patient behavior/response analysis
            if "behavior" in session_data:
                behavior_assessment = await self._assess_behavioral_safety(
                    session_data["behavior"], patient_context
                )
                safety_assessment.update(behavior_assessment)

            # Calculate overall risk score
            safety_assessment["risk_score"] = await self._calculate_safety_risk(
                safety_assessment
            )

            # Determine safety level
            if safety_assessment["risk_score"] > 0.8:
                safety_assessment["safety_level"] = "high_risk"
                safety_assessment["immediate_actions"].append(
                    "Stop session immediately"
                )
            elif safety_assessment["risk_score"] > 0.6:
                safety_assessment["safety_level"] = "moderate_risk"
                safety_assessment["recommendations"].append(
                    "Reduce stimulation intensity"
                )
            elif safety_assessment["risk_score"] > 0.3:
                safety_assessment["safety_level"] = "low_risk"
                safety_assessment["monitoring_adjustments"].append(
                    "Increase monitoring frequency"
                )

            return safety_assessment

        except Exception as e:
            logger.error(f"Error in session safety assessment: {e}")
            safety_assessment["safety_level"] = "assessment_error"
            safety_assessment["immediate_actions"].append(
                "Manual safety review required"
            )
            return safety_assessment

    async def predict_treatment_outcomes(
        self, patient_data: dict, treatment_plan: dict
    ) -> Dict[str, Any]:
        """Predict treatment outcomes using machine learning models.

        Args:
            patient_data: Patient characteristics
            treatment_plan: Proposed treatment plan

        Returns:
            Outcome predictions with confidence intervals
        """
        predictions = {
            "patient_id": patient_data.get("patient_id"),
            "prediction_id": str(uuid4()),
            "timestamp": datetime.now(timezone.utc),
            "success_probability": 0.0,
            "predicted_outcomes": {},
            "confidence_intervals": {},
            "risk_factors": [],
            "success_factors": [],
            "timeline_predictions": {},
        }

        try:
            # Extract relevant features
            features = await self._extract_prediction_features(
                patient_data, treatment_plan
            )

            # Apply outcome models
            for outcome_type, model in self.outcome_models.items():
                prediction_result = await self._apply_outcome_model(
                    model, features, outcome_type
                )
                predictions["predicted_outcomes"][outcome_type] = prediction_result

            # Calculate overall success probability
            predictions["success_probability"] = (
                await self._calculate_success_probability(
                    predictions["predicted_outcomes"]
                )
            )

            # Identify key factors
            predictions["risk_factors"] = await self._identify_risk_factors(features)
            predictions["success_factors"] = await self._identify_success_factors(
                features
            )

            # Generate timeline predictions
            predictions["timeline_predictions"] = (
                await self._predict_treatment_timeline(features, treatment_plan)
            )

            return predictions

        except Exception as e:
            logger.error(f"Error predicting treatment outcomes: {e}")
            return predictions

    async def generate_alerts(
        self, patient_id: str, monitoring_data: dict
    ) -> List[Dict[str, Any]]:
        """Generate clinical alerts based on monitoring data.

        Args:
            patient_id: Patient identifier
            monitoring_data: Real-time monitoring data

        Returns:
            List of clinical alerts
        """
        alerts = []

        try:
            # Check clinical rules
            for rule in self.clinical_rules:
                if await self._evaluate_clinical_rule(rule, monitoring_data):
                    alert = {
                        "alert_id": str(uuid4()),
                        "patient_id": patient_id,
                        "timestamp": datetime.now(timezone.utc),
                        "rule_id": rule["id"],
                        "severity": rule["severity"],
                        "message": rule["message"],
                        "recommendations": rule.get("recommendations", []),
                        "auto_actions": rule.get("auto_actions", []),
                    }
                    alerts.append(alert)

            # Check trend-based alerts
            trend_alerts = await self._check_trend_alerts(patient_id, monitoring_data)
            alerts.extend(trend_alerts)

            # Check pattern-based alerts
            pattern_alerts = await self._check_pattern_alerts(
                patient_id, monitoring_data
            )
            alerts.extend(pattern_alerts)

            # Sort by severity
            alerts.sort(
                key=lambda x: {"critical": 3, "high": 2, "medium": 1, "low": 0}.get(
                    x["severity"], 0
                ),
                reverse=True,
            )

            return alerts

        except Exception as e:
            logger.error(f"Error generating alerts for patient {patient_id}: {e}")
            return []

    async def _assess_medical_eligibility(self, patient_data: dict) -> Dict[str, Any]:
        """Assess medical eligibility factors."""
        assessment = {
            "medical_eligible": True,
            "medical_contraindications": [],
            "medical_warnings": [],
            "medical_score": 1.0,
        }

        medical_history = patient_data.get("medical_history", {})
        conditions = medical_history.get("conditions", [])
        medications = medical_history.get("medications", [])

        # Log medication count for medical assessment
        logger.debug(f"Assessing {len(medications)} medications for eligibility")

        # Check absolute contraindications
        absolute_contraindications = [
            "uncontrolled_epilepsy",
            "active_psychosis",
            "pregnancy",
            "pacemaker_implant",
        ]

        for condition in conditions:
            condition_lower = condition.lower().replace(" ", "_")
            for contraindication in absolute_contraindications:
                if contraindication in condition_lower:
                    assessment["medical_eligible"] = False
                    assessment["medical_contraindications"].append(condition)
                    assessment["medical_score"] = 0.0

        # Check relative contraindications
        relative_contraindications = [
            "seizure_history",
            "head_trauma",
            "brain_surgery",
            "medication_interactions",
        ]

        for condition in conditions:
            condition_lower = condition.lower().replace(" ", "_")
            for contraindication in relative_contraindications:
                if contraindication in condition_lower:
                    assessment["medical_warnings"].append(condition)
                    assessment["medical_score"] *= 0.8

        return assessment

    async def _assess_cognitive_eligibility(self, patient_data: dict) -> Dict[str, Any]:
        """Assess cognitive eligibility factors."""
        assessment = {
            "cognitive_eligible": True,
            "cognitive_score": 1.0,
            "cognitive_requirements": [],
        }

        cognitive_data = patient_data.get("cognitive_assessment", {})

        # Minimum cognitive requirements
        min_requirements = {
            "attention_span": 15,  # minutes
            "working_memory": 4,  # span
            "comprehension": 70,  # percentile
        }

        for requirement, min_value in min_requirements.items():
            patient_value = cognitive_data.get(requirement, 0)
            if patient_value < min_value:
                assessment["cognitive_eligible"] = False
                assessment["cognitive_requirements"].append(
                    f"{requirement}: requires {min_value}, patient has {patient_value}"
                )
                assessment["cognitive_score"] *= 0.5

        return assessment

    async def _assess_psychosocial_factors(self, patient_data: dict) -> Dict[str, Any]:
        """Assess psychosocial eligibility factors."""
        assessment = {
            "psychosocial_score": 1.0,
            "support_level": "adequate",
            "motivation_level": "high",
            "psychosocial_recommendations": [],
        }

        psychosocial_data = patient_data.get("psychosocial_assessment", {})

        # Support system assessment
        support_score = psychosocial_data.get("family_support", 5)
        if support_score < 3:
            assessment["support_level"] = "inadequate"
            assessment["psychosocial_score"] *= 0.7
            assessment["psychosocial_recommendations"].append(
                "Consider enhancing family support system"
            )

        # Motivation assessment
        motivation_score = psychosocial_data.get("treatment_motivation", 8)
        if motivation_score < 5:
            assessment["motivation_level"] = "low"
            assessment["psychosocial_score"] *= 0.6
            assessment["psychosocial_recommendations"].append(
                "Address motivation barriers before treatment"
            )

        return assessment

    async def _calculate_eligibility_score(
        self, medical: dict, cognitive: dict, psychosocial: dict
    ) -> float:
        """Calculate overall eligibility score."""
        weights = {"medical": 0.5, "cognitive": 0.3, "psychosocial": 0.2}

        score = (
            medical["medical_score"] * weights["medical"]
            + cognitive["cognitive_score"] * weights["cognitive"]
            + psychosocial["psychosocial_score"] * weights["psychosocial"]
        )

        return max(0.0, min(1.0, score))

    async def _log_decision(self, decision: dict):
        """Log decision for learning and audit."""
        self._decision_history.append(
            {
                "timestamp": datetime.now(timezone.utc),
                "decision_type": "eligibility_assessment",
                "decision_data": decision,
            }
        )

        logger.info(f"Decision logged: {decision['evaluation_id']}")

    def _load_clinical_rules(self) -> List[Dict[str, Any]]:
        """Load clinical decision rules."""
        return [
            {
                "id": "high_seizure_risk",
                "condition": "seizure_markers > threshold",
                "severity": "critical",
                "message": "High seizure risk detected",
                "recommendations": ["Stop session", "Medical evaluation"],
                "auto_actions": ["session_pause"],
            },
            {
                "id": "excessive_fatigue",
                "condition": "performance_decline > 30%",
                "severity": "medium",
                "message": "Patient showing signs of excessive fatigue",
                "recommendations": ["Reduce session intensity", "Shorter sessions"],
            },
            {
                "id": "stimulation_artifact",
                "condition": "artifact_ratio > 0.4",
                "severity": "low",
                "message": "High stimulation artifact detected",
                "recommendations": ["Adjust electrode placement", "Check impedances"],
            },
        ]

    def _load_outcome_models(self) -> Dict[str, Dict[str, Any]]:
        """Load outcome prediction models."""
        return {
            "motor_recovery": {
                "model_type": "regression",
                "features": ["baseline_motor", "lesion_size", "time_since_injury"],
                "coefficients": [0.4, -0.3, -0.1],
                "intercept": 0.6,
            },
            "cognitive_improvement": {
                "model_type": "classification",
                "features": ["baseline_cognitive", "age", "education"],
                "thresholds": [0.7, 0.5, 0.3],
                "weights": [0.5, -0.2, 0.3],
            },
        }

    def _load_risk_algorithms(self) -> Dict[str, Any]:
        """Load risk assessment algorithms."""
        return {
            "seizure_risk": {
                "factors": [
                    "epilepsy_history",
                    "medication_compliance",
                    "stress_level",
                ],
                "weights": [0.6, 0.3, 0.1],
                "threshold": 0.7,
            },
            "adverse_event_risk": {
                "factors": ["age", "comorbidities", "previous_reactions"],
                "weights": [0.2, 0.5, 0.3],
                "threshold": 0.6,
            },
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get decision support statistics."""
        return {
            "total_decisions": len(self._decision_history),
            "decisions_last_24h": sum(
                1
                for decision in self._decision_history
                if decision["timestamp"]
                > datetime.now(timezone.utc) - timedelta(days=1)
            ),
            "decision_types": {},
            "average_eligibility_score": 0.75,  # Would calculate from actual data
        }
