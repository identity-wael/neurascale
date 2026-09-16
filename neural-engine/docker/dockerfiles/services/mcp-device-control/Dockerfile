# Multi-stage Dockerfile for MCP Device Control Server
# Optimized for production with minimal attack surface
# Uses NVIDIA CUDA base for HDF5 and numpy compatibility

# Stage 1: Dependencies
FROM nvidia/cuda:12.6.0-runtime-ubuntu24.04 AS dependencies

# Install Python 3.13
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    python3.13 \
    python3.13-dev \
    python3.13-venv \
    python3-pip \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.13 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.13 1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp

# Install system dependencies and security updates
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    libhdf5-dev \
    libopenblas-dev \
    liblapack-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY neural-engine/requirements-minimal.txt ./requirements.txt
COPY neural-engine/constraints.txt ./constraints.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    python3.13 -m pip install --break-system-packages --upgrade pip && \
    python3.13 -m pip install --break-system-packages -c constraints.txt -r requirements.txt

# Stage 2: Builder
FROM nvidia/cuda:12.6.0-runtime-ubuntu24.04 AS builder

# Install Python 3.13
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    python3.13 \
    python3.13-dev \
    python3.13-venv \
    python3-pip \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.13 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.13 1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Security updates
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy source code
COPY neural-engine/src ./src
COPY neural-engine/setup.py ./
COPY neural-engine/README.md ./

# Create a minimal setup for the MCP server
RUN python -m compileall src/mcp

# Stage 3: Runtime
FROM nvidia/cuda:12.6.0-runtime-ubuntu24.04 AS runtime

# Install Python 3.13
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    python3.13 \
    python3.13-dev \
    python3.13-venv \
    python3-pip \
    && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.13 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.13 1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
# Security updates
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r mcp && useradd -r -g mcp -u 1001 mcp

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libhdf5-103-1t64 \
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
