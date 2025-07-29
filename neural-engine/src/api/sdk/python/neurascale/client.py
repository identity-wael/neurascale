"""NeuraScale Python SDK client."""

from typing import Optional, List, Dict, Any, AsyncGenerator
import httpx
import asyncio
from datetime import datetime
import logging
from urllib.parse import urljoin

from .models import (
    Device,
    DeviceCreate,
    DeviceUpdate,
    Session,
    SessionCreate,
    Patient,
    PatientCreate,
    NeuralData,
    Analysis,
    MLModel,
    PaginatedResponse,
)
from .exceptions import (
    NeuraScaleError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
)

logger = logging.getLogger(__name__)


class NeuraScaleClient:
    """NeuraScale API client."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.neurascale.com",
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        """
        Initialize NeuraScale client.

        Args:
            api_key: API authentication key
            base_url: Base URL for the API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

        # Configure HTTP client
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "NeuraScale-Python-SDK/2.0.0",
            },
            timeout=httpx.Timeout(timeout),
            follow_redirects=True,
        )

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        retry_count: int = 0,
    ) -> httpx.Response:
        """
        Make an HTTP request with retry logic.

        Args:
            method: HTTP method
            path: API path
            params: Query parameters
            json: JSON body
            retry_count: Current retry attempt

        Returns:
            HTTP response

        Raises:
            NeuraScaleError: On API errors
        """
        try:
            response = await self.client.request(
                method=method,
                url=path,
                params=params,
                json=json,
            )

            # Handle rate limiting
            if response.status_code == 429:
                if retry_count < self.max_retries:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    logger.warning(f"Rate limited, retrying after {retry_after}s")
                    await asyncio.sleep(retry_after)
                    return await self._request(
                        method, path, params, json, retry_count + 1
                    )
                raise RateLimitError("Rate limit exceeded", retry_after=retry_after)

            # Handle other errors
            if response.status_code >= 400:
                error_data = response.json() if response.content else {}

                if response.status_code == 401:
                    raise AuthenticationError(
                        error_data.get("error", {}).get(
                            "message", "Authentication failed"
                        )
                    )
                elif response.status_code == 404:
                    raise NotFoundError(
                        error_data.get("error", {}).get("message", "Resource not found")
                    )
                elif response.status_code == 422:
                    raise ValidationError(
                        error_data.get("error", {}).get("message", "Validation failed"),
                        details=error_data.get("error", {}).get("details"),
                    )
                else:
                    raise NeuraScaleError(
                        f"API error: {response.status_code}",
                        status_code=response.status_code,
                        response=error_data,
                    )

            return response

        except httpx.TimeoutException:
            if retry_count < self.max_retries:
                logger.warning(
                    f"Request timeout, retry {retry_count + 1}/{self.max_retries}"
                )
                await asyncio.sleep(2**retry_count)  # Exponential backoff
                return await self._request(method, path, params, json, retry_count + 1)
            raise NeuraScaleError("Request timeout")

        except httpx.RequestError as e:
            raise NeuraScaleError(f"Request failed: {e}")

    # Device methods
    async def get_device(self, device_id: str) -> Device:
        """Get a device by ID."""
        response = await self._request("GET", f"/api/v2/devices/{device_id}")
        return Device(**response.json())

    async def list_devices(
        self,
        status: Optional[str] = None,
        type: Optional[str] = None,
        search: Optional[str] = None,
        page: int = 1,
        size: int = 50,
    ) -> PaginatedResponse[Device]:
        """List devices with filtering."""
        params = {
            "page": page,
            "size": size,
        }
        if status:
            params["status"] = status
        if type:
            params["type"] = type
        if search:
            params["search"] = search

        response = await self._request("GET", "/api/v2/devices", params=params)
        data = response.json()

        return PaginatedResponse(
            items=[Device(**item) for item in data["items"]],
            total=data["total"],
            page=data["page"],
            size=data["size"],
            pages=data["pages"],
        )

    async def create_device(self, device: DeviceCreate) -> Device:
        """Create a new device."""
        response = await self._request("POST", "/api/v2/devices", json=device.dict())
        return Device(**response.json())

    async def update_device(self, device_id: str, update: DeviceUpdate) -> Device:
        """Update a device."""
        response = await self._request(
            "PATCH",
            f"/api/v2/devices/{device_id}",
            json=update.dict(exclude_unset=True),
        )
        return Device(**response.json())

    async def delete_device(self, device_id: str) -> None:
        """Delete a device."""
        await self._request("DELETE", f"/api/v2/devices/{device_id}")

    async def calibrate_device(
        self, device_id: str, parameters: Dict[str, Any]
    ) -> Device:
        """Calibrate a device."""
        response = await self._request(
            "POST", f"/api/v2/devices/{device_id}/calibration", json=parameters
        )
        return Device(**response.json())

    # Session methods
    async def get_session(self, session_id: str) -> Session:
        """Get a session by ID."""
        response = await self._request("GET", f"/api/v2/sessions/{session_id}")
        return Session(**response.json())

    async def list_sessions(
        self,
        patient_id: Optional[str] = None,
        device_id: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        size: int = 50,
    ) -> PaginatedResponse[Session]:
        """List sessions with filtering."""
        params = {
            "page": page,
            "size": size,
        }
        if patient_id:
            params["patient_id"] = patient_id
        if device_id:
            params["device_id"] = device_id
        if status:
            params["status"] = status
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()

        response = await self._request("GET", "/api/v2/sessions", params=params)
        data = response.json()

        return PaginatedResponse(
            items=[Session(**item) for item in data["items"]],
            total=data["total"],
            page=data["page"],
            size=data["size"],
            pages=data["pages"],
        )

    async def create_session(self, session: SessionCreate) -> Session:
        """Create a new session."""
        response = await self._request("POST", "/api/v2/sessions", json=session.dict())
        return Session(**response.json())

    async def start_session(self, session_id: str) -> Session:
        """Start a recording session."""
        response = await self._request("POST", f"/api/v2/sessions/{session_id}/start")
        return Session(**response.json())

    async def stop_session(self, session_id: str) -> Session:
        """Stop a recording session."""
        response = await self._request("POST", f"/api/v2/sessions/{session_id}/stop")
        return Session(**response.json())

    async def export_session(
        self,
        session_id: str,
        format: str,
        channels: Optional[List[int]] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Export session data."""
        export_data = {"format": format}
        if channels:
            export_data["channels"] = channels
        if start_time is not None:
            export_data["start_time"] = start_time
        if end_time is not None:
            export_data["end_time"] = end_time

        response = await self._request(
            "POST", f"/api/v2/sessions/{session_id}/export", json=export_data
        )
        return response.json()

    # Neural data methods
    async def get_neural_data(
        self,
        session_id: str,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        channels: Optional[List[int]] = None,
        downsample: Optional[int] = None,
    ) -> NeuralData:
        """Get neural data for a session."""
        params = {}
        if start_time is not None:
            params["start_time"] = start_time
        if end_time is not None:
            params["end_time"] = end_time
        if channels:
            params["channels"] = ",".join(map(str, channels))
        if downsample:
            params["downsample"] = downsample

        response = await self._request(
            "GET", f"/api/v2/neural-data/sessions/{session_id}", params=params
        )
        return NeuralData(**response.json())

    async def stream_neural_data(
        self, session_id: str, channels: Optional[List[int]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream real-time neural data.

        Args:
            session_id: Session ID
            channels: Optional list of channels to stream

        Yields:
            Neural data frames
        """
        # Get WebSocket URL
        params = {}
        if channels:
            params["channels"] = ",".join(map(str, channels))

        response = await self._request(
            "GET", f"/api/v2/neural-data/sessions/{session_id}/stream", params=params
        )
        stream_info = response.json()

        # In production, would connect to WebSocket
        # For now, mock implementation
        for i in range(10):
            yield {
                "timestamp": datetime.utcnow().isoformat(),
                "channels": channels or list(range(32)),
                "data": [[0.0] * 64 for _ in range(len(channels) if channels else 32)],
            }
            await asyncio.sleep(0.25)

    # Patient methods
    async def get_patient(self, patient_id: str) -> Patient:
        """Get a patient by ID."""
        response = await self._request("GET", f"/api/v2/patients/{patient_id}")
        return Patient(**response.json())

    async def create_patient(self, patient: PatientCreate) -> Patient:
        """Create a new patient."""
        response = await self._request("POST", "/api/v2/patients", json=patient.dict())
        return Patient(**response.json())

    # Analysis methods
    async def get_analysis(self, analysis_id: str) -> Analysis:
        """Get an analysis by ID."""
        response = await self._request("GET", f"/api/v2/analysis/{analysis_id}")
        return Analysis(**response.json())

    async def start_analysis(
        self,
        session_id: str,
        analysis_type: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Analysis:
        """Start a new analysis."""
        data = {
            "session_id": session_id,
            "type": analysis_type,
            "parameters": parameters or {},
        }
        response = await self._request("POST", "/api/v2/analysis", json=data)
        return Analysis(**response.json())

    # ML Model methods
    async def get_model(self, model_id: str) -> MLModel:
        """Get an ML model by ID."""
        response = await self._request("GET", f"/api/v2/ml-models/{model_id}")
        return MLModel(**response.json())

    async def predict(self, model_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make predictions using an ML model."""
        response = await self._request(
            "POST", f"/api/v2/ml-models/{model_id}/predict", json=data
        )
        return response.json()

    # Batch operations
    async def batch_operations(
        self, operations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Execute batch operations."""
        response = await self._request("POST", "/api/v2/batch", json=operations)
        return response.json()
