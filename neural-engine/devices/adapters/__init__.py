"""Device Adapters for NeuraScale Neural Engine.

Hardware-specific adapters for different BCI device types.
"""

from .lsl_adapter import LSLAdapter
from .openbci_adapter import OpenBCIAdapter
from .brainflow_adapter import BrainFlowAdapter
from .synthetic_adapter import SyntheticAdapter

__all__ = [
    "LSLAdapter",
    "OpenBCIAdapter",
    "BrainFlowAdapter",
    "SyntheticAdapter",
]
