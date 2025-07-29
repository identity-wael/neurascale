"""Protocol execution engine for clinical BCI workflows."""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any
from uuid import uuid4
from enum import Enum

from ..types import (
    SessionType,
    ClinicalConfig,
)

logger = logging.getLogger(__name__)


class ProtocolStatus(Enum):
    """Protocol execution status."""

    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(Enum):
    """Protocol step status."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ProtocolEngine:
    """Manages clinical protocol execution and workflow orchestration.

    Handles protocol scheduling, step execution, progress tracking,
    and adaptive protocol adjustments based on patient progress.
    """

    def __init__(self, config: ClinicalConfig):
        """Initialize protocol engine."""
        self.config = config

        # Active protocols storage
        self._active_protocols: Dict[str, Dict[str, Any]] = {}
        self._protocol_history: Dict[str, Dict[str, Any]] = {}

        # Protocol templates and rules
        self.protocol_templates = self._load_protocol_templates()
        self.execution_rules = self._load_execution_rules()
        self.adaptation_algorithms = self._load_adaptation_algorithms()

        logger.info("Protocol engine initialized")

    async def start_protocol_execution(
        self, patient_id: str, protocol_data: dict
    ) -> str:
        """Start protocol execution for a patient.

        Args:
            patient_id: Patient identifier
            protocol_data: Protocol configuration and steps

        Returns:
            Protocol execution ID
        """
        execution_id = str(uuid4())

        try:
            # Validate protocol
            validation_result = await self._validate_protocol(protocol_data)
            if not validation_result["valid"]:
                raise ValueError(f"Invalid protocol: {validation_result['errors']}")

            # Initialize protocol execution state
            execution_state = {
                "execution_id": execution_id,
                "patient_id": patient_id,
                "protocol_id": protocol_data.get("protocol_id", ""),
                "protocol_name": protocol_data.get("name", ""),
                "status": ProtocolStatus.PENDING,
                "started_at": datetime.now(timezone.utc),
                "steps": self._initialize_protocol_steps(protocol_data["steps"]),
                "current_step": 0,
                "progress": {
                    "completed_steps": 0,
                    "total_steps": len(protocol_data["steps"]),
                    "success_rate": 0.0,
                    "estimated_completion": None,
                },
                "metrics": {
                    "total_session_time": 0,
                    "successful_sessions": 0,
                    "failed_sessions": 0,
                    "adaptations_made": 0,
                },
                "adaptations": [],
                "alerts": [],
            }

            # Calculate estimated completion
            execution_state["progress"]["estimated_completion"] = (
                await self._estimate_completion_time(protocol_data["steps"])
            )

            # Store active protocol
            self._active_protocols[execution_id] = execution_state

            # Update status to active
            execution_state["status"] = ProtocolStatus.ACTIVE

            logger.info(
                f"Protocol execution started: {execution_id} for patient {patient_id}"
            )

            return execution_id

        except Exception as e:
            logger.error(f"Failed to start protocol execution: {e}")
            raise

    async def execute_protocol_step(
        self, execution_id: str, step_data: dict
    ) -> Dict[str, Any]:
        """Execute a single protocol step.

        Args:
            execution_id: Protocol execution identifier
            step_data: Step execution parameters

        Returns:
            Step execution result
        """
        if execution_id not in self._active_protocols:
            raise ValueError(f"Protocol execution not found: {execution_id}")

        protocol = self._active_protocols[execution_id]
        current_step_index = protocol["current_step"]

        if current_step_index >= len(protocol["steps"]):
            raise ValueError("No more steps to execute")

        current_step = protocol["steps"][current_step_index]

        try:
            # Update step status
            current_step["status"] = StepStatus.IN_PROGRESS
            current_step["started_at"] = datetime.now(timezone.utc)

            # Execute step based on type
            execution_result = await self._execute_step_by_type(
                current_step, step_data, protocol
            )

            # Update step completion
            if execution_result["success"]:
                current_step["status"] = StepStatus.COMPLETED
                current_step["completed_at"] = datetime.now(timezone.utc)
                current_step["result"] = execution_result

                # Update protocol progress
                protocol["progress"]["completed_steps"] += 1
                protocol["metrics"]["successful_sessions"] += 1

                # Move to next step
                protocol["current_step"] += 1

            else:
                current_step["status"] = StepStatus.FAILED
                current_step["failed_at"] = datetime.now(timezone.utc)
                current_step["failure_reason"] = execution_result.get(
                    "error", "Unknown error"
                )

                protocol["metrics"]["failed_sessions"] += 1

                # Check if protocol should continue or fail
                if not execution_result.get("can_continue", False):
                    protocol["status"] = ProtocolStatus.FAILED

            # Update success rate
            total_attempts = (
                protocol["metrics"]["successful_sessions"]
                + protocol["metrics"]["failed_sessions"]
            )
            protocol["progress"]["success_rate"] = (
                protocol["metrics"]["successful_sessions"] / total_attempts
                if total_attempts > 0
                else 0.0
            )

            # Check for protocol completion
            if protocol["current_step"] >= len(protocol["steps"]):
                await self._complete_protocol(execution_id)

            # Check for adaptations needed
            await self._check_adaptation_triggers(execution_id, execution_result)

            logger.info(
                f"Protocol step executed: {execution_id}, step {current_step_index}, "
                f"success: {execution_result['success']}"
            )

            return execution_result

        except Exception as e:
            current_step["status"] = StepStatus.FAILED
            current_step["failure_reason"] = str(e)
            logger.error(f"Step execution failed: {e}")
            raise

    async def adapt_protocol(
        self, execution_id: str, adaptation_request: dict
    ) -> Dict[str, Any]:
        """Adapt protocol based on patient progress and performance.

        Args:
            execution_id: Protocol execution identifier
            adaptation_request: Adaptation parameters

        Returns:
            Adaptation result
        """
        if execution_id not in self._active_protocols:
            raise ValueError(f"Protocol execution not found: {execution_id}")

        protocol = self._active_protocols[execution_id]

        try:
            # Analyze adaptation need
            adaptation_analysis = await self._analyze_adaptation_need(
                protocol, adaptation_request
            )

            adaptation_result = {
                "adaptation_id": str(uuid4()),
                "execution_id": execution_id,
                "requested_at": datetime.now(timezone.utc),
                "adaptation_type": adaptation_request.get("type", "unknown"),
                "approved": False,
                "changes_made": [],
                "impact_assessment": adaptation_analysis,
            }

            # Apply adaptation algorithms
            for algorithm_name, algorithm in self.adaptation_algorithms.items():
                if await self._should_apply_algorithm(algorithm, adaptation_analysis):
                    changes = await self._apply_adaptation_algorithm(
                        protocol, algorithm, adaptation_request
                    )
                    adaptation_result["changes_made"].extend(changes)
                    adaptation_result["approved"] = True

            # Record adaptation
            protocol["adaptations"].append(adaptation_result)
            protocol["metrics"]["adaptations_made"] += 1

            logger.info(
                f"Protocol adaptation applied: {execution_id}, "
                f"type: {adaptation_request.get('type')}, "
                f"approved: {adaptation_result['approved']}"
            )

            return adaptation_result

        except Exception as e:
            logger.error(f"Protocol adaptation failed: {e}")
            raise

    async def pause_protocol(self, execution_id: str, reason: str = "") -> bool:
        """Pause protocol execution.

        Args:
            execution_id: Protocol execution identifier
            reason: Reason for pause

        Returns:
            Success status
        """
        if execution_id not in self._active_protocols:
            return False

        protocol = self._active_protocols[execution_id]

        if protocol["status"] != ProtocolStatus.ACTIVE:
            return False

        protocol["status"] = ProtocolStatus.PAUSED
        protocol["paused_at"] = datetime.now(timezone.utc)
        protocol["pause_reason"] = reason

        logger.info(f"Protocol paused: {execution_id}, reason: {reason}")

        return True

    async def resume_protocol(self, execution_id: str) -> bool:
        """Resume paused protocol execution.

        Args:
            execution_id: Protocol execution identifier

        Returns:
            Success status
        """
        if execution_id not in self._active_protocols:
            return False

        protocol = self._active_protocols[execution_id]

        if protocol["status"] != ProtocolStatus.PAUSED:
            return False

        # Check if safe to resume
        safety_check = await self._check_resume_safety(protocol)
        if not safety_check["safe"]:
            logger.warning(f"Protocol resume blocked: {safety_check['reason']}")
            return False

        protocol["status"] = ProtocolStatus.ACTIVE
        protocol["resumed_at"] = datetime.now(timezone.utc)

        logger.info(f"Protocol resumed: {execution_id}")

        return True

    async def get_protocol_status(self, execution_id: str) -> Dict[str, Any]:
        """Get current protocol execution status.

        Args:
            execution_id: Protocol execution identifier

        Returns:
            Protocol status information
        """
        # Check active protocols first
        if execution_id in self._active_protocols:
            protocol = self._active_protocols[execution_id]
        elif execution_id in self._protocol_history:
            protocol = self._protocol_history[execution_id]
        else:
            raise ValueError(f"Protocol execution not found: {execution_id}")

        status_info = {
            "execution_id": execution_id,
            "patient_id": protocol["patient_id"],
            "status": protocol["status"].value,
            "progress": protocol["progress"],
            "current_step": protocol["current_step"],
            "total_steps": len(protocol["steps"]),
            "metrics": protocol["metrics"],
            "last_updated": datetime.now(timezone.utc),
        }

        # Add current step details
        if protocol["current_step"] < len(protocol["steps"]):
            current_step = protocol["steps"][protocol["current_step"]]
            status_info["current_step_details"] = {
                "step_number": protocol["current_step"] + 1,
                "step_name": current_step["name"],
                "step_type": current_step["session_type"],
                "status": current_step["status"].value,
                "estimated_duration": current_step.get("duration_minutes", 60),
            }

        return status_info

    async def _validate_protocol(self, protocol_data: dict) -> Dict[str, Any]:
        """Validate protocol configuration."""
        validation = {"valid": True, "errors": [], "warnings": []}

        # Check required fields
        required_fields = ["steps", "name"]
        for field in required_fields:
            if field not in protocol_data:
                validation["valid"] = False
                validation["errors"].append(f"Missing required field: {field}")

        # Validate steps
        if "steps" in protocol_data:
            steps = protocol_data["steps"]
            if not isinstance(steps, list) or len(steps) == 0:
                validation["valid"] = False
                validation["errors"].append("Protocol must have at least one step")
            else:
                for i, step in enumerate(steps):
                    step_validation = await self._validate_protocol_step(step, i)
                    if not step_validation["valid"]:
                        validation["valid"] = False
                        validation["errors"].extend(step_validation["errors"])

        return validation

    async def _validate_protocol_step(
        self, step: dict, step_index: int
    ) -> Dict[str, Any]:
        """Validate individual protocol step."""
        validation = {"valid": True, "errors": []}

        required_step_fields = ["name", "session_type"]
        for field in required_step_fields:
            if field not in step:
                validation["valid"] = False
                validation["errors"].append(
                    f"Step {step_index}: Missing required field '{field}'"
                )

        # Validate session type
        if "session_type" in step:
            try:
                SessionType(step["session_type"])
            except ValueError:
                validation["valid"] = False
                validation["errors"].append(
                    f"Step {step_index}: Invalid session type '{step['session_type']}'"
                )

        return validation

    def _initialize_protocol_steps(
        self, steps_data: List[dict]
    ) -> List[Dict[str, Any]]:
        """Initialize protocol steps with execution state."""
        initialized_steps = []

        for i, step_data in enumerate(steps_data):
            step = {
                "step_id": str(uuid4()),
                "step_number": i + 1,
                "name": step_data["name"],
                "description": step_data.get("description", ""),
                "session_type": step_data["session_type"],
                "duration_minutes": step_data.get("duration_minutes", 60),
                "parameters": step_data.get("parameters", {}),
                "success_criteria": step_data.get("success_criteria", []),
                "prerequisites": step_data.get("prerequisites", []),
                "status": StepStatus.NOT_STARTED,
                "attempts": 0,
                "max_attempts": step_data.get("max_attempts", 3),
                "created_at": datetime.now(timezone.utc),
                "started_at": None,
                "completed_at": None,
                "failed_at": None,
                "result": None,
                "failure_reason": None,
            }
            initialized_steps.append(step)

        return initialized_steps

    async def _estimate_completion_time(self, steps: List[dict]) -> datetime:
        """Estimate protocol completion time."""
        total_duration_minutes = sum(step.get("duration_minutes", 60) for step in steps)

        # Add buffer time for setup, breaks, assessments
        buffer_minutes = len(steps) * 15  # 15 minutes buffer per step

        # Assume 2 sessions per week
        sessions_per_week = 2
        minutes_per_week = sessions_per_week * 90  # 90 minutes per session

        estimated_weeks = (total_duration_minutes + buffer_minutes) / minutes_per_week

        return datetime.now(timezone.utc) + timedelta(weeks=estimated_weeks)

    async def _execute_step_by_type(
        self, step: dict, step_data: dict, protocol: dict
    ) -> Dict[str, Any]:
        """Execute protocol step based on its type."""
        session_type = step["session_type"]

        execution_result = {
            "success": False,
            "step_id": step["step_id"],
            "execution_time": datetime.now(timezone.utc),
            "session_duration": 0,
            "performance_metrics": {},
            "quality_metrics": {},
            "can_continue": True,
            "recommendations": [],
        }

        try:
            if session_type == "assessment":
                result = await self._execute_assessment_step(step, step_data)
            elif session_type == "training":
                result = await self._execute_training_step(step, step_data)
            elif session_type == "calibration":
                result = await self._execute_calibration_step(step, step_data)
            elif session_type == "therapy":
                result = await self._execute_therapy_step(step, step_data)
            else:
                result = await self._execute_generic_step(step, step_data)

            execution_result.update(result)

            # Check success criteria
            if await self._check_success_criteria(step, execution_result):
                execution_result["success"] = True
            else:
                execution_result["success"] = False
                execution_result["recommendations"].append(
                    "Success criteria not met - consider step repetition or adaptation"
                )

        except Exception as e:
            execution_result["error"] = str(e)
            execution_result["can_continue"] = False
            logger.error(f"Step execution error: {e}")

        return execution_result

    async def _execute_assessment_step(
        self, step: dict, step_data: dict
    ) -> Dict[str, Any]:
        """Execute assessment protocol step."""
        return {
            "assessment_type": step["parameters"].get("assessment_type", "cognitive"),
            "scores": step_data.get("assessment_scores", {}),
            "session_duration": step_data.get("duration", step["duration_minutes"]),
            "completion_rate": step_data.get("completion_rate", 1.0),
            "quality_indicators": step_data.get("quality_metrics", {}),
        }

    async def _execute_training_step(
        self, step: dict, step_data: dict
    ) -> Dict[str, Any]:
        """Execute training protocol step."""
        return {
            "training_type": step["parameters"].get("task", "motor_imagery"),
            "accuracy": step_data.get("accuracy", 0.0),
            "session_duration": step_data.get("duration", step["duration_minutes"]),
            "trials_completed": step_data.get("trials", 0),
            "performance_trend": step_data.get("trend", "stable"),
            "fatigue_level": step_data.get("fatigue", "low"),
        }

    async def _execute_calibration_step(
        self, step: dict, step_data: dict
    ) -> Dict[str, Any]:
        """Execute calibration protocol step."""
        return {
            "calibration_type": step["parameters"].get("calibration_type", "signal"),
            "calibration_quality": step_data.get("quality_score", 0.0),
            "session_duration": step_data.get("duration", step["duration_minutes"]),
            "signal_to_noise": step_data.get("snr", 0.0),
            "stability_index": step_data.get("stability", 0.0),
        }

    async def _execute_therapy_step(
        self, step: dict, step_data: dict
    ) -> Dict[str, Any]:
        """Execute therapy protocol step."""
        return {
            "therapy_type": step["parameters"].get("therapy_type", "neuromodulation"),
            "therapeutic_effect": step_data.get("effect_size", 0.0),
            "session_duration": step_data.get("duration", step["duration_minutes"]),
            "patient_response": step_data.get("response", "positive"),
            "side_effects": step_data.get("side_effects", []),
        }

    async def _execute_generic_step(
        self, step: dict, step_data: dict
    ) -> Dict[str, Any]:
        """Execute generic protocol step."""
        return {
            "step_type": step["session_type"],
            "completion_status": step_data.get("completed", False),
            "session_duration": step_data.get("duration", step["duration_minutes"]),
            "notes": step_data.get("notes", ""),
        }

    async def _check_success_criteria(self, step: dict, execution_result: dict) -> bool:
        """Check if step meets success criteria."""
        criteria = step.get("success_criteria", [])

        if not criteria:
            return True  # No criteria means automatic success

        for criterion in criteria:
            if not await self._evaluate_criterion(criterion, execution_result):
                return False

        return True

    async def _evaluate_criterion(
        self, criterion: dict, execution_result: dict
    ) -> bool:
        """Evaluate a single success criterion."""
        metric = criterion.get("metric")
        operator = criterion.get("operator", ">=")
        threshold = criterion.get("threshold", 0)

        if metric not in execution_result:
            return False

        value = execution_result[metric]

        if operator == ">=":
            return value >= threshold
        elif operator == ">":
            return value > threshold
        elif operator == "<=":
            return value <= threshold
        elif operator == "<":
            return value < threshold
        elif operator == "==":
            return value == threshold
        elif operator == "!=":
            return value != threshold
        else:
            return False

    async def _complete_protocol(self, execution_id: str):
        """Complete protocol execution."""
        protocol = self._active_protocols[execution_id]

        protocol["status"] = ProtocolStatus.COMPLETED
        protocol["completed_at"] = datetime.now(timezone.utc)

        # Calculate final metrics
        total_duration = (
            protocol["completed_at"] - protocol["started_at"]
        ).total_seconds() / 3600  # Convert to hours

        protocol["metrics"]["total_protocol_duration_hours"] = total_duration
        protocol["metrics"]["average_step_duration"] = (
            protocol["metrics"]["total_session_time"]
            / protocol["progress"]["completed_steps"]
            if protocol["progress"]["completed_steps"] > 0
            else 0
        )

        # Move to history
        self._protocol_history[execution_id] = protocol
        del self._active_protocols[execution_id]

        logger.info(f"Protocol completed: {execution_id}")

    def _load_protocol_templates(self) -> Dict[str, Any]:
        """Load protocol templates."""
        return {
            "motor_rehabilitation": {
                "name": "Motor Rehabilitation Protocol",
                "description": "Standard motor function rehabilitation",
                "estimated_duration_weeks": 8,
                "sessions_per_week": 3,
            },
            "cognitive_training": {
                "name": "Cognitive Training Protocol",
                "description": "Cognitive enhancement and rehabilitation",
                "estimated_duration_weeks": 6,
                "sessions_per_week": 2,
            },
        }

    def _load_execution_rules(self) -> Dict[str, Any]:
        """Load protocol execution rules."""
        return {
            "max_consecutive_failures": 2,
            "min_success_rate": 0.6,
            "max_adaptation_attempts": 3,
            "safety_pause_threshold": 0.8,
        }

    def _load_adaptation_algorithms(self) -> Dict[str, Any]:
        """Load protocol adaptation algorithms."""
        return {
            "difficulty_adjustment": {
                "trigger_conditions": ["low_performance", "high_success_rate"],
                "adjustments": ["difficulty_increase", "difficulty_decrease"],
                "parameters": {"performance_threshold": 0.7, "success_threshold": 0.9},
            },
            "session_duration": {
                "trigger_conditions": ["fatigue_indicators", "attention_decline"],
                "adjustments": ["duration_decrease", "break_insertion"],
                "parameters": {"fatigue_threshold": 0.6, "attention_threshold": 0.5},
            },
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get protocol engine statistics."""
        total_protocols = len(self._active_protocols) + len(self._protocol_history)

        return {
            "active_protocols": len(self._active_protocols),
            "completed_protocols": len(self._protocol_history),
            "total_protocols": total_protocols,
            "average_completion_rate": 0.85,  # Would calculate from actual data
            "most_common_adaptations": ["difficulty_adjustment", "session_duration"],
        }
