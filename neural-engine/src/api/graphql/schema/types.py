"""GraphQL type definitions."""

import strawberry
from typing import List, Optional
from datetime import datetime
from enum import Enum


@strawberry.enum
class DeviceType(Enum):
    """Device type enumeration."""

    EEG = "EEG"
    EMG = "EMG"
    ECG = "ECG"
    fNIRS = "fNIRS"
    TMS = "TMS"
    tDCS = "tDCS"
    HYBRID = "HYBRID"


@strawberry.enum
class DeviceStatus(Enum):
    """Device status enumeration."""

    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    MAINTENANCE = "MAINTENANCE"
    ERROR = "ERROR"


@strawberry.enum
class SessionStatus(Enum):
    """Session status enumeration."""

    PREPARING = "PREPARING"
    RECORDING = "RECORDING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@strawberry.type
class Device:
    """Device type."""

    id: str
    name: str
    type: DeviceType
    status: DeviceStatus
    serial_number: str
    firmware_version: str
    last_seen: datetime
    channel_count: int
    sampling_rate: int

    @strawberry.field
    async def sessions(self, limit: int = 10) -> List["Session"]:
        """Get recent sessions for this device."""
        # In production, would fetch from database
        return []

    @strawberry.field
    async def calibration(self) -> Optional["DeviceCalibration"]:
        """Get current calibration."""
        return None


@strawberry.type
class DeviceCalibration:
    """Device calibration type."""

    timestamp: datetime
    valid_until: Optional[datetime]
    performed_by: str
    parameters: strawberry.scalars.JSON


@strawberry.type
class Session:
    """Recording session type."""

    id: str
    patient_id: str
    device_id: str
    start_time: datetime
    end_time: Optional[datetime]
    duration: Optional[float]
    status: SessionStatus
    channel_count: int
    sampling_rate: int
    data_size: Optional[int]

    @strawberry.field
    async def device(self) -> Optional[Device]:
        """Get session device."""
        # Would use DataLoader in production
        return None

    @strawberry.field
    async def patient(self) -> Optional["Patient"]:
        """Get session patient."""
        return None

    @strawberry.field
    async def neural_data(
        self,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        channels: Optional[List[int]] = None,
    ) -> Optional["NeuralData"]:
        """Get neural data for time range."""
        return None


@strawberry.type
class Patient:
    """Patient type."""

    id: str
    external_id: str
    created_at: datetime
    metadata: strawberry.scalars.JSON

    @strawberry.field
    async def sessions(self, limit: int = 10, offset: int = 0) -> List[Session]:
        """Get patient sessions."""
        return []

    @strawberry.field
    async def treatments(self) -> List["Treatment"]:
        """Get patient treatments."""
        return []


@strawberry.type
class NeuralData:
    """Neural data type."""

    session_id: str
    start_time: float
    end_time: float
    channels: List[int]
    sampling_rate: int
    data_shape: List[int]
    statistics: Optional["DataStatistics"]

    @strawberry.field
    async def download_url(self) -> str:
        """Get download URL for binary data."""
        return f"/api/v2/neural-data/sessions/{self.session_id}/download"


@strawberry.type
class DataStatistics:
    """Data statistics type."""

    mean: float
    std: float
    min: float
    max: float
    rms: float
    zero_crossings: int
    peak_frequency: Optional[float]


@strawberry.type
class Treatment:
    """Treatment type."""

    id: str
    patient_id: str
    name: str
    start_date: datetime
    end_date: Optional[datetime]
    status: str
    parameters: strawberry.scalars.JSON


@strawberry.type
class Analysis:
    """Analysis type."""

    id: str
    session_id: str
    type: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    results: Optional[strawberry.scalars.JSON]

    @strawberry.field
    async def session(self) -> Optional[Session]:
        """Get analysis session."""
        return None

    @strawberry.field
    async def visualizations(self) -> List["Visualization"]:
        """Get analysis visualizations."""
        return []


@strawberry.type
class Visualization:
    """Visualization type."""

    id: str
    analysis_id: str
    type: str
    title: str
    config: strawberry.scalars.JSON
    data_url: str


@strawberry.type
class MLModel:
    """ML model type."""

    id: str
    name: str
    type: str
    version: str
    status: str
    accuracy: Optional[float]
    created_at: datetime
    updated_at: datetime

    @strawberry.field
    async def metrics(self) -> "ModelMetrics":
        """Get model metrics."""
        return ModelMetrics(
            accuracy=0.95,
            precision=0.94,
            recall=0.96,
            f1_score=0.95,
            confusion_matrix=[[100, 5], [3, 92]],
        )


@strawberry.type
class ModelMetrics:
    """Model metrics type."""

    accuracy: float
    precision: float
    recall: float
    f1_score: float
    confusion_matrix: List[List[int]]


@strawberry.type
class PageInfo:
    """Pagination information."""

    has_next_page: bool
    has_previous_page: bool
    start_cursor: Optional[str]
    end_cursor: Optional[str]


@strawberry.type
class DeviceConnection:
    """Device connection for pagination."""

    edges: List["DeviceEdge"]
    page_info: PageInfo
    total_count: int


@strawberry.type
class DeviceEdge:
    """Device edge for pagination."""

    node: Device
    cursor: str


@strawberry.type
class SessionConnection:
    """Session connection for pagination."""

    edges: List["SessionEdge"]
    page_info: PageInfo
    total_count: int


@strawberry.type
class SessionEdge:
    """Session edge for pagination."""

    node: Session
    cursor: str


# Input types
@strawberry.input
class DeviceFilter:
    """Device filter input."""

    type: Optional[DeviceType] = None
    status: Optional[DeviceStatus] = None
    search: Optional[str] = None


@strawberry.input
class SessionFilter:
    """Session filter input."""

    patient_id: Optional[str] = None
    device_id: Optional[str] = None
    status: Optional[SessionStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


@strawberry.input
class PaginationInput:
    """Pagination input."""

    first: Optional[int] = None
    after: Optional[str] = None
    last: Optional[int] = None
    before: Optional[str] = None
