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
- **Infrastructure**: Kubernetes, Terraform Cloud
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

Infrastructure is managed through Terraform Cloud with the following workspaces:

- `neural-engine-production`
- `neural-engine-staging`
- `neural-engine-development`

State is stored in Terraform Cloud with backup to GCS buckets in the orchestration project.

### Deployment Flow

1. **Pull Requests** → Deploy to staging environment
2. **Main Branch** → Deploy to production environment
3. **Development Branch** → Deploy to development environment

## Documentation

- [instructions.md](./instructions.md) - Step-by-step implementation guide
- [Neural-Management-System.md](./Neural-Management-System.md) - Complete system design and architecture

## Implementation Status

### ✅ Completed

- Project structure created
- Core dependencies configured (Python 3.12)
- Basic tests implemented
- CI/CD pipeline setup with multi-environment support
- Docker configurations for ingestion, processor, and API services
- Google Cloud deployment configurations
- GitHub issues created for all implementation phases (#121-#141)
- Data ingestion system with validators
- Multi-environment infrastructure (production, staging, development)
- Terraform Cloud integration for state management

### 🚧 Current Issues

- Need to configure GCP_SA_KEY secret after running setup script
- Terraform Cloud workspaces need Workload Identity Federation variables

### 📋 Next Steps

1. Run `gcloud auth login` and `./scripts/setup-gcp-auth.sh`
2. Add GCP_SA_KEY to GitHub secrets
3. Configure Terraform Cloud workspaces with WIF variables
4. Continue with neural processing implementation

Track progress in the [GitHub Project](https://github.com/identity-wael/neurascale/projects/1) or see issues #121-#141 for detailed implementation tasks.

## License

Part of the NeuraScale platform. See main repository for license details.
