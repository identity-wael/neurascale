#!/bin/bash
# Build script for Neural Engine Docker images

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
BUILD_ENV="dev"
SCAN_IMAGES=false
PUSH_IMAGES=false
VERSION="latest"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --prod)
            BUILD_ENV="prod"
            shift
            ;;
        --dev)
            BUILD_ENV="dev"
            shift
            ;;
        --scan)
            SCAN_IMAGES=true
            shift
            ;;
        --push)
            PUSH_IMAGES=true
            shift
            ;;
        --version)
            VERSION="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${GREEN}Building Neural Engine Docker images...${NC}"
echo "Environment: $BUILD_ENV"
echo "Version: $VERSION"

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Change to project root
cd "$PROJECT_ROOT"

# Services to build
SERVICES=(
    "neural-processor"
    "device-manager"
    "api-gateway"
    "ml-pipeline"
    "mcp-server"
)

# Build each service
for SERVICE in "${SERVICES[@]}"; do
    echo -e "${YELLOW}Building $SERVICE...${NC}"

    DOCKERFILE="neural-engine/docker/dockerfiles/services/$SERVICE/Dockerfile"

    if [ ! -f "$DOCKERFILE" ]; then
        echo -e "${YELLOW}Warning: Dockerfile not found for $SERVICE, skipping...${NC}"
        continue
    fi

    # Build the image
    if [ "$BUILD_ENV" = "prod" ]; then
        docker build \
            -f "$DOCKERFILE" \
            -t "neurascale/$SERVICE:$VERSION" \
            -t "neurascale/$SERVICE:latest" \
            --target runtime \
            .
    else
        docker build \
            -f "$DOCKERFILE" \
            -t "neurascale/$SERVICE:dev" \
            --target builder \
            .
    fi

    # Scan if requested
    if [ "$SCAN_IMAGES" = true ]; then
        echo -e "${YELLOW}Scanning $SERVICE for vulnerabilities...${NC}"
        docker run --rm \
            -v /var/run/docker.sock:/var/run/docker.sock \
            aquasec/trivy image \
            --severity HIGH,CRITICAL \
            "neurascale/$SERVICE:$VERSION"
    fi
done

# Build base images
echo -e "${YELLOW}Building base images...${NC}"
BASE_IMAGES=(
    "python"
    "golang"
    "node"
    "ml-base"
)

for BASE in "${BASE_IMAGES[@]}"; do
    BASE_DOCKERFILE="neural-engine/docker/dockerfiles/base/$BASE.Dockerfile"

    if [ -f "$BASE_DOCKERFILE" ]; then
        echo -e "${YELLOW}Building base image: $BASE${NC}"
        docker build \
            -f "$BASE_DOCKERFILE" \
            -t "neurascale/base:$BASE" \
            .
    fi
done

# Push images if requested
if [ "$PUSH_IMAGES" = true ] && [ "$BUILD_ENV" = "prod" ]; then
    echo -e "${GREEN}Pushing images to registry...${NC}"
    for SERVICE in "${SERVICES[@]}"; do
        docker push "neurascale/$SERVICE:$VERSION"
        docker push "neurascale/$SERVICE:latest"
    done
fi

echo -e "${GREEN}Build complete!${NC}"

# Show image sizes
echo -e "${YELLOW}Image sizes:${NC}"
docker images neurascale/* --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}"
