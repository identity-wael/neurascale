#!/bin/bash
set -e

echo "🚀 Preparing cache for self-hosted GitHub Actions runner"

# Create cache directories
CACHE_DIR="${HOME}/.neural-engine-cache"
mkdir -p "$CACHE_DIR/pip"
mkdir -p "$CACHE_DIR/venv"

# Create Python virtual environment with cached packages
echo "Creating cached Python environment..."
cd "$(dirname "$0")"

# Create venv if it doesn't exist
if [ ! -d "$CACHE_DIR/venv/neural-engine" ]; then
    python3 -m venv "$CACHE_DIR/venv/neural-engine"
fi

# Activate venv
source "$CACHE_DIR/venv/neural-engine/bin/activate"

# Upgrade pip
pip install --upgrade pip

# Install all dependencies with cache
echo "Installing and caching dependencies..."
pip install --cache-dir="$CACHE_DIR/pip" -r requirements.txt
pip install --cache-dir="$CACHE_DIR/pip" -r requirements-dev.txt

# Pre-download large models/data
echo "Pre-downloading large assets..."
python -c "
import tensorflow as tf
print('TensorFlow version:', tf.__version__)
# This ensures TensorFlow is properly configured
"

# Create runner environment script
cat > "$CACHE_DIR/setup-env.sh" << EOF
#!/bin/bash
# Source this script in your runner to use cached environment
export PIP_CACHE_DIR="$CACHE_DIR/pip"
export VIRTUAL_ENV="$CACHE_DIR/venv/neural-engine"
export PATH="\$VIRTUAL_ENV/bin:\$PATH"
echo "✅ Using cached neural-engine environment"
EOF

chmod +x "$CACHE_DIR/setup-env.sh"

echo "✅ Cache prepared successfully!"
echo ""
echo "To use in GitHub Actions runner, add to your runner's .env file:"
echo "NEURAL_ENGINE_CACHE_DIR=$CACHE_DIR"
echo ""
echo "Or source the setup script:"
echo "source $CACHE_DIR/setup-env.sh"
