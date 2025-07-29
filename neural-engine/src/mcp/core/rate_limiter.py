"""Rate limiting for MCP server requests."""

import time
from typing import Dict, Any
from collections import defaultdict, deque
from datetime import datetime


class MCPRateLimiter:
    """Rate limiter for MCP server requests."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize rate limiter.

        Args:
            config: Rate limiting configuration
        """
        self.config = config

        # Default rate limits (requests per time window)
        self.default_limits = config.get(
            "default",
            {"requests_per_minute": 60, "requests_per_hour": 1000, "burst_limit": 10},
        )

        # Method-specific rate limits
        self.method_limits = config.get("methods", {})

        # User-specific rate limits
        self.user_limits = config.get("users", {})

        # Rate limiting storage
        self.request_history: Dict[str, deque] = defaultdict(deque)
        self.burst_tokens: Dict[str, Dict[str, Any]] = defaultdict(dict)

        # Cleanup interval
        self.cleanup_interval = config.get("cleanup_interval_seconds", 300)  # 5 minutes
        self.last_cleanup = time.time()

    async def check_limit(
        self, client_id: str, method: str = None, user_id: str = None
    ) -> bool:
        """Check if request is within rate limits.

        Args:
            client_id: Client identifier
            method: Optional method name for method-specific limits
            user_id: Optional user ID for user-specific limits

        Returns:
            True if request is allowed
        """
        # Cleanup old entries periodically
        await self._cleanup_old_entries()

        # Generate rate limit key
        limit_key = self._get_limit_key(client_id, method, user_id)

        # Get applicable limits
        limits = self._get_applicable_limits(method, user_id)

        # Check each limit type
        for limit_type, limit_config in limits.items():
            if not await self._check_specific_limit(
                limit_key, limit_type, limit_config
            ):
                return False

        # Record the request
        self._record_request(limit_key)

        return True

    async def get_rate_limit_status(
        self, client_id: str, method: str = None, user_id: str = None
    ) -> Dict[str, Any]:
        """Get current rate limit status for a client.

        Args:
            client_id: Client identifier
            method: Optional method name
            user_id: Optional user ID

        Returns:
            Rate limit status information
        """
        limit_key = self._get_limit_key(client_id, method, user_id)
        limits = self._get_applicable_limits(method, user_id)

        status = {
            "client_id": client_id,
            "method": method,
            "user_id": user_id,
            "limits": {},
        }

        for limit_type, limit_config in limits.items():
            remaining, reset_time = self._get_limit_status(
                limit_key, limit_type, limit_config
            )

            status["limits"][limit_type] = {
                "limit": limit_config.get("limit", 0),
                "remaining": remaining,
                "reset_at": reset_time.isoformat() if reset_time else None,
            }

        return status

    async def reset_limits(
        self, client_id: str, method: str = None, user_id: str = None
    ) -> bool:
        """Reset rate limits for a client.

        Args:
            client_id: Client identifier
            method: Optional method name
            user_id: Optional user ID

        Returns:
            True if limits were reset
        """
        limit_key = self._get_limit_key(client_id, method, user_id)

        # Clear request history
        if limit_key in self.request_history:
            self.request_history[limit_key].clear()

        # Reset burst tokens
        if limit_key in self.burst_tokens:
            self.burst_tokens[limit_key].clear()

        return True

    def _get_limit_key(
        self, client_id: str, method: str = None, user_id: str = None
    ) -> str:
        """Generate rate limit key.

        Args:
            client_id: Client identifier
            method: Optional method name
            user_id: Optional user ID

        Returns:
            Rate limit key
        """
        key_parts = [client_id]

        if method:
            key_parts.append(f"method:{method}")

        if user_id:
            key_parts.append(f"user:{user_id}")

        return ":".join(key_parts)

    def _get_applicable_limits(
        self, method: str = None, user_id: str = None
    ) -> Dict[str, Dict[str, Any]]:
        """Get applicable rate limits.

        Args:
            method: Optional method name
            user_id: Optional user ID

        Returns:
            Dictionary of applicable limits
        """
        limits = {}

        # Start with default limits
        for limit_type, limit_value in self.default_limits.items():
            if limit_type.startswith("requests_per_"):
                time_window = limit_type.replace("requests_per_", "")
                limits[limit_type] = {"limit": limit_value, "window": time_window}
            elif limit_type == "burst_limit":
                limits[limit_type] = {
                    "limit": limit_value,
                    "refill_rate": 1.0,  # tokens per second
                }

        # Apply method-specific limits
        if method and method in self.method_limits:
            method_limits = self.method_limits[method]
            for limit_type, limit_value in method_limits.items():
                if limit_type.startswith("requests_per_"):
                    time_window = limit_type.replace("requests_per_", "")
                    limits[f"method_{limit_type}"] = {
                        "limit": limit_value,
                        "window": time_window,
                    }
                elif limit_type == "burst_limit":
                    limits[f"method_{limit_type}"] = {
                        "limit": limit_value,
                        "refill_rate": method_limits.get("refill_rate", 1.0),
                    }

        # Apply user-specific limits
        if user_id and user_id in self.user_limits:
            user_limits = self.user_limits[user_id]
            for limit_type, limit_value in user_limits.items():
                if limit_type.startswith("requests_per_"):
                    time_window = limit_type.replace("requests_per_", "")
                    limits[f"user_{limit_type}"] = {
                        "limit": limit_value,
                        "window": time_window,
                    }
                elif limit_type == "burst_limit":
                    limits[f"user_{limit_type}"] = {
                        "limit": limit_value,
                        "refill_rate": user_limits.get("refill_rate", 1.0),
                    }

        return limits

    async def _check_specific_limit(
        self, limit_key: str, limit_type: str, limit_config: Dict[str, Any]
    ) -> bool:
        """Check a specific rate limit.

        Args:
            limit_key: Rate limit key
            limit_type: Type of limit
            limit_config: Limit configuration

        Returns:
            True if within limit
        """
        if limit_type.endswith("burst_limit"):
            return self._check_burst_limit(limit_key, limit_type, limit_config)
        else:
            return self._check_time_window_limit(limit_key, limit_type, limit_config)

    def _check_time_window_limit(
        self, limit_key: str, limit_type: str, limit_config: Dict[str, Any]
    ) -> bool:
        """Check time window-based rate limit.

        Args:
            limit_key: Rate limit key
            limit_type: Type of limit
            limit_config: Limit configuration

        Returns:
            True if within limit
        """
        limit = limit_config["limit"]
        window = limit_config["window"]

        # Calculate time window
        now = time.time()
        if window == "minute":
            window_start = now - 60
        elif window == "hour":
            window_start = now - 3600
        elif window == "day":
            window_start = now - 86400
        else:
            window_start = now - 60  # Default to 1 minute

        # Count requests in time window
        history_key = f"{limit_key}:{limit_type}"
        request_times = self.request_history[history_key]

        # Remove old requests
        while request_times and request_times[0] < window_start:
            request_times.popleft()

        # Check if within limit
        return len(request_times) < limit

    def _check_burst_limit(
        self, limit_key: str, limit_type: str, limit_config: Dict[str, Any]
    ) -> bool:
        """Check burst limit using token bucket algorithm.

        Args:
            limit_key: Rate limit key
            limit_type: Type of limit
            limit_config: Limit configuration

        Returns:
            True if within limit
        """
        limit = limit_config["limit"]
        refill_rate = limit_config["refill_rate"]

        bucket_key = f"{limit_key}:{limit_type}"
        now = time.time()

        # Initialize bucket if not exists
        if bucket_key not in self.burst_tokens:
            self.burst_tokens[bucket_key] = {"tokens": limit, "last_refill": now}

        bucket = self.burst_tokens[bucket_key]

        # Refill tokens
        time_passed = now - bucket["last_refill"]
        tokens_to_add = time_passed * refill_rate
        bucket["tokens"] = min(limit, bucket["tokens"] + tokens_to_add)
        bucket["last_refill"] = now

        # Check if token available
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True

        return False

    def _get_limit_status(
        self, limit_key: str, limit_type: str, limit_config: Dict[str, Any]
    ) -> tuple:
        """Get current status for a specific limit.

        Args:
            limit_key: Rate limit key
            limit_type: Type of limit
            limit_config: Limit configuration

        Returns:
            Tuple of (remaining_requests, reset_time)
        """
        if limit_type.endswith("burst_limit"):
            bucket_key = f"{limit_key}:{limit_type}"
            if bucket_key in self.burst_tokens:
                tokens = self.burst_tokens[bucket_key]["tokens"]
                return int(tokens), None
            else:
                return limit_config["limit"], None

        else:
            limit = limit_config["limit"]
            window = limit_config["window"]

            # Calculate time window
            now = time.time()
            if window == "minute":
                window_start = now - 60
                reset_time = datetime.fromtimestamp(now + (60 - (now % 60)))
            elif window == "hour":
                window_start = now - 3600
                reset_time = datetime.fromtimestamp(now + (3600 - (now % 3600)))
            elif window == "day":
                window_start = now - 86400
                reset_time = datetime.fromtimestamp(now + (86400 - (now % 86400)))
            else:
                window_start = now - 60
                reset_time = datetime.fromtimestamp(now + (60 - (now % 60)))

            # Count requests in window
            history_key = f"{limit_key}:{limit_type}"
            request_times = self.request_history[history_key]

            # Count valid requests
            valid_requests = sum(
                1 for req_time in request_times if req_time >= window_start
            )
            remaining = max(0, limit - valid_requests)

            return remaining, reset_time

    def _record_request(self, limit_key: str) -> None:
        """Record a request for rate limiting.

        Args:
            limit_key: Rate limit key
        """
        now = time.time()

        # Record for all applicable limit types
        for limit_type in [
            "requests_per_minute",
            "requests_per_hour",
            "requests_per_day",
        ]:
            history_key = f"{limit_key}:{limit_type}"
            self.request_history[history_key].append(now)

    async def _cleanup_old_entries(self) -> None:
        """Clean up old rate limiting entries."""
        now = time.time()

        # Only cleanup periodically
        if now - self.last_cleanup < self.cleanup_interval:
            return

        self.last_cleanup = now

        # Clean up request history
        cutoff_time = now - 86400  # Keep 24 hours of history

        for history_key in list(self.request_history.keys()):
            history = self.request_history[history_key]

            # Remove old entries
            while history and history[0] < cutoff_time:
                history.popleft()

            # Remove empty histories
            if not history:
                del self.request_history[history_key]

        # Clean up burst token buckets (remove inactive ones)
        inactive_cutoff = now - 3600  # 1 hour

        for bucket_key in list(self.burst_tokens.keys()):
            bucket = self.burst_tokens[bucket_key]
            if bucket["last_refill"] < inactive_cutoff:
                del self.burst_tokens[bucket_key]
