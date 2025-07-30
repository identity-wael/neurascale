# Neural Engine CLI Docker Usage

The Neural Engine CLI is available as a Docker container for easy access to neural data processing tools without local installation.

## Quick Start

### Interactive Mode

Start an interactive session:

```bash
docker run -it --rm \
  --network neural-engine_neural-net \
  -v $(pwd)/data:/workspace/data \
  neurascale/neural-cli:latest
```

This drops you into a bash shell with the `neural-cli` command available.

### Direct Command Execution

Run a specific command:

```bash
docker run --rm \
  --network neural-engine_neural-net \
  -v $(pwd)/data:/workspace/data \
  neurascale/neural-cli:latest \
  connect --device openbci-cyton --port /dev/ttyUSB0
```

## Common Usage Patterns

### 1. Device Connection

```bash
# List available devices
docker run --rm --network neural-engine_neural-net \
  neurascale/neural-cli:latest list-devices

# Connect to a specific device
docker run -it --rm \
  --network neural-engine_neural-net \
  --device /dev/ttyUSB0:/dev/ttyUSB0 \
  neurascale/neural-cli:latest \
  connect --device openbci-cyton --port /dev/ttyUSB0
```

### 2. Data Streaming

```bash
# Stream data from connected device
docker run -it --rm \
  --network neural-engine_neural-net \
  -v $(pwd)/recordings:/workspace/recordings \
  neurascale/neural-cli:latest \
  stream --output /workspace/recordings/session.h5
```

### 3. Signal Processing

```bash
# Process recorded data
docker run --rm \
  -v $(pwd)/data:/workspace/data \
  neurascale/neural-cli:latest \
  process --input /workspace/data/raw.h5 \
          --output /workspace/data/processed.h5 \
          --filters bandpass:1-100 \
          --notch 60
```

### 4. Real-time Visualization

```bash
# Start visualization server
docker run -it --rm \
  --network neural-engine_neural-net \
  -p 8888:8888 \
  neurascale/neural-cli:latest \
  visualize --port 8888 --host 0.0.0.0
```

## Docker Compose Integration

Add to your `docker-compose.override.yml`:

```yaml
services:
  cli:
    image: neurascale/neural-cli:latest
    stdin_open: true
    tty: true
    networks:
      - neural-net
    volumes:
      - ./data:/workspace/data
      - ./config:/home/neural/.neural-cli
    environment:
      - API_URL=http://neural-processor:8080
      - MCP_URL=http://mcp-server:3001
    command: /bin/bash
```

Then run:

```bash
docker-compose run --rm cli
```

## Environment Variables

- `API_URL`: Neural Engine API endpoint (default: http://localhost:8080)
- `MCP_URL`: MCP Server endpoint (default: http://localhost:3001)
- `LOG_LEVEL`: Logging level (debug, info, warning, error)
- `NEURAL_CLI_HOME`: Configuration directory (default: ~/.neural-cli)

## Volume Mounts

### Required Volumes

- `/workspace/data`: Data directory for input/output files
- `/home/neural/.neural-cli`: CLI configuration and history

### Optional Volumes

- `/dev`: Device access for USB/serial devices (privileged mode required)
- `/workspace/models`: Pre-trained model directory

## Aliases

The container includes helpful aliases:

- `ncli`: Short for `neural-cli`
- `nec`: Short for `neural-cli connect`
- `nes`: Short for `neural-cli stream`
- `nep`: Short for `neural-cli process`

## Examples

### Complete Recording Session

```bash
# Start interactive session
docker-compose run --rm cli

# Inside container:
# 1. Check device connection
ncli list-devices

# 2. Connect to device
nec --device openbci-cyton --port /dev/ttyUSB0

# 3. Check signal quality
ncli check-impedance

# 4. Start recording
nes --duration 300 --output /workspace/data/session_001.h5

# 5. Process recording
nep --input /workspace/data/session_001.h5 \
    --bandpass 1-100 \
    --notch 60 \
    --output /workspace/data/session_001_processed.h5

# 6. Export for analysis
ncli export --input /workspace/data/session_001_processed.h5 \
           --format edf \
           --output /workspace/data/session_001.edf
```

### Batch Processing

```bash
# Process multiple files
for file in data/raw/*.h5; do
  docker run --rm \
    -v $(pwd)/data:/workspace/data \
    neurascale/neural-cli:latest \
    process --input /workspace/$file \
            --output /workspace/data/processed/$(basename $file) \
            --config /workspace/data/processing_config.yaml
done
```

## Troubleshooting

### Permission Issues

If you encounter permission issues with volumes:

```bash
# Run with user ID mapping
docker run -it --rm \
  --user $(id -u):$(id -g) \
  -v $(pwd)/data:/workspace/data \
  neurascale/neural-cli:latest
```

### Device Access

For USB device access:

```bash
# Run with privileged mode
docker run -it --rm --privileged \
  --device /dev/ttyUSB0 \
  neurascale/neural-cli:latest
```

### Network Issues

Ensure you're on the correct Docker network:

```bash
# List networks
docker network ls

# Run with specific network
docker run -it --rm \
  --network neural-engine_neural-net \
  neurascale/neural-cli:latest
```
