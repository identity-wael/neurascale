"""Base interface for neural data acquisition devices."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Callable, Any, Tuple
import numpy as np
from datetime import datetime
import asyncio
import logging

from ...ingestion.data_types import (
    NeuralDataPacket,
    DeviceInfo,
    ChannelInfo,
    NeuralSignalType,
    DataSource,
)

logger = logging.getLogger(__name__)


class DeviceState(Enum):
    """Device connection states."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    STREAMING = "streaming"
    ERROR = "error"


@dataclass
class DeviceCapabilities:
    """Capabilities of a neural data acquisition device."""

    supported_sampling_rates: List[float]
    max_channels: int
    signal_types: List[NeuralSignalType]
    has_impedance_check: bool = False
    has_battery_monitor: bool = False
    has_wireless: bool = False
    has_trigger_input: bool = False
    has_aux_channels: bool = False
    supported_gains: Optional[List[float]] = None
    supported_filters: Optional[Dict[str, Any]] = None


class BaseDevice(ABC):
    """Abstract base class for neural data acquisition devices."""

    def __init__(self, device_id: str, device_name: str):
        """
        Initialize base device.

        Args:
            device_id: Unique identifier for the device
            device_name: Human - readable device name
        """
        self.device_id = device_id
        self.device_name = device_name
        self.state = DeviceState.DISCONNECTED
        self.device_info: Optional[DeviceInfo] = None
        self.session_id: Optional[str] = None
        self._data_callback: Optional[Callable[[NeuralDataPacket], None]] = None
        self._state_callback: Optional[Callable[[DeviceState], None]] = None
        self._error_callback: Optional[Callable[[Exception], None]] = None
        self._streaming_task: Optional[asyncio.Task] = None
        self._stop_streaming = asyncio.Event()

    @abstractmethod
    async def connect(self, **kwargs: Any) -> bool:
        """
        Connect to the device.

        Args:
            **kwargs: Device - specific connection parameters

        Returns:
            True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the device."""
        pass

    @abstractmethod
    async def start_streaming(self) -> None:
        """Start streaming data from the device."""
        pass

    @abstractmethod
    async def stop_streaming(self) -> None:
        """Stop streaming data from the device."""
        pass

    @abstractmethod
    def get_capabilities(self) -> DeviceCapabilities:
        """Get device capabilities."""
        pass

    @abstractmethod
    def configure_channels(self, channels: List[ChannelInfo]) -> bool:
        """
        Configure device channels.

        Args:
            channels: List of channel configurations

        Returns:
            True if configuration successful
        """
        pass

    @abstractmethod
    def set_sampling_rate(self, rate: float) -> bool:
        """
        Set device sampling rate.

        Args:
            rate: Sampling rate in Hz

        Returns:
            True if rate was set successfully
        """
        pass

    def set_data_callback(self, callback: Callable[[NeuralDataPacket], None]) -> None:
        """Set callback for data packets."""
        self._data_callback = callback

    def set_state_callback(self, callback: Callable[[DeviceState], None]) -> None:
        """Set callback for state changes."""
        self._state_callback = callback

    def set_error_callback(self, callback: Callable[[Exception], None]) -> None:
        """Set callback for errors."""
        self._error_callback = callback

    def set_session_id(self, session_id: str) -> None:
        """Set the current session ID."""
        self.session_id = session_id

    async def check_impedance(
        self, channel_ids: Optional[List[int]] = None
    ) -> Dict[int, float]:
        """
        Check impedance for specified channels.

        Args:
            channel_ids: List of channel IDs to check, or None for all channels

        Returns:
            Dictionary mapping channel ID to impedance in ohms
        """
        capabilities = self.get_capabilities()
        if not capabilities.has_impedance_check:
            raise NotImplementedError(
                f"{self.device_name} does not support impedance checking"
            )
        return {}

    async def get_battery_level(self) -> float:
        """
        Get battery level.

        Returns:
            Battery level as percentage (0 - 100)
        """
        capabilities = self.get_capabilities()
        if not capabilities.has_battery_monitor:
            raise NotImplementedError(
                f"{self.device_name} does not have battery monitoring"
            )
        return 100.0

    def _update_state(self, new_state: DeviceState) -> None:
        """Update device state and notify callback."""
        old_state = self.state
        self.state = new_state
        logger.info(f"{self.device_name} state changed: {old_state} -> {new_state}")

        if self._state_callback:
            try:
                self._state_callback(new_state)
            except Exception as e:
                logger.error(f"Error in state callback: {e}")

    def _handle_error(self, error: Exception) -> None:
        """Handle device error."""
        logger.error(f"{self.device_name} error: {error}")
        self._update_state(DeviceState.ERROR)

        if self._error_callback:
            try:
                self._error_callback(error)
            except Exception as e:
                logger.error(f"Error in error callback: {e}")

    def _create_packet(
        self,
        data: np.ndarray,
        timestamp: datetime,
        signal_type: NeuralSignalType,
        source: DataSource,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> NeuralDataPacket:
        """Create a neural data packet."""
        if self.device_info is None:
            raise ValueError("Device info not set")

        if self.session_id is None:
            raise ValueError("Session ID not set")

        packet = NeuralDataPacket(
            timestamp=timestamp,
            data=data,
            signal_type=signal_type,
            source=source,
            device_info=self.device_info,
            session_id=self.session_id,
            sampling_rate=(
                self.device_info.channels[0].sampling_rate
                if self.device_info.channels
                else 256.0
            ),
            metadata=metadata,
        )

        return packet

    async def _streaming_loop(self) -> None:
        """Override this method to implement device - specific streaming."""
        raise NotImplementedError("Subclasses must implement _streaming_loop")

    def is_connected(self) -> bool:
        """Check if device is connected."""
        return self.state in [DeviceState.CONNECTED, DeviceState.STREAMING]

    def is_streaming(self) -> bool:
        """Check if device is streaming."""
        return self.state == DeviceState.STREAMING

    async def __aenter__(self) -> "BaseDevice":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if self.is_streaming():
            await self.stop_streaming()
        if self.is_connected():
            await self.disconnect()
