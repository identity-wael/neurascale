"""Device Registry for managing BCI device metadata and state.

This module provides persistent storage and retrieval of device information
using Redis as the backend storage system.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set

import uuid

try:
    import redis.asyncio as redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Redis not available, falling back to in-memory storage")

from .base import DeviceInfo, DeviceType, DeviceStatus, ConnectionType, SignalQuality

logger = logging.getLogger(__name__)


class DeviceRegistry:
    """Registry for managing BCI device metadata and state."""

    def __init__(
        self, redis_url: str = "redis://localhost:6379 / 0", use_redis: bool = True
    ):
        """Initialize DeviceRegistry.

        Args:
            redis_url: Redis connection URL
            use_redis: Whether to use Redis (falls back to memory if False)
        """
        self.redis_url = redis_url
        self.use_redis = use_redis and REDIS_AVAILABLE

        # Redis connection
        self.redis_client: Optional[redis.Redis] = None

        # Fallback in-memory storage
        self.memory_storage: Dict[str, Dict[str, Any]] = {}

        # Key prefixes for Redis
        self.device_prefix = "neurascale:device:"
        self.device_list_key = "neurascale:devices"
        self.device_types_key = "neurascale:device_types"

        logger.info(f"DeviceRegistry initialized (Redis: {self.use_redis})")

    async def connect(self) -> bool:
        """Connect to Redis backend.

        Returns:
            True if connection successful
        """
        if not self.use_redis:
            logger.info("Using in-memory storage (Redis disabled)")
            return True

        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )

            # Test connection
            await self.redis_client.ping()
            logger.info("Connected to Redis successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            logger.info("Falling back to in-memory storage")
            self.use_redis = False
            return False

    async def disconnect(self) -> None:
        """Disconnect from Redis backend."""
        if self.redis_client:
            await self.redis_client.aclose()
            self.redis_client = None
            logger.info("Disconnected from Redis")

    async def register_device(self, device_info: DeviceInfo) -> str:
        """Register a new device or update existing device.

        Args:
            device_info: Device information

        Returns:
            Device ID
        """
        if not device_info.device_id:
            device_info.device_id = str(uuid.uuid4())

        device_id = device_info.device_id
        device_data = self._serialize_device_info(device_info)

        try:
            if self.use_redis and self.redis_client:
                # Store device data
                device_key = f"{self.device_prefix}{device_id}"
                await self.redis_client.hset(device_key, mapping=device_data)

                # Add to device list
                await self.redis_client.sadd(self.device_list_key, device_id)

                # Add to device type index
                type_key = f"{self.device_types_key}:{device_info.device_type.value}"
                await self.redis_client.sadd(type_key, device_id)

                # Set expiration for device data (24 hours default)
                await self.redis_client.expire(device_key, 86400)

            else:
                # Use in-memory storage
                self.memory_storage[device_id] = device_data

            logger.info(
                f"Registered device: {device_id} ({device_info.device_type.value})"
            )
            return device_id

        except Exception as e:
            logger.error(f"Error registering device {device_id}: {str(e)}")
            raise

    async def get_device(self, device_id: str) -> Optional[DeviceInfo]:
        """Get device information by ID.

        Args:
            device_id: Device identifier

        Returns:
            Device information or None if not found
        """
        try:
            if self.use_redis and self.redis_client:
                device_key = f"{self.device_prefix}{device_id}"
                device_data = await self.redis_client.hgetall(device_key)

                if not device_data:
                    return None

            else:
                device_data = self.memory_storage.get(device_id)
                if not device_data:
                    return None

            return self._deserialize_device_info(device_data)

        except Exception as e:
            logger.error(f"Error getting device {device_id}: {str(e)}")
            return None

    async def update_device(self, device_info: DeviceInfo) -> bool:
        """Update device information.

        Args:
            device_info: Updated device information

        Returns:
            True if update successful
        """
        return await self.register_device(device_info) is not None

    async def update_device_status(self, device_id: str, status: DeviceStatus) -> bool:
        """Update device status.

        Args:
            device_id: Device identifier
            status: New device status

        Returns:
            True if update successful
        """
        try:
            if self.use_redis and self.redis_client:
                device_key = f"{self.device_prefix}{device_id}"
                await self.redis_client.hset(device_key, "status", status.value)
                await self.redis_client.hset(
                    device_key, "last_seen", datetime.utcnow().isoformat()
                )

            else:
                if device_id in self.memory_storage:
                    self.memory_storage[device_id]["status"] = status.value
                    self.memory_storage[device_id][
                        "last_seen"
                    ] = datetime.utcnow().isoformat()
                else:
                    return False

            logger.debug(f"Updated device {device_id} status to {status.value}")
            return True

        except Exception as e:
            logger.error(f"Error updating device status {device_id}: {str(e)}")
            return False

    async def remove_device(self, device_id: str) -> bool:
        """Remove device from registry.

        Args:
            device_id: Device identifier

        Returns:
            True if removal successful
        """
        try:
            if self.use_redis and self.redis_client:
                # Get device info for cleanup
                device_info = await self.get_device(device_id)

                # Remove device data
                device_key = f"{self.device_prefix}{device_id}"
                await self.redis_client.delete(device_key)

                # Remove from device list
                await self.redis_client.srem(self.device_list_key, device_id)

                # Remove from device type index
                if device_info:
                    type_key = (
                        f"{self.device_types_key}:{device_info.device_type.value}"
                    )
                    await self.redis_client.srem(type_key, device_id)

            else:
                if device_id in self.memory_storage:
                    del self.memory_storage[device_id]
                else:
                    return False

            logger.info(f"Removed device: {device_id}")
            return True

        except Exception as e:
            logger.error(f"Error removing device {device_id}: {str(e)}")
            return False

    async def get_all_devices(self) -> List[DeviceInfo]:
        """Get all registered devices.

        Returns:
            List of all device information
        """
        try:
            devices = []

            if self.use_redis and self.redis_client:
                device_ids = await self.redis_client.smembers(self.device_list_key)

                for device_id in device_ids:
                    device_info = await self.get_device(device_id)
                    if device_info:
                        devices.append(device_info)

            else:
                for device_id, device_data in self.memory_storage.items():
                    device_info = self._deserialize_device_info(device_data)
                    if device_info:
                        devices.append(device_info)

            return devices

        except Exception as e:
            logger.error(f"Error getting all devices: {str(e)}")
            return []

    async def get_devices_by_type(self, device_type: DeviceType) -> List[DeviceInfo]:
        """Get devices by type.

        Args:
            device_type: Device type to filter by

        Returns:
            List of devices of the specified type
        """
        try:
            devices = []

            if self.use_redis and self.redis_client:
                type_key = f"{self.device_types_key}:{device_type.value}"
                device_ids = await self.redis_client.smembers(type_key)

                for device_id in device_ids:
                    device_info = await self.get_device(device_id)
                    if device_info:
                        devices.append(device_info)

            else:
                for device_id, device_data in self.memory_storage.items():
                    if device_data.get("device_type") == device_type.value:
                        device_info = self._deserialize_device_info(device_data)
                        if device_info:
                            devices.append(device_info)

            return devices

        except Exception as e:
            logger.error(f"Error getting devices by type {device_type.value}: {str(e)}")
            return []

    async def get_devices_by_status(self, status: DeviceStatus) -> List[DeviceInfo]:
        """Get devices by status.

        Args:
            status: Device status to filter by

        Returns:
            List of devices with the specified status
        """
        all_devices = await self.get_all_devices()
        return [device for device in all_devices if device.status == status]

    async def get_connected_devices(self) -> List[DeviceInfo]:
        """Get all connected devices.

        Returns:
            List of connected devices
        """
        return await self.get_devices_by_status(DeviceStatus.CONNECTED)

    async def get_streaming_devices(self) -> List[DeviceInfo]:
        """Get all streaming devices.

        Returns:
            List of streaming devices
        """
        return await self.get_devices_by_status(DeviceStatus.STREAMING)

    async def cleanup_stale_devices(self, max_age_hours: int = 24) -> int:
        """Remove devices that haven't been seen for a specified time.

        Args:
            max_age_hours: Maximum age in hours before device is considered stale

        Returns:
            Number of devices removed
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            all_devices = await self.get_all_devices()
            removed_count = 0

            for device in all_devices:
                if device.last_seen < cutoff_time:
                    success = await self.remove_device(device.device_id)
                    if success:
                        removed_count += 1

            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} stale devices")

            return removed_count

        except Exception as e:
            logger.error(f"Error cleaning up stale devices: {str(e)}")
            return 0

    async def get_device_count(self) -> int:
        """Get total number of registered devices.

        Returns:
            Number of registered devices
        """
        try:
            if self.use_redis and self.redis_client:
                return await self.redis_client.scard(self.device_list_key)
            else:
                return len(self.memory_storage)

        except Exception as e:
            logger.error(f"Error getting device count: {str(e)}")
            return 0

    async def get_device_types(self) -> List[DeviceType]:
        """Get list of device types currently registered.

        Returns:
            List of device types
        """
        try:
            all_devices = await self.get_all_devices()
            device_types = set()

            for device in all_devices:
                device_types.add(device.device_type)

            return list(device_types)

        except Exception as e:
            logger.error(f"Error getting device types: {str(e)}")
            return []

    async def search_devices(self, query: str) -> List[DeviceInfo]:
        """Search devices by various criteria.

        Args:
            query: Search query (matches device_id, model, serial_number)

        Returns:
            List of matching devices
        """
        try:
            all_devices = await self.get_all_devices()
            matching_devices = []

            query_lower = query.lower()

            for device in all_devices:
                # Search in device ID, model, and serial number
                if (
                    query_lower in device.device_id.lower()
                    or query_lower in device.model.lower()
                    or (
                        device.serial_number
                        and query_lower in device.serial_number.lower()
                    )
                ):
                    matching_devices.append(device)

            return matching_devices

        except Exception as e:
            logger.error(f"Error searching devices: {str(e)}")
            return []

    async def get_registry_stats(self) -> Dict[str, Any]:
        """Get registry statistics.

        Returns:
            Registry statistics
        """
        try:
            all_devices = await self.get_all_devices()

            # Count by status
            status_counts = {}
            for status in DeviceStatus:
                status_counts[status.value] = len(
                    [d for d in all_devices if d.status == status]
                )

            # Count by type
            type_counts = {}
            for device_type in DeviceType:
                type_counts[device_type.value] = len(
                    [d for d in all_devices if d.device_type == device_type]
                )

            # Count by connection type
            connection_counts = {}
            for conn_type in ConnectionType:
                connection_counts[conn_type.value] = len(
                    [d for d in all_devices if d.connection_type == conn_type]
                )

            return {
                "total_devices": len(all_devices),
                "status_counts": status_counts,
                "type_counts": type_counts,
                "connection_counts": connection_counts,
                "using_redis": self.use_redis,
                "last_updated": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting registry stats: {str(e)}")
            return {"error": str(e)}

    def _serialize_device_info(self, device_info: DeviceInfo) -> Dict[str, str]:
        """Serialize DeviceInfo to string dictionary for Redis storage.

        Args:
            device_info: Device information

        Returns:
            String dictionary
        """
        return {
            "device_id": device_info.device_id,
            "device_type": device_info.device_type.value,
            "model": device_info.model,
            "firmware_version": device_info.firmware_version,
            "serial_number": device_info.serial_number or "",
            "channel_count": str(device_info.channel_count),
            "sampling_rate": str(device_info.sampling_rate),
            "supported_sampling_rates": json.dumps(
                device_info.supported_sampling_rates
            ),
            "capabilities": json.dumps(device_info.capabilities),
            "connection_type": device_info.connection_type.value,
            "connection_params": json.dumps(device_info.connection_params),
            "status": device_info.status.value,
            "last_seen": device_info.last_seen.isoformat(),
            "uptime_seconds": str(device_info.uptime_seconds),
            "signal_quality": device_info.signal_quality.value,
            "impedance_values": json.dumps(device_info.impedance_values),
            "noise_level": str(device_info.noise_level),
            "configuration": json.dumps(device_info.configuration),
            "metadata": json.dumps(device_info.metadata),
            "latency_ms": str(device_info.latency_ms),
            "packet_loss_rate": str(device_info.packet_loss_rate),
            "data_rate_hz": str(device_info.data_rate_hz),
        }

    def _deserialize_device_info(
        self, device_data: Dict[str, str]
    ) -> Optional[DeviceInfo]:
        """Deserialize string dictionary to DeviceInfo.

        Args:
            device_data: String dictionary from storage

        Returns:
            DeviceInfo object or None if deserialization fails
        """
        try:
            return DeviceInfo(
                device_id=device_data["device_id"],
                device_type=DeviceType(device_data["device_type"]),
                model=device_data["model"],
                firmware_version=device_data["firmware_version"],
                serial_number=device_data.get("serial_number") or None,
                channel_count=int(device_data.get("channel_count", "8")),
                sampling_rate=float(device_data.get("sampling_rate", "250.0")),
                supported_sampling_rates=json.loads(
                    device_data.get("supported_sampling_rates", "[250.0]")
                ),
                capabilities=json.loads(device_data.get("capabilities", "[]")),
                connection_type=ConnectionType(
                    device_data.get("connection_type", "serial")
                ),
                connection_params=json.loads(
                    device_data.get("connection_params", "{}")
                ),
                status=DeviceStatus(device_data.get("status", "disconnected")),
                last_seen=datetime.fromisoformat(device_data["last_seen"]),
                uptime_seconds=float(device_data.get("uptime_seconds", "0.0")),
                signal_quality=SignalQuality(device_data.get("signal_quality", "poor")),
                impedance_values=json.loads(device_data.get("impedance_values", "{}")),
                noise_level=float(device_data.get("noise_level", "0.0")),
                configuration=json.loads(device_data.get("configuration", "{}")),
                metadata=json.loads(device_data.get("metadata", "{}")),
                latency_ms=float(device_data.get("latency_ms", "0.0")),
                packet_loss_rate=float(device_data.get("packet_loss_rate", "0.0")),
                data_rate_hz=float(device_data.get("data_rate_hz", "0.0")),
            )

        except Exception as e:
            logger.error(f"Error deserializing device data: {str(e)}")
            return None
