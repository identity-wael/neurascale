# Neural Engine Docker Configuration

This directory contains Docker configurations for containerizing the NeuraScale Neural Engine, implementing Phase 16 of the project roadmap.

## Overview

The Docker setup provides:

- Multi-stage builds for optimized images
- Security-hardened containers
- Development and production configurations
- Automated build and deployment scripts
- Container orchestration with Docker Compose

## Directory Structure

```
docker/
├── dockerfiles/              # Dockerfile definitions
│   ├── base/                # Base images for different stacks
│   ├── services/            # Service-specific Dockerfiles
│   └── tools/               # Development tool containers
├── compose/                 # Docker Compose configurations
│   ├── docker-compose.yml   # Base configuration
│   ├── docker-compose.dev.yml
│   └── docker-compose.prod.yml
├── scripts/                 # Build and deployment scripts
└── registry/                # Container registry configs
```

## Quick Start

### Development Environment

1. Copy environment template:

```bash
cp compose/.env.example compose/.env
```

2. Build all services:

```bash
./scripts/build.sh --dev
```

3. Start development environment:

```bash
docker-compose -f compose/docker-compose.yml \
               -f compose/docker-compose.dev.yml up
```

### Production Build

1. Build optimized images:

```bash
./scripts/build.sh --prod --scan
```

2. Push to registry:

```bash
./scripts/push.sh --tag v1.0.0
```

## Services

### Core Services

1. **neural-processor**: Main neural data processing engine

   - Python 3.12 base
   - Scientific computing libraries
   - GPU support (optional)

2. **device-manager**: BCI device connection manager

   - Go 1.21 base
   - USB/Bluetooth libraries
   - Real-time capabilities

3. **api-gateway**: External API interface

   - Node.js base
   - GraphQL/REST endpoints
   - Authentication middleware

4. **ml-pipeline**: Machine learning inference service
   - Python 3.12 with ML libraries
   - Model serving
   - GPU acceleration

### Supporting Services

- PostgreSQL database
- Redis cache
- Kafka message broker
- Prometheus monitoring
- Grafana dashboards

## Build Process

### Multi-stage Builds

Each service uses multi-stage builds:

1. **dependencies**: Install build dependencies
2. **builder**: Compile/build application
3. **runtime**: Minimal runtime image

### Security Features

- Non-root user execution
- Minimal base images (distroless where possible)
- No shell in production images
- Read-only root filesystem
- Security scanning with Trivy

### Optimization

- Layer caching strategies
- Minimal final image sizes
- Shared base layers
- Build-time argument injection

## Development

### Hot Reloading

Development containers support hot reloading:

- Python: watchdog + reload
- Go: air
- Node.js: nodemon

### Debugging

Debug configurations available:

- Remote Python debugging (debugpy)
- Go Delve debugger
- Node.js inspector

### Volumes

Development volumes for code synchronization:

```yaml
volumes:
  - ./src:/app/src
  - ./tests:/app/tests
```

## Production

### Health Checks

All services include health checks:

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8080/health || exit 1
```

### Resource Limits

Production resource constraints:

```yaml
deploy:
  resources:
    limits:
      cpus: "2.0"
      memory: 4G
    reservations:
      cpus: "1.0"
      memory: 2G
```

## CI/CD Integration

### GitHub Actions

Automated builds on:

- Pull requests (build & scan)
- Main branch (build, scan, push)
- Tags (production release)

### Image Tagging

- `latest`: Latest main branch build
- `dev`: Latest development build
- `v1.0.0`: Semantic version tags
- `sha-abc123`: Git commit SHA

## Monitoring

### Metrics

Prometheus metrics exposed:

- Container resource usage
- Application metrics
- Custom business metrics

### Logging

Structured JSON logging:

- Centralized log aggregation
- Log levels: DEBUG, INFO, WARN, ERROR
- Correlation IDs for tracing

## Security

### Scanning

Automated vulnerability scanning:

- Build-time: Trivy scan
- Runtime: Falco monitoring
- Dependencies: Snyk integration

### Best Practices

- Principle of least privilege
- Immutable infrastructure
- Secret management via environment
- Network segmentation

## Troubleshooting

### Common Issues

1. **Build failures**: Check build cache
2. **Permission errors**: Verify user IDs
3. **Network issues**: Check Docker networks
4. **Resource limits**: Monitor container stats

### Debug Commands

```bash
# View logs
docker-compose logs -f neural-processor

# Execute shell in container
docker exec -it neural-processor sh

# Inspect container
docker inspect neural-processor

# Clean build cache
docker builder prune -a
```
