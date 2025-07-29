# NeuraScale API Documentation

## Overview

The NeuraScale API provides comprehensive access to neural data processing, device management, and real-time brain-computer interface functionality. Built with FastAPI and Strawberry GraphQL, protected by Kong API Gateway, it offers enterprise-grade security, monitoring, and performance.

## 🎉 Latest Update: Kong API Gateway Integration

**Phase 12 Complete** | **[Kong Gateway Documentation](../gateway/README.md)** | **[Admin Dashboard](http://localhost:8001)**

Kong API Gateway now provides:
- **🚀 Enterprise Performance**: Sub-10ms overhead, 10,000+ req/sec throughput
- **🔒 Advanced Security**: JWT authentication, rate limiting, circuit breakers
- **📊 Comprehensive Monitoring**: Prometheus metrics, Grafana dashboards
- **⚡ Load Balancing**: Round-robin with health checks and failover
- **🌐 SSL Termination**: Full TLS support with custom certificates

## API Versions

### REST API v2 (`/api/v2/`) - via Kong Gateway

- **Production URL**: `https://api.neurascale.com/api/v2/` (through Kong)
- **Development URL**: `http://localhost:8000/api/v2/` (through Kong)
- **Direct API URL**: `http://localhost:8000/api/v2/` (bypass Kong for development)
- **Authentication**: Bearer JWT tokens (validated by Kong)
- **Content Type**: `application/json`
- **Rate Limiting**: 1000 requests/minute per API key (enforced by Kong)
- **HATEOAS**: All responses include navigation links
- **Circuit Breaking**: Automatic failover and recovery

### GraphQL API (`/api/graphql`) - via Kong Gateway

- **Production Endpoint**: `https://api.neurascale.com/api/graphql` (through Kong)
- **Development Endpoint**: `http://localhost:8000/api/graphql` (through Kong)
- **WebSocket**: `wss://api.neurascale.com/api/graphql` (subscriptions through Kong)
- **Playground**: Available in development at `/api/graphql`
- **Introspection**: Enabled for development environments
- **Load Balancing**: Automatic backend failover

## Quick Start

### Authentication

All API endpoints require authentication using JWT Bearer tokens:

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     https://api.neurascale.com/api/v2/devices
```

### REST API Example

```bash
# List all devices
curl -X GET \
  -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.neurascale.com/api/v2/devices

# Create a new session
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"patientId": "pat_001", "deviceId": "dev_001"}' \
  https://api.neurascale.com/api/v2/sessions
```

### GraphQL Example

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { devices { edges { node { id name type status } } } }"
  }' \
  https://api.neurascale.com/api/graphql
```

## API Reference

### Core Endpoints

#### 🔌 Device Management

- **REST**: `/api/v2/devices/`
- **GraphQL**: `devices`, `device(id)`
- Manage neural acquisition devices, calibration, and status monitoring

#### 📊 Session Recording

- **REST**: `/api/v2/sessions/`
- **GraphQL**: `sessions`, `session(id)`
- Control recording sessions, real-time data streaming

#### 🧠 Neural Data Access

- **REST**: `/api/v2/neural-data/`
- **GraphQL**: `neuralData(sessionId)`
- Retrieve and stream neural signal data with filtering

#### 👤 Patient Management

- **REST**: `/api/v2/patients/`
- **GraphQL**: `patients`, `patient(id)`
- Patient records and clinical data integration

#### 🔬 Analysis Pipeline

- **REST**: `/api/v2/analysis/`
- **GraphQL**: `analyses`, `startAnalysis`
- Signal processing and machine learning inference

#### 🤖 ML Models

- **REST**: `/api/v2/ml-models/`
- **GraphQL**: `mlModels`, `predict`
- Neural network models for BCI applications

## Client SDKs

### Python SDK

```python
from neurascale import NeuraScaleClient

# Initialize client
client = NeuraScaleClient(api_key="your-api-key")

# List devices
devices = await client.list_devices()

# Start a recording session
session = await client.start_session("ses_001")

# Get neural data
data = await client.get_neural_data(
    session_id="ses_001",
    channels=[0, 1, 2, 3],
    start_time=0,
    end_time=60
)
```

