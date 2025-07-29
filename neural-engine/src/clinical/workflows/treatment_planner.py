"""Treatment planning and protocol management for clinical BCI workflows."""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any
from uuid import uuid4

from ..types import (
    TreatmentPlan,
    SessionType,
    TreatmentGoal,
    ProtocolStep,
    ClinicalConfig,
)

logger = logging.getLogger(__name__)


class TreatmentPlanner:
    """Manages treatment planning and protocol orchestration.

    Creates personalized treatment plans based on patient assessments,
    manages protocol execution, and tracks treatment progress.
    """

    def __init__(self, config: ClinicalConfig):
        """Initialize treatment planner."""
        self.config = config

        # Treatment storage (would be database in production)
        self._treatment_plans: Dict[str, TreatmentPlan] = {}
        self._protocol_templates = self._load_protocol_templates()
        self._treatment_algorithms = self._load_treatment_algorithms()

        logger.info("Treatment planner initialized")

    async def create_treatment_plan(
        self, patient_id: str, assessment_data: dict
    ) -> TreatmentPlan:
        """Create personalized treatment plan based on patient assessment.

        Args:
            patient_id: Patient identifier
            assessment_data: Clinical assessment results

        Returns:
            Created TreatmentPlan
        """
        try:
            # Analyze assessment data
            assessment_analysis = await self._analyze_assessment_data(assessment_data)

            # Determine optimal treatment approach
            treatment_approach = await self._determine_treatment_approach(
                patient_id, assessment_analysis
            )

            # Generate treatment goals
            treatment_goals = await self._generate_treatment_goals(
                assessment_analysis, treatment_approach
            )

            # Create protocol steps
            protocol_steps = await self._create_protocol_steps(
                treatment_approach, treatment_goals
            )

            # Estimate timeline and milestones
            timeline = self._calculate_treatment_timeline(protocol_steps)

            # Create treatment plan
            plan_id = str(uuid4())
            treatment_plan = TreatmentPlan(
                plan_id=plan_id,
                patient_id=patient_id,
                created_by="treatment_planner",
                treatment_goals=treatment_goals,
                protocol_steps=protocol_steps,
                estimated_duration_weeks=timeline["total_weeks"],
                target_outcomes=assessment_analysis.get("target_outcomes", []),
                contraindications=assessment_analysis.get("contraindications", []),
                special_considerations=assessment_analysis.get("considerations", []),
            )

            # Store treatment plan
            self._treatment_plans[plan_id] = treatment_plan

            logger.info(f"Treatment plan created for patient {patient_id}: {plan_id}")

            return treatment_plan

        except Exception as e:
            logger.error(
                f"Failed to create treatment plan for patient {patient_id}: {e}"
            )
            raise

    async def update_treatment_plan(self, plan_id: str, updates: dict) -> TreatmentPlan:
        """Update existing treatment plan.

        Args:
            plan_id: Treatment plan identifier
            updates: Updates to apply

        Returns:
            Updated treatment plan
        """
        if plan_id not in self._treatment_plans:
            raise ValueError(f"Treatment plan not found: {plan_id}")

        plan = self._treatment_plans[plan_id]

        try:
            # Update goals if provided
            if "goals" in updates:
                plan.treatment_goals = updates["goals"]

            # Update protocol steps if provided
            if "protocol_steps" in updates:
                plan.protocol_steps = updates["protocol_steps"]

            # Update timeline if protocol changed
            if "protocol_steps" in updates:
                timeline = self._calculate_treatment_timeline(plan.protocol_steps)
                plan.estimated_duration_weeks = timeline["total_weeks"]

            # Update last modified
            plan.last_updated = datetime.now(timezone.utc)

            logger.info(f"Treatment plan updated: {plan_id}")

            return plan

        except Exception as e:
            logger.error(f"Failed to update treatment plan {plan_id}: {e}")
            raise

    async def get_treatment_recommendations(
        self, patient_id: str, current_progress: dict
    ) -> Dict[str, Any]:
        """Generate treatment recommendations based on current progress.

        Args:
            patient_id: Patient identifier
            current_progress: Current treatment progress data

        Returns:
            Treatment recommendations
        """
        # Find patient's treatment plan
        patient_plan = None
        for plan in self._treatment_plans.values():
            if plan.patient_id == patient_id:
                patient_plan = plan
                break

        if not patient_plan:
            return {"error": "No treatment plan found for patient"}

        # Analyze current progress
        progress_analysis = await self._analyze_treatment_progress(
            patient_plan, current_progress
        )

        recommendations = {
            "patient_id": patient_id,
            "plan_id": patient_plan.plan_id,
            "progress_status": progress_analysis["status"],
            "completion_percentage": progress_analysis["completion_percent"],
            "recommendations": [],
            "next_steps": [],
            "adjustments_needed": [],
        }

        # Generate specific recommendations
        if progress_analysis["behind_schedule"]:
            recommendations["recommendations"].append(
                "Consider increasing session frequency or intensity"
            )
            recommendations["adjustments_needed"].append("schedule_adjustment")

        if progress_analysis["exceptional_progress"]:
            recommendations["recommendations"].append(
                "Patient showing excellent progress - consider advancing protocol"
            )
            recommendations["next_steps"].append("protocol_advancement")

        # Safety recommendations
        if progress_analysis["safety_concerns"]:
            recommendations["recommendations"].extend(
                progress_analysis["safety_recommendations"]
            )

        return recommendations

    async def optimize_treatment_protocol(
        self, plan_id: str, performance_data: dict
    ) -> Dict[str, Any]:
        """Optimize treatment protocol based on performance data.

        Args:
            plan_id: Treatment plan identifier
            performance_data: Patient performance metrics

        Returns:
            Protocol optimization results
        """
        if plan_id not in self._treatment_plans:
            raise ValueError(f"Treatment plan not found: {plan_id}")

        plan = self._treatment_plans[plan_id]

        # Analyze performance patterns
        performance_analysis = await self._analyze_performance_patterns(
            plan, performance_data
        )

        optimization_results = {
            "plan_id": plan_id,
            "analysis": performance_analysis,
            "optimizations": [],
            "protocol_adjustments": [],
            "expected_improvements": [],
        }

        # Protocol intensity optimization
        if performance_analysis["can_increase_intensity"]:
            optimization_results["optimizations"].append(
                {
                    "type": "intensity_increase",
                    "recommendation": "Increase stimulation intensity by 10%",
                    "expected_benefit": "Improved signal acquisition and faster progress",
                }
            )

        # Session duration optimization
        if performance_analysis["optimal_session_length"]:
            optimal_duration = performance_analysis["optimal_session_length"]
            optimization_results["optimizations"].append(
                {
                    "type": "duration_adjustment",
                    "recommendation": f"Adjust session duration to {optimal_duration} minutes",
                    "expected_benefit": "Maximize learning while preventing fatigue",
                }
            )

        # Frequency optimization
        if performance_analysis["optimal_frequency"]:
            optimal_freq = performance_analysis["optimal_frequency"]
            optimization_results["optimizations"].append(
                {
                    "type": "frequency_adjustment",
                    "recommendation": f"Adjust to {optimal_freq} sessions per week",
                    "expected_benefit": "Optimize skill consolidation and retention",
                }
            )

        return optimization_results

    async def _analyze_assessment_data(self, assessment_data: dict) -> Dict[str, Any]:
        """Analyze patient assessment data for treatment planning."""
        analysis = {
            "severity_level": "moderate",
            "functional_deficits": [],
            "target_outcomes": [],
            "contraindications": [],
            "considerations": [],
            "treatment_readiness": True,
        }

        # Analyze cognitive assessments
        if "cognitive_scores" in assessment_data:
            cognitive_analysis = self._analyze_cognitive_scores(
                assessment_data["cognitive_scores"]
            )
            analysis.update(cognitive_analysis)

        # Analyze motor assessments
        if "motor_scores" in assessment_data:
            motor_analysis = self._analyze_motor_scores(assessment_data["motor_scores"])
            analysis.update(motor_analysis)

        # Check medical history for contraindications
        if "medical_history" in assessment_data:
            contraindications = self._check_treatment_contraindications(
                assessment_data["medical_history"]
            )
            analysis["contraindications"].extend(contraindications)

        return analysis

    async def _determine_treatment_approach(
        self, patient_id: str, assessment_analysis: dict
    ) -> str:
        """Determine optimal treatment approach based on assessment."""
        severity = assessment_analysis.get("severity_level", "moderate")
        deficits = assessment_analysis.get("functional_deficits", [])

        # Algorithm to determine treatment approach
        if severity == "severe" and "motor" in deficits:
            return "intensive_motor_training"
        elif severity == "severe" and "cognitive" in deficits:
            return "cognitive_rehabilitation"
        elif "communication" in deficits:
            return "communication_enhancement"
        elif severity == "mild":
            return "skill_enhancement"
        else:
            return "standard_rehabilitation"

    async def _generate_treatment_goals(
        self, assessment_analysis: dict, treatment_approach: str
    ) -> List[TreatmentGoal]:
        """Generate specific treatment goals."""
        goals = []

        # Create goals based on treatment approach
        goal_templates = self._treatment_algorithms.get(treatment_approach, {}).get(
            "goals", []
        )

        for template in goal_templates:
            goal = TreatmentGoal(
                goal_id=str(uuid4()),
                description=template["description"],
                target_metric=template["metric"],
                target_value=template["target_value"],
                measurement_method=template["measurement"],
                timeline_weeks=template["timeline"],
                priority=template.get("priority", "medium"),
            )
            goals.append(goal)

        return goals

    async def _create_protocol_steps(
        self, treatment_approach: str, treatment_goals: List[TreatmentGoal]
    ) -> List[ProtocolStep]:
        """Create detailed protocol steps."""
        steps = []

        # Get protocol template
        protocol_template = self._protocol_templates.get(treatment_approach, {})
        step_templates = protocol_template.get("steps", [])

        for i, template in enumerate(step_templates):
            step = ProtocolStep(
                step_id=str(uuid4()),
                step_number=i + 1,
                name=template["name"],
                description=template["description"],
                session_type=SessionType(template.get("session_type", "training")),
                duration_minutes=template.get("duration", 60),
                parameters=template.get("parameters", {}),
                success_criteria=template.get("success_criteria", []),
                prerequisites=template.get("prerequisites", []),
            )
            steps.append(step)

        return steps

    def _calculate_treatment_timeline(
        self, protocol_steps: List[ProtocolStep]
    ) -> Dict[str, Any]:
        """Calculate treatment timeline and milestones."""
        total_sessions = len(protocol_steps)
        sessions_per_week = self.config.default_sessions_per_week
        total_weeks = max(1, total_sessions // sessions_per_week)

        # Add buffer for assessments and adjustments
        total_weeks += 2

        return {
            "total_weeks": total_weeks,
            "total_sessions": total_sessions,
            "sessions_per_week": sessions_per_week,
            "estimated_completion": datetime.now(timezone.utc)
            + timedelta(weeks=total_weeks),
        }

    async def _analyze_treatment_progress(
        self, treatment_plan: TreatmentPlan, current_progress: dict
    ) -> Dict[str, Any]:
        """Analyze treatment progress against plan."""
        completed_steps = current_progress.get("completed_steps", 0)
        total_steps = len(treatment_plan.protocol_steps)
        completion_percent = (
            (completed_steps / total_steps) * 100 if total_steps > 0 else 0
        )

        # Calculate expected progress based on timeline
        weeks_since_start = current_progress.get("weeks_since_start", 0)
        expected_percent = (
            weeks_since_start / treatment_plan.estimated_duration_weeks
        ) * 100

        analysis = {
            "status": "on_track",
            "completion_percent": completion_percent,
            "expected_percent": expected_percent,
            "behind_schedule": completion_percent < (expected_percent - 10),
            "exceptional_progress": completion_percent > (expected_percent + 15),
            "safety_concerns": current_progress.get("safety_events", 0) > 0,
            "safety_recommendations": [],
        }

        # Determine overall status
        if analysis["behind_schedule"]:
            analysis["status"] = "behind_schedule"
        elif analysis["exceptional_progress"]:
            analysis["status"] = "ahead_of_schedule"
        elif analysis["safety_concerns"]:
            analysis["status"] = "safety_review_needed"

        return analysis

    async def _analyze_performance_patterns(
        self, treatment_plan: TreatmentPlan, performance_data: dict
    ) -> Dict[str, Any]:
        """Analyze performance patterns for optimization."""
        sessions_data = performance_data.get("sessions", [])

        if not sessions_data:
            return {"insufficient_data": True}

        # Analyze trends
        recent_sessions = sessions_data[-5:]  # Last 5 sessions
        performance_scores = [s.get("performance_score", 0) for s in recent_sessions]

        analysis = {
            "average_performance": sum(performance_scores) / len(performance_scores),
            "trend": "stable",
            "can_increase_intensity": False,
            "optimal_session_length": None,
            "optimal_frequency": None,
            "fatigue_indicators": [],
        }

        # Determine trend
        if len(performance_scores) >= 3:
            if performance_scores[-1] > performance_scores[0]:
                analysis["trend"] = "improving"
                analysis["can_increase_intensity"] = (
                    analysis["average_performance"] > 75
                )
            elif performance_scores[-1] < performance_scores[0]:
                analysis["trend"] = "declining"

        # Analyze session length patterns
        session_lengths = [s.get("duration_minutes", 60) for s in recent_sessions]
        performance_by_length = {}
        for i, length in enumerate(session_lengths):
            if length not in performance_by_length:
                performance_by_length[length] = []
            performance_by_length[length].append(performance_scores[i])

        # Find optimal length
        if performance_by_length:
            avg_by_length = {
                length: sum(scores) / len(scores)
                for length, scores in performance_by_length.items()
            }
            optimal_length = max(avg_by_length, key=avg_by_length.get)
            analysis["optimal_session_length"] = optimal_length

        return analysis

    def _analyze_cognitive_scores(self, cognitive_scores: dict) -> Dict[str, Any]:
        """Analyze cognitive assessment scores."""
        analysis = {"functional_deficits": [], "target_outcomes": []}

        for domain, score in cognitive_scores.items():
            if score < 70:  # Below normal range
                analysis["functional_deficits"].append(f"cognitive_{domain}")
                analysis["target_outcomes"].append(
                    f"Improve {domain} function to >80th percentile"
                )

        return analysis

    def _analyze_motor_scores(self, motor_scores: dict) -> Dict[str, Any]:
        """Analyze motor assessment scores."""
        analysis = {"functional_deficits": [], "target_outcomes": []}

        for domain, score in motor_scores.items():
            if score < 60:  # Below functional threshold
                analysis["functional_deficits"].append(f"motor_{domain}")
                analysis["target_outcomes"].append(
                    f"Restore {domain} function to functional level"
                )

        return analysis

    def _check_treatment_contraindications(self, medical_history: dict) -> List[str]:
        """Check for treatment contraindications in medical history."""
        contraindications = []

        conditions = medical_history.get("conditions", [])
        medications = medical_history.get("medications", [])

        # Check conditions
        high_risk_conditions = [
            "uncontrolled_epilepsy",
            "active_psychosis",
            "severe_cognitive_impairment",
            "unstable_cardiovascular_disease",
        ]

        for condition in conditions:
            condition_lower = condition.lower().replace(" ", "_")
            if any(risk in condition_lower for risk in high_risk_conditions):
                contraindications.append(f"Medical condition: {condition}")

        # Check medications
        problematic_medications = ["anticoagulants", "antipsychotics"]
        for med in medications:
            med_name = med.get("name", "").lower()
            if any(prob_med in med_name for prob_med in problematic_medications):
                contraindications.append(f"Medication: {med.get('name')}")

        return contraindications

    def _load_protocol_templates(self) -> Dict[str, Any]:
        """Load treatment protocol templates."""
        return {
            "intensive_motor_training": {
                "name": "Intensive Motor Training Protocol",
                "steps": [
                    {
                        "name": "Baseline Assessment",
                        "description": "Comprehensive motor function baseline",
                        "session_type": "assessment",
                        "duration": 90,
                        "parameters": {"assessment_type": "motor_baseline"},
                    },
                    {
                        "name": "Motor Imagery Training",
                        "description": "Train motor imagery patterns",
                        "session_type": "training",
                        "duration": 60,
                        "parameters": {
                            "task": "motor_imagery",
                            "difficulty": "beginner",
                        },
                    },
                    {
                        "name": "Closed-Loop Training",
                        "description": "Real-time feedback training",
                        "session_type": "training",
                        "duration": 60,
                        "parameters": {"feedback_type": "visual", "targets": 4},
                    },
                ],
            },
            "cognitive_rehabilitation": {
                "name": "Cognitive Rehabilitation Protocol",
                "steps": [
                    {
                        "name": "Cognitive Assessment",
                        "description": "Comprehensive cognitive evaluation",
                        "session_type": "assessment",
                        "duration": 120,
                        "parameters": {"domains": ["attention", "memory", "executive"]},
                    },
                    {
                        "name": "Attention Training",
                        "description": "Focused attention enhancement",
                        "session_type": "training",
                        "duration": 45,
                        "parameters": {"task": "sustained_attention", "duration": 30},
                    },
                ],
            },
        }

    def _load_treatment_algorithms(self) -> Dict[str, Any]:
        """Load treatment selection algorithms."""
        return {
            "intensive_motor_training": {
                "goals": [
                    {
                        "description": "Restore basic motor control",
                        "metric": "motor_control_score",
                        "target_value": 75,
                        "measurement": "clinical_assessment",
                        "timeline": 8,
                        "priority": "high",
                    },
                    {
                        "description": "Improve fine motor skills",
                        "metric": "fine_motor_score",
                        "target_value": 65,
                        "measurement": "dexterity_test",
                        "timeline": 12,
                        "priority": "medium",
                    },
                ],
            },
            "cognitive_rehabilitation": {
                "goals": [
                    {
                        "description": "Enhance working memory",
                        "metric": "working_memory_span",
                        "target_value": 6,
                        "measurement": "n_back_test",
                        "timeline": 6,
                        "priority": "high",
                    },
                ],
            },
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get treatment planner statistics."""
        total_plans = len(self._treatment_plans)
        active_plans = sum(
            1 for plan in self._treatment_plans.values() if plan.status == "active"
        )

        return {
            "total_treatment_plans": total_plans,
            "active_treatment_plans": active_plans,
            "completed_treatment_plans": sum(
                1
                for plan in self._treatment_plans.values()
                if plan.status == "completed"
            ),
            "average_plan_duration": (
                sum(
                    plan.estimated_duration_weeks
                    for plan in self._treatment_plans.values()
                )
                / total_plans
                if total_plans > 0
                else 0
            ),
        }
