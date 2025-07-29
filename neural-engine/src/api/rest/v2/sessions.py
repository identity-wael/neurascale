"""Session management REST API endpoints."""

from fastapi import APIRouter, Query, Depends, HTTPException, Response, BackgroundTasks
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import asyncio

from ...rest.middleware.auth import get_current_user, check_permission
from ...rest.utils.pagination import PaginationParams, PaginatedResponse, paginate
from ...rest.utils.hypermedia import add_hateoas_links, create_action_links

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models
class SessionStatus(BaseModel):
    """Session status enumeration."""

    value: str = Field(..., pattern="^(PREPARING|RECORDING|PAUSED|COMPLETED|FAILED)$")


class SessionMetadata(BaseModel):
    """Session metadata."""

    experiment_type: Optional[str] = None
    protocol: Optional[str] = None
    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    environment: Dict[str, Any] = Field(default_factory=dict)


class Session(BaseModel):
    """Session model."""

    id: str
    patient_id: str
    device_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None  # seconds
    status: SessionStatus
    channel_count: int
    sampling_rate: int
    metadata: SessionMetadata
    data_size: Optional[int] = None  # bytes
    _links: Optional[Dict[str, Any]] = None
    _actions: Optional[Dict[str, Any]] = None


class SessionCreate(BaseModel):
    """Session creation model."""

    patient_id: str = Field(..., min_length=1)
    device_id: str = Field(..., min_length=1)
    channel_count: int = Field(..., ge=1, le=256)
    sampling_rate: int = Field(..., ge=128, le=10000)
    metadata: SessionMetadata = Field(default_factory=SessionMetadata)


class SessionUpdate(BaseModel):
    """Session update model."""

    status: Optional[SessionStatus] = None
    metadata: Optional[SessionMetadata] = None
    notes: Optional[str] = None


class SessionExportRequest(BaseModel):
    """Session export request."""

    format: str = Field(..., pattern="^(json|csv|edf|mat|fif)$")
    channels: Optional[List[int]] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    downsample: Optional[int] = None


# Mock data store
sessions_db: Dict[str, Session] = {}
active_sessions: Dict[str, asyncio.Task] = {}


