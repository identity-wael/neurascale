"""Device Interface Management for NeuraScale Neural Engine.

This module provides comprehensive BCI device management including:
- Device discovery and registration
- LSL stream integration
- Hardware adapter support for OpenBCI, BrainFlow, and custom devices
- Real-time health monitoring and diagnostics
- Device configuration management
"""

from .base import (
    BaseDevice,
    DeviceInfo,
    DeviceType,
    DeviceStatus,
    ConnectionType,
    SignalQuality,
    DataSample,
    DeviceEvent,
)
from .device_manager import (
    DeviceManager,
    DeviceManagerConfig,
    DeviceManagerStats,
    DiscoveryMethod,
)
from .device_registry import DeviceRegistry
from .lsl_integration import LSLIntegration, LSLStreamInfo, LSLStreamType
from .health_monitor import HealthMonitor, HealthStatus, AlertType, HealthMetrics

# Import adapters
from .adapters.lsl_adapter import LSLAdapter
from .adapters.openbci_adapter import OpenBCIAdapter
from .adapters.brainflow_adapter import BrainFlowAdapter
from .adapters.synthetic_adapter import SyntheticAdapter

# Import protocols
from .protocols.serial_protocol import SerialProtocol, SerialConfig

__version__ = "1.0.0"
__all__ = [
    # Base classes and data structures
    "BaseDevice",
    "DeviceInfo",
    "DeviceType",
    "DeviceStatus",
    "ConnectionType",
    "SignalQuality",
    "DataSample",
    "DeviceEvent",
    # Core management classes
    "DeviceManager",
    "DeviceManagerConfig",
    "DeviceManagerStats",
    "DiscoveryMethod",
    "DeviceRegistry",
    # LSL Integration
    "LSLIntegration",
    "LSLStreamInfo",
    "LSLStreamType",
    # Health monitoring
    "HealthMonitor",
    "HealthStatus",
    "AlertType",
    "HealthMetrics",
    # Device adapters
    "LSLAdapter",
    "OpenBCIAdapter",
    "BrainFlowAdapter",
    "SyntheticAdapter",
    # Protocols
    "SerialProtocol",
    "SerialConfig",
]
