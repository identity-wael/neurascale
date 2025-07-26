"""Quality Monitor - Real-time signal quality monitoring and alerting.

This module provides continuous monitoring of signal quality metrics
with configurable thresholds and alert mechanisms.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque

from .preprocessing.quality_assessment import QualityAssessment, QualityMetrics

logger = logging.getLogger(__name__)


@dataclass
class QualityThresholds:
    """Configurable quality thresholds for monitoring."""

    # Overall quality thresholds
    min_overall_score: float = 0.6
    critical_overall_score: float = 0.4

    # SNR thresholds (dB)
    min_snr: float = 5.0
    critical_snr: float = 3.0

    # Noise thresholds (microvolts)
    max_noise_level: float = 50.0
    critical_noise_level: float = 100.0

    # Artifact thresholds (percentage)
    max_artifact_percentage: float = 10.0
    critical_artifact_percentage: float = 20.0

    # Channel thresholds
    max_bad_channels: int = 2
    critical_bad_channels: int = 4

    # Stability thresholds
    max_quality_variance: float = 0.2
    min_stable_duration: float = 5.0  # seconds


@dataclass
class QualityAlert:
    """Quality alert information."""

    timestamp: datetime
    session_id: str
    alert_type: str  # 'warning' or 'critical'
    metric_name: str
    metric_value: float
    threshold_value: float
    message: str
    duration_seconds: float = 0.0
    resolved: bool = False
    resolved_at: Optional[datetime] = None


@dataclass
class QualityTrend:
    """Quality trend information over time."""

    metric_name: str
    window_seconds: float
    values: deque = field(default_factory=lambda: deque(maxlen=100))
    timestamps: deque = field(default_factory=lambda: deque(maxlen=100))

    def add_value(self, value: float, timestamp: datetime) -> None:
        """Add a new value to the trend."""
        self.values.append(value)
        self.timestamps.append(timestamp)

    def get_trend_stats(self) -> Dict[str, float]:
        """Get statistical summary of the trend."""
        if not self.values:
            return {}

        recent_values = list(self.values)
        return {
            "mean": np.mean(recent_values),
            "std": np.std(recent_values),
            "min": np.min(recent_values),
            "max": np.max(recent_values),
            "trend": self._calculate_trend(),
        }

    def _calculate_trend(self) -> float:
        """Calculate trend direction (-1 to 1)."""
        if len(self.values) < 2:
            return 0.0

        # Simple linear regression on recent values
        x = np.arange(len(self.values))
        y = np.array(self.values)

        # Normalize to [-1, 1] range
        if np.std(y) > 0:
            slope = np.polyfit(x, y, 1)[0]
            normalized_slope = np.tanh(slope / np.std(y))
            return float(normalized_slope)
        return 0.0


class QualityMonitor:
    """Real-time quality monitoring system."""

    def __init__(
        self,
        quality_assessment: QualityAssessment,
        thresholds: Optional[QualityThresholds] = None,
    ):
        """Initialize quality monitor.

        Args:
            quality_assessment: Quality assessment instance
            thresholds: Quality thresholds (uses defaults if None)
        """
        self.assessment = quality_assessment
        self.thresholds = thresholds or QualityThresholds()

        # Monitoring state
        self.is_monitoring = False
        self.monitoring_sessions: Dict[str, Dict[str, Any]] = {}

        # Alert management
        self.active_alerts: Dict[str, List[QualityAlert]] = {}
        self.alert_history: deque = deque(maxlen=1000)

        # Callbacks
        self.alert_callbacks: List[Callable] = []

        # Quality trends
        self.trends: Dict[str, Dict[str, QualityTrend]] = {}

        logger.info("QualityMonitor initialized")

    async def start_monitoring(
        self, session_id: str, check_interval: float = 1.0
    ) -> bool:
        """Start monitoring a session.

        Args:
            session_id: Session to monitor
            check_interval: Check interval in seconds

        Returns:
            Success status
        """
        if session_id in self.monitoring_sessions:
            logger.warning(f"Already monitoring session {session_id}")
            return False

        try:
            # Initialize session monitoring
            self.monitoring_sessions[session_id] = {
                "start_time": datetime.utcnow(),
                "check_interval": check_interval,
                "last_check": None,
                "quality_history": deque(maxlen=60),  # Keep 1 minute of history
                "is_stable": False,
                "stable_since": None,
            }

            # Initialize alerts
            self.active_alerts[session_id] = []

            # Initialize trends
            self._initialize_trends(session_id)

            # Start monitoring task
            asyncio.create_task(self._monitor_session(session_id))

            logger.info(f"Started monitoring session {session_id}")
            return True

        except Exception as e:
            logger.error(f"Error starting monitoring: {str(e)}")
            return False

    async def stop_monitoring(self, session_id: str) -> Dict[str, Any]:
        """Stop monitoring a session.

        Args:
            session_id: Session to stop monitoring

        Returns:
            Final monitoring report
        """
        if session_id not in self.monitoring_sessions:
            logger.warning(f"Session {session_id} not being monitored")
            return {}

        # Generate final report
        report = await self.generate_quality_report(session_id)

        # Cleanup
        del self.monitoring_sessions[session_id]

        # Resolve any active alerts
        if session_id in self.active_alerts:
            for alert in self.active_alerts[session_id]:
                if not alert.resolved:
                    alert.resolved = True
                    alert.resolved_at = datetime.utcnow()
            del self.active_alerts[session_id]

        # Remove trends
        if session_id in self.trends:
            del self.trends[session_id]

        logger.info(f"Stopped monitoring session {session_id}")
        return report

    async def check_quality(
        self, session_id: str, data: np.ndarray, sampling_rate: float
    ) -> QualityMetrics:
        """Check quality of signal data.

        Args:
            session_id: Session identifier
            data: Signal data to check
            sampling_rate: Sampling rate

        Returns:
            Quality metrics
        """
        # Assess quality
        metrics = await self.assessment.calculate_signal_quality(data, sampling_rate)

        # Update monitoring if active
        if session_id in self.monitoring_sessions:
            await self._update_monitoring(session_id, metrics)

        return metrics

    async def add_alert_callback(self, callback: Callable) -> None:
        """Add a callback for quality alerts.

        Args:
            callback: Async function to call on alerts
        """
        self.alert_callbacks.append(callback)

    async def get_active_alerts(
        self, session_id: Optional[str] = None
    ) -> List[QualityAlert]:
        """Get active alerts.

        Args:
            session_id: Optional session filter

        Returns:
            List of active alerts
        """
        if session_id:
            return self.active_alerts.get(session_id, [])

        # Return all active alerts
        all_alerts = []
        for alerts in self.active_alerts.values():
            all_alerts.extend(alerts)
        return all_alerts

    async def get_quality_trends(
        self, session_id: str, metric_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get quality trends for a session.

        Args:
            session_id: Session identifier
            metric_names: Specific metrics to retrieve

        Returns:
            Trend information
        """
        if session_id not in self.trends:
            return {}

        session_trends = self.trends[session_id]

        if metric_names:
            # Filter specific metrics
            filtered_trends = {
                name: trend
                for name, trend in session_trends.items()
                if name in metric_names
            }
        else:
            filtered_trends = session_trends

        # Convert to serializable format
        result = {}
        for name, trend in filtered_trends.items():
            stats = trend.get_trend_stats()
            result[name] = {
                "window_seconds": trend.window_seconds,
                "n_samples": len(trend.values),
                "stats": stats,
                "recent_values": list(trend.values)[-10:],  # Last 10 values
            }

        return result

    async def generate_quality_report(self, session_id: str) -> Dict[str, Any]:
        """Generate comprehensive quality report.

        Args:
            session_id: Session identifier

        Returns:
            Quality report
        """
        if session_id not in self.monitoring_sessions:
            return {}

        session_info = self.monitoring_sessions[session_id]

        # Calculate monitoring duration
        duration = (datetime.utcnow() - session_info["start_time"]).total_seconds()

        # Get quality history stats
        quality_history = list(session_info["quality_history"])
        if quality_history:
            quality_scores = [m.overall_score for m in quality_history]
            avg_quality = np.mean(quality_scores)
            quality_stability = 1.0 - np.std(quality_scores)
        else:
            avg_quality = 0.0
            quality_stability = 0.0

        # Count alerts
        alerts = self.active_alerts.get(session_id, [])
        warning_count = sum(1 for a in alerts if a.alert_type == "warning")
        critical_count = sum(1 for a in alerts if a.alert_type == "critical")

        # Get trend summaries
        trend_summaries = await self.get_quality_trends(session_id)

        report = {
            "session_id": session_id,
            "monitoring_duration_seconds": duration,
            "start_time": session_info["start_time"].isoformat(),
            "quality_summary": {
                "average_quality_score": round(avg_quality, 3),
                "quality_stability": round(quality_stability, 3),
                "is_stable": session_info["is_stable"],
                "stable_duration_seconds": self._get_stable_duration(session_id),
            },
            "alert_summary": {
                "total_alerts": len(alerts),
                "warning_alerts": warning_count,
                "critical_alerts": critical_count,
                "unresolved_alerts": sum(1 for a in alerts if not a.resolved),
            },
            "trends": trend_summaries,
            "recommendations": self._generate_recommendations(session_id),
        }

        return report

    async def _monitor_session(self, session_id: str) -> None:
        """Background task to monitor a session."""
        session_info = self.monitoring_sessions.get(session_id)
        if not session_info:
            return

        while session_id in self.monitoring_sessions:
            try:
                # Wait for next check interval
                await asyncio.sleep(session_info["check_interval"])

                # Session might have been removed while sleeping
                if session_id not in self.monitoring_sessions:
                    break

                # Mark that monitoring is still active
                session_info["last_check"] = datetime.utcnow()

            except Exception as e:
                logger.error(f"Error in monitoring loop for {session_id}: {str(e)}")

    async def _update_monitoring(
        self, session_id: str, metrics: QualityMetrics
    ) -> None:
        """Update monitoring with new quality metrics.

        Args:
            session_id: Session identifier
            metrics: Quality metrics
        """
        session_info = self.monitoring_sessions.get(session_id)
        if not session_info:
            return

        # Add to history
        session_info["quality_history"].append(metrics)

        # Update trends
        await self._update_trends(session_id, metrics)

        # Check thresholds
        alerts = await self._check_thresholds(session_id, metrics)

        # Process new alerts
        for alert in alerts:
            await self._process_alert(session_id, alert)

        # Check stability
        await self._check_stability(session_id)

        # Check for resolved alerts
        await self._check_resolved_alerts(session_id, metrics)

    async def _check_thresholds(
        self, session_id: str, metrics: QualityMetrics
    ) -> List[QualityAlert]:
        """Check quality metrics against thresholds.

        Args:
            session_id: Session identifier
            metrics: Quality metrics

        Returns:
            List of new alerts
        """
        alerts = []
        timestamp = datetime.utcnow()

        # Check overall quality score
        if metrics.overall_score < self.thresholds.critical_overall_score:
            alerts.append(
                QualityAlert(
                    timestamp=timestamp,
                    session_id=session_id,
                    alert_type="critical",
                    metric_name="overall_quality",
                    metric_value=metrics.overall_score,
                    threshold_value=self.thresholds.critical_overall_score,
                    message=f"Critical: Overall quality score {metrics.overall_score:.2f} "
                    f"below threshold {self.thresholds.critical_overall_score}",
                )
            )
        elif metrics.overall_score < self.thresholds.min_overall_score:
            alerts.append(
                QualityAlert(
                    timestamp=timestamp,
                    session_id=session_id,
                    alert_type="warning",
                    metric_name="overall_quality",
                    metric_value=metrics.overall_score,
                    threshold_value=self.thresholds.min_overall_score,
                    message=f"Warning: Overall quality score {metrics.overall_score:.2f} "
                    f"below threshold {self.thresholds.min_overall_score}",
                )
            )

        # Check SNR
        if metrics.snr_db < self.thresholds.critical_snr:
            alerts.append(
                QualityAlert(
                    timestamp=timestamp,
                    session_id=session_id,
                    alert_type="critical",
                    metric_name="snr",
                    metric_value=metrics.snr_db,
                    threshold_value=self.thresholds.critical_snr,
                    message=f"Critical: SNR {metrics.snr_db:.1f}dB below threshold",
                )
            )
        elif metrics.snr_db < self.thresholds.min_snr:
            alerts.append(
                QualityAlert(
                    timestamp=timestamp,
                    session_id=session_id,
                    alert_type="warning",
                    metric_name="snr",
                    metric_value=metrics.snr_db,
                    threshold_value=self.thresholds.min_snr,
                    message=f"Warning: SNR {metrics.snr_db:.1f}dB below threshold",
                )
            )

        # Check noise level
        if metrics.noise_level_rms > self.thresholds.critical_noise_level:
            alerts.append(
                QualityAlert(
                    timestamp=timestamp,
                    session_id=session_id,
                    alert_type="critical",
                    metric_name="noise_level",
                    metric_value=metrics.noise_level_rms,
                    threshold_value=self.thresholds.critical_noise_level,
                    message=f"Critical: Noise level {metrics.noise_level_rms:.1f}µV exceeds threshold",
                )
            )
        elif metrics.noise_level_rms > self.thresholds.max_noise_level:
            alerts.append(
                QualityAlert(
                    timestamp=timestamp,
                    session_id=session_id,
                    alert_type="warning",
                    metric_name="noise_level",
                    metric_value=metrics.noise_level_rms,
                    threshold_value=self.thresholds.max_noise_level,
                    message=f"Warning: Noise level {metrics.noise_level_rms:.1f}µV exceeds threshold",
                )
            )

        # Check artifacts
        if metrics.artifact_percentage > self.thresholds.critical_artifact_percentage:
            alerts.append(
                QualityAlert(
                    timestamp=timestamp,
                    session_id=session_id,
                    alert_type="critical",
                    metric_name="artifacts",
                    metric_value=metrics.artifact_percentage,
                    threshold_value=self.thresholds.critical_artifact_percentage,
                    message=f"Critical: Artifact rate {metrics.artifact_percentage:.1f}% exceeds threshold",
                )
            )
        elif metrics.artifact_percentage > self.thresholds.max_artifact_percentage:
            alerts.append(
                QualityAlert(
                    timestamp=timestamp,
                    session_id=session_id,
                    alert_type="warning",
                    metric_name="artifacts",
                    metric_value=metrics.artifact_percentage,
                    threshold_value=self.thresholds.max_artifact_percentage,
                    message=f"Warning: Artifact rate {metrics.artifact_percentage:.1f}% exceeds threshold",
                )
            )

        # Check bad channels
        bad_channel_count = (
            len(metrics.flatline_channels)
            + len(metrics.clipping_channels)
            + len(metrics.high_impedance_channels)
        )

        if bad_channel_count > self.thresholds.critical_bad_channels:
            alerts.append(
                QualityAlert(
                    timestamp=timestamp,
                    session_id=session_id,
                    alert_type="critical",
                    metric_name="bad_channels",
                    metric_value=bad_channel_count,
                    threshold_value=self.thresholds.critical_bad_channels,
                    message=f"Critical: {bad_channel_count} bad channels detected",
                )
            )
        elif bad_channel_count > self.thresholds.max_bad_channels:
            alerts.append(
                QualityAlert(
                    timestamp=timestamp,
                    session_id=session_id,
                    alert_type="warning",
                    metric_name="bad_channels",
                    metric_value=bad_channel_count,
                    threshold_value=self.thresholds.max_bad_channels,
                    message=f"Warning: {bad_channel_count} bad channels detected",
                )
            )

        return alerts

    async def _process_alert(self, session_id: str, alert: QualityAlert) -> None:
        """Process a new alert.

        Args:
            session_id: Session identifier
            alert: Alert to process
        """
        # Check if similar alert already active
        existing_alerts = self.active_alerts.get(session_id, [])

        for existing in existing_alerts:
            if (
                existing.metric_name == alert.metric_name
                and existing.alert_type == alert.alert_type
                and not existing.resolved
            ):
                # Update duration of existing alert
                existing.duration_seconds = (
                    alert.timestamp - existing.timestamp
                ).total_seconds()
                return

        # Add new alert
        self.active_alerts[session_id].append(alert)
        self.alert_history.append(alert)

        # Trigger callbacks
        for callback in self.alert_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {str(e)}")

        logger.warning(f"Quality alert for {session_id}: {alert.message}")

    async def _check_resolved_alerts(
        self, session_id: str, metrics: QualityMetrics
    ) -> None:
        """Check if any active alerts are resolved.

        Args:
            session_id: Session identifier
            metrics: Current quality metrics
        """
        if session_id not in self.active_alerts:
            return

        timestamp = datetime.utcnow()

        for alert in self.active_alerts[session_id]:
            if alert.resolved:
                continue

            # Check if condition is resolved
            resolved = False

            if alert.metric_name == "overall_quality":
                resolved = metrics.overall_score >= self.thresholds.min_overall_score
            elif alert.metric_name == "snr":
                resolved = metrics.snr_db >= self.thresholds.min_snr
            elif alert.metric_name == "noise_level":
                resolved = metrics.noise_level_rms <= self.thresholds.max_noise_level
            elif alert.metric_name == "artifacts":
                resolved = (
                    metrics.artifact_percentage
                    <= self.thresholds.max_artifact_percentage
                )
            elif alert.metric_name == "bad_channels":
                bad_count = (
                    len(metrics.flatline_channels)
                    + len(metrics.clipping_channels)
                    + len(metrics.high_impedance_channels)
                )
                resolved = bad_count <= self.thresholds.max_bad_channels

            if resolved:
                alert.resolved = True
                alert.resolved_at = timestamp
                alert.duration_seconds = (timestamp - alert.timestamp).total_seconds()

                logger.info(f"Alert resolved for {session_id}: {alert.metric_name}")

    async def _check_stability(self, session_id: str) -> None:
        """Check if quality is stable.

        Args:
            session_id: Session identifier
        """
        session_info = self.monitoring_sessions.get(session_id)
        if not session_info:
            return

        history = list(session_info["quality_history"])
        if len(history) < 5:  # Need at least 5 samples
            return

        # Check recent quality variance
        recent_scores = [m.overall_score for m in history[-10:]]
        variance = np.var(recent_scores)

        is_stable = variance < self.thresholds.max_quality_variance

        if is_stable and not session_info["is_stable"]:
            # Became stable
            session_info["is_stable"] = True
            session_info["stable_since"] = datetime.utcnow()
            logger.info(f"Quality became stable for session {session_id}")

        elif not is_stable and session_info["is_stable"]:
            # Lost stability
            session_info["is_stable"] = False
            session_info["stable_since"] = None
            logger.warning(f"Quality became unstable for session {session_id}")

    def _initialize_trends(self, session_id: str) -> None:
        """Initialize quality trends for a session.

        Args:
            session_id: Session identifier
        """
        self.trends[session_id] = {
            "overall_quality": QualityTrend("overall_quality", 60.0),
            "snr": QualityTrend("snr", 60.0),
            "noise_level": QualityTrend("noise_level", 60.0),
            "artifact_rate": QualityTrend("artifact_rate", 60.0),
        }

    async def _update_trends(self, session_id: str, metrics: QualityMetrics) -> None:
        """Update quality trends with new metrics.

        Args:
            session_id: Session identifier
            metrics: Quality metrics
        """
        if session_id not in self.trends:
            return

        timestamp = datetime.utcnow()
        session_trends = self.trends[session_id]

        # Update each trend
        session_trends["overall_quality"].add_value(metrics.overall_score, timestamp)
        session_trends["snr"].add_value(metrics.snr_db, timestamp)
        session_trends["noise_level"].add_value(metrics.noise_level_rms, timestamp)
        session_trends["artifact_rate"].add_value(
            metrics.artifact_percentage, timestamp
        )

    def _get_stable_duration(self, session_id: str) -> float:
        """Get duration of stable quality.

        Args:
            session_id: Session identifier

        Returns:
            Stable duration in seconds
        """
        session_info = self.monitoring_sessions.get(session_id)
        if not session_info or not session_info["is_stable"]:
            return 0.0

        if session_info["stable_since"]:
            return (datetime.utcnow() - session_info["stable_since"]).total_seconds()

        return 0.0

    def _generate_recommendations(self, session_id: str) -> List[str]:
        """Generate quality improvement recommendations.

        Args:
            session_id: Session identifier

        Returns:
            List of recommendations
        """
        recommendations = []

        # Get active alerts
        alerts = self.active_alerts.get(session_id, [])

        # Check for specific issues
        has_noise_issue = any(a.metric_name == "noise_level" for a in alerts)
        has_snr_issue = any(a.metric_name == "snr" for a in alerts)
        has_artifact_issue = any(a.metric_name == "artifacts" for a in alerts)
        has_channel_issue = any(a.metric_name == "bad_channels" for a in alerts)

        if has_noise_issue:
            recommendations.append("Check electrode connections and grounding")
            recommendations.append("Move away from electrical interference sources")
            recommendations.append("Enable additional filtering if available")

        if has_snr_issue:
            recommendations.append("Verify electrode impedances")
            recommendations.append("Apply conductive gel if using dry electrodes")
            recommendations.append("Check for loose connections")

        if has_artifact_issue:
            recommendations.append("Minimize subject movement")
            recommendations.append("Check for muscle tension")
            recommendations.append("Ensure comfortable electrode placement")

        if has_channel_issue:
            recommendations.append("Reconnect or replace problematic electrodes")
            recommendations.append("Clean electrode sites")
            recommendations.append("Consider using channel interpolation")

        if not alerts:
            recommendations.append("Signal quality is good - maintain current setup")

        return recommendations

    def update_thresholds(self, params: Dict[str, Any]) -> None:
        """Update quality thresholds.

        Args:
            params: Threshold parameters to update
        """
        for key, value in params.items():
            if hasattr(self.thresholds, key):
                setattr(self.thresholds, key, value)

        logger.info(f"Updated quality thresholds: {params}")
