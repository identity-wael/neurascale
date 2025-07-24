NeuraScale Neural Engine - Implementation Instructions for Claude Dev
Overview
You will implement a complete neural data management system that processes brain signals from BCIs, performs real-time signal processing, and enables control of virtual avatars in NVIDIA Omniverse. The system will be deployed on Google Cloud Platform in Montreal region.
Prerequisites Check
Before starting, ensure you have:

Google Cloud SDK installed and authenticated
Python 3.9+ with pip
Docker Desktop running
Node.js 18+ (for MCP server)
Git initialized in project directory
A Google Cloud project created with billing enabled

Phase 1: Project Setup and Structure (Tasks 1-3)
Task 1: Create Project Structure
Create the following directory structure:
neurascale-neural-engine/
├── neural-engine/
│ ├── functions/
│ │ └── neural_ingestion/
│ ├── dataflow/
│ ├── models/
│ ├── processing/
│ ├── datasets/
│ ├── devices/
│ ├── omniverse/
│ │ └── deployment/
│ ├── security/
│ ├── monitoring/
│ ├── api/
│ └── mcp-server/
│ └── src/
├── tests/
│ ├── unit/
│ ├── integration/
│ └── performance/
├── k8s/
│ ├── deployments/
│ ├── services/
│ ├── configmaps/
│ └── monitoring/
├── terraform/
│ ├── schemas/
│ └── dashboards/
├── docker/
├── deploy/
├── docs/
└── .github/
└── workflows/
Task 2: Initialize Python Environment

Create virtual environment: python -m venv venv
Activate it: source venv/bin/activate (Linux/Mac) or venv\Scripts\activate (Windows)
Create requirements.txt with the following content:

pylsl==1.16.0
brainflow==5.10.0
numpy==1.24.3
scipy==1.10.1
scikit-learn==1.3.0
tensorflow==2.13.0
google-cloud-pubsub==2.18.1
google-cloud-firestore==2.11.1
google-cloud-bigquery==3.11.4
google-cloud-bigtable==2.19.0
google-cloud-storage==2.10.0
google-cloud-dataflow==2.5.0
apache-beam[gcp]==2.49.0
cryptography==41.0.3
flask==2.3.3
gunicorn==21.2.0
pytest==7.4.0
pytest-asyncio==0.21.1
h5py==3.9.0
matplotlib==3.7.2
joblib==1.3.1
wandb==0.15.8
pywavelets==1.4.1

Install dependencies: pip install -r requirements.txt

Task 3: Configure Google Cloud

Set your project ID:

bashexport PROJECT_ID="your-project-id"
gcloud config set project $PROJECT_ID

Enable required APIs by running:

bashgcloud services enable compute.googleapis.com
gcloud services enable container.googleapis.com
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable pubsub.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable bigtable.googleapis.com
gcloud services enable dataflow.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable cloudiot.googleapis.com
gcloud services enable storage.googleapis.com

Create service account and download key:

bashgcloud iam service-accounts create neurascale-dev --display-name="NeuraScale Development"
gcloud iam service-accounts keys create key.json --iam-account=neurascale-dev@${PROJECT_ID}.iam.gserviceaccount.com
export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/key.json
Phase 2: Core Neural Engine Implementation (Tasks 4-8)
Task 4: Implement Neural Data Ingestion

