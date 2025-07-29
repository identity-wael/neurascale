# NeuraScale MCP (Model Context Protocol) Servers

This directory contains the MCP server implementations for the NeuraScale Neural Engine, enabling AI assistants like Claude to interact directly with neural data, control BCI devices, and execute clinical workflows through standardized tool interfaces.

## Overview

The NeuraScale MCP servers provide four specialized interfaces:

1. **Neural Data Server** (`neural_data`) - Data access, analysis, and processing
2. **Device Control Server** (`device_control`) - BCI device management and monitoring
3. **Clinical Workflow Server** (`clinical`) - Clinical protocol execution
4. **Analysis Server** (`analysis`) - Advanced neural data analysis

## Quick Start

### Installation

```bash
# Install from neural-engine directory
cd neural-engine
pip install -e .

# Or install MCP dependencies
pip install mcp websockets pyyaml numpy jsonschema
```

### Running Servers

```bash
# Start all MCP servers
python -m mcp.main

# Start specific servers
python -m mcp.main --servers neural_data device_control

# Start with custom configuration
python -m mcp.main --config /path/to/config.yaml --log-level DEBUG

# Start individual servers
python -c "from mcp.main import cli_neural_data; cli_neural_data()"
python -c "from mcp.main import cli_device_control; cli_device_control()"
```

### Claude Desktop Integration

Add to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "neurascale-neural": {
      "command": "python",
      "args": ["-c", "from mcp.main import cli_neural_data; cli_neural_data()"],
      "env": {
        "NEURASCALE_API_KEY": "your-api-key",
        "NEURAL_ENGINE_API_URL": "http://localhost:8000"
      }
    },
    "neurascale-devices": {
      "command": "python",
      "args": [
        "-c",
        "from mcp.main import cli_device_control; cli_device_control()"
      ],
      "env": {
        "NEURASCALE_API_KEY": "your-api-key"
      }
    }
  }
}
```

## Server Architecture

### Core Framework

All MCP servers inherit from `BaseNeuralMCPServer` which provides:

- **Authentication**: API key, JWT token, and session-based auth
- **Authorization**: Role-based permissions with resource-level access control
- **Rate Limiting**: Per-user, per-method limits with token bucket algorithm
- **Error Handling**: Standardized error responses and logging
- **Validation**: JSON schema validation for all tool inputs

### Neural Data Server

**Port**: 8100
**Tools Available**:

- `query_sessions` - Query recording sessions with filtering
- `get_neural_data` - Retrieve neural data from sessions
- `apply_filter` - Apply signal processing filters
- `run_spectral_analysis` - Perform spectral analysis
- `detect_artifacts` - Detect artifacts in neural data
- `export_neural_data` - Export data in various formats
- `create_visualization` - Generate plots and visualizations

**Example Usage**:

```python
# Query recent EEG sessions
result = await client.call_tool("query_sessions", {
    "device_type": "EEG",
    "start_date": "2025-01-01T00:00:00Z",
    "limit": 10
})

# Get neural data with filtering
data = await client.call_tool("get_neural_data", {
    "session_id": "session_001",
    "channels": [0, 1, 2, 3],
    "start_time": 10.0,
    "end_time": 20.0,
    "downsample_factor": 4
})
```

### Device Control Server

**Port**: 8101
**Tools Available**:

- `list_devices` - List available BCI devices
- `get_device_info` - Get detailed device information
- `connect_device` - Connect to a device
- `disconnect_device` - Disconnect from a device
- `configure_device` - Configure device settings
- `start_recording` - Start data recording
- `stop_recording` - Stop data recording
- `check_impedance` - Check electrode impedances
- `monitor_signal_quality` - Monitor real-time signal quality
- `run_device_diagnostics` - Run device diagnostics
- `calibrate_device` - Calibrate device settings

**Example Usage**:

```python
# List available devices
devices = await client.call_tool("list_devices", {
    "device_type": "EEG",
    "status": "connected"
})

# Start recording session
session = await client.call_tool("start_recording", {
    "device_id": "eeg_device_001",
    "duration": 300,  # 5 minutes
    "patient_id": "patient_123",
    "session_name": "Resting State EEG"
})
```

## Configuration

### Server Configuration (`config/server_config.yaml`)

Key configuration sections:

- **servers**: Port and host settings for each server
- **auth**: Authentication methods and API keys
- **permissions**: Role-based access control definitions
- **rate_limits**: Request rate limiting configuration
- **neural_engine**: Integration settings for neural engine API
- **logging**: Logging configuration and output settings

### Environment Variables

- `NEURASCALE_JWT_SECRET` - JWT signing secret
- `NEURAL_ENGINE_API_URL` - Neural engine API endpoint
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)

### Authentication

Three authentication methods supported:

1. **API Keys**: Long-lived keys for service accounts
2. **JWT Tokens**: Time-limited tokens for user sessions
3. **Session IDs**: Temporary session-based authentication

**Permissions System**: Role-based with granular permissions:

- `neural_data.*` - Neural data access and processing
- `devices.*` - Device control and management
- `recording.*` - Recording session control
- `analysis.*` - Data analysis capabilities
- `clinical.*` - Clinical workflow access

## Development

### Adding New Tools

1. Define tool in server's `register_tools()` method:

```python
self.register_tool(
    name="my_new_tool",
    handler=self._my_new_tool,
    description="Description of what the tool does",
    input_schema={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "Parameter description"}
        },
        "required": ["param1"]
    },
    permissions=["required.permission"]
)
```

2. Implement handler method:

```python
async def _my_new_tool(self, param1: str) -> Dict[str, Any]:
    # Validate inputs
    # Process request
    # Return results
    return {"result": "success", "data": processed_data}
