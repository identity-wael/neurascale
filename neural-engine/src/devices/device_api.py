"""API endpoints for device management and WebSocket notifications."""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from pydantic import BaseModel

from .device_manager import DeviceManager
from .interfaces.base_device import DeviceState

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/devices", tags=["devices"])

# Global device manager instance (should be initialized by the application)
device_manager: Optional[DeviceManager] = None


def get_device_manager() -> DeviceManager:
    """Get the device manager instance."""
    if device_manager is None:
        raise HTTPException(status_code=500, detail="Device manager not initialized")
    return device_manager


class DeviceConnectionRequest(BaseModel):
    """Request model for device connection."""

    device_id: str
    device_type: str
    connection_params: Dict[str, Any] = {}


class ImpedanceCheckRequest(BaseModel):
    """Request model for impedance check."""

    device_id: str
    channel_ids: Optional[List[int]] = None


class DeviceInfo(BaseModel):
    """Device information response model."""

    device_id: str
    device_name: str
    state: str
    connected: bool
    streaming: bool
    capabilities: Optional[Dict[str, Any]] = None


@router.get("/")
async def list_devices(
    manager: DeviceManager = Depends(get_device_manager),
) -> List[DeviceInfo]:
    """List all registered devices."""
    devices = manager.list_devices()
    return [DeviceInfo(**device) for device in devices]


@router.post("/add")
async def add_device(
    request: DeviceConnectionRequest,
    manager: DeviceManager = Depends(get_device_manager),
) -> DeviceInfo:
    """Add a new device to the manager."""
    try:
        device = await manager.add_device(
            request.device_id, request.device_type, **request.connection_params
        )

        return DeviceInfo(
            device_id=device.device_id,
            device_name=device.device_name,
            state=device.state.value,
            connected=device.is_connected(),
            streaming=device.is_streaming(),
            capabilities=None,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{device_id}/connect")
async def connect_device(
    device_id: str, manager: DeviceManager = Depends(get_device_manager)
) -> Dict[str, Any]:
    """Connect to a specific device."""
    try:
        success = await manager.connect_device(device_id)
        device = manager.get_device(device_id)

        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        return {
            "success": success,
            "device_id": device_id,
            "state": device.state.value,
            "capabilities": device.get_capabilities() if success else None,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/disconnect")
async def disconnect_device(
    device_id: str, manager: DeviceManager = Depends(get_device_manager)
) -> Dict[str, str]:
    """Disconnect a specific device."""
    try:
        await manager.disconnect_device(device_id)
        return {"status": "disconnected", "device_id": device_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/start-streaming")
async def start_streaming(
    device_id: str, manager: DeviceManager = Depends(get_device_manager)
) -> Dict[str, str]:
    """Start streaming from a specific device."""
    try:
        await manager.start_streaming([device_id])
        return {"status": "streaming", "device_id": device_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/stop-streaming")
async def stop_streaming(
    device_id: str, manager: DeviceManager = Depends(get_device_manager)
) -> Dict[str, str]:
    """Stop streaming from a specific device."""
    try:
        await manager.stop_streaming([device_id])
        return {"status": "stopped", "device_id": device_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-impedance")
async def check_impedance(
    request: ImpedanceCheckRequest, manager: DeviceManager = Depends(get_device_manager)
) -> Dict[str, Any]:
    """Check impedance for a device."""
    try:
        impedance_results = await manager.check_device_impedance(
            request.device_id, request.channel_ids
        )

        return {
            "device_id": request.device_id,
            "impedance_values": impedance_results,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/signal-quality")
async def get_signal_quality(
    device_id: str,
    channel_ids: Optional[str] = None,  # Comma-separated list
    manager: DeviceManager = Depends(get_device_manager),
) -> Dict[str, Any]:
    """Get signal quality for device channels."""
    try:
        device = manager.get_device(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        if not device.is_streaming():
            raise HTTPException(status_code=400, detail="Device must be streaming")

        # Parse channel IDs
        channels = None
        if channel_ids:
            channels = [int(ch) for ch in channel_ids.split(",")]

        # Get signal quality (assuming device has this method)
        if hasattr(device, "get_signal_quality"):
            quality_metrics = await device.get_signal_quality(channels)

            return {
                "device_id": device_id,
                "signal_quality": {
                    str(ch_id): {
                        "snr_db": metrics.snr_db,
                        "quality_level": metrics.quality_level.value,
                        "rms_amplitude": metrics.rms_amplitude,
                        "artifacts_detected": metrics.artifacts_detected,
                    }
                    for ch_id, metrics in quality_metrics.items()
                },
                "timestamp": datetime.utcnow().isoformat(),
            }
        else:
            raise HTTPException(
                status_code=501,
                detail="Device does not support signal quality monitoring",
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/discover")
async def discover_devices(
    timeout: float = 5.0, manager: DeviceManager = Depends(get_device_manager)
) -> List[Dict[str, Any]]:
    """Discover available devices."""
    try:
        discovered = await manager.auto_discover_devices(timeout)
        return discovered
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/health")
async def get_device_health(
    device_id: str, manager: DeviceManager = Depends(get_device_manager)
) -> Dict[str, Any]:
    """Get device health information."""
    try:
        health_info = manager.get_device_health(device_id)
        return health_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/notifications")
async def device_notifications_websocket(
    websocket: WebSocket, manager: DeviceManager = Depends(get_device_manager)
):
    """WebSocket endpoint for real-time device notifications."""
    # Accept connection
    await manager.notification_service.connect(websocket)

    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_json()

            # Handle client messages
            await manager.notification_service.handle_client_message(websocket, data)

    except WebSocketDisconnect:
        # Client disconnected
        await manager.notification_service.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.notification_service.disconnect(websocket)


def initialize_device_manager(manager: DeviceManager):
    """Initialize the global device manager instance."""
    global device_manager
    device_manager = manager
    logger.info("Device manager initialized for API")
