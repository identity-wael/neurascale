"""Tests for NVIDIA Omniverse integration."""

import pytest
import numpy as np
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from src.visualization.omniverse.neural_omniverse_connector import (
    NeuralOmniverseConnector,
    OmniverseConfig,
    VisualizationMode,
)
from src.visualization.omniverse.connectors.nucleus_client import NucleusClient
from src.visualization.omniverse.connectors.usd_generator import USDGenerator
from src.visualization.omniverse.models.brain_mesh_loader import BrainMeshLoader
from src.visualization.omniverse.models.electrode_models import ElectrodeModels
from src.visualization.omniverse.rendering.rtx_renderer import RTXRenderer
from src.visualization.omniverse.interaction.vr_controller import VRController
from src.visualization.omniverse.analytics.heatmap_generator import HeatmapGenerator


@pytest.fixture
def omniverse_config():
    """Create test Omniverse configuration."""
    config = OmniverseConfig()
    config.nucleus_server = "test-server:3030"
    config.project_path = "/test/project"
    config.enable_vr = False
    config.quality_preset = "medium"
    return config


@pytest.fixture
def neural_connector(omniverse_config):
    """Create Neural Omniverse Connector instance."""
    return NeuralOmniverseConnector(omniverse_config)


class TestNeuralOmniverseConnector:
    """Test Neural Omniverse Connector."""

    @pytest.mark.asyncio
    async def test_connect_success(self, neural_connector):
        """Test successful connection to Omniverse."""
        # Mock dependencies
        with patch.object(neural_connector.nucleus_client, "connect", return_value=True):
            with patch.object(neural_connector, "_initialize_scene", return_value=True):
                with patch.object(neural_connector, "_setup_materials", return_value=True):
                    result = await neural_connector.connect()
                    
                    assert result is True
                    assert neural_connector.is_connected is True
                    assert neural_connector.session_id is not None

    @pytest.mark.asyncio
    async def test_connect_failure(self, neural_connector):
        """Test failed connection to Omniverse."""
        # Mock connection failure
        with patch.object(neural_connector.nucleus_client, "connect", return_value=False):
            result = await neural_connector.connect()
            
            assert result is False
            assert neural_connector.is_connected is False

    @pytest.mark.asyncio
    async def test_disconnect(self, neural_connector):
        """Test disconnection from Omniverse."""
        # Set connected state
        neural_connector.is_connected = True
        
        # Mock dependencies
        with patch.object(neural_connector.nucleus_client, "disconnect", return_value=True):
            await neural_connector.disconnect()
            
            assert neural_connector.is_connected is False

    @pytest.mark.asyncio
    async def test_stream_neural_data(self, neural_connector):
        """Test streaming neural data."""
        # Create test data
        eeg_data = {
            "Fp1": np.random.randn(100),
            "Fp2": np.random.randn(100),
            "F3": np.random.randn(100),
        }
        
        frame = Mock()
        frame.timestamp = datetime.now()
        frame.eeg_data = eeg_data
        frame.sample_rate = 1000
        
        # Mock connected state
        neural_connector.is_connected = True
        
        # Mock visualization update
        with patch.object(neural_connector, "_update_surface_activity", return_value=True):
            result = await neural_connector.stream_neural_data(frame)
            assert result is True

    def test_set_visualization_mode(self, neural_connector):
        """Test setting visualization mode."""
        # Test each mode
        for mode in VisualizationMode:
            neural_connector.set_visualization_mode(mode)
            assert neural_connector.config.visualization_mode == mode


class TestNucleusClient:
    """Test Nucleus Client."""

    @pytest.fixture
    def nucleus_client(self):
        """Create Nucleus Client instance."""
        return NucleusClient("test-server:3030")

    @pytest.mark.asyncio
    async def test_connect(self, nucleus_client):
        """Test connection to Nucleus server."""
        # Mock Kit app
        with patch("omni.client.initialize", return_value=True):
            result = await nucleus_client.connect()
            assert result is True

    @pytest.mark.asyncio
    async def test_file_operations(self, nucleus_client):
        """Test file operations."""
        # Mock connected state
        nucleus_client.is_connected = True
        
        # Test file exists
        with patch("omni.client.stat", return_value=(True, Mock())):
            exists = await nucleus_client.file_exists("/test/file.usd")
            assert exists is True
        
        # Test create folder
        with patch("omni.client.create_folder", return_value=True):
            result = await nucleus_client.create_folder("/test/folder")
            assert result is True


