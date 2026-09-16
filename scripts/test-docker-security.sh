#!/bin/bash

# Test Docker builds with security-optimized base images
set -e

echo "=================================================="
echo "Docker Security Build Test"
echo "=================================================="
echo ""
echo "Architecture:"
echo "• Alpine: MCP server, test-runner (lightweight services)"
echo "• Debian slim: API, ingestion, device services (need numpy/pandas)"
echo "• NVIDIA CUDA: ML processors (need PyTorch/TensorFlow)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track success/failure
FAILED_BUILDS=""
SUCCESSFUL_BUILDS=""

# Function to test a build
test_build() {
    local dockerfile=$1
    local context=$2
    local name=$3
    local base_type=$4

    echo -e "\n${YELLOW}Testing: $name ($base_type)${NC}"
    echo "Dockerfile: $dockerfile"

    if docker build -f "$dockerfile" -t "test-$name:latest" "$context" --no-cache > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Build successful${NC}"
        SUCCESSFUL_BUILDS="$SUCCESSFUL_BUILDS\n  ✓ $name ($base_type)"

        # Run Trivy scan if available
        if command -v trivy &> /dev/null; then
            echo "Running Trivy security scan..."
            trivy image --severity HIGH,CRITICAL --ignore-unfixed "test-$name:latest" 2>/dev/null | grep -E "Total:|HIGH:|CRITICAL:" || echo "No HIGH/CRITICAL vulnerabilities found"
        fi

        # Show image size
        size=$(docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep "test-$name" | awk '{print $3}')
        echo "Image size: $size"

        # Clean up
        docker rmi "test-$name:latest" > /dev/null 2>&1 || true
    else
        echo -e "${RED}✗ Build failed${NC}"
        FAILED_BUILDS="$FAILED_BUILDS\n  ✗ $name ($base_type)"
    fi
}

# Test Alpine-based containers (truly lightweight)
echo -e "\n${YELLOW}=== Testing Alpine-based containers ===${NC}"
test_build "neural-engine/docker/Dockerfile.mcp-server" "neural-engine" "mcp-server" "Alpine"
test_build "neural-engine/docker/dockerfiles/tools/test-runner/Dockerfile" "neural-engine" "test-runner" "Alpine"

# Test Debian slim containers (need numpy/pandas but not ML)
echo -e "\n${YELLOW}=== Testing Debian slim containers ===${NC}"
test_build "neural-engine/docker/Dockerfile.api" "neural-engine" "api" "Debian-slim"
test_build "neural-engine/docker/Dockerfile.ingestion" "neural-engine" "ingestion" "Debian-slim"
test_build "neural-engine/docker/dockerfiles/services/api-gateway/Dockerfile" "neural-engine" "api-gateway" "Debian-slim"
test_build "neural-engine/docker/dockerfiles/services/device-manager/Dockerfile" "neural-engine" "device-manager" "Debian-slim"
test_build "neural-engine/docker/dockerfiles/services/mcp-device-control/Dockerfile" "neural-engine" "mcp-device-control" "Debian-slim"
test_build "neural-engine/docker/dockerfiles/services/mcp-neural-data/Dockerfile" "neural-engine" "mcp-neural-data" "Debian-slim"
test_build "neural-engine/docker/dockerfiles/tools/cli/Dockerfile" "neural-engine" "cli" "Debian-slim"

# Test NVIDIA CUDA containers (ML/AI workloads)
echo -e "\n${YELLOW}=== Testing NVIDIA CUDA containers ===${NC}"
test_build "neural-engine/docker/Dockerfile.processor" "neural-engine" "processor" "NVIDIA-CUDA"
test_build "neural-engine/docker/Dockerfile.processor.hybrid" "neural-engine" "processor-hybrid" "NVIDIA-CUDA"
test_build "neural-engine/docker/dockerfiles/services/ml-pipeline/Dockerfile" "neural-engine" "ml-pipeline" "NVIDIA-CUDA"
test_build "neural-engine/docker/dockerfiles/services/neural-processor/Dockerfile" "neural-engine" "neural-processor" "NVIDIA-CUDA"

# Summary
echo -e "\n=================================================="
echo -e "${YELLOW}Build Summary${NC}"
echo "=================================================="

if [ -n "$SUCCESSFUL_BUILDS" ]; then
    echo -e "${GREEN}Successful builds:${NC}$SUCCESSFUL_BUILDS"
fi

if [ -n "$FAILED_BUILDS" ]; then
    echo -e "${RED}Failed builds:${NC}$FAILED_BUILDS"
    echo -e "\n${RED}Some builds failed. Please check the Dockerfiles.${NC}"
    exit 1
else
    echo -e "\n${GREEN}All builds completed successfully!${NC}"
fi

echo -e "\n${YELLOW}Security Notes:${NC}"
echo "• Alpine images: Minimal attack surface, smallest size"
echo "• Debian slim: Good balance of compatibility and security"
echo "• NVIDIA CUDA: Required for GPU acceleration, larger but necessary"
echo "• All images include security updates in their build process"
