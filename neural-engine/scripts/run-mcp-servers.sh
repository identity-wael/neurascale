#!/bin/bash
# Script to run MCP servers in Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
COMPOSE_FILE="docker/compose/docker-compose.mcp.yml"
ACTION="up"
SERVICES=""

# Help function
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -a, --action ACTION     Action to perform (up, down, restart, logs) [default: up]"
    echo "  -s, --services SERVICES Specific services to run (neural-data, device-control, all) [default: all]"
    echo "  -d, --detach           Run in detached mode"
    echo "  -b, --build            Build images before starting"
    echo "  -h, --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                     # Start all MCP servers"
    echo "  $0 -s neural-data      # Start only neural data server"
    echo "  $0 -a logs -s device   # Show logs for device control server"
    echo "  $0 -a down             # Stop all MCP servers"
}

# Parse arguments
DETACH=""
BUILD=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -a|--action)
            ACTION="$2"
            shift 2
            ;;
        -s|--services)
            SERVICES="$2"
            shift 2
            ;;
        -d|--detach)
            DETACH="-d"
            shift
            ;;
        -b|--build)
            BUILD="--build"
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Navigate to neural-engine directory
cd "$(dirname "$0")/.."

# Check if docker-compose file exists
if [ ! -f "$COMPOSE_FILE" ]; then
    echo -e "${RED}Docker compose file not found: $COMPOSE_FILE${NC}"
    exit 1
fi

# Set environment variables
export REGISTRY="${REGISTRY:-neurascale}"
export TAG="${TAG:-latest}"
export DB_PASSWORD="${DB_PASSWORD:-neurascale-db-2024}"
export REDIS_PASSWORD="${REDIS_PASSWORD:-neurascale-redis-2024}"
export LOG_LEVEL="${LOG_LEVEL:-INFO}"

# Ensure the neural-net network exists
echo -e "${YELLOW}Ensuring Docker network exists...${NC}"
docker network create neural-net 2>/dev/null || true

# Determine which services to run
case "$SERVICES" in
    neural-data)
        SERVICE_NAMES="mcp-neural-data"
        ;;
    device-control|device)
        SERVICE_NAMES="mcp-device-control"
        ;;
    all|"")
        SERVICE_NAMES="mcp-server"  # Use combined server by default
        ;;
    *)
        echo -e "${RED}Unknown service: $SERVICES${NC}"
        echo "Valid services: neural-data, device-control, all"
        exit 1
        ;;
esac

# Execute action
case "$ACTION" in
    up)
        echo -e "${GREEN}Starting MCP servers: $SERVICE_NAMES${NC}"
        docker-compose -f "$COMPOSE_FILE" up $DETACH $BUILD $SERVICE_NAMES
        ;;
    down)
        echo -e "${YELLOW}Stopping MCP servers${NC}"
        docker-compose -f "$COMPOSE_FILE" down
        ;;
    restart)
        echo -e "${YELLOW}Restarting MCP servers: $SERVICE_NAMES${NC}"
        docker-compose -f "$COMPOSE_FILE" restart $SERVICE_NAMES
        ;;
    logs)
        echo -e "${GREEN}Showing logs for: $SERVICE_NAMES${NC}"
        docker-compose -f "$COMPOSE_FILE" logs -f $SERVICE_NAMES
        ;;
    ps)
        echo -e "${GREEN}MCP server status:${NC}"
        docker-compose -f "$COMPOSE_FILE" ps
        ;;
    *)
        echo -e "${RED}Unknown action: $ACTION${NC}"
        echo "Valid actions: up, down, restart, logs, ps"
        exit 1
        ;;
esac

# Show status after up/restart
if [ "$ACTION" = "up" ] || [ "$ACTION" = "restart" ]; then
    sleep 2
    echo -e "\n${GREEN}MCP Server Status:${NC}"
    docker-compose -f "$COMPOSE_FILE" ps

    echo -e "\n${GREEN}Health Check URLs:${NC}"
    echo "  Neural Data Server: http://localhost:8081/health"
    echo "  Device Control Server: http://localhost:8082/health"
    echo "  Combined Server: http://localhost:8080/health"

    echo -e "\n${GREEN}MCP Server Ports:${NC}"
    echo "  Neural Data: localhost:9001"
    echo "  Device Control: localhost:9002"
fi
