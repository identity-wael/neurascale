# Multi-stage Dockerfile for API Gateway Service
# FastAPI-based GraphQL/REST API gateway

# Stage 1: Dependencies
FROM python:3.12-slim AS dependencies

WORKDIR /tmp

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install requirements
# Use lightweight requirements for CI builds
COPY neural-engine/requirements-ci.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir \
        fastapi==0.109.0 \
        uvicorn[standard]==0.27.0 \
        graphene==3.3 \
        starlette-graphene3==0.6.0

# Stage 2: Builder
FROM python:3.12-slim AS builder

WORKDIR /app

# Copy virtual environment
COPY --from=dependencies /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy API gateway source
COPY neural-engine/src/api ./api
COPY neural-engine/src/utils ./utils
COPY neural-engine/src/processors ./processors
COPY neural-engine/src/devices ./devices

# Compile Python files
RUN python -m compileall -b .

# Stage 3: Runtime
FROM python:3.12-slim AS runtime

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r neural && useradd -r -g neural -m neural

WORKDIR /app

# Copy virtual environment
COPY --from=dependencies /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy compiled application
COPY --from=builder --chown=neural:neural /app .

# Create startup script
RUN echo '#!/bin/sh\nuvicorn api.app:app --host 0.0.0.0 --port 8080 --workers 4' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Switch to non-root user
USER neural

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the service
ENTRYPOINT ["/entrypoint.sh"]
