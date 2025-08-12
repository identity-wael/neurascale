#!/bin/bash

# Script to test Docker images for security vulnerabilities
set -e

echo "Testing Docker images for security vulnerabilities..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if trivy is installed
if ! command -v trivy &> /dev/null; then
    echo -e "${YELLOW}Trivy not installed. Installing...${NC}"
    brew install aquasecurity/trivy/trivy || {
        echo -e "${RED}Failed to install Trivy. Please install manually.${NC}"
        exit 1
    }
fi

# List of Dockerfiles to test
DOCKERFILES=(
    "neural-engine/docker/Dockerfile.api"
    "neural-engine/docker/Dockerfile.processor"
    "neural-engine/docker/Dockerfile.ingestion"
    "neural-engine/docker/Dockerfile.mcp-server"
)

# Results array
declare -a RESULTS

echo "Building and scanning Docker images..."
echo "========================================="

for dockerfile in "${DOCKERFILES[@]}"; do
    if [ ! -f "$dockerfile" ]; then
        echo -e "${YELLOW}Skipping $dockerfile (not found)${NC}"
        continue
    fi

    IMAGE_NAME="neurascale-test:$(basename $dockerfile)"
    echo -e "\n${GREEN}Building $dockerfile...${NC}"

    # Build the image
    if docker build -f "$dockerfile" -t "$IMAGE_NAME" . 2>/dev/null; then
        echo -e "${GREEN}✓ Build successful${NC}"

        # Run Trivy scan
        echo "Running Trivy scan..."
        SCAN_OUTPUT=$(mktemp)

        if trivy image --severity HIGH,CRITICAL --ignore-unfixed \
            --ignorefile .trivyignore "$IMAGE_NAME" > "$SCAN_OUTPUT" 2>&1; then
            echo -e "${GREEN}✓ No critical vulnerabilities found${NC}"
            RESULTS+=("$dockerfile: PASSED")
        else
            echo -e "${RED}✗ Vulnerabilities found:${NC}"
            cat "$SCAN_OUTPUT" | grep -E "Total:|HIGH:|CRITICAL:" || true
            RESULTS+=("$dockerfile: FAILED")
        fi

        rm -f "$SCAN_OUTPUT"

        # Clean up image
        docker rmi "$IMAGE_NAME" > /dev/null 2>&1
    else
        echo -e "${RED}✗ Build failed${NC}"
        RESULTS+=("$dockerfile: BUILD FAILED")
    fi
done

echo -e "\n========================================="
echo "Summary:"
echo "========================================="

FAILED=0
for result in "${RESULTS[@]}"; do
    if [[ $result == *"PASSED"* ]]; then
        echo -e "${GREEN}$result${NC}"
    else
        echo -e "${RED}$result${NC}"
        FAILED=$((FAILED + 1))
    fi
done

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}All images passed security scanning!${NC}"
    exit 0
else
    echo -e "\n${RED}$FAILED images have security issues.${NC}"
    echo "Please review and fix the vulnerabilities."
    exit 1
fi
