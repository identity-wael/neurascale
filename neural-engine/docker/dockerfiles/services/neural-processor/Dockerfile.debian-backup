# Multi-stage Dockerfile for Neural Processor Service
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
# Use lightweight requirements for CI builds
COPY neural-engine/requirements-minimal.txt ./requirements.txt
COPY neural-engine/constraints.txt ./constraints.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install -c constraints.txt -r requirements.txt

# Stage 2: Builder
FROM python:3.12-slim AS builder

WORKDIR /app

# Copy virtual environment from dependencies stage
COPY --from=dependencies /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy only essential source files
COPY neural-engine/src ./src
COPY neural-engine/requirements.txt ./

# Compile Python files for optimization
RUN python -m compileall -b src/

# Stage 3: Runtime
FROM python:3.12-slim AS runtime

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    libhdf5-103 \
    libopenblas0 \
    ca-certificates \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/*

# Create non-root user
RUN groupadd -r neural && useradd -r -g neural -m neural

# Copy virtual environment
COPY --from=dependencies /opt/venv /opt/venv

# Copy compiled application
COPY --from=builder --chown=neural:neural /app /app

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    NEURAL_ENGINE_ENV=production \
    PYTHONPATH=/app

# Create necessary directories
RUN mkdir -p /app/logs /app/tmp && \
    chown -R neural:neural /app

WORKDIR /app

# Switch to non-root user
USER neural

# Expose ports
EXPOSE 8080 50051 9090

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Default command
CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8080"]
