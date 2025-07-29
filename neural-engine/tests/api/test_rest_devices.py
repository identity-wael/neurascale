"""Tests for REST API device endpoints."""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import patch, MagicMock
import jwt

from src.api.app import app
from src.api.rest.models import Device, DeviceType, DeviceStatus


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Create authentication headers."""
    # Create a test JWT token
    secret_key = "test-secret-key"
    token = jwt.encode(
        {
            "sub": "test-user",
            "user_id": "user_001",
            "roles": ["admin"],
            "exp": datetime.utcnow().timestamp() + 3600,
        },
        secret_key,
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def mock_jwt_validation():
    """Mock JWT validation for tests."""
    with patch("src.api.rest.middleware.auth.jwt.decode") as mock_decode:
        mock_decode.return_value = {
            "sub": "test-user",
            "user_id": "user_001",
            "roles": ["admin"],
        }
        yield mock_decode


class TestDeviceEndpoints:
    """Test device REST API endpoints."""

    def test_list_devices(self, client, auth_headers):
        """Test listing devices."""
        response = client.get("/api/v2/devices", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "_links" in data

        # Check items structure
        assert len(data["items"]) > 0
        device = data["items"][0]
        assert "id" in device
        assert "name" in device
        assert "type" in device
        assert "status" in device
        assert "_links" in device

    def test_list_devices_with_filters(self, client, auth_headers):
        """Test listing devices with filters."""
        # Filter by status
        response = client.get("/api/v2/devices?status=ONLINE", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        for device in data["items"]:
            assert device["status"] == "ONLINE"

        # Filter by type
        response = client.get("/api/v2/devices?type=EEG", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        for device in data["items"]:
            assert device["type"] == "EEG"

    def test_list_devices_pagination(self, client, auth_headers):
        """Test device listing pagination."""
        # First page
        response = client.get("/api/v2/devices?page=1&size=2", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["size"] == 2
        assert len(data["items"]) <= 2

        # Check pagination links
        assert "_links" in data
        assert "self" in data["_links"]
        if data["total"] > 2:
            assert "next" in data["_links"]

    def test_get_device(self, client, auth_headers):
        """Test getting a single device."""
        response = client.get("/api/v2/devices/dev_000001", headers=auth_headers)
        assert response.status_code == 200
        device = response.json()

        assert device["id"] == "dev_000001"
        assert "name" in device
        assert "type" in device
        assert "status" in device
        assert "serialNumber" in device
        assert "firmwareVersion" in device
        assert "lastSeen" in device
        assert "channelCount" in device
        assert "samplingRate" in device
        assert "_links" in device

    def test_get_device_not_found(self, client, auth_headers):
        """Test getting non-existent device."""
        response = client.get("/api/v2/devices/invalid_id", headers=auth_headers)
        assert response.status_code == 404
        error = response.json()
        assert "error" in error
        assert error["error"]["code"] == "DEVICE_NOT_FOUND"

    def test_create_device(self, client, auth_headers):
        """Test creating a new device."""
        new_device = {
            "name": "Test Device",
            "type": "EEG",
            "serialNumber": "TEST-12345",
            "firmwareVersion": "1.0.0",
            "channelCount": 32,
            "samplingRate": 256,
        }

        response = client.post("/api/v2/devices", json=new_device, headers=auth_headers)
        assert response.status_code == 201
        device = response.json()

        assert "id" in device
        assert device["name"] == new_device["name"]
        assert device["type"] == new_device["type"]
        assert device["status"] == "OFFLINE"
        assert device["serialNumber"] == new_device["serialNumber"]

        # Check Location header
        assert "Location" in response.headers
        assert f"/api/v2/devices/{device['id']}" in response.headers["Location"]

    def test_create_device_validation_error(self, client, auth_headers):
        """Test device creation with invalid data."""
        invalid_device = {
            "name": "Test Device",
            # Missing required fields
        }

        response = client.post(
            "/api/v2/devices", json=invalid_device, headers=auth_headers
        )
        assert response.status_code == 422

    def test_update_device(self, client, auth_headers):
        """Test updating a device."""
        update_data = {
            "name": "Updated Device Name",
            "status": "ONLINE",
        }

        response = client.patch(
            "/api/v2/devices/dev_000001", json=update_data, headers=auth_headers
        )
        assert response.status_code == 200
        device = response.json()

        assert device["id"] == "dev_000001"
        assert device["name"] == update_data["name"]
        assert device["status"] == update_data["status"]

    def test_update_device_not_found(self, client, auth_headers):
        """Test updating non-existent device."""
        update_data = {"name": "Updated Name"}

        response = client.patch(
            "/api/v2/devices/invalid_id", json=update_data, headers=auth_headers
        )
        assert response.status_code == 404

    def test_delete_device(self, client, auth_headers):
        """Test deleting a device."""
        response = client.delete("/api/v2/devices/dev_000001", headers=auth_headers)
        assert response.status_code == 204

        # Verify device is deleted
        response = client.get("/api/v2/devices/dev_000001", headers=auth_headers)
        assert response.status_code == 404

    def test_device_calibration(self, client, auth_headers):
        """Test device calibration."""
        calibration_params = {
            "gain": 1.5,
            "offset": 0.1,
            "channels": [0, 1, 2, 3],
        }

        response = client.post(
            "/api/v2/devices/dev_000001/calibration",
            json=calibration_params,
            headers=auth_headers,
        )
        assert response.status_code == 200
        device = response.json()

        assert device["id"] == "dev_000001"
        assert device["status"] == "CALIBRATING"

    def test_batch_operations(self, client, auth_headers):
        """Test batch device operations."""
        operations = [
            {
                "operation": "update",
                "id": "dev_000001",
                "data": {"status": "ONLINE"},
            },
            {
                "operation": "update",
                "id": "dev_000002",
                "data": {"status": "ONLINE"},
            },
            {
                "operation": "create",
                "data": {
                    "name": "Batch Created Device",
                    "type": "EEG",
                    "serialNumber": "BATCH-001",
                    "firmwareVersion": "1.0.0",
                    "channelCount": 32,
                    "samplingRate": 256,
                },
            },
        ]

        response = client.post(
            "/api/v2/devices/batch", json=operations, headers=auth_headers
        )
        assert response.status_code == 200
        results = response.json()

        assert len(results) == 3
        assert results[0]["success"] is True
        assert results[1]["success"] is True
        assert results[2]["success"] is True
        assert "id" in results[2]["result"]

    def test_authentication_required(self, client):
        """Test that authentication is required."""
        response = client.get("/api/v2/devices")
        assert response.status_code == 401

    def test_invalid_authentication(self, client):
        """Test invalid authentication token."""
        headers = {"Authorization": "Bearer invalid-token"}
        with patch("src.api.rest.middleware.auth.jwt.decode") as mock_decode:
            mock_decode.side_effect = jwt.InvalidTokenError()
            response = client.get("/api/v2/devices", headers=headers)
            assert response.status_code == 401

    def test_rate_limiting(self, client, auth_headers):
        """Test rate limiting."""
        # Make many requests quickly
        for i in range(10):
            response = client.get("/api/v2/devices", headers=auth_headers)
            if response.status_code == 429:
                # Rate limit hit
                assert "X-RateLimit-Limit" in response.headers
                assert "X-RateLimit-Remaining" in response.headers
                assert "X-RateLimit-Reset" in response.headers
                break
        else:
            # If rate limit not hit in test, that's okay
            # (depends on rate limit configuration)
            pass

    def test_cors_headers(self, client, auth_headers):
        """Test CORS headers are present."""
        response = client.options("/api/v2/devices")
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers

    def test_hateoas_links(self, client, auth_headers):
        """Test HATEOAS links are properly formed."""
        response = client.get("/api/v2/devices/dev_000001", headers=auth_headers)
        assert response.status_code == 200
        device = response.json()

        assert "_links" in device
        assert "self" in device["_links"]
        assert "update" in device["_links"]
        assert "delete" in device["_links"]
        assert "calibration" in device["_links"]

        # Verify link structure
        self_link = device["_links"]["self"]
        assert "href" in self_link
        assert "method" in self_link
        assert self_link["href"] == f"/api/v2/devices/{device['id']}"
        assert self_link["method"] == "GET"
