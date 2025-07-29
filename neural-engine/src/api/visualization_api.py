"""API endpoints for NVIDIA Omniverse visualization."""

from flask import Blueprint, jsonify, request, Response
import logging
from typing import Optional
from datetime import datetime

# Import visualization components
from ..visualization.omniverse.neural_omniverse_connector import (
    NeuralOmniverseConnector,
)
from ..visualization.omniverse.models.electrode_models import ElectrodeModels
from ..visualization.omniverse.analytics.heatmap_generator import HeatmapGenerator
from ..visualization.omniverse.analytics.flow_visualizer import FlowVisualizer
from ..core.config import get_config

logger = logging.getLogger(__name__)

visualization_api = Blueprint(
    "visualization", __name__, url_prefix="/api/v1/visualization"
)

# Global instances
omniverse_connector: Optional[NeuralOmniverseConnector] = None
electrode_models = ElectrodeModels()
heatmap_generator = HeatmapGenerator()
flow_visualizer = FlowVisualizer()


def get_omniverse_connector() -> NeuralOmniverseConnector:
    """Get or create Omniverse connector instance."""
    global omniverse_connector
    if omniverse_connector is None:
        config = get_config()
        omniverse_connector = NeuralOmniverseConnector(config)
    return omniverse_connector


@visualization_api.route("/status", methods=["GET"])
def get_visualization_status() -> Response:
    """Get visualization system status."""
    try:
        connector = get_omniverse_connector()

        status = {
            "connected": connector.is_connected,
            "session_id": connector.session_id,
            "visualization_mode": connector.config.visualization_mode.value,
            "vr_enabled": connector.config.enable_vr,
            "streaming_active": hasattr(connector, "_streaming_active")
            and connector._streaming_active,
            "timestamp": datetime.utcnow().isoformat(),
        }

        return jsonify(status), 200

    except Exception as e:
        logger.error(f"Failed to get visualization status: {e}")
        return jsonify({"error": str(e)}), 500


@visualization_api.route("/connect", methods=["POST"])
async def connect_to_omniverse() -> Response:
    """Connect to NVIDIA Omniverse."""
    try:
        data = request.get_json() or {}

        # Get connection parameters
        nucleus_server = data.get("nucleus_server", "localhost:3030")
        project_path = data.get("project_path", "/neurascale/default")

        connector = get_omniverse_connector()

        # Update configuration
        connector.config.nucleus_server = nucleus_server
        connector.config.project_path = project_path

        # Connect
        success = await connector.connect()

        if success:
            return (
                jsonify(
                    {
                        "status": "connected",
                        "session_id": connector.session_id,
                        "nucleus_server": nucleus_server,
                        "project_path": project_path,
                    }
                ),
                200,
            )
        else:
            return jsonify({"error": "Failed to connect to Omniverse"}), 500

    except Exception as e:
        logger.error(f"Failed to connect to Omniverse: {e}")
        return jsonify({"error": str(e)}), 500


@visualization_api.route("/disconnect", methods=["POST"])
async def disconnect_from_omniverse() -> Response:
    """Disconnect from NVIDIA Omniverse."""
    try:
        connector = get_omniverse_connector()
        await connector.disconnect()

        return jsonify({"status": "disconnected"}), 200

    except Exception as e:
        logger.error(f"Failed to disconnect from Omniverse: {e}")
        return jsonify({"error": str(e)}), 500


@visualization_api.route("/brain-model", methods=["POST"])
async def load_brain_model() -> Response:
    """Load brain model from MRI/CT data."""
    try:
        data = request.get_json() or {}

        # Get model parameters
        model_source = data.get("source", "template")  # template, mri_file, ct_file
        file_path = data.get("file_path")
        resolution = data.get("resolution", "medium")  # low, medium, high

        connector = get_omniverse_connector()

        # Load brain model
        if model_source == "template":
            success = await connector.brain_mesh_loader.load_template_brain(resolution)
        else:
            if not file_path:
                return jsonify({"error": "file_path required for MRI/CT source"}), 400
            success = await connector.brain_mesh_loader.load_from_file(file_path)

        if success:
            return (
                jsonify(
                    {
                        "status": "loaded",
                        "source": model_source,
                        "resolution": resolution,
                        "vertex_count": len(connector.brain_mesh_loader.vertices),
                        "face_count": len(connector.brain_mesh_loader.faces),
                    }
                ),
                200,
            )
        else:
            return jsonify({"error": "Failed to load brain model"}), 500

    except Exception as e:
        logger.error(f"Failed to load brain model: {e}")
        return jsonify({"error": str(e)}), 500


