"""Pytest configuration and fixtures."""

import pytest
import os
from unittest.mock import Mock


@pytest.fixture(scope="session")
def gcp_project():
    """Get GCP project ID from environment or use test default."""
    return os.environ.get("PROJECT_ID", "test-project")


@pytest.fixture(scope="session")
def test_config():
    """Test configuration."""
    return {
        "project_id": "test-project",
        "region": "northamerica-northeast1",
        "use_emulator": True,
        "debug": True,
    }


@pytest.fixture
def mock_pubsub_client():
    """Mock Google Cloud Pub/Sub client."""
    mock = Mock()
    mock.project_path.return_value = "projects/test-project"
    mock.topic_path.return_value = "projects/test-project/topics/test-topic"
    return mock


@pytest.fixture
def mock_firestore_client():
    """Mock Google Cloud Firestore client."""
    mock = Mock()
    mock.collection.return_value = Mock()
    return mock


@pytest.fixture
def sample_neural_data():
    """Sample neural data for testing."""
    import numpy as np

    return {
        "device_id": "test_device_001",
        "user_id": "test_user_001",
        "session_id": "test_session_001",
        "data_type": "eeg",
        "sampling_rate": 250,
        "channels": [
            {"id": i, "label": f"CH{i}", "unit": "μV"}
            for i in range(8)
        ],
        "neural_signals": np.random.randn(8, 1000).tolist(),
        "timestamp": "2024-01-01T00:00:00Z",
        "metadata": {
            "experiment": "motor_imagery",
            "task": "left_hand_movement",
        }
    }
