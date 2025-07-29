---
layout: doc
title: API Documentation
permalink: /api-documentation/
---

# NeuraScale API Documentation

## Overview

The NeuraScale API provides comprehensive access to neural data acquisition, processing, and analysis capabilities. Built on FastAPI with WebSocket support, it offers both RESTful endpoints and real-time streaming interfaces.

## Base URL

```
https://api.neurascale.io/v1
```

For local development:

```
http://localhost:8000/api/v1
```

## Authentication

All API requests require authentication via Bearer token:

```http
Authorization: Bearer YOUR_API_TOKEN
```

## REST API Reference

### Device Management

#### List All Devices

```http
GET /api/v1/devices
```

**Response:**

```json
[
  {
    "device_id": "openbci_cyton_1",
    "device_name": "OpenBCI Cyton",
    "device_type": "openbci",
    "state": "connected",
    "streaming": false,
    "capabilities": {
      "max_channels": 8,
      "supported_sampling_rates": [250],
      "has_impedance_check": true,
      "has_battery_monitor": true
    }
  }
]
```

#### Get Device Information

```http
GET /api/v1/devices/{device_id}
```

**Parameters:**

- `device_id` (string): Unique device identifier

**Response:**

```json
{
  "device_id": "openbci_cyton_1",
  "device_name": "OpenBCI Cyton",
  "state": "connected",
  "connected": true,
  "streaming": false,
  "session_id": "session_2025_01_27_123456",
  "capabilities": {
    "supported_sampling_rates": [250],
    "max_channels": 8,
    "signal_types": ["EEG", "EMG", "ECG"],
    "has_impedance_check": true,
    "has_battery_monitor": true
  },
  "telemetry": {
    "battery_level": 85,
    "temperature": 32.5,
    "uptime_seconds": 3600
  }
}
```

#### Add New Device

```http
POST /api/v1/devices
```

**Request Body:**

```json
{
  "device_id": "custom_device_1",
  "device_type": "openbci",
  "device_config": {
    "port": "/dev/ttyUSB0",
    "board_name": "cyton"
  }
}
```

**Response:**

```json
{
  "device_id": "custom_device_1",
  "device_name": "OpenBCI Cyton",
  "state": "disconnected",
  "message": "Device custom_device_1 added successfully"
}
```

### Device Control

#### Connect to Device

```http
POST /api/v1/devices/{device_id}/connect
```

**Request Body (optional):**

```json
{
  "connection_params": {
    "timeout": 30,
    "retry_count": 3
  }
}
```

**Response:**

```json
{
  "device_id": "openbci_cyton_1",
  "connected": true,
  "message": "Device openbci_cyton_1 connected successfully"
}
```

#### Start Streaming

```http
POST /api/v1/devices/{device_id}/stream/start
```

**Response:**

```json
{
  "device_id": "openbci_cyton_1",
  "streaming": true,
  "session_id": "session_2025_01_27_123456",
  "message": "Device openbci_cyton_1 started streaming"
}
```

### Device Operations

#### Check Impedance

```http
GET /api/v1/devices/{device_id}/impedance
```

**Query Parameters:**

- `channels` (string, optional): Comma-separated channel IDs (e.g., "0,1,2")

**Response:**

```json
{
  "device_id": "openbci_cyton_1",
  "impedances": {
    "0": { "value_ohms": 5000, "value_kohms": 5.0 },
    "1": { "value_ohms": 8000, "value_kohms": 8.0 },
    "2": { "value_ohms": 12000, "value_kohms": 12.0 }
  },
  "quality_summary": {
    "excellent": 1,
    "good": 1,
    "fair": 1,
    "poor": 0,
    "bad": 0
  },
  "timestamp": "2025-01-27T10:30:00Z"
}
```

#### Get Signal Quality

```http
GET /api/v1/devices/{device_id}/signal-quality
```

**Query Parameters:**

- `channels` (string, optional): Comma-separated channel IDs

**Response:**

```json
{
  "device_id": "openbci_cyton_1",
  "signal_quality": {
    "0": {
      "snr_db": 15.2,
      "quality_level": "GOOD",
      "is_acceptable": true,
      "rms_amplitude": 45.3,
      "line_noise_power": 0.12,
      "artifacts_detected": []
    },
    "1": {
      "snr_db": 12.8,
      "quality_level": "FAIR",
      "is_acceptable": true,
      "rms_amplitude": 38.7,
      "line_noise_power": 0.18,
      "artifacts_detected": ["EOG"]
    }
  },
  "timestamp": "2025-01-27T10:31:00Z"
}
```

### Device Discovery

#### Discover Available Devices

```http
GET /api/v1/devices/discover
```

