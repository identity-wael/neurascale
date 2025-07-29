# NeuraScale Python SDK

Official Python SDK for the NeuraScale Neural Engine API.

## Installation

```bash
pip install neurascale
```

## Quick Start

```python
import asyncio
from neurascale import NeuraScaleClient

async def main():
    # Initialize client
    async with NeuraScaleClient(api_key="your-api-key") as client:
        # List devices
        devices = await client.list_devices()
        for device in devices.items:
            print(f"Device: {device.name} ({device.status})")

        # Get a specific session
        session = await client.get_session("ses_000001")
        print(f"Session {session.id}: {session.status}")

        # Start an analysis
        analysis = await client.start_analysis(
            session_id="ses_000001",
            analysis_type="spectral_analysis",
            parameters={"frequency_bands": ["alpha", "beta", "gamma"]}
        )
        print(f"Analysis started: {analysis.id}")

# Run the async function
asyncio.run(main())
```

## GraphQL Client

For more complex queries, use the GraphQL client:

```python
from neurascale import GraphQLClient

async def graphql_example():
    async with GraphQLClient(api_key="your-api-key") as client:
        # Custom query
        query = """
            query GetSessionDetails($id: String!) {
                session(id: $id) {
                    id
                    status
                    device {
                        name
                        type
                    }
                    patient {
                        externalId
                    }
                }
            }
        """

        result = await client.query(query, {"id": "ses_000001"})
        print(result)
```

## Streaming Data

Stream real-time neural data:

```python
async def stream_example():
    async with NeuraScaleClient(api_key="your-api-key") as client:
        # Stream neural data
        async for frame in client.stream_neural_data(
            session_id="ses_000001",
            channels=[0, 1, 2, 3]
        ):
            print(f"Timestamp: {frame['timestamp']}")
            print(f"Data shape: {len(frame['data'])} channels")
```

## Error Handling

```python
from neurascale import NeuraScaleClient, NotFoundError, RateLimitError

async def error_handling():
    async with NeuraScaleClient(api_key="your-api-key") as client:
        try:
            device = await client.get_device("invalid_id")
        except NotFoundError:
            print("Device not found")
        except RateLimitError as e:
            print(f"Rate limited, retry after {e.retry_after} seconds")
```

## Features

- Async/await support
- Automatic retry with exponential backoff
- Rate limit handling
- Type hints and validation with Pydantic
- Both REST and GraphQL clients
- Real-time data streaming support
- Comprehensive error handling

## Documentation

Full documentation available at: https://docs.neurascale.com/sdk/python

## License

MIT License - see LICENSE file for details.
