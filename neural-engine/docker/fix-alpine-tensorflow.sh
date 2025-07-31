#!/bin/bash
# Fix Alpine compatibility issues with TensorFlow/PyTorch

echo "Fixing Alpine compatibility for ML services..."

# Services that need TensorFlow/PyTorch should use slim, not Alpine
cd /Users/weg/NeuraScale/neurascale/neural-engine/docker

# Revert processor and ml-pipeline to use slim
for dockerfile in Dockerfile.processor dockerfiles/services/ml-pipeline/Dockerfile; do
    if [[ -f "$dockerfile" ]]; then
        echo "Reverting $dockerfile to slim for ML compatibility..."
        sed -i.alpine-backup 's/FROM python:3.12-alpine/FROM python:3.12-slim-bookworm/g' "$dockerfile"
        sed -i 's/apk add --no-cache/apt-get update \&\& apt-get install -y --no-install-recommends/g' "$dockerfile"
        sed -i 's/build-base/build-essential/g' "$dockerfile"
        sed -i 's/musl-dev/libffi-dev/g' "$dockerfile"
        sed -i 's/addgroup -S neural/groupadd -r neural/g' "$dockerfile"
        sed -i 's/adduser -S neural -G neural/useradd -r -g neural -m neural/g' "$dockerfile"
        # Add cleanup for apt
        sed -i '/apt-get install/a\    && apt-get clean \\' "$dockerfile"
        sed -i '/apt-get clean/a\    && rm -rf /var/lib/apt/lists/*' "$dockerfile"
    fi
done

echo "Services can now be categorized as:"
echo "- Alpine-based (no ML): api-gateway, mcp-server, ingestion"
echo "- Slim-based (with ML): processor, ml-pipeline"
