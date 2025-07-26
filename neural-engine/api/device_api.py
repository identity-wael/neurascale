"""FastAPI Device Management API for NeuraScale Neural Engine.

This module provides REST API endpoints for device discovery, connection,
configuration, and data streaming management.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import (
    APIRouter,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from pydantic import BaseModel, Field

from ..devices import (
    DeviceManager,
    DeviceRegistry,
    HealthMonitor,
    DeviceInfo,
    DataSample,
    LSLIntegration,
    LSLIntegrationConfig,
)

logger = logging.getLogger(__name__)

# Initialize device manager and related services
device_manager = None
device_registry = None
health_monitor = None
lsl_integration = None


class DeviceResponse(BaseModel):
    """Device information response model."""

    device_id: str
    device_type: str
    model: str
    firmware_version: str
    serial_number: Optional[str] = None
    channel_count: int
    sampling_rate: float
    supported_sampling_rates: List[float]
    capabilities: List[str]
    connection_type: str
    status: str
    is_connected: bool = False
    is_streaming: bool = False
    last_seen: Optional[datetime] = None
    signal_quality: Optional[str] = None
    data_rate_hz: Optional[float] = None
    impedance_values: Optional[Dict[str, float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DeviceConfigRequest(BaseModel):
    """Device configuration request model."""

    sampling_rate: Optional[float] = None
    channels: Optional[List[bool]] = None
    test_signal: Optional[bool] = None
    enable_filtering: Optional[bool] = None
    buffer_size: Optional[int] = None
    serial_config: Optional[Dict[str, Any]] = None
    connection_params: Optional[Dict[str, Any]] = None


class StreamDataRequest(BaseModel):
    """Stream data request model."""

    device_id: str
    enable_streaming: bool
    data_format: str = "json"
    include_metadata: bool = True
    buffer_size: Optional[int] = None


class ConnectionRequest(BaseModel):
    """Device connection request model."""

    device_id: str
    connection_params: Optional[Dict[str, Any]] = None
    timeout_seconds: float = 30.0


class DiscoveryRequest(BaseModel):
    """Device discovery request model."""

    methods: Optional[List[str]] = None
    timeout_seconds: float = 5.0
    include_synthetic: bool = True


class HealthCheckResponse(BaseModel):
    """Health check response model."""

    device_count: int
    connected_devices: int
    streaming_devices: int
    total_data_rate: float
    system_status: str
    alerts: List[Dict[str, Any]]
    uptime_seconds: float


class LSLStreamResponse(BaseModel):
    """LSL stream response model."""

    stream_name: str
    stream_type: str
    channel_count: int
    sampling_rate: float
    source_id: str
    is_active: bool
    data_rate_hz: float


# Initialize router
router = APIRouter(prefix="/devices", tags=["devices"])


@router.on_event("startup")
async def startup_device_services():
    """Initialize device management services on API startup."""
    global device_manager, device_registry, health_monitor, lsl_integration

    try:
        # Initialize registry
        device_registry = DeviceRegistry()
        await device_registry.initialize()

        # Initialize health monitor
        health_monitor = HealthMonitor()
        await health_monitor.start()

        # Initialize LSL integration
        lsl_config = LSLIntegrationConfig()
        lsl_integration = LSLIntegration(lsl_config)
        await lsl_integration.start()

        # Initialize device manager
        device_manager = DeviceManager(
            registry=device_registry, health_monitor=health_monitor
        )
        await device_manager.start()

        logger.info("Device management services initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize device services: {str(e)}")
        raise


@router.on_event("shutdown")
async def shutdown_device_services():
    """Cleanup device management services on API shutdown."""
    global device_manager, device_registry, health_monitor, lsl_integration

    try:
        if device_manager:
            await device_manager.stop()
        if health_monitor:
            await health_monitor.stop()
        if lsl_integration:
            await lsl_integration.stop()
        if device_registry:
            await device_registry.cleanup()

        logger.info("Device management services shutdown complete")

    except Exception as e:
        logger.error(f"Error during device services shutdown: {str(e)}")


def _device_info_to_response(device_info: DeviceInfo) -> DeviceResponse:
    """Convert DeviceInfo to API response model."""
    return DeviceResponse(
        device_id=device_info.device_id,
        device_type=device_info.device_type.value,
        model=device_info.model,
        firmware_version=device_info.firmware_version,
        serial_number=device_info.serial_number,
        channel_count=device_info.channel_count,
        sampling_rate=device_info.sampling_rate,
        supported_sampling_rates=device_info.supported_sampling_rates,
        capabilities=device_info.capabilities,
        connection_type=device_info.connection_type.value,
        status=device_info.status.value,
        is_connected=device_info.is_connected,
        is_streaming=device_info.is_streaming,
        last_seen=device_info.last_seen,
        signal_quality=(
            device_info.signal_quality.value if device_info.signal_quality else None
        ),
        data_rate_hz=device_info.data_rate_hz,
        impedance_values=device_info.impedance_values,
        metadata=device_info.metadata,
    )


@router.get("/", response_model=List[DeviceResponse])
async def list_devices(
    status: Optional[str] = None,
    device_type: Optional[str] = None,
    connected_only: bool = False,
):
    """List all registered devices with optional filtering."""
    if not device_registry:
        raise HTTPException(status_code=503, detail="Device registry not available")

    try:
        # Get all devices
        all_devices = await device_registry.get_all_devices()

        # Apply filters
        filtered_devices = []
        for device_info in all_devices:
            # Status filter
            if status and device_info.status.value != status:
                continue

            # Device type filter
            if device_type and device_info.device_type.value != device_type:
                continue

            # Connected only filter
            if connected_only and not device_info.is_connected:
                continue

            filtered_devices.append(device_info)

        # Convert to response models
        response_devices = [
            _device_info_to_response(device) for device in filtered_devices
        ]

        return response_devices

    except Exception as e:
        logger.error(f"Error listing devices: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list devices: {str(e)}")


@router.post("/discover", response_model=List[DeviceResponse])
async def discover_devices(request: DiscoveryRequest):
    """Discover available devices using specified methods."""
    if not device_manager:
        raise HTTPException(status_code=503, detail="Device manager not available")

    try:
        # Map string methods to enum values if provided
        discovery_methods = None
        if request.methods:
            from ..devices.device_manager import DiscoveryMethod

            method_map = {
                "serial": DiscoveryMethod.SERIAL,
                "lsl": DiscoveryMethod.LSL,
                "brainflow": DiscoveryMethod.BRAINFLOW,
                "synthetic": DiscoveryMethod.SYNTHETIC,
                "openbci": DiscoveryMethod.OPENBCI,
            }
            discovery_methods = [
                method_map.get(m) for m in request.methods if m in method_map
            ]

        # Perform discovery
        discovered_devices = await device_manager.discover_devices(
            methods=discovery_methods
        )

        # Convert to response models
        response_devices = [
            _device_info_to_response(device) for device in discovered_devices
        ]

        return response_devices

    except Exception as e:
        logger.error(f"Error during device discovery: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Device discovery failed: {str(e)}"
        )


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: str):
    """Get detailed information about a specific device."""
    if not device_registry:
        raise HTTPException(status_code=503, detail="Device registry not available")

    try:
        device_info = await device_registry.get_device(device_id)
        if not device_info:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")

        return _device_info_to_response(device_info)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting device {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get device: {str(e)}")


@router.post("/{device_id}/connect")
async def connect_device(device_id: str, request: ConnectionRequest):
    """Connect to a specific device."""
    if not device_manager:
        raise HTTPException(status_code=503, detail="Device manager not available")

    try:
        # Get device info
        device_info = await device_registry.get_device(device_id)
        if not device_info:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")

        # Update connection parameters if provided
        if request.connection_params:
            device_info.connection_params.update(request.connection_params)

        # Attempt connection
        success = await device_manager.connect_device(device_id)

        if success:
            return {"status": "connected", "device_id": device_id}
        else:
            raise HTTPException(
                status_code=400, detail=f"Failed to connect to device {device_id}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error connecting to device {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Connection failed: {str(e)}")


@router.post("/{device_id}/disconnect")
async def disconnect_device(device_id: str):
    """Disconnect from a specific device."""
    if not device_manager:
        raise HTTPException(status_code=503, detail="Device manager not available")

    try:
        success = await device_manager.disconnect_device(device_id)

        if success:
            return {"status": "disconnected", "device_id": device_id}
        else:
            raise HTTPException(
                status_code=400, detail=f"Failed to disconnect from device {device_id}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disconnecting from device {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Disconnection failed: {str(e)}")


@router.post("/{device_id}/configure")
async def configure_device(device_id: str, config: DeviceConfigRequest):
    """Configure device parameters."""
    if not device_manager:
        raise HTTPException(status_code=503, detail="Device manager not available")

    try:
        # Convert request to configuration dict
        config_dict = {}
        if config.sampling_rate is not None:
            config_dict["sampling_rate"] = config.sampling_rate
        if config.channels is not None:
            config_dict["channels"] = config.channels
        if config.test_signal is not None:
            config_dict["test_signal"] = config.test_signal
        if config.enable_filtering is not None:
            config_dict["enable_filtering"] = config.enable_filtering
        if config.buffer_size is not None:
            config_dict["buffer_size"] = config.buffer_size
        if config.serial_config is not None:
            config_dict["serial_config"] = config.serial_config
        if config.connection_params is not None:
            config_dict["connection_params"] = config.connection_params

        # Apply configuration
        device = device_manager.get_device(device_id)
        if not device:
            raise HTTPException(
                status_code=404, detail=f"Device {device_id} not found or not connected"
            )

        success = await device.configure(config_dict)

        if success:
            return {
                "status": "configured",
                "device_id": device_id,
                "config": config_dict,
            }
        else:
            raise HTTPException(
                status_code=400, detail=f"Failed to configure device {device_id}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error configuring device {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Configuration failed: {str(e)}")


@router.post("/{device_id}/stream / start")
async def start_streaming(device_id: str):
    """Start data streaming from a device."""
    if not device_manager:
        raise HTTPException(status_code=503, detail="Device manager not available")

    try:
        success = await device_manager.start_streaming(device_id)

        if success:
            return {"status": "streaming", "device_id": device_id}
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to start streaming from device {device_id}",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting stream for device {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Stream start failed: {str(e)}")


@router.post("/{device_id}/stream / stop")
async def stop_streaming(device_id: str):
    """Stop data streaming from a device."""
    if not device_manager:
        raise HTTPException(status_code=503, detail="Device manager not available")

    try:
        success = await device_manager.stop_streaming(device_id)

        if success:
            return {"status": "stopped", "device_id": device_id}
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to stop streaming from device {device_id}",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping stream for device {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Stream stop failed: {str(e)}")


@router.get("/{device_id}/impedance")
async def get_device_impedance(device_id: str):
    """Get electrode impedance values for a device."""
    if not device_manager:
        raise HTTPException(status_code=503, detail="Device manager not available")

    try:
        device = device_manager.get_device(device_id)
        if not device:
            raise HTTPException(
                status_code=404, detail=f"Device {device_id} not found or not connected"
            )

        impedance_values = await device.get_impedance()

        return {
            "device_id": device_id,
            "impedance_values": impedance_values,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting impedance for device {device_id}: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Impedance measurement failed: {str(e)}"
        )


@router.post("/{device_id}/test")
async def perform_device_test(device_id: str):
    """Perform self-test on a device."""
    if not device_manager:
        raise HTTPException(status_code=503, detail="Device manager not available")

    try:
        device = device_manager.get_device(device_id)
        if not device:
            raise HTTPException(
                status_code=404, detail=f"Device {device_id} not found or not connected"
            )

        test_results = await device.perform_self_test()

        return {"device_id": device_id, "test_results": test_results}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing device {device_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Device test failed: {str(e)}")


@router.get("/health / status", response_model=HealthCheckResponse)
async def get_health_status():
    """Get overall system health status."""
    if not health_monitor or not device_manager:
        raise HTTPException(status_code=503, detail="Health monitoring not available")

    try:
        # Get device counts
        all_devices = await device_registry.get_all_devices() if device_registry else []
        connected_devices = [d for d in all_devices if d.is_connected]
        streaming_devices = [d for d in all_devices if d.is_streaming]

        # Calculate total data rate
        total_data_rate = sum(d.data_rate_hz or 0 for d in streaming_devices)

        # Get health status
        health_status = await health_monitor.get_health_status()

        # Get alerts
        alerts = await health_monitor.get_active_alerts()

        return HealthCheckResponse(
            device_count=len(all_devices),
            connected_devices=len(connected_devices),
            streaming_devices=len(streaming_devices),
            total_data_rate=total_data_rate,
            system_status=health_status.get("status", "unknown"),
            alerts=[alert.to_dict() for alert in alerts],
            uptime_seconds=health_status.get("uptime_seconds", 0),
        )

    except Exception as e:
        logger.error(f"Error getting health status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/lsl / streams", response_model=List[LSLStreamResponse])
async def list_lsl_streams():
    """List available LSL streams."""
    if not lsl_integration:
        raise HTTPException(status_code=503, detail="LSL integration not available")

    try:
        streams = await lsl_integration.discover_streams()

        response_streams = []
        for stream in streams:
            response_streams.append(
                LSLStreamResponse(
                    stream_name=stream.name,
                    stream_type=stream.stream_type.value,
                    channel_count=stream.channel_count,
                    sampling_rate=stream.sampling_rate,
                    source_id=stream.source_id,
                    is_active=stream.is_active,
                    data_rate_hz=stream.data_rate_hz,
                )
            )

        return response_streams

    except Exception as e:
        logger.error(f"Error listing LSL streams: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"LSL stream listing failed: {str(e)}"
        )


@router.post("/lsl / streams/{stream_name}/connect")
async def connect_lsl_stream(stream_name: str, buffer_size: int = 1000):
    """Connect to an LSL stream as inlet."""
    if not lsl_integration:
        raise HTTPException(status_code=503, detail="LSL integration not available")

    try:
        success = await lsl_integration.create_inlet(stream_name, buffer_size)

        if success:
            return {"status": "connected", "stream_name": stream_name}
        else:
            raise HTTPException(
                status_code=400, detail=f"Failed to connect to LSL stream {stream_name}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error connecting to LSL stream {stream_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"LSL connection failed: {str(e)}")


@router.websocket("/{device_id}/stream")
async def device_stream_websocket(websocket: WebSocket, device_id: str):
    """WebSocket endpoint for real-time device data streaming."""
    await websocket.accept()

    if not device_manager:
        await websocket.close(code=1003, reason="Device manager not available")
        return

    device = device_manager.get_device(device_id)
    if not device:
        await websocket.close(code=1003, reason=f"Device {device_id} not found")
        return

    # Data callback for streaming
    async def data_callback(data_sample: DataSample):
        try:
            data_dict = {
                "timestamp": data_sample.timestamp,
                "channel_data": data_sample.channel_data.tolist(),
                "sample_number": data_sample.sample_number,
                "device_id": data_sample.device_id,
                "sampling_rate": data_sample.sampling_rate,
                "signal_quality": data_sample.signal_quality,
                "metadata": data_sample.metadata,
            }
            await websocket.send_json(data_dict)
        except Exception as e:
            logger.error(f"Error sending WebSocket data: {str(e)}")

    # Add callback to device
    device.add_data_callback(data_callback)

    try:
        while True:
            # Keep connection alive and handle client messages
            try:
                message = await websocket.receive_text()
                # Handle control messages if needed
                if message == "ping":
                    await websocket.send_text("pong")
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {str(e)}")
                break

    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}")
    finally:
        # Remove callback
        try:
            device.remove_data_callback(data_callback)
        except Exception:
            pass


@router.get("/stats")
async def get_device_statistics():
    """Get device management statistics."""
    if not device_manager:
        raise HTTPException(status_code=503, detail="Device manager not available")

    try:
        stats = await device_manager.get_statistics()

        # Add health monitor stats
        if health_monitor:
            health_stats = await health_monitor.get_statistics()
            stats.update({"health": health_stats})

        # Add LSL stats
        if lsl_integration:
            lsl_stats = await lsl_integration.get_statistics()
            stats.update({"lsl": lsl_stats})

        return stats

    except Exception as e:
        logger.error(f"Error getting device statistics: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Statistics retrieval failed: {str(e)}"
        )
