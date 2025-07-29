# Kong API Gateway for NeuraScale

[![Kong Version](https://img.shields.io/badge/Kong-3.4-blue.svg)](https://konghq.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](../../LICENSE)

## Overview

Kong API Gateway provides enterprise-grade API management for the NeuraScale Neural Engine. This implementation includes rate limiting, authentication, load balancing, circuit breaking, and comprehensive monitoring.

### Key Features

- **🚀 High Performance**: Sub-10ms overhead, 10,000+ req/sec throughput
- **🔒 Enterprise Security**: JWT authentication, rate limiting, CORS, IP restrictions
- **📊 Comprehensive Monitoring**: Prometheus metrics, Grafana dashboards
- **🔄 Load Balancing**: Round-robin with health checks and failover
- **⚡ Circuit Breaking**: Automatic fault tolerance and recovery
- **🌐 SSL/TLS**: Full SSL termination with custom certificates
- **📈 Auto-Scaling**: Horizontal scaling with service discovery

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Kong API Gateway                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   Proxy     │  │   Admin     │  │  Monitoring │            │
│  │   :8000     │  │   :8001     │  │   :9090     │            │
│  │   :8443     │  │   :8444     │  │   :3000     │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  Middleware Stack                       │   │
│  │  • Rate Limiting    • Circuit Breaker                  │   │
│  │  • Authentication   • CORS                             │   │
│  │  • Load Balancing   • SSL Termination                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │ PostgreSQL  │  │    Redis    │  │  Prometheus │            │
│  │ (Config)    │  │  (Cache)    │  │  (Metrics)  │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                Neural Engine API Cluster                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│  │   API-1     │  │   API-2     │  │   API-N     │            │
│  │   :8000     │  │   :8000     │  │   :8000     │            │
│  └─────────────┘  └─────────────┘  └─────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- curl and jq (for testing)
- OpenSSL (for SSL certificates)

### 1. Start Kong Gateway

```bash
# Navigate to gateway directory
cd neural-engine/src/api/gateway

# Start all services
./scripts/start-kong.sh
```

### 2. Verify Installation

```bash
# Check gateway status
./scripts/kong-status.sh

# Test API endpoints
curl http://localhost:8000/api/v2/health
curl http://localhost:8001/status
```

### 3. Access Monitoring

- **Kong Admin**: http://localhost:8001
- **Grafana**: http://localhost:3000 (admin/neurascale-grafana-2025)
- **Prometheus**: http://localhost:9090

## Configuration

### Environment Variables

Copy and customize the environment file:

```bash
cp .env.example .env
# Edit .env with your settings
```

Key configurations:

```bash
# Database
KONG_PG_PASSWORD=your-secure-password

# Rate Limiting
RATE_LIMIT_MINUTE=1000
RATE_LIMIT_HOUR=50000

# JWT Secrets (rotate in production)
PYTHON_SDK_SECRET=your-python-sdk-secret
JS_SDK_SECRET=your-js-sdk-secret
```

### SSL Certificates

Generate development certificates:

```bash
cd kong/ssl
./generate-certs.sh
```

For production, replace with CA-signed certificates:

```bash
# Replace these files:
kong/ssl/kong.crt      # Proxy SSL certificate
kong/ssl/kong.key      # Proxy SSL private key
kong/ssl/admin.crt     # Admin API SSL certificate
kong/ssl/admin.key     # Admin API SSL private key
```

### Kong Configuration

The main configuration is in `kong/kong.yml`. Key sections:

#### Services

```yaml
services:
  - name: neurascale-api-rest
    url: http://neural-engine-api:8000
    connect_timeout: 60000
    retries: 5
```

#### Routes

```yaml
routes:
  - name: api-v2-devices
    service: neurascale-api-rest
    paths: ["/api/v2/devices", "/api/v2/devices/.*"]
    methods: ["GET", "POST", "PATCH", "DELETE"]
```

#### Plugins

```yaml
plugins:
  - name: rate-limiting
    config:
      minute: 1000
      policy: redis
      redis_host: redis
```

## API Endpoints

### Core API Routes

All Neural Engine endpoints are proxied through Kong with added security and monitoring:

| Route Pattern           | Service   | Description         |
| ----------------------- | --------- | ------------------- |
| `/api/v2/devices/*`     | REST API  | Device management   |
| `/api/v2/sessions/*`    | REST API  | Session recording   |
| `/api/v2/neural-data/*` | REST API  | Neural data access  |
| `/api/v2/patients/*`    | REST API  | Patient management  |
| `/api/v2/analysis/*`    | REST API  | Analysis pipeline   |
| `/api/v2/ml-models/*`   | REST API  | ML model endpoints  |
| `/api/graphql`          | GraphQL   | GraphQL API         |
| `/ws/*`                 | WebSocket | Real-time streaming |

### Gateway Endpoints

| Endpoint  | Purpose       | Authentication |
| --------- | ------------- | -------------- |
| `:8000/*` | API Proxy     | JWT Required   |
| `:8001/*` | Admin API     | IP Restricted  |
| `:8443/*` | API Proxy SSL | JWT Required   |
| `:8444/*` | Admin API SSL | IP Restricted  |

## Authentication

Kong handles JWT authentication for all API endpoints:

### JWT Token Format

```json
{
  "iss": "python-sdk-issuer",
  "sub": "user-12345",
  "aud": "neurascale-api",
  "exp": 1642248600,
  "iat": 1642245000,
  "roles": ["researcher", "clinician"],
  "permissions": ["read:devices", "write:sessions"]
}
```

### Client Authentication

```bash
# Include JWT in Authorization header
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/v2/devices
```

### SDK Configuration

**Python SDK:**

```python
from neurascale import NeuraScaleClient

client = NeuraScaleClient(
    api_key="your-jwt-token",
    base_url="http://localhost:8000"  # Through Kong
)
```

**JavaScript SDK:**

```javascript
import { NeuraScaleClient } from "@neurascale/sdk";

const client = new NeuraScaleClient({
  apiKey: "your-jwt-token",
  baseUrl: "http://localhost:8000", // Through Kong
});
```

## Rate Limiting

Kong implements sliding window rate limiting with Redis backend:

### Default Limits

| Tier       | Per Minute | Per Hour  | Per Day   |
| ---------- | ---------- | --------- | --------- |
| Default    | 1000       | 50,000    | 1,000,000 |
| Premium    | 5000       | 200,000   | 5,000,000 |
| Enterprise | Unlimited  | Unlimited | Unlimited |

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642248660
```

### Custom Rate Limits

Configure per-consumer limits:

```bash
# Set custom rate limit for a consumer
curl -X POST http://localhost:8001/consumers/python-sdk/plugins \
  --data "name=rate-limiting" \
  --data "config.minute=2000" \
  --data "config.hour=100000"
```

## Load Balancing

Kong provides intelligent load balancing across multiple API instances:

### Health Checks

- **Active**: HTTP GET `/api/v2/health` every 5s
- **Passive**: Circuit breaker on 5xx responses
- **Failover**: Automatic unhealthy instance removal

### Upstream Configuration

```yaml
upstreams:
  - name: neural-engine-cluster
    algorithm: round-robin
    healthchecks:
      active:
        http_path: "/api/v2/health"
        interval: 5
```

### Adding Backend Instances

```bash
# Add new API server to load balancer
curl -X POST http://localhost:8001/upstreams/neural-engine-cluster/targets \
  --data "target=neural-engine-api-3:8000" \
  --data "weight=100"
```

## Circuit Breaking

Automatic fault tolerance with configurable thresholds:

### Configuration

```yaml
plugins:
  - name: circuit-breaker
    config:
      failure_threshold_percentage: 50
      minimum_request_threshold: 10
      window_size_in_seconds: 30
      recovery_window_size_in_seconds: 30
```

### Circuit States

- **CLOSED**: Normal operation, requests pass through
- **OPEN**: Failures exceed threshold, requests blocked
- **HALF_OPEN**: Testing recovery, limited requests allowed

## Monitoring & Observability

### Prometheus Metrics

Kong exposes detailed metrics at `/metrics`:

```bash
# View Kong metrics
curl http://localhost:8001/metrics
```

Key metrics:

- `kong_http_requests_total`
- `kong_latency_ms`
- `kong_upstream_health`
- `kong_rate_limit_exceeded_total`

### Grafana Dashboards

Pre-configured dashboards include:

1. **Kong Overview**: Request rate, latency, errors
2. **API Performance**: Endpoint-specific metrics
3. **Security**: Rate limiting, authentication failures
4. **Infrastructure**: Database, Redis, system health

### Log Aggregation

Kong logs are forwarded to a central collector:

```yaml
plugins:
  - name: http-log
    config:
      http_endpoint: http://log-collector:8080/kong-logs
```

### Alerting

Prometheus alerts for critical conditions:

- High error rate (>5%)
- High latency (>1000ms P95)
- Circuit breaker open
- Backend unhealthy

## Security

### SSL/TLS Configuration

Kong terminates SSL with strong security:

```yaml
# SSL configuration
KONG_SSL_PROTOCOLS: "TLSv1.2 TLSv1.3"
KONG_SSL_CIPHERS: "ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS"
KONG_SSL_PREFER_SERVER_CIPHERS: "on"
```

### CORS Policy

Configured for secure cross-origin requests:

```yaml
plugins:
  - name: cors
    config:
      origins: ["https://neurascale.com", "https://app.neurascale.com"]
      methods: ["GET", "POST", "PATCH", "DELETE", "OPTIONS"]
      credentials: true
```

### IP Restrictions

Admin API is restricted to internal networks:

```yaml
plugins:
  - name: ip-restriction
    route: api-docs
    config:
      allow: ["10.0.0.0/8", "192.168.0.0/16", "172.16.0.0/12"]
```

## Scaling & Performance

### Horizontal Scaling

Scale Kong gateway instances:

```bash
# Scale Kong gateway
docker-compose -f docker-compose.kong.yml up -d --scale kong-gateway=3
```

### Performance Tuning

Key configuration for high throughput:

```yaml
# Worker processes
KONG_WORKER_PROCESSES: "auto"
KONG_WORKER_CONNECTIONS: 4096

# Upstream connections
KONG_UPSTREAM_KEEPALIVE_POOL_SIZE: 60
KONG_UPSTREAM_KEEPALIVE_MAX_REQUESTS: 100
```

### Resource Requirements

| Component    | CPU       | Memory | Disk  |
| ------------ | --------- | ------ | ----- |
| Kong Gateway | 1 core    | 1GB    | 10GB  |
| PostgreSQL   | 0.5 core  | 512MB  | 50GB  |
| Redis        | 0.25 core | 256MB  | 1GB   |
| Prometheus   | 0.5 core  | 512MB  | 100GB |
| Grafana      | 0.25 core | 256MB  | 10GB  |

## Troubleshooting

### Common Issues

#### Kong Won't Start

```bash
# Check logs
docker-compose -f docker-compose.kong.yml logs kong-gateway

# Check database connection
docker-compose -f docker-compose.kong.yml exec kong-database psql -U kong -c "\l"
```

#### High Latency

```bash
# Check upstream health
curl http://localhost:8001/upstreams/neural-engine-cluster/health

# View performance metrics
curl http://localhost:8001/status
```

#### Rate Limiting Issues

```bash
# Check rate limit plugin status
curl http://localhost:8001/plugins | jq '.data[] | select(.name=="rate-limiting")'

# Check Redis connection
docker-compose -f docker-compose.kong.yml exec kong-redis redis-cli ping
```

### Debug Mode

Enable debug logging:

```bash
# Set debug level
docker-compose -f docker-compose.kong.yml exec kong-gateway \
  kong config set log_level debug
```

### Health Checks

```bash
# Gateway health
./scripts/kong-status.sh

# Detailed service status
curl http://localhost:8001/status | jq '.'

# Plugin status
curl http://localhost:8001/plugins | jq '.data[] | {name, enabled}'
```

## Maintenance

### Backup & Recovery

```bash
# Backup Kong configuration
kong config db_export kong-backup.yaml

# Restore configuration
kong config db_import kong-backup.yaml
```

### Updates

```bash
# Update Kong version
docker-compose -f docker-compose.kong.yml pull
docker-compose -f docker-compose.kong.yml up -d
```

### Log Rotation

Configure log rotation for production:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## Production Deployment

### Environment Preparation

1. **SSL Certificates**: Use CA-signed certificates
2. **Secrets Management**: Use encrypted secrets store
3. **Database**: Use managed PostgreSQL service
4. **Monitoring**: Configure external monitoring
5. **Backup**: Set up automated backups

### Kubernetes Deployment

For Kubernetes, use Kong Ingress Controller:

```bash
# Install Kong Ingress Controller
kubectl apply -f https://bit.ly/k4k8s
```

### AWS/Cloud Deployment

Use managed services:

- **Database**: AWS RDS PostgreSQL
- **Cache**: AWS ElastiCache Redis
- **Load Balancer**: AWS Application Load Balancer
- **Monitoring**: AWS CloudWatch + Prometheus

## Support

### Getting Help

- **Documentation**: [Kong Documentation](https://docs.konghq.com/)
- **Community**: [Kong Nation](https://discuss.konghq.com/)
- **GitHub Issues**: [NeuraScale Issues](https://github.com/identity-wael/neurascale/issues)

### Performance Tuning

For high-traffic environments, contact the NeuraScale team for custom tuning and enterprise support.

---

**Built with ❤️ and ⚡ by the NeuraScale Team**
