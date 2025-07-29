"""Tests for individual Omniverse components."""

import pytest
import numpy as np
from unittest.mock import Mock, patch

from src.visualization.omniverse.connectors.usd_generator import USDGenerator
from src.visualization.omniverse.connectors.live_sync import LiveSync
from src.visualization.omniverse.connectors.material_library import MaterialLibrary
from src.visualization.omniverse.models.animation_engine import (
    AnimationEngine,
    AnimationKeyframe,
    InterpolationType,
)
from src.visualization.omniverse.models.atlas_mapper import AtlasMapper
from src.visualization.omniverse.rendering.particle_system import ParticleSystem
from src.visualization.omniverse.rendering.shader_manager import ShaderManager
from src.visualization.omniverse.analytics.flow_visualizer import (
    FlowVisualizer,
    FlowPath,
)
from src.visualization.omniverse.interaction.gesture_recognition import (
    GestureRecognition,
    GestureType,
    HandPose,
)


class TestUSDGenerator:
    """Test USD Generator."""

    @pytest.fixture
    def usd_generator(self):
        """Create USD Generator instance."""
        return USDGenerator("/test/stage.usd")

    @pytest.mark.asyncio
    async def test_create_stage(self, usd_generator):
        """Test USD stage creation."""
        with patch("pxr.Usd.Stage.CreateNew") as mock_create:
            mock_stage = Mock()
            mock_create.return_value = mock_stage

            result = await usd_generator.create_stage()
            assert result is True
            assert usd_generator.stage is not None

    @pytest.mark.asyncio
    async def test_add_brain_mesh(self, usd_generator):
        """Test adding brain mesh to USD."""
        # Mock stage
        usd_generator.stage = Mock()

        # Create test mesh data
        vertices = np.random.randn(100, 3)
        faces = np.random.randint(0, 100, (200, 3))

        with patch.object(usd_generator, "_create_mesh_prim", return_value=Mock()):
            result = await usd_generator.add_brain_mesh(vertices, faces)
            assert result is True


class TestLiveSync:
    """Test Live Sync."""

    @pytest.fixture
    def live_sync(self):
        """Create Live Sync instance."""
        return LiveSync("test-server:3030")

    @pytest.mark.asyncio
    async def test_start_session(self, live_sync):
        """Test starting live sync session."""
        with patch.object(live_sync, "_connect_to_live_session", return_value=True):
            result = await live_sync.start_session("test-session")
            assert result is True
            assert live_sync.is_active is True

    @pytest.mark.asyncio
    async def test_send_update(self, live_sync):
        """Test sending live update."""
        # Mock active session
        live_sync.is_active = True
        live_sync.websocket = Mock()
        live_sync.websocket.send = Mock()

        # Create test update
        update_data = {
            "type": "neural_activity",
            "timestamp": 123456789,
            "data": {"Fp1": 0.5},
        }

        result = await live_sync.send_update(update_data)
        assert result is True


class TestMaterialLibrary:
    """Test Material Library."""

    @pytest.fixture
    def material_library(self):
        """Create Material Library instance."""
        return MaterialLibrary()

    def test_create_neural_material(self, material_library):
        """Test neural material creation."""
        material = material_library.create_neural_material(
            activity_level=0.8,
            frequency_band="alpha",
        )

        assert material is not None
        assert "base_color" in material
        assert "metallic" in material
        assert "emission_color" in material

    def test_blend_materials(self, material_library):
        """Test material blending."""
        mat1 = {"base_color": (1.0, 0.0, 0.0), "metallic": 0.0}
        mat2 = {"base_color": (0.0, 0.0, 1.0), "metallic": 1.0}

        blended = material_library.blend_materials([mat1, mat2], [0.7, 0.3])

        assert "base_color" in blended
        assert blended["metallic"] == pytest.approx(0.3, rel=1e-3)


