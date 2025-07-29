"""Session resolver implementation."""

from typing import Optional, List, Dict
from datetime import datetime, timedelta
import logging
import random

from ..schema.types import (
    Session,
    SessionConnection,
    SessionEdge,
    PageInfo,
    SessionFilter,
    PaginationInput,
    SessionStatus,
)

logger = logging.getLogger(__name__)


class SessionResolver:
    """Resolver for session-related queries."""

    def __init__(self):
        """Initialize session resolver."""
        self.sessions_db = self._create_mock_sessions()

    def _create_mock_sessions(self) -> Dict[str, Session]:
        """Create mock sessions for testing."""
        sessions = {}
        statuses = list(SessionStatus)

        for i in range(100):
            session_id = f"ses_{i + 1:06d}"

            # Generate realistic timestamps
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            start_time = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago)

            # Set duration based on status
            status = statuses[i % len(statuses)]
            if status in [SessionStatus.COMPLETED, SessionStatus.FAILED]:
                duration = random.uniform(300, 3600)  # 5 minutes to 1 hour
                end_time = start_time + timedelta(seconds=duration)
            else:
                duration = None
                end_time = None

            session = Session(
                id=session_id,
                patient_id=f"pat_{(i % 50) + 1:03d}",
                device_id=f"dev_{(i % 25) + 1:03d}",
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                status=status,
                channel_count=32 if i % 2 == 0 else 64,
                sampling_rate=256 if i % 3 == 0 else 512,
                data_size=int(duration * 32 * 256 * 4) if duration else None,  # bytes
            )
            sessions[session_id] = session

        return sessions

    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID."""
        return self.sessions_db.get(session_id)

    async def list_sessions(
        self,
        filter: Optional[SessionFilter] = None,
        pagination: Optional[PaginationInput] = None,
    ) -> SessionConnection:
        """List sessions with filtering and pagination."""
        # Apply filters
        filtered_sessions = list(self.sessions_db.values())

        if filter:
            if filter.patient_id:
                filtered_sessions = [
                    s for s in filtered_sessions if s.patient_id == filter.patient_id
                ]
            if filter.device_id:
                filtered_sessions = [
                    s for s in filtered_sessions if s.device_id == filter.device_id
                ]
            if filter.status:
                filtered_sessions = [
                    s for s in filtered_sessions if s.status == filter.status
                ]
            if filter.start_date:
                filtered_sessions = [
                    s for s in filtered_sessions if s.start_time >= filter.start_date
                ]
            if filter.end_date:
                filtered_sessions = [
                    s for s in filtered_sessions if s.start_time <= filter.end_date
                ]

        # Sort by start time (newest first)
        filtered_sessions.sort(key=lambda s: s.start_time, reverse=True)

        # Apply pagination
        total_count = len(filtered_sessions)

        # Default pagination
        if not pagination:
            pagination = PaginationInput(first=20)

        # Calculate slice indices
        if pagination.first is not None:
            start_idx = 0
            if pagination.after:
                # Find the index after the cursor
                for i, session in enumerate(filtered_sessions):
                    if session.id == pagination.after:
                        start_idx = i + 1
                        break

            end_idx = min(start_idx + pagination.first, total_count)
            page_sessions = filtered_sessions[start_idx:end_idx]

        elif pagination.last is not None:
            end_idx = total_count
            if pagination.before:
                # Find the index before the cursor
                for i, session in enumerate(filtered_sessions):
                    if session.id == pagination.before:
                        end_idx = i
                        break

            start_idx = max(0, end_idx - pagination.last)
            page_sessions = filtered_sessions[start_idx:end_idx]
        else:
            # Default to first 20
            page_sessions = filtered_sessions[:20]

        # Create edges
        edges = [
            SessionEdge(node=session, cursor=session.id) for session in page_sessions
        ]

        # Create page info
        has_previous = start_idx > 0 if "start_idx" in locals() else False
        has_next = (
            end_idx < total_count
            if "end_idx" in locals()
            else len(page_sessions) < total_count
        )

        page_info = PageInfo(
            has_next_page=has_next,
            has_previous_page=has_previous,
            start_cursor=edges[0].cursor if edges else None,
            end_cursor=edges[-1].cursor if edges else None,
        )

        return SessionConnection(
            edges=edges,
            page_info=page_info,
            total_count=total_count,
        )

    async def get_active_sessions(self) -> List[Session]:
        """Get all currently active (recording/paused) sessions."""
        active_sessions = [
            session
            for session in self.sessions_db.values()
            if session.status in [SessionStatus.RECORDING, SessionStatus.PAUSED]
        ]

        # Sort by start time
        active_sessions.sort(key=lambda s: s.start_time, reverse=True)

        return active_sessions
