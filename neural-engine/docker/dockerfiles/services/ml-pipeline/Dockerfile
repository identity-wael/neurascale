# Multi-stage Dockerfile for ML Pipeline Service
# Python-based machine learning inference service with GPU support
#
# NOTE: Large ML frameworks (TensorFlow, PyTorch) should be:
# 1. Installed at runtime via pip when needed
# 2. Mounted as volumes from pre-built images
# 3. Or use specialized ML base images (nvidia/cuda, tensorflow/tensorflow)
# This keeps the base image smaller and CI builds faster

# Stage 1: Dependencies
FROM python:3.12-slim AS dependencies

WORKDIR /tmp

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libhdf5-dev \
    libopenblas-dev \
    gfortran \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install requirements
# Use lightweight requirements for CI builds
COPY neural-engine/requirements-ci.txt ./requirements.txt
# Install base requirements first
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Install only essential ML packages for CI builds
# For production, use Dockerfile.gpu with full ML frameworks
RUN pip install --no-cache-dir \
    scikit-learn==1.4.0 \
    xgboost==2.0.3 \
    joblib==1.3.2 \
    pandas==2.1.4 \
    numpy==1.26.4 \
    scipy==1.14.1

# Stage 2: Builder
FROM python:3.12-slim AS builder

WORKDIR /app

# Copy virtual environment
COPY --from=dependencies /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy ML pipeline source
COPY neural-engine/src/classification ./classification
COPY neural-engine/src/utils ./utils
COPY neural-engine/src/processors ./processors
COPY neural-engine/models ./models

# Compile Python files
RUN python -m compileall -b .

# Stage 3: Runtime
FROM python:3.12-slim AS runtime

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    libhdf5-103 \
    libopenblas0 \
    ca-certificates \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r neural && useradd -r -g neural -m neural

# Create model cache directory
RUN mkdir -p /app/model_cache && chown -R neural:neural /app/model_cache

WORKDIR /app

# Copy virtual environment
COPY --from=dependencies /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy compiled application
COPY --from=builder --chown=neural:neural /app .

# Environment variables for ML frameworks
ENV TF_CPP_MIN_LOG_LEVEL=2
ENV OMP_NUM_THREADS=4
ENV OPENBLAS_NUM_THREADS=4
ENV MKL_NUM_THREADS=4

# Create startup script
RUN echo '#!/bin/sh\npython -m classification.api --host 0.0.0.0 --port 8080' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Switch to non-root user
USER neural

# Expose ports
EXPOSE 8080 50051

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the service
ENTRYPOINT ["/entrypoint.sh"]
