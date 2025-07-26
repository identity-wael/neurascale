"""Device Interface Management for NeuraScale Neural Engine.

This module provides comprehensive BCI device management including:
- Device discovery and registration
- LSL stream integration
- Hardware adapter support for OpenBCI, BrainFlow, and custom devices
- Real-time health monitoring and diagnostics
- Device configuration management
"""

from .base import BaseDevice, DeviceType, DeviceStatus, ConnectionType
from .device_manager import DeviceManager
from .device_registry import DeviceRegistry
from .lsl_integration import LSLIntegration
from .health_monitor import HealthMonitor

__version__ = "1.0.0"
__all__ = [
    "BaseDevice",
    "DeviceType",
    "DeviceStatus",
    "ConnectionType",
    "DeviceManager",
    "DeviceRegistry",
    "LSLIntegration",
    "HealthMonitor",
]
