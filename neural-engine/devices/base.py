"""Base device classes and interfaces for NeuraScale Neural Engine.

This module defines the abstract base classes and core data structures
for BCI device management and integration.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
import numpy as np

logger = logging.getLogger(__name__)


class DeviceType(Enum):
    """Supported BCI device types."""

    OPENBCI_CYTON = "openbci_cyton"
    OPENBCI_GANGLION = "openbci_ganglion"
    OPENBCI_WIFI = "openbci_wifi"
    BRAINFLOW_SYNTHETIC = "brainflow_synthetic"
    BRAINFLOW_CYTON = "brainflow_cyton"
    BRAINFLOW_GANGLION = "brainflow_ganglion"
    LSL_STREAM = "lsl_stream"
    SYNTHETIC = "synthetic"
    CUSTOM = "custom"


class DeviceStatus(Enum):
    """Device connection and operational status."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    STREAMING = "streaming"
    ERROR = "error"
    CONFIGURATION = "configuration"
    CALIBRATING = "calibrating"
    PAUSED = "paused"


class ConnectionType(Enum):
    """Device connection methods."""

    SERIAL = "serial"
    USB = "usb"
    BLUETOOTH = "bluetooth"
    WIFI = "wifi"
    LSL = "lsl"
    SYNTHETIC = "synthetic"


class SignalQuality(Enum):
    """Signal quality assessment levels."""

    EXCELLENT = "excellent"  # >90%
    GOOD = "good"  # 70-90%
    FAIR = "fair"  # 50-70%
    POOR = "poor"  # 30-50%
    UNUSABLE = "unusable"  # <30%


