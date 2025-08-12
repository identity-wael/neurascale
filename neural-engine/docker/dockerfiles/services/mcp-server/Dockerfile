# Multi-stage Dockerfile for MCP Server
# Model Context Protocol server for neural data processing
# Using Debian slim for compatibility

# Stage 1: Dependencies
FROM python:3.12.11-slim-bookworm AS dependencies
# Security updates
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    # For async support
    libuv1-dev \
    # For neural processing
    libopenblas-dev \
    liblapack-dev \
    libhdf5-dev \
    gfortran \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY neural-engine/requirements-minimal.txt ./
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements-minimal.txt && \
    pip install aiohttp uvloop

# Stage 2: Runtime
FROM python:3.12.11-slim-bookworm AS runtime
# Security updates
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Runtime libraries
    libopenblas0 \
    liblapack3 \
    libhdf5-103 \
    libgfortran5 \
    libstdc++6 \
    libuv1 \
    # Security and networking
    ca-certificates \
    # Process management
    tini \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r neural && useradd -r -g neural -m neural

# Copy virtual environment
COPY --from=dependencies /opt/venv /opt/venv

# Copy MCP server code
WORKDIR /app
COPY --chown=neural:neural neural-engine/src/mcp ./src/mcp

# Environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    MCP_ENV=production

# Create necessary directories
RUN mkdir -p /app/logs /app/tmp && \
    chown -R neural:neural /app

# Switch to non-root user
USER neural

# Expose MCP server port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import aiohttp, asyncio; asyncio.run(aiohttp.ClientSession().get('http://localhost:3000/health'))" || exit 1

# Use tini for signal handling
ENTRYPOINT ["/sbin/tini", "--"]

# Start MCP server
CMD ["python", "-m", "src.mcp.servers.main", "--host", "0.0.0.0", "--port", "3000"]
