# Secure Python base image using distroless
# This provides maximum security with minimal attack surface

# Build stage - using Alpine for smaller build
FROM python:3.12-alpine AS builder

# Install build dependencies
RUN apk add --no-cache \
    build-base \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
WORKDIR /build
COPY requirements*.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Runtime stage - using distroless for security
FROM gcr.io/distroless/python3-debian12:nonroot

# Copy Python installation from builder
COPY --from=builder /opt/venv /opt/venv

# Set Python path
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"

# Copy application
WORKDIR /app
COPY --chown=nonroot:nonroot . .

# Run as non-root user (automatic in distroless nonroot image)
USER nonroot

# Note: HEALTHCHECK not supported in distroless
# Health checks should be configured at orchestration layer (k8s/Cloud Run)
