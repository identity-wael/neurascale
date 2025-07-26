"""Alert management system for NeuraScale Neural Engine monitoring.

This module provides comprehensive alert management including rule evaluation,
alert triggering, suppression, and integration with notification services.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import logging

from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertStatus(Enum):
    """Alert status states."""

    TRIGGERED = "triggered"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


class RuleCondition(Enum):
    """Rule condition operators."""

    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    EQUALS = "eq"
    NOT_EQUALS = "ne"
    GREATER_EQUAL = "ge"
    LESS_EQUAL = "le"
    CONTAINS = "contains"
    REGEX_MATCH = "regex"


@dataclass
class AlertRule:
    """Alert rule definition."""

    id: str
    name: str
    description: str
    metric_name: str
    condition: RuleCondition
    threshold: float
    severity: AlertSeverity

    # Rule behavior
    evaluation_interval: int = 60  # seconds
    for_duration: int = 300  # seconds (how long condition must be true)
    cooldown_period: int = 1800  # seconds (suppression after resolution)

    # Rule targeting
    labels: Dict[str, str] = field(default_factory=dict)
    tags: Dict[str, str] = field(default_factory=dict)

    # Advanced configuration
    enabled: bool = True
    notification_channels: List[str] = field(default_factory=list)
    escalation_policy: Optional[str] = None

    # Runtime state
    last_evaluation: Optional[datetime] = None
    condition_met_since: Optional[datetime] = None
    last_triggered: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert rule to dictionary format."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "metric_name": self.metric_name,
            "condition": self.condition.value,
            "threshold": self.threshold,
            "severity": self.severity.value,
            "evaluation_interval": self.evaluation_interval,
            "for_duration": self.for_duration,
            "cooldown_period": self.cooldown_period,
            "labels": self.labels,
            "tags": self.tags,
            "enabled": self.enabled,
            "notification_channels": self.notification_channels,
            "escalation_policy": self.escalation_policy,
            "last_evaluation": (
                self.last_evaluation.isoformat() if self.last_evaluation else None
            ),
            "condition_met_since": (
                self.condition_met_since.isoformat()
                if self.condition_met_since
                else None
            ),
            "last_triggered": (
                self.last_triggered.isoformat() if self.last_triggered else None
            ),
        }


@dataclass
class Alert:
    """Alert instance."""

    id: str
    rule_id: str
    rule_name: str
    severity: AlertSeverity
    status: AlertStatus
    message: str

    # Alert context
    metric_name: str
    metric_value: float
    threshold: float
    labels: Dict[str, str] = field(default_factory=dict)

    # Timestamps
    triggered_at: datetime = field(default_factory=datetime.utcnow)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    # Additional data
    details: Dict[str, Any] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary format."""
        return {
            "id": self.id,
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "severity": self.severity.value,
            "status": self.status.value,
            "message": self.message,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "threshold": self.threshold,
            "labels": self.labels,
            "triggered_at": self.triggered_at.isoformat(),
            "acknowledged_at": (
                self.acknowledged_at.isoformat() if self.acknowledged_at else None
            ),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "details": self.details,
            "annotations": self.annotations,
        }


