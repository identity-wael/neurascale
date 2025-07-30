# Docker-Kubernetes Integration Guide

This guide explains how the Docker images built in Phase 16 integrate with the Kubernetes deployments from Phase 15.

## Overview

The Neural Engine uses a microservices architecture with the following components:

1. **Neural Processor** - Core signal processing engine
2. **Device Manager** - Hardware device interface and management
3. **API Gateway** - External API interface with rate limiting
4. **ML Pipeline** - Machine learning model training and inference
5. **MCP Server** - Model Context Protocol server for AI agents

## Image Registry Structure

All images are stored in Google Container Registry:

```
gcr.io/development-neurascale/
├── neural-processor:latest
├── device-manager:latest
├── api-gateway:latest
├── ml-pipeline:latest
├── mcp-server:latest
└── neural-cli:latest
```

## Building Images

### Local Development Build

```bash
# Build all images
make -C neural-engine docker-build

# Build specific service
make -C neural-engine docker-build-neural-processor
```

### CI/CD Pipeline

Images are automatically built and pushed on:

- Push to `main` branch
- Push to `develop` branch
- Creation of version tags (`v*`)

## Deployment to Kubernetes

### 1. Ensure Images are Built

```bash
# Validate Docker-K8s alignment
./neural-engine/scripts/validate-k8s-docker.sh
```

### 2. Deploy with Helm

```bash
# Deploy to development
helm upgrade --install neural-engine \
  ./neural-engine/kubernetes/helm/neural-engine \
  -f ./neural-engine/kubernetes/helm/neural-engine/values-dev.yaml \
  --namespace neural-engine \
  --create-namespace

# Deploy to production
helm upgrade --install neural-engine \
  ./neural-engine/kubernetes/helm/neural-engine \
  -f ./neural-engine/kubernetes/helm/neural-engine/values-prod.yaml \
  --namespace neural-engine-prod
```

## Service Configuration

### Neural Processor

```yaml
processor:
  enabled: true
  image:
    repository: gcr.io/development-neurascale/neural-processor
    tag: latest
  resources:
    limits:
      cpu: 2000m
      memory: 4Gi
```

### Device Manager

```yaml
deviceManager:
  enabled: true
  image:
    repository: gcr.io/development-neurascale/device-manager
    tag: latest
  privileged: false # Set to true for USB access
  usbAccess: false # Mount /dev/bus/usb
```

### API Gateway

```yaml
apiGateway:
  enabled: true
  image:
    repository: gcr.io/development-neurascale/api-gateway
    tag: latest
  ingress:
    enabled: true
    hosts:
      - host: api.neurascale.dev
```

### ML Pipeline

```yaml
mlPipeline:
  enabled: true
  image:
    repository: gcr.io/development-neurascale/ml-pipeline
    tag: latest
  resources:
    limits:
      nvidia.com/gpu: 1 # When GPU enabled
```

### MCP Server

```yaml
mcpServer:
  enabled: true
  image:
    repository: gcr.io/development-neurascale/mcp-server
    tag: latest
  autoscaling:
    enabled: false
```

## Local Testing with Docker Compose

### Using K8s-Compatible Images

```bash
# Start services with K8s images
docker-compose -f neural-engine/docker/compose/docker-compose.yml \
               -f neural-engine/docker/compose/docker-compose.k8s.yml \
               up -d

# Test with CLI
docker-compose run --rm cli neural-cli list-devices
```

## Monitoring and Debugging

### Check Image Versions

```bash
# In Kubernetes
kubectl get pods -n neural-engine -o jsonpath="{.items[*].spec.containers[*].image}" | tr ' ' '\n' | sort -u

# Locally
docker images | grep neurascale
```

### View Logs

```bash
# Kubernetes logs
kubectl logs -n neural-engine -l component=neural-processor -f

# Docker Compose logs
docker-compose logs -f neural-processor
```

### Troubleshooting

1. **Image Pull Errors**

   ```bash
   # Check GCR authentication
   kubectl get secret -n neural-engine gcr-secret -o yaml
   ```

2. **Resource Issues**

   ```bash
   # Check resource usage
   kubectl top pods -n neural-engine
   ```

3. **Configuration Mismatches**
   ```bash
   # Compare configs
   helm get values neural-engine -n neural-engine
   ```

## Security Considerations

1. **Non-Root Containers**: All images run as non-root users
2. **Read-Only Root Filesystem**: Enabled by default
3. **Security Scanning**: Trivy scans in CI/CD pipeline
4. **Network Policies**: Restricted inter-service communication

## Best Practices

1. **Image Tagging**

   - Use semantic versioning for production
   - SHA-based tags for traceability
   - Environment-specific tags (dev, staging, prod)

2. **Resource Limits**

   - Always set CPU/memory limits
   - Use horizontal pod autoscaling
   - Monitor resource usage

3. **Health Checks**

   - Implement liveness probes
   - Configure readiness probes
   - Set appropriate timeouts

4. **Secrets Management**
   - Use Kubernetes secrets
   - Enable external secrets operator
   - Rotate credentials regularly

## Continuous Deployment

### GitOps Workflow

1. Code merged to main
2. CI builds and tags images
3. ArgoCD detects new images
4. Automatic deployment to staging
5. Manual promotion to production

### Manual Deployment

```bash
# Update image tag
helm upgrade neural-engine ./neural-engine/kubernetes/helm/neural-engine \
  --set image.tag=v1.2.3 \
  --reuse-values
```

## Related Documentation

- [Docker README](./README.md) - Docker architecture details
- [Kubernetes README](../kubernetes/README.md) - K8s deployment guide
- [CLI Usage](./CLI_USAGE.md) - Using the Neural CLI container
