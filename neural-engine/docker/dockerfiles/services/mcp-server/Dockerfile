# Multi-stage Dockerfile for MCP (Model Context Protocol) Server
# Provides neural data and device control services

# Stage 1: Dependencies
FROM python:3.12-slim AS dependencies

WORKDIR /tmp

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install requirements
COPY neural-engine/src/mcp/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Builder
FROM python:3.12-slim AS builder

WORKDIR /app

# Copy virtual environment
COPY --from=dependencies /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy MCP source code
COPY neural-engine/src/mcp ./mcp
COPY neural-engine/src/utils ./utils
COPY neural-engine/src/config ./config

# Compile Python files
RUN python -m compileall -b mcp/ utils/

# Stage 3: Runtime
FROM python:3.12-slim AS runtime

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    ca-certificates \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r neural && useradd -r -g neural -m neural

# Copy virtual environment
COPY --from=dependencies /opt/venv /opt/venv

# Copy application
COPY --from=builder --chown=neural:neural /app /app

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    MCP_ENV=production

# Create necessary directories
RUN mkdir -p /app/logs /app/cache && \
    chown -R neural:neural /app

WORKDIR /app

# Switch to non-root user
USER neural

# Expose MCP server port
EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3001/health || exit 1

# Run the MCP server
CMD ["python", "-m", "mcp.main", "--host", "0.0.0.0", "--port", "3001"]
