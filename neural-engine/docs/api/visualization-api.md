# Visualization API Documentation

## Overview

The Visualization API provides endpoints for controlling the NVIDIA Omniverse integration, enabling real-time 3D visualization of neural data with VR/AR support.

## Base URL

```
http://localhost:8080/api/v1/visualization
```

## Authentication

Currently, no authentication is required. This will be added in future versions.

## Endpoints

### Status

#### GET /status

Get the current status of the visualization system.

**Response:**
```json
{
  "connected": true,
  "session_id": "viz-123456",
  "visualization_mode": "surface_activity",
  "vr_enabled": false,
  "streaming_active": false,
  "timestamp": "2024-01-20T10:30:00Z"
}
```

### Connection Management

#### POST /connect

Connect to NVIDIA Omniverse server.

**Request:**
```json
{
  "nucleus_server": "localhost:3030",
  "project_path": "/neurascale/default"
}
```

**Response:**
```json
{
  "status": "connected",
  "session_id": "viz-123456",
  "nucleus_server": "localhost:3030",
  "project_path": "/neurascale/default"
}
```

#### POST /disconnect

Disconnect from NVIDIA Omniverse.

**Response:**
```json
{
  "status": "disconnected"
}
```

### Brain Model

#### POST /brain-model

Load a brain model for visualization.

**Request:**
```json
{
  "source": "template",  // "template", "mri_file", "ct_file"
  "file_path": "/path/to/mri.nii",  // Required for mri_file/ct_file
  "resolution": "medium"  // "low", "medium", "high"
}
```

**Response:**
```json
{
  "status": "loaded",
  "source": "template",
  "resolution": "medium",
  "vertex_count": 50000,
  "face_count": 100000
}
```

### Electrode Configuration

#### POST /electrodes

Set up electrode positions based on standard montages.

**Request:**
```json
{
  "montage": "10-20",  // "10-20", "10-10", "HD-128", "BCI-8x8", "BCI-16x16"
  "scale_to_head": true
}
```

**Response:**
```json
{
  "status": "configured",
  "montage": "10-20",
  "electrode_count": 19,
  "channels": ["Fp1", "Fp2", "F7", "F3", "Fz", "F4", "F8", ...]
}
```

### Real-time Streaming

#### POST /stream/start

Start real-time data streaming to the visualization.

**Request:**
```json
{
  "source": "live",  // "live", "file", "simulation"
  "sample_rate": 1000
}
```

**Response:**
```json
{
  "status": "streaming",
  "source": "live",
  "sample_rate": 1000
}
```

#### POST /stream/stop

Stop real-time data streaming.

**Response:**
```json
{
  "status": "stopped"
}
```

### Heatmap Generation

#### POST /heatmap/generate

Generate activity heatmap visualization.

**Request:**
```json
{
  "type": "2d_projection",  // "surface", "2d_projection", "volume"
  "values": {
    "Fp1": 0.8,
    "Fp2": 0.6,
    "F3": 0.9,
    // ... more electrode values
  },
  "colormap": "viridis",  // "viridis", "jet", "hot", "cool"
  "projection": "top"  // For 2d_projection: "top", "front", "side"
}
```

**Response:**
```json
{
  "status": "generated",
  "type": "2d_projection",
  "projection": "top",
  "shape": [100, 100],
  "colormap": "viridis"
}
```

### Connectivity Visualization

#### POST /flow/connectivity

Visualize functional connectivity between brain regions.

**Request:**
```json
{
  "matrix": [[1.0, 0.8, 0.3], [0.8, 1.0, 0.5], [0.3, 0.5, 1.0]],
  "channels": ["Fp1", "Fp2", "F3"],
  "threshold": 0.3,
  "frequency_band": "alpha"  // Optional: "delta", "theta", "alpha", "beta", "gamma"
}
```

**Response:**
```json
{
  "status": "generated",
  "flow_paths": 5,
  "threshold": 0.3,
  "frequency_band": "alpha"
}
```

### VR/AR Control

#### POST /vr/enable

Enable VR mode for immersive visualization.

**Request:**
```json
{
  "platform": "openxr"  // "openxr", "oculus", "steamvr"
}
```

**Response:**
```json
{
  "status": "enabled",
  "platform": "openxr",
  "controllers_detected": true
}
```

#### POST /vr/disable

Disable VR mode.

**Response:**
```json
{
  "status": "disabled"
}
```

### Animation

#### POST /animation/create

Create animations for visualization.

