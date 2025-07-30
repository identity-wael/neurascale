"""NeuraScale MCP (Model Context Protocol) Servers.

This module provides MCP servers for interfacing with the NeuraScale Neural Engine,
enabling AI assistants like Claude to interact with neural data, control devices,
and perform complex analyses through standardized tool interfaces.
"""

from .core.base_server import BaseNeuralMCPServer
from .servers.neural_data.server import NeuralDataMCPServer
from .servers.device_control.server import DeviceControlMCPServer

__version__ = "1.0.0"
__author__ = "NeuraScale Engineering Team"

__all__ = [
    "BaseNeuralMCPServer",
    "NeuralDataMCPServer",
    "DeviceControlMCPServer",
]
