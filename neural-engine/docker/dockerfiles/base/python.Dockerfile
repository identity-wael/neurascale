# Base Python image for Neural Engine services
# Provides common Python runtime with scientific computing libraries

# Use Python 3.12 on Alpine for smaller size and fewer vulnerabilities
FROM python:3.12-alpine AS python-base

# Build arguments
ARG DEBIAN_FRONTEND=noninteractive
ARG PIP_NO_CACHE_DIR=1
ARG PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for Alpine
RUN apk add --no-cache \
    # Build essentials
    build-base \
    gcc \
    g++ \
    gfortran \
    # Scientific computing
    openblas-dev \
    lapack-dev \
    hdf5-dev \
    # Network and security
    ca-certificates \
    curl \
    # Python dependencies
    python3-dev \
    py3-pip \
    # Additional libs needed for Python packages
    libffi-dev \
    openssl-dev \
    # Clean up is automatic with --no-cache

# Create non-root user (Alpine uses addgroup/adduser)
RUN addgroup -S neural && adduser -S neural -G neural

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
