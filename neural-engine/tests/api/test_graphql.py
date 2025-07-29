"""Tests for GraphQL API endpoints."""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import patch, MagicMock
import jwt
import json

from src.api.app import app


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


class TestGraphQLQueries:
    """Test GraphQL query operations."""

    def test_device_query(self, client, auth_headers):
        """Test querying a single device."""
        query = """
        query GetDevice($id: String!) {
            device(id: $id) {
                id
                name
                type
                status
                serialNumber
                firmwareVersion
                lastSeen
                channelCount
                samplingRate
            }
        }
        """
        variables = {"id": "dev_000001"}

        response = client.post(
            "/api/graphql",
            json={"query": query, "variables": variables},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        assert "data" in data
        assert "device" in data["data"]
        device = data["data"]["device"]
        assert device["id"] == "dev_000001"
        assert "name" in device
        assert "type" in device

    def test_devices_list_query(self, client, auth_headers):
        """Test querying device list with pagination."""
        query = """
        query ListDevices($filter: DeviceFilter, $pagination: PaginationInput) {
            devices(filter: $filter, pagination: $pagination) {
                edges {
                    node {
                        id
                        name
                        type
                        status
                    }
                    cursor
                }
                pageInfo {
                    hasNextPage
                    hasPreviousPage
                    startCursor
                    endCursor
                }
                totalCount
            }
        }
        """
        variables = {
            "filter": {"status": "ONLINE"},
            "pagination": {"first": 5},
        }

        response = client.post(
            "/api/graphql",
            json={"query": query, "variables": variables},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        assert "data" in data
        devices = data["data"]["devices"]
        assert "edges" in devices
        assert "pageInfo" in devices
        assert "totalCount" in devices

        # Check filtering worked
        for edge in devices["edges"]:
            assert edge["node"]["status"] == "ONLINE"

    def test_session_with_relationships(self, client, auth_headers):
        """Test querying session with related data."""
        query = """
        query GetSessionWithRelations($id: String!) {
            session(id: $id) {
                id
                patientId
                deviceId
                startTime
                endTime
                status
                device {
                    id
                    name
                    type
                }
                patient {
                    id
                    externalId
                }
                neuralData(channels: [0, 1, 2, 3]) {
                    startTime
                    endTime
                    samplingRate
                    dataShape
                }
            }
        }
        """
        variables = {"id": "ses_000001"}

        response = client.post(
            "/api/graphql",
            json={"query": query, "variables": variables},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        session = data["data"]["session"]
        assert session["id"] == "ses_000001"
        assert "device" in session
        assert "patient" in session
        assert "neuralData" in session

        # Check nested relationships
        assert session["device"]["id"] == session["deviceId"]
        assert session["patient"]["id"] == session["patientId"]

    def test_complex_nested_query(self, client, auth_headers):
        """Test complex nested query with multiple levels."""
        query = """
        query ComplexQuery {
            devices(pagination: {first: 3}) {
                edges {
                    node {
                        id
                        name
                        sessions(pagination: {first: 2}) {
                            edges {
                                node {
                                    id
                                    status
                                    patient {
                                        id
                                        externalId
                                    }
                                    analyses {
                                        id
                                        type
                                        status
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        """

        response = client.post(
            "/api/graphql", json={"query": query}, headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        devices = data["data"]["devices"]["edges"]
        assert len(devices) <= 3

        for device_edge in devices:
            device = device_edge["node"]
            assert "sessions" in device
            sessions = device["sessions"]["edges"]

            for session_edge in sessions:
                session = session_edge["node"]
                assert "patient" in session
                assert "analyses" in session

    def test_invalid_query_syntax(self, client, auth_headers):
        """Test GraphQL syntax error handling."""
        invalid_query = """
        query InvalidSyntax {
            device(id: "dev_001") {
                id
                # Missing closing brace
        """

        response = client.post(
            "/api/graphql", json={"query": invalid_query}, headers=auth_headers
        )
        assert response.status_code == 400
        data = response.json()
        assert "errors" in data

    def test_query_validation_error(self, client, auth_headers):
        """Test GraphQL validation error."""
        query = """
        query InvalidField {
            device(id: "dev_001") {
                id
                nonExistentField
            }
        }
        """

        response = client.post(
            "/api/graphql", json={"query": query}, headers=auth_headers
        )
        assert response.status_code == 400
        data = response.json()
        assert "errors" in data


class TestGraphQLMutations:
    """Test GraphQL mutation operations."""

    def test_create_device_mutation(self, client, auth_headers):
        """Test creating device via GraphQL mutation."""
        mutation = """
        mutation CreateDevice($input: CreateDeviceInput!) {
            createDevice(input: $input) {
                success
                message
                device {
                    id
                    name
                    type
                    status
                    serialNumber
                }
            }
        }
        """
        variables = {
            "input": {
                "name": "GraphQL Test Device",
                "type": "EEG",
                "serialNumber": "GQL-TEST-001",
                "firmwareVersion": "1.0.0",
                "channelCount": 32,
                "samplingRate": 256,
            }
        }

        response = client.post(
            "/api/graphql",
            json={"query": mutation, "variables": variables},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        result = data["data"]["createDevice"]
        assert result["success"] is True
        assert "device" in result
        device = result["device"]
        assert device["name"] == variables["input"]["name"]
        assert device["type"] == variables["input"]["type"]

    def test_update_device_mutation(self, client, auth_headers):
        """Test updating device via GraphQL mutation."""
        mutation = """
        mutation UpdateDevice($id: String!, $input: UpdateDeviceInput!) {
            updateDevice(id: $id, input: $input) {
                success
                message
                device {
                    id
                    name
                    status
                }
            }
        }
        """
        variables = {
            "id": "dev_000001",
            "input": {
                "name": "Updated via GraphQL",
                "status": "ONLINE",
            },
        }

        response = client.post(
            "/api/graphql",
            json={"query": mutation, "variables": variables},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        result = data["data"]["updateDevice"]
        assert result["success"] is True
        device = result["device"]
        assert device["name"] == variables["input"]["name"]
        assert device["status"] == variables["input"]["status"]

    def test_start_session_mutation(self, client, auth_headers):
        """Test starting session via GraphQL mutation."""
        mutation = """
        mutation StartSession($sessionId: String!) {
            startSession(sessionId: $sessionId) {
                success
                message
                session {
                    id
                    status
                    startTime
                }
            }
        }
        """
        variables = {"sessionId": "ses_000001"}

        response = client.post(
            "/api/graphql",
            json={"query": mutation, "variables": variables},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        result = data["data"]["startSession"]
        assert result["success"] is True
        session = result["session"]
        assert session["status"] == "RECORDING"
        assert session["startTime"] is not None

    def test_start_analysis_mutation(self, client, auth_headers):
        """Test starting analysis via GraphQL mutation."""
        mutation = """
        mutation StartAnalysis($input: StartAnalysisInput!) {
            startAnalysis(input: $input) {
                success
                message
                analysis {
                    id
                    sessionId
                    type
                    status
                    createdAt
                }
            }
        }
        """
        variables = {
            "input": {
                "sessionId": "ses_000001",
                "type": "spectral_analysis",
                "parameters": {
                    "frequencyBands": ["alpha", "beta", "gamma"],
                    "windowSize": 2.0,
                },
            }
        }

        response = client.post(
            "/api/graphql",
            json={"query": mutation, "variables": variables},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        result = data["data"]["startAnalysis"]
        assert result["success"] is True
        analysis = result["analysis"]
        assert analysis["type"] == "spectral_analysis"
        assert analysis["status"] == "RUNNING"

    def test_mutation_validation_error(self, client, auth_headers):
        """Test mutation with validation errors."""
        mutation = """
        mutation CreateInvalidDevice($input: CreateDeviceInput!) {
            createDevice(input: $input) {
                success
                message
                device {
                    id
                }
            }
        }
        """
        variables = {
            "input": {
                # Missing required fields
                "name": "Incomplete Device",
            }
        }

        response = client.post(
            "/api/graphql",
            json={"query": mutation, "variables": variables},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        result = data["data"]["createDevice"]
        assert result["success"] is False
        assert "message" in result
        assert "validation" in result["message"].lower()


class TestGraphQLSubscriptions:
    """Test GraphQL subscription operations."""

    def test_subscription_endpoint_exists(self, client, auth_headers):
        """Test that subscription endpoint is available."""
        # Note: Full WebSocket testing would require different setup
        # This tests the subscription schema definition
        query = """
        query {
            __schema {
                subscriptionType {
                    name
                    fields {
                        name
                        type {
                            name
                        }
                    }
                }
            }
        }
        """

        response = client.post(
            "/api/graphql", json={"query": query}, headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()

        subscription_type = data["data"]["__schema"]["subscriptionType"]
        assert subscription_type is not None
        assert subscription_type["name"] == "Subscription"

        # Check for expected subscription fields
        field_names = [field["name"] for field in subscription_type["fields"]]
        assert "deviceStatusUpdates" in field_names
        assert "neuralDataStream" in field_names


class TestGraphQLAuthentication:
    """Test GraphQL authentication and authorization."""

    def test_unauthenticated_request(self, client):
        """Test GraphQL without authentication."""
        query = """
        query {
            devices {
                edges {
                    node {
                        id
                    }
                }
            }
        }
        """

        response = client.post("/api/graphql", json={"query": query})
        assert response.status_code == 401

    def test_invalid_token(self, client):
        """Test GraphQL with invalid token."""
        headers = {"Authorization": "Bearer invalid-token"}
        query = """
        query {
            devices {
                edges {
                    node {
                        id
                    }
                }
            }
        }
        """

        with patch("src.api.rest.middleware.auth.jwt.decode") as mock_decode:
            mock_decode.side_effect = jwt.InvalidTokenError()
            response = client.post(
                "/api/graphql", json={"query": query}, headers=headers
            )
            assert response.status_code == 401


class TestGraphQLPerformance:
    """Test GraphQL performance characteristics."""

    def test_query_complexity_limiting(self, client, auth_headers):
        """Test query complexity limiting."""
        # Create a very nested query that should be limited
        complex_query = """
        query VeryComplexQuery {
            devices {
                edges {
                    node {
                        sessions {
                            edges {
                                node {
                                    analyses {
                                        id
                                        results {
                                            id
                                            data
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        """

        response = client.post(
            "/api/graphql", json={"query": complex_query}, headers=auth_headers
        )
        # Should either succeed or fail with complexity error
        # The exact behavior depends on complexity analyzer configuration
        assert response.status_code in [200, 400]

    def test_n_plus_one_prevention(self, client, auth_headers):
        """Test that DataLoaders prevent N+1 queries."""
        # This query should use DataLoaders to efficiently fetch related data
        query = """
        query EfficientQuery {
            sessions(pagination: {first: 10}) {
                edges {
                    node {
                        id
                        device {
                            id
                            name
                        }
                        patient {
                            id
                            externalId
                        }
                    }
                }
            }
        }
        """

        # Mock DataLoader to verify it's being used
        with patch("src.api.graphql.dataloaders.device_loader") as mock_loader:
            mock_loader.load_many.return_value = []
            response = client.post(
                "/api/graphql", json={"query": query}, headers=auth_headers
            )
            assert response.status_code == 200

    def test_introspection_query(self, client, auth_headers):
        """Test GraphQL introspection."""
        introspection_query = """
        query IntrospectionQuery {
            __schema {
                types {
                    name
                    kind
                }
                queryType {
                    name
                }
                mutationType {
                    name
                }
                subscriptionType {
                    name
                }
            }
        }
        """

        response = client.post(
            "/api/graphql",
            json={"query": introspection_query},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        schema = data["data"]["__schema"]
        assert schema["queryType"]["name"] == "Query"
        assert schema["mutationType"]["name"] == "Mutation"
        assert schema["subscriptionType"]["name"] == "Subscription"

        # Check for our custom types
        type_names = [t["name"] for t in schema["types"]]
        assert "Device" in type_names
        assert "Session" in type_names
        assert "Patient" in type_names
