"""Tests for REST API session endpoints."""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import patch, MagicMock, AsyncMock
import jwt

from src.api.app import app
from src.api.rest.models import Session, SessionStatus


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Create authentication headers."""
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


class TestSessionEndpoints:
    """Test session REST API endpoints."""

    def test_list_sessions(self, client, auth_headers):
        """Test listing sessions."""
        response = client.get("/api/v2/sessions", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        assert "total" in data
        assert len(data["items"]) > 0

        session = data["items"][0]
        assert "id" in session
        assert "patientId" in session
        assert "deviceId" in session
        assert "startTime" in session
        assert "status" in session

    def test_list_sessions_with_filters(self, client, auth_headers):
        """Test listing sessions with filters."""
        # Filter by patient
        response = client.get(
            "/api/v2/sessions?patientId=pat_001", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        for session in data["items"]:
            assert session["patientId"] == "pat_001"

        # Filter by device
        response = client.get(
            "/api/v2/sessions?deviceId=dev_000001", headers=auth_headers
        )
        assert response.status_code == 200

        # Filter by status
        response = client.get(
            "/api/v2/sessions?status=RECORDING", headers=auth_headers
        )
        assert response.status_code == 200

    def test_get_session(self, client, auth_headers):
        """Test getting a single session."""
        response = client.get("/api/v2/sessions/ses_000001", headers=auth_headers)
        assert response.status_code == 200
        session = response.json()

        assert session["id"] == "ses_000001"
        assert "patientId" in session
        assert "deviceId" in session
        assert "startTime" in session
        assert "endTime" in session
        assert "duration" in session
        assert "status" in session
        assert "channelCount" in session
        assert "samplingRate" in session
        assert "_links" in session

    def test_create_session(self, client, auth_headers):
        """Test creating a new session."""
        new_session = {
            "patientId": "pat_001",
            "deviceId": "dev_000001",
            "channelCount": 32,
            "samplingRate": 256,
            "metadata": {
                "protocol": "resting_state",
                "notes": "Test session",
            },
        }

        response = client.post(
            "/api/v2/sessions", json=new_session, headers=auth_headers
        )
        assert response.status_code == 201
        session = response.json()

        assert "id" in session
        assert session["patientId"] == new_session["patientId"]
        assert session["deviceId"] == new_session["deviceId"]
        assert session["status"] == "CREATED"
        assert session["channelCount"] == new_session["channelCount"]
        assert session["samplingRate"] == new_session["samplingRate"]

    @patch("src.api.rest.v2.sessions.BackgroundTasks.add_task")
    def test_start_session(self, mock_add_task, client, auth_headers):
        """Test starting a session."""
        response = client.post(
            "/api/v2/sessions/ses_000001/start", headers=auth_headers
        )
        assert response.status_code == 200
        session = response.json()

        assert session["id"] == "ses_000001"
        assert session["status"] == "RECORDING"
        assert session["startTime"] is not None

        # Verify background task was added
        mock_add_task.assert_called_once()

    def test_stop_session(self, client, auth_headers):
        """Test stopping a session."""
        # First start the session
        client.post("/api/v2/sessions/ses_000001/start", headers=auth_headers)

        # Then stop it
        response = client.post(
            "/api/v2/sessions/ses_000001/stop", headers=auth_headers
        )
        assert response.status_code == 200
        session = response.json()

        assert session["id"] == "ses_000001"
        assert session["status"] == "COMPLETED"
        assert session["endTime"] is not None
        assert session["duration"] > 0

    def test_pause_resume_session(self, client, auth_headers):
        """Test pausing and resuming a session."""
        # Start session
        client.post("/api/v2/sessions/ses_000001/start", headers=auth_headers)

        # Pause session
        response = client.post(
            "/api/v2/sessions/ses_000001/pause", headers=auth_headers
        )
        assert response.status_code == 200
        session = response.json()
        assert session["status"] == "PAUSED"

        # Resume session
        response = client.post(
            "/api/v2/sessions/ses_000001/resume", headers=auth_headers
        )
        assert response.status_code == 200
        session = response.json()
        assert session["status"] == "RECORDING"

    def test_export_session(self, client, auth_headers):
        """Test exporting session data."""
        export_params = {
            "format": "EDF",
            "channels": [0, 1, 2, 3],
            "startTime": 0,
            "endTime": 100,
        }

        response = client.post(
            "/api/v2/sessions/ses_000001/export",
            json=export_params,
            headers=auth_headers,
        )
        assert response.status_code == 202
        export = response.json()

        assert "exportId" in export
        assert export["status"] == "PROCESSING"
        assert "_links" in export
        assert "status" in export["_links"]

    def test_add_session_annotation(self, client, auth_headers):
        """Test adding annotation to session."""
        annotation = {
            "timestamp": 123.45,
            "duration": 1.0,
            "label": "spike",
            "confidence": 0.95,
            "channels": [0, 1],
        }

        response = client.post(
            "/api/v2/sessions/ses_000001/annotations",
            json=annotation,
            headers=auth_headers,
        )
        assert response.status_code == 201
        result = response.json()

        assert "id" in result
        assert result["timestamp"] == annotation["timestamp"]
        assert result["label"] == annotation["label"]

    def test_session_not_found(self, client, auth_headers):
        """Test operations on non-existent session."""
        response = client.get("/api/v2/sessions/invalid_id", headers=auth_headers)
        assert response.status_code == 404

        response = client.post(
            "/api/v2/sessions/invalid_id/start", headers=auth_headers
        )
        assert response.status_code == 404

    def test_invalid_session_state_transitions(self, client, auth_headers):
        """Test invalid state transitions."""
        # Try to stop a session that hasn't been started
        response = client.post(
            "/api/v2/sessions/ses_000002/stop", headers=auth_headers
        )
        assert response.status_code == 400
        error = response.json()
        assert "Cannot stop session" in error["error"]["message"]

        # Try to pause a non-recording session
        response = client.post(
            "/api/v2/sessions/ses_000002/pause", headers=auth_headers
        )
        assert response.status_code == 400

    def test_session_metadata_update(self, client, auth_headers):
        """Test updating session metadata."""
        metadata_update = {
            "notes": "Updated notes",
            "tags": ["test", "eeg"],
            "customField": "value",
        }

        response = client.patch(
            "/api/v2/sessions/ses_000001/metadata",
            json=metadata_update,
            headers=auth_headers,
        )
        assert response.status_code == 200
        session = response.json()

        assert session["metadata"]["notes"] == metadata_update["notes"]
        assert session["metadata"]["tags"] == metadata_update["tags"]

    def test_date_range_filtering(self, client, auth_headers):
        """Test filtering sessions by date range."""
        # Test with valid date range
        response = client.get(
            "/api/v2/sessions?startDate=2023-01-01&endDate=2023-12-31",
            headers=auth_headers,
        )
        assert response.status_code == 200

        # Test with invalid date format
        response = client.get(
            "/api/v2/sessions?startDate=invalid-date", headers=auth_headers
        )
        assert response.status_code == 400

    def test_session_summary(self, client, auth_headers):
        """Test getting session summary."""
        response = client.get(
            "/api/v2/sessions/ses_000001/summary", headers=auth_headers
        )
        assert response.status_code == 200
        summary = response.json()

        assert "sessionId" in summary
        assert "duration" in summary
        assert "dataSize" in summary
        assert "eventCount" in summary
        assert "qualityMetrics" in summary

    def test_concurrent_session_operations(self, client, auth_headers):
        """Test handling concurrent operations on same session."""
        # Start a session
        response1 = client.post(
            "/api/v2/sessions/ses_000003/start", headers=auth_headers
        )
        assert response1.status_code == 200

        # Try to start it again (should fail)
        response2 = client.post(
            "/api/v2/sessions/ses_000003/start", headers=auth_headers
        )
        assert response2.status_code == 400

    def test_session_permissions(self, client):
        """Test session access permissions."""
        # Create headers for different user with limited permissions
        limited_token = jwt.encode(
            {
                "sub": "limited-user",
                "user_id": "user_002",
                "roles": ["viewer"],
                "exp": datetime.utcnow().timestamp() + 3600,
            },
            "test-secret-key",
            algorithm="HS256",
        )
        limited_headers = {"Authorization": f"Bearer {limited_token}"}

        with patch("src.api.rest.middleware.auth.jwt.decode") as mock_decode:
            mock_decode.return_value = {
                "sub": "limited-user",
                "user_id": "user_002",
                "roles": ["viewer"],
            }

            # Viewer should be able to list and get sessions
            response = client.get("/api/v2/sessions", headers=limited_headers)
            assert response.status_code == 200

            # But not create or modify sessions
            response = client.post(
                "/api/v2/sessions",
                json={"patientId": "pat_001", "deviceId": "dev_001"},
                headers=limited_headers,
            )
            assert response.status_code == 403