"""Dashboard configurations for NeuraScale Neural Engine monitoring.

This package provides dashboard templates and configurations for
Grafana and other visualization systems.
"""

from .grafana_dashboards import GrafanaDashboardManager
from .neural_dashboard import NeuralDashboard
from .system_dashboard import SystemDashboard
from .alert_dashboard import AlertDashboard

__all__ = [
    "GrafanaDashboardManager",
    "NeuralDashboard",
    "SystemDashboard",
    "AlertDashboard",
]
