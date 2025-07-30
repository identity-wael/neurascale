"""Integration tests for the Neural Engine API."""

import requests
import os


API_URL = os.environ.get("API_URL", "http://neural-processor:8080")


def test_health_endpoint():
    """Test the health endpoint."""
    response = requests.get(f"{API_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_ready_endpoint():
    """Test the ready endpoint."""
    response = requests.get(f"{API_URL}/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_home_endpoint():
    """Test the home endpoint."""
    response = requests.get(f"{API_URL}/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Neural Engine API"
    assert data["version"] == "0.1.0"
    assert data["status"] == "ready"


def test_api_cors_headers():
    """Test that CORS headers are properly set."""
    response = requests.options(f"{API_URL}/health")
    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" in response.headers