```

### Testing

```bash
# Run MCP server tests
python -m pytest neural-engine/tests/mcp/

# Test individual servers
python -m pytest neural-engine/tests/mcp/test_neural_data_server.py
python -m pytest neural-engine/tests/mcp/test_device_control_server.py
```

### Mock Data

In development mode (`development.mock_data: true`), servers use realistic mock data:

- Synthetic neural signals with physiological characteristics
- Mock device status and capabilities
- Simulated recording sessions and metadata

## API Reference

### Common Response Format

All tools return responses in this format:

```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "JSON-formatted tool results"
      }
    ]
  },
  "id": "request-id"
}
```

### Error Responses

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32000,
    "message": "Error description",
    "type": "error_type",
    "timestamp": "2025-01-01T00:00:00Z"
  },
  "id": "request-id"
}
```

## Security

### GCP Secret Manager Integration

The MCP server integrates with Google Cloud Secret Manager for secure credential storage:

#### Configuration

Secrets are referenced in the configuration using GCP Secret Manager URIs:

```yaml
auth:
  api_key_salt: "gcp-secret://projects/${GCP_PROJECT_ID}/secrets/mcp-api-key-salt/versions/latest"
  jwt_secret: "gcp-secret://projects/${GCP_PROJECT_ID}/secrets/mcp-jwt-secret/versions/latest"
```

#### Setup Secrets

Use the provided script to create required secrets:

```bash
# Set your GCP project ID
export GCP_PROJECT_ID=your-project-id

# Run the setup script
./scripts/setup-mcp-secrets.sh
```

This script will:
- Enable the Secret Manager API
- Create secure random values for MCP secrets
- Set up appropriate IAM permissions
- Verify secret accessibility

#### Manual Secret Management

You can also manage secrets manually using the GCP CLI:

```bash
# Create a secret
gcloud secrets create mcp-api-key-salt --replication-policy="automatic"

# Add a secret version
echo -n "your-secret-value" | gcloud secrets versions add mcp-api-key-salt --data-file=-

# Access a secret
gcloud secrets versions access latest --secret="mcp-api-key-salt"
```

#### Required IAM Permissions

The service account running the MCP server needs:
- `roles/secretmanager.secretAccessor` - To read secret values

#### Environment Variables

- `GCP_PROJECT_ID` - Your Google Cloud project ID (required for secret resolution)

### Authentication Security

- API keys are hashed and salted using secrets from GCP Secret Manager
- JWT tokens have configurable expiration
- Sessions timeout after inactivity

### Permission Security

- All tools require explicit permissions
- Resource-level access control supported
- Default deny policy for undefined permissions

### Rate Limiting

- Per-user and per-method rate limits
- Token bucket algorithm for burst handling
- Configurable limits based on operation cost

### Network Security

- TLS 1.3 encryption for all connections
- Origin validation for WebSocket connections
- Audit logging for all operations

## Monitoring

### Logging

- Structured JSON logging for analysis
- Request/response logging with sanitization
- Performance metrics and timing data
- Error tracking and alerting

### Metrics

- Connection counts and client information
- Tool usage statistics and performance
- Rate limit hits and authentication failures
- System resource usage

## Troubleshooting

### Common Issues

1. **Connection Refused**

   - Check server is running: `netstat -an | grep 8100`
   - Verify firewall settings
   - Check configuration file syntax

2. **Authentication Failed**

   - Verify API key is correct
   - Check user permissions for requested operation
   - Ensure JWT token hasn't expired

3. **Rate Limited**

   - Check rate limit configuration
   - Implement exponential backoff in client
   - Consider upgrading user permissions

4. **Tool Not Found**
   - Verify server type supports the tool
   - Check tool name spelling
   - Ensure server started successfully

### Debug Mode

Enable debug mode for detailed logging:

```bash
python -m mcp.main --log-level DEBUG
```

## Contributing

1. Follow existing code patterns and naming conventions
2. Add comprehensive input validation for new tools
3. Include appropriate error handling and logging
4. Update documentation and tests for new features
5. Ensure security best practices are followed

## License

MIT License - see LICENSE file for details.