class TestBrainMeshLoader:
    """Test Brain Mesh Loader."""

    @pytest.fixture
    def brain_loader(self):
        """Create Brain Mesh Loader instance."""
        return BrainMeshLoader()

    @pytest.mark.asyncio
    async def test_load_template_brain(self, brain_loader):
        """Test loading template brain."""
        result = await brain_loader.load_template_brain("medium")
        
        assert result is True
        assert brain_loader.vertices is not None
        assert brain_loader.faces is not None
        assert len(brain_loader.vertices) > 0
        assert len(brain_loader.faces) > 0

    def test_generate_sphere_mesh(self, brain_loader):
        """Test sphere mesh generation."""
        vertices, faces = brain_loader._generate_sphere_mesh(1.0, 20)
        
        assert vertices.shape[1] == 3  # 3D coordinates
        assert faces.shape[1] == 3  # Triangular faces
        assert len(vertices) > 0
        assert len(faces) > 0

    @pytest.mark.asyncio
    async def test_apply_smoothing(self, brain_loader):
        """Test mesh smoothing."""
        # Create simple mesh
        brain_loader.vertices = np.random.randn(100, 3)
        brain_loader.faces = np.random.randint(0, 100, (200, 3))
        
        # Apply smoothing
        await brain_loader.apply_smoothing(iterations=2)
        
        # Vertices should still exist
        assert brain_loader.vertices is not None
        assert len(brain_loader.vertices) == 100


class TestElectrodeModels:
    """Test Electrode Models."""

    @pytest.fixture
    def electrode_models(self):
        """Create Electrode Models instance."""
        return ElectrodeModels()

    def test_standard_montages(self, electrode_models):
        """Test standard electrode montages."""
        # Check 10-20 system
        assert "10-20" in electrode_models.montages
        assert "Fp1" in electrode_models.montages["10-20"]
        assert len(electrode_models.montages["10-20"]) == 19
        
        # Check 10-10 system
        assert "10-10" in electrode_models.montages
        assert len(electrode_models.montages["10-10"]) > len(electrode_models.montages["10-20"])

    @pytest.mark.asyncio
    async def test_create_electrode_models(self, electrode_models):
        """Test creating electrode models."""
        models = await electrode_models.create_electrode_models("10-20")
        
        assert len(models) == 19
        assert "Fp1" in models
        assert "vertices" in models["Fp1"]
        assert "faces" in models["Fp1"]

    def test_get_neighbors(self, electrode_models):
        """Test finding neighboring electrodes."""
        neighbors = electrode_models.get_neighbors("Cz", radius=0.5)
        
        assert len(neighbors) > 0
        assert all(isinstance(n, tuple) for n in neighbors)
        assert all(len(n) == 2 for n in neighbors)  # (channel, distance)


