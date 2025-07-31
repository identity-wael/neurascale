#!/bin/bash
# Script to migrate all Python service Dockerfiles to Alpine

set -e

SERVICES_DIR="dockerfiles/services"
BACKUP_SUFFIX=".debian-backup"

# List of services to migrate
SERVICES=(
    "api-gateway"
    "device-manager"
    "ml-pipeline"
    "mcp-server"
    "mcp-device-control"
    "mcp-neural-data"
)

echo "Starting migration to Alpine-based Dockerfiles..."

for SERVICE in "${SERVICES[@]}"; do
    DOCKERFILE_PATH="${SERVICES_DIR}/${SERVICE}/Dockerfile"

    if [[ -f "$DOCKERFILE_PATH" ]]; then
        echo "Migrating $SERVICE..."

        # Backup original
        if [[ ! -f "${DOCKERFILE_PATH}${BACKUP_SUFFIX}" ]]; then
            cp "$DOCKERFILE_PATH" "${DOCKERFILE_PATH}${BACKUP_SUFFIX}"
        fi

        # Create Alpine version based on the service type
        cat > "$DOCKERFILE_PATH" << 'EOF'
# Multi-stage Dockerfile for ${SERVICE}
# Using Alpine Linux for reduced vulnerabilities and smaller size

# Stage 1: Dependencies
FROM python:3.12-alpine AS dependencies

WORKDIR /tmp

# Install build dependencies
RUN apk add --no-cache \
    build-base gcc g++ musl-dev linux-headers \
    libffi-dev openssl-dev \
    openblas-dev lapack-dev hdf5-dev gfortran \
    postgresql-dev  # For database connections

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies
COPY neural-engine/requirements-minimal.txt ./
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements-minimal.txt

# Stage 2: Runtime
FROM python:3.12-alpine AS runtime

# Install runtime dependencies
RUN apk add --no-cache \
    openblas lapack hdf5 libgfortran libstdc++ \
    postgresql-libs ca-certificates curl tini

# Create non-root user
RUN addgroup -S neural && adduser -S neural -G neural

# Copy virtual environment
COPY --from=dependencies /opt/venv /opt/venv

# Copy application
WORKDIR /app
COPY --chown=neural:neural neural-engine/src ./src

# Environment
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Create directories
RUN mkdir -p /app/logs /app/tmp && chown -R neural:neural /app

USER neural
EXPOSE 8080 50051 9090

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["python", "-m", "src.services.${SERVICE}"]
EOF

        # Replace ${SERVICE} placeholder
        sed -i "s/\${SERVICE}/${SERVICE}/g" "$DOCKERFILE_PATH"

        echo "✓ Migrated $SERVICE"
    else
        echo "⚠ Dockerfile not found for $SERVICE"
    fi
done

echo "Migration complete! All services now use Alpine-based images."
