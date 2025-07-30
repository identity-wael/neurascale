"""Integration tests for the Neural Engine API."""

import requests
import os


API_URL = os.environ.get("API_URL", "http://neural-processor:8080")


def test_health_endpoint():
    """Test the health endpoint."""
    response = requests.get(f"{API_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["version"] == "2.0.0"


def test_api_v2_endpoint():
    """Test the API v2 endpoint."""
    response = requests.get(f"{API_URL}/api/v2")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "2.0.0"
    assert "_links" in data


def test_home_endpoint():
    """Test the home endpoint."""
    response = requests.get(f"{API_URL}/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "NeuraScale Neural Engine API"
    assert data["version"] == "2.0.0"
    assert data["status"] == "operational"


def test_api_cors_headers():
    """Test that CORS headers are properly set."""
    # Test CORS on a regular GET request since FastAPI handles CORS differently
    response = requests.get(
        f"{API_URL}/health", headers={"Origin": "http://localhost:3000"}
    )
    assert response.status_code == 200
    # CORS headers should be present in the response
    assert (
        "Access-Control-Allow-Origin" in response.headers
        or response.headers.get("access-control-allow-origin") == "*"
    )
