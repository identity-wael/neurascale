"""
Alert management and processing system
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import aiohttp

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    ERROR = "error"


class AlertStatus(Enum):
    """Alert status"""

    PENDING = "pending"
    FIRING = "firing"
    RESOLVED = "resolved"
    SILENCED = "silenced"


@dataclass
class Alert:
    """Alert definition"""

    name: str
    severity: AlertSeverity
    message: str
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    fingerprint: Optional[str] = None
    status: AlertStatus = AlertStatus.PENDING

    def __post_init__(self) -> None:
        """Generate fingerprint if not provided"""
        if not self.fingerprint:
            # Create unique fingerprint based on alert properties
            label_str = "_".join(f"{k}:{v}" for k, v in sorted(self.labels.items()))
            self.fingerprint = f"{self.name}_{label_str}"


@dataclass
class AlertRule:
    """Alert rule definition"""

    name: str
    expression: str  # Prometheus-style query expression
    duration: timedelta  # How long condition must be true
    severity: AlertSeverity
    labels: Dict[str, str] = field(default_factory=dict)
    annotations: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True


class AlertManager:
    """Manages alerts and notifications"""

    def __init__(
        self,
        webhook_url: Optional[str] = None,
        pagerduty_key: Optional[str] = None,
        slack_webhook: Optional[str] = None,
        alert_history_size: int = 10000,
    ):
        """
        Initialize alert manager

        Args:
            webhook_url: Generic webhook URL
            pagerduty_key: PagerDuty API key
            slack_webhook: Slack webhook URL
            alert_history_size: Number of alerts to keep in history
        """
        self.webhook_url = webhook_url
        self.pagerduty_key = pagerduty_key
        self.slack_webhook = slack_webhook

        # Alert storage
        self._active_alerts: Dict[str, Alert] = {}
        self._alert_history: deque = deque(maxlen=alert_history_size)
        self._pending_alerts: asyncio.Queue = asyncio.Queue()

        # Alert rules
        self._alert_rules: Dict[str, AlertRule] = {}

        # Alert state tracking
        self._alert_states: Dict[str, datetime] = {}  # Track when condition started
        self._silence_rules: Dict[str, datetime] = {}  # Silence until timestamp

        # Notification tracking
        self._notification_history: Dict[str, datetime] = defaultdict(
            lambda: datetime.min
        )
        self._notification_cooldown = timedelta(
            minutes=5
        )  # Minimum time between notifications

        logger.info("Alert manager initialized")

    def register_alert_rule(self, rule: AlertRule) -> None:
        """
        Register new alert rule

        Args:
            rule: Alert rule to register
        """
        self._alert_rules[rule.name] = rule
        logger.info(f"Alert rule registered: {rule.name}")

    def update_alert_rule(self, rule_name: str, enabled: bool) -> None:
        """
        Update alert rule status

        Args:
            rule_name: Name of rule to update
            enabled: Whether rule is enabled
        """
        if rule_name in self._alert_rules:
            self._alert_rules[rule_name].enabled = enabled
            logger.info(
                f"Alert rule {rule_name} {'enabled' if enabled else 'disabled'}"
            )

    async def trigger_alert(
        self,
        name: str,
        severity: str,
        message: str,
        labels: Optional[Dict[str, str]] = None,
        annotations: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Trigger an alert

        Args:
            name: Alert name
            severity: Alert severity
            message: Alert message
            labels: Alert labels
            annotations: Alert annotations
        """
        alert = Alert(
            name=name,
            severity=AlertSeverity(severity),
            message=message,
            labels=labels or {},
            annotations=annotations or {},
        )

        # Check if alert is silenced
        if self._is_silenced(alert.fingerprint):
            alert.status = AlertStatus.SILENCED
            logger.info(f"Alert {alert.name} is silenced")
            return

        # Add to pending queue
        await self._pending_alerts.put(alert)
        logger.info(f"Alert triggered: {alert.name} - {alert.message}")

    async def evaluate_alerts(self, metrics: Dict[str, float]) -> None:  # noqa: C901
        """
        Evaluate alert rules against metrics

        Args:
            metrics: Current metrics values
        """
        current_time = datetime.now()

        for rule_name, rule in self._alert_rules.items():
            if not rule.enabled:
                continue

            try:
                # Evaluate rule expression (simplified for this implementation)
                # In production, you'd use a proper expression evaluator
                condition_met = self._evaluate_expression(rule.expression, metrics)

                if condition_met:
                    # Track how long condition has been true
                    if rule_name not in self._alert_states:
                        self._alert_states[rule_name] = current_time

                    # Check if duration threshold met
                    if current_time - self._alert_states[rule_name] >= rule.duration:
                        # Create alert
                        alert = Alert(
                            name=rule.name,
                            severity=rule.severity,
                            message=rule.annotations.get(
                                "summary", f"Alert {rule.name} triggered"
                            ),
                            labels=rule.labels,
                            annotations=rule.annotations,
                        )

                        # Check if already active
                        if alert.fingerprint not in self._active_alerts:
                            alert.status = AlertStatus.FIRING
                            self._active_alerts[alert.fingerprint] = alert
                            await self._pending_alerts.put(alert)
                else:
                    # Condition no longer met
                    if rule_name in self._alert_states:
                        del self._alert_states[rule_name]

                        # Resolve alert if it was active
                        for fingerprint, alert in list(self._active_alerts.items()):
                            if alert.name == rule_name:
                                await self._resolve_alert(fingerprint)

            except Exception as e:
                logger.error(f"Error evaluating alert rule {rule_name}: {e}")

    def _evaluate_expression(self, expression: str, metrics: Dict[str, float]) -> bool:
        """
        Evaluate alert expression

        Simple implementation - in production use proper expression parser
        """
        # Example expressions:
        # "cpu_usage > 90"
        # "memory_usage_percent > 80"
        # "error_rate > 0.01"

        try:
            # Parse simple comparison expressions
            parts = expression.split()
            if len(parts) == 3:
                metric_name, operator, threshold = parts
                metric_value = metrics.get(metric_name, 0)
                threshold_value = float(threshold)

                if operator == ">":
                    return metric_value > threshold_value
                elif operator == "<":
                    return metric_value < threshold_value
                elif operator == ">=":
                    return metric_value >= threshold_value
                elif operator == "<=":
                    return metric_value <= threshold_value
                elif operator == "==":
                    return metric_value == threshold_value

        except Exception as e:
            logger.error(f"Error evaluating expression '{expression}': {e}")

        return False

    async def _resolve_alert(self, fingerprint: str) -> None:
        """Resolve an active alert"""
        if fingerprint in self._active_alerts:
            alert = self._active_alerts[fingerprint]
            alert.status = AlertStatus.RESOLVED

            # Move to history
            self._alert_history.append(alert)
            del self._active_alerts[fingerprint]

            # Send resolution notification
            await self._send_resolution_notification(alert)

            logger.info(f"Alert resolved: {alert.name}")

    def update_alert_status(self, alert_id: str, status: str) -> None:
        """
        Update alert status

        Args:
            alert_id: Alert fingerprint
            status: New status
        """
        if alert_id in self._active_alerts:
            self._active_alerts[alert_id].status = AlertStatus(status)
            logger.info(f"Alert {alert_id} status updated to {status}")

    def silence_alert(self, fingerprint: str, duration: timedelta) -> None:
        """
        Silence an alert for specified duration

        Args:
            fingerprint: Alert fingerprint
            duration: How long to silence
        """
        self._silence_rules[fingerprint] = datetime.now() + duration
        logger.info(f"Alert {fingerprint} silenced for {duration}")

    def _is_silenced(self, fingerprint: str) -> bool:
        """Check if alert is silenced"""
        if fingerprint in self._silence_rules:
            if datetime.now() < self._silence_rules[fingerprint]:
                return True
            else:
                # Silence expired
                del self._silence_rules[fingerprint]
        return False

    async def process_pending_alerts(self) -> int:
        """
        Process pending alerts and send notifications

        Returns:
            Number of alerts processed
        """
        processed_count = 0

        while not self._pending_alerts.empty():
            try:
                alert = await asyncio.wait_for(self._pending_alerts.get(), timeout=0.1)

                # Check notification cooldown
                if self._should_notify(alert):
                    await self._send_notifications(alert)
                    self._notification_history[alert.fingerprint] = datetime.now()

                # Add to active alerts if firing
                if alert.status == AlertStatus.FIRING:
                    self._active_alerts[alert.fingerprint] = alert

                # Add to history
                self._alert_history.append(alert)

                processed_count += 1

            except asyncio.TimeoutError:
                break
            except Exception as e:
                logger.error(f"Error processing alert: {e}")

        return processed_count

    def _should_notify(self, alert: Alert) -> bool:
        """Check if notification should be sent"""
        last_notification = self._notification_history.get(
            alert.fingerprint, datetime.min
        )

        # Check cooldown period
        if datetime.now() - last_notification < self._notification_cooldown:
            return False

        # Always notify for critical alerts
        if alert.severity == AlertSeverity.CRITICAL:
            return True

        # Check other conditions...
        return True

    async def _send_notifications(self, alert: Alert) -> None:
        """Send alert notifications to configured channels"""
        tasks = []

        # Send to webhook
        if self.webhook_url:
            tasks.append(self._send_webhook_notification(alert))

        # Send to PagerDuty for critical alerts
        if self.pagerduty_key and alert.severity == AlertSeverity.CRITICAL:
            tasks.append(self._send_pagerduty_notification(alert))

        # Send to Slack
        if self.slack_webhook:
            tasks.append(self._send_slack_notification(alert))

        # Execute all notifications in parallel
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _send_webhook_notification(self, alert: Alert) -> None:
        """Send generic webhook notification"""
        try:
            payload = {
                "alert": alert.name,
                "severity": alert.severity.value,
                "message": alert.message,
                "labels": alert.labels,
                "annotations": alert.annotations,
                "timestamp": alert.timestamp.isoformat(),
                "fingerprint": alert.fingerprint,
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as response:
                    if response.status != 200:
                        logger.error(f"Webhook notification failed: {response.status}")

        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")

    async def _send_pagerduty_notification(self, alert: Alert) -> None:
        """Send PagerDuty notification"""
        try:
            payload = {
                "routing_key": self.pagerduty_key,
                "event_action": "trigger",
                "dedup_key": alert.fingerprint,
                "payload": {
                    "summary": alert.message,
                    "severity": (
                        "error"
                        if alert.severity == AlertSeverity.CRITICAL
                        else "warning"
                    ),
                    "source": "neural-engine",
                    "component": alert.labels.get("component", "unknown"),
                    "custom_details": {
                        "labels": alert.labels,
                        "annotations": alert.annotations,
                    },
                },
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://events.pagerduty.com/v2/enqueue",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as response:
                    if response.status != 202:
                        logger.error(
                            f"PagerDuty notification failed: {response.status}"
                        )

        except Exception as e:
            logger.error(f"Failed to send PagerDuty notification: {e}")

    async def _send_slack_notification(self, alert: Alert) -> None:
        """Send Slack notification"""
        try:
            # Format message based on severity
            color = {
                AlertSeverity.INFO: "#36a64f",
                AlertSeverity.WARNING: "#ff9800",
                AlertSeverity.CRITICAL: "#ff0000",
                AlertSeverity.ERROR: "#ff0000",
            }.get(alert.severity, "#808080")

            payload = {
                "attachments": [
                    {
                        "fallback": f"{alert.severity.value.upper()}: {alert.message}",
                        "color": color,
                        "title": f"{alert.severity.value.upper()}: {alert.name}",
                        "text": alert.message,
                        "fields": [
                            {"title": key, "value": value, "short": True}
                            for key, value in alert.labels.items()
                        ],
                        "footer": "Neural Engine Monitoring",
                        "ts": int(alert.timestamp.timestamp()),
                    }
                ]
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.slack_webhook,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=5),
                ) as response:
                    if response.status != 200:
                        logger.error(f"Slack notification failed: {response.status}")

        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")

    async def _send_resolution_notification(self, alert: Alert) -> None:
        """Send notification when alert is resolved"""
        # Similar to regular notifications but with resolved status
        if self.slack_webhook:
            payload = {
                "text": f"✅ Alert Resolved: {alert.name}",
                "attachments": [
                    {
                        "color": "#36a64f",
                        "title": f"RESOLVED: {alert.name}",
                        "text": f"The alert '{alert.message}' has been resolved.",
                        "footer": "Neural Engine Monitoring",
                        "ts": int(datetime.now().timestamp()),
                    }
                ],
            }

            try:
                async with aiohttp.ClientSession() as session:
                    await session.post(
                        self.slack_webhook,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=5),
                    )
            except Exception as e:
                logger.error(f"Failed to send resolution notification: {e}")

    def get_active_alerts(self) -> List[Alert]:
        """Get list of active alerts"""
        return list(self._active_alerts.values())

    def get_alerts_in_range(
        self, start_time: datetime, end_time: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get alerts within time range

        Args:
            start_time: Start of time range
            end_time: End of time range

        Returns:
            List of alerts in range
        """
        alerts = []

        for alert in self._alert_history:
            if start_time <= alert.timestamp <= end_time:
                alerts.append(
                    {
                        "name": alert.name,
                        "severity": alert.severity.value,
                        "message": alert.message,
                        "timestamp": alert.timestamp.isoformat(),
                        "status": alert.status.value,
                        "labels": alert.labels,
                        "annotations": alert.annotations,
                    }
                )

        return alerts

    def update_config(
        self,
        webhook_url: Optional[str] = None,
        pagerduty_key: Optional[str] = None,
        slack_webhook: Optional[str] = None,
    ) -> None:
        """
        Update notification configuration

        Args:
            webhook_url: New webhook URL
            pagerduty_key: New PagerDuty key
            slack_webhook: New Slack webhook
        """
        if webhook_url is not None:
            self.webhook_url = webhook_url
        if pagerduty_key is not None:
            self.pagerduty_key = pagerduty_key
        if slack_webhook is not None:
            self.slack_webhook = slack_webhook

        logger.info("Alert manager configuration updated")
