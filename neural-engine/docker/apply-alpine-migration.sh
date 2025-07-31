#!/bin/bash
# Apply Alpine migration to all service Dockerfiles

set -e

echo "Applying Alpine migration to service Dockerfiles..."

# Services directory
cd /Users/weg/NeuraScale/neurascale/neural-engine/docker/dockerfiles/services

# Function to backup and replace
migrate_dockerfile() {
    local service=$1
    if [[ -f "${service}/Dockerfile.alpine" ]]; then
        echo "Migrating ${service}..."
        # Backup original if not already done
        if [[ ! -f "${service}/Dockerfile.debian-backup" ]]; then
            mv "${service}/Dockerfile" "${service}/Dockerfile.debian-backup"
        fi
        # Use Alpine version
        cp "${service}/Dockerfile.alpine" "${service}/Dockerfile"
        echo "✓ ${service} migrated to Alpine"
    fi
}

# Migrate services that have Alpine versions
migrate_dockerfile "neural-processor"
migrate_dockerfile "api-gateway"
migrate_dockerfile "mcp-server"

# Update base Dockerfiles in the root docker directory
cd /Users/weg/NeuraScale/neurascale/neural-engine/docker

# Update main Dockerfiles to use Alpine
for dockerfile in Dockerfile.api Dockerfile.processor Dockerfile.ingestion Dockerfile.mcp-server; do
    if [[ -f "$dockerfile" ]]; then
        echo "Updating $dockerfile to use Alpine base..."
        sed -i.bak 's/FROM python:3.12-slim/FROM python:3.12-alpine/g' "$dockerfile"
        # Update apt-get to apk
        sed -i 's/apt-get update.*$/apk add --no-cache \\/' "$dockerfile"
        sed -i 's/apt-get install -y --no-install-recommends//' "$dockerfile"
        sed -i 's/&& rm -rf \/var\/lib\/apt\/lists\*//' "$dockerfile"
        # Update package names
        sed -i 's/build-essential/build-base/g' "$dockerfile"
        sed -i 's/libhdf5-dev/hdf5-dev/g' "$dockerfile"
        sed -i 's/libopenblas-dev/openblas-dev/g' "$dockerfile"
        sed -i 's/liblapack-dev/lapack-dev/g' "$dockerfile"
        # Update runtime packages
        sed -i 's/libhdf5-103/hdf5/g' "$dockerfile"
        sed -i 's/libopenblas0/openblas/g' "$dockerfile"
        sed -i 's/libgomp1/libgomp/g' "$dockerfile"
        # Update user creation
        sed -i 's/groupadd -r neural && useradd -r -g neural -m neural/addgroup -S neural \&\& adduser -S neural -G neural/g' "$dockerfile"
    fi
done

echo "Alpine migration complete!"
