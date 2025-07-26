#!/bin/bash
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

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Create necessary directories
echo "Creating directory structure..."
mkdir -p data/datasets
mkdir -p logs
mkdir -p models/saved
mkdir -p temp

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# Google Cloud Configuration
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
EOF
fi

echo "✅ Setup complete! Next steps:"
echo "1. Copy your Google Cloud service account key to ./key.json"
echo "2. Update .env with your project details"
echo "3. Run 'source venv/bin/activate' to activate virtual environment"
echo "4. Run './configure-gcp.sh' to set up Google Cloud"
