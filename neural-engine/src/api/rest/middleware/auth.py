"""Authentication middleware for API security."""

from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
from typing import Optional, Dict, Any
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Configuration (should come from environment)
SECRET_KEY = "your-secret-key-here"  # TODO: Load from environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class AuthMiddleware(BaseHTTPMiddleware):
    """JWT authentication middleware."""

    # Public endpoints that don't require authentication
    PUBLIC_ENDPOINTS = {
        "/",
        "/health",
        "/api/docs",
        "/api/redoc",
        "/api/openapi.json",
        "/api/v2",
    }

    async def dispatch(self, request: Request, call_next):
        """Process request with authentication check."""
        # Skip auth for public endpoints
        if request.url.path in self.PUBLIC_ENDPOINTS:
            return await call_next(request)

        # Skip auth for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        # Extract and verify token
        try:
            token = self._extract_token(request)
            if token:
                payload = self._verify_token(token)
                request.state.user = payload
            else:
                # No token provided for protected endpoint
                if not request.url.path.startswith("/graphql"):
                    raise HTTPException(
                        status_code=401,
                        detail="Authentication required",
                        headers={"WWW-Authenticate": "Bearer"},
                    )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return await call_next(request)

    def _extract_token(self, request: Request) -> Optional[str]:
        """Extract JWT token from request."""
        # Check Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header:
            try:
                scheme, token = auth_header.split()
                if scheme.lower() == "bearer":
                    return token
            except ValueError:
                pass

        # Check query parameter (for WebSocket connections)
        token = request.query_params.get("token")
        if token:
            return token

        # Check cookie
        token = request.cookies.get("access_token")
        if token:
            return token

        return None

    def _verify_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError as e:
            logger.error(f"JWT verification failed: {e}")
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )


class JWTBearer(HTTPBearer):
    """JWT Bearer token dependency for FastAPI."""

    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[Dict[str, Any]]:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme"
                )
            payload = self.verify_jwt(credentials.credentials)
            if not payload:
                raise HTTPException(
                    status_code=403, detail="Invalid token or expired token"
                )
            return payload
        return None

    def verify_jwt(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.

    Args:
        data: Token payload
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(request: Request) -> Dict[str, Any]:
    """
    Get current user from request state.

    Args:
        request: FastAPI request

    Returns:
        User information from JWT

    Raises:
        HTTPException: If user not authenticated
    """
    if not hasattr(request.state, "user"):
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return request.state.user


async def check_permission(
    user: Dict[str, Any], permission: str, resource_id: str = None
) -> bool:
    """
    Check if user has required permission.

    Args:
        user: User information
        permission: Required permission
        resource_id: Optional resource ID

    Returns:
        True if user has permission
    """
    # Simple role-based check
    user_role = user.get("role", "viewer")
    user_permissions = {
        "admin": ["*"],
        "operator": ["sessions.*", "devices.*", "patients.read", "analysis.*"],
        "researcher": [
            "sessions.read",
            "devices.read",
            "patients.read",
            "analysis.read",
        ],
        "viewer": ["*.read"],
    }

    role_permissions = user_permissions.get(user_role, [])

    # Check for wildcard permission
    if "*" in role_permissions or f"{permission.split('.')[0]}.*" in role_permissions:
        return True

    # Check specific permission
    if permission in role_permissions:
        return True

    # Check wildcard read permission
    if permission.endswith(".read") and "*.read" in role_permissions:
        return True

    return False
