"""REST API endpoints for device management."""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
import json

from flask import Blueprint, jsonify, request, Response
from flask_cors import CORS

from ..devices.device_manager import DeviceManager
from ..devices.interfaces.base_device import DeviceState

logger = logging.getLogger(__name__)

# Create Blueprint
device_api = Blueprint('device_api', __name__, url_prefix='/api/v1/devices')
CORS(device_api)  # Enable CORS for device API

# Global device manager instance
_device_manager: Optional[DeviceManager] = None
_event_loop: Optional[asyncio.AbstractEventLoop] = None


def get_device_manager() -> DeviceManager:
    """Get or create device manager instance."""
    global _device_manager
    if _device_manager is None:
        _device_manager = DeviceManager()
    return _device_manager


def get_event_loop() -> asyncio.AbstractEventLoop:
    """Get or create event loop for async operations."""
    global _event_loop
    if _event_loop is None:
        try:
            _event_loop = asyncio.get_running_loop()
        except RuntimeError:
            _event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(_event_loop)
    return _event_loop


def run_async(coro):
    """Run async coroutine in the event loop."""
    loop = get_event_loop()
    return loop.run_until_complete(coro)


# Device Management Endpoints

@device_api.route('/', methods=['GET'])
def list_devices() -> Response:
    """
    List all devices.

    Returns:
        JSON array of device information
    """
    try:
        manager = get_device_manager()
        devices = manager.list_devices()
        return jsonify(devices)
    except Exception as e:
        logger.error(f"Error listing devices: {e}")
        return jsonify({"error": str(e)}), 500


@device_api.route('/<device_id>', methods=['GET'])
def get_device(device_id: str) -> Response:
    """
    Get specific device information.

    Args:
        device_id: Device identifier

    Returns:
        JSON object with device information
    """
    try:
        manager = get_device_manager()
        device = manager.get_device(device_id)

        if not device:
            return jsonify({"error": "Device not found"}), 404

        device_info = {
            "device_id": device_id,
            "device_name": device.device_name,
            "state": device.state.value,
            "connected": device.is_connected(),
            "streaming": device.is_streaming(),
            "session_id": device.session_id,
        }

        if device.is_connected():
            device_info["capabilities"] = {
                "supported_sampling_rates": device.get_capabilities().supported_sampling_rates,
                "max_channels": device.get_capabilities().max_channels,
                "signal_types": [st.value for st in device.get_capabilities().signal_types],
                "has_impedance_check": device.get_capabilities().has_impedance_check,
                "has_battery_monitor": device.get_capabilities().has_battery_monitor,
            }

        return jsonify(device_info)

    except Exception as e:
        logger.error(f"Error getting device {device_id}: {e}")
        return jsonify({"error": str(e)}), 500


