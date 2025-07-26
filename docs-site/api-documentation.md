---
layout: doc
title: API Documentation
permalink: /api-documentation/
---

# NeuraScale API Documentation

## Overview

The NeuraScale API provides programmatic access to neural data processing capabilities, device management, and machine learning models. The API follows REST principles and supports both JSON and WebSocket protocols for real-time streaming.

## Base URL

```
https://api.neurascale.io/v1
```

## Authentication

All API requests require authentication using JWT tokens:

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     https://api.neurascale.io/v1/devices
```

### Obtaining a Token

```bash
POST /auth/token
Content-Type: application/json

{
  "client_id": "your_client_id",
  "client_secret": "your_client_secret",
  "grant_type": "client_credentials"
}
```

## Current Endpoints

### Device Management

#### List Devices

```bash
GET /devices
```

Returns all registered BCI devices.

**Response:**

```json
{
  "devices": [
    {
      "device_id": "dev_123",
      "name": "OpenBCI Cyton",
      "type": "openbci",
      "status": "connected",
      "channels": 8,
      "sample_rate": 250
    }
  ]
}
```

#### Get Device Status

```bash
GET /devices/{device_id}/status
```

**Response:**

```json
{
  "device_id": "dev_123",
  "connected": true,
  "battery_level": 85,
  "signal_quality": {
    "overall": "good",
    "channels": [
      { "channel": 1, "impedance": 5.2, "quality": "excellent" },
      { "channel": 2, "impedance": 7.8, "quality": "good" }
    ]
  },
  "streaming": true,
  "uptime_seconds": 3600
}
```

#### Connect Device

```bash
POST /devices/{device_id}/connect
```

Establishes connection to a BCI device.

#### Start Streaming

```bash
POST /devices/{device_id}/stream/start
```

**Request:**

```json
{
  "channels": [1, 2, 3, 4],
  "sample_rate": 250,
  "filters": {
    "notch": 60,
    "bandpass": [1, 50]
  }
}
```

### Data Ingestion

#### Ingest Neural Data

```bash
POST /ingest/neural-data
```

**Request:**

```json
{
  "device_id": "dev_123",
  "session_id": "sess_456",
  "timestamp": "2025-07-26T10:30:00Z",
  "data": {
    "eeg": [[0.1, 0.2, ...], [0.15, 0.25, ...]],
    "sample_rate": 250,
    "channels": 8
  },
  "metadata": {
    "task": "motor_imagery",
    "subject_id": "encrypted_id"
  }
}
```

**Response:**

```json
{
  "status": "accepted",
  "ingestion_id": "ing_789",
  "processing_time_ms": 45
}
```

### Sessions

#### Create Session

```bash
POST /sessions
```

**Request:**

```json
{
  "device_id": "dev_123",
  "subject_id": "encrypted_subject_id",
  "experiment_type": "motor_imagery",
  "duration_minutes": 30
}
```

#### Get Session Data

```bash
GET /sessions/{session_id}
```

**Response:**

```json
{
  "session_id": "sess_456",
  "status": "active",
  "start_time": "2025-07-26T10:00:00Z",
  "duration_seconds": 1800,
  "data_points": 450000,
  "quality_metrics": {
    "artifact_percentage": 2.5,
    "signal_quality": "good"
  }
}
```

## WebSocket API

For real-time streaming, connect to:

```
wss://api.neurascale.io/v1/stream
```

### Streaming Neural Data

```javascript
const ws = new WebSocket("wss://api.neurascale.io/v1/stream");

ws.on("open", () => {
  ws.send(
    JSON.stringify({
      type: "subscribe",
      device_id: "dev_123",
      channels: [1, 2, 3, 4],
    }),
  );
});

ws.on("message", (data) => {
  const packet = JSON.parse(data);
  // Process neural data packet
  console.log(`Timestamp: ${packet.timestamp}`);
  console.log(`Samples: ${packet.samples}`);
});
```

### Message Types

#### Data Packet

```json
{
  "type": "data",
  "device_id": "dev_123",
  "timestamp": 1627394400000,
  "samples": [[0.1, 0.2, 0.3, 0.4], ...],
  "sequence": 12345
}
```

#### Status Update

```json
{
  "type": "status",
  "device_id": "dev_123",
  "event": "impedance_check",
  "data": {
    "channel": 1,
    "impedance": 5.2,
    "quality": "excellent"
  }
}
```

## Planned Endpoints (Coming Soon)

### Machine Learning

#### Run Inference

```bash
POST /models/{model_id}/predict
```

**Request:**

```json
{
  "input_data": {
    "eeg": [[...]],
    "duration_ms": 1000
  },
  "model_version": "v2.1"
}
```

**Response:**

```json
{
  "predictions": {
    "class": "left_hand_movement",
    "confidence": 0.89,
    "probabilities": {
      "left_hand": 0.89,
      "right_hand": 0.08,
      "rest": 0.03
    }
  },
  "inference_time_ms": 23
}
```

### Signal Processing

#### Apply Filters

```bash
POST /processing/filter
```

**Request:**

```json
{
  "data": [[...]],
  "filters": [
    {"type": "bandpass", "low": 8, "high": 12},
    {"type": "notch", "frequency": 60}
  ]
}
```

### Dataset Management

#### List Datasets

```bash
GET /datasets
```

#### Create Dataset

```bash
POST /datasets
```

**Request:**

```json
{
  "name": "motor_imagery_study",
  "type": "eeg",
  "metadata": {
    "subjects": 20,
    "sessions_per_subject": 5,
    "sampling_rate": 250
  }
}
```

## Error Handling

The API uses standard HTTP status codes:

- `200 OK` - Request succeeded
- `201 Created` - Resource created
- `400 Bad Request` - Invalid request
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Access denied
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

### Error Response Format

```json
{
  "error": {
    "code": "INVALID_DEVICE_ID",
    "message": "Device with ID 'dev_999' not found",
    "details": {
      "device_id": "dev_999",
      "suggestion": "Check device ID or register device first"
    }
  }
}
```

## Rate Limiting

API requests are rate limited per client:

- **Standard**: 1000 requests per hour
- **Streaming**: 100 concurrent connections
- **Bulk Operations**: 100 requests per hour

Rate limit headers:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1627398000
```

## SDK Support

Official SDKs are available for:

- **Python**: `pip install neurascale`
- **JavaScript**: `npm install @neurascale/sdk`
- **Go**: `go get github.com/neurascale/go-sdk`

### Python Example

```python
from neurascale import Client

client = Client(api_key="your_api_key")

# List devices
devices = client.devices.list()

# Start streaming
stream = client.devices.stream("dev_123", channels=[1, 2, 3, 4])
for packet in stream:
    print(f"Received {len(packet.samples)} samples")
```

## Best Practices

1. **Use Compression**: Enable gzip for large payloads
2. **Batch Operations**: Group multiple operations when possible
3. **Handle Reconnection**: Implement exponential backoff for WebSocket
4. **Cache Responses**: Use ETags for conditional requests
5. **Monitor Rate Limits**: Track usage to avoid throttling

## API Changelog

### v1.0.0 (Current)

- Initial release with device management
- Basic data ingestion endpoints
- WebSocket streaming support

### v1.1.0 (Planned)

- Machine learning endpoints
- Advanced signal processing
- Dataset management API
- GraphQL support

---

_For integration examples and tutorials, see our [Developer Guide](/developer-guide/)_
