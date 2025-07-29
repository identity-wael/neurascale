"""Authentication manager for MCP servers."""

import jwt
import hashlib
import hmac
from typing import Dict, Optional, Any
from datetime import datetime, timedelta


class MCPAuthManager:
    """Handles authentication for MCP server requests."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize authentication manager.
        
        Args:
            config: Authentication configuration
        """
        self.config = config
        self.jwt_secret = config.get("jwt_secret", "default-secret")
        self.jwt_algorithm = config.get("jwt_algorithm", "HS256")
        self.jwt_expiry = config.get("jwt_expiry_hours", 24)
        
        # API keys configuration
        self.api_keys = config.get("api_keys", {})
        self.api_key_salt = config.get("api_key_salt", "neurascale-mcp")
        
        # Session configuration
        self.session_timeout = config.get("session_timeout_minutes", 60)
        self.active_sessions: Dict[str, Dict[str, Any]] = {}

    async def authenticate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Authenticate using API key.
        
        Args:
            api_key: API key to validate
            
        Returns:
            User information if valid, None otherwise
        """
        try:
            # Hash the API key for comparison
            key_hash = self._hash_api_key(api_key)
            
            # Check against stored API keys
            for key_id, key_info in self.api_keys.items():
                if key_info.get("hash") == key_hash:
                    # Check if key is active
                    if not key_info.get("active", True):
                        return None
                    
                    # Check expiration
                    expires_at = key_info.get("expires_at")
                    if expires_at and datetime.fromisoformat(expires_at) < datetime.utcnow():
                        return None
                    
                    # Return user information
                    return {
                        "id": key_info.get("user_id", key_id),
                        "name": key_info.get("user_name", "API User"),
                        "permissions": key_info.get("permissions", []),
                        "auth_method": "api_key",
                        "key_id": key_id
                    }
            
            return None
            
        except Exception:
            return None

    async def authenticate_jwt(self, token: str) -> Optional[Dict[str, Any]]:
        """Authenticate using JWT token.
        
        Args:
            token: JWT token to validate
            
        Returns:
            User information if valid, None otherwise
        """
        try:
            # Decode JWT token
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.jwt_algorithm]
            )
            
            # Check expiration
            exp = payload.get("exp")
            if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
                return None
            
            # Return user information
            return {
                "id": payload.get("sub"),
                "name": payload.get("name"),
                "permissions": payload.get("permissions", []),
                "auth_method": "jwt",
                "token_payload": payload
            }
            
        except jwt.InvalidTokenError:
            return None
        except Exception:
            return None

    async def authenticate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Authenticate using session ID.
        
        Args:
            session_id: Session ID to validate
            
        Returns:
            User information if valid, None otherwise
        """
        session = self.active_sessions.get(session_id)
        if not session:
            return None
        
        # Check session expiration
        expires_at = session.get("expires_at")
        if expires_at and expires_at < datetime.utcnow():
            # Clean up expired session
            del self.active_sessions[session_id]
            return None
        
        # Refresh session expiration
        session["expires_at"] = datetime.utcnow() + timedelta(
            minutes=self.session_timeout
        )
        
        return session.get("user")

    async def create_session(self, user: Dict[str, Any]) -> str:
        """Create a new session for authenticated user.
        
        Args:
            user: User information
            
        Returns:
            Session ID
        """
        import uuid
        
        session_id = str(uuid.uuid4())
        
        self.active_sessions[session_id] = {
            "user": user,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(
                minutes=self.session_timeout
            ),
            "last_accessed": datetime.utcnow()
        }
        
        return session_id

    async def invalidate_session(self, session_id: str) -> bool:
        """Invalidate a session.
        
        Args:
            session_id: Session ID to invalidate
            
        Returns:
            True if session was found and invalidated
        """
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            return True
        return False

    def generate_api_key(self, user_id: str, permissions: list = None, 
                        expires_days: int = None) -> Dict[str, str]:
        """Generate a new API key for a user.
        
        Args:
            user_id: User identifier
            permissions: List of permissions for this key
            expires_days: Number of days until expiration
            
        Returns:
            Dictionary with api_key and key_id
        """
        import secrets
        import uuid
        
        # Generate random API key
        api_key = secrets.token_urlsafe(32)
        key_id = str(uuid.uuid4())
        
        # Calculate expiration
        expires_at = None
        if expires_days:
            expires_at = (datetime.utcnow() + timedelta(days=expires_days)).isoformat()
        
        # Store key information (in practice, this would be saved to database)
        self.api_keys[key_id] = {
            "hash": self._hash_api_key(api_key),
            "user_id": user_id,
            "permissions": permissions or [],
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": expires_at,
            "active": True
        }
        
        return {
            "api_key": api_key,
            "key_id": key_id
        }

    def generate_jwt_token(self, user_id: str, permissions: list = None, 
                          expires_hours: int = None) -> str:
        """Generate a JWT token for a user.
        
        Args:
            user_id: User identifier
            permissions: List of permissions
            expires_hours: Hours until expiration
            
        Returns:
            JWT token string
        """
        now = datetime.utcnow()
        expires_hours = expires_hours or self.jwt_expiry
        
        payload = {
            "sub": user_id,
            "iat": now,
            "exp": now + timedelta(hours=expires_hours),
            "permissions": permissions or [],
            "iss": "neurascale-mcp"
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    def _hash_api_key(self, api_key: str) -> str:
        """Hash an API key for secure storage.
        
        Args:
            api_key: API key to hash
            
        Returns:
            Hashed API key
        """
        return hmac.new(
            self.api_key_salt.encode(),
            api_key.encode(),
            hashlib.sha256
        ).hexdigest()

    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        now = datetime.utcnow()
        expired_sessions = [
            session_id for session_id, session in self.active_sessions.items()
            if session.get("expires_at", now) < now
        ]
        
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
        
        return len(expired_sessions)