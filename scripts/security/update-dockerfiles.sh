#!/bin/bash

# Script to update all Dockerfiles with security fixes
# This script updates base images and adds security patches

set -e

echo "Updating Dockerfiles for security vulnerabilities..."

# Get the latest Python 3.12 base image tag
LATEST_PYTHON_TAG="3.12.11-slim-bookworm"
LATEST_ALPINE_TAG="3.12.11-alpine3.21"

# Find all Dockerfiles
DOCKERFILES=$(find neural-engine/docker -name "Dockerfile*" -type f | grep -v ".bak" | grep -v ".backup")

for dockerfile in $DOCKERFILES; do
    echo "Processing: $dockerfile"

    # Backup original
    cp "$dockerfile" "${dockerfile}.security-backup"

    # Check if it's an Alpine-based file
    if grep -q "alpine" "$dockerfile"; then
        # Update Alpine-based images
        sed -i.tmp "s/FROM python:3.12-alpine[^ ]*/FROM python:${LATEST_ALPINE_TAG}/g" "$dockerfile"
        sed -i.tmp "s/FROM alpine:[^ ]*/FROM alpine:3.21/g" "$dockerfile"

        # Ensure Alpine packages are updated
        if ! grep -q "apk upgrade" "$dockerfile"; then
            # Add apk upgrade after FROM statements
            awk '/^FROM.*alpine/ {print; print "RUN apk update && apk upgrade --no-cache && rm -rf /var/cache/apk/*"; next} {print}' "${dockerfile}.tmp" > "$dockerfile"
        fi
    else
        # Update Debian-based images
        sed -i.tmp "s/FROM python:3.12-slim[^ ]*/FROM python:${LATEST_PYTHON_TAG}/g" "$dockerfile"
        sed -i.tmp "s/FROM python:3.12-bookworm/FROM python:${LATEST_PYTHON_TAG}/g" "$dockerfile"

        # Ensure Debian packages are updated
        if ! grep -q "apt-get upgrade" "$dockerfile"; then
            # Add apt-get upgrade after FROM statements for runtime stages
            awk '/^FROM python.*AS runtime$|^FROM python.*slim.*$/ {
                print;
                getline;
                if ($0 !~ /^RUN apt-get update/) {
                    print "# Security updates";
                    print "RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*";
                }
                print;
                next
            } {print}' "${dockerfile}.tmp" > "${dockerfile}.new"

            if [ -f "${dockerfile}.new" ] && [ -s "${dockerfile}.new" ]; then
                mv "${dockerfile}.new" "$dockerfile"
            fi
        fi
    fi

    # Clean up temp files
    rm -f "${dockerfile}.tmp" "${dockerfile}.new"

    echo "Updated: $dockerfile"
done

# Special handling for CUDA-based images
echo "Updating CUDA-based Dockerfiles..."
CUDA_FILES=$(grep -l "nvidia/cuda" $DOCKERFILES || true)
for cudafile in $CUDA_FILES; do
    echo "Updating CUDA image in: $cudafile"
    # Update to latest CUDA base image
    sed -i.tmp "s/FROM nvidia\/cuda:12.[0-9].[0-9]-[^ ]*/FROM nvidia\/cuda:12.4.1-cudnn9-runtime-ubuntu22.04/g" "$cudafile"

    # Add security updates for Ubuntu-based CUDA images
    if ! grep -q "apt-get upgrade" "$cudafile"; then
        awk '/^FROM nvidia\/cuda/ {
            print;
            print "# Security updates";
            print "RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/*";
            next
        } {print}' "$cudafile" > "${cudafile}.new"

        if [ -f "${cudafile}.new" ] && [ -s "${cudafile}.new" ]; then
            mv "${cudafile}.new" "$cudafile"
        fi
    fi
    rm -f "${cudafile}.tmp"
done

echo "All Dockerfiles updated with security patches!"
echo ""
echo "Summary of changes:"
echo "- Updated Python base images to ${LATEST_PYTHON_TAG}"
echo "- Added OS package updates to all runtime images"
echo "- Updated CUDA images to latest versions"
echo ""
echo "Next steps:"
echo "1. Review the changes with: git diff neural-engine/docker/"
echo "2. Build and test the updated images"
echo "3. Run Trivy scan to verify vulnerabilities are fixed"
