"""Security middleware for NeuraScale Neural Engine APIs.

This module provides comprehensive security middleware including authentication,
authorization, rate limiting, and security headers for FastAPI applications.
"""

import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Callable, Awaitable

from fastapi import Request, Response, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .authentication import JWTManager
from .access_control import RBACManager, Role, Permission, UserContext
from .hipaa_compliance import HIPAAComplianceManager

logger = logging.getLogger(__name__)


class SecurityHeaders:
    """Security headers for HTTP responses."""

    @staticmethod
    def get_headers() -> Dict[str, str]:
        """Get security headers for responses."""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "camera=(), microphone=(), location=()",
        }


class RateLimiter:
    """Rate limiting middleware with Redis backend."""

    def __init__(
        self, redis_client, default_limit: int = 100, window_seconds: int = 60
    ):
        """Initialize rate limiter.

        Args:
            redis_client: Redis client for storing rate limit data
            default_limit: Default requests per window
            window_seconds: Time window in seconds
        """
        self.redis = redis_client
        self.default_limit = default_limit
        self.window = window_seconds

        # Role-based rate limits
        self.role_limits = {
            Role.DEVICE: {"requests": 1000, "window": 60},  # 1000/min
            Role.SERVICE: {"requests": 10000, "window": 60},  # 10k/min
            Role.ADMIN: {"requests": 500, "window": 60},  # 500/min
            Role.CLINICIAN: {"requests": 300, "window": 60},  # 300/min
            Role.RESEARCHER: {"requests": 100, "window": 60},  # 100/min
            Role.PATIENT: {"requests": 60, "window": 60},  # 60/min
        }

    async def check_rate_limit(
        self, identifier: str, role: Optional[Role] = None
    ) -> bool:
        """Check if request is within rate limits.

        Args:
            identifier: Client identifier (user_id, IP, etc.)
            role: User role for role-based limits

        Returns:
            True if within limits, False if rate limited
        """
        if not self.redis:
            return True  # Allow if Redis unavailable

        # Get limits for role
        limits = self.role_limits.get(
            role, {"requests": self.default_limit, "window": self.window}
        )

        key = f"rate_limit:{identifier}"

        try:
            # Sliding window rate limiting
            current_time = int(time.time())
            window_start = current_time - limits["window"]

            # Remove old entries
            await self.redis.zremrangebyscore(key, 0, window_start)

            # Count current requests
            current_count = await self.redis.zcard(key)

            if current_count >= limits["requests"]:
                return False

            # Add current request
            await self.redis.zadd(key, {str(current_time): current_time})
            await self.redis.expire(key, limits["window"])

            return True

        except Exception as e:
            logger.error(f"Rate limiting error: {str(e)}")
            return True  # Fail open

    async def get_rate_limit_info(
        self, identifier: str, role: Optional[Role] = None
    ) -> Dict[str, Any]:
        """Get rate limit information for client.

        Args:
            identifier: Client identifier
            role: User role

        Returns:
            Rate limit information
        """
        if not self.redis:
            return {
                "limit": self.default_limit,
                "remaining": self.default_limit,
                "reset": time.time() + self.window,
            }

        limits = self.role_limits.get(
            role, {"requests": self.default_limit, "window": self.window}
        )

        key = f"rate_limit:{identifier}"
        current_time = int(time.time())
        window_start = current_time - limits["window"]

        try:
            # Remove old entries
            await self.redis.zremrangebyscore(key, 0, window_start)

            # Count current requests
            current_count = await self.redis.zcard(key)
            remaining = max(0, limits["requests"] - current_count)
            reset_time = current_time + limits["window"]

            return {
                "limit": limits["requests"],
                "remaining": remaining,
                "reset": reset_time,
                "window": limits["window"],
            }

        except Exception as e:
            logger.error(f"Rate limit info error: {str(e)}")
            return {
                "limit": limits["requests"],
                "remaining": limits["requests"],
                "reset": current_time + limits["window"],
            }


