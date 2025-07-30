"""Basic health check integration test."""

import requests
import time


def test_neural_processor_health():
    """Test that the neural processor service is healthy."""
    # Give services a moment to fully start
    time.sleep(2)

    # Test the health endpoint
    response = requests.get("http://neural-processor:8080/health")
    assert response.status_code == 200

    health_data = response.json()
    assert health_data["status"] == "healthy"
    assert "timestamp" in health_data
    assert "version" in health_data


def test_neural_processor_root():
    """Test that the neural processor root endpoint is accessible."""
    response = requests.get("http://neural-processor:8080/")
    assert response.status_code == 200

    root_data = response.json()
    assert root_data["service"] == "NeuraScale Neural Engine API"
    assert root_data["status"] == "operational"
    assert "version" in root_data
    assert "documentation" in root_data
