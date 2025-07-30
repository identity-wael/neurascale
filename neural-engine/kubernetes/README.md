# Neural Engine Kubernetes Deployment

This directory contains Kubernetes deployment configurations for the NeuraScale Neural Engine, implementing Phase 15 of the project roadmap.

## Overview

The Kubernetes deployment provides:

- Container orchestration for neural processing services
- Auto-scaling for dynamic workloads
- Service mesh integration for advanced traffic management
- GitOps workflows for automated deployments
- Comprehensive monitoring and observability

## Directory Structure

```
kubernetes/
├── helm/                     # Helm charts
│   ├── neural-engine/       # Main application chart
│   ├── infrastructure/      # Platform services
│   └── dependencies/        # External charts
├── manifests/               # Raw Kubernetes manifests
│   ├── base/               # Kustomize base
│   ├── overlays/           # Environment overlays
│   └── components/         # Reusable components
├── operators/              # Custom operators
├── gitops/                 # GitOps configurations
├── scripts/                # Deployment scripts
└── docs/                   # Documentation
```

## Quick Start

### Prerequisites

1. Kubernetes cluster (GKE) provisioned via Phase 14 Terraform
2. kubectl configured with cluster access
3. Helm 3.x installed
4. Optional: ArgoCD or Flux for GitOps

### Basic Deployment

1. Install the Neural Engine Helm chart:

```bash
helm install neural-engine ./helm/neural-engine \
  --namespace neural-engine \
  --create-namespace \
  --values ./helm/neural-engine/values.yaml
```

2. Verify deployment:

```bash
kubectl get pods -n neural-engine
kubectl get services -n neural-engine
```

## Components

### Core Services

1. **Neural Processor**: Main processing engine for neural data
2. **Device Manager**: Handles BCI device connections
3. **API Gateway**: External API interface
4. **ML Pipeline**: Machine learning inference services

### Platform Services

1. **Monitoring**: Prometheus, Grafana, AlertManager
2. **Logging**: Loki, Promtail
3. **Service Mesh**: Istio (optional)
4. **Ingress**: NGINX Ingress Controller
5. **Certificate Management**: cert-manager

## Environment Configuration

- **Development**: Minimal resources, no HA
- **Staging**: Moderate resources, partial HA
- **Production**: Full resources, complete HA

## Security

- Network policies for pod-to-pod communication
- RBAC configurations
- Secret management via Sealed Secrets
- Pod security policies

## Monitoring

- Prometheus metrics collection
- Grafana dashboards
- Custom alerts for neural processing
- Distributed tracing with Jaeger

## Next Steps

1. Review the [deployment guide](./docs/deployment-guide.md)
2. Check environment-specific configurations
3. Set up GitOps workflows
4. Configure monitoring and alerts
