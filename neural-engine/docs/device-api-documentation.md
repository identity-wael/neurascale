# Device Management REST API Documentation

## Overview

The Device Management API provides RESTful endpoints for managing neural data acquisition devices in the NeuraScale Neural Engine. It supports device discovery, connection management, health monitoring, and telemetry collection.

## Base URL

```
http://localhost:8080/api/v1/devices
```

## Authentication

Currently, the API does not require authentication. In production, implement appropriate authentication mechanisms.

## Endpoints

### Device Management

#### List All Devices

```http
GET /api/v1/devices/
```

**Response:**

```json
[
  {
    "device_id": "device1",
    "device_name": "OpenBCI Cyton",
    "state": "connected",
    "connected": true,
    "streaming": false,
    "capabilities": {
      "supported_sampling_rates": [250.0],
      "max_channels": 8,
      "signal_types": ["EEG"],
      "has_impedance_check": true,
      "has_battery_monitor": false
    }
  }
]
```

#### Get Device Information

```http
GET /api/v1/devices/{device_id}
```

**Response:**

```json
{
  "device_id": "device1",
  "device_name": "OpenBCI Cyton",
  "state": "streaming",
  "connected": true,
  "streaming": true,
  "session_id": "session_20240125_120000_abc123",
  "capabilities": {
    "supported_sampling_rates": [250.0],
    "max_channels": 8,
    "signal_types": ["EEG"],
    "has_impedance_check": true,
    "has_battery_monitor": false
  }
}
```

#### Add Device

```http
POST /api/v1/devices/
```

**Request Body:**

```json
{
  "device_id": "unique_device_id",
  "device_type": "brainflow",
  "device_config": {
    "board_name": "synthetic",
    "serial_port": "/dev/ttyUSB0"
  }
}
```

**Response:**

```json
{
  "device_id": "unique_device_id",
  "device_name": "BrainFlow-Synthetic",
  "state": "disconnected",
  "message": "Device unique_device_id added successfully"
}
```

#### Remove Device

```http
DELETE /api/v1/devices/{device_id}
```

**Response:**

```json
{
  "message": "Device device1 removed successfully"
}
```

### Device Control

#### Connect Device

```http
POST /api/v1/devices/{device_id}/connect
```

**Optional Request Body:**

```json
{
  "connection_params": {
    "timeout": 30
  }
}
```

**Response:**

```json
{
  "device_id": "device1",
  "connected": true,
  "message": "Device device1 connected successfully"
}
```

#### Disconnect Device

```http
POST /api/v1/devices/{device_id}/disconnect
```

**Response:**

```json
{
  "device_id": "device1",
  "connected": false,
  "message": "Device device1 disconnected successfully"
}
```

#### Start Streaming

```http
POST /api/v1/devices/{device_id}/stream/start
```

**Response:**

```json
{
  "device_id": "device1",
  "streaming": true,
  "session_id": "session_20240125_120000_abc123",
  "message": "Device device1 started streaming"
}
```

#### Stop Streaming

```http
POST /api/v1/devices/{device_id}/stream/stop
```

**Response:**

```json
{
  "device_id": "device1",
  "streaming": false,
  "message": "Device device1 stopped streaming"
}
```

### Device Discovery

#### Discover Devices

```http
GET /api/v1/devices/discover
```

**Query Parameters:**

- `timeout` (optional): Discovery timeout in seconds (default: 10)
- `protocols` (optional): Comma-separated list of protocols (serial,bluetooth,wifi,lsl)

**Response:**

```json
[
  {
    "device_type": "lsl",
    "device_id": "LSL_TestStream",
    "name": "LSL Stream: TestStream",
    "protocol": "lsl",
    "connection_info": {
      "name": "TestStream",
      "type": "EEG"
    },
    "metadata": {
      "channel_count": 8,
      "sampling_rate": 256.0
    }
  },
  {
    "device_type": "openbci",
    "device_id": "OpenBCI_/dev/ttyUSB0",
    "name": "OpenBCI Cyton",
    "protocol": "serial",
    "connection_info": {
      "port": "/dev/ttyUSB0"
    }
  }
]
```

#### Create Device from Discovery

```http
POST /api/v1/devices/discover/{discovery_id}/create
```

**Optional Request Body:**

```json
{
  "device_id": "custom_device_id"
}
```

**Response:**

```json
{
  "device_id": "custom_device_id",
  "device_name": "OpenBCI Cyton",
  "state": "disconnected",
  "message": "Device created successfully from discovery"
}
```

### Health Monitoring

#### Get Device Health

```http
GET /api/v1/devices/health
```

**Query Parameters:**

- `device_id` (optional): Specific device ID, or all devices if not provided

**Response:**

