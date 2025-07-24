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
- **Languages**: Python 3.9+, Node.js 18+

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

## Documentation

- [instructions.md](./instructions.md) - Step-by-step implementation guide
- [Neural-Management-System.md](./Neural-Management-System.md) - Complete system design and architecture

## Implementation Status

### ✅ Completed

- Project structure created
- Core dependencies configured (Python 3.12)
- Basic tests implemented
- CI/CD pipeline setup (with self-hosted runner support)
- Docker configurations for processor and API
- Google Cloud deployment configurations
- GitHub issues created for all implementation phases (#121-#141)

### 🚧 Current Issues

- GitHub Actions workflow experiencing startup failures
- Need to configure GCP_SA_KEY secret after running setup script

### 📋 Next Steps

1. Run `gcloud auth login` and `./scripts/setup-gcp-auth.sh`
2. Add GCP_SA_KEY to GitHub secrets
3. Continue with Phase 1 implementation

Track progress in the [GitHub Project](https://github.com/identity-wael/neurascale/projects/1) or see issues #121-#141 for detailed implementation tasks.

## License

Part of the NeuraScale platform. See main repository for license details.
