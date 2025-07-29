#!/bin/bash

# Start Kong API Gateway
# NeuraScale Neural Engine - Phase 12 API Implementation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GATEWAY_DIR="$(dirname "$SCRIPT_DIR")"
KONG_DIR="$GATEWAY_DIR/kong"

echo "🚀 Starting NeuraScale Kong API Gateway..."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Generate SSL certificates if they don't exist
if [ ! -f "$KONG_DIR/ssl/kong.crt" ]; then
    echo "🔒 Generating SSL certificates..."
    cd "$KONG_DIR/ssl"
    ./generate-certs.sh
    cd "$SCRIPT_DIR"
fi

# Create external network if it doesn't exist
echo "🌐 Setting up Docker networks..."
docker network create neurascale-api-network 2>/dev/null || true

# Set environment variables
export KONG_PG_PASSWORD="${KONG_PG_PASSWORD:-kong-neurascale-2025}"
export GRAFANA_PASSWORD="${GRAFANA_PASSWORD:-neurascale-grafana-2025}"

# Start Kong services
echo "🐳 Starting Kong containers..."
cd "$GATEWAY_DIR"
docker-compose -f docker-compose.kong.yml up -d

# Wait for Kong to be ready
echo "⏳ Waiting for Kong Gateway to be ready..."
timeout=60
counter=0

while ! curl -f http://localhost:8001/status >/dev/null 2>&1; do
    if [ $counter -eq $timeout ]; then
        echo "❌ Kong Gateway failed to start within $timeout seconds"
        docker-compose -f docker-compose.kong.yml logs kong-gateway
        exit 1
    fi
    echo -n "."
    sleep 2
    counter=$((counter + 1))
done

echo ""
echo "✅ Kong Gateway is ready!"

# Display status
echo ""
echo "📊 Kong Gateway Status:"
echo "────────────────────────────────────────────────────────────────"
echo "🌐 Proxy HTTP:       http://localhost:8000"
echo "🔐 Proxy HTTPS:      https://localhost:8443"
echo "⚙️  Admin API HTTP:   http://localhost:8001"
echo "🔒 Admin API HTTPS:  https://localhost:8444"
echo "📈 Prometheus:       http://localhost:9090"
echo "📊 Grafana:          http://localhost:3000 (admin/neurascale-grafana-2025)"
echo "📉 Redis:            localhost:6379"
echo "────────────────────────────────────────────────────────────────"

# Test Kong status
echo ""
echo "🧪 Testing Kong Gateway:"
echo "$(curl -s http://localhost:8001/status | jq -r '.message // "Kong is running"')"

# Show running containers
echo ""
echo "🐳 Running containers:"
docker-compose -f docker-compose.kong.yml ps

echo ""
echo "🎉 Kong Gateway started successfully!"
echo ""
echo "📖 Next steps:"
echo "   1. Test API endpoints: curl http://localhost:8000/api/v2/health"
echo "   2. View Kong Admin UI: http://localhost:8001"
echo "   3. Monitor with Grafana: http://localhost:3000"
echo "   4. Check Prometheus metrics: http://localhost:9090"
echo ""
echo "🛑 To stop Kong: ./stop-kong.sh"