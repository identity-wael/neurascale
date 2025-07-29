# NeuraScale TypeScript/JavaScript SDK

Official TypeScript/JavaScript SDK for the NeuraScale Neural Engine API.

## Installation

```bash
npm install @neurascale/sdk
# or
yarn add @neurascale/sdk
```

## Quick Start

```typescript
import { NeuraScaleClient } from "@neurascale/sdk";

const client = new NeuraScaleClient({
  apiKey: "your-api-key",
});

// List devices
const devices = await client.listDevices();
console.log(`Found ${devices.total} devices`);

// Get a session
const session = await client.getSession("ses_000001");
console.log(`Session status: ${session.status}`);

// Start an analysis
const analysis = await client.startAnalysis("ses_000001", "spectral_analysis", {
  frequencyBands: ["alpha", "beta", "gamma"],
});
console.log(`Analysis started: ${analysis.id}`);
```

## GraphQL Client

For complex queries, use the GraphQL client:

```typescript
import { GraphQLClient } from "@neurascale/sdk";

const graphql = new GraphQLClient({
  apiKey: "your-api-key",
});

// Custom query
const query = `
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
`;

const result = await graphql.query({
  query,
  variables: { id: "ses_000001" },
});
```

## Real-time Streaming

Stream neural data in real-time:

```typescript
import { StreamClient } from "@neurascale/sdk";

const stream = new StreamClient({
  url: "wss://api.neurascale.com/ws/neural-data",
  token: "your-stream-token",
});

// Connect and subscribe
await stream.connect();
stream.subscribeToSession("ses_000001", [0, 1, 2, 3]);

// Listen for data
stream.on("data", (frame) => {
  console.log(`Received ${frame.data.length} channels at ${frame.timestamp}`);
});

// Using async iterator
for await (const frame of stream.streamData()) {
  console.log(`Frame: ${frame.timestamp}`);
}
```

## Error Handling

```typescript
import {
  NeuraScaleClient,
  NotFoundError,
  RateLimitError,
} from "@neurascale/sdk";

try {
  const device = await client.getDevice("invalid_id");
} catch (error) {
  if (error instanceof NotFoundError) {
    console.error("Device not found");
  } else if (error instanceof RateLimitError) {
    console.error(`Rate limited, retry after ${error.retryAfter}s`);
  }
}
```

## Batch Operations

Execute multiple operations efficiently:

```typescript
const results = await client.batchOperations([
  {
    operation: "update",
    resource: "devices",
    data: { status: "ONLINE" },
  },
  {
    operation: "create",
    resource: "sessions",
    data: {
      patientId: "pat_001",
      deviceId: "dev_001",
      channelCount: 32,
      samplingRate: 256,
    },
  },
]);
```

## TypeScript Support

The SDK is written in TypeScript and provides full type definitions:

```typescript
import { Device, DeviceType, Session, SessionStatus } from "@neurascale/sdk";

const device: Device = {
  id: "dev_001",
  name: "EEG Device 1",
  type: DeviceType.EEG,
  status: DeviceStatus.ONLINE,
  // ... other properties
};
```

## Browser Usage

The SDK works in modern browsers with appropriate polyfills:

```html
<script type="module">
  import { NeuraScaleClient } from "https://cdn.neurascale.com/sdk/2.0.0/index.esm.js";

  const client = new NeuraScaleClient({
    apiKey: "your-api-key",
  });

  // Use the client
</script>
```

## Features

- Full TypeScript support with type definitions
- Promise-based async/await API
- Automatic retry with exponential backoff
- Rate limit handling
- Request cancellation with AbortController
- GraphQL client for complex queries
- WebSocket support for real-time data
- Works in Node.js and browsers
- Comprehensive error handling

## API Reference

Full API documentation: https://docs.neurascale.com/sdk/javascript

## License

MIT License - see LICENSE file for details.
