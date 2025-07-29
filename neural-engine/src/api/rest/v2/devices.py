"""Device management REST API endpoints."""

from fastapi import APIRouter, Query, Depends, HTTPException, Response
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import logging

from ...rest.middleware.auth import get_current_user, check_permission
from ...rest.utils.pagination import PaginationParams, PaginatedResponse, paginate

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models
class DeviceType(BaseModel):
    """Device type enumeration."""

    value: str = Field(..., pattern="^(EEG|EMG|ECG|fNIRS|TMS|tDCS|HYBRID)$")


class DeviceStatus(BaseModel):
    """Device status enumeration."""

    value: str = Field(..., pattern="^(ONLINE|OFFLINE|MAINTENANCE|ERROR)$")


class DeviceCalibration(BaseModel):
    """Device calibration data."""

    timestamp: datetime
    parameters: Dict[str, Any]
    valid_until: Optional[datetime] = None
    performed_by: str


class Device(BaseModel):
    """Device model."""

    id: str
    name: str
    type: DeviceType
    status: DeviceStatus
    serial_number: str
    firmware_version: str
    last_seen: datetime
    calibration: Optional[DeviceCalibration] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    _links: Optional[Dict[str, Dict[str, str]]] = None


class DeviceCreate(BaseModel):
    """Device creation model."""

    name: str = Field(..., min_length=1, max_length=100)
    type: DeviceType
    serial_number: str = Field(..., min_length=1, max_length=50)
    firmware_version: str = Field(..., min_length=1, max_length=20)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DeviceUpdate(BaseModel):
    """Device update model."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[DeviceStatus] = None
    firmware_version: Optional[str] = Field(None, min_length=1, max_length=20)
    metadata: Optional[Dict[str, Any]] = None


class DeviceBatchOperation(BaseModel):
    """Batch operation for devices."""

    operation: str = Field(..., pattern="^(update|delete|calibrate)$")
    device_ids: List[str]
    data: Optional[Dict[str, Any]] = None


# Mock data store (replace with actual database)
devices_db: Dict[str, Device] = {}


@router.get("", response_model=PaginatedResponse[Device])
async def list_devices(
    status: Optional[str] = Query(None, description="Filter by status"),
    type: Optional[str] = Query(None, description="Filter by type"),
    search: Optional[str] = Query(None, description="Search in name or serial number"),
    pagination: PaginationParams = Depends(),
    user: Dict[str, Any] = Depends(get_current_user),
) -> PaginatedResponse[Device]:
    """
    List all devices with optional filtering.

    - **status**: Filter by device status (ONLINE, OFFLINE, etc.)
    - **type**: Filter by device type (EEG, EMG, etc.)
    - **search**: Search in device name or serial number
    """
    if not await check_permission(user, "devices.read"):
        raise HTTPException(403, "Insufficient permissions")

    # Filter devices
    filtered_devices = []
    for device in devices_db.values():
        if status and device.status.value != status.upper():
            continue
        if type and device.type.value != type.upper():
            continue
        if (
            search
            and search.lower() not in device.name.lower()
            and search not in device.serial_number
        ):
            continue

        # Add HATEOAS links
        device._links = {
            "self": {"href": f"/api/v2/devices/{device.id}"},
            "sessions": {"href": f"/api/v2/sessions?device_id={device.id}"},
            "calibration": {"href": f"/api/v2/devices/{device.id}/calibration"},
            "metrics": {"href": f"/api/v2/devices/{device.id}/metrics"},
        }
        filtered_devices.append(device)

    # Apply pagination
    return paginate(filtered_devices, pagination, base_url="/api/v2/devices")


@router.post("", response_model=Device, status_code=201)
async def create_device(
    device: DeviceCreate,
    user: Dict[str, Any] = Depends(get_current_user),
) -> Device:
    """Create a new device."""
    if not await check_permission(user, "devices.create"):
        raise HTTPException(403, "Insufficient permissions")

    # Generate device ID
    device_id = f"dev_{len(devices_db) + 1:04d}"

    # Create device
    new_device = Device(
        id=device_id,
        name=device.name,
        type=device.type,
        status=DeviceStatus(value="OFFLINE"),
        serial_number=device.serial_number,
        firmware_version=device.firmware_version,
        last_seen=datetime.utcnow(),
        metadata=device.metadata,
    )

    # Add HATEOAS links
    new_device._links = {
        "self": {"href": f"/api/v2/devices/{device_id}"},
        "sessions": {"href": f"/api/v2/sessions?device_id={device_id}"},
        "calibration": {"href": f"/api/v2/devices/{device_id}/calibration"},
        "metrics": {"href": f"/api/v2/devices/{device_id}/metrics"},
    }

    # Store device
    devices_db[device_id] = new_device

    logger.info(f"Created device {device_id} by user {user.get('sub')}")

    return new_device


@router.get("/{device_id}", response_model=Device)
async def get_device(
    device_id: str,
    include_calibration: bool = Query(False, description="Include calibration data"),
    user: Dict[str, Any] = Depends(get_current_user),
) -> Device:
    """Get a specific device by ID."""
    if not await check_permission(user, "devices.read", device_id):
        raise HTTPException(403, "Insufficient permissions")

    device = devices_db.get(device_id)
    if not device:
        raise HTTPException(404, f"Device not found: {device_id}")

    # Add HATEOAS links
    device._links = {
        "self": {"href": f"/api/v2/devices/{device_id}"},
        "sessions": {"href": f"/api/v2/sessions?device_id={device_id}"},
        "calibration": {"href": f"/api/v2/devices/{device_id}/calibration"},
        "metrics": {"href": f"/api/v2/devices/{device_id}/metrics"},
    }

    # Optionally exclude calibration data
    if not include_calibration:
        device = device.copy()
        device.calibration = None

    return device


@router.patch("/{device_id}", response_model=Device)
async def update_device(
    device_id: str,
    update: DeviceUpdate,
    user: Dict[str, Any] = Depends(get_current_user),
) -> Device:
    """Update a device using PATCH."""
    if not await check_permission(user, "devices.update", device_id):
        raise HTTPException(403, "Insufficient permissions")

    device = devices_db.get(device_id)
    if not device:
        raise HTTPException(404, f"Device not found: {device_id}")

    # Apply updates
    update_data = update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(device, field, value)

    # Update last seen
    device.last_seen = datetime.utcnow()

    logger.info(f"Updated device {device_id} by user {user.get('sub')}")

    return device


@router.delete("/{device_id}", status_code=204)
async def delete_device(
    device_id: str,
    user: Dict[str, Any] = Depends(get_current_user),
) -> Response:
    """Delete a device."""
    if not await check_permission(user, "devices.delete", device_id):
        raise HTTPException(403, "Insufficient permissions")

    if device_id not in devices_db:
        raise HTTPException(404, f"Device not found: {device_id}")

    del devices_db[device_id]

    logger.info(f"Deleted device {device_id} by user {user.get('sub')}")

    return Response(status_code=204)


@router.post("/{device_id}/calibration", response_model=Device)
async def calibrate_device(
    device_id: str,
    calibration_data: Dict[str, Any],
    user: Dict[str, Any] = Depends(get_current_user),
) -> Device:
    """Calibrate a device."""
    if not await check_permission(user, "devices.calibrate", device_id):
        raise HTTPException(403, "Insufficient permissions")

    device = devices_db.get(device_id)
    if not device:
        raise HTTPException(404, f"Device not found: {device_id}")

    # Create calibration record
    device.calibration = DeviceCalibration(
        timestamp=datetime.utcnow(),
        parameters=calibration_data,
        valid_until=datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        ),
        performed_by=user.get("sub", "unknown"),
    )

    logger.info(f"Calibrated device {device_id} by user {user.get('sub')}")

    return device


@router.post("/batch", response_model=List[Dict[str, Any]])
async def batch_device_operations(
    operations: List[DeviceBatchOperation],
    user: Dict[str, Any] = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """Execute batch operations on multiple devices."""
    if not await check_permission(user, "devices.batch"):
        raise HTTPException(403, "Insufficient permissions")

    results = []

    for op in operations:
        op_results = {"operation": op.operation, "results": []}

        for device_id in op.device_ids:
            try:
                if op.operation == "update":
                    # Batch update
                    device = devices_db.get(device_id)
                    if device and op.data:
                        for key, value in op.data.items():
                            setattr(device, key, value)
                        op_results["results"].append(
                            {"device_id": device_id, "status": "success"}
                        )
                    else:
                        op_results["results"].append(
                            {"device_id": device_id, "status": "not_found"}
                        )

                elif op.operation == "delete":
                    # Batch delete
                    if device_id in devices_db:
                        del devices_db[device_id]
                        op_results["results"].append(
                            {"device_id": device_id, "status": "success"}
                        )
                    else:
                        op_results["results"].append(
                            {"device_id": device_id, "status": "not_found"}
                        )

                elif op.operation == "calibrate":
                    # Batch calibrate
                    device = devices_db.get(device_id)
                    if device:
                        device.calibration = DeviceCalibration(
                            timestamp=datetime.utcnow(),
                            parameters=op.data or {},
                            performed_by=user.get("sub", "unknown"),
                        )
                        op_results["results"].append(
                            {"device_id": device_id, "status": "success"}
                        )
                    else:
                        op_results["results"].append(
                            {"device_id": device_id, "status": "not_found"}
                        )

            except Exception as e:
                op_results["results"].append(
                    {"device_id": device_id, "status": "error", "error": str(e)}
                )

        results.append(op_results)

    return results
