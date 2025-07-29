"""Main connector between Neural Engine and NVIDIA Omniverse."""

import logging
from typing import Dict, Any
import numpy as np

from .types import (
    SessionConfig,
    NeuralActivityFrame,
    VisualizationState,
    VisualizationMode,
)
from .connectors import NucleusClient, USDGenerator, LiveSync
from .models import BrainMeshLoader, ElectrodeModels, AnimationEngine
from .rendering import RTXRenderer, VolumeRenderer, ParticleSystem
from .interaction import VRController, GestureRecognition
from .analytics import HeatmapGenerator, FlowVisualizer

logger = logging.getLogger(__name__)


class NeuralOmniverseConnector:
    """Main connector between Neural Engine and Omniverse.

    This class orchestrates the entire visualization pipeline,
    from neural data streaming to real-time 3D rendering in Omniverse.
    """

    def __init__(self, config: SessionConfig):
        """Initialize Omniverse connector.

        Args:
            config: Session configuration
        """
        self.config = config
        self.session_id = config.session_id
        self.patient_id = config.patient_id

        # Core components
        self.nucleus_client = None
        self.usd_generator = None
        self.live_sync = None

        # Visualization components
        self.brain_model = None
        self.mesh_loader = None
        self.animation_engine = None

        # Rendering components
        self.rtx_renderer = None
        self.volume_renderer = None
        self.particle_system = None

        # Interaction components
        self.vr_controller = None
        self.gesture_recognition = None

        # Analytics components
        self.heatmap_generator = None
        self.flow_visualizer = None

        # State management
        self.visualization_state = None
        self.is_initialized = False
        self.is_streaming = False

        logger.info(f"NeuralOmniverseConnector created for session {self.session_id}")

    async def initialize(self) -> bool:
        """Initialize all Omniverse components.

        Returns:
            Success status
        """
        try:
            # Connect to Nucleus server
            self.nucleus_client = NucleusClient(self.config.nucleus_server)
            await self.nucleus_client.connect()

            # Initialize USD generator
            self.usd_generator = USDGenerator(self.config.stage_path)
            await self.usd_generator.create_stage()

            # Set up live synchronization
            self.live_sync = LiveSync(self.nucleus_client, self.usd_generator)
            await self.live_sync.initialize()

            # Load brain model
            await self._initialize_brain_model()

            # Initialize rendering pipeline
            await self._initialize_rendering()

            # Set up interaction if VR enabled
            if self.config.enable_vr:
                await self._initialize_vr_interaction()

            # Initialize analytics
            await self._initialize_analytics()

            # Create initial visualization state
            self.visualization_state = VisualizationState(
                session_id=self.session_id,
                current_time=0.0,
                playback_speed=1.0,
                camera_position=(0.0, 0.0, 2.0),
                camera_rotation=(0.0, 0.0, 0.0),
                active_regions=[],
                color_map="viridis",
                transparency=1.0,
                annotations=[],
            )

            self.is_initialized = True
            logger.info("NeuralOmniverseConnector initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Omniverse connector: {e}")
            return False

    async def stream_neural_data(self, frame: NeuralActivityFrame) -> bool:
        """Stream neural activity data to Omniverse.

        Args:
            frame: Neural activity data frame

        Returns:
            Success status
        """
        if not self.is_initialized:
            logger.error("Connector not initialized")
            return False

        try:
            # Map EEG channels to 3D positions
            activity_map = await self._map_channels_to_surface(frame.eeg_data)

            # Update visualization based on mode
            if self.config.visualization_mode == VisualizationMode.SURFACE_ACTIVITY:
                await self._update_surface_activity(activity_map)

            elif self.config.visualization_mode == VisualizationMode.VOLUME_RENDERING:
                await self._update_volume_rendering(frame)

            elif self.config.visualization_mode == VisualizationMode.CONNECTIVITY_GRAPH:
                await self._update_connectivity_graph(frame.connectivity_matrix)

            elif self.config.visualization_mode == VisualizationMode.PARTICLE_SYSTEM:
                await self._update_particle_system(frame)

            elif self.config.visualization_mode == VisualizationMode.HYBRID:
                await self._update_hybrid_visualization(frame, activity_map)

            # Update animation timeline
            self.visualization_state.current_time = frame.timestamp

            # Sync to Omniverse
            await self.live_sync.sync_frame()

            # Process VR interactions if enabled
            if self.config.enable_vr and self.vr_controller:
                await self._process_vr_interactions()

            return True

        except Exception as e:
            logger.error(f"Failed to stream neural data: {e}")
            return False

    async def create_collaborative_session(self) -> str:
        """Create multi-user collaborative session.

        Returns:
            Session URL for participants
        """
        if not self.config.enable_collaboration:
            raise ValueError("Collaboration not enabled in config")

        try:
            # Create live layer for collaboration
            live_layer_url = await self.live_sync.create_live_layer(
                f"collab_{self.session_id}"
            )

            # Set up voice chat
            await self._setup_voice_chat()

            # Initialize annotation system
            await self._setup_annotation_system()

            # Configure permissions
            await self._configure_collaboration_permissions()

            logger.info(f"Collaborative session created: {live_layer_url}")
            return live_layer_url

        except Exception as e:
            logger.error(f"Failed to create collaborative session: {e}")
            raise

    async def _initialize_brain_model(self):
        """Initialize patient-specific brain model."""
        self.mesh_loader = BrainMeshLoader()

        # Load or generate brain model
        self.brain_model = await self.mesh_loader.load_patient_model(self.patient_id)

        # Create USD representation
        await self.usd_generator.create_brain_geometry(
            self.brain_model.mesh_vertices,
            self.brain_model.mesh_faces,
            self.brain_model.atlas_regions,
        )

        # Set up electrode positions
        electrode_models = ElectrodeModels()
        await electrode_models.create_electrode_visualization(
            self.brain_model.electrode_positions, self.usd_generator.stage
        )

        # Initialize animation engine
        self.animation_engine = AnimationEngine(self.brain_model, self.usd_generator)

    async def _initialize_rendering(self):
        """Initialize rendering pipeline."""
        # Set up RTX renderer
        self.rtx_renderer = RTXRenderer(self.config.render_quality)
        await self.rtx_renderer.configure_neural_rendering()

        # Initialize volume renderer if needed
        if self.config.visualization_mode in [
            VisualizationMode.VOLUME_RENDERING,
            VisualizationMode.HYBRID,
        ]:
            self.volume_renderer = VolumeRenderer()
            await self.volume_renderer.initialize()

        # Set up particle system
        self.particle_system = ParticleSystem()
        await self.particle_system.create_neural_particles()

    async def _initialize_vr_interaction(self):
        """Initialize VR interaction components."""
        self.vr_controller = VRController()
        await self.vr_controller.initialize_openxr()

        self.gesture_recognition = GestureRecognition(self.vr_controller)
        await self.gesture_recognition.load_gesture_models()

    async def _initialize_analytics(self):
        """Initialize visual analytics components."""
        self.heatmap_generator = HeatmapGenerator(self.brain_model)
        self.flow_visualizer = FlowVisualizer(self.brain_model)

    async def _map_channels_to_surface(self, eeg_data: np.ndarray) -> np.ndarray:
        """Map EEG channel data to brain surface vertices.

        Args:
            eeg_data: EEG data array

        Returns:
            Activity values for each vertex
        """
        # Interpolate channel data to surface vertices
        activity_map = await self.animation_engine.interpolate_to_surface(
            eeg_data, self.brain_model.electrode_positions
        )

        return activity_map

    async def _update_surface_activity(self, activity_map: np.ndarray):
        """Update surface activity visualization."""
        # Generate heatmap texture
        heatmap = await self.heatmap_generator.create_activity_heatmap(
            activity_map, self.visualization_state.color_map
        )

        # Apply to brain surface
        await self.animation_engine.update_vertex_colors(heatmap)

    async def _update_volume_rendering(self, frame: NeuralActivityFrame):
        """Update volume rendering visualization."""
        if frame.source_localization is not None:
            await self.volume_renderer.update_volume(frame.source_localization)

    async def _update_connectivity_graph(self, connectivity_matrix: np.ndarray):
        """Update connectivity visualization."""
        if connectivity_matrix is not None:
            flow_lines = await self.flow_visualizer.create_flow_lines(
                connectivity_matrix
            )
            await self.animation_engine.update_connectivity_lines(flow_lines)

    async def _update_particle_system(self, frame: NeuralActivityFrame):
        """Update particle system for neural spikes."""
        if frame.event_markers:
            spike_events = [e for e in frame.event_markers if e.get("type") == "spike"]
            await self.particle_system.emit_spike_particles(spike_events)

    async def _update_hybrid_visualization(
        self, frame: NeuralActivityFrame, activity_map: np.ndarray
    ):
        """Update hybrid visualization combining multiple modes."""
        # Update surface activity
        await self._update_surface_activity(activity_map)

        # Add connectivity if available
        if frame.connectivity_matrix is not None:
            await self._update_connectivity_graph(frame.connectivity_matrix)

        # Add particles for events
        await self._update_particle_system(frame)

    async def _process_vr_interactions(self):
        """Process VR controller inputs and gestures."""
        # Get current controller state
        controller_state = await self.vr_controller.get_controller_state()

        # Detect gestures
        gesture = await self.gesture_recognition.detect_gesture(controller_state)

        if gesture:
            await self._handle_vr_gesture(gesture)

    async def _handle_vr_gesture(self, gesture: Dict[str, Any]):
        """Handle recognized VR gesture."""
        gesture_type = gesture.get("type")

        if gesture_type == "point":
            # Pointing at brain region
            region = await self._get_pointed_region(gesture["ray"])
            if region:
                await self._highlight_region(region)

        elif gesture_type == "grab":
            # Grabbing to rotate brain
            await self._update_brain_rotation(gesture["rotation"])

        elif gesture_type == "pinch":
            # Pinching to zoom
            await self._update_zoom_level(gesture["scale"])

    async def _setup_voice_chat(self) -> str:
        """Set up voice chat for collaboration."""
        # Implementation would integrate with Omniverse Voice
        pass

    async def _setup_annotation_system(self):
        """Set up 3D annotation system."""
        # Implementation would create annotation UI and storage
        pass

    async def _configure_collaboration_permissions(self):
        """Configure permissions for collaborative session."""
        # Implementation would set read/write permissions
        pass

    async def close(self):
        """Clean up and close connections."""
        try:
            if self.is_streaming:
                self.is_streaming = False

            if self.live_sync:
                await self.live_sync.close()

            if self.nucleus_client:
                await self.nucleus_client.disconnect()

            if self.vr_controller:
                await self.vr_controller.close()

            logger.info("NeuralOmniverseConnector closed")

        except Exception as e:
            logger.error(f"Error closing connector: {e}")
