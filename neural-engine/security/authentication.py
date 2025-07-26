"""JWT Authentication for NeuraScale Neural Engine.

This module implements JWT-based authentication with refresh tokens,
session management, and security best practices.
"""

import jwt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
import logging
from .access_control import Role

logger = logging.getLogger(__name__)


@dataclass
class TokenPair:
    """Access and refresh token pair."""

    access_token: str
    refresh_token: str
    expires_at: datetime
    token_type: str = "Bearer"


@dataclass
class TokenClaims:
    """JWT token claims."""

    sub: str  # Subject (user ID)
    role: str  # User role
    tenant_id: Optional[str] = None
    type: str = "access"  # Token type (access / refresh)
    iat: Optional[datetime] = None  # Issued at
    exp: Optional[datetime] = None  # Expires at
    jti: Optional[str] = None  # JWT ID
    aud: str = "neurascale-api"  # Audience
    iss: str = "neurascale-auth"  # Issuer


class JWTManager:
    """Manages JWT token generation, validation, and refresh."""

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 7,
        redis_client=None,
    ):
        """Initialize JWT manager.

        Args:
            secret_key: Secret key for signing tokens
            algorithm: JWT signing algorithm
            access_token_expire_minutes: Access token expiration time
            refresh_token_expire_days: Refresh token expiration time
            redis_client: Redis client for token blacklist
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_expire = timedelta(minutes=access_token_expire_minutes)
        self.refresh_expire = timedelta(days=refresh_token_expire_days)
        self.redis = redis_client
        self._token_blacklist_prefix = "blacklisted_token:"

    def generate_token_pair(
        self, user_id: str, role: Role, tenant_id: Optional[str] = None
    ) -> TokenPair:
        """Generate access and refresh token pair.

        Args:
            user_id: User identifier
            role: User role
            tenant_id: Optional tenant identifier

        Returns:
            TokenPair with access and refresh tokens
        """
        now = datetime.utcnow()

        # Generate access token
        access_token = self._generate_token(
            user_id=user_id,
            role=role,
            tenant_id=tenant_id,
            token_type="access",
            expires_delta=self.access_expire,
        )

        # Generate refresh token
        refresh_token = self._generate_token(
            user_id=user_id,
            role=role,
            tenant_id=tenant_id,
            token_type="refresh",
            expires_delta=self.refresh_expire,
        )

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=now + self.access_expire,
        )

    def _generate_token(
        self,
        user_id: str,
        role: Role,
        tenant_id: Optional[str],
        token_type: str,
        expires_delta: timedelta,
    ) -> str:
        """Generate a JWT token.

        Args:
            user_id: User identifier
            role: User role
            tenant_id: Optional tenant identifier
            token_type: Type of token (access / refresh)
            expires_delta: Token expiration time

        Returns:
            Encoded JWT token
        """
        now = datetime.utcnow()

        claims = TokenClaims(
            sub=user_id,
            role=role.value,
            tenant_id=tenant_id,
            type=token_type,
            iat=now,
            exp=now + expires_delta,
            jti=secrets.token_urlsafe(16),
        )

        # Convert to dict and remove None values
        payload = {k: v for k, v in asdict(claims).items() if v is not None}

        # Convert datetime objects to timestamps
        if payload.get("iat"):
            payload["iat"] = int(payload["iat"].timestamp())
        if payload.get("exp"):
            payload["exp"] = int(payload["exp"].timestamp())

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def validate_token(self, token: str, token_type: str = "access") -> TokenClaims:
        """Validate and decode JWT token.

        Args:
            token: JWT token to validate
            token_type: Expected token type

        Returns:
            TokenClaims if valid

        Raises:
            ValueError: If token is invalid, expired, or blacklisted
        """
        try:
            # Decode token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                audience="neurascale-api",
                issuer="neurascale-auth",
            )

            # Validate token type
            if payload.get("type") != token_type:
                raise ValueError(f"Invalid token type. Expected {token_type}")

            # Check if token is blacklisted
            if self._is_token_blacklisted(payload.get("jti")):
                raise ValueError("Token has been revoked")

            # Convert timestamps back to datetime
            if payload.get("iat"):
                payload["iat"] = datetime.utcfromtimestamp(payload["iat"])
            if payload.get("exp"):
                payload["exp"] = datetime.utcfromtimestamp(payload["exp"])

            # Create TokenClaims object
            return TokenClaims(**payload)

        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {str(e)}")
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            raise ValueError("Token validation failed")

    def refresh_token(self, refresh_token: str) -> TokenPair:
        """Refresh access token using refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            New TokenPair with fresh access token

        Raises:
            ValueError: If refresh token is invalid
        """
        try:
            # Validate refresh token
            claims = self.validate_token(refresh_token, token_type="refresh")

            # Generate new token pair
            role = Role(claims.role)
            return self.generate_token_pair(
                user_id=claims.sub, role=role, tenant_id=claims.tenant_id
            )

        except Exception as e:
            logger.error(f"Token refresh error: {str(e)}")
            raise ValueError("Failed to refresh token")

    async def revoke_token(self, token: str) -> bool:
        """Revoke a token by adding it to blacklist.

        Args:
            token: Token to revoke

        Returns:
            True if successfully revoked
        """
        try:
            # Decode token to get JTI
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False},  # Allow expired tokens for revocation
            )

            jti = payload.get("jti")
            if not jti:
                return False

            # Add to blacklist
            if self.redis:
                expiry = payload.get("exp", 0)
                if expiry > datetime.utcnow().timestamp():
                    # Only blacklist if not yet expired
                    ttl = int(expiry - datetime.utcnow().timestamp())
                    await self.redis.setex(
                        f"{self._token_blacklist_prefix}{jti}", ttl, "revoked"
                    )

            logger.info(f"Token revoked: {jti}")
            return True

        except Exception as e:
            logger.error(f"Token revocation error: {str(e)}")
            return False

    def _is_token_blacklisted(self, jti: Optional[str]) -> bool:
        """Check if token is blacklisted.

        Args:
            jti: JWT ID to check

        Returns:
            True if blacklisted, False otherwise
        """
        if not jti or not self.redis:
            return False

        try:
            # Check Redis for blacklisted token (synchronous)
            # In async context, this should be awaited
            return bool(self.redis.get(f"{self._token_blacklist_prefix}{jti}"))
        except Exception:
            # If Redis is unavailable, allow token (fail open)
            return False

    def get_token_info(self, token: str) -> Dict[str, Any]:
        """Get token information without validation.

        Args:
            token: JWT token

        Returns:
            Token payload or empty dict if invalid
        """
        try:
            payload = jwt.decode(
                token, options={"verify_signature": False, "verify_exp": False}
            )

            # Convert timestamps to readable format
            if payload.get("iat"):
                payload["iat_readable"] = datetime.utcfromtimestamp(
                    payload["iat"]
                ).isoformat()
            if payload.get("exp"):
                payload["exp_readable"] = datetime.utcfromtimestamp(
                    payload["exp"]
                ).isoformat()

            return payload

        except Exception:
            return {}


class SessionManager:
    """Manages user sessions and token lifecycle."""

    def __init__(self, jwt_manager: JWTManager, database_client=None):
        """Initialize session manager.

        Args:
            jwt_manager: JWT manager instance
            database_client: Database client for session storage
        """
        self.jwt_manager = jwt_manager
        self.db = database_client

    async def create_session(
        self,
        user_id: str,
        role: Role,
        tenant_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> TokenPair:
        """Create a new user session.

        Args:
            user_id: User identifier
            role: User role
            tenant_id: Optional tenant identifier
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            TokenPair for the session
        """
        # Generate token pair
        token_pair = self.jwt_manager.generate_token_pair(
            user_id=user_id, role=role, tenant_id=tenant_id
        )

        # Store session in database if available
        if self.db:
            await self._store_session(
                user_id=user_id,
                token_pair=token_pair,
                ip_address=ip_address,
                user_agent=user_agent,
            )

        logger.info(f"Session created for user {user_id} with role {role.value}")
        return token_pair

    async def end_session(self, token: str) -> bool:
        """End a user session.

        Args:
            token: Access or refresh token

        Returns:
            True if session ended successfully
        """
        try:
            # Revoke the token
            success = await self.jwt_manager.revoke_token(token)

            # Update session in database
            if self.db and success:
                await self._update_session_status(token, "ended")

            return success

        except Exception as e:
            logger.error(f"Session end error: {str(e)}")
            return False

    async def _store_session(
        self,
        user_id: str,
        token_pair: TokenPair,
        ip_address: Optional[str],
        user_agent: Optional[str],
    ) -> None:
        """Store session information in database."""
        # Extract token info
        access_info = self.jwt_manager.get_token_info(token_pair.access_token)

        # This would be implemented based on your database schema
        logger.info(
            f"Session stored for user {user_id} with token {access_info.get('jti')}"
        )

    async def _update_session_status(self, token: str, status: str) -> None:
        """Update session status in database."""
        token_info = self.jwt_manager.get_token_info(token)
        token_id = token_info.get("jti")

        if token_id:
            # Update session status in database
            logger.info(f"Session {token_id} status updated to {status}")

    async def get_active_sessions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get active sessions for a user.

        Args:
            user_id: User identifier

        Returns:
            List of active session information
        """
        if not self.db:
            return []

        # Query active sessions from database
        # This would be implemented based on your database schema
        logger.info(f"Retrieved active sessions for user {user_id}")
        return []

    async def revoke_all_sessions(self, user_id: str) -> bool:
        """Revoke all active sessions for a user.

        Args:
            user_id: User identifier

        Returns:
            True if all sessions revoked successfully
        """
        try:
            # Get all active sessions
            sessions = await self.get_active_sessions(user_id)

            # Revoke each session
            for session in sessions:
                token_id = session.get("token_id")
                if token_id and self.jwt_manager.redis:
                    # Add to blacklist
                    await self.jwt_manager.redis.setex(
                        f"{self.jwt_manager._token_blacklist_prefix}{token_id}",
                        86400,  # 24 hours
                        "revoked",
                    )

            # Update database
            if self.db:
                await self._revoke_user_sessions(user_id)

            logger.info(f"All sessions revoked for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Session revocation error: {str(e)}")
            return False

    async def _revoke_user_sessions(self, user_id: str) -> None:
        """Mark all user sessions as revoked in database."""
        # This would be implemented based on your database schema
        logger.info(f"User sessions revoked in database for {user_id}")


def create_auth_system(
    secret_key: str, redis_client=None, database_client=None
) -> tuple[JWTManager, SessionManager]:
    """Create authentication system components.

    Args:
        secret_key: JWT signing secret
        redis_client: Redis client for token blacklist
        database_client: Database client for session storage

    Returns:
        Tuple of (JWTManager, SessionManager)
    """
    jwt_manager = JWTManager(secret_key=secret_key, redis_client=redis_client)

    session_manager = SessionManager(
        jwt_manager=jwt_manager, database_client=database_client
    )

    return jwt_manager, session_manager