class SecurityMiddleware(BaseHTTPMiddleware):
    """Main security middleware for FastAPI applications."""

    def __init__(
        self,
        app,
        jwt_manager: JWTManager,
        rbac_manager: RBACManager,
        rate_limiter: Optional[RateLimiter] = None,
        hipaa_manager: Optional[HIPAAComplianceManager] = None,
    ):
        """Initialize security middleware.

        Args:
            app: FastAPI application
            jwt_manager: JWT manager for authentication
            rbac_manager: RBAC manager for authorization
            rate_limiter: Optional rate limiter
            hipaa_manager: Optional HIPAA compliance manager
        """
        super().__init__(app)
        self.jwt_manager = jwt_manager
        self.rbac_manager = rbac_manager
        self.rate_limiter = rate_limiter
        self.hipaa_manager = hipaa_manager

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        """Process request through security middleware.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response with security headers
        """
        start_time = time.time()

        # Skip security for health checks and docs
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            response = await call_next(request)
            return self._add_security_headers(response)

        try:
            # Rate limiting
            if self.rate_limiter:
                client_id = self._get_client_identifier(request)
                if not await self.rate_limiter.check_rate_limit(client_id):
                    return self._create_rate_limit_response(request)

            # Process request
            response = await call_next(request)

            # Add security headers
            response = self._add_security_headers(response)

            # Log request
            self._log_request(request, response, time.time() - start_time)

            return response

        except Exception as e:
            logger.error(f"Security middleware error: {str(e)}")
            return JSONResponse(
                status_code=500, content={"error": "Internal security error"}
            )

    def _get_client_identifier(self, request: Request) -> str:
        """Get client identifier for rate limiting."""
        # Try to get user ID from token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            token_info = self.jwt_manager.get_token_info(token)
            if token_info.get("sub"):
                return f"user:{token_info['sub']}"

        # Fall back to IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return f"ip:{forwarded_for.split(',')[0].strip()}"

        return f"ip:{request.client.host if request.client else 'unknown'}"

    def _create_rate_limit_response(self, request: Request) -> JSONResponse:
        """Create rate limit exceeded response."""
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later.",
            },
            headers=SecurityHeaders.get_headers(),
        )

    def _add_security_headers(self, response: Response) -> Response:
        """Add security headers to response."""
        headers = SecurityHeaders.get_headers()
        for key, value in headers.items():
            response.headers[key] = value
        return response

    def _log_request(
        self, request: Request, response: Response, duration: float
    ) -> None:
        """Log request for audit purposes."""
        logger.info(
            f"{request.method} {request.url.path} - "
            f"{response.status_code} - {duration:.3f}s - "
            f"{request.client.host if request.client else 'unknown'}"
        )


