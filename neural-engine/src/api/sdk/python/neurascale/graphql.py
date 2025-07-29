"""GraphQL client for NeuraScale SDK."""

from typing import Optional, Dict, Any, List
import httpx

from .exceptions import NeuraScaleError


class GraphQLError(NeuraScaleError):
    """GraphQL query error."""

    def __init__(self, errors: List[Dict[str, Any]]):
        message = "GraphQL query failed"
        if errors:
            message = errors[0].get("message", message)
        super().__init__(message)
        self.errors = errors


class GraphQLClient:
    """GraphQL client for NeuraScale API."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.neurascale.com",
        timeout: float = 30.0,
    ):
        """
        Initialize GraphQL client.

        Args:
            api_key: API authentication key
            base_url: Base URL for the API
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.endpoint = f"{self.base_url}/graphql"
        self.timeout = timeout

        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(timeout),
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

    async def query(
        self, query: str, variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a GraphQL query.

        Args:
            query: GraphQL query string
            variables: Query variables

        Returns:
            Query result data

        Raises:
            GraphQLError: On query errors
        """
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        try:
            response = await self.client.post(self.endpoint, json=payload)
            response.raise_for_status()

            result = response.json()

            if "errors" in result:
                raise GraphQLError(result["errors"])

            return result.get("data", {})

        except httpx.HTTPStatusError as e:
            raise NeuraScaleError(f"HTTP error: {e.response.status_code}")
        except httpx.RequestError as e:
            raise NeuraScaleError(f"Request failed: {e}")

    async def mutation(
        self, mutation: str, variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a GraphQL mutation.

        Args:
            mutation: GraphQL mutation string
            variables: Mutation variables

        Returns:
            Mutation result data

        Raises:
            GraphQLError: On mutation errors
        """
        return await self.query(mutation, variables)

    async def subscribe(
        self, subscription: str, variables: Optional[Dict[str, Any]] = None
    ):
        """
        Subscribe to GraphQL subscription.

        Args:
            subscription: GraphQL subscription string
            variables: Subscription variables

        Returns:
            WebSocket connection for subscription

        Note:
            This would be implemented with websockets in production
        """
        # In production, would establish WebSocket connection
        # For now, raise NotImplementedError
        raise NotImplementedError("Subscriptions not yet implemented")

    # Convenience methods for common queries
    async def get_device(self, device_id: str) -> Dict[str, Any]:
        """Get device by ID."""
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
        result = await self.query(query, {"id": device_id})
        return result.get("device")

    async def list_devices(
        self,
        filter: Optional[Dict[str, Any]] = None,
        first: int = 10,
        after: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List devices with pagination."""
        query = """
            query ListDevices($filter: DeviceFilter, $first: Int, $after: String) {
                devices(filter: $filter, pagination: {first: $first, after: $after}) {
                    edges {
                        node {
                            id
                            name
                            type
                            status
                            serialNumber
                            lastSeen
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
        variables = {"first": first}
        if filter:
            variables["filter"] = filter
        if after:
            variables["after"] = after

        result = await self.query(query, variables)
        return result.get("devices")

    async def get_session_with_data(self, session_id: str) -> Dict[str, Any]:
        """Get session with nested data."""
        query = """
            query GetSessionWithData($id: String!) {
                session(id: $id) {
                    id
                    patientId
                    deviceId
                    startTime
                    endTime
                    duration
                    status
                    channelCount
                    samplingRate
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
        result = await self.query(query, {"id": session_id})
        return result.get("session")

    async def start_analysis(
        self,
        session_id: str,
        analysis_type: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Start an analysis."""
        mutation = """
            mutation StartAnalysis($input: StartAnalysisInput!) {
                startAnalysis(input: $input) {
                    analysis {
                        id
                        sessionId
                        type
                        status
                        createdAt
                    }
                    success
                    message
                }
            }
        """
        variables = {
            "input": {
                "sessionId": session_id,
                "type": analysis_type,
                "parameters": parameters or {},
            }
        }
        result = await self.mutation(mutation, variables)
        return result.get("startAnalysis", {})