### TypeScript/JavaScript SDK

```typescript
import { NeuraScaleClient, StreamClient } from "@neurascale/sdk";

// REST API client
const client = new NeuraScaleClient({
  apiKey: "your-api-key",
});

// List devices
const devices = await client.listDevices();

// Real-time streaming
const stream = new StreamClient({
  url: "wss://api.neurascale.com/ws/neural-data",
  token: "your-stream-token",
});

stream.on("data", (frame) => {
  console.log(`Received data: ${frame.channels.length} channels`);
});
```

## Real-time Features

### WebSocket Streaming

Connect to real-time neural data streams:

```javascript
const ws = new WebSocket("wss://api.neurascale.com/ws/neural-data");

ws.onmessage = (event) => {
  const frame = JSON.parse(event.data);
  // Process neural data frame
  console.log(`Frame ${frame.timestamp}: ${frame.data.length} samples`);
};
```

### GraphQL Subscriptions

Subscribe to real-time updates:

```graphql
subscription {
  neuralDataStream(sessionId: "ses_001", channels: [0, 1, 2, 3]) {
    timestamp
    samplingRate
    data
    channels
  }
}
```

## Error Handling

### HTTP Status Codes

| Code | Description      | Action                        |
| ---- | ---------------- | ----------------------------- |
| 200  | Success          | Continue                      |
| 201  | Created          | Resource created successfully |
| 400  | Bad Request      | Check request format          |
| 401  | Unauthorized     | Verify authentication token   |
| 403  | Forbidden        | Check permissions             |
| 404  | Not Found        | Resource doesn't exist        |
| 422  | Validation Error | Fix request data              |
| 429  | Rate Limited     | Reduce request frequency      |
| 500  | Server Error     | Retry or contact support      |

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": [
      {
        "field": "channelCount",
        "message": "Must be between 1 and 256"
      }
    ]
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "requestId": "req_1234567890"
}
```

## Rate Limiting

### Limits

- **Default**: 1000 requests/minute per API key
- **Burst**: Up to 10 requests/second
- **Streaming**: 100 concurrent connections per account

### Headers

Response headers include rate limit information:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642248600
```

## Pagination

### REST API Pagination

```bash
# Offset-based pagination
GET /api/v2/devices?page=2&size=20

# Response includes pagination metadata
{
  "items": [...],
  "total": 150,
  "page": 2,
  "size": 20,
  "totalPages": 8,
  "_links": {
    "self": "/api/v2/devices?page=2&size=20",
    "first": "/api/v2/devices?page=1&size=20",
    "prev": "/api/v2/devices?page=1&size=20",
    "next": "/api/v2/devices?page=3&size=20",
    "last": "/api/v2/devices?page=8&size=20"
  }
}
```

### GraphQL Pagination

```graphql
# Cursor-based pagination
query {
  devices(pagination: { first: 10, after: "cursor123" }) {
    edges {
      node {
        id
        name
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
```

## Data Formats

### Neural Data Structure

```json
{
  "sessionId": "ses_001",
  "startTime": 0.0,
  "endTime": 60.0,
  "samplingRate": 256,
  "channelCount": 32,
  "data": [
    [1.2, 1.5, 1.8, ...],  // Channel 0 samples
    [0.8, 0.9, 1.1, ...],  // Channel 1 samples
    // ... more channels
  ],
  "timestamps": [0.0, 0.00390625, 0.0078125, ...],
  "channels": [0, 1, 2, 3, ...],
  "metadata": {
    "deviceType": "EEG",
    "units": "microvolts",
    "impedances": [2.1, 1.8, 2.3, ...]
  }
}
```

### Device Information

