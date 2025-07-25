"""Data types and models for neural data ingestion."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
import numpy as np


class NeuralSignalType(Enum):
    """Types of neural signals supported by the system."""

    EEG = "eeg"  # Electroencephalography
    ECOG = "ecog"  # Electrocorticography
    SPIKES = "spikes"  # Spike trains
    LFP = "lfp"  # Local field potentials
    EMG = "emg"  # Electromyography
    ACCELEROMETER = "accelerometer"  # Movement data
    CUSTOM = "custom"  # User - defined signal types


class DataSource(Enum):
    """Supported data sources for neural signals."""

    LSL = "lsl"  # Lab Streaming Layer
    OPENBCI = "openbci"  # OpenBCI devices
    BRAINFLOW = "brainflow"  # BrainFlow supported devices
    FILE_UPLOAD = "file_upload"  # Batch file uploads
    SYNTHETIC = "synthetic"  # Synthetic test data
    CUSTOM_API = "custom_api"  # Custom streaming APIs


@dataclass
class ChannelInfo:
    """Information about a single data channel."""

    channel_id: int
    label: str
    unit: str = "microvolts"
    sampling_rate: float = 256.0
    reference: Optional[str] = None
    hardware_id: Optional[str] = None
    position: Optional[Dict[str, float]] = None  # 3D coordinates if available


@dataclass
class DeviceInfo:
    """Information about the recording device."""

    device_id: str
    device_type: str
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    firmware_version: Optional[str] = None
    channels: Optional[List[ChannelInfo]] = None


@dataclass
class NeuralDataPacket:
    """A packet of neural data with metadata."""

    # Core data
    timestamp: datetime
    data: np.ndarray  # Shape: (n_channels, n_samples)
    signal_type: NeuralSignalType
    source: DataSource

    # Metadata
    device_info: DeviceInfo
    session_id: str
    subject_id: Optional[str] = None  # Anonymized subject identifier

    # Data quality
    sampling_rate: float = 256.0
    data_quality: float = 1.0  # 0 - 1 quality score
    missing_samples: int = 0

    # Additional metadata
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        """Validate data packet after initialization."""
        if self.data.ndim != 2:
            raise ValueError(f"Data must be 2D array, got shape {self.data.shape}")

        if self.device_info.channels:
            n_channels = len(self.device_info.channels)
            if self.data.shape[0] != n_channels:
                raise ValueError(
                    f"Data channels ({self.data.shape[0]}) don't match "
                    f"device channels ({n_channels})"
                )

    @property
    def n_channels(self) -> int:
        """Number of channels in the data."""
        return self.data.shape[0]

    @property
    def n_samples(self) -> int:
        """Number of samples per channel."""
        return self.data.shape[1]

    @property
    def duration_seconds(self) -> float:
        """Duration of the data packet in seconds."""
        return self.n_samples / self.sampling_rate


@dataclass
class ValidationResult:
    """Result of data validation."""

    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    data_quality_score: float = 1.0

    def __post_init__(self) -> None:
        """Initialize empty lists if None."""
        # Lists are now initialized by default_factory, no need for None checks
        pass

    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)