class TestAnimationEngine:
    """Test Animation Engine."""

    @pytest.fixture
    def animation_engine(self):
        """Create Animation Engine instance."""
        return AnimationEngine()

    def test_create_track(self, animation_engine):
        """Test animation track creation."""
        keyframes = [
            AnimationKeyframe(time=0.0, value=0.0),
            AnimationKeyframe(time=1.0, value=1.0),
            AnimationKeyframe(time=2.0, value=0.0),
        ]

        track = animation_engine.create_track(
            name="test_track",
            target_path="/Root/Object",
            property_name="scale",
            keyframes=keyframes,
        )

        assert track is not None
        assert track.name == "test_track"
        assert len(track.keyframes) == 3
        assert track.duration == 2.0

    def test_interpolation(self, animation_engine):
        """Test value interpolation."""
        # Test linear interpolation
        result = animation_engine._interpolate(0.0, 1.0, 0.5, InterpolationType.LINEAR)
        assert result == pytest.approx(0.5)

        # Test ease in
        result = animation_engine._interpolate(0.0, 1.0, 0.5, InterpolationType.EASE_IN)
        assert result == pytest.approx(0.25)

    def test_update_animation(self, animation_engine):
        """Test animation update."""
        # Create simple animation
        keyframes = [
            AnimationKeyframe(time=0.0, value=0.0),
            AnimationKeyframe(time=1.0, value=1.0),
        ]

        animation_engine.create_track(
            name="test",
            target_path="/Root/Object",
            property_name="x",
            keyframes=keyframes,
        )

        # Start playback
        animation_engine.play()

        # Update
        updates = animation_engine.update(0.5)

        assert "/Root/Object" in updates
        assert "x" in updates["/Root/Object"]
        assert updates["/Root/Object"]["x"] == pytest.approx(0.5)


class TestAtlasMapper:
    """Test Atlas Mapper."""

    @pytest.fixture
    def atlas_mapper(self):
        """Create Atlas Mapper instance."""
        return AtlasMapper()

    @pytest.mark.asyncio
    async def test_load_atlas(self, atlas_mapper):
        """Test loading brain atlas."""
        # For now, just test initialization
        assert "AAL" in atlas_mapper.available_atlases
        assert "Brodmann" in atlas_mapper.available_atlases

    def test_get_region_info(self, atlas_mapper):
        """Test getting region information."""
        # Mock some regions
        atlas_mapper.atlas_regions = {
            1: {"name": "Frontal_Lobe", "color": (1.0, 0.0, 0.0)},
            2: {"name": "Temporal_Lobe", "color": (0.0, 1.0, 0.0)},
        }

        info = atlas_mapper.get_region_info(1)
        assert info is not None
        assert info["name"] == "Frontal_Lobe"


class TestParticleSystem:
    """Test Particle System."""

    @pytest.fixture
    def particle_system(self):
        """Create Particle System instance."""
        return ParticleSystem()

    def test_add_emitter(self, particle_system):
        """Test adding particle emitter."""
        emitter_id = particle_system.add_emitter(
            position=(0, 0, 0),
            emitter_type="sphere",
            radius=0.5,
            emission_rate=100,
        )

        assert emitter_id is not None
        assert len(particle_system.emitters) == 1

    @pytest.mark.asyncio
    async def test_emit_burst(self, particle_system):
        """Test particle burst emission."""
        initial_count = len(particle_system.particles)

        await particle_system.emit_burst(
            position=(0, 0, 0),
            count=50,
            speed=1.0,
            lifetime=2.0,
        )

        assert len(particle_system.particles) == initial_count + 50

    @pytest.mark.asyncio
    async def test_update_particles(self, particle_system):
        """Test particle update."""
        # Add some particles
        await particle_system.emit_burst(position=(0, 0, 0), count=10)

        initial_positions = [p.position.copy() for p in particle_system.particles]

        # Update
        await particle_system.update(0.1)

        # Positions should have changed
        for i, particle in enumerate(particle_system.particles):
            if particle.active:
                assert not np.array_equal(particle.position, initial_positions[i])


