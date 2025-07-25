"""Device interface layer for neural data acquisition."""

from .interfaces.base_device import BaseDevice, DeviceState, DeviceCapabilities
from .implementations.lsl_device import LSLDevice
from .implementations.openbci_device import OpenBCIDevice
from .implementations.brainflow_device import BrainFlowDevice
from .implementations.synthetic_device import SyntheticDevice
from .device_manager import DeviceManager

__all__ = [
    "BaseDevice",
    "DeviceState",
    "DeviceCapabilities",
    "LSLDevice",
    "OpenBCIDevice",
    "BrainFlowDevice",
    "SyntheticDevice",
    "DeviceManager",
]
