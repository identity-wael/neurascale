# Neural Engine Development Guide

## Quick Start

1. **Clone and setup**:

   ```bash
   cd neural-engine
   ./setup.sh
   source venv/bin/activate
   ```

2. **Configure Google Cloud**:

   ```bash
   # Update .env with your project ID
   # Copy your service account key to key.json
   ./configure-gcp.sh
   ```

3. **Run tests**:
   ```bash
   make test
   ```

## Project Structure

```
neural-engine/
├── functions/         # Cloud Functions (serverless)
├── dataflow/          # Apache Beam pipelines
├── models/            # ML model training and inference
├── processing/        # Signal processing algorithms
├── datasets/          # Data loaders and managers
├── devices/           # Hardware interfaces
├── omniverse/         # NVIDIA integration
├── security/          # Encryption and access control
├── monitoring/        # Metrics and logging
├── api/               # REST API
├── mcp-server/        # Model Context Protocol
└── tests/             # Test suites
```

## Development Workflow

### 1. Feature Development

```bash
# Create feature branch
git checkout -b feat/your-feature

# Make changes
# Run tests
make test

# Format code
make format

# Lint
make lint

# Commit
git add .
git commit -m "feat: your feature description"
```

### 2. Running Locally

**Start API server**:

```bash
make run-api
```

**Start emulators** (for local testing):

```bash
make run-emulators
```

**Run with Docker**:

```bash
make docker-build
make docker-run
```

### 3. Testing

**Unit tests**:

```bash
make test-unit
```

**Integration tests**:

```bash
make test-integration
```

**Coverage report**:

```bash
make test  # Generates htmlcov/index.html
```

## Google Cloud Development

### Local Emulators

For local development without GCP costs:

```bash
# Firestore
export FIRESTORE_EMULATOR_HOST=localhost:8081

# Pub/Sub
export PUBSUB_EMULATOR_HOST=localhost:8085

# Start emulators
make run-emulators
```

### Authentication

1. **Service Account** (recommended for development):

   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=./key.json
   ```

2. **User Account** (for testing):
   ```bash
   gcloud auth application-default login
   ```

## Common Tasks

### Adding a New Device Interface

1. Create file in `devices/`:

   ```python
   # devices/new_device.py
   from .base import BaseDevice

   class NewDevice(BaseDevice):
       def connect(self):
           # Implementation
           pass
   ```

2. Add tests in `tests/unit/test_devices.py`

3. Update `devices/__init__.py` to export

### Adding a New ML Model

1. Create model in `models/`:

   ```python
   # models/new_model.py
   import tensorflow as tf

   class NewModel:
       def __init__(self):
           self.model = self._build_model()

       def _build_model(self):
           # Model architecture
           pass
   ```

2. Add training script in `models/training/`

3. Add inference in `models/inference/`

### Deploying a Cloud Function

```bash
cd functions/your_function
gcloud functions deploy your-function \
  --runtime python39 \
  --trigger-http \
  --entry-point main \
  --region northamerica-northeast1
```

## Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Remote Debugging

For Cloud Functions:

```python
import pdb; pdb.set_trace()  # Use with caution in production
```

### Performance Profiling

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
# Your code here
profiler.disable()
stats = pstats.Stats(profiler).sort_stats('cumulative')
stats.print_stats()
```

## CI/CD

The GitHub Actions workflow (`../.github/workflows/neural-engine-ci.yml`) runs:

1. **On PR**: Linting, type checking, unit tests
2. **On merge to main**: Build Docker images, deploy to staging
3. **Manual approval**: Deploy to production

## Troubleshooting

### "Module not found" errors

```bash
# Ensure you're in virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Google Cloud authentication errors

```bash
# Check credentials
echo $GOOGLE_APPLICATION_CREDENTIALS

# Verify service account
gcloud auth list
```

### Docker build failures

```bash
# Clean Docker cache
docker system prune -a

# Rebuild without cache
docker build --no-cache -t image-name .
```

## Resources

- [Google Cloud Python Client Libraries](https://cloud.google.com/python/docs/reference)
- [Apache Beam Programming Guide](https://beam.apache.org/documentation/programming-guide/)
- [Lab Streaming Layer Docs](https://labstreaminglayer.readthedocs.io/)
- [BrainFlow Documentation](https://brainflow.readthedocs.io/)
