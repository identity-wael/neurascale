"""Clinical session scheduling and resource management."""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, NamedTuple
from uuid import uuid4
from dataclasses import dataclass

from ..types import ClinicalConfig

logger = logging.getLogger(__name__)


class TimeRange(NamedTuple):
    """Time range for scheduling."""

    start: datetime
    end: datetime


@dataclass
class SchedulingConflict:
    """Scheduling conflict information."""

    conflict_type: str
    resource_id: str
    existing_appointment_id: str
    conflicting_time: TimeRange
    description: str


@dataclass
class Appointment:
    """Clinical appointment record."""

    appointment_id: str
    session_id: str
    patient_id: str
    provider_id: str
    device_id: Optional[str]
    scheduled_time: TimeRange
    status: str = "scheduled"  # scheduled, confirmed, cancelled, rescheduled
    created_date: Optional[datetime] = None
    notes: str = ""

    def __post_init__(self) -> None:
        if self.created_date is None:
            self.created_date = datetime.now(timezone.utc)


@dataclass
class ResourceAvailability:
    """Resource availability information."""

    resource_id: str
    resource_type: str  # provider, device, room
    available_slots: List[TimeRange]
    blocked_slots: List[TimeRange]
    maintenance_windows: List[TimeRange]


class SchedulingService:
    """Manages clinical session scheduling and resource allocation.

    Handles appointment booking, conflict resolution, resource management,
    and schedule optimization for clinical BCI sessions.
    """

    def __init__(self, config: ClinicalConfig):
        """Initialize scheduling service."""
        self.config = config

        # Scheduling storage (would be database in production)
        self._appointments: Dict[str, Appointment] = {}
        self._provider_schedules: Dict[str, List[TimeRange]] = {}
        self._device_schedules: Dict[str, List[TimeRange]] = {}
        self._room_schedules: Dict[str, List[TimeRange]] = {}

        # Scheduling constraints
        self.business_hours = self._load_business_hours()
        self.scheduling_rules = self._load_scheduling_rules()

        logger.info("Scheduling service initialized")

    async def check_provider_availability(
        self, provider_id: str, time_range: TimeRange
    ) -> ResourceAvailability:
        """Check provider availability for given time range.

        Args:
            provider_id: Provider identifier
            time_range: Requested time range

        Returns:
            Provider availability information
        """
        # Get provider's existing appointments
        existing_appointments = [
            apt
            for apt in self._appointments.values()
            if apt.provider_id == provider_id
            and apt.status in ["scheduled", "confirmed"]
        ]

        # Calculate blocked slots
        blocked_slots = []
        for appointment in existing_appointments:
            blocked_slots.append(appointment.scheduled_time)

        # Calculate available slots within business hours
        available_slots = self._calculate_available_slots(
            time_range, blocked_slots, self.business_hours
        )

        return ResourceAvailability(
            resource_id=provider_id,
            resource_type="provider",
            available_slots=available_slots,
            blocked_slots=blocked_slots,
            maintenance_windows=[],  # Providers don't have maintenance windows
        )

    async def check_device_availability(
        self, device_type: str, time_range: TimeRange
    ) -> ResourceAvailability:
        """Check device availability for given time range.

        Args:
            device_type: Type of device required
            time_range: Requested time range

        Returns:
            Device availability information
        """
        # Find devices of the requested type
        available_devices = self._get_devices_by_type(device_type)

        if not available_devices:
            return ResourceAvailability(
                resource_id="none",
                resource_type="device",
                available_slots=[],
                blocked_slots=[],
                maintenance_windows=[],
            )

        # Find device with best availability
        best_device_id = None
        best_availability = None

        for device_id in available_devices:
            # Get device's existing appointments
            device_appointments = [
                apt
                for apt in self._appointments.values()
                if apt.device_id == device_id
                and apt.status in ["scheduled", "confirmed"]
            ]

            blocked_slots = [apt.scheduled_time for apt in device_appointments]

            # Add maintenance windows
            maintenance_windows = self._get_device_maintenance_windows(
                device_id, time_range
            )

            available_slots = self._calculate_available_slots(
                time_range, blocked_slots + maintenance_windows, self.business_hours
            )

            if not best_availability or len(available_slots) > len(
                best_availability.available_slots
            ):
                best_device_id = device_id
                logger.debug(f"Selected best device: {best_device_id}")
                best_availability = ResourceAvailability(
                    resource_id=device_id,
                    resource_type="device",
                    available_slots=available_slots,
                    blocked_slots=blocked_slots,
                    maintenance_windows=maintenance_windows,
                )

        return best_availability or ResourceAvailability(
            resource_id="none",
            resource_type="device",
            available_slots=[],
            blocked_slots=[],
            maintenance_windows=[],
        )

    async def schedule_session(self, session_request: dict) -> Appointment:
        """Schedule clinical session with resource allocation.

        Args:
            session_request: Session scheduling request

        Returns:
            Created appointment

        Raises:
            ValueError: If scheduling conflicts exist
        """
        try:
            # Validate request
            required_fields = [
                "session_id",
                "patient_id",
                "provider_id",
                "start_time",
                "duration_minutes",
            ]
            for field in required_fields:
                if field not in session_request:
                    raise ValueError(f"Missing required field: {field}")

            # Parse scheduling parameters
            start_time = session_request["start_time"]
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time)

            duration = timedelta(minutes=session_request["duration_minutes"])
            end_time = start_time + duration
            time_range = TimeRange(start_time, end_time)

            # Check for scheduling conflicts
            conflicts = await self._check_scheduling_conflicts(
                session_request, time_range
            )

            if conflicts:
                conflict_descriptions = [c.description for c in conflicts]
                raise ValueError(
                    f"Scheduling conflicts: {'; '.join(conflict_descriptions)}"
                )

            # Allocate device if required
            device_id = None
            if "device_requirements" in session_request:
                device_type = session_request["device_requirements"].get("type")
                if device_type:
                    device_availability = await self.check_device_availability(
                        device_type, time_range
                    )
                    if device_availability.available_slots:
                        device_id = device_availability.resource_id
                    else:
                        raise ValueError(
                            f"No {device_type} devices available for requested time"
                        )

            # Create appointment
            appointment = Appointment(
                appointment_id=str(uuid4()),
                session_id=session_request["session_id"],
                patient_id=session_request["patient_id"],
                provider_id=session_request["provider_id"],
                device_id=device_id,
                scheduled_time=time_range,
                notes=session_request.get("notes", ""),
            )

            # Store appointment
            self._appointments[appointment.appointment_id] = appointment

            logger.info(
                f"Session scheduled: {appointment.appointment_id} for {start_time}"
            )

            return appointment

        except Exception as e:
            logger.error(f"Failed to schedule session: {e}")
            raise

    async def handle_scheduling_conflicts(
        self, conflicts: List[SchedulingConflict]
    ) -> Dict[str, Any]:
        """Handle and resolve scheduling conflicts.

        Args:
            conflicts: List of scheduling conflicts

        Returns:
            Conflict resolution result
        """
        resolution_result: Dict[str, Any] = {
            "resolved_conflicts": [],
            "unresolved_conflicts": [],
            "suggested_alternatives": [],
            "actions_taken": [],
        }

        for conflict in conflicts:
            try:
                if conflict.conflict_type == "provider_double_booking":
                    # Try to reschedule conflicting appointment
                    alternative_slots = await self._find_alternative_slots(conflict)
                    if alternative_slots:
                        resolution_result["suggested_alternatives"].extend(
                            alternative_slots
                        )
                        resolution_result["resolved_conflicts"].append(conflict)
                    else:
                        resolution_result["unresolved_conflicts"].append(conflict)

                elif conflict.conflict_type == "device_conflict":
                    # Try to find alternative device
                    alternative_devices = await self._find_alternative_devices(conflict)
                    if alternative_devices:
                        resolution_result["suggested_alternatives"].extend(
                            alternative_devices
                        )
                        resolution_result["resolved_conflicts"].append(conflict)
                    else:
                        resolution_result["unresolved_conflicts"].append(conflict)

                elif conflict.conflict_type == "maintenance_window":
                    # Suggest rescheduling around maintenance
                    alternative_times = await self._suggest_alternative_times(conflict)
                    resolution_result["suggested_alternatives"].extend(
                        alternative_times
                    )
                    resolution_result["resolved_conflicts"].append(conflict)

                else:
                    resolution_result["unresolved_conflicts"].append(conflict)

            except Exception as e:
                logger.error(f"Error resolving conflict {conflict.conflict_type}: {e}")
                resolution_result["unresolved_conflicts"].append(conflict)

        return resolution_result

    async def reschedule_appointment(
        self, appointment_id: str, new_time_range: TimeRange
    ) -> bool:
        """Reschedule existing appointment.

        Args:
            appointment_id: Appointment identifier
            new_time_range: New time range

        Returns:
            Success status
        """
        if appointment_id not in self._appointments:
            return False

        appointment = self._appointments[appointment_id]

        try:
            # Check for conflicts at new time
            session_request = {
                "session_id": appointment.session_id,
                "patient_id": appointment.patient_id,
                "provider_id": appointment.provider_id,
                "start_time": new_time_range.start,
                "duration_minutes": int(
                    (new_time_range.end - new_time_range.start).total_seconds() / 60
                ),
            }

            conflicts = await self._check_scheduling_conflicts(
                session_request, new_time_range
            )

            if conflicts:
                return False

            # Update appointment
            appointment.scheduled_time = new_time_range
            appointment.status = "rescheduled"

            logger.info(
                f"Appointment rescheduled: {appointment_id} to {new_time_range.start}"
            )

            return True

        except Exception as e:
            logger.error(f"Failed to reschedule appointment {appointment_id}: {e}")
            return False

    async def cancel_appointment(self, appointment_id: str, reason: str = "") -> bool:
        """Cancel scheduled appointment.

        Args:
            appointment_id: Appointment identifier
            reason: Cancellation reason

        Returns:
            Success status
        """
        if appointment_id not in self._appointments:
            return False

        appointment = self._appointments[appointment_id]
        appointment.status = "cancelled"
        appointment.notes += f" CANCELLED: {reason}"

        logger.info(f"Appointment cancelled: {appointment_id}, reason: {reason}")

        return True

    async def get_schedule(
        self, resource_id: str, date_range: TimeRange
    ) -> List[Appointment]:
        """Get schedule for resource within date range.

        Args:
            resource_id: Resource identifier (provider, device, etc.)
            date_range: Date range to query

        Returns:
            List of appointments in range
        """
        appointments = []

        for appointment in self._appointments.values():
            # Check if appointment overlaps with date range
            if (
                appointment.scheduled_time.start < date_range.end
                and appointment.scheduled_time.end > date_range.start
            ):

                # Check if resource is involved
                if (
                    appointment.provider_id == resource_id
                    or appointment.device_id == resource_id
                ):
                    appointments.append(appointment)

        # Sort by start time
        appointments.sort(key=lambda a: a.scheduled_time.start)

        return appointments

    async def find_optimal_scheduling_time(
        self, session_request: dict, preferences: Optional[dict] = None
    ) -> List[TimeRange]:
        """Find optimal scheduling times based on availability and preferences.

        Args:
            session_request: Session requirements
            preferences: Scheduling preferences

        Returns:
            List of optimal time slots
        """
        preferences = preferences or {}

        # Define search parameters
        search_start = preferences.get(
            "earliest_start", datetime.now(timezone.utc) + timedelta(hours=1)
        )
        search_end = preferences.get("latest_end", search_start + timedelta(days=30))
        duration_minutes = session_request["duration_minutes"]

        # Check provider availability
        provider_availability = await self.check_provider_availability(
            session_request["provider_id"], TimeRange(search_start, search_end)
        )

        # Check device availability if required
        device_availability = None
        if "device_requirements" in session_request:
            device_type = session_request["device_requirements"].get("type")
            if device_type:
                device_availability = await self.check_device_availability(
                    device_type, TimeRange(search_start, search_end)
                )

        # Find overlapping available slots
        optimal_slots = []

        for provider_slot in provider_availability.available_slots:
            # Check if slot is long enough
            slot_duration = (
                provider_slot.end - provider_slot.start
            ).total_seconds() / 60
            if slot_duration < duration_minutes:
                continue

            # Check device availability if required
            if device_availability:
                device_available = any(
                    device_slot.start <= provider_slot.start
                    and device_slot.end >= provider_slot.end
                    for device_slot in device_availability.available_slots
                )
                if not device_available:
                    continue

            # Add to optimal slots
            session_end = provider_slot.start + timedelta(minutes=duration_minutes)
            if session_end <= provider_slot.end:
                optimal_slots.append(TimeRange(provider_slot.start, session_end))

        # Sort by preference (e.g., prefer morning slots)
        preferred_time = preferences.get("preferred_time", "morning")
        optimal_slots.sort(
            key=lambda slot: self._calculate_time_preference_score(slot, preferred_time)
        )

        return optimal_slots[:10]  # Return top 10 options

    def _calculate_available_slots(
        self,
        time_range: TimeRange,
        blocked_slots: List[TimeRange],
        business_hours: Dict[str, TimeRange],
    ) -> List[TimeRange]:
        """Calculate available time slots within constraints."""
        available_slots = []

        # Get business hours for the date range
        current_date = time_range.start.date()
        end_date = time_range.end.date()

        while current_date <= end_date:
            day_name = current_date.strftime("%A").lower()

            if day_name in business_hours:
                day_hours = business_hours[day_name]

                # Create datetime objects for this day
                day_start = datetime.combine(
                    current_date, day_hours.start.time()
                ).replace(tzinfo=timezone.utc)
                day_end = datetime.combine(current_date, day_hours.end.time()).replace(
                    tzinfo=timezone.utc
                )

                # Adjust for requested time range
                slot_start = max(day_start, time_range.start)
                slot_end = min(day_end, time_range.end)

                if slot_start < slot_end:
                    # Remove blocked periods
                    available_periods = self._subtract_blocked_periods(
                        TimeRange(slot_start, slot_end), blocked_slots
                    )
                    available_slots.extend(available_periods)

            current_date += timedelta(days=1)

        return available_slots

    def _subtract_blocked_periods(
        self, available_period: TimeRange, blocked_slots: List[TimeRange]
    ) -> List[TimeRange]:
        """Subtract blocked periods from available period."""
        result = [available_period]

        for blocked in blocked_slots:
            new_result = []

            for period in result:
                # Check for overlap
                if blocked.start >= period.end or blocked.end <= period.start:
                    # No overlap
                    new_result.append(period)
                else:
                    # Overlap exists, split the period
                    if period.start < blocked.start:
                        # Add period before blocked time
                        new_result.append(TimeRange(period.start, blocked.start))

                    if period.end > blocked.end:
                        # Add period after blocked time
                        new_result.append(TimeRange(blocked.end, period.end))

            result = new_result

        return result

    async def _check_scheduling_conflicts(
        self, session_request: dict, time_range: TimeRange
    ) -> List[SchedulingConflict]:
        """Check for scheduling conflicts."""
        conflicts = []

        # Check provider conflicts
        provider_id = session_request["provider_id"]
        provider_appointments = [
            apt
            for apt in self._appointments.values()
            if apt.provider_id == provider_id
            and apt.status in ["scheduled", "confirmed"]
        ]

        for appointment in provider_appointments:
            if self._time_ranges_overlap(time_range, appointment.scheduled_time):
                conflicts.append(
                    SchedulingConflict(
                        conflict_type="provider_double_booking",
                        resource_id=provider_id,
                        existing_appointment_id=appointment.appointment_id,
                        conflicting_time=appointment.scheduled_time,
                        description=f"Provider {provider_id} already scheduled during this time",
                    )
                )

        # Check device conflicts if device required
        if "device_requirements" in session_request:
            device_type = session_request["device_requirements"].get("type")
            if device_type:
                device_availability = await self.check_device_availability(
                    device_type, time_range
                )

                if not device_availability.available_slots:
                    conflicts.append(
                        SchedulingConflict(
                            conflict_type="device_conflict",
                            resource_id=device_type,
                            existing_appointment_id="",
                            conflicting_time=time_range,
                            description=f"No {device_type} devices available during requested time",
                        )
                    )

        return conflicts

    def _time_ranges_overlap(self, range1: TimeRange, range2: TimeRange) -> bool:
        """Check if two time ranges overlap."""
        return range1.start < range2.end and range1.end > range2.start

    async def _find_alternative_slots(self, conflict: SchedulingConflict) -> List[dict]:
        """Find alternative time slots for scheduling conflict."""
        # Simplified implementation
        alternatives = []

        # Suggest slots 1 hour before and after the conflict
        conflict_start = conflict.conflicting_time.start
        conflict_end = conflict.conflicting_time.end
        duration = conflict_end - conflict_start

        # Before conflict
        alt_start = conflict_start - duration - timedelta(hours=1)
        if alt_start > datetime.now(timezone.utc):
            alternatives.append(
                {
                    "type": "alternative_time",
                    "start_time": alt_start,
                    "end_time": alt_start + duration,
                    "description": "Earlier time slot",
                }
            )

        # After conflict
        alt_start = conflict_end + timedelta(hours=1)
        alternatives.append(
            {
                "type": "alternative_time",
                "start_time": alt_start,
                "end_time": alt_start + duration,
                "description": "Later time slot",
            }
        )

        return alternatives

    async def _find_alternative_devices(
        self, conflict: SchedulingConflict
    ) -> List[dict]:
        """Find alternative devices for scheduling conflict."""
        # Simplified implementation
        alternatives = []

        # In production, would query available devices of same type
        alternatives.append(
            {
                "type": "alternative_device",
                "device_id": f"alt_{conflict.resource_id}",
                "description": "Alternative device of same type",
            }
        )

        return alternatives

    async def _suggest_alternative_times(
        self, conflict: SchedulingConflict
    ) -> List[dict]:
        """Suggest alternative times around maintenance windows."""
        alternatives = []

        # Suggest times before and after maintenance window
        maint_start = conflict.conflicting_time.start
        maint_end = conflict.conflicting_time.end

        # Before maintenance
        alt_end = maint_start - timedelta(minutes=30)  # 30 min buffer
        alt_start = alt_end - timedelta(hours=1)  # Assume 1 hour session

        if alt_start > datetime.now(timezone.utc):
            alternatives.append(
                {
                    "type": "alternative_time",
                    "start_time": alt_start,
                    "end_time": alt_end,
                    "description": "Before maintenance window",
                }
            )

        # After maintenance
        alt_start = maint_end + timedelta(minutes=30)  # 30 min buffer
        alt_end = alt_start + timedelta(hours=1)

        alternatives.append(
            {
                "type": "alternative_time",
                "start_time": alt_start,
                "end_time": alt_end,
                "description": "After maintenance window",
            }
        )

        return alternatives

    def _calculate_time_preference_score(
        self, time_slot: TimeRange, preference: str
    ) -> float:
        """Calculate preference score for time slot."""
        hour = time_slot.start.hour

        if preference == "morning":
            # Prefer 8-12
            if 8 <= hour < 12:
                return hour - 8  # Earlier is better
            else:
                return abs(hour - 10) + 10  # Penalty for non-morning

        elif preference == "afternoon":
            # Prefer 12-17
            if 12 <= hour < 17:
                return hour - 12
            else:
                return abs(hour - 14) + 10

        elif preference == "evening":
            # Prefer 17-20
            if 17 <= hour < 20:
                return hour - 17
            else:
                return abs(hour - 18) + 10

        return 0

    def _get_devices_by_type(self, device_type: str) -> List[str]:
        """Get list of devices by type."""
        # In production, would query device registry
        return [f"{device_type}_001", f"{device_type}_002", f"{device_type}_003"]

    def _get_device_maintenance_windows(
        self, device_id: str, time_range: TimeRange
    ) -> List[TimeRange]:
        """Get device maintenance windows within time range."""
        # Simplified implementation - in production would query maintenance schedule
        return []

    def _load_business_hours(self) -> Dict[str, TimeRange]:
        """Load business hours configuration."""
        # Standard business hours
        standard_hours = TimeRange(
            datetime.now().replace(hour=8, minute=0, second=0, microsecond=0),
            datetime.now().replace(hour=17, minute=0, second=0, microsecond=0),
        )

        return {
            "monday": standard_hours,
            "tuesday": standard_hours,
            "wednesday": standard_hours,
            "thursday": standard_hours,
            "friday": standard_hours,
            # Weekend hours could be different or None
        }

    def _load_scheduling_rules(self) -> Dict[str, Any]:
        """Load scheduling rules and constraints."""
        return {
            "min_advance_booking_hours": 2,
            "max_advance_booking_days": 90,
            "session_buffer_minutes": 15,
            "max_sessions_per_day": 8,
            "provider_break_minutes": 30,
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get scheduling service statistics."""
        total_appointments = len(self._appointments)
        active_appointments = sum(
            1
            for apt in self._appointments.values()
            if apt.status in ["scheduled", "confirmed"]
        )

        return {
            "total_appointments": total_appointments,
            "active_appointments": active_appointments,
            "cancelled_appointments": sum(
                1 for apt in self._appointments.values() if apt.status == "cancelled"
            ),
            "providers_scheduled": len(
                set(apt.provider_id for apt in self._appointments.values())
            ),
            "devices_scheduled": len(
                set(
                    apt.device_id
                    for apt in self._appointments.values()
                    if apt.device_id
                )
            ),
        }
