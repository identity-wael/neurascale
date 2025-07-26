"""Alerting and notification system for NeuraScale Neural Engine monitoring.

This package provides alert management, rule evaluation, anomaly detection,
and multi-channel notification capabilities.
"""

from .alert_manager import AlertManager, Alert, AlertRule, AlertSeverity
from .anomaly_detector import AnomalyDetector, AnomalyResult
from .notification_service import NotificationService, NotificationChannel
from .escalation_policy import EscalationPolicy, EscalationLevel

__all__ = [
    "AlertManager",
    "Alert",
    "AlertRule",
    "AlertSeverity",
    "AnomalyDetector",
    "AnomalyResult",
    "NotificationService",
    "NotificationChannel",
    "EscalationPolicy",
    "EscalationLevel",
]
