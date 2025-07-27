"""
Classification types and data structures
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import numpy as np


class MentalState(Enum):
    """Mental state categories"""

    FOCUS = "focus"
    RELAXATION = "relaxation"
    STRESS = "stress"
    NEUTRAL = "neutral"
    UNKNOWN = "unknown"


class SleepStage(Enum):
    """Sleep stage categories"""

    WAKE = "wake"
    N1 = "n1"  # Light sleep
    N2 = "n2"  # Light sleep
    N3 = "n3"  # Deep sleep
    REM = "rem"  # REM sleep
    UNKNOWN = "unknown"


class MotorIntent(Enum):
    """Motor imagery categories"""

    LEFT_HAND = "left_hand"
    RIGHT_HAND = "right_hand"
    FEET = "feet"
    TONGUE = "tongue"
    REST = "rest"
    UNKNOWN = "unknown"


class SeizureRisk(Enum):
    """Seizure risk levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    IMMINENT = "imminent"


@dataclass
class ClassificationResult:
    """Base classification result"""

    classification_type: str
    timestamp: datetime
    confidence: float
    label: str
    probabilities: Dict[str, float]
    latency_ms: float
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class MentalStateResult:
    """Mental state classification result"""

    # Required fields first
    timestamp: datetime
    confidence: float
    label: str
    probabilities: Dict[str, float]
    latency_ms: float
    state: MentalState
    arousal_level: float  # 0-1
    valence: float  # -1 to 1
    attention_score: float  # 0-1

    # Optional fields with defaults
    classification_type: str = field(default="mental_state", init=False)
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        self.label = self.state.value


@dataclass
class SleepStageResult:
    """Sleep stage classification result"""

    # Required fields first
    timestamp: datetime
    confidence: float
    label: str
    probabilities: Dict[str, float]
    latency_ms: float
    stage: SleepStage
    epoch_number: int
    sleep_depth: float  # 0-1
    transition_probability: float  # 0-1

    # Optional fields with defaults
    classification_type: str = field(default="sleep_stage", init=False)
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        self.label = self.stage.value


@dataclass
class SeizurePrediction:
    """Seizure prediction result"""

    # Required fields first
    timestamp: datetime
    confidence: float
    label: str
    probabilities: Dict[str, float]
    latency_ms: float
    risk_level: SeizureRisk
    probability: float
    patient_id: str

    # Optional fields with defaults
    time_to_seizure_minutes: Optional[float] = None
    spatial_focus: Optional[List[int]] = None  # Channel indices
    classification_type: str = field(default="seizure_prediction", init=False)
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        self.label = self.risk_level.value


@dataclass
class MotorImageryResult:
    """Motor imagery classification result"""

    # Required fields first
    timestamp: datetime
    confidence: float
    label: str
    probabilities: Dict[str, float]
    latency_ms: float
    intent: MotorIntent
    control_signal: np.ndarray  # Control vector for BCI
    erd_ers_score: float  # Event-related (de)synchronization
    spatial_pattern: np.ndarray  # CSP weights

    # Optional fields with defaults
    classification_type: str = field(default="motor_imagery", init=False)
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        self.label = self.intent.value


@dataclass
class BCICommand:
    """BCI control command"""

    command_type: str
    parameters: Dict[str, Any]
    confidence: float
    timestamp: datetime


@dataclass
class NeuralData:
    """Neural data container"""

    data: np.ndarray  # Shape: (channels, samples)
    sampling_rate: float
    channels: List[str]
    timestamp: datetime
    device_id: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class FeatureVector:
    """Extracted feature vector"""

    features: Dict[str, np.ndarray]
    timestamp: datetime
    window_size_ms: float
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ModelMetrics:
    """Model performance metrics"""

    model_name: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    latency_p50: float
    latency_p95: float
    latency_p99: float
    inference_count: int
    error_count: int
    last_updated: datetime


@dataclass
class StreamMetadata:
    """Stream metadata"""

    stream_id: str
    device_id: str
    subject_id: str
    sampling_rate: float
    channel_count: int
    channel_names: List[str]
    start_time: datetime
    classification_types: List[str]
