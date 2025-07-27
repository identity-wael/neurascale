"""WebSocket notifications for device status changes."""

import asyncio
import logging
import json
from typing import Dict, Set, Optional, Any, List
from datetime import datetime, timezone
from dataclasses import dataclass
from enum import Enum

from fastapi import WebSocket, WebSocketDisconnect
from .interfaces.base_device import DeviceState

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Types of device notifications."""

    DEVICE_CONNECTED = "device_connected"
    DEVICE_DISCONNECTED = "device_disconnected"
    DEVICE_STATE_CHANGED = "device_state_changed"
    DEVICE_ERROR = "device_error"
    DEVICE_STREAMING_STARTED = "device_streaming_started"
    DEVICE_STREAMING_STOPPED = "device_streaming_stopped"
    IMPEDANCE_CHECK_COMPLETE = "impedance_check_complete"
    SIGNAL_QUALITY_UPDATE = "signal_quality_update"
    DEVICE_DISCOVERED = "device_discovered"
    DEVICE_REMOVED = "device_removed"
    BATTERY_UPDATE = "battery_update"
    HEALTH_ALERT = "health_alert"


@dataclass
class DeviceNotification:
    """Device notification payload."""

    notification_type: NotificationType
    device_id: str
    timestamp: datetime
    data: Dict[str, Any]
    severity: str = "info"  # info, warning, error, critical

    def to_json(self) -> str:
        """Convert notification to JSON string."""
        payload = {
            "type": self.notification_type.value,
            "device_id": self.device_id,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "severity": self.severity,
        }
        return json.dumps(payload)


class DeviceNotificationService:
    """Service for managing device notifications via WebSocket."""

    def __init__(self):
        """Initialize notification service."""
        self._connections: Set[WebSocket] = set()
        self._connection_info: Dict[WebSocket, Dict[str, Any]] = {}
        self._notification_queue: Optional[asyncio.Queue] = None
        self._broadcast_task: Optional[asyncio.Task] = None
        self._is_running = False

    async def start(self):
        """Start the notification service."""
        if self._is_running:
            return

        self._is_running = True
        self._notification_queue = asyncio.Queue()
        self._broadcast_task = asyncio.create_task(self._broadcast_loop())
        logger.info("Device notification service started")

    async def stop(self):
        """Stop the notification service."""
        self._is_running = False

        if self._broadcast_task and not self._broadcast_task.done():
            self._broadcast_task.cancel()
            try:
                await self._broadcast_task
            except asyncio.CancelledError:
                pass
            except RuntimeError:
                # Task might have already finished
                pass

        # Clear the queue if it exists
        if self._notification_queue:
            while not self._notification_queue.empty():
                try:
                    self._notification_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break

        # Close all connections
        for websocket in list(self._connections):
            await self.disconnect(websocket)

        logger.info("Device notification service stopped")

    async def connect(
        self, websocket: WebSocket, client_info: Optional[Dict[str, Any]] = None
    ):
        """Add a new WebSocket connection."""
        await websocket.accept()
        self._connections.add(websocket)
        self._connection_info[websocket] = client_info or {}

        logger.info(
            f"WebSocket client connected. Total connections: {len(self._connections)}"
        )

        # Send welcome message
        welcome = {
            "type": "connected",
            "message": "Connected to device notification service",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await websocket.send_json(welcome)

    async def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self._connections:
            self._connections.remove(websocket)
            self._connection_info.pop(websocket, None)

            try:
                await websocket.close()
            except Exception:
                pass

            logger.info(
                f"WebSocket client disconnected. Total connections: {len(self._connections)}"
            )

    async def notify_device_state_change(
        self, device_id: str, old_state: DeviceState, new_state: DeviceState
    ):
        """Notify about device state change."""
        notification = DeviceNotification(
            notification_type=NotificationType.DEVICE_STATE_CHANGED,
            device_id=device_id,
            timestamp=datetime.now(timezone.utc),
            data={"old_state": old_state.value, "new_state": new_state.value},
            severity="info",
        )

        # Special handling for specific state transitions
        if new_state == DeviceState.CONNECTED:
            notification.notification_type = NotificationType.DEVICE_CONNECTED
        elif new_state == DeviceState.DISCONNECTED:
            notification.notification_type = NotificationType.DEVICE_DISCONNECTED
        elif new_state == DeviceState.STREAMING:
            notification.notification_type = NotificationType.DEVICE_STREAMING_STARTED
        elif old_state == DeviceState.STREAMING and new_state != DeviceState.STREAMING:
            notification.notification_type = NotificationType.DEVICE_STREAMING_STOPPED
        elif new_state == DeviceState.ERROR:
            notification.severity = "error"

        await self._queue_notification(notification)

    async def notify_device_error(
        self,
        device_id: str,
        error: Exception,
        error_details: Optional[Dict[str, Any]] = None,
    ):
        """Notify about device error."""
        notification = DeviceNotification(
            notification_type=NotificationType.DEVICE_ERROR,
            device_id=device_id,
            timestamp=datetime.now(timezone.utc),
            data={
                "error_type": type(error).__name__,
                "error_message": str(error),
                "details": error_details or {},
            },
            severity="error",
        )

        await self._queue_notification(notification)

    async def notify_impedance_check_complete(
        self,
        device_id: str,
        impedance_results: Dict[int, float],
        quality_summary: Optional[Dict[str, Any]] = None,
    ):
        """Notify about impedance check completion."""
        notification = DeviceNotification(
            notification_type=NotificationType.IMPEDANCE_CHECK_COMPLETE,
            device_id=device_id,
            timestamp=datetime.now(timezone.utc),
            data={
                "impedance_values": impedance_results,
                "quality_summary": quality_summary or {},
                "channels_checked": len(impedance_results),
            },
            severity="info",
        )

        await self._queue_notification(notification)

    async def notify_signal_quality_update(
        self, device_id: str, channel_id: int, quality_metrics: Dict[str, Any]
    ):
        """Notify about signal quality update."""
        severity = "info"
        quality_level = quality_metrics.get("quality_level", "unknown")

        if quality_level in ["poor", "bad"]:
            severity = "warning"

        notification = DeviceNotification(
            notification_type=NotificationType.SIGNAL_QUALITY_UPDATE,
            device_id=device_id,
            timestamp=datetime.now(timezone.utc),
            data={"channel_id": channel_id, "metrics": quality_metrics},
            severity=severity,
        )

        await self._queue_notification(notification)

    async def notify_device_discovered(self, device_info: Dict[str, Any]):
        """Notify about device discovery."""
        notification = DeviceNotification(
            notification_type=NotificationType.DEVICE_DISCOVERED,
            device_id=device_info.get("device_id", "unknown"),
            timestamp=datetime.now(timezone.utc),
            data=device_info,
            severity="info",
        )

        await self._queue_notification(notification)

    async def notify_health_alert(self, device_id: str, alert_data: Dict[str, Any]):
        """Notify about device health alert."""
        severity_map = {"critical": "critical", "warning": "warning", "info": "info"}

        notification = DeviceNotification(
            notification_type=NotificationType.HEALTH_ALERT,
            device_id=device_id,
            timestamp=datetime.now(timezone.utc),
            data=alert_data,
            severity=severity_map.get(alert_data.get("severity", "info"), "info"),
        )

        await self._queue_notification(notification)

    async def notify_battery_update(
        self, device_id: str, battery_level: float, is_charging: bool = False
    ):
        """Notify about battery level update."""
        severity = "info"
        if battery_level < 10:
            severity = "critical"
        elif battery_level < 20:
            severity = "warning"

        notification = DeviceNotification(
            notification_type=NotificationType.BATTERY_UPDATE,
            device_id=device_id,
            timestamp=datetime.now(timezone.utc),
            data={"battery_level": battery_level, "is_charging": is_charging},
            severity=severity,
        )

        await self._queue_notification(notification)

    async def _queue_notification(self, notification: DeviceNotification):
        """Queue a notification for broadcast."""
        if not self._notification_queue:
            logger.warning("Notification service not started, dropping notification")
            return
        try:
            await self._notification_queue.put(notification)
        except Exception as e:
            logger.error(f"Error queuing notification: {e}")

    async def _broadcast_loop(self):
        """Main loop for broadcasting notifications."""
        while self._is_running:
            try:
                if not self._notification_queue:
                    await asyncio.sleep(0.1)
                    continue

                # Wait for notification with timeout
                try:
                    notification = await asyncio.wait_for(
                        self._notification_queue.get(), timeout=1.0
                    )
                    # Broadcast to all connected clients
                    await self._broadcast_notification(notification)
                except asyncio.TimeoutError:
                    # Timeout is normal, just continue
                    continue
                except asyncio.CancelledError:
                    # Task is being cancelled, break the loop
                    break

            except Exception as e:
                logger.error(f"Error in broadcast loop: {e}")
                # Small delay to prevent tight loop on persistent errors
                try:
                    await asyncio.sleep(0.1)
                except RuntimeError:
                    # Event loop might be closing
                    break

    async def _broadcast_notification(self, notification: DeviceNotification):
        """Broadcast notification to all connected clients."""
        if not self._connections:
            return

        # Prepare notification payload
        payload = notification.to_json()

        # Send to all connections
        disconnected = []

        for websocket in self._connections:
            try:
                await websocket.send_text(payload)
            except WebSocketDisconnect:
                disconnected.append(websocket)
            except Exception as e:
                logger.error(f"Error sending notification to client: {e}")
                disconnected.append(websocket)

        # Clean up disconnected clients
        for websocket in disconnected:
            await self.disconnect(websocket)

    async def handle_client_message(
        self, websocket: WebSocket, message: Dict[str, Any]
    ):
        """Handle incoming message from client."""
        msg_type = message.get("type")

        if msg_type == "ping":
            # Respond to ping
            await websocket.send_json(
                {"type": "pong", "timestamp": datetime.now(timezone.utc).isoformat()}
            )
        elif msg_type == "subscribe":
            # Handle subscription to specific device or notification types
            device_id = message.get("device_id")
            notification_types = message.get("notification_types", [])

            if websocket in self._connection_info:
                self._connection_info[websocket]["subscriptions"] = {
                    "device_id": device_id,
                    "notification_types": notification_types,
                }

                await websocket.send_json(
                    {
                        "type": "subscription_confirmed",
                        "device_id": device_id,
                        "notification_types": notification_types,
                    }
                )
        else:
            logger.warning(f"Unknown message type: {msg_type}")

    def get_connection_count(self) -> int:
        """Get number of active connections."""
        return len(self._connections)

    def get_connection_info(self) -> List[Dict[str, Any]]:
        """Get information about active connections."""
        info = []
        for ws, data in self._connection_info.items():
            info.append({"client_info": data, "connected": True})
        return info
