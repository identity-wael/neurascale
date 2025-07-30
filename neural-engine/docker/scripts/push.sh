#!/bin/bash
# Push script for Neural Engine Docker images

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Default values
REGISTRY=""
TAG="latest"
DRY_RUN=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --registry)
            REGISTRY="$2"
            shift 2
            ;;
        --tag)
            TAG="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --registry REGISTRY  Docker registry URL (e.g., gcr.io/project-id)"
            echo "  --tag TAG           Image tag (default: latest)"
            echo "  --dry-run           Show what would be pushed without pushing"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Services to push
SERVICES=(
    "neural-processor"
    "device-manager"
    "api-gateway"
    "ml-pipeline"
)

# Base images
BASE_IMAGES=(
    "base:python"
    "base:golang"
    "base:node"
    "base:ml-base"
)

echo -e "${GREEN}Pushing Neural Engine Docker images...${NC}"
echo "Registry: ${REGISTRY:-Docker Hub}"
echo "Tag: $TAG"

# Function to push image
push_image() {
    local image=$1
    local source="neurascale/$image"
    local target="${REGISTRY:+$REGISTRY/}$source"

    echo -e "${YELLOW}Pushing $image...${NC}"

    if [ "$DRY_RUN" = true ]; then
        echo "Would push: $source -> $target"
    else
        # Tag image if registry specified
        if [ -n "$REGISTRY" ]; then
            docker tag "$source:$TAG" "$target:$TAG"
            docker tag "$source:$TAG" "$target:latest"
        fi

        # Push image
        docker push "${target}:$TAG"
        docker push "${target}:latest"

        # Push additional tags for production
        if [ "$TAG" != "latest" ] && [ "$TAG" != "dev" ]; then
            # Also push major.minor version tags
            MAJOR=$(echo "$TAG" | cut -d. -f1)
            MINOR=$(echo "$TAG" | cut -d. -f1,2)

            docker tag "$source:$TAG" "${target}:$MAJOR"
            docker tag "$source:$TAG" "${target}:$MINOR"

            docker push "${target}:$MAJOR"
            docker push "${target}:$MINOR"
        fi
    fi
}

# Check if logged in to registry
if [ -n "$REGISTRY" ]; then
    echo -e "${YELLOW}Checking registry authentication...${NC}"
    if ! docker pull "$REGISTRY/hello-world" &>/dev/null; then
        echo -e "${RED}Not authenticated to registry $REGISTRY${NC}"
        echo "Please run: docker login $REGISTRY"
        exit 1
    fi
fi

# Push service images
for SERVICE in "${SERVICES[@]}"; do
    if docker image inspect "neurascale/$SERVICE:$TAG" &>/dev/null; then
        push_image "$SERVICE"
    else
        echo -e "${YELLOW}Warning: Image not found: neurascale/$SERVICE:$TAG${NC}"
    fi
done

# Push base images
echo -e "${YELLOW}Pushing base images...${NC}"
for BASE in "${BASE_IMAGES[@]}"; do
    if docker image inspect "neurascale/$BASE" &>/dev/null; then
        push_image "$BASE"
    else
        echo -e "${YELLOW}Warning: Base image not found: neurascale/$BASE${NC}"
    fi
done

# Create and push manifest for multi-arch support (if needed)
if [ "$DRY_RUN" = false ] && command -v docker manifest &>/dev/null; then
    echo -e "${YELLOW}Creating multi-arch manifests...${NC}"
    for SERVICE in "${SERVICES[@]}"; do
        MANIFEST="${REGISTRY:+$REGISTRY/}neurascale/$SERVICE:$TAG"

        # Check if we have multiple architectures
        if docker image inspect "neurascale/$SERVICE:$TAG-arm64" &>/dev/null; then
            docker manifest create "$MANIFEST" \
                "$MANIFEST-amd64" \
                "$MANIFEST-arm64"

            docker manifest push "$MANIFEST"
        fi
    done
fi

echo -e "${GREEN}Push complete!${NC}"

# Show pushed images
echo -e "${YELLOW}Pushed images:${NC}"
for SERVICE in "${SERVICES[@]}"; do
    echo "  ${REGISTRY:+$REGISTRY/}neurascale/$SERVICE:$TAG"
done
