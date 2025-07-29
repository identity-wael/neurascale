#!/bin/bash

# Check Kong Gateway Status
# NeuraScale Neural Engine - Phase 12 API Implementation

set -e

echo "🔍 NeuraScale Kong Gateway Status Check"
echo "════════════════════════════════════════════════════════════════"

# Check if Kong is running
if curl -f http://localhost:8001/status >/dev/null 2>&1; then
    echo "✅ Kong Gateway: RUNNING"
    
    # Get detailed status
    STATUS=$(curl -s http://localhost:8001/status)
    echo "📊 Gateway Status: $(echo "$STATUS" | jq -r '.message // "Healthy"')"
    
    # Check database connection
    DB_STATUS=$(echo "$STATUS" | jq -r '.database.reachable // "unknown"')
    echo "🗄️  Database: $DB_STATUS"
    
    # Get configuration hash
    CONFIG_HASH=$(curl -s http://localhost:8001 | jq -r '.configuration.database // "unknown"' | head -c 8)
    echo "⚙️  Config Hash: $CONFIG_HASH..."
    
else
    echo "❌ Kong Gateway: NOT RUNNING"
fi

echo ""
echo "🌐 Service Endpoints:"
echo "────────────────────────────────────────────────────────────────"

# Check proxy endpoint
if curl -f http://localhost:8000 >/dev/null 2>&1; then
    echo "✅ Proxy HTTP (8000): Available"
else
    echo "❌ Proxy HTTP (8000): Unavailable"
fi

# Check admin endpoint
if curl -f http://localhost:8001 >/dev/null 2>&1; then
    echo "✅ Admin API (8001): Available"
else
    echo "❌ Admin API (8001): Unavailable"
fi

# Check Redis
if redis-cli -h localhost -p 6379 ping >/dev/null 2>&1; then
    echo "✅ Redis Cache (6379): Available"
else
    echo "❌ Redis Cache (6379): Unavailable"
fi

# Check Prometheus
if curl -f http://localhost:9090/-/healthy >/dev/null 2>&1; then
    echo "✅ Prometheus (9090): Available"
else
    echo "❌ Prometheus (9090): Unavailable"
fi

# Check Grafana
if curl -f http://localhost:3000/api/health >/dev/null 2>&1; then
    echo "✅ Grafana (3000): Available"
else
    echo "❌ Grafana (3000): Unavailable"
fi

echo ""
echo "🐳 Container Status:"
echo "────────────────────────────────────────────────────────────────"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GATEWAY_DIR="$(dirname "$SCRIPT_DIR")"
cd "$GATEWAY_DIR"

if [ -f "docker-compose.kong.yml" ]; then
    docker-compose -f docker-compose.kong.yml ps
else
    echo "❌ docker-compose.kong.yml not found"
fi

echo ""
echo "📈 API Statistics (last 5 minutes):"
echo "────────────────────────────────────────────────────────────────"

if curl -f http://localhost:8001/status >/dev/null 2>&1; then
    # Get recent metrics
    CONNECTIONS=$(curl -s http://localhost:8001/status | jq -r '.server.connections_handled // 0')
    REQUESTS=$(curl -s http://localhost:8001/status | jq -r '.server.total_requests // 0')
    
    echo "🔗 Total Connections: $CONNECTIONS"
    echo "📊 Total Requests: $REQUESTS"
    
    # Get service status
    echo ""
    echo "🔧 Configured Services:"
    curl -s http://localhost:8001/services | jq -r '.data[] | "   \(.name): \(.host):\(.port)"' 2>/dev/null || echo "   Unable to fetch services"
    
    echo ""
    echo "🛣️  Active Routes:"
    curl -s http://localhost:8001/routes | jq -r '.data[] | "   \(.name): \(.methods // ["ANY"] | join(",")) \(.paths[0] // "/")"' 2>/dev/null || echo "   Unable to fetch routes"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"