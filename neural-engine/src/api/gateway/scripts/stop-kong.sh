#!/bin/bash

# Stop Kong API Gateway
# NeuraScale Neural Engine - Phase 12 API Implementation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GATEWAY_DIR="$(dirname "$SCRIPT_DIR")"

echo "🛑 Stopping NeuraScale Kong API Gateway..."

cd "$GATEWAY_DIR"

# Stop all Kong services
docker-compose -f docker-compose.kong.yml down

echo "✅ Kong Gateway stopped successfully!"

# Optionally remove volumes (uncomment to clean up completely)
# echo "🧹 Cleaning up volumes..."
# docker-compose -f docker-compose.kong.yml down -v
# docker volume prune -f

echo ""
echo "📊 Stopped services:"
echo "   - Kong Gateway"
echo "   - PostgreSQL Database"
echo "   - Redis Cache"
echo "   - Prometheus Monitoring"
echo "   - Grafana Dashboard"
echo ""
echo "🚀 To restart Kong: ./start-kong.sh"