@router.get("", response_model=PaginatedResponse[Session])
async def list_sessions(
    patient_id: Optional[str] = Query(None, description="Filter by patient ID"),
    device_id: Optional[str] = Query(None, description="Filter by device ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    pagination: PaginationParams = Depends(),
    user: Dict[str, Any] = Depends(get_current_user),
) -> PaginatedResponse[Session]:
    """
    List recording sessions with filtering.

    - **patient_id**: Filter by patient
    - **device_id**: Filter by device
    - **status**: Filter by session status
    - **start_date**: Sessions starting after this date
    - **end_date**: Sessions starting before this date
    """
    if not await check_permission(user, "sessions.read"):
        raise HTTPException(403, "Insufficient permissions")

    # Filter sessions
    filtered_sessions = []
    for session in sessions_db.values():
        if patient_id and session.patient_id != patient_id:
            continue
        if device_id and session.device_id != device_id:
            continue
        if status and session.status.value != status.upper():
            continue
        if start_date and session.start_time < start_date:
            continue
        if end_date and session.start_time > end_date:
            continue

        # Add links and actions
        session._links = add_hateoas_links(session, "session", session.id, "/api/v2")

        # Add available actions based on status
        available_actions = []
        if session.status.value == "PREPARING":
            available_actions = ["start", "cancel"]
        elif session.status.value == "RECORDING":
            available_actions = ["pause", "stop"]
        elif session.status.value == "PAUSED":
            available_actions = ["resume", "stop"]
        elif session.status.value == "COMPLETED":
            available_actions = ["export", "analyze"]

        session._actions = create_action_links(
            "session", session.id, available_actions, "/api/v2"
        )

        filtered_sessions.append(session)

    return paginate(filtered_sessions, pagination, "/api/v2/sessions")


@router.post("", response_model=Session, status_code=201)
async def create_session(
    session_data: SessionCreate,
    background_tasks: BackgroundTasks,
    user: Dict[str, Any] = Depends(get_current_user),
) -> Session:
    """Create a new recording session."""
    if not await check_permission(user, "sessions.create"):
        raise HTTPException(403, "Insufficient permissions")

    # Generate session ID
    session_id = f"ses_{len(sessions_db) + 1:06d}"

    # Create session
    new_session = Session(
        id=session_id,
        patient_id=session_data.patient_id,
        device_id=session_data.device_id,
        start_time=datetime.utcnow(),
        status=SessionStatus(value="PREPARING"),
        channel_count=session_data.channel_count,
        sampling_rate=session_data.sampling_rate,
        metadata=session_data.metadata,
    )

    # Add links and actions
    new_session._links = add_hateoas_links(
        new_session, "session", session_id, "/api/v2"
    )
    new_session._actions = create_action_links(
        "session", session_id, ["start", "cancel"], "/api/v2"
    )

    # Store session
    sessions_db[session_id] = new_session

    # Start background preparation
    background_tasks.add_task(prepare_session, session_id)

    logger.info(f"Created session {session_id} by user {user.get('sub')}")

    return new_session


@router.get("/{session_id}", response_model=Session)
async def get_session(
    session_id: str,
    include_data: bool = Query(False, description="Include data summary"),
    user: Dict[str, Any] = Depends(get_current_user),
) -> Session:
    """Get a specific session by ID."""
    if not await check_permission(user, "sessions.read", session_id):
        raise HTTPException(403, "Insufficient permissions")

    session = sessions_db.get(session_id)
    if not session:
        raise HTTPException(404, f"Session not found: {session_id}")

    # Add links and actions
    session._links = add_hateoas_links(session, "session", session_id, "/api/v2")

    # Determine available actions
    available_actions = []
    if session.status.value == "PREPARING":
        available_actions = ["start", "cancel"]
    elif session.status.value == "RECORDING":
        available_actions = ["pause", "stop"]
    elif session.status.value == "PAUSED":
        available_actions = ["resume", "stop"]
    elif session.status.value == "COMPLETED":
        available_actions = ["export", "analyze"]

    session._actions = create_action_links(
        "session", session_id, available_actions, "/api/v2"
    )

    # Add data summary if requested
    if include_data and session.status.value == "COMPLETED":
        session._links["data_summary"] = {
            "href": f"/api/v2/neural-data/sessions/{session_id}/summary"
        }

    return session


@router.patch("/{session_id}", response_model=Session)
async def update_session(
    session_id: str,
    update: SessionUpdate,
    user: Dict[str, Any] = Depends(get_current_user),
) -> Session:
    """Update session metadata."""
    if not await check_permission(user, "sessions.update", session_id):
        raise HTTPException(403, "Insufficient permissions")

    session = sessions_db.get(session_id)
    if not session:
        raise HTTPException(404, f"Session not found: {session_id}")

    # Apply updates
    update_data = update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "metadata" and value:
            # Merge metadata
            for key, val in value.items():
                setattr(session.metadata, key, val)
        else:
            setattr(session, field, value)

    logger.info(f"Updated session {session_id} by user {user.get('sub')}")

    return session


@router.post("/{session_id}/start", response_model=Session)
async def start_session(
    session_id: str,
    background_tasks: BackgroundTasks,
    user: Dict[str, Any] = Depends(get_current_user),
) -> Session:
    """Start a recording session."""
    if not await check_permission(user, "sessions.control", session_id):
        raise HTTPException(403, "Insufficient permissions")

    session = sessions_db.get(session_id)
    if not session:
        raise HTTPException(404, f"Session not found: {session_id}")

    if session.status.value != "PREPARING":
        raise HTTPException(
            400, f"Cannot start session in status {session.status.value}"
        )

    # Update status
    session.status = SessionStatus(value="RECORDING")
    session.start_time = datetime.utcnow()

    # Start recording task
    task = asyncio.create_task(record_session(session_id))
    active_sessions[session_id] = task

    logger.info(f"Started session {session_id} by user {user.get('sub')}")

    return session


@router.post("/{session_id}/stop", response_model=Session)
async def stop_session(
    session_id: str,
    user: Dict[str, Any] = Depends(get_current_user),
) -> Session:
    """Stop a recording session."""
    if not await check_permission(user, "sessions.control", session_id):
        raise HTTPException(403, "Insufficient permissions")

    session = sessions_db.get(session_id)
    if not session:
        raise HTTPException(404, f"Session not found: {session_id}")

    if session.status.value not in ["RECORDING", "PAUSED"]:
        raise HTTPException(
            400, f"Cannot stop session in status {session.status.value}"
        )

    # Stop recording task if active
    if session_id in active_sessions:
        active_sessions[session_id].cancel()
        del active_sessions[session_id]

    # Update session
    session.status = SessionStatus(value="COMPLETED")
    session.end_time = datetime.utcnow()
    session.duration = (session.end_time - session.start_time).total_seconds()

    logger.info(f"Stopped session {session_id} by user {user.get('sub')}")

    return session


@router.post("/{session_id}/export")
async def export_session(
    session_id: str,
    export_request: SessionExportRequest,
    user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """Export session data in various formats."""
    if not await check_permission(user, "sessions.export", session_id):
        raise HTTPException(403, "Insufficient permissions")

    session = sessions_db.get(session_id)
    if not session:
        raise HTTPException(404, f"Session not found: {session_id}")

    if session.status.value != "COMPLETED":
        raise HTTPException(400, "Can only export completed sessions")

    # Generate export URL (in production, would trigger actual export)
    export_id = f"exp_{session_id}_{int(datetime.utcnow().timestamp())}"

    logger.info(
        f"Exported session {session_id} as {export_request.format} by user {user.get('sub')}"
    )

    return {
        "export_id": export_id,
        "format": export_request.format,
        "status": "processing",
        "estimated_time": 30,  # seconds
        "_links": {
            "self": {"href": f"/api/v2/exports/{export_id}"},
            "download": {"href": f"/api/v2/exports/{export_id}/download"},
            "status": {"href": f"/api/v2/exports/{export_id}/status"},
        },
    }


# Background tasks
async def prepare_session(session_id: str):
    """Prepare a session (mock implementation)."""
    await asyncio.sleep(2)  # Simulate preparation
    session = sessions_db.get(session_id)
    if session and session.status.value == "PREPARING":
        logger.info(f"Session {session_id} prepared")


async def record_session(session_id: str):
    """Record session data (mock implementation)."""
    try:
        session = sessions_db.get(session_id)
        data_size = 0

        while session and session.status.value == "RECORDING":
            # Simulate data recording
            await asyncio.sleep(1)
            data_size += (
                session.channel_count * session.sampling_rate * 4
            )  # 4 bytes per sample
            session.data_size = data_size

            # Check if session still exists
            session = sessions_db.get(session_id)

    except asyncio.CancelledError:
        logger.info(f"Recording cancelled for session {session_id}")
    except Exception as e:
        logger.error(f"Error recording session {session_id}: {e}")
        if session_id in sessions_db:
            sessions_db[session_id].status = SessionStatus(value="FAILED")
