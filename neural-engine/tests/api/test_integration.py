"""Integration tests for the complete API system."""

import pytest
import asyncio
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import patch
import jwt

from src.api.app import app


@pytest.fixture
def client():
    """Create test client for integration tests."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Create authentication headers."""
    token = jwt.encode(
        {
            "sub": "integration-test-user",
            "user_id": "user_integration",
            "roles": ["admin"],
            "exp": datetime.utcnow().timestamp() + 3600,
        },
        "test-secret-key",
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def mock_jwt_validation():
    """Mock JWT validation for integration tests."""
    with patch("src.api.rest.middleware.auth.jwt.decode") as mock_decode:
        mock_decode.return_value = {
            "sub": "integration-test-user",
            "user_id": "user_integration",
            "roles": ["admin"],
        }
        yield mock_decode


@pytest.mark.integration
class TestCompleteWorkflow:
    """Test complete API workflows from start to finish."""

    def test_device_to_session_workflow(self, client, auth_headers):
        """Test complete workflow from device creation to session recording."""
        # Step 1: Create a device
        device_data = {
            "name": "Integration Test Device",
            "type": "EEG",
            "serialNumber": "INT-TEST-001",
            "firmwareVersion": "1.0.0",
            "channelCount": 32,
            "samplingRate": 256,
        }

        response = client.post(
            "/api/v2/devices", json=device_data, headers=auth_headers
        )
        assert response.status_code == 201
        device = response.json()
        device_id = device["id"]

        # Step 2: Create a patient
        patient_data = {
            "externalId": "INT-PATIENT-001",
            "dateOfBirth": "1990-01-01",
            "gender": "M",
        }

        response = client.post(
            "/api/v2/patients", json=patient_data, headers=auth_headers
        )
        assert response.status_code == 201
        patient = response.json()
        patient_id = patient["id"]

        # Step 3: Create a session
        session_data = {
            "patientId": patient_id,
            "deviceId": device_id,
            "channelCount": 32,
            "samplingRate": 256,
            "metadata": {
                "protocol": "integration_test",
                "notes": "Full workflow test",
            },
        }

        response = client.post(
            "/api/v2/sessions", json=session_data, headers=auth_headers
        )
        assert response.status_code == 201
        session = response.json()
        session_id = session["id"]

        # Step 4: Start the session
        response = client.post(
            f"/api/v2/sessions/{session_id}/start", headers=auth_headers
        )
        assert response.status_code == 200
        recording_session = response.json()
        assert recording_session["status"] == "RECORDING"

        # Step 5: Get neural data (simulate recorded data)
        response = client.get(
            f"/api/v2/neural-data/sessions/{session_id}",
            params={"channels": "0,1,2,3"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        neural_data = response.json()
        assert neural_data["sessionId"] == session_id

        # Step 6: Start analysis
        analysis_data = {
            "sessionId": session_id,
            "type": "spectral_analysis",
            "parameters": {
                "frequencyBands": ["alpha", "beta"],
                "windowSize": 2.0,
            },
        }

        response = client.post(
            "/api/v2/analysis", json=analysis_data, headers=auth_headers
        )
        assert response.status_code == 201
        analysis = response.json()
        analysis_id = analysis["id"]

        # Step 7: Check analysis status
        response = client.get(
            f"/api/v2/analysis/{analysis_id}", headers=auth_headers
        )
        assert response.status_code == 200
        analysis_status = response.json()
        assert analysis_status["sessionId"] == session_id

        # Step 8: Stop the session
        response = client.post(
            f"/api/v2/sessions/{session_id}/stop", headers=auth_headers
        )
        assert response.status_code == 200
        completed_session = response.json()
        assert completed_session["status"] == "COMPLETED"

        # Step 9: Export session data
        export_data = {
            "format": "EDF",
            "channels": [0, 1, 2, 3],
        }

        response = client.post(
            f"/api/v2/sessions/{session_id}/export",
            json=export_data,
            headers=auth_headers,
        )
        assert response.status_code == 202
        export_result = response.json()
        assert export_result["status"] == "PROCESSING"

    def test_graphql_rest_consistency(self, client, auth_headers):
        """Test that GraphQL and REST APIs return consistent data."""
        # Create a device via REST
        device_data = {
            "name": "Consistency Test Device",
            "type": "EEG",
            "serialNumber": "CONS-001",
            "firmwareVersion": "1.0.0",
            "channelCount": 32,
            "samplingRate": 256,
        }

        rest_response = client.post(
            "/api/v2/devices", json=device_data, headers=auth_headers
        )
        assert rest_response.status_code == 201
        rest_device = rest_response.json()
        device_id = rest_device["id"]

        # Get the same device via REST
        rest_get_response = client.get(
            f"/api/v2/devices/{device_id}", headers=auth_headers
        )
        assert rest_get_response.status_code == 200
        rest_device_get = rest_get_response.json()

        # Get the same device via GraphQL
        graphql_query = """
        query GetDevice($id: String!) {
            device(id: $id) {
                id
                name
                type
                status
                serialNumber
                firmwareVersion
                channelCount
                samplingRate
            }
        }
        """

        graphql_response = client.post(
            "/api/graphql",
            json={"query": graphql_query, "variables": {"id": device_id}},
            headers=auth_headers,
        )
        assert graphql_response.status_code == 200
        graphql_data = graphql_response.json()
        graphql_device = graphql_data["data"]["device"]

        # Compare key fields
        assert rest_device_get["id"] == graphql_device["id"]
        assert rest_device_get["name"] == graphql_device["name"]
        assert rest_device_get["type"] == graphql_device["type"]
        assert rest_device_get["status"] == graphql_device["status"]
        assert rest_device_get["serialNumber"] == graphql_device["serialNumber"]

    def test_batch_operations_workflow(self, client, auth_headers):
        """Test batch operations across multiple resources."""
        # Create multiple devices in batch
        batch_operations = [
            {
                "operation": "create",
                "data": {
                    "name": f"Batch Device {i}",
                    "type": "EEG",
                    "serialNumber": f"BATCH-{i:03d}",
                    "firmwareVersion": "1.0.0",
                    "channelCount": 32,
                    "samplingRate": 256,
                },
            }
            for i in range(1, 4)
        ]

        response = client.post(
            "/api/v2/devices/batch", json=batch_operations, headers=auth_headers
        )
        assert response.status_code == 200
        batch_results = response.json()
        assert len(batch_results) == 3
        assert all(result["success"] for result in batch_results)

        created_device_ids = [result["result"]["id"] for result in batch_results]

        # Update all devices in batch
        update_operations = [
            {
                "operation": "update",
                "id": device_id,
                "data": {"status": "ONLINE"},
            }
            for device_id in created_device_ids
        ]

        response = client.post(
            "/api/v2/devices/batch", json=update_operations, headers=auth_headers
        )
        assert response.status_code == 200
        update_results = response.json()
        assert all(result["success"] for result in update_results)

        # Verify all devices are online
        for device_id in created_device_ids:
            response = client.get(
                f"/api/v2/devices/{device_id}", headers=auth_headers
            )
            assert response.status_code == 200
            device = response.json()
            assert device["status"] == "ONLINE"

    def test_pagination_consistency(self, client, auth_headers):
        """Test pagination consistency across endpoints."""
        # Create several devices for pagination testing
        for i in range(15):
            device_data = {
                "name": f"Pagination Test Device {i:02d}",
                "type": "EEG",
                "serialNumber": f"PAGE-{i:03d}",
                "firmwareVersion": "1.0.0",
                "channelCount": 32,
                "samplingRate": 256,
            }
            response = client.post(
                "/api/v2/devices", json=device_data, headers=auth_headers
            )
            assert response.status_code == 201

        # Test REST pagination
        response = client.get(
            "/api/v2/devices?page=1&size=5", headers=auth_headers
        )
        assert response.status_code == 200
        page1_data = response.json()
        assert len(page1_data["items"]) == 5
        assert page1_data["page"] == 1

        response = client.get(
            "/api/v2/devices?page=2&size=5", headers=auth_headers
        )
        assert response.status_code == 200
        page2_data = response.json()
        assert len(page2_data["items"]) == 5
        assert page2_data["page"] == 2

        # Ensure no overlap between pages
        page1_ids = {device["id"] for device in page1_data["items"]}
        page2_ids = {device["id"] for device in page2_data["items"]}
        assert page1_ids.isdisjoint(page2_ids)

        # Test GraphQL pagination (cursor-based)
        graphql_query = """
        query ListDevices($first: Int) {
            devices(pagination: {first: $first}) {
                edges {
                    node {
                        id
                        name
                    }
                    cursor
                }
                pageInfo {
                    hasNextPage
                    endCursor
                }
            }
        }
        """

        response = client.post(
            "/api/graphql",
            json={"query": graphql_query, "variables": {"first": 5}},
            headers=auth_headers,
        )
        assert response.status_code == 200
        graphql_data = response.json()
        devices = graphql_data["data"]["devices"]
        assert len(devices["edges"]) == 5
        assert devices["pageInfo"]["hasNextPage"] is True

    def test_error_handling_consistency(self, client, auth_headers):
        """Test that error handling is consistent across endpoints."""
        # Test 404 errors
        response = client.get("/api/v2/devices/nonexistent", headers=auth_headers)
        assert response.status_code == 404
        rest_error = response.json()
        assert "error" in rest_error

        # GraphQL 404 equivalent
        graphql_query = """
        query GetDevice($id: String!) {
            device(id: $id) {
                id
                name
            }
        }
        """

        response = client.post(
            "/api/graphql",
            json={"query": graphql_query, "variables": {"id": "nonexistent"}},
            headers=auth_headers,
        )
        assert response.status_code == 200  # GraphQL returns 200 with errors
        graphql_data = response.json()
        assert graphql_data["data"]["device"] is None

        # Test validation errors
        invalid_device = {"name": ""}  # Missing required fields

        response = client.post(
            "/api/v2/devices", json=invalid_device, headers=auth_headers
        )
        assert response.status_code == 422
        rest_validation_error = response.json()
        assert "error" in rest_validation_error

    def test_concurrent_session_operations(self, client, auth_headers):
        """Test handling of concurrent operations on sessions."""
        # Create device and patient first
        device_data = {
            "name": "Concurrent Test Device",
            "type": "EEG",
            "serialNumber": "CONC-001",
            "firmwareVersion": "1.0.0",
            "channelCount": 32,
            "samplingRate": 256,
        }

        device_response = client.post(
            "/api/v2/devices", json=device_data, headers=auth_headers
        )
        device_id = device_response.json()["id"]

        patient_data = {
            "externalId": "CONC-PATIENT-001",
            "dateOfBirth": "1990-01-01",
            "gender": "F",
        }

        patient_response = client.post(
            "/api/v2/patients", json=patient_data, headers=auth_headers
        )
        patient_id = patient_response.json()["id"]

        # Create session
        session_data = {
            "patientId": patient_id,
            "deviceId": device_id,
            "channelCount": 32,
            "samplingRate": 256,
        }

        session_response = client.post(
            "/api/v2/sessions", json=session_data, headers=auth_headers
        )
        session_id = session_response.json()["id"]

        # Start session
        start_response = client.post(
            f"/api/v2/sessions/{session_id}/start", headers=auth_headers
        )
        assert start_response.status_code == 200

        # Try to start again (should fail)
        start_again_response = client.post(
            f"/api/v2/sessions/{session_id}/start", headers=auth_headers
        )
        assert start_again_response.status_code == 400

        # Pause session
        pause_response = client.post(
            f"/api/v2/sessions/{session_id}/pause", headers=auth_headers
        )
        assert pause_response.status_code == 200

        # Resume session
        resume_response = client.post(
            f"/api/v2/sessions/{session_id}/resume", headers=auth_headers
        )
        assert resume_response.status_code == 200

        # Stop session
        stop_response = client.post(
            f"/api/v2/sessions/{session_id}/stop", headers=auth_headers
        )
        assert stop_response.status_code == 200

    def test_hateoas_link_integrity(self, client, auth_headers):
        """Test that HATEOAS links are valid and functional."""
        # Create a device
        device_data = {
            "name": "HATEOAS Test Device",
            "type": "EEG",
            "serialNumber": "HATEOAS-001",
            "firmwareVersion": "1.0.0",
            "channelCount": 32,
            "samplingRate": 256,
        }

        response = client.post(
            "/api/v2/devices", json=device_data, headers=auth_headers
        )
        device = response.json()
        device_id = device["id"]

        # Get device with HATEOAS links
        response = client.get(f"/api/v2/devices/{device_id}", headers=auth_headers)
        device_with_links = response.json()
        assert "_links" in device_with_links

        # Test self link
        self_link = device_with_links["_links"]["self"]
        response = client.request(
            method=self_link["method"],
            url=self_link["href"],
            headers=auth_headers,
        )
        assert response.status_code == 200

        # Test update link
        update_link = device_with_links["_links"]["update"]
        update_data = {"name": "Updated via HATEOAS"}
        response = client.request(
            method=update_link["method"],
            url=update_link["href"],
            json=update_data,
            headers=auth_headers,
        )
        assert response.status_code == 200
        updated_device = response.json()
        assert updated_device["name"] == "Updated via HATEOAS"

    @pytest.mark.slow
    def test_api_performance_baseline(self, client, auth_headers):
        """Test basic API performance characteristics."""
        import time

        # Test device listing performance
        start_time = time.time()
        response = client.get("/api/v2/devices", headers=auth_headers)
        end_time = time.time()

        assert response.status_code == 200
        response_time = end_time - start_time
        assert response_time < 1.0  # Should respond within 1 second

        # Test GraphQL query performance
        start_time = time.time()
        graphql_query = """
        query ListDevices {
            devices(pagination: {first: 10}) {
                edges {
                    node {
                        id
                        name
                        type
                    }
                }
            }
        }
        """

        response = client.post(
            "/api/graphql", json={"query": graphql_query}, headers=auth_headers
        )
        end_time = time.time()

        assert response.status_code == 200
        graphql_response_time = end_time - start_time
        assert graphql_response_time < 1.0  # Should respond within 1 second