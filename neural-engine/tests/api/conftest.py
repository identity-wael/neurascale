"""Pytest configuration and fixtures for API tests."""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timedelta


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_device_store():
    """Mock device data store."""
    devices = {
        "dev_000001": {
            "id": "dev_000001",
            "name": "EEG Device 1",
            "type": "EEG",
            "status": "ONLINE",
            "serialNumber": "EEG-001",
            "firmwareVersion": "1.2.0",
            "lastSeen": "2023-01-01T12:00:00Z",
            "channelCount": 32,
            "samplingRate": 256,
        },
        "dev_000002": {
            "id": "dev_000002",
            "name": "EMG Device 1",
            "type": "EMG",
            "status": "OFFLINE",
            "serialNumber": "EMG-001",
            "firmwareVersion": "1.1.0",
            "lastSeen": "2023-01-01T11:00:00Z",
            "channelCount": 16,
            "samplingRate": 512,
        },
        "dev_000003": {
            "id": "dev_000003",
            "name": "EEG Device 2",
            "type": "EEG",
            "status": "ONLINE",
            "serialNumber": "EEG-002",
            "firmwareVersion": "1.2.0",
            "lastSeen": "2023-01-01T12:30:00Z",
            "channelCount": 64,
            "samplingRate": 256,
        },
    }
    return devices


@pytest.fixture
def mock_session_store():
    """Mock session data store."""
    sessions = {
        "ses_000001": {
            "id": "ses_000001",
            "patientId": "pat_001",
            "deviceId": "dev_000001",
            "startTime": "2023-01-01T10:00:00Z",
            "endTime": "2023-01-01T11:00:00Z",
            "duration": 3600,
            "status": "COMPLETED",
            "channelCount": 32,
            "samplingRate": 256,
            "metadata": {
                "protocol": "resting_state",
                "notes": "Test session",
            },
        },
        "ses_000002": {
            "id": "ses_000002",
            "patientId": "pat_002",
            "deviceId": "dev_000002",
            "startTime": None,
            "endTime": None,
            "duration": 0,
            "status": "CREATED",
            "channelCount": 16,
            "samplingRate": 512,
            "metadata": {},
        },
        "ses_000003": {
            "id": "ses_000003",
            "patientId": "pat_001",
            "deviceId": "dev_000001",
            "startTime": "2023-01-01T14:00:00Z",
            "endTime": None,
            "duration": 0,
            "status": "RECORDING",
            "channelCount": 32,
            "samplingRate": 256,
            "metadata": {
                "protocol": "task_based",
            },
        },
    }
    return sessions


@pytest.fixture
def mock_patient_store():
    """Mock patient data store."""
    patients = {
        "pat_001": {
            "id": "pat_001",
            "externalId": "PATIENT-001",
            "dateOfBirth": "1990-01-01",
            "gender": "M",
            "createdAt": "2023-01-01T00:00:00Z",
        },
        "pat_002": {
            "id": "pat_002",
            "externalId": "PATIENT-002",
            "dateOfBirth": "1985-05-15",
            "gender": "F",
            "createdAt": "2023-01-01T00:00:00Z",
        },
    }
    return patients


@pytest.fixture
def mock_analysis_store():
    """Mock analysis data store."""
    analyses = {
        "ana_000001": {
            "id": "ana_000001",
            "sessionId": "ses_000001",
            "type": "spectral_analysis",
            "status": "COMPLETED",
            "createdAt": "2023-01-01T11:00:00Z",
            "completedAt": "2023-01-01T11:05:00Z",
            "parameters": {
                "frequencyBands": ["alpha", "beta", "gamma"],
                "windowSize": 2.0,
            },
            "results": {
                "powerSpectrum": [1.2, 2.3, 1.8, 0.9],
                "dominantFrequency": 10.5,
                "spectralEntropy": 0.85,
            },
        },
        "ana_000002": {
            "id": "ana_000002",
            "sessionId": "ses_000003",
            "type": "artifact_detection",
            "status": "RUNNING",
            "createdAt": "2023-01-01T14:30:00Z",
            "completedAt": None,
            "parameters": {
                "threshold": 100,
                "method": "statistical",
            },
            "results": None,
        },
    }
    return analyses


