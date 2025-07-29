"""Device resolver implementation."""

from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from ..schema.types import (
    Device,
    DeviceConnection,
    DeviceEdge,
    PageInfo,
    DeviceFilter,
    PaginationInput,
    DeviceType,
    DeviceStatus,
)

logger = logging.getLogger(__name__)


class DeviceResolver:
    """Resolver for device-related queries."""

    def __init__(self):
        """Initialize device resolver."""
        # In production, would inject database service
        self.devices_db = self._create_mock_devices()

    def _create_mock_devices(self) -> Dict[str, Device]:
        """Create mock devices for testing."""
        devices = {}

        for i in range(25):
            device_id = f"dev_{i + 1:03d}"
            device_types = list(DeviceType)
            device_statuses = list(DeviceStatus)

            device = Device(
                id=device_id,
                name=f"Device {i + 1}",
                type=device_types[i % len(device_types)],
                status=device_statuses[i % len(device_statuses)],
                serial_number=f"SN{i + 1:05d}",
                firmware_version=f"{(i % 3) + 1}.{(i % 5)}.{i % 10}",
                last_seen=datetime.utcnow(),
                channel_count=32 if i % 2 == 0 else 64,
                sampling_rate=256 if i % 3 == 0 else 512,
            )
            devices[device_id] = device

        return devices

    async def get_device(self, device_id: str) -> Optional[Device]:
        """Get a device by ID."""
        return self.devices_db.get(device_id)

    async def list_devices(
        self,
        filter: Optional[DeviceFilter] = None,
        pagination: Optional[PaginationInput] = None,
    ) -> DeviceConnection:
        """List devices with filtering and pagination."""
        # Apply filters
        filtered_devices = list(self.devices_db.values())

        if filter:
            if filter.type:
                filtered_devices = [
                    d for d in filtered_devices if d.type == filter.type
                ]
            if filter.status:
                filtered_devices = [
                    d for d in filtered_devices if d.status == filter.status
                ]
            if filter.search:
                search_lower = filter.search.lower()
                filtered_devices = [
                    d
                    for d in filtered_devices
                    if search_lower in d.name.lower()
                    or search_lower in d.serial_number.lower()
                ]

        # Sort by ID for consistent ordering
        filtered_devices.sort(key=lambda d: d.id)

        # Apply pagination
        total_count = len(filtered_devices)

        # Default pagination
        if not pagination:
            pagination = PaginationInput(first=10)

        # Calculate slice indices
        if pagination.first is not None:
            start_idx = 0
            if pagination.after:
                # Find the index after the cursor
                for i, device in enumerate(filtered_devices):
                    if device.id == pagination.after:
                        start_idx = i + 1
                        break

            end_idx = min(start_idx + pagination.first, total_count)
            page_devices = filtered_devices[start_idx:end_idx]

        elif pagination.last is not None:
            end_idx = total_count
            if pagination.before:
                # Find the index before the cursor
                for i, device in enumerate(filtered_devices):
                    if device.id == pagination.before:
                        end_idx = i
                        break

            start_idx = max(0, end_idx - pagination.last)
            page_devices = filtered_devices[start_idx:end_idx]
        else:
            # Default to first 10
            page_devices = filtered_devices[:10]

        # Create edges
        edges = [DeviceEdge(node=device, cursor=device.id) for device in page_devices]

        # Create page info
        has_previous = start_idx > 0 if "start_idx" in locals() else False
        has_next = (
            end_idx < total_count
            if "end_idx" in locals()
            else len(page_devices) < total_count
        )

        page_info = PageInfo(
            has_next_page=has_next,
            has_previous_page=has_previous,
            start_cursor=edges[0].cursor if edges else None,
            end_cursor=edges[-1].cursor if edges else None,
        )

        return DeviceConnection(
            edges=edges,
            page_info=page_info,
            total_count=total_count,
        )

    async def get_device_sessions(self, device_id: str, limit: int = 10) -> List[Any]:
        """Get sessions for a device."""
        # Would be implemented with actual session data
        return []

    async def get_device_calibration(self, device_id: str) -> Optional[Any]:
        """Get device calibration data."""
        # Would be implemented with actual calibration data
        return None