**Query Parameters:**

- `timeout` (float, optional): Discovery timeout in seconds (default: 10)
- `protocols` (string, optional): Comma-separated protocols (serial,bluetooth,wifi,lsl)

**Response:**

```json
[
  {
    "device_type": "openbci",
    "device_name": "OpenBCI Cyton",
    "protocol": "serial",
    "connection_info": {
      "port": "/dev/ttyUSB0",
      "description": "OpenBCI Cyton",
      "vid": 1027,
      "pid": 24597
    },
    "discovered_at": "2025-01-27T10:30:00Z"
  },
  {
    "device_type": "lsl",
    "device_name": "LSL Stream: EEG",
    "protocol": "lsl",
    "connection_info": {
      "name": "EEG",
      "type": "EEG",
      "hostname": "lab-pc.local",
      "uid": "myuid123"
    },
    "metadata": {
      "channel_count": 32,
      "sampling_rate": 1000.0,
      "channel_format": "float32"
    }
  }
]
```

### Health & Telemetry

#### Get Device Health

```http
GET /api/v1/devices/health
```

**Query Parameters:**

- `device_id` (string, optional): Specific device ID

**Response:**

```json
{
  "overall_status": "healthy",
  "devices": {
    "openbci_cyton_1": {
      "status": "healthy",
      "uptime_seconds": 3600,
      "metrics": {
        "data_rate_hz": 250,
        "dropped_samples": 0,
        "buffer_usage": 0.15,
        "cpu_usage": 0.05
      },
      "last_error": null
    }
  },
  "system": {
    "cpu_percent": 15.2,
    "memory_mb": 1024,
    "active_streams": 1,
    "total_channels": 8
  }
}
```

#### Get Health Alerts

```http
GET /api/v1/devices/health/alerts
```

**Response:**

```json
[
  {
    "device_id": "openbci_cyton_1",
    "alert_type": "high_impedance",
    "severity": "warning",
    "message": "Channel 3 impedance above threshold (>25kΩ)",
    "timestamp": "2025-01-27T10:30:00Z",
    "data": {
      "channel": 3,
      "impedance_ohms": 28000
    }
  }
]
```

### Session Management

#### Start Recording Session

```http
POST /api/v1/session/start
```

**Request Body (optional):**

```json
{
  "session_id": "experiment_001",
  "metadata": {
    "subject_id": "S001",
    "experiment": "motor_imagery",
    "notes": "Baseline recording"
  }
}
```

**Response:**

```json
{
  "session_id": "experiment_001",
  "started_at": "2025-01-27T10:30:00Z",
  "message": "Session started successfully"
}
```

## WebSocket API

### Connection

```javascript
const ws = new WebSocket("ws://localhost:8000/ws");
```

### Message Types

#### Subscribe to Channels

```json
{
  "type": "subscribe",
  "channels": ["device_events", "data_stream", "telemetry"]
}
```

#### Device Events

```json
{
  "type": "device_connected",
  "device_id": "openbci_cyton_1",
  "timestamp": "2025-01-27T10:30:00Z",
  "data": {
    "device_name": "OpenBCI Cyton",
    "capabilities": {...}
  }
}
```

#### Streaming Data

```json
{
  "type": "data",
  "device_id": "openbci_cyton_1",
  "timestamp": "2025-01-27T10:30:00.123Z",
  "sequence": 12345,
  "data": {
    "channels": [
      [1.2, 2.3, 3.4, ...],  // Channel 0
      [2.1, 3.2, 4.3, ...],  // Channel 1
      ...
    ],
    "samples": 250,
    "sampling_rate": 250
  }
}
```

#### Impedance Results

```json
{
  "type": "impedance_check_complete",
  "device_id": "openbci_cyton_1",
  "timestamp": "2025-01-27T10:30:00Z",
  "data": {
    "impedance_values": {
      "0": 5000,
      "1": 8000,
      "2": 12000
    },
    "quality_summary": {
      "total_channels": 3,
      "good_channels": 2,
      "fair_channels": 1,
      "poor_channels": 0
    }
  }
}
```

#### Error Notifications

```json
{
  "type": "device_error",
  "device_id": "openbci_cyton_1",
  "severity": "error",
  "timestamp": "2025-01-27T10:30:00Z",
  "data": {
    "error_type": "ConnectionError",
    "message": "Device disconnected unexpectedly",
    "context": {
      "during": "streaming",
      "samples_lost": 250
    }
  }
}
```

### Binary Protocol

For high-frequency data streaming, use the binary WebSocket protocol:

