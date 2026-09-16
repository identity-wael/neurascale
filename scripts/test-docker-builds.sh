#!/bin/bash

# Test Docker builds for mixed Alpine and NVIDIA CUDA base images
set -e

echo "=================================================="
echo "Testing Docker Builds with Mixed Base Images"
echo "=================================================="

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

    echo -e "\n${YELLOW}Testing: $name${NC}"
    echo "Dockerfile: $dockerfile"
    echo "Context: $context"

    if docker build -f "$dockerfile" -t "test-$name:latest" "$context" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Build successful${NC}"
        SUCCESSFUL_BUILDS="$SUCCESSFUL_BUILDS\n  ✓ $name"

        # Run Trivy scan if available
        if command -v trivy &> /dev/null; then
            echo "Running Trivy security scan..."
            trivy image --severity HIGH,CRITICAL --ignore-unfixed "test-$name:latest" || true
        fi

        # Clean up
        docker rmi "test-$name:latest" > /dev/null 2>&1 || true
    else
        echo -e "${RED}✗ Build failed${NC}"
        FAILED_BUILDS="$FAILED_BUILDS\n  ✗ $name"
    fi
}

# Test Alpine-based containers (non-ML)
echo -e "\n${YELLOW}=== Testing Alpine-based containers ===${NC}"

test_build "neural-engine/docker/Dockerfile.api" "neural-engine" "api-alpine"
test_build "neural-engine/docker/Dockerfile.ingestion" "neural-engine" "ingestion-alpine"
test_build "neural-engine/docker/Dockerfile.mcp-server" "neural-engine" "mcp-server-alpine"
test_build "neural-engine/docker/dockerfiles/services/api-gateway/Dockerfile" "neural-engine" "api-gateway-alpine"
test_build "neural-engine/docker/dockerfiles/services/device-manager/Dockerfile" "neural-engine" "device-manager-alpine"

# Test NVIDIA CUDA-based containers (ML/AI)
echo -e "\n${YELLOW}=== Testing NVIDIA CUDA-based containers ===${NC}"

test_build "neural-engine/docker/Dockerfile.processor" "neural-engine" "processor-cuda"
test_build "neural-engine/docker/Dockerfile.processor.hybrid" "neural-engine" "processor-hybrid-cuda"
test_build "neural-engine/docker/dockerfiles/services/ml-pipeline/Dockerfile" "neural-engine" "ml-pipeline-cuda"
test_build "neural-engine/docker/dockerfiles/services/neural-processor/Dockerfile" "neural-engine" "neural-processor-cuda"

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

    # Show image sizes
    echo -e "\n${YELLOW}Image Size Comparison:${NC}"
    echo "Alpine-based images are typically 50-80% smaller than Ubuntu/Debian"
    echo "NVIDIA CUDA images are larger but necessary for GPU acceleration"
fi

echo -e "\n${YELLOW}Notes:${NC}"
echo "• Alpine images use musl libc (smaller, more secure)"
echo "• NVIDIA CUDA images use glibc (required for PyTorch/TensorFlow)"
echo "• Run 'trivy image <image-name>' for detailed security analysis"
