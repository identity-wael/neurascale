#!/bin/bash
# Cleanup script for Neural Engine Docker resources

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Default values
CLEAN_IMAGES=false
CLEAN_VOLUMES=false
CLEAN_NETWORKS=false
CLEAN_ALL=false
PRUNE_SYSTEM=false
FORCE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --images)
            CLEAN_IMAGES=true
            shift
            ;;
        --volumes)
            CLEAN_VOLUMES=true
            shift
            ;;
        --networks)
            CLEAN_NETWORKS=true
            shift
            ;;
        --all)
            CLEAN_ALL=true
            shift
            ;;
        --prune)
            PRUNE_SYSTEM=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  --images     Remove Neural Engine Docker images"
            echo "  --volumes    Remove Neural Engine Docker volumes"
            echo "  --networks   Remove Neural Engine Docker networks"
            echo "  --all        Remove all Neural Engine Docker resources"
            echo "  --prune      Also run Docker system prune"
            echo "  --force      Don't prompt for confirmation"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# If --all is specified, enable all cleaning
if [ "$CLEAN_ALL" = true ]; then
    CLEAN_IMAGES=true
    CLEAN_VOLUMES=true
    CLEAN_NETWORKS=true
fi

# If no specific cleaning requested, show help
if [ "$CLEAN_IMAGES" = false ] && [ "$CLEAN_VOLUMES" = false ] && [ "$CLEAN_NETWORKS" = false ]; then
    echo "No cleaning options specified. Use --help for usage."
    exit 0
fi

# Confirmation prompt
if [ "$FORCE" = false ]; then
    echo -e "${YELLOW}This will remove the following Docker resources:${NC}"
    [ "$CLEAN_IMAGES" = true ] && echo "  - Neural Engine images"
    [ "$CLEAN_VOLUMES" = true ] && echo "  - Neural Engine volumes"
    [ "$CLEAN_NETWORKS" = true ] && echo "  - Neural Engine networks"
    [ "$PRUNE_SYSTEM" = true ] && echo "  - Unused Docker resources (system prune)"
    echo ""
    read -p "Are you sure you want to continue? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cleanup cancelled."
        exit 0
    fi
fi

echo -e "${GREEN}Starting Neural Engine Docker cleanup...${NC}"

# Stop running containers
echo -e "${YELLOW}Stopping Neural Engine containers...${NC}"
docker-compose -f docker/compose/docker-compose.yml down 2>/dev/null || true
docker ps -a --filter "name=neural-" --format "{{.ID}}" | xargs -r docker stop 2>/dev/null || true
docker ps -a --filter "name=neural-" --format "{{.ID}}" | xargs -r docker rm 2>/dev/null || true

# Clean images
if [ "$CLEAN_IMAGES" = true ]; then
    echo -e "${YELLOW}Removing Neural Engine images...${NC}"

    # Remove service images
    docker images "neurascale/*" --format "{{.Repository}}:{{.Tag}}" | while read -r image; do
        echo "  Removing $image"
        docker rmi "$image" 2>/dev/null || true
    done

    # Remove dangling images
    docker images -f "dangling=true" -q | xargs -r docker rmi 2>/dev/null || true
fi

# Clean volumes
if [ "$CLEAN_VOLUMES" = true ]; then
    echo -e "${YELLOW}Removing Neural Engine volumes...${NC}"

    # List and remove named volumes
    docker volume ls --filter "name=neural" --format "{{.Name}}" | while read -r volume; do
        echo "  Removing volume: $volume"
        docker volume rm "$volume" 2>/dev/null || true
    done

    # Remove compose project volumes
    docker volume ls --filter "label=com.docker.compose.project=neural-engine" --format "{{.Name}}" | while read -r volume; do
        echo "  Removing volume: $volume"
        docker volume rm "$volume" 2>/dev/null || true
    done
fi

# Clean networks
if [ "$CLEAN_NETWORKS" = true ]; then
    echo -e "${YELLOW}Removing Neural Engine networks...${NC}"

    # Remove custom networks
    docker network ls --filter "name=neural" --format "{{.Name}}" | grep -v "bridge\|host\|none" | while read -r network; do
        echo "  Removing network: $network"
        docker network rm "$network" 2>/dev/null || true
    done
fi

# System prune
if [ "$PRUNE_SYSTEM" = true ]; then
    echo -e "${YELLOW}Running Docker system prune...${NC}"

    if [ "$FORCE" = true ]; then
        docker system prune -af --volumes
    else
        docker system prune -a --volumes
    fi

    # Clean build cache
    echo -e "${YELLOW}Cleaning build cache...${NC}"
    docker builder prune -af
fi

# Show disk usage
echo -e "${GREEN}Cleanup complete!${NC}"
echo ""
echo -e "${YELLOW}Current Docker disk usage:${NC}"
docker system df

# Show remaining Neural Engine resources
echo ""
echo -e "${YELLOW}Remaining Neural Engine resources:${NC}"

# Check images
IMAGE_COUNT=$(docker images "neurascale/*" -q | wc -l)
if [ "$IMAGE_COUNT" -gt 0 ]; then
    echo -e "${BLUE}Images:${NC}"
    docker images "neurascale/*" --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}"
fi

# Check volumes
VOLUME_COUNT=$(docker volume ls --filter "name=neural" -q | wc -l)
if [ "$VOLUME_COUNT" -gt 0 ]; then
    echo -e "${BLUE}Volumes:${NC}"
    docker volume ls --filter "name=neural"
fi

# Check networks
NETWORK_COUNT=$(docker network ls --filter "name=neural" -q | wc -l)
if [ "$NETWORK_COUNT" -gt 0 ]; then
    echo -e "${BLUE}Networks:${NC}"
    docker network ls --filter "name=neural"
fi

echo ""
echo -e "${GREEN}Cleanup finished!${NC}"