class TestFlowVisualizer:
    """Test Flow Visualizer."""

    @pytest.fixture
    def flow_visualizer(self):
        """Create Flow Visualizer instance."""
        return FlowVisualizer()

    @pytest.mark.asyncio
    async def test_create_connectivity_flow(self, flow_visualizer):
        """Test connectivity flow creation."""
        # Create test connectivity matrix
        connectivity = np.array(
            [
                [1.0, 0.8, 0.3],
                [0.8, 1.0, 0.5],
                [0.3, 0.5, 1.0],
            ]
        )

        positions = {
            "A": (0, 0, 0),
            "B": (1, 0, 0),
            "C": (0, 1, 0),
        }

        flows = await flow_visualizer.create_connectivity_flow(
            connectivity, positions, threshold=0.4
        )

        assert len(flows) > 0
        assert all(isinstance(f, FlowPath) for f in flows)

    def test_calculate_bezier_waypoints(self, flow_visualizer):
        """Test bezier curve calculation."""
        start = (0, 0, 0)
        end = (1, 0, 0)

        waypoints = flow_visualizer._calculate_bezier_waypoints(start, end)

        assert len(waypoints) == 5
        assert all(len(w) == 3 for w in waypoints)


class TestGestureRecognition:
    """Test Gesture Recognition."""

    @pytest.fixture
    def gesture_recognition(self):
        """Create Gesture Recognition instance."""
        return GestureRecognition()

    def test_detect_pinch(self, gesture_recognition):
        """Test pinch gesture detection."""
        # Create hand pose with pinch
        pose = HandPose(
            timestamp=0.0,
            wrist=(0, 0, 0),
            thumb_tip=(0.02, 0, 0),
            index_tip=(0.02, 0, 0),  # Close to thumb
            middle_tip=(0.1, 0, 0),
            ring_tip=(0.1, 0, 0),
            pinky_tip=(0.1, 0, 0),
            palm_normal=(0, 0, 1),
            palm_center=(0, 0, 0),
            confidence=1.0,
        )

        gesture = gesture_recognition._detect_pinch(pose)

        assert gesture is not None
        assert gesture.type == GestureType.PINCH

    def test_detect_grab(self, gesture_recognition):
        """Test grab gesture detection."""
        # Create hand pose with all fingers close to palm
        pose = HandPose(
            timestamp=0.0,
            wrist=(0, 0, 0),
            thumb_tip=(0.03, 0, 0),
            index_tip=(0.03, 0, 0),
            middle_tip=(0.03, 0, 0),
            ring_tip=(0.03, 0, 0),
            pinky_tip=(0.03, 0, 0),
            palm_normal=(0, 0, 1),
            palm_center=(0, 0, 0),
            confidence=1.0,
        )

        gesture = gesture_recognition._detect_grab(pose)

        assert gesture is not None
        assert gesture.type == GestureType.GRAB

    @pytest.mark.asyncio
    async def test_update_gestures(self, gesture_recognition):
        """Test gesture update with hand poses."""
        # Create test hand pose
        pose = HandPose(
            timestamp=0.0,
            wrist=(0, 0, 0),
            thumb_tip=(0.02, 0, 0),
            index_tip=(0.02, 0, 0),
            middle_tip=(0.1, 0, 0),
            ring_tip=(0.1, 0, 0),
            pinky_tip=(0.1, 0, 0),
            palm_normal=(0, 0, 1),
            palm_center=(0, 0, 0),
            confidence=1.0,
        )

        gestures = await gesture_recognition.update(pose, None)

        assert len(gestures) > 0
        assert any(g.type == GestureType.PINCH for g in gestures)


class TestShaderManager:
    """Test Shader Manager."""

    @pytest.fixture
    def shader_manager(self):
        """Create Shader Manager instance."""
        return ShaderManager()

    @pytest.mark.asyncio
    async def test_load_shader(self, shader_manager):
        """Test shader loading."""
        # Test loading built-in shader
        shader = await shader_manager.load_shader("neural_activity")

        assert shader is not None
        assert "vertex" in shader
        assert "fragment" in shader

    def test_create_neural_shader(self, shader_manager):
        """Test neural shader creation."""
        params = {
            "base_color": (1.0, 0.5, 0.0),
            "activity_level": 0.8,
            "pulse_frequency": 2.0,
        }

        shader = shader_manager.create_neural_shader(params)

        assert shader is not None
        assert "vertex" in shader
        assert "fragment" in shader
        assert "uniforms" in shader


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
