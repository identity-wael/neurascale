# NeuraScale Neural Engine

The Neural Engine is the core processing system for NeuraScale, handling real-time brain signal processing, machine learning inference, and virtual avatar control.

## Overview

This engine processes petabytes of brain data from Brain-Computer Interfaces (BCIs), performs real-time signal processing, and enables control of virtual avatars through NVIDIA Omniverse integration.

## Architecture

```
neural-engine/
├── functions/         # Cloud functions for data ingestion
├── dataflow/          # Apache Beam pipelines for stream processing
├── models/            # Machine learning models for neural decoding
├── processing/        # Advanced signal processing algorithms
├── datasets/          # Dataset loaders and data management
├── devices/           # BCI device interfaces (OpenBCI, etc.)
├── omniverse/         # NVIDIA Omniverse integration
├── security/          # Encryption and access control
├── monitoring/        # Performance monitoring and metrics
├── api/               # REST API endpoints
├── mcp-server/        # Model Context Protocol server
└── tests/             # Comprehensive test suites
```

## Key Features

- **Real-time Processing**: Sub-50ms latency for neural signal processing
- **Multi-device Support**: Compatible with OpenBCI, Emotiv, NeuroSky, and more
- **Secure**: End-to-end encryption with Google Cloud KMS
- **Scalable**: Handles 1000+ concurrent users
- **ML-Powered**: Advanced neural decoders using TensorFlow and scikit-learn

## Technologies

- **Cloud Platform**: Google Cloud Platform (Montreal region)
- **Stream Processing**: Apache Beam/Dataflow
- **Machine Learning**: TensorFlow, scikit-learn
- **Device Integration**: Lab Streaming Layer (LSL), BrainFlow
- **3D Visualization**: NVIDIA Omniverse
- **Infrastructure**: Kubernetes, Terraform
- **Languages**: Python 3.12+, Node.js 18+

## Getting Started

### Prerequisites

- Python 3.12
- Google Cloud SDK (`gcloud`)
- Docker
- Access to `neurascale` GCP project

### Setup

1. **Clone and install dependencies:**

```bash
cd neural-engine
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Set up Google Cloud authentication:**

```bash
# First authenticate with your Google account
gcloud auth login

# Then run the setup script
./scripts/setup-gcp-auth.sh

# Follow the instructions to add the key to GitHub
```

3. **Run tests:**

```bash
pytest tests/
```

For detailed implementation instructions, see [instructions.md](./instructions.md).

## Multi-Environment Setup

The Neural Engine supports three environments:

- **Production** (`production-neurascale`): Main branch deployments
- **Staging** (`staging-neurascale`): Pull request deployments
- **Development** (`development-neurascale`): Development branch deployments

### Infrastructure Management

Infrastructure is managed through Terraform with state stored in Google Cloud Storage:

- **State Bucket**: `neurascale-terraform-state`
- **Production State**: `gs://neurascale-terraform-state/neural-engine/production/`
- **Staging State**: `gs://neurascale-terraform-state/neural-engine/staging/`
- **Development State**: `gs://neurascale-terraform-state/neural-engine/development/`

### Deployment Flow

1. **Pull Requests** → Deploy to staging environment
2. **Main Branch** → Deploy to production environment
3. **Development Branch** → Deploy to development environment

## Documentation

- [instructions.md](./instructions.md) - Step-by-step implementation guide
- [Neural-Management-System.md](./Neural-Management-System.md) - Complete system design and architecture

## Implementation Status

### ✅ Phase 2 Completed (January 2025)

**Core Neural Data Ingestion System**

- ✅ Complete data ingestion pipeline with validators and anonymizers
- ✅ Multi-device support (OpenBCI, BrainFlow, LSL, synthetic)
- ✅ Real-time signal processing pipeline (Apache Beam/Dataflow)
- ✅ Machine learning models (movement decoder, emotion classifier)
- ✅ Cloud Functions for all signal types (EEG, EMG, ECG, spikes, LFP, accelerometer)
- ✅ Comprehensive test suite with >80% coverage
- ✅ CI/CD pipeline consolidated and optimized
- ✅ Cost optimization with Bigtable autoscaling
- ✅ Monitoring and alerting infrastructure
- ✅ Security implementation with encryption and access controls

**Infrastructure Achievements**

- Multi-environment deployment (production, staging, development)
- Terraform state management with GCS backend
- GitHub Actions with Workload Identity Federation
- Docker builds with BuildKit caching
- Automated Cloud Functions deployment
- Complete API structure with health checks

### 🎯 Phase 3 Ready

With Phase 2 complete, the system is ready for:

- NVIDIA Omniverse integration
- Advanced signal processing algorithms
- Edge deployment capabilities
- Real-world BCI device testing
- Production workload scaling

### 📋 Next Steps

1. Begin Phase 3: Advanced Features and Integration
2. Deploy NVIDIA Omniverse connector
3. Implement real-time avatar control
4. Add multi-user collaboration features

Track progress in the [GitHub Project](https://github.com/identity-wael/neurascale/projects/1) or see issues #121-#141 for detailed implementation tasks.

## License

Part of the NeuraScale platform. See main repository for license details.

# Trigger workflow

# Trigger deployment

# Trigger deployment with fixed permissions
