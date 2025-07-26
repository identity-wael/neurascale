"""Neural Ledger integration for security audit logging.

This module integrates the security system with the Neural Ledger
for immutable audit trails of all security events.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging

from ..ledger.neural_ledger import NeuralLedger, EventType
from ..ledger.event_schema import NeuralEvent
from .access_control import Role, Permission

logger = logging.getLogger(__name__)


class SecurityEventType(Enum):
    """Types of security events for audit logging."""

    AUTH_SUCCESS = "auth_success"
    AUTH_FAILURE = "auth_failure"
    AUTH_LOGOUT = "auth_logout"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_DENIED = "permission_denied"
    RESOURCE_ACCESS_GRANTED = "resource_access_granted"
    RESOURCE_ACCESS_DENIED = "resource_access_denied"
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REVOKED = "role_revoked"
    CONSENT_GRANTED = "consent_granted"
    CONSENT_WITHDRAWN = "consent_withdrawn"
    DATA_ANONYMIZED = "data_anonymized"
    PHI_ACCESS = "phi_access"
    TOKEN_ISSUED = "token_issued"
    TOKEN_REVOKED = "token_revoked"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SECURITY_VIOLATION = "security_violation"


@dataclass
class SecurityEvent:
    """Security event for audit logging."""

    event_type: SecurityEventType
    user_id: str
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    resource_id: Optional[str] = None
    resource_type: Optional[str] = None
    permission: Optional[str] = None
    role: Optional[str] = None
    success: bool = True
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SecurityAuditLogger:
    """Security audit logger with Neural Ledger integration."""

    def __init__(self, neural_ledger: Optional[NeuralLedger] = None):
        """Initialize security audit logger.

        Args:
            neural_ledger: Neural Ledger instance for persistent storage
        """
        self.neural_ledger = neural_ledger
        self._event_buffer: List[SecurityEvent] = []
        self._buffer_size = 100
        self._flush_interval = 60  # seconds
        self._last_flush = datetime.utcnow()

    async def log_authentication_success(
        self,
        user_id: str,
        role: Role,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> None:
        """Log successful authentication event.

        Args:
            user_id: User identifier
            role: User role
            ip_address: Client IP address
            user_agent: Client user agent
            session_id: Session identifier
        """
        event = SecurityEvent(
            event_type=SecurityEventType.AUTH_SUCCESS,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            role=role.value,
            success=True,
            metadata={"authentication_method": "jwt", "role": role.value},
        )

        await self._log_event(event)

    async def log_authentication_failure(
        self,
        user_id: str,
        reason: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """Log failed authentication event.

        Args:
            user_id: User identifier (may be invalid)
            reason: Failure reason
            ip_address: Client IP address
            user_agent: Client user agent
        """
        event = SecurityEvent(
            event_type=SecurityEventType.AUTH_FAILURE,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            reason=reason,
            metadata={"authentication_method": "jwt", "failure_reason": reason},
        )

        await self._log_event(event)

    async def log_authorization_check(
        self,
        user_id: str,
        permission: Permission,
        granted: bool,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> None:
        """Log authorization check event.

        Args:
            user_id: User identifier
            permission: Permission being checked
            granted: Whether permission was granted
            resource_type: Type of resource
            resource_id: Resource identifier
            reason: Reason for denial (if applicable)
        """
        event_type = (
            SecurityEventType.PERMISSION_GRANTED
            if granted
            else SecurityEventType.PERMISSION_DENIED
        )

        event = SecurityEvent(
            event_type=event_type,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            permission=permission.value,
            resource_type=resource_type,
            resource_id=resource_id,
            success=granted,
            reason=reason,
            metadata={
                "permission_check": permission.value,
                "resource_type": resource_type,
                "resource_id": resource_id,
            },
        )

        await self._log_event(event)

    async def log_resource_access(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        operation: str,
        granted: bool,
        role: Optional[Role] = None,
        reason: Optional[str] = None,
    ) -> None:
        """Log resource access event.

        Args:
            user_id: User identifier
            resource_type: Type of resource
            resource_id: Resource identifier
            operation: Operation performed (read, write, delete, etc.)
            granted: Whether access was granted
            role: User role
            reason: Reason for denial (if applicable)
        """
        event_type = (
            SecurityEventType.RESOURCE_ACCESS_GRANTED
            if granted
            else SecurityEventType.RESOURCE_ACCESS_DENIED
        )

        event = SecurityEvent(
            event_type=event_type,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            resource_type=resource_type,
            resource_id=resource_id,
            role=role.value if role else None,
            success=granted,
            reason=reason,
            metadata={
                "operation": operation,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "user_role": role.value if role else None,
            },
        )

        await self._log_event(event)

    async def log_consent_event(
        self,
        patient_id: str,
        consent_type: str,
        status: str,
        purpose: str,
        granted_by: Optional[str] = None,
    ) -> None:
        """Log consent management event.

        Args:
            patient_id: Patient identifier
            consent_type: Type of consent
            status: Consent status (granted, withdrawn, etc.)
            purpose: Purpose of consent
            granted_by: User who granted/withdrew consent
        """
        event_type = (
            SecurityEventType.CONSENT_GRANTED
            if status == "granted"
            else SecurityEventType.CONSENT_WITHDRAWN
        )

        event = SecurityEvent(
            event_type=event_type,
            user_id=granted_by or patient_id,
            timestamp=datetime.utcnow(),
            resource_id=patient_id,
            resource_type="patient_data",
            success=True,
            metadata={
                "patient_id": patient_id,
                "consent_type": consent_type,
                "consent_status": status,
                "purpose": purpose,
                "granted_by": granted_by,
            },
        )

        await self._log_event(event)

    async def log_data_anonymization(
        self,
        user_id: str,
        data_type: str,
        original_records: int,
        anonymized_records: int,
        purpose: str,
    ) -> None:
        """Log data anonymization event.

        Args:
            user_id: User performing anonymization
            data_type: Type of data being anonymized
            original_records: Number of original records
            anonymized_records: Number of anonymized records
            purpose: Purpose of anonymization
        """
        event = SecurityEvent(
            event_type=SecurityEventType.DATA_ANONYMIZED,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            resource_type="neural_data",
            success=True,
            metadata={
                "data_type": data_type,
                "original_records": original_records,
                "anonymized_records": anonymized_records,
                "purpose": purpose,
                "anonymization_method": "hipaa_safe_harbor",
            },
        )

        await self._log_event(event)

    async def log_phi_access(
        self,
        user_id: str,
        patient_id: str,
        data_type: str,
        operation: str,
        anonymized: bool,
        role: Optional[Role] = None,
    ) -> None:
        """Log PHI access event.

        Args:
            user_id: User accessing PHI
            patient_id: Patient whose data is accessed
            data_type: Type of data accessed
            operation: Operation performed
            anonymized: Whether data was anonymized
            role: User role
        """
        event = SecurityEvent(
            event_type=SecurityEventType.PHI_ACCESS,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            resource_id=patient_id,
            resource_type="phi_data",
            role=role.value if role else None,
            success=True,
            metadata={
                "patient_id": patient_id,
                "data_type": data_type,
                "operation": operation,
                "anonymized": anonymized,
                "user_role": role.value if role else None,
                "hipaa_covered": True,
            },
        )

        await self._log_event(event)

    async def log_token_event(
        self,
        user_id: str,
        token_type: str,
        action: str,
        token_id: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> None:
        """Log token lifecycle event.

        Args:
            user_id: User identifier
            token_type: Type of token (access, refresh)
            action: Action performed (issued, revoked, refreshed)
            token_id: Token identifier
            expires_at: Token expiration time
        """
        event_type = (
            SecurityEventType.TOKEN_ISSUED
            if action == "issued"
            else SecurityEventType.TOKEN_REVOKED
        )

        event = SecurityEvent(
            event_type=event_type,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            session_id=token_id,
            success=True,
            metadata={
                "token_type": token_type,
                "action": action,
                "token_id": token_id,
                "expires_at": expires_at.isoformat() if expires_at else None,
            },
        )

        await self._log_event(event)

    async def log_rate_limit_exceeded(
        self,
        identifier: str,
        ip_address: Optional[str] = None,
        user_id: Optional[str] = None,
        endpoint: Optional[str] = None,
    ) -> None:
        """Log rate limit exceeded event.

        Args:
            identifier: Rate limit identifier
            ip_address: Client IP address
            user_id: User identifier (if available)
            endpoint: API endpoint
        """
        event = SecurityEvent(
            event_type=SecurityEventType.RATE_LIMIT_EXCEEDED,
            user_id=user_id or "anonymous",
            timestamp=datetime.utcnow(),
            ip_address=ip_address,
            success=False,
            reason="Rate limit exceeded",
            metadata={
                "identifier": identifier,
                "endpoint": endpoint,
                "violation_type": "rate_limit",
            },
        )

        await self._log_event(event)

    async def log_security_violation(
        self,
        user_id: str,
        violation_type: str,
        details: Dict[str, Any],
        ip_address: Optional[str] = None,
        severity: str = "medium",
    ) -> None:
        """Log security violation event.

        Args:
            user_id: User identifier
            violation_type: Type of violation
            details: Violation details
            ip_address: Client IP address
            severity: Severity level (low, medium, high, critical)
        """
        event = SecurityEvent(
            event_type=SecurityEventType.SECURITY_VIOLATION,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            ip_address=ip_address,
            success=False,
            reason=violation_type,
            metadata={
                "violation_type": violation_type,
                "severity": severity,
                "details": details,
            },
        )

        await self._log_event(event)

    async def _log_event(self, event: SecurityEvent) -> None:
        """Log security event to buffer and Neural Ledger.

        Args:
            event: Security event to log
        """
        # Add to buffer
        self._event_buffer.append(event)

        # Log immediately to standard logger
        logger.info(
            f"SECURITY_EVENT: {event.event_type.value} - User: {event.user_id} - Success: {event.success}"
        )

        # Log to Neural Ledger if available
        if self.neural_ledger:
            try:
                await self._log_to_neural_ledger(event)
            except Exception as e:
                logger.error(f"Failed to log security event to Neural Ledger: {str(e)}")

        # Check if buffer needs flushing
        await self._check_buffer_flush()

    async def _log_to_neural_ledger(self, event: SecurityEvent) -> None:
        """Log security event to Neural Ledger.

        Args:
            event: Security event to log
        """
        # Convert security event to Neural Ledger event
        neural_event = NeuralEvent(
            event_type=EventType.SYSTEM_SECURITY,
            timestamp=event.timestamp,
            user_id=event.user_id,
            session_id=event.session_id or "security_audit",
            metadata={
                "security_event_type": event.event_type.value,
                "ip_address": event.ip_address,
                "user_agent": event.user_agent,
                "resource_type": event.resource_type,
                "resource_id": event.resource_id,
                "permission": event.permission,
                "role": event.role,
                "success": event.success,
                "reason": event.reason,
                **(event.metadata or {}),
            },
        )

        # Submit to Neural Ledger
        await self.neural_ledger.submit_event(neural_event)

    async def _check_buffer_flush(self) -> None:
        """Check if buffer should be flushed."""
        now = datetime.utcnow()
        time_since_flush = (now - self._last_flush).total_seconds()

        if (
            len(self._event_buffer) >= self._buffer_size
            or time_since_flush >= self._flush_interval
        ):
            await self.flush_buffer()

    async def flush_buffer(self) -> None:
        """Flush event buffer to persistent storage."""
        if not self._event_buffer:
            return

        events_to_flush = self._event_buffer.copy()
        self._event_buffer.clear()
        self._last_flush = datetime.utcnow()

        # Additional processing if needed (e.g., batch writes to database)
        logger.info(f"Flushed {len(events_to_flush)} security events from buffer")

    async def get_security_events(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[SecurityEventType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[SecurityEvent]:
        """Retrieve security events from audit log.

        Args:
            user_id: Filter by user ID
            event_type: Filter by event type
            start_time: Start time for filter
            end_time: End time for filter
            limit: Maximum number of events to return

        Returns:
            List of security events
        """
        if not self.neural_ledger:
            # Return from buffer if Neural Ledger not available
            filtered_events = self._event_buffer

            if user_id:
                filtered_events = [e for e in filtered_events if e.user_id == user_id]
            if event_type:
                filtered_events = [
                    e for e in filtered_events if e.event_type == event_type
                ]
            if start_time:
                filtered_events = [
                    e for e in filtered_events if e.timestamp >= start_time
                ]
            if end_time:
                filtered_events = [
                    e for e in filtered_events if e.timestamp <= end_time
                ]

            return filtered_events[:limit]

        # Query Neural Ledger for events
        try:
            # This would implement querying the Neural Ledger
            # for security events based on the provided filters
            logger.info(f"Querying security events: user={user_id}, type={event_type}")
            return []
        except Exception as e:
            logger.error(f"Failed to query security events: {str(e)}")
            return []

    async def generate_security_report(
        self,
        user_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Generate security audit report.

        Args:
            user_id: Filter by user ID
            start_time: Start time for report
            end_time: End time for report

        Returns:
            Security report dictionary
        """
        events = await self.get_security_events(
            user_id=user_id, start_time=start_time, end_time=end_time, limit=10000
        )

        # Generate statistics
        total_events = len(events)
        auth_failures = len(
            [e for e in events if e.event_type == SecurityEventType.AUTH_FAILURE]
        )
        permission_denials = len(
            [e for e in events if e.event_type == SecurityEventType.PERMISSION_DENIED]
        )
        security_violations = len(
            [e for e in events if e.event_type == SecurityEventType.SECURITY_VIOLATION]
        )

        # Event type distribution
        event_types = {}
        for event in events:
            event_types[event.event_type.value] = (
                event_types.get(event.event_type.value, 0) + 1
            )

        # User activity
        user_activity = {}
        for event in events:
            user_activity[event.user_id] = user_activity.get(event.user_id, 0) + 1

        return {
            "report_period": {
                "start_time": start_time.isoformat() if start_time else None,
                "end_time": end_time.isoformat() if end_time else None,
            },
            "summary": {
                "total_events": total_events,
                "auth_failures": auth_failures,
                "permission_denials": permission_denials,
                "security_violations": security_violations,
                "failure_rate": (auth_failures + permission_denials)
                / max(total_events, 1)
                * 100,
            },
            "event_distribution": event_types,
            "top_users": dict(
                sorted(user_activity.items(), key=lambda x: x[1], reverse=True)[:10]
            ),
            "generated_at": datetime.utcnow().isoformat(),
        }


def create_security_audit_system(
    neural_ledger: Optional[NeuralLedger] = None,
) -> SecurityAuditLogger:
    """Create security audit system with Neural Ledger integration.

    Args:
        neural_ledger: Neural Ledger instance

    Returns:
        Configured SecurityAuditLogger
    """
    return SecurityAuditLogger(neural_ledger=neural_ledger)