class AlertManager:
    """Manages alert rules, evaluation, and notification."""

    def __init__(self, config):
        """Initialize alert manager.

        Args:
            config: Monitoring configuration
        """
        self.config = config

        # Rule and alert storage
        self.rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: deque = deque(maxlen=1000)

        # Evaluation tracking
        self.rule_states: Dict[str, Dict] = defaultdict(dict)
        self.suppressed_rules: Dict[str, datetime] = {}

        # Notification integration
        self.notification_service = None
        self.escalation_policies = {}

        # Statistics
        self.total_evaluations = 0
        self.total_alerts_triggered = 0
        self.total_alerts_resolved = 0
        self.evaluation_errors = 0

        # Initialize default rules
        self._initialize_default_rules()

        logger.info("AlertManager initialized")

    def _initialize_default_rules(self) -> None:
        """Initialize default alert rules for Neural Engine."""

        # Neural processing alerts
        self.register_rule(
            AlertRule(
                id="high_signal_processing_latency",
                name="High Signal Processing Latency",
                description="Neural signal processing latency is above threshold",
                metric_name="neural_signal_processing_latency_ms",
                condition=RuleCondition.GREATER_THAN,
                threshold=100.0,  # 100ms
                severity=AlertSeverity.WARNING,
                for_duration=120,  # 2 minutes
                notification_channels=["email", "slack"],
            )
        )

        self.register_rule(
            AlertRule(
                id="low_data_quality",
                name="Low Neural Data Quality",
                description="Neural data quality score is below acceptable threshold",
                metric_name="neural_data_quality_score",
                condition=RuleCondition.LESS_THAN,
                threshold=0.7,
                severity=AlertSeverity.WARNING,
                for_duration=300,  # 5 minutes
                notification_channels=["email"],
            )
        )

        self.register_rule(
            AlertRule(
                id="device_connection_failures",
                name="High Device Connection Failures",
                description="Multiple device connection failures detected",
                metric_name="device_connection_failures_rate",
                condition=RuleCondition.GREATER_THAN,
                threshold=3.0,  # 3 failures per minute
                severity=AlertSeverity.CRITICAL,
                for_duration=60,  # 1 minute
                notification_channels=["email", "slack", "pagerduty"],
            )
        )

        # System resource alerts
        self.register_rule(
            AlertRule(
                id="high_cpu_usage",
                name="High CPU Usage",
                description="System CPU usage is critically high",
                metric_name="system_cpu_percent",
                condition=RuleCondition.GREATER_THAN,
                threshold=85.0,
                severity=AlertSeverity.CRITICAL,
                for_duration=180,  # 3 minutes
                notification_channels=["email", "slack"],
            )
        )

        self.register_rule(
            AlertRule(
                id="high_memory_usage",
                name="High Memory Usage",
                description="System memory usage is critically high",
                metric_name="system_memory_percent",
                condition=RuleCondition.GREATER_THAN,
                threshold=90.0,
                severity=AlertSeverity.CRITICAL,
                for_duration=300,  # 5 minutes
                notification_channels=["email", "slack", "pagerduty"],
            )
        )

        self.register_rule(
            AlertRule(
                id="low_disk_space",
                name="Low Disk Space",
                description="System disk space is running low",
                metric_name="system_disk_percent",
                condition=RuleCondition.GREATER_THAN,
                threshold=90.0,
                severity=AlertSeverity.WARNING,
                for_duration=600,  # 10 minutes
                notification_channels=["email"],
            )
        )

        # API performance alerts
        self.register_rule(
            AlertRule(
                id="high_api_error_rate",
                name="High API Error Rate",
                description="API error rate is above acceptable threshold",
                metric_name="api_error_rate_percent",
                condition=RuleCondition.GREATER_THAN,
                threshold=5.0,  # 5% error rate
                severity=AlertSeverity.WARNING,
                for_duration=180,  # 3 minutes
                notification_channels=["email", "slack"],
            )
        )

        self.register_rule(
            AlertRule(
                id="high_api_latency",
                name="High API Response Time",
                description="API response time is above acceptable threshold",
                metric_name="api_response_time_ms",
                condition=RuleCondition.GREATER_THAN,
                threshold=2000.0,  # 2 seconds
                severity=AlertSeverity.WARNING,
                for_duration=300,  # 5 minutes
                notification_channels=["email"],
            )
        )

        # Security alerts
        self.register_rule(
            AlertRule(
                id="high_failed_login_rate",
                name="High Failed Login Rate",
                description="Unusually high rate of failed login attempts",
                metric_name="failed_login_attempts_rate",
                condition=RuleCondition.GREATER_THAN,
                threshold=10.0,  # 10 failures per minute
                severity=AlertSeverity.CRITICAL,
                for_duration=60,  # 1 minute
                notification_channels=["email", "slack", "security"],
            )
        )

    def register_rule(self, rule: AlertRule) -> bool:
        """Register a new alert rule.

        Args:
            rule: AlertRule to register

        Returns:
            True if registration successful
        """
        try:
            if rule.id in self.rules:
                logger.warning(f"Alert rule {rule.id} already exists")
                return False

            self.rules[rule.id] = rule
            self.rule_states[rule.id] = {
                "condition_met": False,
                "condition_start": None,
                "last_value": None,
            }

            logger.info(f"Registered alert rule: {rule.id}")
            return True

        except Exception as e:
            logger.error(f"Failed to register rule {rule.id}: {str(e)}")
            return False

    def unregister_rule(self, rule_id: str) -> bool:
        """Unregister an alert rule.

        Args:
            rule_id: ID of rule to unregister

        Returns:
            True if unregistration successful
        """
        try:
            if rule_id not in self.rules:
                logger.warning(f"Alert rule {rule_id} not found")
                return False

            # Resolve any active alerts for this rule
            alerts_to_resolve = [
                alert
                for alert in self.active_alerts.values()
                if alert.rule_id == rule_id
            ]

            for alert in alerts_to_resolve:
                self.resolve_alert(alert.id, "Rule unregistered")

            # Remove rule and state
            del self.rules[rule_id]
            del self.rule_states[rule_id]

            logger.info(f"Unregistered alert rule: {rule_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to unregister rule {rule_id}: {str(e)}")
            return False

    async def evaluate_rule(
        self, rule_id: str, current_metrics: Dict[str, float]
    ) -> bool:
        """Evaluate a specific alert rule.

        Args:
            rule_id: ID of rule to evaluate
            current_metrics: Current metric values

        Returns:
            True if rule was evaluated successfully
        """
        if rule_id not in self.rules:
            logger.warning(f"Rule {rule_id} not found")
            return False

        rule = self.rules[rule_id]

        if not rule.enabled:
            return True

        # Check if rule is suppressed
        if rule_id in self.suppressed_rules:
            if datetime.utcnow() < self.suppressed_rules[rule_id]:
                return True  # Still suppressed
            else:
                del self.suppressed_rules[rule_id]  # Suppression expired

        try:
            current_time = datetime.utcnow()
            rule.last_evaluation = current_time

            # Get metric value
            metric_value = current_metrics.get(rule.metric_name)
            if metric_value is None:
                logger.debug(f"Metric {rule.metric_name} not found for rule {rule_id}")
                return True

            # Evaluate condition
            condition_met = self._evaluate_condition(
                metric_value, rule.condition, rule.threshold
            )

            state = self.rule_states[rule_id]
            state["last_value"] = metric_value

            if condition_met:
                if not state["condition_met"]:
                    # Condition just became true
                    state["condition_met"] = True
                    state["condition_start"] = current_time
                    rule.condition_met_since = current_time

                # Check if condition has been true long enough
                elif state["condition_start"]:
                    duration = (current_time - state["condition_start"]).total_seconds()
                    if duration >= rule.for_duration:
                        # Trigger alert if not already active
                        await self._trigger_alert_if_needed(rule, metric_value)

            else:
                if state["condition_met"]:
                    # Condition is no longer true
                    state["condition_met"] = False
                    state["condition_start"] = None
                    rule.condition_met_since = None

                    # Resolve any active alerts for this rule
                    await self._resolve_alerts_for_rule(
                        rule_id, "Condition no longer met"
                    )

            self.total_evaluations += 1
            return True

        except Exception as e:
            logger.error(f"Failed to evaluate rule {rule_id}: {str(e)}")
            self.evaluation_errors += 1
            return False

    async def evaluate_all_rules(
        self, current_metrics: Optional[Dict[str, float]] = None
    ) -> int:
        """Evaluate all enabled alert rules.

        Args:
            current_metrics: Optional current metric values

        Returns:
            Number of alerts triggered
        """
        if current_metrics is None:
            current_metrics = {}

        alerts_triggered = 0

        for rule_id in self.rules.keys():
            try:
                await self.evaluate_rule(rule_id, current_metrics)
            except Exception as e:
                logger.error(f"Error evaluating rule {rule_id}: {str(e)}")

        return alerts_triggered

    async def trigger_manual_alert(
        self,
        alert_type: str,
        message: str,
        severity: str = "warning",
        details: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Trigger a manual alert.

        Args:
            alert_type: Type / category of alert
            message: Alert message
            severity: Alert severity level
            details: Optional additional details

        Returns:
            Alert ID
        """
        try:
            import uuid

            alert_id = str(uuid.uuid4())

            alert = Alert(
                id=alert_id,
                rule_id="manual",
                rule_name=f"Manual Alert - {alert_type}",
                severity=AlertSeverity(severity),
                status=AlertStatus.TRIGGERED,
                message=message,
                metric_name="manual",
                metric_value=0.0,
                threshold=0.0,
                details=details or {},
                annotations={"alert_type": alert_type, "manual": "true"},
            )

            self.active_alerts[alert_id] = alert
            self.alert_history.append(alert)
            self.total_alerts_triggered += 1

            # Send notifications
            await self._send_alert_notifications(alert)

            logger.info(f"Manual alert triggered: {alert_id}")
            return alert_id

        except Exception as e:
            logger.error(f"Failed to trigger manual alert: {str(e)}")
            raise

    def acknowledge_alert(self, alert_id: str, acknowledged_by: str = "system") -> bool:
        """Acknowledge an alert.

        Args:
            alert_id: Alert ID to acknowledge
            acknowledged_by: Who acknowledged the alert

        Returns:
            True if acknowledgment successful
        """
        try:
            if alert_id not in self.active_alerts:
                logger.warning(f"Alert {alert_id} not found")
                return False

            alert = self.active_alerts[alert_id]

            if alert.status != AlertStatus.TRIGGERED:
                logger.warning(f"Alert {alert_id} is not in triggered state")
                return False

            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_at = datetime.utcnow()
            alert.annotations["acknowledged_by"] = acknowledged_by

            logger.info(f"Alert {alert_id} acknowledged by {acknowledged_by}")
            return True

        except Exception as e:
            logger.error(f"Failed to acknowledge alert {alert_id}: {str(e)}")
            return False

    def resolve_alert(
        self, alert_id: str, resolution_reason: str = "Manual resolution"
    ) -> bool:
        """Resolve an alert.

        Args:
            alert_id: Alert ID to resolve
            resolution_reason: Reason for resolution

        Returns:
            True if resolution successful
        """
        try:
            if alert_id not in self.active_alerts:
                logger.warning(f"Alert {alert_id} not found")
                return False

            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.utcnow()
            alert.annotations["resolution_reason"] = resolution_reason

            # Move to history and remove from active
            self.alert_history.append(alert)
            del self.active_alerts[alert_id]

            self.total_alerts_resolved += 1

            # Apply cooldown period to the rule
            if alert.rule_id in self.rules:
                rule = self.rules[alert.rule_id]
                cooldown_end = datetime.utcnow() + timedelta(
                    seconds=rule.cooldown_period
                )
                self.suppressed_rules[alert.rule_id] = cooldown_end

            logger.info(f"Alert {alert_id} resolved: {resolution_reason}")
            return True

        except Exception as e:
            logger.error(f"Failed to resolve alert {alert_id}: {str(e)}")
            return False

    def get_active_alerts(
        self, severity: Optional[AlertSeverity] = None
    ) -> List[Alert]:
        """Get list of active alerts.

        Args:
            severity: Optional severity filter

        Returns:
            List of active alerts
        """
        alerts = list(self.active_alerts.values())

        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]

        # Sort by severity and triggered time
        severity_order = {
            AlertSeverity.EMERGENCY: 0,
            AlertSeverity.CRITICAL: 1,
            AlertSeverity.WARNING: 2,
            AlertSeverity.INFO: 3,
        }

        alerts.sort(key=lambda a: (severity_order[a.severity], a.triggered_at))
        return alerts

    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of alert system status.

        Returns:
            Alert summary statistics
        """
        try:
            active_by_severity = defaultdict(int)
            for alert in self.active_alerts.values():
                active_by_severity[alert.severity.value] += 1

            enabled_rules = sum(1 for rule in self.rules.values() if rule.enabled)
            suppressed_rules = len(self.suppressed_rules)

            return {
                "total_rules": len(self.rules),
                "enabled_rules": enabled_rules,
                "suppressed_rules": suppressed_rules,
                "active_alerts": len(self.active_alerts),
                "active_by_severity": dict(active_by_severity),
                "total_evaluations": self.total_evaluations,
                "total_alerts_triggered": self.total_alerts_triggered,
                "total_alerts_resolved": self.total_alerts_resolved,
                "evaluation_errors": self.evaluation_errors,
            }

        except Exception as e:
            logger.error(f"Failed to get alert summary: {str(e)}")
            return {"error": str(e)}

    def _evaluate_condition(
        self, value: float, condition: RuleCondition, threshold: float
    ) -> bool:
        """Evaluate rule condition."""
        try:
            if condition == RuleCondition.GREATER_THAN:
                return value > threshold
            elif condition == RuleCondition.LESS_THAN:
                return value < threshold
            elif condition == RuleCondition.EQUALS:
                return abs(value - threshold) < 0.001  # Float equality
            elif condition == RuleCondition.NOT_EQUALS:
                return abs(value - threshold) >= 0.001
            elif condition == RuleCondition.GREATER_EQUAL:
                return value >= threshold
            elif condition == RuleCondition.LESS_EQUAL:
                return value <= threshold
            else:
                logger.warning(f"Unsupported condition: {condition}")
                return False

        except Exception as e:
            logger.error(f"Error evaluating condition: {str(e)}")
            return False

    async def _trigger_alert_if_needed(
        self, rule: AlertRule, metric_value: float
    ) -> None:
        """Trigger alert if not already active for this rule."""
        # Check if there's already an active alert for this rule
        existing_alert = None
        for alert in self.active_alerts.values():
            if alert.rule_id == rule.id and alert.status == AlertStatus.TRIGGERED:
                existing_alert = alert
                break

        if existing_alert:
            # Update existing alert with new metric value
            existing_alert.metric_value = metric_value
            existing_alert.details["last_updated"] = datetime.utcnow().isoformat()
            return

        # Create new alert
        import uuid

        alert_id = str(uuid.uuid4())

        alert = Alert(
            id=alert_id,
            rule_id=rule.id,
            rule_name=rule.name,
            severity=rule.severity,
            status=AlertStatus.TRIGGERED,
            message=f"{rule.description} (current: {metric_value}, threshold: {rule.threshold})",
            metric_name=rule.metric_name,
            metric_value=metric_value,
            threshold=rule.threshold,
            labels=rule.labels.copy(),
            details={
                "rule_description": rule.description,
                "condition": rule.condition.value,
                "for_duration": rule.for_duration,
            },
        )

        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        self.total_alerts_triggered += 1

        rule.last_triggered = datetime.utcnow()

        # Send notifications
        await self._send_alert_notifications(alert)

        logger.warning(f"Alert triggered: {rule.name} ({alert_id})")

    async def _resolve_alerts_for_rule(self, rule_id: str, reason: str) -> None:
        """Resolve all active alerts for a specific rule."""
        alerts_to_resolve = [
            alert_id
            for alert_id, alert in self.active_alerts.items()
            if alert.rule_id == rule_id
        ]

        for alert_id in alerts_to_resolve:
            self.resolve_alert(alert_id, reason)

    async def _send_alert_notifications(self, alert: Alert) -> None:
        """Send notifications for an alert."""
        try:
            if self.notification_service:
                # Get notification channels from rule
                rule = self.rules.get(alert.rule_id)
                channels = rule.notification_channels if rule else ["email"]

                for channel in channels:
                    await self.notification_service.send_alert_notification(
                        alert, channel
                    )

        except Exception as e:
            logger.error(f"Failed to send alert notifications: {str(e)}")

    def set_notification_service(self, notification_service) -> None:
        """Set the notification service for alert delivery.

        Args:
            notification_service: NotificationService instance
        """
        self.notification_service = notification_service
        logger.info("Notification service configured")
