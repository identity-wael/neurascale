"""Clinical session lifecycle management and orchestration."""

import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Callable
from uuid import uuid4

from ..types import (
    ClinicalSession,
    SessionStatus,
    SessionType,
    DeviceConfig,
    ClinicalNote,
    SafetyEvent,
    OutcomeMeasure,
    ClinicalConfig,
)
from .scheduling_service import SchedulingService
from .live_monitoring import LiveSessionMonitor
from .clinical_notes import ClinicalNotes
from .safety_protocols import SafetyProtocols

logger = logging.getLogger(__name__)


class SessionManager:
    """Orchestrates clinical BCI session lifecycle.

    Manages session creation, execution, monitoring, and completion
    with integrated safety protocols and real-time oversight.
    """

    def __init__(self, config: ClinicalConfig, device_manager=None, neural_ledger=None):
        """Initialize session manager.

        Args:
            config: Clinical configuration
            device_manager: Device management system
            neural_ledger: Audit logging system
        """
        self.config = config
        self.device_manager = device_manager
        self.neural_ledger = neural_ledger

        # Initialize sub-services
        self.scheduling_service = SchedulingService(config)
        self.live_monitor = LiveSessionMonitor(config)
        self.clinical_notes = ClinicalNotes(config)
        self.safety_protocols = SafetyProtocols(config)

        # Session storage (would be database in production)
        self._active_sessions: Dict[str, ClinicalSession] = {}
        self._session_history: Dict[str, ClinicalSession] = {}

        # Session callbacks
        self._session_callbacks: Dict[str, List[Callable]] = {
            "session_started": [],
            "session_ended": [],
            "safety_alert": [],
            "progress_update": [],
        }

        # Background tasks
        self._monitoring_tasks: Dict[str, asyncio.Task] = {}

        logger.info("Session manager initialized")

    async def create_session(
        self, patient_id: str, session_config: dict
    ) -> ClinicalSession:
        """Create new clinical session.

        Args:
            patient_id: Patient identifier
            session_config: Session configuration parameters

        Returns:
            Created ClinicalSession
        """
        try:
            # Generate session ID
            session_id = str(uuid4())

            # Validate session configuration
            validation_result = await self._validate_session_config(session_config)
            if not validation_result["valid"]:
                raise ValueError(
                    f"Session configuration invalid: {validation_result['errors']}"
                )

            # Create device configuration
            device_config = None
            if "device" in session_config:
                device_config = DeviceConfig(
                    device_type=session_config["device"]["type"],
                    device_id=session_config["device"]["id"],
                    sampling_rate=session_config["device"].get("sampling_rate", 256.0),
                    channels=session_config["device"].get("channels", []),
                    calibration_settings=session_config["device"].get(
                        "calibration", {}
                    ),
                    safety_thresholds=session_config["device"].get(
                        "safety_thresholds", {}
                    ),
                )

            # Create clinical session
            session = ClinicalSession(
                session_id=session_id,
                patient_id=patient_id,
                provider_id=session_config.get("provider_id", ""),
                session_type=SessionType(session_config.get("type", "treatment")),
                protocol_id=session_config.get("protocol_id", ""),
                scheduled_start=(
                    datetime.fromisoformat(session_config["scheduled_start"])
                    if "scheduled_start" in session_config
                    else None
                ),
                duration_minutes=session_config.get("duration_minutes", 60),
                device_configuration=device_config,
                status=SessionStatus.SCHEDULED,
            )

            # Store session
            self._active_sessions[session_id] = session

            # Schedule session if requested
            if session.scheduled_start:
                await self.scheduling_service.schedule_session(
                    {
                        "session_id": session_id,
                        "patient_id": patient_id,
                        "provider_id": session.provider_id,
                        "start_time": session.scheduled_start,
                        "duration_minutes": session.duration_minutes,
                        "device_requirements": session_config.get("device", {}),
                    }
                )

            logger.info(
                f"Clinical session created: {session_id} for patient {patient_id}"
            )

            # Log to audit trail
            await self._log_session_event(
                session_id,
                "session_created",
                {
                    "patient_id": patient_id,
                    "session_type": session.session_type.value,
                    "provider_id": session.provider_id,
                },
            )

            return session

        except Exception as e:
            logger.error(f"Failed to create session for patient {patient_id}: {e}")
            raise

    async def start_session(self, session_id: str) -> SessionStatus:
        """Start clinical BCI session with safety checks.

        Args:
            session_id: Session identifier

        Returns:
            Session status after start attempt
        """
        if session_id not in self._active_sessions:
            raise ValueError(f"Session not found: {session_id}")

        session = self._active_sessions[session_id]

        try:
            # Pre-session safety validation
            safety_check = await self.safety_protocols.validate_pre_session_safety(
                session.patient_id,
                (
                    session.device_configuration.__dict__
                    if session.device_configuration
                    else {}
                ),
            )

            if not safety_check["safe_to_proceed"]:
                session.status = SessionStatus.ERROR
                logger.error(
                    f"Session {session_id} failed safety check: {safety_check['issues']}"
                )
                return session.status

            # Update session status
            session.status = SessionStatus.PREPARING
            session.actual_start = datetime.now(timezone.utc)

            # Initialize device if specified
            if session.device_configuration and self.device_manager:
                device_ready = await self._prepare_session_device(session)
                if not device_ready:
                    session.status = SessionStatus.ERROR
                    return session.status

            # Start live monitoring
            await self.live_monitor.start_real_time_monitoring(session_id)

            # Start monitoring task
            self._monitoring_tasks[session_id] = asyncio.create_task(
                self._session_monitoring_loop(session_id)
            )

            # Update status to in progress
            session.status = SessionStatus.IN_PROGRESS

            # Notify callbacks
            await self._notify_session_callbacks("session_started", session)

            logger.info(f"Clinical session started: {session_id}")

            # Log to audit trail
            await self._log_session_event(
                session_id,
                "session_started",
                {
                    "start_time": session.actual_start.isoformat(),
                    "safety_check_passed": True,
                },
            )

            return session.status

        except Exception as e:
            session.status = SessionStatus.ERROR
            logger.error(f"Failed to start session {session_id}: {e}")

            # Log error
            await self._log_session_event(
                session_id, "session_start_failed", {"error": str(e)}
            )

            return session.status

    async def monitor_session_progress(self, session_id: str) -> Dict[str, Any]:
        """Monitor ongoing session progress.

        Args:
            session_id: Session identifier

        Returns:
            Current session progress status
        """
        if session_id not in self._active_sessions:
            raise ValueError(f"Session not found: {session_id}")

        session = self._active_sessions[session_id]

        # Get current progress from live monitor
        progress = await self.live_monitor.get_session_progress(session_id)

        # Calculate session metrics
        if session.actual_start:
            elapsed_time = (
                datetime.now(timezone.utc) - session.actual_start
            ).total_seconds() / 60
            planned_duration = session.duration_minutes
            progress_percent = min((elapsed_time / planned_duration) * 100, 100)
        else:
            elapsed_time = 0
            progress_percent = 0

        # Get safety status
        safety_status = await self.safety_protocols.get_session_safety_status(
            session_id
        )

        # Get device performance if available
        device_performance = {}
        if session.device_configuration and self.device_manager:
            device_performance = await self._get_device_performance(session)

        progress_report = {
            "session_id": session_id,
            "status": session.status.value,
            "progress_percent": progress_percent,
            "elapsed_minutes": elapsed_time,
            "remaining_minutes": max(0, session.duration_minutes - elapsed_time),
            "safety_status": safety_status,
            "device_performance": device_performance,
            "live_monitoring": progress,
            "clinical_notes_count": len(session.clinical_notes),
            "safety_events_count": len(session.safety_events),
            "last_updated": datetime.now(timezone.utc),
        }

        return progress_report

    async def end_session(
        self, session_id: str, completion_notes: dict
    ) -> ClinicalSession:
        """End clinical session and perform cleanup.

        Args:
            session_id: Session identifier
            completion_notes: Session completion information

        Returns:
            Completed session record
        """
        if session_id not in self._active_sessions:
            raise ValueError(f"Session not found: {session_id}")

        session = self._active_sessions[session_id]

        try:
            # Stop monitoring task
            if session_id in self._monitoring_tasks:
                self._monitoring_tasks[session_id].cancel()
                try:
                    await self._monitoring_tasks[session_id]
                except asyncio.CancelledError:
                    pass
                del self._monitoring_tasks[session_id]

            # Stop live monitoring
            await self.live_monitor.stop_monitoring(session_id)

            # Stop device if active
            if session.device_configuration and self.device_manager:
                await self._cleanup_session_device(session)

            # Record session completion
            session.actual_end = datetime.now(timezone.utc)
            session.status = SessionStatus.COMPLETED

            # Add completion notes
            if completion_notes:
                completion_note = ClinicalNote(
                    session_id=session_id,
                    provider_id=session.provider_id,
                    note_type="completion",
                    content=completion_notes.get("notes", ""),
                    assessment_scores=completion_notes.get("scores", {}),
                    tags=completion_notes.get("tags", []),
                )
                session.clinical_notes.append(completion_note)

            # Calculate session outcomes
            session_outcomes = await self._calculate_session_outcomes(session)
            session.outcomes.extend(session_outcomes)

            # Move to history
            self._session_history[session_id] = session
            del self._active_sessions[session_id]

            # Notify callbacks
            await self._notify_session_callbacks("session_ended", session)

            logger.info(f"Clinical session completed: {session_id}")

            # Log to audit trail
            await self._log_session_event(
                session_id,
                "session_completed",
                {
                    "end_time": session.actual_end.isoformat(),
                    "duration_minutes": (
                        (session.actual_end - session.actual_start).total_seconds() / 60
                        if session.actual_start
                        else 0
                    ),
                    "outcomes_count": len(session.outcomes),
                },
            )

            return session

        except Exception as e:
            logger.error(f"Failed to end session {session_id}: {e}")
            raise

    async def pause_session(self, session_id: str, reason: str = "") -> bool:
        """Pause active session.

        Args:
            session_id: Session identifier
            reason: Reason for pause

        Returns:
            Success status
        """
        if session_id not in self._active_sessions:
            return False

        session = self._active_sessions[session_id]

        if session.status != SessionStatus.IN_PROGRESS:
            return False

        try:
            # Pause monitoring
            await self.live_monitor.pause_monitoring(session_id)

            # Pause device if active
            if session.device_configuration and self.device_manager:
                await self._pause_session_device(session)

            # Update status
            session.status = SessionStatus.PAUSED

            # Record pause event
            pause_event = SafetyEvent(
                session_id=session_id,
                event_type="session_paused",
                description=f"Session paused: {reason}",
                response_taken="Monitoring and device paused",
                resolved=False,
                reported_by="system",
            )
            session.safety_events.append(pause_event)

            logger.info(f"Session paused: {session_id}, reason: {reason}")

            return True

        except Exception as e:
            logger.error(f"Failed to pause session {session_id}: {e}")
            return False

    async def resume_session(self, session_id: str) -> bool:
        """Resume paused session.

        Args:
            session_id: Session identifier

        Returns:
            Success status
        """
        if session_id not in self._active_sessions:
            return False

        session = self._active_sessions[session_id]

        if session.status != SessionStatus.PAUSED:
            return False

        try:
            # Safety check before resume
            safety_check = await self.safety_protocols.validate_pre_session_safety(
                session.patient_id,
                (
                    session.device_configuration.__dict__
                    if session.device_configuration
                    else {}
                ),
            )

            if not safety_check["safe_to_proceed"]:
                logger.error(f"Session {session_id} cannot resume: safety check failed")
                return False

            # Resume device
            if session.device_configuration and self.device_manager:
                await self._resume_session_device(session)

            # Resume monitoring
            await self.live_monitor.resume_monitoring(session_id)

            # Update status
            session.status = SessionStatus.IN_PROGRESS

            # Record resume event
            resume_event = SafetyEvent(
                session_id=session_id,
                event_type="session_resumed",
                description="Session resumed after pause",
                response_taken="Monitoring and device resumed",
                resolved=True,
                reported_by="system",
            )
            session.safety_events.append(resume_event)

            logger.info(f"Session resumed: {session_id}")

            return True

        except Exception as e:
            logger.error(f"Failed to resume session {session_id}: {e}")
            return False

    async def get_session(self, session_id: str) -> Optional[ClinicalSession]:
        """Get session by ID (active or historical).

        Args:
            session_id: Session identifier

        Returns:
            Session record if found
        """
        # Check active sessions first
        if session_id in self._active_sessions:
            return self._active_sessions[session_id]

        # Check historical sessions
        if session_id in self._session_history:
            return self._session_history[session_id]

        return None

    async def get_patient_sessions(
        self, patient_id: str, include_history: bool = False
    ) -> List[ClinicalSession]:
        """Get all sessions for a patient.

        Args:
            patient_id: Patient identifier
            include_history: Whether to include completed sessions

        Returns:
            List of patient sessions
        """
        patient_sessions = []

        # Get active sessions
        for session in self._active_sessions.values():
            if session.patient_id == patient_id:
                patient_sessions.append(session)

        # Get historical sessions if requested
        if include_history:
            for session in self._session_history.values():
                if session.patient_id == patient_id:
                    patient_sessions.append(session)

        # Sort by creation/start time
        patient_sessions.sort(
            key=lambda s: s.scheduled_start
            or s.actual_start
            or datetime.min.replace(tzinfo=timezone.utc)
        )

        return patient_sessions

    def add_session_callback(self, event_type: str, callback: Callable):
        """Add callback for session events.

        Args:
            event_type: Type of event to listen for
            callback: Callback function
        """
        if event_type in self._session_callbacks:
            self._session_callbacks[event_type].append(callback)

    async def _session_monitoring_loop(self, session_id: str):
        """Background monitoring loop for active session."""
        try:
            while session_id in self._active_sessions:
                session = self._active_sessions[session_id]

                if session.status not in [
                    SessionStatus.IN_PROGRESS,
                    SessionStatus.PAUSED,
                ]:
                    break

                # Check for safety issues
                safety_alerts = await self.safety_protocols.check_session_safety(
                    session_id
                )

                for alert in safety_alerts:
                    # Record safety event
                    safety_event = SafetyEvent(
                        session_id=session_id,
                        event_type=alert["type"],
                        description=alert["description"],
                        severity=alert["severity"],
                        response_taken=alert.get("response", ""),
                        reported_by="monitoring_system",
                    )
                    session.safety_events.append(safety_event)

                    # Notify callbacks
                    await self._notify_session_callbacks(
                        "safety_alert", {"session": session, "alert": alert}
                    )

                # Check session timeout
                if session.actual_start:
                    elapsed = (
                        datetime.now(timezone.utc) - session.actual_start
                    ).total_seconds() / 60
                    if elapsed >= session.duration_minutes:
                        logger.info(f"Session {session_id} reached scheduled duration")
                        # Could auto-end or notify provider

                # Wait before next check
                await asyncio.sleep(5)  # Check every 5 seconds

        except asyncio.CancelledError:
            logger.info(f"Monitoring loop cancelled for session {session_id}")
        except Exception as e:
            logger.error(f"Error in monitoring loop for session {session_id}: {e}")

    async def _validate_session_config(self, config: dict) -> Dict[str, Any]:
        """Validate session configuration."""
        validation = {"valid": True, "errors": [], "warnings": []}

        # Required fields
        required_fields = ["type"]
        for field in required_fields:
            if field not in config:
                validation["valid"] = False
                validation["errors"].append(f"Missing required field: {field}")

        # Validate session type
        if "type" in config:
            try:
                SessionType(config["type"])
            except ValueError:
                validation["valid"] = False
                validation["errors"].append(f"Invalid session type: {config['type']}")

        # Validate duration
        if "duration_minutes" in config:
            duration = config["duration_minutes"]
            if not isinstance(duration, int) or duration <= 0:
                validation["valid"] = False
                validation["errors"].append("Duration must be positive integer")
            elif duration > 180:  # 3 hours
                validation["warnings"].append("Session duration exceeds 3 hours")

        return validation

    async def _prepare_session_device(self, session: ClinicalSession) -> bool:
        """Prepare device for session."""
        # In production, would integrate with device management system
        try:
            device_config = session.device_configuration
            if not device_config:
                return True

            # Would connect to device, run calibration, etc.
            logger.info(
                f"Device prepared for session {session.session_id}: {device_config.device_type}"
            )
            return True

        except Exception as e:
            logger.error(
                f"Failed to prepare device for session {session.session_id}: {e}"
            )
            return False

    async def _cleanup_session_device(self, session: ClinicalSession):
        """Cleanup device after session."""
        try:
            device_config = session.device_configuration
            if device_config:
                # Would disconnect device, save data, etc.
                logger.info(
                    f"Device cleanup completed for session {session.session_id}"
                )
        except Exception as e:
            logger.error(f"Device cleanup failed for session {session.session_id}: {e}")

    async def _pause_session_device(self, session: ClinicalSession):
        """Pause device during session."""
        try:
            device_config = session.device_configuration
            if device_config:
                # Would pause data collection
                logger.info(f"Device paused for session {session.session_id}")
        except Exception as e:
            logger.error(f"Device pause failed for session {session.session_id}: {e}")

    async def _resume_session_device(self, session: ClinicalSession):
        """Resume device after pause."""
        try:
            device_config = session.device_configuration
            if device_config:
                # Would resume data collection
                logger.info(f"Device resumed for session {session.session_id}")
        except Exception as e:
            logger.error(f"Device resume failed for session {session.session_id}: {e}")

    async def _get_device_performance(self, session: ClinicalSession) -> Dict[str, Any]:
        """Get device performance metrics."""
        # Placeholder implementation
        return {
            "signal_quality": "good",
            "connection_stable": True,
            "data_rate": 256.0,
            "last_update": datetime.now(timezone.utc).isoformat(),
        }

    async def _calculate_session_outcomes(
        self, session: ClinicalSession
    ) -> List[OutcomeMeasure]:
        """Calculate session outcome measures."""
        outcomes = []

        # Example outcome measures
        if session.actual_start and session.actual_end:
            duration = (session.actual_end - session.actual_start).total_seconds() / 60

            outcomes.append(
                OutcomeMeasure(
                    session_id=session.session_id,
                    measure_type="session_duration",
                    value=duration,
                    unit="minutes",
                    notes="Actual session duration",
                )
            )

        # Add safety event count
        outcomes.append(
            OutcomeMeasure(
                session_id=session.session_id,
                measure_type="safety_events",
                value=len(session.safety_events),
                unit="count",
                notes="Number of safety events during session",
            )
        )

        return outcomes

    async def _notify_session_callbacks(self, event_type: str, data: Any):
        """Notify registered callbacks of session events."""
        if event_type in self._session_callbacks:
            for callback in self._session_callbacks[event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data)
                    else:
                        callback(data)
                except Exception as e:
                    logger.error(f"Error in session callback {event_type}: {e}")

    async def _log_session_event(self, session_id: str, event_type: str, details: dict):
        """Log session event to audit trail."""
        if self.neural_ledger:
            await self.neural_ledger.log_event(
                event_type=f"clinical_session_{event_type}",
                session_id=session_id,
                details=details,
                timestamp=datetime.now(timezone.utc),
            )
        else:
            logger.info(f"Session audit log: {session_id} - {event_type}: {details}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get session management statistics."""
        return {
            "active_sessions": len(self._active_sessions),
            "completed_sessions": len(self._session_history),
            "monitoring_tasks": len(self._monitoring_tasks),
            "total_sessions": len(self._active_sessions) + len(self._session_history),
        }