```javascript
ws.binaryType = "arraybuffer";

// Send binary subscription
const encoder = new TextEncoder();
ws.send(
  encoder.encode(
    JSON.stringify({
      type: "subscribe_binary",
      device_id: "openbci_cyton_1",
    }),
  ),
);

// Receive binary data
ws.onmessage = (event) => {
  if (event.data instanceof ArrayBuffer) {
    // Parse binary header (16 bytes)
    const header = new DataView(event.data, 0, 16);
    const timestamp = header.getBigUint64(0, true);
    const sequence = header.getUint32(8, true);
    const channels = header.getUint16(12, true);
    const samples = header.getUint16(14, true);

    // Parse channel data (float32 array)
    const data = new Float32Array(event.data, 16);
    // Process data...
  }
};
```

## Error Handling

### Error Response Format

```json
{
  "error": "DeviceNotFound",
  "message": "Device with ID 'unknown_device' not found",
  "detail": {
    "device_id": "unknown_device",
    "available_devices": ["openbci_cyton_1", "synthetic_1"]
  },
  "timestamp": "2025-01-27T10:30:00Z"
}
```

### HTTP Status Codes

| Code | Description           |
| ---- | --------------------- |
| 200  | Success               |
| 201  | Created               |
| 400  | Bad Request           |
| 404  | Not Found             |
| 409  | Conflict              |
| 500  | Internal Server Error |
| 501  | Not Implemented       |
| 503  | Service Unavailable   |

### Common Error Types

- `DeviceNotFound`: Requested device doesn't exist
- `DeviceNotConnected`: Operation requires connected device
- `DeviceAlreadyStreaming`: Device is already streaming
- `InvalidConfiguration`: Invalid device configuration
- `OperationNotSupported`: Device doesn't support operation
- `ConnectionTimeout`: Connection attempt timed out

## Rate Limiting

API requests are rate limited to ensure fair usage:

- **REST API**: 1000 requests per minute per API key
- **WebSocket**: 10 connections per API key
- **Data streaming**: Unlimited once connected

Rate limit headers:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1706354400
```

## SDK Examples

### Python

```python
import neurascale

# Initialize client
client = neurascale.Client(api_key="YOUR_API_KEY")

# List devices
devices = client.devices.list()

# Connect to device
device = client.devices.get("openbci_cyton_1")
device.connect()

# Stream data
def on_data(data):
    print(f"Received {data.samples} samples from {data.channels} channels")

device.start_streaming(callback=on_data)
```

### JavaScript/TypeScript

```typescript
import { NeuraScale } from "@neurascale/sdk";

// Initialize client
const client = new NeuraScale({ apiKey: "YOUR_API_KEY" });

// Connect to device
const device = await client.devices.get("openbci_cyton_1");
await device.connect();

// Stream data
device.on("data", (data) => {
  console.log(`Received ${data.samples} samples`);
});

await device.startStreaming();
```

### MATLAB

```matlab
% Initialize client
client = neurascale.Client('YOUR_API_KEY');

% List devices
devices = client.listDevices();

% Connect and stream
device = client.getDevice('openbci_cyton_1');
device.connect();

% Set up callback
device.setDataCallback(@(data) processData(data));
device.startStreaming();

function processData(data)
    fprintf('Received %d samples\n', data.samples);
