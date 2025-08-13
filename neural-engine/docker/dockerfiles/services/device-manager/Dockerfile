# Multi-stage Dockerfile for Device Manager Service
# Manages neural device connections and data streaming
# Uses Debian slim as device libraries need numpy for signal processing

# Stage 1: Dependencies
FROM python:3.13-slim AS dependencies

WORKDIR /tmp

# Install system dependencies and security updates
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    libusb-1.0-0-dev \
    libudev-dev \
    libhidapi-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install requirements
# Use lightweight requirements for CI builds
COPY neural-engine/requirements-minimal.txt ./requirements.txt
COPY neural-engine/constraints.txt ./constraints.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -c constraints.txt -r requirements.txt && \
    pip install --no-cache-dir \
        pyusb==1.2.1 \
        hidapi==0.14.0 \
        pylsl==1.16.0

# Stage 2: Builder
FROM python:3.13-slim AS builder
# Security updates
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy virtual environment
COPY --from=dependencies /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy device manager source
COPY neural-engine/src/devices ./devices
COPY neural-engine/src/utils ./utils
COPY neural-engine/devices ./legacy_devices

# Compile Python files
RUN python -m compileall -b devices/ utils/

# Stage 3: Runtime
FROM python:3.13-slim AS runtime
# Security updates
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libusb-1.0-0 \
    libudev1 \
    libhidapi-hidraw0 \
    ca-certificates \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r neural && useradd -r -g neural -m neural

# Create necessary directories
RUN mkdir -p /var/log/device-manager /etc/device-manager && \
    chown -R neural:neural /var/log/device-manager /etc/device-manager

WORKDIR /app

# Copy virtual environment
COPY --from=dependencies /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy compiled application
COPY --from=builder --chown=neural:neural /app .

# Create entrypoint script
RUN echo '#!/bin/sh\npython -m devices.device_manager "$@"' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Switch to non-root user
USER neural

# Expose ports
EXPOSE 8081 50052 9091

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8081/health || exit 1

# Run the service
ENTRYPOINT ["/entrypoint.sh"]
CMD ["--host", "0.0.0.0", "--port", "8081"]
