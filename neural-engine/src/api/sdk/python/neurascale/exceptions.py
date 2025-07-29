"""NeuraScale SDK exceptions."""

from typing import Optional, Dict, Any


class NeuraScaleError(Exception):
    """Base exception for NeuraScale SDK."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response


class AuthenticationError(NeuraScaleError):
    """Authentication failed."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class AuthorizationError(NeuraScaleError):
    """Authorization failed."""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status_code=403)


class NotFoundError(NeuraScaleError):
    """Resource not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ValidationError(NeuraScaleError):
    """Validation error."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422)
        self.details = details


class RateLimitError(NeuraScaleError):
    """Rate limit exceeded."""

    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 60):
        super().__init__(message, status_code=429)
        self.retry_after = retry_after


class ServerError(NeuraScaleError):
    """Server error."""

    def __init__(self, message: str = "Internal server error"):
        super().__init__(message, status_code=500)


class ConnectionError(NeuraScaleError):
    """Connection error."""

    def __init__(self, message: str = "Connection failed"):
        super().__init__(message)


class TimeoutError(NeuraScaleError):
    """Request timeout."""

    def __init__(self, message: str = "Request timeout"):
        super().__init__(message)