```json
{
  "device1": {
    "status": "healthy",
    "metrics": {
      "device_id": "device1",
      "timestamp": "2024-01-25T12:00:00Z",
      "connection": {
        "uptime_seconds": 300.5,
        "stability": 0.98,
        "reconnections": 0,
        "last_error": null
      },
      "data": {
        "packets_received": 15000,
        "packets_dropped": 2,
        "data_rate_hz": 256.0,
        "latency_ms": 4.2
      },
      "signal_quality": {
        "average_snr_db": 22.5,
        "channels_good": 7,
        "channels_total": 8,
        "last_impedance_check": "2024-01-25T11:55:00Z"
      },
      "resources": {
        "buffer_usage_percent": 12.5,
        "cpu_usage_percent": 5.2,
        "memory_usage_mb": 45.3
      },
      "battery": null
    }
  }
}
```

#### Get Health Alerts

```http
GET /api/v1/devices/health/alerts
```

**Query Parameters:**

- `device_id` (optional): Specific device ID

**Response:**

```json
[
  {
    "device_id": "device1",
    "severity": "degraded",
    "category": "health",
    "message": "Device degraded: stability 0.75",
    "timestamp": "2024-01-25T12:00:00Z",
    "metadata": {
      "metrics": {}
    }
  }
]
```

#### Start Health Monitoring

```http
POST /api/v1/devices/health/monitoring/start
```

**Response:**

```json
{
  "monitoring": true,
  "message": "Health monitoring started"
}
```

#### Stop Health Monitoring

```http
POST /api/v1/devices/health/monitoring/stop
```

**Response:**

```json
{
  "monitoring": false,
  "message": "Health monitoring stopped"
}
```

### Telemetry Collection

#### Start Telemetry Collection

```http
POST /api/v1/devices/telemetry/start
```

**Request Body:**

```json
{
  "output_dir": "/path/to/telemetry",
  "enable_cloud": false
}
```

**Response:**

```json
{
  "telemetry": true,
  "output_dir": "/path/to/telemetry",
  "cloud_enabled": false,
  "message": "Telemetry collection started"
}
```

#### Stop Telemetry Collection

```http
POST /api/v1/devices/telemetry/stop
```

**Response:**

```json
{
  "telemetry": false,
  "statistics": {
    "events_collected": 45230,
    "events_exported": 45200,
    "events_filtered": 30,
    "export_failures": 0
  },
  "message": "Telemetry collection stopped"
}
```

#### Get Telemetry Statistics

```http
GET /api/v1/devices/telemetry/stats
```

**Response:**

```json
{
  "events_collected": 45230,
  "events_exported": 45200,
  "events_filtered": 30,
  "export_failures": 0
}
```

### Session Management

#### Start Session

```http
POST /api/v1/devices/session/start
```

**Optional Request Body:**

```json
{
  "session_id": "custom_session_id"
}
```

**Response:**

```json
{
  "session_id": "session_20240125_120000_abc123",
  "started_at": "2024-01-25T12:00:00Z",
  "message": "Session started successfully"
}
```

#### End Session

```http
POST /api/v1/devices/session/end
```

**Response:**

```json
{
  "session_id": "session_20240125_120000_abc123",
  "ended_at": "2024-01-25T12:30:00Z",
  "message": "Session ended successfully"
}
```

#### Get Current Session

```http
GET /api/v1/devices/session
```

**Response:**

```json
{
  "session_id": "session_20240125_120000_abc123",
  "active": true
}
```

### Device-Specific Operations

#### Check Impedance

```http
GET /api/v1/devices/{device_id}/impedance
```

**Query Parameters:**

- `channels` (optional): Comma-separated list of channel IDs

**Response:**

```json
{
  "device_id": "device1",
  "impedances": {
    "0": {
      "value_ohms": 5200,
      "value_kohms": 5.2
    },
    "1": {
      "value_ohms": 4800,
      "value_kohms": 4.8
    }
  },
  "timestamp": "2024-01-25T12:00:00Z"
}
```

#### Get Signal Quality

```http
GET /api/v1/devices/{device_id}/signal-quality
```

**Query Parameters:**

- `channels` (optional): Comma-separated list of channel IDs

**Response:**

```json
{
  "device_id": "device1",
  "signal_quality": {
    "0": {
      "snr_db": 22.5,
      "quality_level": "good",
      "is_acceptable": true,
      "rms_amplitude": 12.3,
      "line_noise_power": 0.05,
      "artifacts_detected": 2
    },
    "1": {
      "snr_db": 18.2,
      "quality_level": "fair",
      "is_acceptable": true,
      "rms_amplitude": 10.1,
      "line_noise_power": 0.08,
      "artifacts_detected": 5
    }
  },
  "timestamp": "2024-01-25T12:00:00Z"
}
```

## Error Responses

All endpoints return appropriate HTTP status codes:

- `200 OK`: Successful GET request
- `201 Created`: Successful POST request that created a resource
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error
- `501 Not Implemented`: Feature not supported by device

Error response format:

```json
{
  "error": "Error message describing what went wrong"
}
```

## WebSocket Support

For real-time data streaming and notifications, WebSocket connections are planned but not yet implemented. Future versions will support:

- Real-time neural data streaming
- Health status updates
- Device state change notifications

## Usage Example

See `examples/device_api_example.py` for a complete example of using the API with Python's `requests` library.
