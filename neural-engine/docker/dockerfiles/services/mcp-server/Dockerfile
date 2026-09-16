# Multi-stage Dockerfile for MCP Server
# Model Context Protocol server for neural data processing
# Using Alpine for minimal attack surface and small image size

# Stage 1: Dependencies
FROM python:3.13-alpine AS dependencies

WORKDIR /tmp

# Install build dependencies for Alpine
RUN apk update && \
    apk upgrade && \
    apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    linux-headers \
    libffi-dev \
    openssl-dev \
    # For async support
    libuv-dev \
    # For neural processing (Alpine packages)
    openblas-dev \
    lapack-dev \
    hdf5-dev \
    gfortran \
    make

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY neural-engine/requirements-minimal.txt ./
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements-minimal.txt && \
    pip install aiohttp uvloop

# Stage 2: Runtime
FROM python:3.13-alpine AS runtime

# Install runtime dependencies for Alpine
RUN apk update && \
    apk upgrade && \
    apk add --no-cache \
    # Runtime libraries
    openblas \
    lapack \
    hdf5 \
    libgfortran \
    libstdc++ \
    libuv \
    # Security and process management
    ca-certificates \
    tini

# Create non-root user
RUN addgroup -g 1000 neural && \
    adduser -u 1000 -G neural -D neural

# Copy virtual environment
COPY --from=dependencies /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy application code
COPY neural-engine/src/mcp ./mcp
COPY neural-engine/src/utils ./utils

# Set ownership
RUN chown -R neural:neural /app

# Switch to non-root user
USER neural

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Expose port
EXPOSE 8080

# Use tini as entrypoint to handle signals properly
ENTRYPOINT ["/sbin/tini", "--"]

# Run the MCP server
CMD ["python", "-m", "mcp.server"]
