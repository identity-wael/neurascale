"""Rate limiting middleware for API protection."""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Tuple
import time
import asyncio
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using sliding window algorithm."""

    def __init__(self, app, calls: int = 100, period: int = 60):
        """
        Initialize rate limiter.

        Args:
            app: FastAPI application
            calls: Number of allowed calls
            period: Time period in seconds
        """
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients: Dict[str, list] = defaultdict(list)
        self._cleanup_task = None

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        # Extract client identifier (IP or API key)
        client_id = self._get_client_id(request)

        # Check rate limit
        if not self._check_rate_limit(client_id):
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "retry_after": self.period,
                    "limit": self.calls,
                    "period": self.period,
                },
                headers={"Retry-After": str(self.period)},
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        remaining = self._get_remaining_calls(client_id)
        response.headers["X-RateLimit-Limit"] = str(self.calls)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + self.period)

        # Start cleanup task if not running
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_old_entries())

        return response

    def _get_client_id(self, request: Request) -> str:
        """Extract client identifier from request."""
        # Check for API key first
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"key:{api_key}"

        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"

        client = request.client
        if client:
            return f"ip:{client.host}"

        return "ip:unknown"

    def _check_rate_limit(self, client_id: str) -> bool:
        """Check if client has exceeded rate limit."""
        now = time.time()
        window_start = now - self.period

        # Remove old entries
        self.clients[client_id] = [
            timestamp
            for timestamp in self.clients[client_id]
            if timestamp > window_start
        ]

        # Check limit
        if len(self.clients[client_id]) >= self.calls:
            return False

        # Add current request
        self.clients[client_id].append(now)
        return True

    def _get_remaining_calls(self, client_id: str) -> int:
        """Get remaining calls for client."""
        return max(0, self.calls - len(self.clients[client_id]))

    async def _cleanup_old_entries(self):
        """Periodically clean up old rate limit entries."""
        while True:
            try:
                await asyncio.sleep(self.period)
                now = time.time()
                window_start = now - self.period

                # Clean up old entries
                for client_id in list(self.clients.keys()):
                    self.clients[client_id] = [
                        timestamp
                        for timestamp in self.clients[client_id]
                        if timestamp > window_start
                    ]

                    # Remove empty entries
                    if not self.clients[client_id]:
                        del self.clients[client_id]

                logger.debug(
                    f"Cleaned up rate limit entries, {len(self.clients)} clients tracked"
                )

            except Exception as e:
                logger.error(f"Error in rate limit cleanup: {e}")


class DistributedRateLimiter:
    """Redis-based distributed rate limiter for multi-instance deployments."""

    def __init__(self, redis_client, prefix: str = "ratelimit"):
        """
        Initialize distributed rate limiter.

        Args:
            redis_client: Redis client instance
            prefix: Key prefix for Redis
        """
        self.redis = redis_client
        self.prefix = prefix

    async def check_rate_limit(
        self, client_id: str, calls: int, period: int
    ) -> Tuple[bool, int]:
        """
        Check rate limit using Redis.

        Args:
            client_id: Client identifier
            calls: Allowed calls
            period: Time period

        Returns:
            Tuple of (allowed, remaining_calls)
        """
        key = f"{self.prefix}:{client_id}"
        now = int(time.time())

        # Use Redis pipeline for atomic operations
        pipe = self.redis.pipeline()

        # Remove old entries
        pipe.zremrangebyscore(key, 0, now - period)

        # Count current entries
        pipe.zcard(key)

        # Add current request if under limit
        pipe.zadd(key, {str(now): now})

        # Set expiry
        pipe.expire(key, period)

        results = await pipe.execute()

        current_calls = results[1]
        if current_calls >= calls:
            # Remove the added entry if over limit
            await self.redis.zrem(key, str(now))
            return False, 0

        return True, calls - current_calls - 1