class AuthenticationDependency:
    """FastAPI dependency for authentication."""

    def __init__(self, jwt_manager: JWTManager):
        """Initialize authentication dependency.

        Args:
            jwt_manager: JWT manager instance
        """
        self.jwt_manager = jwt_manager
        self.bearer = HTTPBearer()

    async def __call__(
        self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ) -> UserContext:
        """Authenticate request and return user context.

        Args:
            credentials: Bearer token credentials

        Returns:
            User context

        Raises:
            HTTPException: If authentication fails
        """
        token = credentials.credentials

        try:
            claims = self.jwt_manager.validate_token(token)

            return UserContext(
                user_id=claims.sub, role=Role(claims.role), tenant_id=claims.tenant_id
            )

        except ValueError as e:
            logger.warning(f"Authentication failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )


class AuthorizationDependency:
    """FastAPI dependency for authorization."""

    def __init__(self, rbac_manager: RBACManager, required_permission: Permission):
        """Initialize authorization dependency.

        Args:
            rbac_manager: RBAC manager instance
            required_permission: Required permission
        """
        self.rbac_manager = rbac_manager
        self.required_permission = required_permission

    async def __call__(self, user_context: UserContext) -> UserContext:
        """Check authorization and return user context.

        Args:
            user_context: User context from authentication

        Returns:
            User context if authorized

        Raises:
            HTTPException: If authorization fails
        """
        if not self.rbac_manager.check_user_permission(
            user_context, self.required_permission
        ):
            logger.warning(
                f"Authorization failed: user {user_context.user_id} "
                f"lacks permission {self.required_permission.value}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {self.required_permission.value}",
            )

        return user_context


class ResourceAccessDependency:
    """FastAPI dependency for resource-specific access control."""

    def __init__(self, rbac_manager: RBACManager, resource_type: str):
        """Initialize resource access dependency.

        Args:
            rbac_manager: RBAC manager instance
            resource_type: Type of resource being accessed
        """
        self.rbac_manager = rbac_manager
        self.resource_type = resource_type

    async def __call__(
        self, resource_id: str, user_context: UserContext
    ) -> UserContext:
        """Check resource access and return user context.

        Args:
            resource_id: Resource identifier
            user_context: User context from authentication

        Returns:
            User context if access granted

        Raises:
            HTTPException: If access denied
        """
        has_access = await self.rbac_manager.check_resource_access(
            user_context.user_id,
            user_context.role,
            self.resource_type,
            resource_id,
            user_context.tenant_id,
        )

        if not has_access:
            logger.warning(
                f"Resource access denied: user {user_context.user_id} "
                f"to {self.resource_type}/{resource_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied to {self.resource_type}/{resource_id}",
            )

        return user_context


def require_auth(jwt_manager: JWTManager):
    """Decorator for requiring authentication."""
    return Depends(AuthenticationDependency(jwt_manager))


def require_permission(rbac_manager: RBACManager, permission: Permission):
    """Decorator for requiring specific permission."""

    def dependency(
        user_context: UserContext = Depends(AuthenticationDependency),
    ) -> UserContext:
        return AuthorizationDependency(rbac_manager, permission)(user_context)

    return Depends(dependency)


def require_resource_access(rbac_manager: RBACManager, resource_type: str):
    """Decorator for requiring resource access."""

    def dependency(
        resource_id: str, user_context: UserContext = Depends(AuthenticationDependency)
    ) -> UserContext:
        return ResourceAccessDependency(rbac_manager, resource_type)(
            resource_id, user_context
        )

    return Depends(dependency)


class AuditLogger:
    """Audit logging for security events."""

    def __init__(self, neural_ledger_client=None):
        """Initialize audit logger.

        Args:
            neural_ledger_client: Neural Ledger client for persistent audit trail
        """
        self.ledger = neural_ledger_client

    async def log_authentication(
        self,
        user_id: str,
        success: bool,
        ip_address: str,
        user_agent: str,
        reason: Optional[str] = None,
    ) -> None:
        """Log authentication event.

        Args:
            user_id: User identifier
            success: Whether authentication succeeded
            ip_address: Client IP address
            user_agent: Client user agent
            reason: Optional failure reason
        """
        event_data = {
            "event_type": "authentication",
            "user_id": user_id,
            "success": success,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "timestamp": datetime.utcnow().isoformat(),
            "reason": reason,
        }

        await self._log_event(event_data)

    async def log_authorization(
        self,
        user_id: str,
        permission: str,
        resource: str,
        granted: bool,
        reason: Optional[str] = None,
    ) -> None:
        """Log authorization event.

        Args:
            user_id: User identifier
            permission: Permission being checked
            resource: Resource being accessed
            granted: Whether access was granted
            reason: Optional denial reason
        """
        event_data = {
            "event_type": "authorization",
            "user_id": user_id,
            "permission": permission,
            "resource": resource,
            "granted": granted,
            "timestamp": datetime.utcnow().isoformat(),
            "reason": reason,
        }

        await self._log_event(event_data)

    async def log_data_access(
        self,
        user_id: str,
        data_type: str,
        operation: str,
        resource_id: str,
        anonymized: bool = False,
    ) -> None:
        """Log data access event.

        Args:
            user_id: User identifier
            data_type: Type of data accessed
            operation: Operation performed (read, write, delete, export)
            resource_id: Resource identifier
            anonymized: Whether data was anonymized
        """
        event_data = {
            "event_type": "data_access",
            "user_id": user_id,
            "data_type": data_type,
            "operation": operation,
            "resource_id": resource_id,
            "anonymized": anonymized,
            "timestamp": datetime.utcnow().isoformat(),
        }

        await self._log_event(event_data)

    async def _log_event(self, event_data: Dict[str, Any]) -> None:
        """Log event to audit trail."""
        # Log to standard logger
        logger.info(f"AUDIT: {event_data}")

        # Log to Neural Ledger if available
        if self.ledger:
            try:
                await self.ledger.log_security_event(event_data)
            except Exception as e:
                logger.error(f"Failed to log to Neural Ledger: {str(e)}")


def create_security_system(
    jwt_manager: JWTManager,
    rbac_manager: RBACManager,
    redis_client=None,
    neural_ledger_client=None,
) -> Dict[str, Any]:
    """Create complete security system.

    Args:
        jwt_manager: JWT manager instance
        rbac_manager: RBAC manager instance
        redis_client: Redis client for rate limiting
        neural_ledger_client: Neural Ledger client for audit logging

    Returns:
        Dictionary with security components
    """
    rate_limiter = RateLimiter(redis_client) if redis_client else None
    audit_logger = AuditLogger(neural_ledger_client)

    return {
        "jwt_manager": jwt_manager,
        "rbac_manager": rbac_manager,
        "rate_limiter": rate_limiter,
        "audit_logger": audit_logger,
        "require_auth": require_auth(jwt_manager),
        "require_permission": lambda perm: require_permission(rbac_manager, perm),
        "require_resource_access": lambda res_type: require_resource_access(
            rbac_manager, res_type
        ),
    }
