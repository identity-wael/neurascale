"""Type definitions for Omniverse integration."""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from datetime import datetime


class VisualizationMode(Enum):
    """Visualization modes for neural data."""

    SURFACE_ACTIVITY = "surface_activity"
    VOLUME_RENDERING = "volume_rendering"
    CONNECTIVITY_GRAPH = "connectivity_graph"
    PARTICLE_SYSTEM = "particle_system"
    HYBRID = "hybrid"


class RenderQuality(Enum):
    """Rendering quality presets."""

    DRAFT = "draft"
    PREVIEW = "preview"
    PRODUCTION = "production"
    CINEMATIC = "cinematic"


@dataclass
class BrainModel:
    """Brain model data structure."""

    patient_id: str
    mesh_vertices: np.ndarray  # Shape: (n_vertices, 3)
    mesh_faces: np.ndarray  # Shape: (n_faces, 3)
    atlas_regions: Dict[str, List[int]]  # Region name to vertex indices
    electrode_positions: Dict[str, Tuple[float, float, float]]  # Channel to 3D position
    mri_source_path: Optional[str] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class SessionConfig:
    """Configuration for Omniverse visualization session."""

    session_id: str
    patient_id: str
    visualization_mode: VisualizationMode
    render_quality: RenderQuality
    nucleus_server: str
    stage_path: str
    enable_vr: bool = False
    enable_collaboration: bool = False
    max_participants: int = 4
    recording_enabled: bool = False
    stream_url: Optional[str] = None


@dataclass
class NeuralActivityFrame:
    """Single frame of neural activity data."""

    timestamp: float
    eeg_data: np.ndarray  # Shape: (n_channels, n_samples)
    channel_names: List[str]
    sampling_rate: float
    event_markers: Optional[List[Dict[str, Any]]] = None
    connectivity_matrix: Optional[np.ndarray] = None
    source_localization: Optional[np.ndarray] = None


@dataclass
class VisualizationState:
    """Current state of the visualization."""

    session_id: str
    current_time: float
    playback_speed: float
    camera_position: Tuple[float, float, float]
    camera_rotation: Tuple[float, float, float]
    active_regions: List[str]
    color_map: str
    transparency: float
    annotations: List[Dict[str, Any]]
    is_playing: bool = False
    is_recording: bool = False


@dataclass
class CollaborationEvent:
    """Event in collaborative session."""

    event_id: str
    user_id: str
    event_type: str  # "annotation", "camera_sync", "playback_control", etc.
    timestamp: datetime
    data: Dict[str, Any]


@dataclass
class MaterialProperties:
    """Material properties for brain tissue visualization."""

    base_color: Tuple[float, float, float, float]  # RGBA
    metallic: float
    roughness: float
    subsurface_scattering: float
    emission_strength: float
    opacity: float
    ior: float  # Index of refraction


@dataclass
class VRControllerState:
    """VR controller state for interaction."""

    controller_id: str
    position: Tuple[float, float, float]
    rotation: Tuple[float, float, float, float]  # Quaternion
    trigger_value: float
    grip_value: float
    buttons_pressed: List[str]
    is_pointing: bool
    ray_direction: Optional[Tuple[float, float, float]] = None


@dataclass
class HapticFeedback:
    """Haptic feedback configuration."""

    controller_id: str
    feedback_type: str  # "pulse", "continuous", "pattern"
    intensity: float  # 0.0 to 1.0
    duration_ms: int
    pattern: Optional[List[float]] = None  # For custom patterns
