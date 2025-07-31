# Multi-stage Dockerfile for API Gateway Service
# FastAPI-based GraphQL/REST API gateway
# Using Debian slim for compatibility

# Stage 1: Dependencies
FROM python:3.12-slim-bookworm AS dependencies

WORKDIR /tmp

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install requirements
COPY neural-engine/requirements-minimal.txt ./requirements.txt
COPY neural-engine/constraints.txt ./constraints.txt
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -c constraints.txt -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim-bookworm AS runtime

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    ca-certificates \
    curl \
    tini \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r neural && useradd -r -g neural -m neural

# Copy virtual environment
COPY --from=dependencies /opt/venv /opt/venv

# Copy application code
WORKDIR /app
COPY --chown=neural:neural neural-engine/src ./src
COPY --chown=neural:neural neural-engine/api ./api

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    API_ENV=production

# Create necessary directories
RUN mkdir -p /app/logs && chown -R neural:neural /app

# Switch to non-root user
USER neural

# Expose ports
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Use tini for signal handling
ENTRYPOINT ["/sbin/tini", "--"]

# Start API Gateway
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