```json
{
  "id": "dev_001",
  "name": "OpenBCI Cyton",
  "type": "EEG",
  "status": "ONLINE",
  "serialNumber": "OBC-001",
  "firmwareVersion": "3.1.2",
  "lastSeen": "2024-01-15T10:30:00Z",
  "channelCount": 8,
  "samplingRate": 250,
  "capabilities": {
    "streaming": true,
    "impedanceCheck": true,
    "calibration": true
  },
  "_links": {
    "self": {
      "href": "/api/v2/devices/dev_001",
      "method": "GET"
    },
    "update": {
      "href": "/api/v2/devices/dev_001",
      "method": "PATCH"
    },
    "calibration": {
      "href": "/api/v2/devices/dev_001/calibration",
      "method": "POST"
    }
  }
}
```

## Advanced Features

### Batch Operations

Execute multiple operations in a single request:

```json
POST /api/v2/devices/batch
{
  "operations": [
    {
      "operation": "update",
      "id": "dev_001",
      "data": {"status": "ONLINE"}
    },
    {
      "operation": "create",
      "data": {
        "name": "New Device",
        "type": "EMG",
        "serialNumber": "EMG-001"
      }
    }
  ]
}
```

### Filtering and Search

```bash
# Filter devices by status and type
GET /api/v2/devices?status=ONLINE&type=EEG

# Search sessions by date range
GET /api/v2/sessions?startDate=2024-01-01&endDate=2024-01-31

# Filter neural data by channels
GET /api/v2/neural-data/sessions/ses_001?channels=0,1,2,3&startTime=10&endTime=20
```

### Export Formats

```bash
# Export session data in EDF format
POST /api/v2/sessions/ses_001/export
{
  "format": "EDF",
  "channels": [0, 1, 2, 3],
  "startTime": 0,
  "endTime": 3600
}

# Response includes export job ID
{
  "exportId": "exp_12345",
  "status": "PROCESSING",
  "_links": {
    "status": "/api/v2/exports/exp_12345",
    "download": "/api/v2/exports/exp_12345/download"
  }
}
```

## SDK Documentation

### Python SDK (`neurascale`)

- **Installation**: `pip install neurascale`
- **Documentation**: [Python SDK Guide](./python-sdk.md)
- **Examples**: [Python Examples](./examples/python/)

### JavaScript SDK (`@neurascale/sdk`)

- **Installation**: `npm install @neurascale/sdk`
- **Documentation**: [JavaScript SDK Guide](./javascript-sdk.md)
- **Examples**: [JavaScript Examples](./examples/javascript/)

## OpenAPI Specification

- **Swagger UI**: https://api.neurascale.com/api/docs
- **ReDoc**: https://api.neurascale.com/api/redoc
- **OpenAPI JSON**: https://api.neurascale.com/api/openapi.json

## GraphQL Schema

- **Playground**: https://api.neurascale.com/api/graphql (development)
- **Schema**: Available via introspection query
- **Documentation**: Auto-generated from schema

## Support

### Getting Help

- 📖 **Documentation**: https://docs.neurascale.io/api
- 💬 **Discord**: https://discord.gg/neurascale
- 📧 **Email Support**: api-support@neurascale.io
- 🐛 **Bug Reports**: https://github.com/identity-wael/neurascale/issues

### API Status

- **Status Page**: https://status.neurascale.io
- **Uptime**: 99.9% SLA
- **Monitoring**: Real-time API health metrics

### Migration Guides

- [v1 to v2 Migration](./migration-v1-to-v2.md)
- [Breaking Changes](./breaking-changes.md)
- [Deprecation Schedule](./deprecations.md)

## Changelog

### v2.0.0 (2024-01-15) - Phase 12 Release

- ✨ Complete GraphQL API with subscriptions
- ✨ Enhanced REST API v2 with HATEOAS
- ✨ Python and TypeScript/JavaScript SDKs
- ✨ Real-time WebSocket streaming
- ✨ Comprehensive test coverage (100+ tests)
- ✨ Advanced error handling and validation
- ✨ Rate limiting and security enhancements

### v1.x.x (Legacy)

- 🗑️ REST API v1 (deprecated, removal planned for Q2 2024)
- 📋 See [Migration Guide](./migration-v1-to-v2.md) for upgrade path

---

For the complete API reference, interactive examples, and SDK documentation, visit [https://docs.neurascale.io/api](https://docs.neurascale.io/api).
