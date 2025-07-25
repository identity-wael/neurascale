"""Device implementations."""

from .lsl_device import LSLDevice
from .openbci_device import OpenBCIDevice
from .brainflow_device import BrainFlowDevice
from .synthetic_device import SyntheticDevice

__all__ = [
    'LSLDevice',
    'OpenBCIDevice',
    'BrainFlowDevice',
    'SyntheticDevice'
]