@pytest.fixture
def mock_neural_data():
    """Mock neural data generator."""

    def generate_data(session_id, start_time=0, end_time=10, channels=None):
        if channels is None:
            channels = [0, 1, 2, 3]

        sampling_rate = 256
        num_samples = int((end_time - start_time) * sampling_rate)
        num_channels = len(channels)

        # Generate synthetic EEG-like data
        import numpy as np

        data = np.random.randn(num_samples, num_channels) * 50  # Microvolts
        timestamps = np.linspace(start_time, end_time, num_samples)

        return {
            "sessionId": session_id,
            "startTime": start_time,
            "endTime": end_time,
            "samplingRate": sampling_rate,
            "channelCount": num_channels,
            "data": data.tolist(),
            "timestamps": timestamps.tolist(),
            "channels": channels,
        }

    return generate_data


@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection."""
    websocket = MagicMock()
    websocket.accept = AsyncMock()
    websocket.send_text = AsyncMock()
    websocket.send_json = AsyncMock()
    websocket.receive_text = AsyncMock()
    websocket.receive_json = AsyncMock()
    websocket.close = AsyncMock()
    return websocket


@pytest.fixture
def mock_background_tasks():
    """Mock FastAPI BackgroundTasks."""
    tasks = MagicMock()
    tasks.add_task = MagicMock()
    return tasks


@pytest.fixture
def sample_jwt_payload():
    """Sample JWT payload for testing."""
    return {
        "sub": "test-user",
        "user_id": "user_001",
        "roles": ["admin"],
        "exp": datetime.utcnow().timestamp() + 3600,
        "iat": datetime.utcnow().timestamp(),
    }


@pytest.fixture
def rate_limit_store():
    """In-memory store for rate limiting tests."""
    return {}


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    redis_mock = MagicMock()
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.set = AsyncMock()
    redis_mock.incr = AsyncMock(return_value=1)
    redis_mock.expire = AsyncMock()
    redis_mock.pipeline = MagicMock()
    redis_mock.pipeline.return_value.__aenter__ = AsyncMock()
    redis_mock.pipeline.return_value.__aexit__ = AsyncMock()
    return redis_mock


@pytest.fixture
def api_test_data():
    """Combined test data for API tests."""
    return {
        "devices": [
            {
                "id": "dev_test_001",
                "name": "Test EEG Device",
                "type": "EEG",
                "status": "ONLINE",
                "serialNumber": "TEST-EEG-001",
                "firmwareVersion": "1.0.0",
                "lastSeen": datetime.utcnow().isoformat(),
                "channelCount": 32,
                "samplingRate": 256,
            }
        ],
        "sessions": [
            {
                "id": "ses_test_001",
                "patientId": "pat_test_001",
                "deviceId": "dev_test_001",
                "startTime": datetime.utcnow().isoformat(),
                "status": "RECORDING",
                "channelCount": 32,
                "samplingRate": 256,
            }
        ],
        "patients": [
            {
                "id": "pat_test_001",
                "externalId": "TEST-PATIENT-001",
                "dateOfBirth": "1990-01-01",
                "gender": "F",
                "createdAt": datetime.utcnow().isoformat(),
            }
        ],
    }


@pytest.fixture
def graphql_test_queries():
    """Common GraphQL queries for testing."""
    return {
        "get_device": """
            query GetDevice($id: String!) {
                device(id: $id) {
                    id
                    name
                    type
                    status
                }
            }
        """,
        "list_devices": """
            query ListDevices($filter: DeviceFilter) {
                devices(filter: $filter) {
                    edges {
                        node {
                            id
                            name
                            type
                            status
                        }
                    }
                    totalCount
                }
            }
        """,
        "create_device": """
            mutation CreateDevice($input: CreateDeviceInput!) {
                createDevice(input: $input) {
                    success
                    message
                    device {
                        id
                        name
                        type
                    }
                }
            }
        """,
    }


# Pytest markers for test categorization
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (may require external dependencies)"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "api: marks tests as API tests"
    )
    config.addinivalue_line(
        "markers", "graphql: marks tests as GraphQL specific"
    )
    config.addinivalue_line(
        "markers", "rest: marks tests as REST API specific"
    )
    config.addinivalue_line(
        "markers", "auth: marks tests as authentication related"
    )
    config.addinivalue_line(
        "markers", "websocket: marks tests as WebSocket related"
    )


# Skip tests that require external dependencies in CI
def pytest_collection_modifyitems(config, items):
    """Modify test collection to skip certain tests in CI."""
    import os

    if os.environ.get("CI"):
        skip_slow = pytest.mark.skip(reason="Skipping slow tests in CI")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment variables."""
    import os

    # Set test environment variables
    original_env = os.environ.copy()
    os.environ["NEURASCALE_ENV"] = "test"
    os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-testing"

    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)