**Request:**
```json
{
  "type": "neural_activity",  // "neural_activity", "camera_orbit"
  "duration": 10.0,
  "frequency": 1.0,  // For neural_activity
  "amplitude": 1.0,  // For neural_activity
  "radius": 2.0,     // For camera_orbit
  "vertical_angle": 30.0  // For camera_orbit
}
```

**Response:**
```json
{
  "status": "created",
  "type": "neural_activity",
  "track_name": "neural_activity",
  "duration": 10.0
}
```

#### POST /animation/control

Control animation playback.

**Request:**
```json
{
  "action": "play",  // "play", "pause", "stop", "seek"
  "time": 5.0  // For seek action
}
```

**Response:**
```json
{
  "status": "play",
  "current_time": 0.0,
  "is_playing": true
}
```

### Settings

#### GET /settings

Get current visualization settings.

**Response:**
```json
{
  "visualization_mode": "surface_activity",
  "enable_vr": false,
  "enable_haptics": true,
  "quality_preset": "high",
  "max_fps": 60,
  "particle_limit": 100000
}
```

#### POST /settings

Update visualization settings.

**Request:**
```json
{
  "enable_vr": true,
  "quality_preset": "ultra",
  "max_fps": 90
}
```

**Response:**
```json
{
  "status": "updated"
}
```

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "error": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- 200: Success
- 400: Bad Request (invalid parameters)
- 404: Not Found
- 500: Internal Server Error
- 501: Not Implemented

## WebSocket Streaming

For real-time data streaming, connect to:

```
ws://localhost:8080/ws/visualization
```

Send neural data frames in the format:

```json
{
  "type": "neural_frame",
  "timestamp": 1234567890.123,
  "eeg_data": {
    "Fp1": [0.1, 0.2, 0.3, ...],
    "Fp2": [0.2, 0.3, 0.4, ...],
    // ... more channels
  },
  "sample_rate": 1000
}
```

## Example Usage

### Python Client

```python
import requests
import json

# Base URL
base_url = "http://localhost:8080/api/v1/visualization"

# Connect to Omniverse
response = requests.post(f"{base_url}/connect", json={
    "nucleus_server": "localhost:3030",
    "project_path": "/neurascale/demo"
})
print(response.json())

# Load brain model
response = requests.post(f"{base_url}/brain-model", json={
    "source": "template",
    "resolution": "high"
})
print(response.json())

# Set up electrodes
response = requests.post(f"{base_url}/electrodes", json={
    "montage": "10-20",
    "scale_to_head": True
})
print(response.json())

# Start streaming
response = requests.post(f"{base_url}/stream/start", json={
    "source": "simulation",
    "sample_rate": 1000
})
print(response.json())

# Enable VR
response = requests.post(f"{base_url}/vr/enable", json={
    "platform": "openxr"
})
print(response.json())
```

### JavaScript Client

```javascript
const baseUrl = 'http://localhost:8080/api/v1/visualization';

// Connect to Omniverse
fetch(`${baseUrl}/connect`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    nucleus_server: 'localhost:3030',
    project_path: '/neurascale/demo'
  })
})
.then(response => response.json())
.then(data => console.log(data));

// Generate heatmap
fetch(`${baseUrl}/heatmap/generate`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    type: '2d_projection',
    values: {
      'Fp1': 0.8,
      'Fp2': 0.6,
      'F3': 0.9
    },
    colormap: 'viridis',
    projection: 'top'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

## Best Practices

1. **Connection Lifecycle**: Always connect before loading models or streaming data
2. **Resource Management**: Disconnect when done to free GPU resources
3. **Streaming Rate**: Match sample rate to your data source to avoid buffer overflow
4. **VR Performance**: Use "medium" or "low" resolution for VR to maintain 90 FPS
5. **Error Handling**: Always check response status and handle errors appropriately

## Performance Considerations

- **Brain Model Resolution**:
  - Low: ~10k vertices (best for real-time VR)
  - Medium: ~50k vertices (balanced quality/performance)
  - High: ~200k vertices (best quality, may impact VR performance)

- **Streaming Rates**:
  - Up to 10kHz supported for raw data
  - Visualization updates at 60-90 FPS
  - Network latency should be <10ms for real-time feel

- **Particle Limits**:
  - Default: 100,000 particles
  - VR Mode: Recommend 50,000 or less
  - Can be adjusted via settings endpoint

## Future Enhancements

- Authentication and authorization
- Multi-user collaborative sessions
- Cloud rendering support
- Mobile AR support
- Advanced shader customization
- Neural network visualization
- Time-series playback controls