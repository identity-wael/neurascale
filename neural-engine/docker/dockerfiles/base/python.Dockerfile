# Base Python image for Neural Engine services
# Provides common Python runtime with scientific computing libraries

# Use Python 3.12 on Debian slim for compatibility
FROM python:3.12-slim-bookworm AS python-base

# Build arguments
ARG DEBIAN_FRONTEND=noninteractive
ARG PIP_NO_CACHE_DIR=1
ARG PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for Debian
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build essentials
    build-essential \
    gcc \
    g++ \
    gfortran \
    # Scientific computing
    libopenblas-dev \
    liblapack-dev \
    libhdf5-dev \
    # Network and security
    ca-certificates \
    curl \
    # Python dependencies
    python3-dev \
    # Additional libs needed for Python packages
    libffi-dev \
    libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r neural && useradd -r -g neural -m neural

# Setup Python environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install base Python packages
RUN pip install --upgrade pip setuptools wheel

# Common scientific packages
RUN pip install \
    numpy==1.26.4 \
    scipy==1.13.0 \
    pandas==2.2.2 \
    scikit-learn==1.4.2 \
    h5py==3.11.0

# Create app directory
WORKDIR /app

# Switch to non-root user
USER neural

# Health check command
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1
