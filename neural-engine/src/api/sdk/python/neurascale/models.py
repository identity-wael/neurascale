"""NeuraScale SDK data models."""

from typing import Optional, List, Dict, Any, Generic, TypeVar
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

T = TypeVar("T")


class DeviceType(str, Enum):
    """Device type enumeration."""

    EEG = "EEG"
    EMG = "EMG"
    ECG = "ECG"
    fNIRS = "fNIRS"
    TMS = "TMS"
    tDCS = "tDCS"
    HYBRID = "HYBRID"


class DeviceStatus(str, Enum):
    """Device status enumeration."""

    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    MAINTENANCE = "MAINTENANCE"
    ERROR = "ERROR"


class SessionStatus(str, Enum):
    """Session status enumeration."""

    PREPARING = "PREPARING"
    RECORDING = "RECORDING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Device(BaseModel):
    """Device model."""

    id: str
    name: str
    type: DeviceType
    status: DeviceStatus
    serial_number: str
    firmware_version: str
    last_seen: datetime
    channel_count: int
    sampling_rate: int
    calibration: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DeviceCreate(BaseModel):
    """Device creation model."""

    name: str
    type: DeviceType
    serial_number: str
    firmware_version: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DeviceUpdate(BaseModel):
    """Device update model."""

    name: Optional[str] = None
    status: Optional[DeviceStatus] = None
    firmware_version: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Session(BaseModel):
    """Session model."""

    id: str
    patient_id: str
    device_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    status: SessionStatus
    channel_count: int
    sampling_rate: int
    metadata: Dict[str, Any] = Field(default_factory=dict)
    data_size: Optional[int] = None


class SessionCreate(BaseModel):
    """Session creation model."""

    patient_id: str
    device_id: str
    channel_count: int
    sampling_rate: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Patient(BaseModel):
    """Patient model."""

    id: str
    external_id: str
    created_at: datetime
    metadata: Dict[str, Any]


class PatientCreate(BaseModel):
    """Patient creation model."""

    external_id: str
    metadata: Dict[str, Any]


class NeuralData(BaseModel):
    """Neural data model."""

    session_id: str
    start_time: float
    end_time: float
    channels: List[int]
    sampling_rate: int
    data_shape: List[int]
    data_url: Optional[str] = None
    statistics: Optional[Dict[str, Any]] = None


class Analysis(BaseModel):
    """Analysis model."""

    id: str
    session_id: str
    type: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    results: Optional[Dict[str, Any]] = None


class MLModel(BaseModel):
    """ML model."""

    id: str
    name: str
    type: str
    version: str
    status: str
    accuracy: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""

    items: List[T]
    total: int
    page: int
    size: int
    pages: int