Create neural-engine/functions/neural_ingestion/**init**.py (empty file)
Create neural-engine/functions/neural_ingestion/main.py and implement the complete NeuralDataIngestion class from the provided code
Create neural-engine/functions/neural_ingestion/requirements.txt with function-specific dependencies
Test locally by creating test_ingestion.py:

pythonfrom neural_engine.functions.neural_ingestion.main import NeuralDataIngestion
import numpy as np

# Test with synthetic data

ingestion = NeuralDataIngestion()
test_data = {
'device_id': 'test_device',
'user_id': 'test_user',
'data_type': 'eeg',
'sampling_rate': 250,
'channels': [{'id': i, 'label': f'CH{i}'} for i in range(8)],
'neural_signals': np.random.randn(8, 1000).tolist()
}

# Mock request object

class MockRequest:
def get_json(self):
return test_data

result, status = ingestion.ingest_neural_data(MockRequest())
print(f"Result: {result}, Status: {status}")
Task 5: Implement Signal Processing Pipeline

Create neural-engine/dataflow/**init**.py
Create neural-engine/dataflow/neural_processing_pipeline.py with the complete pipeline code
Create the BigQuery schemas:

Create terraform/schemas/realtime_features.json:

json[
{"name": "session_id", "type": "STRING", "mode": "REQUIRED"},
{"name": "timestamp", "type": "TIMESTAMP", "mode": "REQUIRED"},
{"name": "data_type", "type": "STRING", "mode": "REQUIRED"},
{"name": "processing_time", "type": "TIMESTAMP", "mode": "REQUIRED"},
{"name": "features", "type": "JSON", "mode": "NULLABLE"}
]

Create similar schema files for decoded_movements.json

Test the pipeline locally:

bashpython -m neural_engine.dataflow.neural_processing_pipeline \
 --runner=DirectRunner \
 --project=$PROJECT_ID \
  --temp_location=gs://${PROJECT_ID}-temp/temp
Task 6: Implement ML Models

Create neural-engine/models/**init**.py
Create neural-engine/models/movement_decoder_training.py with the complete model implementations
Create a test script to verify model creation:

pythonfrom neural_engine.models.movement_decoder_training import MovementDecoderTrainer

trainer = MovementDecoderTrainer()

# Test model building

model = trainer.build_model(input_shape=80) # 16 channels \* 5 features
model.summary()
Task 7: Implement Device Interfaces

Create neural-engine/devices/**init**.py
Create neural-engine/devices/device_interfaces.py with all device classes
Test OpenBCI interface with synthetic board:

pythonfrom neural_engine.devices.device_interfaces import OpenBCIDevice

device = OpenBCIDevice(board_type='synthetic')
if device.connect():
print("Connected to synthetic board")
device.start_streaming() # Let it stream for 5 seconds
import time
time.sleep(5)
device.stop_streaming()
Task 8: Implement Dataset Loaders

Create neural-engine/datasets/**init**.py
Create neural-engine/datasets/dataset_manager.py with all dataset loader classes
Create neural-engine/datasets/bci_competition_loader.py for LSL streaming:

pythonfrom pylsl import StreamInfo, StreamOutlet
import numpy as np
import time
from neural_engine.datasets.dataset_manager import BCICompetitionIVLoader

class BCICompetitionDataStreamer:
def **init**(self, data_path: str):
self.loader = BCICompetitionIVLoader(data_path)
self.outlet = None

    def start_streaming(self, subject_id: str = 'A01'):
        # Load data
        trials, labels = self.loader.load_data(subject_id)

        # Create LSL stream
        info = StreamInfo('BCICompetition', 'EEG',
                         self.loader.info.n_channels,
                         self.loader.info.sampling_rate,
                         'float32', subject_id)
        self.outlet = StreamOutlet(info)

        # Stream trials
        for trial in trials:
            for sample in trial.T:  # Transpose to get samples
                self.outlet.push_sample(sample.tolist())
                time.sleep(1.0 / self.loader.info.sampling_rate)

Phase 3: Advanced Processing Implementation (Tasks 9-11)
Task 9: Implement Advanced Signal Processing

Create neural-engine/processing/**init**.py
Create neural-engine/processing/advanced_signal_processing.py with the complete AdvancedSignalProcessor class
Create neural-engine/processing/movement_decoder.py:

pythonfrom pylsl import StreamInlet, resolve_stream, StreamInfo, StreamOutlet
import numpy as np
import threading
import queue
import time

class RealtimeMovementDecoder:
def **init**(self, model_path: str = None):
self.model_path = model_path
self.model = None
self.inlet = None
self.outlet = None
self.processing_queue = queue.Queue(maxsize=1000)
self.running = False

    def connect_to_stream(self, stream_name: str = 'OpenBCI_Stream'):
        print(f"Looking for {stream_name}...")
        streams = resolve_stream('name', stream_name)
        if streams:
            self.inlet = StreamInlet(streams[0])
            print("Connected to neural stream")

            # Create output stream for movements
            info = StreamInfo('DecodedMovements', 'Movements', 5, 10, 'float32', 'movements')
            self.outlet = StreamOutlet(info)
            return True
        return False

    def start_decoding(self):
        self.running = True

        # Start processing thread
        process_thread = threading.Thread(target=self._process_loop)
        process_thread.daemon = True
        process_thread.start()

        # Start receiving thread
        receive_thread = threading.Thread(target=self._receive_loop)
        receive_thread.daemon = True
        receive_thread.start()

    def _receive_loop(self):
        buffer = []
        while self.running:
            sample, timestamp = self.inlet.pull_sample(timeout=0.1)
            if sample:
                buffer.append(sample)

                # Process in windows of 250 samples (1 second at 250Hz)
                if len(buffer) >= 250:
                    window = np.array(buffer[-250:])
                    self.processing_queue.put((window, timestamp))

    def _process_loop(self):
        while self.running:
            try:
                window, timestamp = self.processing_queue.get(timeout=0.1)

                # Extract features (simplified)
                features = self._extract_features(window)

                # Decode movement (mock for now)
                movement = self._decode_movement(features)

                # Send via LSL
                output = [movement['x'], movement['y'], movement['z'],
                         float(movement['gripper']), movement['confidence']]
                self.outlet.push_sample(output)

            except queue.Empty:
                continue

    def _extract_features(self, window):
        # Simplified feature extraction
        return {
            'mean': np.mean(window, axis=0),
            'std': np.std(window, axis=0),
            'beta_power': np.mean(np.abs(window), axis=0)
        }

    def _decode_movement(self, features):
        # Mock decoding - replace with actual model
        return {
            'x': np.random.randn() * 0.1,
            'y': np.random.randn() * 0.1,
            'z': 0.0,
            'gripper': np.random.random() > 0.5,
            'confidence': 0.8 + np.random.random() * 0.2
        }

Task 10: Implement Security Layer

Create neural-engine/security/**init**.py
Create neural-engine/security/encryption.py with the complete encryption classes
Create neural-engine/security/access_control.py with RBAC implementation
Test encryption:

pythonfrom neural_engine.security.encryption import NeuralDataEncryption

# Note: This will fail without proper GCP setup, so mock for testing

encryptor = NeuralDataEncryption()
test_data = b"neural signal data"
encrypted = encryptor.encrypt_neural_data(test_data, "session_123")
print(f"Encrypted: {encrypted}")
Task 11: Implement Performance Monitoring

Create neural-engine/monitoring/**init**.py
Create neural-engine/monitoring/performance_metrics.py with monitoring classes
Create a test monitoring script:

pythonfrom neural_engine.monitoring.performance_metrics import PerformanceMonitor

monitor = PerformanceMonitor()

# Record test metrics

monitor.record_metric('neural_processing_latency', 45.2, {'device': 'openbci'})
monitor.record_metric('movement_decode_accuracy', 0.94, {'model': 'v1'})
Phase 4: NVIDIA Omniverse Integration (Tasks 12-14)
Task 12: Implement Omniverse Controller
Note: Full Omniverse requires special setup. Create a simplified version first.

Create neural-engine/omniverse/**init**.py
Create neural-engine/omniverse/simple_avatar_controller.py:

pythonimport pygame
import numpy as np
from pylsl import StreamInlet, resolve_stream
import threading
import queue

class SimpleAvatarController:
def **init**(self, width=800, height=600):
pygame.init()
self.screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Neural Avatar Control")
self.clock = pygame.time.Clock()

        self.avatar_pos = [width // 2, height // 2]
        self.avatar_radius = 20
        self.gripper_open = True

        self.movement_queue = queue.Queue()
        self.running = True

    def connect_neural_stream(self):
        print("Connecting to movement decoder...")
        streams = resolve_stream('name', 'DecodedMovements')

        if streams:
            self.inlet = StreamInlet(streams[0])
            print("Connected to movement stream")

            # Start receiving thread
            thread = threading.Thread(target=self._receive_movements)
            thread.daemon = True
            thread.start()
            return True
        return False

    def _receive_movements(self):
        while self.running:
            sample, _ = self.inlet.pull_sample(timeout=0.1)
            if sample:
                self.movement_queue.put(sample)

    def run(self):
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Get neural movements
            if not self.movement_queue.empty():
                movement = self.movement_queue.get()

                # Update position (movement[0] = x, movement[1] = y)
                self.avatar_pos[0] += movement[0] * 50  # Scale movement
                self.avatar_pos[1] += movement[1] * 50

                # Keep in bounds
                self.avatar_pos[0] = max(self.avatar_radius,
                                        min(800 - self.avatar_radius, self.avatar_pos[0]))
                self.avatar_pos[1] = max(self.avatar_radius,
                                        min(600 - self.avatar_radius, self.avatar_pos[1]))

                # Update gripper
                self.gripper_open = movement[3] < 0.5

            # Draw
            self.screen.fill((0, 0, 0))

            # Draw avatar
            color = (0, 255, 0) if self.gripper_open else (255, 0, 0)
            pygame.draw.circle(self.screen, color,
                             [int(self.avatar_pos[0]), int(self.avatar_pos[1])],
                             self.avatar_radius)

            # Draw gripper state
            if self.gripper_open:
                pygame.draw.circle(self.screen, (255, 255, 255),
                                 [int(self.avatar_pos[0]), int(self.avatar_pos[1])],
                                 self.avatar_radius + 5, 2)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

# Test script

if **name** == "**main**":
controller = SimpleAvatarController()
if controller.connect_neural_stream():
controller.run()
else:
print("No neural stream found. Run movement decoder first.")

For full Omniverse (skip if no GPU):

Create neural-engine/omniverse/neural_avatar_system.py with the complete implementation
Create neural-engine/omniverse/deployment/omniverse-kubernetes.yaml

Task 13: Create API Implementation

Create neural-engine/api/**init**.py
Create neural-engine/api/app.py:

pythonfrom flask import Flask, request, jsonify
from neural_engine.functions.neural_ingestion.main import NeuralDataIngestion
from neural_engine.security.access_control import RoleBasedAccessControl
import os

app = Flask(**name**)
rbac = RoleBasedAccessControl()
ingestion = NeuralDataIngestion()

@app.route('/health', methods=['GET'])
def health():
return jsonify({'status': 'healthy'}), 200

@app.route('/v1/ingest/neural-data', methods=['POST'])
@rbac.require_permission('write:neural_data')
def ingest_neural_data():
return ingestion.ingest_neural_data(request)

@app.route('/v1/sessions/<session_id>', methods=['GET'])
@rbac.require_permission('read:sessions')
def get_session(session_id): # Implementation here
return jsonify({'session_id': session_id, 'status': 'mock'}), 200

if **name** == '**main**':
port = int(os.environ.get('PORT', 8080))
app.run(host='0.0.0.0', port=port)

Create neural-engine/api/openapi.yaml with the complete API specification

Task 14: Implement MCP Server

Initialize npm project in neural-engine/mcp-server/:

bashcd neural-engine/mcp-server
npm init -y
npm install @modelcontextprotocol/sdk @google-cloud/bigquery @google-cloud/pubsub @google-cloud/firestore

Create neural-engine/mcp-server/package.json:

json{
"name": "neurascale-mcp-server",
"version": "1.0.0",
"type": "module",
"main": "src/neurascale-mcp-server.js",
"scripts": {
"start": "node src/neurascale-mcp-server.js"
},
"dependencies": {
"@modelcontextprotocol/sdk": "^0.5.0",
"@google-cloud/bigquery": "^6.2.0",
"@google-cloud/pubsub": "^3.7.3",
"@google-cloud/firestore": "^6.7.0"
}
}

Create neural-engine/mcp-server/src/neurascale-mcp-server.js with the complete TypeScript implementation (rename to .js and adjust syntax for JavaScript)

Phase 5: Infrastructure and Deployment (Tasks 15-18)
Task 15: Create Terraform Configuration

Initialize Terraform:

bashcd terraform
terraform init

Create terraform/main.tf with the complete infrastructure code
Create terraform/variables.tf:

hclvariable "project_id" {
description = "GCP Project ID"
type = string
}

variable "region" {
description = "GCP Region"
type = string
default = "northamerica-northeast1"
}

variable "zone" {
description = "GCP Zone"
type = string
default = "northamerica-northeast1-a"
}

Create terraform/terraform.tfvars:

hclproject_id = "your-actual-project-id"

Plan and apply (be careful - this creates resources):

bashterraform plan

# Review the plan carefully

# terraform apply # Only run when ready to create resources

Task 16: Create Kubernetes Manifests

Create all YAML files in k8s/ directory structure:

k8s/deployments/neural-processor.yaml
k8s/deployments/movement-decoder.yaml
k8s/services/neurascale-service.yaml
k8s/configmaps/neurascale-config.yaml

Example deployment:
yaml# k8s/deployments/neural-processor.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
name: neural-processor
namespace: neurascale
spec:
replicas: 3
selector:
matchLabels:
app: neural-processor
template:
metadata:
labels:
app: neural-processor
spec:
containers: - name: processor
image: gcr.io/PROJECT_ID/neural-processor:latest
env: - name: GOOGLE_APPLICATION_CREDENTIALS
value: /secrets/gcp/key.json
resources:
requests:
memory: "2Gi"
cpu: "1"
limits:
memory: "4Gi"
cpu: "2"
volumeMounts: - name: gcp-key
mountPath: /secrets/gcp
readOnly: true
volumes: - name: gcp-key
secret:
secretName: gcp-service-account-key
Task 17: Create Docker Images

Create docker/Dockerfile.processor:

dockerfileFROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY neural-engine/ ./neural_engine/

ENV PYTHONPATH=/app

CMD ["python", "-m", "neural_engine.dataflow.neural_processing_pipeline"]

Create similar Dockerfiles for other components
Build images:

bashdocker build -t neural-processor -f docker/Dockerfile.processor .
Task 18: Create CI/CD Pipeline

Create .github/workflows/neurascale-cicd.yaml with the complete pipeline
Create test files:

tests/unit/test_ingestion.py
tests/integration/test_pipeline.py
tests/performance/locustfile.py

Phase 6: Testing and Documentation (Tasks 19-20)
Task 19: Implement Complete Test Suite

Create tests/test_e2e.py with the complete end-to-end test suite
Create tests/conftest.py for pytest configuration:

pythonimport pytest
import os

@pytest.fixture(scope="session")
def gcp_project():
return os.environ.get("PROJECT_ID", "test-project")

@pytest.fixture(scope="session")
def test_config():
return {
"project_id": "test-project",
"region": "northamerica-northeast1",
"use_emulator": True
}

Run tests:

bashpytest tests/unit/ -v
pytest tests/integration/ -v -m "not performance"
Task 20: Create Documentation

Create main README.md with the provided content
Create docs/API.md with detailed API documentation
Create docs/DEPLOYMENT.md:

markdown# Deployment Guide

## Prerequisites

- GCP Project with billing enabled
- kubectl configured
- Docker images built and pushed

## Deployment Steps

1. Deploy infrastructure:
   ```bash
   cd terraform
   terraform apply
   ```

Deploy to GKE:
bash./deploy/deploy.sh

Verify deployment:
bashkubectl get pods -n neurascale
kubectl get svc -n neurascale

Monitoring

Grafana: https://monitor.neurascale.io
Logs: gcloud logging read "resource.type=k8s_cluster"

## Final Integration Test

### Task 21: Run Full System Test

Create `test_full_system.py`:

````python
#!/usr/bin/env python3
"""
Full system integration test
Tests the complete flow from neural data to avatar movement
"""

import time
import threading
from neural_engine.devices.device_interfaces import OpenBCIDevice
from neural_engine.processing.movement_decoder import RealtimeMovementDecoder
from neural_engine.omniverse.simple_avatar_controller import SimpleAvatarController

def run_full_test():
    print("🧠 Starting NeuraScale Neural Engine Test...")

    # 1. Start synthetic BCI device
    print("📡 Starting synthetic BCI device...")
    device = OpenBCIDevice(board_type='synthetic')
    if not device.connect():
        print("❌ Failed to connect to device")
        return
    device.start_streaming()
    print("✅ BCI streaming started")

    # 2. Start movement decoder
    print("🔄 Starting movement decoder...")
    decoder = RealtimeMovementDecoder()
    if not decoder.connect_to_stream('OpenBCI_Stream'):
        print("❌ Failed to connect decoder to stream")
        return
    decoder.start_decoding()
    print("✅ Movement decoder started")

    # 3. Start avatar controller
    print("🎮 Starting avatar controller...")
    controller = SimpleAvatarController()
    if not controller.connect_neural_stream():
        print("❌ Failed to connect avatar to movement stream")
        return

    print("✅ All systems connected!")
    print("👁️  Watch the avatar move based on simulated neural signals")
    print("Press Ctrl+C to stop")

    # Run avatar controller (blocking)
    try:
        controller.run()
    except KeyboardInterrupt:
        print("\n🛑 Stopping systems...")
    finally:
        device.stop_streaming()
        decoder.running = False

if __name__ == "__main__":
    run_full_test()
Run the test:
bashpython test_full_system.py
Troubleshooting Guide
Common Issues and Solutions

LSL Stream Not Found

Check firewall settings
Ensure all components are on same network
Try running python -c "from pylsl import resolve_streams; print(resolve_streams())"


Google Cloud Authentication Errors

Verify GOOGLE_APPLICATION_CREDENTIALS is set
Check service account has necessary permissions
Run gcloud auth application-default login for local development


Docker Build Failures

Ensure all Python packages are in requirements.txt
Check for conflicting package versions
Use --no-cache flag when building


High Latency in Pipeline

Check Dataflow autoscaling settings
Optimize feature extraction code
Consider using more powerful machine types


Kubernetes Deployment Issues

Verify cluster credentials: kubectl cluster-info
Check pod logs: kubectl logs -n neurascale <pod-name>
Ensure secrets are created before deployment



Success Checklist

 Project structure created
 Python environment configured
 Google Cloud APIs enabled
 Neural ingestion working locally
 Signal processing pipeline running
 ML models created and tested
 Device interfaces connecting
 Simple avatar controller working
 API endpoints responding
 MCP server running
 Docker images building
 Unit tests passing
 Integration test successful
 Documentation complete
 Full system test shows avatar movement

Next Steps

Deploy to Cloud: Once local testing is complete, deploy to GCP
Add Real Devices: Connect actual BCI hardware
Train Custom Models: Use collected data to improve decoders
Enhance Omniverse: Add full NVIDIA Omniverse with GPU support
Scale Testing: Run performance tests with multiple concurrent users

Remember to commit frequently and document any deviations from these instructions!

Additional Files for Claude Dev
1. Environment Configuration Template
Create .env.example:
bash# Google Cloud Configuration
PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=./key.json
REGION=northamerica-northeast1
ZONE=northamerica-northeast1-a

# API Configuration
API_PORT=8080
API_HOST=0.0.0.0

# Neural Processing Configuration
MAX_CHANNELS=1024
DEFAULT_SAMPLING_RATE=1000
LATENCY_TARGET_MS=50

# Development Settings
DEBUG=true
USE_EMULATOR=false
2. Development Docker Compose
Create docker-compose.dev.yml:
yamlversion: '3.8'

services:
  # Local development services
  firestore-emulator:
    image: google/cloud-sdk:latest
    command: gcloud beta emulators firestore start --host-port=0.0.0.0:8081
    ports:
      - "8081:8081"
    environment:
      - FIRESTORE_EMULATOR_HOST=localhost:8081

  pubsub-emulator:
    image: google/cloud-sdk:latest
    command: gcloud beta emulators pubsub start --host-port=0.0.0.0:8085
    ports:
      - "8085:8085"
    environment:
      - PUBSUB_EMULATOR_HOST=localhost:8085

  neural-processor:
    build:
      context: .
      dockerfile: docker/Dockerfile.processor
    environment:
      - GOOGLE_APPLICATION_CREDENTIALS=/app/key.json
      - FIRESTORE_EMULATOR_HOST=firestore-emulator:8081
      - PUBSUB_EMULATOR_HOST=pubsub-emulator:8085
    volumes:
      - ./key.json:/app/key.json:ro
      - ./neural-engine:/app/neural_engine
    depends_on:
      - firestore-emulator
      - pubsub-emulator

  api:
    build:
      context: .
      dockerfile: docker/Dockerfile.api
    ports:
      - "8080:8080"
    environment:
      - GOOGLE_APPLICATION_CREDENTIALS=/app/key.json
      - FIRESTORE_EMULATOR_HOST=firestore-emulator:8081
    volumes:
      - ./key.json:/app/key.json:ro
      - ./neural-engine:/app/neural_engine
    depends_on:
      - firestore-emulator
3. Setup Script
Create setup.sh:
bash#!/bin/bash
set -e

echo "🚀 Setting up NeuraScale Neural Engine development environment..."

# Check prerequisites
echo "Checking prerequisites..."
command -v python3 >/dev/null 2>&1 || { echo "Python 3 is required but not installed. Aborting." >&2; exit 1; }
command -v gcloud >/dev/null 2>&1 || { echo "Google Cloud SDK is required but not installed. Aborting." >&2; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "Docker is required but not installed. Aborting." >&2; exit 1; }

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup Google Cloud
echo "Setting up Google Cloud..."
if [ ! -f "key.json" ]; then
    echo "⚠️  No service account key found. Please run:"
    echo "gcloud iam service-accounts keys create key.json --iam-account=neurascale-dev@PROJECT_ID.iam.gserviceaccount.com"
fi

# Create necessary directories
echo "Creating directory structure..."
mkdir -p data/datasets
mkdir -p logs
mkdir -p models/saved
mkdir -p temp

# Download sample data
echo "Downloading sample datasets..."
# Add dataset download commands here

echo "✅ Setup complete! Next steps:"
echo "1. Copy .env.example to .env and fill in your values"
echo "2. Run 'source venv/bin/activate' to activate virtual environment"
echo "3. Run './run_local_test.sh' to test the system"
4. Local Test Runner
Create run_local_test.sh:
bash#!/bin/bash
source venv/bin/activate

echo "🧪 Running NeuraScale local test suite..."

# Start emulators in background
echo "Starting emulators..."
gcloud beta emulators firestore start --host-port=localhost:8081 &
FIRESTORE_PID=$!
gcloud beta emulators pubsub start --host-port=localhost:8085 &
PUBSUB_PID=$!

# Wait for emulators to start
sleep 5

# Set emulator environment variables
export FIRESTORE_EMULATOR_HOST=localhost:8081
export PUBSUB_EMULATOR_HOST=localhost:8085

# Run component tests
echo "Testing neural ingestion..."
python -m pytest tests/unit/test_ingestion.py -v

echo "Testing signal processing..."
python -m pytest tests/unit/test_processing.py -v

echo "Starting full system test..."
python test_full_system.py

# Cleanup
kill $FIRESTORE_PID $PUBSUB_PID

echo "✅ Tests complete!"
5. Requirements for Development
Create requirements-dev.txt:
pytest==7.4.0
pytest-asyncio==0.21.1
pytest-cov==4.1.0
black==23.7.0
flake8==6.1.0
mypy==1.5.1
locust==2.15.1
jupyter==1.0.0
ipython==8.14.0
6. Quick Start Guide
Create QUICKSTART.md:
markdown# NeuraScale Neural Engine - Quick Start Guide

## 🚀 5-Minute Setup

1. **Clone and Setup**
   ```bash
   git clone <repository>
   cd neurascale-neural-engine
   chmod +x setup.sh
   ./setup.sh

Configure Environment
bashcp .env.example .env
# Edit .env with your project details

Run Local Test
bash./run_local_test.sh


🧪 Testing Individual Components
Test Neural Ingestion Only
bashpython -m neural_engine.functions.neural_ingestion.main
Test Signal Processing Only
bashpython -m neural_engine.processing.movement_decoder
Test Simple Avatar
bashpython -m neural_engine.omniverse.simple_avatar_controller
🐛 Common Issues

"No module named neural_engine"

Run: export PYTHONPATH=$PYTHONPATH:$(pwd)


"Google Cloud credentials not found"

Run: export GOOGLE_APPLICATION_CREDENTIALS=./key.json


"LSL stream timeout"

Check firewall isn't blocking UDP ports
Try: sudo ufw allow 16571:16604/udp



📊 Monitoring Local Performance
Start the performance monitor:
bashpython -m neural_engine.monitoring.performance_metrics
View real-time metrics at: http://localhost:9090

### 7. Makefile for Common Tasks
Create `Makefile`:
```makefile
.PHONY: help setup test clean deploy

help:
    @echo "NeuraScale Neural Engine - Available commands:"
    @echo "  make setup    - Set up development environment"
    @echo "  make test     - Run all tests"
    @echo "  make clean    - Clean up generated files"
    @echo "  make deploy   - Deploy to Google Cloud"
    @echo "  make run      - Run local development server"

setup:
    ./setup.sh

test:
    pytest tests/ -v --cov=neural_engine

test-unit:
    pytest tests/unit/ -v

test-integration:
    pytest tests/integration/ -v -m "not performance"

test-performance:
    pytest tests/performance/ -v -m "performance"

run:
    ./run_local_test.sh

clean:
    find . -type f -name "*.pyc" -delete
    find . -type d -name "__pycache__" -delete
    rm -rf .pytest_cache
    rm -rf .coverage
    rm -rf htmlcov

docker-build:
    docker build -t neural-processor -f docker/Dockerfile.processor .
    docker build -t neural-api -f docker/Dockerfile.api .

docker-run:
    docker-compose -f docker-compose.dev.yml up

deploy-staging:
    gcloud builds submit --tag gcr.io/$(PROJECT_ID)/neural-processor:staging
    gcloud run deploy neural-api-staging --image gcr.io/$(PROJECT_ID)/neural-processor:staging --region $(REGION)

format:
    black neural-engine/
    isort neural-engine/

lint:
    flake8 neural-engine/
    mypy neural-engine/
8. VS Code Configuration
Create .vscode/settings.json:
json{
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestArgs": [
        "tests"
    ],
    "python.testing.unittestEnabled": false,
    "python.testing.pytestEnabled": true,
    "python.envFile": "${workspaceFolder}/.env",
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
Create .vscode/launch.json:
json{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Neural Processor",
            "type": "python",
            "request": "launch",
            "module": "neural_engine.processing.movement_decoder",
            "justMyCode": true,
            "env": {
                "PYTHONPATH": "${workspaceFolder}",
                "GOOGLE_APPLICATION_CREDENTIALS": "${workspaceFolder}/key.json"
            }
        },
        {
            "name": "Python: API Server",
            "type": "python",
            "request": "launch",
            "module": "neural_engine.api.app",
            "justMyCode": true,
            "env": {
                "PYTHONPATH": "${workspaceFolder}",
                "GOOGLE_APPLICATION_CREDENTIALS": "${workspaceFolder}/key.json",
                "FLASK_ENV": "development"
            }
        },
        {
            "name": "Python: Full System Test",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/test_full_system.py",
            "console": "integratedTerminal",
            "justMyCode": true
        }
    ]
}
Summary
With these additional files, Claude Dev will have:

Easy setup: One-command setup script
Local development: Docker Compose for emulators
Quick testing: Shell scripts for common tasks
IDE support: VS Code configurations
Build automation: Makefile for common commands
Environment management: .env template
Clear documentation: Quick start guide
````
