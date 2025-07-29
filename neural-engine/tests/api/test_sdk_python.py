"""Tests for Python SDK."""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import aiohttp
from datetime import datetime

from src.api.sdk.python.neurascale.client import NeuraScaleClient
from src.api.sdk.python.neurascale.exceptions import (
    NeuraScaleError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from src.api.sdk.python.neurascale.models import Device, Session, Patient


class TestNeuraScaleClient:
    """Test the main Python SDK client."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return NeuraScaleClient(
            api_key="test-api-key",
            base_url="https://api.test.neurascale.com",
            timeout=10,
        )

    @pytest.fixture
    def mock_session(self):
        """Mock aiohttp session."""
        return AsyncMock(spec=aiohttp.ClientSession)

    @pytest.mark.asyncio
    async def test_get_device_success(self, client, mock_session):
        """Test successful device retrieval."""
        device_data = {
            "id": "dev_001",
            "name": "Test Device",
            "type": "EEG",
            "status": "ONLINE",
            "serialNumber": "TEST-001",
            "firmwareVersion": "1.0.0",
            "lastSeen": "2023-01-01T00:00:00Z",
            "channelCount": 32,
            "samplingRate": 256,
        }

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = device_data
        mock_session.get.return_value.__aenter__.return_value = mock_response

        with patch.object(client, "_session", mock_session):
            device = await client.get_device("dev_001")

        assert isinstance(device, Device)
        assert device.id == "dev_001"
        assert device.name == "Test Device"
        assert device.type == "EEG"
        mock_session.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_device_not_found(self, client, mock_session):
        """Test device not found error."""
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_response.json.return_value = {
            "error": {"message": "Device not found", "code": "DEVICE_NOT_FOUND"}
        }
        mock_session.get.return_value.__aenter__.return_value = mock_response

        with patch.object(client, "_session", mock_session):
            with pytest.raises(NotFoundError) as exc_info:
                await client.get_device("invalid_id")

        assert "Device not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_list_devices_with_pagination(self, client, mock_session):
        """Test listing devices with pagination."""
        devices_data = {
            "items": [
                {
                    "id": "dev_001",
                    "name": "Device 1",
                    "type": "EEG",
                    "status": "ONLINE",
                    "serialNumber": "DEV-001",
                    "firmwareVersion": "1.0.0",
                    "lastSeen": "2023-01-01T00:00:00Z",
                    "channelCount": 32,
                    "samplingRate": 256,
                },
                {
                    "id": "dev_002",
                    "name": "Device 2",
                    "type": "EMG",
                    "status": "OFFLINE",
                    "serialNumber": "DEV-002",
                    "firmwareVersion": "1.1.0",
                    "lastSeen": "2023-01-01T01:00:00Z",
                    "channelCount": 16,
                    "samplingRate": 512,
                },
            ],
            "total": 2,
            "page": 1,
            "size": 10,
            "totalPages": 1,
        }

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = devices_data
        mock_session.get.return_value.__aenter__.return_value = mock_response

        with patch.object(client, "_session", mock_session):
            result = await client.list_devices(
                filters={"status": "ONLINE"}, page=1, size=10
            )

        assert result.total == 2
        assert len(result.items) == 2
        assert isinstance(result.items[0], Device)
        assert result.items[0].id == "dev_001"

    @pytest.mark.asyncio
    async def test_create_device(self, client, mock_session):
        """Test device creation."""
        device_data = {
            "name": "New Device",
            "type": "EEG",
            "serialNumber": "NEW-001",
            "firmwareVersion": "1.0.0",
            "channelCount": 32,
            "samplingRate": 256,
        }

        created_device = {
            "id": "dev_new",
            "status": "OFFLINE",
            **device_data,
        }

        mock_response = AsyncMock()
        mock_response.status = 201
        mock_response.json.return_value = created_device
        mock_session.post.return_value.__aenter__.return_value = mock_response

        with patch.object(client, "_session", mock_session):
            device = await client.create_device(device_data)

        assert isinstance(device, Device)
        assert device.id == "dev_new"
        assert device.name == "New Device"
        mock_session.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_device(self, client, mock_session):
        """Test device update."""
        update_data = {"name": "Updated Device", "status": "ONLINE"}

        updated_device = {
            "id": "dev_001",
            "name": "Updated Device",
            "type": "EEG",
            "status": "ONLINE",
            "serialNumber": "DEV-001",
            "firmwareVersion": "1.0.0",
            "lastSeen": "2023-01-01T00:00:00Z",
            "channelCount": 32,
            "samplingRate": 256,
        }

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = updated_device
        mock_session.patch.return_value.__aenter__.return_value = mock_response

        with patch.object(client, "_session", mock_session):
            device = await client.update_device("dev_001", update_data)

        assert device.name == "Updated Device"
        assert device.status == "ONLINE"

    @pytest.mark.asyncio
    async def test_delete_device(self, client, mock_session):
        """Test device deletion."""
        mock_response = AsyncMock()
        mock_response.status = 204
        mock_session.delete.return_value.__aenter__.return_value = mock_response

        with patch.object(client, "_session", mock_session):
            await client.delete_device("dev_001")

        mock_session.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_session(self, client, mock_session):
        """Test session retrieval."""
        session_data = {
            "id": "ses_001",
            "patientId": "pat_001",
            "deviceId": "dev_001",
            "startTime": "2023-01-01T10:00:00Z",
            "endTime": "2023-01-01T11:00:00Z",
            "duration": 3600,
            "status": "COMPLETED",
            "channelCount": 32,
            "samplingRate": 256,
        }

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = session_data
        mock_session.get.return_value.__aenter__.return_value = mock_response

        with patch.object(client, "_session", mock_session):
            session = await client.get_session("ses_001")

        assert isinstance(session, Session)
        assert session.id == "ses_001"
        assert session.status == "COMPLETED"

    @pytest.mark.asyncio
    async def test_start_session(self, client, mock_session):
        """Test starting a session."""
        session_data = {
            "id": "ses_001",
            "patientId": "pat_001",
            "deviceId": "dev_001",
            "startTime": "2023-01-01T10:00:00Z",
            "status": "RECORDING",
            "channelCount": 32,
            "samplingRate": 256,
        }

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = session_data
        mock_session.post.return_value.__aenter__.return_value = mock_response

        with patch.object(client, "_session", mock_session):
            session = await client.start_session("ses_001")

        assert session.status == "RECORDING"
        assert session.startTime is not None

    @pytest.mark.asyncio
    async def test_get_neural_data(self, client, mock_session):
        """Test neural data retrieval."""
        neural_data = {
            "sessionId": "ses_001",
            "startTime": 0.0,
            "endTime": 10.0,
            "samplingRate": 256,
            "channelCount": 4,
            "data": [[1, 2, 3, 4]] * 256 * 10,  # 10 seconds of data
            "timestamps": list(range(256 * 10)),
            "channels": [0, 1, 2, 3],
        }

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = neural_data
        mock_session.get.return_value.__aenter__.return_value = mock_response

        with patch.object(client, "_session", mock_session):
            data = await client.get_neural_data(
                "ses_001", start_time=0.0, end_time=10.0, channels=[0, 1, 2, 3]
            )

        assert data.sessionId == "ses_001"
        assert data.samplingRate == 256
        assert len(data.data) == 2560  # 10 seconds * 256 samples

    @pytest.mark.asyncio
    async def test_create_patient(self, client, mock_session):
        """Test patient creation."""
        patient_data = {
            "externalId": "PAT-001",
            "dateOfBirth": "1990-01-01",
            "gender": "M",
        }

        created_patient = {
            "id": "pat_001",
            **patient_data,
            "createdAt": "2023-01-01T00:00:00Z",
        }

        mock_response = AsyncMock()
        mock_response.status = 201
        mock_response.json.return_value = created_patient
        mock_session.post.return_value.__aenter__.return_value = mock_response

        with patch.object(client, "_session", mock_session):
            patient = await client.create_patient(patient_data)

        assert isinstance(patient, Patient)
        assert patient.id == "pat_001"
        assert patient.externalId == "PAT-001"

    @pytest.mark.asyncio
    async def test_start_analysis(self, client, mock_session):
        """Test starting analysis."""
        analysis_data = {
            "id": "ana_001",
            "sessionId": "ses_001",
            "type": "spectral_analysis",
            "status": "RUNNING",
            "createdAt": "2023-01-01T00:00:00Z",
            "parameters": {
                "frequencyBands": ["alpha", "beta", "gamma"],
                "windowSize": 2.0,
            },
        }

        mock_response = AsyncMock()
        mock_response.status = 201
        mock_response.json.return_value = analysis_data
        mock_session.post.return_value.__aenter__.return_value = mock_response

        with patch.object(client, "_session", mock_session):
            analysis = await client.start_analysis(
                "ses_001",
                "spectral_analysis",
                {"frequencyBands": ["alpha", "beta", "gamma"]},
            )

        assert analysis.id == "ana_001"
        assert analysis.type == "spectral_analysis"
        assert analysis.status == "RUNNING"

    @pytest.mark.asyncio
    async def test_authentication_error(self, client, mock_session):
        """Test authentication error handling."""
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.json.return_value = {
            "error": {"message": "Invalid API key", "code": "AUTHENTICATION_FAILED"}
        }
        mock_session.get.return_value.__aenter__.return_value = mock_response

        with patch.object(client, "_session", mock_session):
            with pytest.raises(AuthenticationError) as exc_info:
                await client.get_device("dev_001")

        assert "Invalid API key" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_rate_limit_error(self, client, mock_session):
        """Test rate limit error handling."""
        mock_response = AsyncMock()
        mock_response.status = 429
        mock_response.headers = {"Retry-After": "60"}
        mock_response.json.return_value = {
            "error": {"message": "Rate limit exceeded", "code": "RATE_LIMIT_EXCEEDED"}
        }
        mock_session.get.return_value.__aenter__.return_value = mock_response

        with patch.object(client, "_session", mock_session):
            with pytest.raises(RateLimitError) as exc_info:
                await client.get_device("dev_001")

        assert exc_info.value.retry_after == 60

    @pytest.mark.asyncio
    async def test_validation_error(self, client, mock_session):
        """Test validation error handling."""
        mock_response = AsyncMock()
        mock_response.status = 422
        mock_response.json.return_value = {
            "error": {
                "message": "Validation failed",
                "code": "VALIDATION_ERROR",
                "details": [
                    {"field": "name", "message": "Name is required"},
                    {"field": "type", "message": "Invalid device type"},
                ],
            }
        }
        mock_session.post.return_value.__aenter__.return_value = mock_response

        with patch.object(client, "_session", mock_session):
            with pytest.raises(ValidationError) as exc_info:
                await client.create_device({"invalid": "data"})

        assert "Validation failed" in str(exc_info.value)
        assert exc_info.value.details is not None

    @pytest.mark.asyncio
    async def test_retry_mechanism(self, client, mock_session):
        """Test automatic retry on transient errors."""
        # First call fails with 500, second succeeds
        failed_response = AsyncMock()
        failed_response.status = 500
        failed_response.json.return_value = {"error": {"message": "Server error"}}

        success_response = AsyncMock()
        success_response.status = 200
        success_response.json.return_value = {
            "id": "dev_001",
            "name": "Test Device",
            "type": "EEG",
            "status": "ONLINE",
            "serialNumber": "TEST-001",
            "firmwareVersion": "1.0.0",
            "lastSeen": "2023-01-01T00:00:00Z",
            "channelCount": 32,
            "samplingRate": 256,
        }

        mock_session.get.return_value.__aenter__.side_effect = [
            failed_response,
            success_response,
        ]

        with patch.object(client, "_session", mock_session):
            device = await client.get_device("dev_001")

        assert device.id == "dev_001"
        assert mock_session.get.call_count == 2

    @pytest.mark.asyncio
    async def test_request_cancellation(self, client, mock_session):
        """Test request cancellation with timeout."""
        mock_session.get.side_effect = asyncio.TimeoutError()

        with patch.object(client, "_session", mock_session):
            with pytest.raises(asyncio.TimeoutError):
                await client.get_device("dev_001")

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test client as async context manager."""
        async with NeuraScaleClient(api_key="test-key") as client:
            assert client._session is not None

        # Session should be closed after exiting context
        assert client._session.closed

    def test_client_configuration(self):
        """Test client configuration options."""
        client = NeuraScaleClient(
            api_key="test-key",
            base_url="https://custom.api.com",
            timeout=60,
            max_retries=5,
        )

        assert client.config.api_key == "test-key"
        assert client.config.base_url == "https://custom.api.com"
        assert client.config.timeout == 60
        assert client.config.max_retries == 5

    def test_default_configuration(self):
        """Test default client configuration."""
        client = NeuraScaleClient(api_key="test-key")

        assert client.config.base_url == "https://api.neurascale.com"
        assert client.config.timeout == 30
        assert client.config.max_retries == 3
