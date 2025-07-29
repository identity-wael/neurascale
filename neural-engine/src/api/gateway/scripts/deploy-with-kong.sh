#!/bin/bash

# Deploy NeuraScale API with Kong Gateway
# NeuraScale Neural Engine - Phase 12 API Implementation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GATEWAY_DIR="$(dirname "$SCRIPT_DIR")"
API_DIR="$(dirname "$GATEWAY_DIR")"
NEURAL_ENGINE_DIR="$(dirname "$API_DIR")"

echo "🚀 Deploying NeuraScale API with Kong Gateway..."

# Check prerequisites
check_prerequisites() {
    echo "🔍 Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose is not installed"
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        echo "❌ Docker is not running"
        exit 1
    fi
    
    echo "✅ Prerequisites met"
}

# Set up environment
setup_environment() {
    echo "🌍 Setting up environment..."
    
    # Copy environment file if it doesn't exist
    if [ ! -f "$GATEWAY_DIR/.env" ]; then
        cp "$GATEWAY_DIR/.env.example" "$GATEWAY_DIR/.env"
        echo "📝 Created .env file from template"
        echo "⚠️  Please review and customize .env before production deployment"
    fi
    
    # Generate SSL certificates if needed
    if [ ! -f "$GATEWAY_DIR/kong/ssl/kong.crt" ]; then
        echo "🔒 Generating SSL certificates..."
        cd "$GATEWAY_DIR/kong/ssl"
        ./generate-certs.sh
        cd "$SCRIPT_DIR"
    fi
    
    # Create networks
    echo "🌐 Creating Docker networks..."
    docker network create neurascale-api-network 2>/dev/null || true
    docker network create neurascale-kong-network 2>/dev/null || true
}

# Build API Docker image
build_api() {
    echo "🔨 Building Neural Engine API..."
    
    cd "$NEURAL_ENGINE_DIR"
    
    # Build API image
    docker build -t neurascale/neural-engine-api:latest -f Dockerfile .
    
    echo "✅ API image built successfully"
}

# Start API services
start_api() {
    echo "🌟 Starting Neural Engine API services..."
    
    cd "$NEURAL_ENGINE_DIR"
    
    # Check if there's a docker-compose file for the API
    if [ -f "docker-compose.yml" ]; then
        docker-compose up -d
    else
        # Start API container directly
        docker run -d \
            --name neural-engine-api \
            --network neurascale-api-network \
            -p 8000:8000 \
            -e ENVIRONMENT=production \
            neurascale/neural-engine-api:latest
    fi
    
    echo "✅ API services started"
}

# Start Kong Gateway
start_kong() {
    echo "🐉 Starting Kong Gateway..."
    
    cd "$GATEWAY_DIR"
    
    # Source environment variables
    if [ -f ".env" ]; then
        set -a
        source .env
        set +a
    fi
    
    # Start Kong services
    docker-compose -f docker-compose.kong.yml up -d
    
    # Wait for Kong to be ready
    echo "⏳ Waiting for Kong Gateway to be ready..."
    timeout=120
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
}

# Verify deployment
verify_deployment() {
    echo "🧪 Verifying deployment..."
    
    # Test Kong status
    if ! curl -f http://localhost:8001/status >/dev/null 2>&1; then
        echo "❌ Kong Gateway is not responding"
        exit 1
    fi
    
    # Test API through Kong
    if ! curl -f http://localhost:8000/api/v2/health >/dev/null 2>&1; then
        echo "❌ API is not accessible through Kong"
        exit 1
    fi
    
    # Test GraphQL endpoint
    if ! curl -f http://localhost:8000/api/graphql -X POST -d '{"query":"query { __schema { types { name } } }"}' -H "Content-Type: application/json" >/dev/null 2>&1; then
        echo "❌ GraphQL endpoint is not accessible"
        exit 1
    fi
    
    echo "✅ All services are responding correctly"
}

# Display deployment info
show_deployment_info() {
    echo ""
    echo "🎉 NeuraScale API with Kong Gateway deployed successfully!"
    echo ""
    echo "📊 Service URLs:"
    echo "────────────────────────────────────────────────────────────────"
    echo "🌐 API Gateway (HTTP):    http://localhost:8000"
    echo "🔐 API Gateway (HTTPS):   https://localhost:8443"
    echo "⚙️  Kong Admin API:       http://localhost:8001"
    echo "🔒 Kong Admin (HTTPS):    https://localhost:8444"
    echo "📈 Prometheus:            http://localhost:9090"
    echo "📊 Grafana:               http://localhost:3000"
    echo "📉 Redis:                 localhost:6379"
    echo "────────────────────────────────────────────────────────────────"
    echo ""
    echo "🧪 Test Commands:"
    echo "────────────────────────────────────────────────────────────────"
    echo "# Test API health"
    echo "curl http://localhost:8000/api/v2/health"
    echo ""
    echo "# Test GraphQL"
    echo "curl -X POST http://localhost:8000/api/graphql \\"
    echo "  -H 'Content-Type: application/json' \\"
    echo "  -d '{\"query\":\"query { __schema { types { name } } }\"}'"
    echo ""
    echo "# Check Kong status"
    echo "./scripts/kong-status.sh"
    echo "────────────────────────────────────────────────────────────────"
    echo ""
    echo "📖 Documentation:"
    echo "   - Kong Gateway: $GATEWAY_DIR/README.md"
    echo "   - API Docs: http://localhost:8000/api/docs"
    echo "   - GraphQL Playground: http://localhost:8000/api/graphql"
    echo ""
    echo "🛑 To stop all services:"
    echo "   ./scripts/stop-kong.sh"
    echo "   docker-compose down  # (in neural-engine directory)"
}

# Main deployment flow
main() {
    echo "════════════════════════════════════════════════════════════════"
    echo "🧠 NeuraScale Neural Engine - Kong Gateway Deployment"
    echo "════════════════════════════════════════════════════════════════"
    
    check_prerequisites
    setup_environment
    build_api
    start_api
    start_kong
    verify_deployment
    show_deployment_info
    
    echo ""
    echo "✨ Deployment completed successfully!"
}

# Run main function
main "$@"