@dataclass
class DeviceInfo:
    """Complete device information and metadata."""

    # Core identification
    device_id: str
    device_type: DeviceType
    model: str
    firmware_version: str
    serial_number: Optional[str] = None

    # Capabilities
    channel_count: int = 8
    sampling_rate: float = 250.0
    supported_sampling_rates: List[float] = field(default_factory=lambda: [250.0])
    capabilities: List[str] = field(default_factory=list)

    # Connection information
    connection_type: ConnectionType = ConnectionType.SERIAL
    connection_params: Dict[str, Any] = field(default_factory=dict)

    # Status and health
    status: DeviceStatus = DeviceStatus.DISCONNECTED
    last_seen: datetime = field(default_factory=datetime.utcnow)
    uptime_seconds: float = 0.0

    # Signal quality and performance
    signal_quality: SignalQuality = SignalQuality.POOR
    impedance_values: Dict[str, float] = field(default_factory=dict)
    noise_level: float = 0.0

    # Configuration
    configuration: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Performance metrics
    latency_ms: float = 0.0
    packet_loss_rate: float = 0.0
    data_rate_hz: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert device info to dictionary format."""
        return {
            "device_id": self.device_id,
            "device_type": self.device_type.value,
            "model": self.model,
            "firmware_version": self.firmware_version,
            "serial_number": self.serial_number,
            "channel_count": self.channel_count,
            "sampling_rate": self.sampling_rate,
            "supported_sampling_rates": self.supported_sampling_rates,
            "capabilities": self.capabilities,
            "connection_type": self.connection_type.value,
            "connection_params": self.connection_params,
            "status": self.status.value,
            "last_seen": self.last_seen.isoformat(),
            "uptime_seconds": self.uptime_seconds,
            "signal_quality": self.signal_quality.value,
            "impedance_values": self.impedance_values,
            "noise_level": self.noise_level,
            "configuration": self.configuration,
            "metadata": self.metadata,
            "latency_ms": self.latency_ms,
            "packet_loss_rate": self.packet_loss_rate,
            "data_rate_hz": self.data_rate_hz,
        }


@dataclass
class DataSample:
    """Single data sample from a BCI device."""

    # Core data
    timestamp: float
    channel_data: np.ndarray
    sample_number: int

    # Quality indicators
    signal_quality: Dict[str, float] = field(default_factory=dict)
    artifacts_detected: List[str] = field(default_factory=list)

    # Device context
    device_id: str = ""
    sampling_rate: float = 250.0

    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeviceEvent:
    """Device state change or notification event."""

    event_type: str
    device_id: str
    timestamp: datetime
    data: Dict[str, Any] = field(default_factory=dict)
    severity: str = "info"  # info, warning, error, critical


class BaseDevice(ABC):
    """Abstract base class for all BCI device implementations."""

    def __init__(self, device_info: DeviceInfo):
        """Initialize device with device information.

        Args:
            device_info: Complete device information
        """
        self.device_info = device_info
        self.is_connected = False
        self.is_streaming = False

        # Event callbacks
        self._event_callbacks: List[Callable[[DeviceEvent], None]] = []
        self._data_callbacks: List[Callable[[DataSample], None]] = []

        # Internal state
        self._connection_task: Optional[asyncio.Task] = None
        self._streaming_task: Optional[asyncio.Task] = None
        self._last_sample_time = 0.0

        logger.info(f"Initialized device: {device_info.device_id}")

    # Abstract methods that must be implemented by subclasses

    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to the device.

        Returns:
            True if connection successful
        """
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from the device.

        Returns:
            True if disconnection successful
        """
        pass

    @abstractmethod
    async def start_streaming(self) -> bool:
        """Start data streaming from the device.

        Returns:
            True if streaming started successfully
        """
        pass

    @abstractmethod
    async def stop_streaming(self) -> bool:
        """Stop data streaming from the device.

        Returns:
            True if streaming stopped successfully
        """
        pass

    @abstractmethod
    async def configure(self, config: Dict[str, Any]) -> bool:
        """Configure device parameters.

        Args:
            config: Configuration parameters

        Returns:
            True if configuration successful
        """
        pass

    @abstractmethod
    async def get_impedance(self) -> Dict[str, float]:
        """Get electrode impedance values.

        Returns:
            Dictionary mapping channel names to impedance values (kOhms)
        """
        pass

    @abstractmethod
    async def perform_self_test(self) -> Dict[str, Any]:
        """Perform device self-test and diagnostics.

        Returns:
            Test results and diagnostic information
        """
        pass

    # Common implementation methods

    def add_event_callback(self, callback: Callable[[DeviceEvent], None]) -> None:
        """Add callback for device events.

        Args:
            callback: Function to call when device events occur
        """
        self._event_callbacks.append(callback)

    def remove_event_callback(self, callback: Callable[[DeviceEvent], None]) -> None:
        """Remove event callback.

        Args:
            callback: Function to remove from callbacks
        """
        if callback in self._event_callbacks:
            self._event_callbacks.remove(callback)

    def add_data_callback(self, callback: Callable[[DataSample], None]) -> None:
        """Add callback for data samples.

        Args:
            callback: Function to call when new data arrives
        """
        self._data_callbacks.append(callback)

    def remove_data_callback(self, callback: Callable[[DataSample], None]) -> None:
        """Remove data callback.

        Args:
            callback: Function to remove from callbacks
        """
        if callback in self._data_callbacks:
            self._data_callbacks.remove(callback)

    def _emit_event(
        self, event_type: str, data: Dict[str, Any] = None, severity: str = "info"
    ) -> None:
        """Emit device event to all registered callbacks.

        Args:
            event_type: Type of event
            data: Event data
            severity: Event severity level
        """
        event = DeviceEvent(
            event_type=event_type,
            device_id=self.device_info.device_id,
            timestamp=datetime.utcnow(),
            data=data or {},
            severity=severity,
        )

        for callback in self._event_callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in event callback: {str(e)}")

    def _emit_data(self, sample: DataSample) -> None:
        """Emit data sample to all registered callbacks.

        Args:
            sample: Data sample to emit
        """
        sample.device_id = self.device_info.device_id

        for callback in self._data_callbacks:
            try:
                callback(sample)
            except Exception as e:
                logger.error(f"Error in data callback: {str(e)}")

    async def get_status(self) -> DeviceStatus:
        """Get current device status.

        Returns:
            Current device status
        """
        return self.device_info.status

    async def get_device_info(self) -> DeviceInfo:
        """Get complete device information.

        Returns:
            Current device information
        """
        return self.device_info

    async def update_status(self, status: DeviceStatus) -> None:
        """Update device status and emit event.

        Args:
            status: New device status
        """
        old_status = self.device_info.status
        self.device_info.status = status
        self.device_info.last_seen = datetime.utcnow()

        self._emit_event(
            "status_changed",
            {"old_status": old_status.value, "new_status": status.value},
        )

        logger.info(
            f"Device {self.device_info.device_id} status: {old_status.value} -> {status.value}"
        )

    async def calculate_signal_quality(self, data: np.ndarray) -> SignalQuality:
        """Calculate signal quality from data.

        Args:
            data: Channel data for quality assessment

        Returns:
            Signal quality assessment
        """
        try:
            # Simple quality assessment based on signal variance and outliers
            if len(data.shape) == 1:
                data = data.reshape(1, -1)

            # Calculate signal-to-noise ratio approximation
            signal_power = np.var(data, axis=1)
            noise_estimate = np.median(np.abs(np.diff(data, axis=1)), axis=1) / 0.6745

            # Avoid division by zero
            snr = np.mean(signal_power / (noise_estimate + 1e-10))

            # Convert SNR to quality assessment
            if snr > 10:
                quality = SignalQuality.EXCELLENT
            elif snr > 5:
                quality = SignalQuality.GOOD
            elif snr > 2:
                quality = SignalQuality.FAIR
            elif snr > 0.5:
                quality = SignalQuality.POOR
            else:
                quality = SignalQuality.UNUSABLE

            self.device_info.signal_quality = quality
            return quality

        except Exception as e:
            logger.error(f"Error calculating signal quality: {str(e)}")
            return SignalQuality.POOR

    async def cleanup(self) -> None:
        """Clean up device resources."""
        try:
            if self.is_streaming:
                await self.stop_streaming()

            if self.is_connected:
                await self.disconnect()

            # Cancel any running tasks
            if self._connection_task and not self._connection_task.done():
                self._connection_task.cancel()

            if self._streaming_task and not self._streaming_task.done():
                self._streaming_task.cancel()

            logger.info(f"Cleaned up device: {self.device_info.device_id}")

        except Exception as e:
            logger.error(f"Error during device cleanup: {str(e)}")

    def __str__(self) -> str:
        """String representation of device."""
        return f"{self.device_info.device_type.value}({self.device_info.device_id})"

    def __repr__(self) -> str:
        """Detailed string representation of device."""
        return (
            f"BaseDevice(id={self.device_info.device_id}, "
            f"type={self.device_info.device_type.value}, "
            f"status={self.device_info.status.value})"
        )