@visualization_api.route("/electrodes", methods=["POST"])
async def setup_electrodes() -> Response:
    """Setup electrode positions."""
    try:
        data = request.get_json() or {}

        # Get electrode configuration
        montage = data.get("montage", "10-20")  # 10-20, 10-10, HD-128, BCI-8x8
        scale_to_head = data.get("scale_to_head", True)

        # Create electrode models
        models = await electrode_models.create_electrode_models(
            montage_name=montage, scale_to_head=scale_to_head
        )

        # Update connector
        connector = get_omniverse_connector()
        if hasattr(connector, "electrode_models"):
            connector.electrode_models = electrode_models

        return (
            jsonify(
                {
                    "status": "configured",
                    "montage": montage,
                    "electrode_count": len(models),
                    "channels": list(models.keys()),
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Failed to setup electrodes: {e}")
        return jsonify({"error": str(e)}), 500


@visualization_api.route("/stream/start", methods=["POST"])
async def start_streaming() -> Response:
    """Start real-time data streaming."""
    try:
        data = request.get_json() or {}

        # Get streaming parameters
        source = data.get("source", "live")  # live, file, simulation
        sample_rate = data.get("sample_rate", 1000)

        connector = get_omniverse_connector()

        # Start streaming based on source
        if source == "live":
            # Connect to live data source
            pass  # Implementation depends on device interface
        elif source == "simulation":
            # Start simulated data
            await connector._start_simulated_stream(sample_rate)
        else:
            return jsonify({"error": f"Unknown source: {source}"}), 400

        return (
            jsonify(
                {"status": "streaming", "source": source, "sample_rate": sample_rate}
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Failed to start streaming: {e}")
        return jsonify({"error": str(e)}), 500


@visualization_api.route("/stream/stop", methods=["POST"])
async def stop_streaming() -> Response:
    """Stop real-time data streaming."""
    try:
        connector = get_omniverse_connector()

        # Stop streaming
        if hasattr(connector, "_streaming_active"):
            connector._streaming_active = False

        return jsonify({"status": "stopped"}), 200

    except Exception as e:
        logger.error(f"Failed to stop streaming: {e}")
        return jsonify({"error": str(e)}), 500


@visualization_api.route("/heatmap/generate", methods=["POST"])
async def generate_heatmap() -> Response:
    """Generate activity heatmap."""
    try:
        data = request.get_json() or {}

        # Get heatmap parameters
        heatmap_type = data.get("type", "surface")  # surface, 2d_projection, volume
        electrode_values = data.get("values", {})
        colormap = data.get("colormap", "viridis")

        # Set colormap
        heatmap_generator.set_colormap(colormap)

        # Get electrode positions
        positions = {}
        for channel in electrode_values:
            pos = electrode_models.get_electrode_position(channel)
            if pos:
                positions[channel] = pos

        # Generate heatmap based on type
        if heatmap_type == "2d_projection":
            projection = data.get("projection", "top")
            heatmap = await heatmap_generator.generate_2d_projection(
                positions, electrode_values, projection
            )

            return (
                jsonify(
                    {
                        "status": "generated",
                        "type": heatmap_type,
                        "projection": projection,
                        "shape": heatmap.shape,
                        "colormap": colormap,
                    }
                ),
                200,
            )
        else:
            return (
                jsonify({"error": f"Heatmap type {heatmap_type} not yet implemented"}),
                501,
            )

    except Exception as e:
        logger.error(f"Failed to generate heatmap: {e}")
        return jsonify({"error": str(e)}), 500


@visualization_api.route("/flow/connectivity", methods=["POST"])
async def visualize_connectivity() -> Response:
    """Visualize connectivity flow."""
    try:
        data = request.get_json() or {}

        # Get connectivity parameters
        connectivity_matrix = data.get("matrix", [])
        threshold = data.get("threshold", 0.3)
        frequency_band = data.get("frequency_band")

        # Get electrode positions
        positions = {}
        channels = data.get("channels", [])
        for channel in channels:
            pos = electrode_models.get_electrode_position(channel)
            if pos:
                positions[channel] = pos

        # Create connectivity flow
        flow_paths = await flow_visualizer.create_connectivity_flow(
            connectivity_matrix=connectivity_matrix,
            node_positions=positions,
            threshold=threshold,
            frequency_band=frequency_band,
        )

        return (
            jsonify(
                {
                    "status": "generated",
                    "flow_paths": len(flow_paths),
                    "threshold": threshold,
                    "frequency_band": frequency_band,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Failed to visualize connectivity: {e}")
        return jsonify({"error": str(e)}), 500


@visualization_api.route("/vr/enable", methods=["POST"])
async def enable_vr() -> Response:
    """Enable VR mode."""
    try:
        data = request.get_json() or {}

        # Get VR parameters
        platform = data.get("platform", "openxr")  # openxr, oculus, steamvr

        connector = get_omniverse_connector()

        # Enable VR
        connector.config.enable_vr = True

        # Initialize VR controller if available
        if hasattr(connector, "vr_controller"):
            success = await connector.vr_controller.initialize(platform)

            if success:
                return (
                    jsonify(
                        {
                            "status": "enabled",
                            "platform": platform,
                            "controllers_detected": connector.vr_controller.left_controller
                            is not None,
                        }
                    ),
                    200,
                )

        return jsonify({"status": "enabled", "platform": platform}), 200

    except Exception as e:
        logger.error(f"Failed to enable VR: {e}")
        return jsonify({"error": str(e)}), 500


@visualization_api.route("/vr/disable", methods=["POST"])
async def disable_vr() -> Response:
    """Disable VR mode."""
    try:
        connector = get_omniverse_connector()

        # Disable VR
        connector.config.enable_vr = False

        # Shutdown VR controller if available
        if hasattr(connector, "vr_controller"):
            await connector.vr_controller.shutdown()

        return jsonify({"status": "disabled"}), 200

    except Exception as e:
        logger.error(f"Failed to disable VR: {e}")
        return jsonify({"error": str(e)}), 500


@visualization_api.route("/animation/create", methods=["POST"])
async def create_animation() -> Response:
    """Create animation."""
    try:
        data = request.get_json() or {}

        # Get animation parameters
        animation_type = data.get("type", "neural_activity")
        duration = data.get("duration", 10.0)

        connector = get_omniverse_connector()

        if animation_type == "neural_activity":
            frequency = data.get("frequency", 1.0)
            amplitude = data.get("amplitude", 1.0)

            track_name = connector.animation_engine.create_neural_activity_animation(
                duration=duration, frequency=frequency, amplitude=amplitude
            )
        elif animation_type == "camera_orbit":
            radius = data.get("radius", 2.0)
            vertical_angle = data.get("vertical_angle", 30.0)

            track_name = connector.animation_engine.create_camera_orbit_animation(
                duration=duration, radius=radius, vertical_angle=vertical_angle
            )
        else:
            return jsonify({"error": f"Unknown animation type: {animation_type}"}), 400

        return (
            jsonify(
                {
                    "status": "created",
                    "type": animation_type,
                    "track_name": track_name,
                    "duration": duration,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Failed to create animation: {e}")
        return jsonify({"error": str(e)}), 500


@visualization_api.route("/animation/control", methods=["POST"])
def control_animation() -> Response:
    """Control animation playback."""
    try:
        data = request.get_json() or {}

        # Get control action
        action = data.get("action", "play")  # play, pause, stop, seek

        connector = get_omniverse_connector()

        if action == "play":
            connector.animation_engine.play()
        elif action == "pause":
            connector.animation_engine.pause()
        elif action == "stop":
            connector.animation_engine.stop()
        elif action == "seek":
            time = data.get("time", 0.0)
            connector.animation_engine.seek(time)
        else:
            return jsonify({"error": f"Unknown action: {action}"}), 400

        return (
            jsonify(
                {
                    "status": action,
                    "current_time": connector.animation_engine.current_time,
                    "is_playing": connector.animation_engine.is_playing,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Failed to control animation: {e}")
        return jsonify({"error": str(e)}), 500


@visualization_api.route("/settings", methods=["GET", "POST"])
def visualization_settings() -> Response:
    """Get or update visualization settings."""
    try:
        connector = get_omniverse_connector()

        if request.method == "GET":
            # Return current settings
            settings = {
                "visualization_mode": connector.config.visualization_mode.value,
                "enable_vr": connector.config.enable_vr,
                "enable_haptics": connector.config.enable_haptics,
                "quality_preset": connector.config.quality_preset,
                "max_fps": connector.config.max_fps,
                "particle_limit": connector.config.particle_limit,
            }
            return jsonify(settings), 200

        else:  # POST
            data = request.get_json() or {}

            # Update settings
            if "visualization_mode" in data:
                # Update mode (would need to handle enum conversion)
                pass
            if "enable_vr" in data:
                connector.config.enable_vr = data["enable_vr"]
            if "enable_haptics" in data:
                connector.config.enable_haptics = data["enable_haptics"]
            if "quality_preset" in data:
                connector.config.quality_preset = data["quality_preset"]
            if "max_fps" in data:
                connector.config.max_fps = data["max_fps"]
            if "particle_limit" in data:
                connector.config.particle_limit = data["particle_limit"]

            return jsonify({"status": "updated"}), 200

    except Exception as e:
        logger.error(f"Failed to handle visualization settings: {e}")
        return jsonify({"error": str(e)}), 500