@device_api.route('/', methods=['POST'])
def add_device() -> Response:
    """
    Add a new device.

    Request body:
        {
            "device_id": "unique_id",
            "device_type": "lsl|openbci|brainflow|synthetic",
            "device_config": {
                // Device-specific configuration
            }
        }

    Returns:
        JSON object with device information
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        device_id = data.get("device_id")
        device_type = data.get("device_type")
        device_config = data.get("device_config", {})

        if not device_id or not device_type:
            return jsonify({"error": "device_id and device_type are required"}), 400

        manager = get_device_manager()
        device = run_async(manager.add_device(device_id, device_type, **device_config))

        return jsonify({
            "device_id": device_id,
            "device_name": device.device_name,
            "state": device.state.value,
            "message": f"Device {device_id} added successfully"
        }), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error adding device: {e}")
        return jsonify({"error": str(e)}), 500


@device_api.route('/<device_id>', methods=['DELETE'])
def remove_device(device_id: str) -> Response:
    """
    Remove a device.

    Args:
        device_id: Device identifier

    Returns:
        JSON object with success message
    """
    try:
        manager = get_device_manager()
        run_async(manager.remove_device(device_id))

        return jsonify({
            "message": f"Device {device_id} removed successfully"
        })

    except Exception as e:
        logger.error(f"Error removing device {device_id}: {e}")
        return jsonify({"error": str(e)}), 500


# Device Control Endpoints

@device_api.route('/<device_id>/connect', methods=['POST'])
def connect_device(device_id: str) -> Response:
    """
    Connect to a device.

    Args:
        device_id: Device identifier

    Request body (optional):
        {
            "connection_params": {
                // Device-specific connection parameters
            }
        }

    Returns:
        JSON object with connection status
    """
    try:
        data = request.get_json() or {}
        connection_params = data.get("connection_params", {})

        manager = get_device_manager()
        success = run_async(manager.connect_device(device_id, **connection_params))

        if success:
            return jsonify({
                "device_id": device_id,
                "connected": True,
                "message": f"Device {device_id} connected successfully"
            })
        else:
            return jsonify({
                "device_id": device_id,
                "connected": False,
                "error": "Failed to connect to device"
            }), 500

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error connecting device {device_id}: {e}")
        return jsonify({"error": str(e)}), 500


@device_api.route('/<device_id>/disconnect', methods=['POST'])
def disconnect_device(device_id: str) -> Response:
    """
    Disconnect from a device.

    Args:
        device_id: Device identifier

    Returns:
        JSON object with disconnection status
    """
    try:
        manager = get_device_manager()
        run_async(manager.disconnect_device(device_id))

        return jsonify({
            "device_id": device_id,
            "connected": False,
            "message": f"Device {device_id} disconnected successfully"
        })

    except Exception as e:
        logger.error(f"Error disconnecting device {device_id}: {e}")
        return jsonify({"error": str(e)}), 500


@device_api.route('/<device_id>/stream/start', methods=['POST'])
def start_streaming(device_id: str) -> Response:
    """
    Start streaming from a device.

    Args:
        device_id: Device identifier

    Returns:
        JSON object with streaming status
    """
    try:
        manager = get_device_manager()
        run_async(manager.start_streaming([device_id]))

        return jsonify({
            "device_id": device_id,
            "streaming": True,
            "session_id": manager.active_session_id,
            "message": f"Device {device_id} started streaming"
        })

    except Exception as e:
        logger.error(f"Error starting stream for device {device_id}: {e}")
        return jsonify({"error": str(e)}), 500


@device_api.route('/<device_id>/stream/stop', methods=['POST'])
def stop_streaming(device_id: str) -> Response:
    """
    Stop streaming from a device.

    Args:
        device_id: Device identifier

    Returns:
        JSON object with streaming status
    """
    try:
        manager = get_device_manager()
        run_async(manager.stop_streaming([device_id]))

        return jsonify({
            "device_id": device_id,
            "streaming": False,
            "message": f"Device {device_id} stopped streaming"
        })

    except Exception as e:
        logger.error(f"Error stopping stream for device {device_id}: {e}")
        return jsonify({"error": str(e)}), 500


# Device Discovery Endpoints

@device_api.route('/discover', methods=['GET'])
def discover_devices() -> Response:
    """
    Discover available devices.

    Query parameters:
        - timeout: Discovery timeout in seconds (default: 10)
        - protocols: Comma-separated list of protocols to scan

    Returns:
        JSON array of discovered devices
    """
    try:
        timeout = float(request.args.get('timeout', 10))
        protocols = request.args.get('protocols', '').split(',') if request.args.get('protocols') else None

        manager = get_device_manager()
        discovered = run_async(manager.auto_discover_devices(timeout=timeout))

        return jsonify(discovered)

    except Exception as e:
        logger.error(f"Error discovering devices: {e}")
        return jsonify({"error": str(e)}), 500


@device_api.route('/discover/<discovery_id>/create', methods=['POST'])
def create_from_discovery(discovery_id: str) -> Response:
    """
    Create a device from discovery.

    Args:
        discovery_id: Discovery identifier

    Request body (optional):
        {
            "device_id": "custom_device_id"  // Optional custom ID
        }

    Returns:
        JSON object with created device information
    """
    try:
        data = request.get_json() or {}
        custom_device_id = data.get("device_id")

        manager = get_device_manager()
        device = run_async(manager.create_device_from_discovery(
            discovery_id,
            device_id=custom_device_id
        ))

        return jsonify({
            "device_id": custom_device_id or discovery_id,
            "device_name": device.device_name,
            "state": device.state.value,
            "message": "Device created successfully from discovery"
        }), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error creating device from discovery: {e}")
        return jsonify({"error": str(e)}), 500


# Device Health and Telemetry Endpoints

@device_api.route('/health', methods=['GET'])
def get_health() -> Response:
    """
    Get health status for all devices or specific device.

    Query parameters:
        - device_id: Specific device ID (optional)

    Returns:
        JSON object with health information
    """
    try:
        device_id = request.args.get('device_id')
        manager = get_device_manager()

        health_info = manager.get_device_health(device_id)
        return jsonify(health_info)

    except Exception as e:
        logger.error(f"Error getting health info: {e}")
        return jsonify({"error": str(e)}), 500


@device_api.route('/health/alerts', methods=['GET'])
def get_health_alerts() -> Response:
    """
    Get active health alerts.

    Query parameters:
        - device_id: Specific device ID (optional)

    Returns:
        JSON array of health alerts
    """
    try:
        device_id = request.args.get('device_id')
        manager = get_device_manager()

        alerts = manager.get_health_alerts(device_id)
        return jsonify(alerts)

    except Exception as e:
        logger.error(f"Error getting health alerts: {e}")
        return jsonify({"error": str(e)}), 500


@device_api.route('/health/monitoring/start', methods=['POST'])
def start_health_monitoring() -> Response:
    """
    Start health monitoring for all devices.

    Returns:
        JSON object with monitoring status
    """
    try:
        manager = get_device_manager()
        run_async(manager.start_health_monitoring())

        return jsonify({
            "monitoring": True,
            "message": "Health monitoring started"
        })

    except Exception as e:
        logger.error(f"Error starting health monitoring: {e}")
        return jsonify({"error": str(e)}), 500


@device_api.route('/health/monitoring/stop', methods=['POST'])
def stop_health_monitoring() -> Response:
    """
    Stop health monitoring for all devices.

    Returns:
        JSON object with monitoring status
    """
    try:
        manager = get_device_manager()
        run_async(manager.stop_health_monitoring())

        return jsonify({
            "monitoring": False,
            "message": "Health monitoring stopped"
        })

    except Exception as e:
        logger.error(f"Error stopping health monitoring: {e}")
        return jsonify({"error": str(e)}), 500


@device_api.route('/telemetry/start', methods=['POST'])
def start_telemetry() -> Response:
    """
    Start telemetry collection.

    Request body:
        {
            "output_dir": "/path/to/telemetry",  // Optional
            "enable_cloud": false  // Optional
        }

    Returns:
        JSON object with telemetry status
    """
    try:
        data = request.get_json() or {}
        output_dir = data.get("output_dir")
        enable_cloud = data.get("enable_cloud", False)

        manager = get_device_manager()
        run_async(manager.start_telemetry_collection(
            output_dir=Path(output_dir) if output_dir else None,
            enable_cloud=enable_cloud
        ))

        return jsonify({
            "telemetry": True,
            "output_dir": output_dir,
            "cloud_enabled": enable_cloud,
            "message": "Telemetry collection started"
        })

    except Exception as e:
        logger.error(f"Error starting telemetry: {e}")
        return jsonify({"error": str(e)}), 500


@device_api.route('/telemetry/stop', methods=['POST'])
def stop_telemetry() -> Response:
    """
    Stop telemetry collection.

    Returns:
        JSON object with telemetry statistics
    """
    try:
        manager = get_device_manager()
        stats = manager.get_telemetry_statistics()
        run_async(manager.stop_telemetry_collection())

        return jsonify({
            "telemetry": False,
            "statistics": stats,
            "message": "Telemetry collection stopped"
        })

    except Exception as e:
        logger.error(f"Error stopping telemetry: {e}")
        return jsonify({"error": str(e)}), 500


@device_api.route('/telemetry/stats', methods=['GET'])
def get_telemetry_stats() -> Response:
    """
    Get telemetry statistics.

    Returns:
        JSON object with telemetry statistics
    """
    try:
        manager = get_device_manager()
        stats = manager.get_telemetry_statistics()

        return jsonify(stats)

    except Exception as e:
        logger.error(f"Error getting telemetry stats: {e}")
        return jsonify({"error": str(e)}), 500


# Session Management Endpoints

@device_api.route('/session/start', methods=['POST'])
def start_session() -> Response:
    """
    Start a new recording session.

    Request body (optional):
        {
            "session_id": "custom_session_id"  // Optional
        }

    Returns:
        JSON object with session information
    """
    try:
        data = request.get_json() or {}
        session_id = data.get("session_id")

        manager = get_device_manager()
        session_id = manager.start_session(session_id)

        return jsonify({
            "session_id": session_id,
            "started_at": datetime.now().isoformat(),
            "message": "Session started successfully"
        })

    except Exception as e:
        logger.error(f"Error starting session: {e}")
        return jsonify({"error": str(e)}), 500


@device_api.route('/session/end', methods=['POST'])
def end_session() -> Response:
    """
    End the current recording session.

    Returns:
        JSON object with session information
    """
    try:
        manager = get_device_manager()
        session_id = manager.active_session_id
        manager.end_session()

        return jsonify({
            "session_id": session_id,
            "ended_at": datetime.now().isoformat(),
            "message": "Session ended successfully"
        })

    except Exception as e:
        logger.error(f"Error ending session: {e}")
        return jsonify({"error": str(e)}), 500


@device_api.route('/session', methods=['GET'])
def get_session() -> Response:
    """
    Get current session information.

    Returns:
        JSON object with session information
    """
    try:
        manager = get_device_manager()

        if manager.active_session_id:
            return jsonify({
                "session_id": manager.active_session_id,
                "active": True
            })
        else:
            return jsonify({
                "session_id": None,
                "active": False
            })

    except Exception as e:
        logger.error(f"Error getting session: {e}")
        return jsonify({"error": str(e)}), 500


# Device-specific Operations

@device_api.route('/<device_id>/impedance', methods=['GET'])
def check_impedance(device_id: str) -> Response:
    """
    Check impedance for a device.

    Args:
        device_id: Device identifier

    Query parameters:
        - channels: Comma-separated list of channel IDs (optional)

    Returns:
        JSON object with impedance values
    """
    try:
        channels = request.args.get('channels')
        channel_ids = [int(ch) for ch in channels.split(',')] if channels else None

        manager = get_device_manager()
        device = manager.get_device(device_id)

        if not device:
            return jsonify({"error": "Device not found"}), 404

        if not device.is_connected():
            return jsonify({"error": "Device not connected"}), 400

        impedances = run_async(device.check_impedance(channel_ids))

        return jsonify({
            "device_id": device_id,
            "impedances": {
                str(ch): {"value_ohms": imp, "value_kohms": imp/1000}
                for ch, imp in impedances.items()
            },
            "timestamp": datetime.now().isoformat()
        })

    except NotImplementedError:
        return jsonify({"error": "Device does not support impedance checking"}), 501
    except Exception as e:
        logger.error(f"Error checking impedance: {e}")
        return jsonify({"error": str(e)}), 500


@device_api.route('/<device_id>/signal-quality', methods=['GET'])
def get_signal_quality(device_id: str) -> Response:
    """
    Get signal quality metrics for a device.

    Args:
        device_id: Device identifier

    Query parameters:
        - channels: Comma-separated list of channel IDs (optional)

    Returns:
        JSON object with signal quality metrics
    """
    try:
        channels = request.args.get('channels')
        channel_ids = [int(ch) for ch in channels.split(',')] if channels else None

        manager = get_device_manager()
        device = manager.get_device(device_id)

        if not device:
            return jsonify({"error": "Device not found"}), 404

        if not device.is_streaming():
            return jsonify({"error": "Device must be streaming to assess signal quality"}), 400

        if hasattr(device, 'get_signal_quality'):
            quality_metrics = run_async(device.get_signal_quality(channel_ids))

            return jsonify({
                "device_id": device_id,
                "signal_quality": {
                    str(ch_id): {
                        "snr_db": metrics.snr_db,
                        "quality_level": metrics.quality_level.value,
                        "is_acceptable": metrics.is_acceptable,
                        "rms_amplitude": metrics.rms_amplitude,
                        "line_noise_power": metrics.line_noise_power,
                        "artifacts_detected": metrics.artifacts_detected,
                    }
                    for ch_id, metrics in quality_metrics.items()
                },
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({"error": "Device does not support signal quality assessment"}), 501

    except Exception as e:
        logger.error(f"Error getting signal quality: {e}")
        return jsonify({"error": str(e)}), 500
