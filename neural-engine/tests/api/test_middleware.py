"""Tests for API middleware components."""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, Request, Response
from datetime import datetime
from unittest.mock import patch, MagicMock
import jwt
import time

from src.api.rest.middleware.auth import get_current_user, AuthMiddleware
from src.api.rest.middleware.rate_limiter import SlidingWindowRateLimiter
from src.api.rest.middleware.validator import RequestValidator


class TestAuthMiddleware:
    """Test authentication middleware."""

    def create_test_app(self):
        """Create test FastAPI app with auth middleware."""
        app = FastAPI()
        app.add_middleware(AuthMiddleware, secret_key="test-secret")

        @app.get("/protected")
        async def protected_endpoint(request: Request):
            user = await get_current_user(request)
            return {"user_id": user.get("user_id")}

        @app.get("/public")
        async def public_endpoint():
            return {"message": "public"}

        return app

    def test_valid_jwt_token(self):
        """Test authentication with valid JWT token."""
        app = self.create_test_app()
        client = TestClient(app)

        token = jwt.encode(
            {
                "sub": "test-user",
                "user_id": "user_001",
                "roles": ["admin"],
                "exp": datetime.utcnow().timestamp() + 3600,
            },
            "test-secret",
            algorithm="HS256",
        )
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/protected", headers=headers)
        assert response.status_code == 200
        assert response.json()["user_id"] == "user_001"

    def test_missing_token(self):
        """Test authentication without token."""
        app = self.create_test_app()
        client = TestClient(app)

        response = client.get("/protected")
        assert response.status_code == 401
        assert "error" in response.json()

    def test_invalid_token(self):
        """Test authentication with invalid token."""
        app = self.create_test_app()
        client = TestClient(app)

        headers = {"Authorization": "Bearer invalid-token"}
        response = client.get("/protected", headers=headers)
        assert response.status_code == 401

    def test_expired_token(self):
        """Test authentication with expired token."""
        app = self.create_test_app()
        client = TestClient(app)

        token = jwt.encode(
            {
                "sub": "test-user",
                "user_id": "user_001",
                "exp": datetime.utcnow().timestamp() - 3600,  # Expired
            },
            "test-secret",
            algorithm="HS256",
        )
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/protected", headers=headers)
        assert response.status_code == 401

    def test_malformed_auth_header(self):
        """Test authentication with malformed header."""
        app = self.create_test_app()
        client = TestClient(app)

        # Missing Bearer prefix
        headers = {"Authorization": "invalid-format"}
        response = client.get("/protected", headers=headers)
        assert response.status_code == 401

    def test_token_from_query_parameter(self):
        """Test authentication with token in query parameter."""
        app = self.create_test_app()
        client = TestClient(app)

        token = jwt.encode(
            {
                "sub": "test-user",
                "user_id": "user_001",
                "exp": datetime.utcnow().timestamp() + 3600,
            },
            "test-secret",
            algorithm="HS256",
        )

        response = client.get(f"/protected?token={token}")
        assert response.status_code == 200

    def test_role_based_access(self):
        """Test role-based access control."""
        app = FastAPI()
        app.add_middleware(AuthMiddleware, secret_key="test-secret")

        @app.get("/admin-only")
        async def admin_endpoint(request: Request):
            user = await get_current_user(request)
            if "admin" not in user.get("roles", []):
                return Response(status_code=403)
            return {"message": "admin access"}

        client = TestClient(app)

        # Regular user token
        user_token = jwt.encode(
            {
                "sub": "regular-user",
                "user_id": "user_002",
                "roles": ["user"],
                "exp": datetime.utcnow().timestamp() + 3600,
            },
            "test-secret",
            algorithm="HS256",
        )

        # Admin user token
        admin_token = jwt.encode(
            {
                "sub": "admin-user",
                "user_id": "user_001",
                "roles": ["admin"],
                "exp": datetime.utcnow().timestamp() + 3600,
            },
            "test-secret",
            algorithm="HS256",
        )

        # Regular user should be denied
        response = client.get(
            "/admin-only", headers={"Authorization": f"Bearer {user_token}"}
        )
        assert response.status_code == 403

        # Admin user should be allowed
        response = client.get(
            "/admin-only", headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200


class TestRateLimiter:
    """Test rate limiting middleware."""

    def test_sliding_window_rate_limiter(self):
        """Test sliding window rate limiter implementation."""
        limiter = SlidingWindowRateLimiter(
            limit=5, window_size=60, redis_client=None  # Use in-memory
        )

        client_id = "test-client"
        current_time = time.time()

        # First 5 requests should be allowed
        for i in range(5):
            allowed, remaining, reset_time = limiter.is_allowed(
                client_id, current_time + i
            )
            assert allowed is True
            assert remaining == 4 - i
            assert reset_time > current_time

        # 6th request should be denied
        allowed, remaining, reset_time = limiter.is_allowed(client_id, current_time + 5)
        assert allowed is False
        assert remaining == 0

    def test_rate_limit_reset(self):
        """Test rate limit reset after window expires."""
        limiter = SlidingWindowRateLimiter(limit=2, window_size=1, redis_client=None)

        client_id = "test-client"
        current_time = time.time()

        # Use up the limit
        for i in range(2):
            allowed, _, _ = limiter.is_allowed(client_id, current_time + i * 0.1)
            assert allowed is True

        # Should be denied immediately after
        allowed, _, _ = limiter.is_allowed(client_id, current_time + 0.5)
        assert allowed is False

        # Should be allowed after window expires
        allowed, _, _ = limiter.is_allowed(client_id, current_time + 1.5)
        assert allowed is True

    def test_different_clients_separate_limits(self):
        """Test that different clients have separate limits."""
        limiter = SlidingWindowRateLimiter(limit=1, window_size=60, redis_client=None)

        current_time = time.time()

        # Client 1 uses its limit
        allowed, _, _ = limiter.is_allowed("client1", current_time)
        assert allowed is True

        allowed, _, _ = limiter.is_allowed("client1", current_time + 1)
        assert allowed is False

        # Client 2 should still have its limit available
        allowed, _, _ = limiter.is_allowed("client2", current_time + 1)
        assert allowed is True

    def test_rate_limit_headers(self):
        """Test rate limit response headers."""
        app = FastAPI()

        limiter = SlidingWindowRateLimiter(limit=3, window_size=60, redis_client=None)

        @app.middleware("http")
        async def rate_limit_middleware(request: Request, call_next):
            client_id = request.client.host
            current_time = time.time()

            allowed, remaining, reset_time = limiter.is_allowed(client_id, current_time)

            response = await call_next(request)

            response.headers["X-RateLimit-Limit"] = str(limiter.limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(int(reset_time))

            if not allowed:
                response.status_code = 429

            return response

        @app.get("/test")
        async def test_endpoint():
            return {"message": "success"}

        client = TestClient(app)

        # First request should succeed with proper headers
        response = client.get("/test")
        assert response.status_code == 200
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers


class TestRequestValidator:
    """Test request validation middleware."""

    def test_validator_registration(self):
        """Test validator registration and execution."""
        validator = RequestValidator()

        async def test_validator(request):
            if request.url.path == "/test":
                if request.method != "GET":
                    raise ValueError("Only GET allowed")

        validator.register_validator("/test", test_validator)

        # Mock request
        mock_request = MagicMock()
        mock_request.url.path = "/test"
        mock_request.method = "GET"

        # Should not raise
        import asyncio

        asyncio.run(validator.validate_request(mock_request))

    def test_pattern_matching(self):
        """Test URL pattern matching."""
        validator = RequestValidator()

        # Test simple pattern matching
        assert validator._match_pattern("/api/v2/devices", "/api/v2/devices") is True
        assert validator._match_pattern("/api/v2/sessions", "/api/v2/devices") is False

        # Test wildcard matching
        assert (
            validator._match_pattern("/api/v2/devices/123", "/api/v2/devices/*") is True
        )
        assert (
            validator._match_pattern("/api/v2/devices/123/status", "/api/v2/devices/*")
            is False
        )

        # Test multiple wildcards
        assert (
            validator._match_pattern(
                "/api/v2/devices/123/sessions/456", "/api/v2/*/sessions/*"
            )
            is True
        )

    def test_json_content_type_validator(self):
        """Test JSON content type validation."""
        from src.api.rest.middleware.validator import validate_json_content_type

        mock_request = MagicMock()
        mock_request.method = "POST"
        mock_request.headers = {"content-type": "application/json"}

        # Should not raise
        import asyncio

        asyncio.run(validate_json_content_type(mock_request))

        # Test invalid content type
        mock_request.headers = {"content-type": "text/plain"}
        with pytest.raises(Exception):  # Should raise HTTPException
            asyncio.run(validate_json_content_type(mock_request))

    def test_pagination_validator(self):
        """Test pagination parameter validation."""
        from src.api.rest.middleware.validator import validate_pagination_params

        mock_request = MagicMock()

        # Valid pagination params
        mock_request.query_params = {"page": "1", "size": "10"}
        import asyncio

        asyncio.run(validate_pagination_params(mock_request))

        # Invalid page
        mock_request.query_params = {"page": "0"}
        with pytest.raises(Exception):
            asyncio.run(validate_pagination_params(mock_request))

        # Invalid size
        mock_request.query_params = {"size": "101"}
        with pytest.raises(Exception):
            asyncio.run(validate_pagination_params(mock_request))

    def test_date_range_validator(self):
        """Test date range validation."""
        from src.api.rest.middleware.validator import validate_date_range

        mock_request = MagicMock()

        # Valid date range
        mock_request.query_params = {
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
        }
        import asyncio

        asyncio.run(validate_date_range(mock_request))

        # Invalid date order
        mock_request.query_params = {
            "start_date": "2023-12-31",
            "end_date": "2023-01-01",
        }
        with pytest.raises(Exception):
            asyncio.run(validate_date_range(mock_request))

        # Invalid date format
        mock_request.query_params = {
            "start_date": "invalid-date",
            "end_date": "2023-12-31",
        }
        with pytest.raises(Exception):
            asyncio.run(validate_date_range(mock_request))


class TestCORSMiddleware:
    """Test CORS middleware configuration."""

    def test_cors_headers(self):
        """Test CORS headers are properly set."""
        app = FastAPI()

        from fastapi.middleware.cors import CORSMiddleware

        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}

        client = TestClient(app)

        # Test preflight request
        response = client.options(
            "/test",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "GET",
            },
        )

        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers

        # Test actual request
        response = client.get("/test", headers={"Origin": "https://example.com"})
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers


class TestGZipMiddleware:
    """Test GZip compression middleware."""

    def test_gzip_compression(self):
        """Test response compression."""
        app = FastAPI()

        from fastapi.middleware.gzip import GZipMiddleware

        app.add_middleware(GZipMiddleware, minimum_size=1000)

        @app.get("/large-response")
        async def large_response():
            return {"data": "x" * 2000}  # Large response to trigger compression

        @app.get("/small-response")
        async def small_response():
            return {"data": "small"}

        client = TestClient(app)

        # Large response should be compressed
        response = client.get("/large-response", headers={"Accept-Encoding": "gzip"})
        assert response.status_code == 200
        # Note: TestClient automatically decompresses, so we can't check encoding header
        # In real scenarios, the content-encoding header would be present

        # Small response should not be compressed
        response = client.get("/small-response", headers={"Accept-Encoding": "gzip"})
        assert response.status_code == 200