class TestHeatmapGenerator:
    """Test Heatmap Generator."""

    @pytest.fixture
    def heatmap_generator(self):
        """Create Heatmap Generator instance."""
        return HeatmapGenerator()

    @pytest.mark.asyncio
    async def test_generate_2d_projection(self, heatmap_generator):
        """Test 2D heatmap projection."""
        # Create test data
        positions = {
            "Fp1": (-0.3, 0.9, 0.0),
            "Fp2": (0.3, 0.9, 0.0),
            "Cz": (0.0, 0.0, 1.0),
        }
        values = {
            "Fp1": 0.8,
            "Fp2": 0.6,
            "Cz": 0.9,
        }
        
        # Generate heatmap
        heatmap = await heatmap_generator.generate_2d_projection(
            positions, values, projection="top"
        )
        
        assert heatmap is not None
        assert heatmap.shape == heatmap_generator.grid_resolution
        assert np.any(~np.isnan(heatmap))  # Some non-NaN values

    @pytest.mark.asyncio
    async def test_generate_surface_heatmap(self, heatmap_generator):
        """Test surface heatmap generation."""
        # Create test data
        positions = {
            "Fp1": (-0.3, 0.9, 0.0),
            "Fp2": (0.3, 0.9, 0.0),
        }
        values = {"Fp1": 0.8, "Fp2": 0.6}
        
        # Create simple mesh
        vertices = np.random.randn(100, 3) * 0.1
        faces = np.random.randint(0, 100, (200, 3))
        
        # Generate heatmap
        colors = await heatmap_generator.generate_surface_heatmap(
            positions, values, vertices, faces
        )
        
        assert colors is not None
        assert colors.shape == (100, 4)  # RGBA for each vertex
        assert np.all(colors >= 0) and np.all(colors <= 1)  # Valid color range


class TestVRController:
    """Test VR Controller."""

    @pytest.fixture
    def vr_controller(self):
        """Create VR Controller instance."""
        return VRController()

    @pytest.mark.asyncio
    async def test_initialize(self, vr_controller):
        """Test VR initialization."""
        # Mock OpenXR availability
        with patch.object(vr_controller, "_initialize_openxr", return_value=True):
            result = await vr_controller.initialize()
            assert result is True

    @pytest.mark.asyncio
    async def test_update_controllers(self, vr_controller):
        """Test controller update."""
        # Mock controller data
        vr_controller.left_controller = Mock()
        vr_controller.right_controller = Mock()
        
        vr_controller.left_controller.position = (0, 1, 0)
        vr_controller.left_controller.rotation = (0, 0, 0, 1)
        vr_controller.right_controller.position = (0, 1, 0)
        vr_controller.right_controller.rotation = (0, 0, 0, 1)
        
        # Update should not crash
        await vr_controller.update()

    def test_haptic_feedback(self, vr_controller):
        """Test haptic feedback."""
        # Mock controller
        vr_controller.left_controller = Mock()
        vr_controller.left_controller.trigger_haptic = Mock()
        
        # Trigger haptic
        vr_controller.trigger_haptic("left", intensity=0.5, duration=0.1)
        vr_controller.left_controller.trigger_haptic.assert_called_once()


class TestVisualizationAPI:
    """Test Visualization API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from src.api.main import app
        app.config["TESTING"] = True
        return app.test_client()

    def test_status_endpoint(self, client):
        """Test status endpoint."""
        response = client.get("/api/v1/visualization/status")
        assert response.status_code == 200
        data = response.get_json()
        assert "connected" in data
        assert "session_id" in data

    def test_connect_endpoint(self, client):
        """Test connect endpoint."""
        # Mock successful connection
        with patch("src.api.visualization_api.get_omniverse_connector") as mock_get:
            mock_connector = Mock()
            mock_connector.connect = AsyncMock(return_value=True)
            mock_connector.session_id = "test-123"
            mock_get.return_value = mock_connector
            
            response = client.post(
                "/api/v1/visualization/connect",
                json={"nucleus_server": "localhost:3030"},
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data["status"] == "connected"

    def test_electrode_setup_endpoint(self, client):
        """Test electrode setup endpoint."""
        with patch("src.api.visualization_api.electrode_models") as mock_models:
            mock_models.create_electrode_models = AsyncMock(
                return_value={"Fp1": {}, "Fp2": {}}
            )
            
            response = client.post(
                "/api/v1/visualization/electrodes",
                json={"montage": "10-20"},
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data["status"] == "configured"
            assert data["montage"] == "10-20"

    def test_vr_enable_endpoint(self, client):
        """Test VR enable endpoint."""
        with patch("src.api.visualization_api.get_omniverse_connector") as mock_get:
            mock_connector = Mock()
            mock_connector.config = Mock()
            mock_get.return_value = mock_connector
            
            response = client.post(
                "/api/v1/visualization/vr/enable",
                json={"platform": "openxr"},
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data["status"] == "enabled"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])