end
```

## Best Practices

### Connection Management

1. **Reuse connections**: Keep WebSocket connections open for streaming
2. **Handle reconnection**: Implement exponential backoff for reconnection
3. **Monitor health**: Use health endpoints to detect issues early

### Data Handling

1. **Buffer appropriately**: Use ring buffers for real-time processing
2. **Process asynchronously**: Don't block on data processing
3. **Handle gaps**: Detect and handle missing samples gracefully

### Error Recovery

1. **Retry with backoff**: Implement exponential backoff for failures
2. **Cache state**: Maintain device state locally for recovery
3. **Log comprehensively**: Log all errors with context for debugging

## Classification API

### Real-time Classification Endpoints

#### Mental State Classification

```http
POST /api/v1/classification/mental-state
```

**Request Body:**

```json
{
  "device_id": "openbci_cyton_1",
  "window_size_ms": 2000,
  "features": {
    "include_spectral": true,
    "include_temporal": true,
    "frequency_bands": ["alpha", "beta", "theta"]
  }
}
```

**Response:**

```json
{
  "timestamp": "2025-01-29T10:30:00Z",
  "confidence": 0.87,
  "label": "focus",
  "probabilities": {
    "focus": 0.87,
    "relaxation": 0.08,
    "stress": 0.04,
    "neutral": 0.01
  },
  "latency_ms": 45.2,
  "arousal_level": 0.72,
  "valence": 0.65,
  "attention_score": 0.89,
  "metadata": {
    "classifier_name": "mental_state",
    "feature_extraction_ms": 15.3,
    "classification_ms": 8.7
  }
}
```

#### Sleep Stage Detection

```http
POST /api/v1/classification/sleep-stage
```

**Request Body:**

```json
{
  "device_id": "openbci_cyton_1",
  "window_size_ms": 30000,
  "features": {
    "include_spindles": true,
    "include_k_complexes": true,
    "include_slow_waves": true
  }
}
```

**Response:**

```json
{
  "timestamp": "2025-01-29T10:30:00Z",
  "confidence": 0.94,
  "stage": "n2",
  "probabilities": {
    "wake": 0.01,
    "n1": 0.03,
    "n2": 0.94,
    "n3": 0.02,
    "rem": 0.0
  },
  "latency_ms": 67.8,
  "sleep_features": {
    "spindle_density": 2.3,
    "k_complex_count": 4,
    "slow_wave_activity": 0.67
  }
}
```

#### Motor Imagery Classification

```http
POST /api/v1/classification/motor-imagery
```

**Request Body:**

```json
{
  "device_id": "openbci_cyton_1",
  "window_size_ms": 1000,
  "channels": ["C3", "C4", "Cz"],
  "features": {
    "frequency_bands": ["mu", "beta"],
    "spatial_filters": true
  }
}
```

**Response:**

```json
{
  "timestamp": "2025-01-29T10:30:00Z",
  "confidence": 0.82,
  "action": "left_hand",
  "probabilities": {
    "left_hand": 0.82,
    "right_hand": 0.12,
    "feet": 0.04,
    "tongue": 0.01,
    "rest": 0.01
  },
  "latency_ms": 38.5,
  "lateralization_index": -0.65,
  "control_signal": {
    "strength": 0.82,
    "direction": "left"
  }
}
```

#### Seizure Prediction

```http
POST /api/v1/classification/seizure-prediction
```

**Request Body:**

```json
{
  "device_id": "openbci_cyton_1",
  "window_size_ms": 10000,
  "prediction_horizon_minutes": 15
}
```

**Response:**

```json
{
  "timestamp": "2025-01-29T10:30:00Z",
  "confidence": 0.23,
  "risk_level": "low",
  "probabilities": {
    "low": 0.77,
    "medium": 0.18,
    "high": 0.04,
    "imminent": 0.01
  },
  "latency_ms": 89.3,
  "warning_time_minutes": 15.0,
  "seizure_probability": 0.05,
  "preictal_features": {
    "connectivity_change": 0.12,
    "spectral_variance": 0.08,
    "synchrony_index": 0.15
  }
}
```

### Stream Classification

#### Start Real-time Classification

```http
POST /api/v1/classification/stream/start
```

**Request Body:**

```json
{
  "device_id": "openbci_cyton_1",
  "classifiers": ["mental_state", "motor_imagery"],
  "classification_interval_ms": 100,
  "buffer_size_ms": 5000
}
```

**Response:**

```json
{
  "stream_id": "classification_stream_123",
  "active_classifiers": ["mental_state", "motor_imagery"],
  "classification_rate_hz": 10,
  "expected_latency_ms": 45,
  "message": "Real-time classification started"
}
```

### WebSocket Classification Events

```json
{
  "type": "classification_result",
  "stream_id": "classification_stream_123",
  "classifier": "mental_state",
  "timestamp": "2025-01-29T10:30:00Z",
  "result": {
    "confidence": 0.87,
    "label": "focus",
    "probabilities": {
      "focus": 0.87,
      "relaxation": 0.08,
      "stress": 0.04,
      "neutral": 0.01
    },
    "latency_ms": 45.2
  }
}
```

## Changelog

### v1.8.0 (2025-01-29)

- **Phase 8 Implementation**: Real-time classification system
- Added mental state classification API
- Added sleep stage detection API
- Added motor imagery classification API
- Added seizure prediction API
- Implemented stream classification endpoints
- Google Vertex AI integration for scalable ML inference
- Sub-100ms latency for real-time classification

### v1.7.0 (2025-01-27)

- Added multi-device concurrent streaming
- Implemented real-time impedance checking
- Added automatic device discovery
- Enhanced WebSocket notification system
- Improved performance to <100ms latency

### v1.6.0 (2024-12-15)

- Added signal quality monitoring
- Implemented health monitoring system
- Added telemetry collection
- Enhanced error reporting

### v1.5.0 (2024-11-01)

- Initial REST API release
- WebSocket streaming support
- Basic device management

---

For more information, visit our [GitHub repository](https://github.com/identity-wael/neurascale) or contact [support@neurascale.io](mailto:support@neurascale.io).
