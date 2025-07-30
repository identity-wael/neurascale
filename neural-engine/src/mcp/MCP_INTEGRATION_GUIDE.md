# NeuraScale MCP Integration Guide

## Overview

NeuraScale implements Model Context Protocol (MCP) servers to provide secure, standardized access to neural data processing capabilities. This guide covers the four MCP servers available in the NeuraScale platform.

## Available MCP Servers

### 1. Neural Data MCP Server (Port 8100)

Provides access to neural data querying, processing, and analysis.

**Available Tools:**

- `query_sessions` - Search and filter recording sessions
- `get_neural_data` - Retrieve neural signal data
- `apply_filter` - Apply signal processing filters
- `run_spectral_analysis` - Perform spectral analysis
- `detect_artifacts` - Detect artifacts in neural data
- `export_neural_data` - Export data in various formats
- `create_visualization` - Generate data visualizations

### 2. Device Control MCP Server (Port 8101)

Manages BCI devices and recording operations.

**Available Tools:**

- `list_devices` - List available BCI devices
- `get_device_info` - Get detailed device information
- `connect_device` - Connect to a BCI device
- `disconnect_device` - Disconnect from a device
- `configure_device` - Configure device settings
- `start_recording` - Start data recording
- `stop_recording` - Stop data recording
- `check_impedance` - Check electrode impedances
- `monitor_signal_quality` - Monitor signal quality
- `run_device_diagnostics` - Run device diagnostics
- `calibrate_device` - Calibrate device

### 3. Clinical MCP Server (Port 8102)

Manages clinical workflows and patient data.

**Available Tools:**

- `create_patient_record` - Create new patient record
- `get_patient_record` - Retrieve patient information
- `update_patient_record` - Update patient data
- `create_treatment_plan` - Create treatment plan
- `record_treatment_session` - Record treatment session
- `generate_clinical_report` - Generate clinical reports
- `record_clinical_outcome` - Record outcome measures
- `track_patient_progress` - Track patient progress
- `get_clinical_protocols` - Get clinical protocols
- `check_treatment_compliance` - Check compliance
- `report_adverse_event` - Report adverse events

### 4. Analysis MCP Server (Port 8103)

Provides advanced neural data analysis and ML capabilities.

**Available Tools:**

- `compute_time_frequency` - Time-frequency analysis
- `analyze_connectivity` - Functional connectivity analysis
- `localize_sources` - Source localization
- `analyze_events` - Event-related analysis
- `train_classifier` - Train ML classifiers
- `predict_neural_states` - Predict neural states
- `run_deep_analysis` - Deep learning analysis
- `statistical_analysis` - Statistical analysis
- `discover_biomarkers` - Biomarker discovery
- `setup_realtime_analysis` - Real-time analysis
- `generate_analysis_report` - Generate reports

## Quick Start

### Running All MCP Servers

```bash
cd neural-engine
source venv/bin/activate
python -m mcp.main --servers neural_data device_control clinical analysis
```

### Running Individual Servers

```bash
# Neural Data Server
mcp-neural-data

# Device Control Server
mcp-device-control

# Clinical Server
mcp-clinical

# Analysis Server
mcp-analysis
```

### Docker Deployment

```bash
# Build and run all MCP servers
docker-compose -f docker/docker-compose.mcp.yml up -d

# Check server status
docker-compose -f docker/docker-compose.mcp.yml ps
```

## Configuration

MCP servers are configured through `src/mcp/config/server_config.yaml`:

```yaml
servers:
  neural_data:
    port: 8100
    host: "0.0.0.0"

  device_control:
    port: 8101
    host: "0.0.0.0"

  clinical:
    port: 8102
    host: "0.0.0.0"

  analysis:
    port: 8103
    host: "0.0.0.0"
```

## Authentication

MCP servers support multiple authentication methods:

1. **API Key Authentication**

   ```json
   {
     "method": "authenticate",
     "params": {
       "api_key": "your-api-key"
     }
   }
   ```

2. **JWT Token Authentication**
   ```json
   {
     "method": "authenticate",
     "params": {
       "token": "your-jwt-token"
     }
   }
   ```

## Example Usage

### Connecting to Neural Data Server

```python
import asyncio
import websockets
import json

async def query_neural_data():
    uri = "ws://localhost:8100"

    async with websockets.connect(uri) as websocket:
        # Initialize connection
        await websocket.send(json.dumps({
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "1.0",
                "clientInfo": {
                    "name": "my-client",
                    "version": "1.0"
                }
            },
            "id": 1
        }))

        # Query sessions
        await websocket.send(json.dumps({
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "query_sessions",
                "arguments": {
                    "patient_id": "patient_001",
                    "limit": 10
                }
            },
            "id": 2
        }))

        response = await websocket.recv()
        print(json.loads(response))

asyncio.run(query_neural_data())
```

### Using with Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "neurascale-neural-data": {
      "command": "mcp-neural-data",
      "cwd": "/path/to/neurascale/neural-engine"
    },
    "neurascale-device-control": {
      "command": "mcp-device-control",
      "cwd": "/path/to/neurascale/neural-engine"
    },
    "neurascale-clinical": {
      "command": "mcp-clinical",
      "cwd": "/path/to/neurascale/neural-engine"
    },
    "neurascale-analysis": {
      "command": "mcp-analysis",
      "cwd": "/path/to/neurascale/neural-engine"
    }
  }
}
```

## Health Monitoring

All MCP servers expose a health check endpoint:

```bash
# Check health status
curl http://localhost:8080/health

# Response
{
  "status": "healthy",
  "servers": {
    "neural_data": {"status": "running", "port": 8100},
    "device_control": {"status": "running", "port": 8101},
    "clinical": {"status": "running", "port": 8102},
    "analysis": {"status": "running", "port": 8103}
  }
}
```

## Security Considerations

1. **Rate Limiting**: All servers implement rate limiting to prevent abuse
2. **Permission System**: Fine-grained permissions control access to tools
3. **Audit Logging**: All operations are logged for compliance
4. **TLS Support**: Enable TLS in production environments
5. **API Key Rotation**: Regularly rotate API keys

## Troubleshooting

### Common Issues

1. **Connection Refused**

   - Check if servers are running: `lsof -i :8100,8101,8102,8103`
   - Verify firewall settings

2. **Authentication Failed**

   - Verify API key is correct
   - Check permissions for the user

3. **Tool Not Found**
   - Ensure you're connected to the correct server
   - Check tool permissions

### Debug Mode

Run servers with debug logging:

```bash
python -m mcp.main --log-level DEBUG
```

## Development

### Adding New Tools

1. Create handler method in appropriate `handlers.py` file
2. Register tool in server's `register_tools()` method
3. Add permissions in `server_config.yaml`
4. Update documentation

### Testing

```bash
# Run test script
python test_mcp_servers.py

# Run unit tests
pytest tests/mcp/
```

## Support

For issues or questions:

- GitHub Issues: https://github.com/identity-wael/neurascale/issues
- Documentation: https://neurascale.io/docs/mcp
- Email: support@neurascale.io
