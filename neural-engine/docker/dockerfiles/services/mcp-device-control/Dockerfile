# Multi-stage Dockerfile for MCP Device Control Server
# Optimized for production with minimal attack surface

# Stage 1: Dependencies
FROM python:3.12-slim AS dependencies

WORKDIR /tmp

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libhdf5-dev \
    libopenblas-dev \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install requirements
COPY neural-engine/requirements-minimal.txt ./requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install -r requirements.txt

# Stage 2: Builder
FROM python:3.12-slim AS builder

WORKDIR /build

# Copy source code
COPY neural-engine/src ./src
COPY neural-engine/setup.py ./
COPY neural-engine/README.md ./

# Create a minimal setup for the MCP server
RUN python -m compileall src/mcp

# Stage 3: Runtime
FROM python:3.12-slim AS runtime

# Create non-root user for security
RUN groupadd -r mcp && useradd -r -g mcp -u 1001 mcp

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libhdf5-103 \
    libopenblas0 \
    liblapack3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from dependencies stage
COPY --from=dependencies /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
WORKDIR /app
COPY --from=builder /build/src ./src

# Copy configuration
COPY neural-engine/src/mcp/config/server_config.yaml ./config/server_config.yaml

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV MCP_SERVER_TYPE=device_control
ENV MCP_SERVER_PORT=9002
ENV MCP_CONFIG_PATH=/app/config/server_config.yaml

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Switch to non-root user
USER mcp

# Expose ports
EXPOSE 9002 8080

# Entry point for the MCP device control server
ENTRYPOINT ["python", "-m", "src.mcp.main", "--servers", "device_control"]
