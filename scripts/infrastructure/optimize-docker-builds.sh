#!/bin/bash

# Docker optimization for multi-runner setup
# Configures Docker to handle multiple concurrent builds

echo "Optimizing Docker for multiple concurrent builds..."

# Increase Docker resource limits
cat > ~/docker-config.json << EOF
{
  "builder": {
    "gc": {
      "enabled": true,
      "defaultKeepStorage": "20GB"
    }
  },
  "experimental": true,
  "max-concurrent-downloads": 10,
  "max-concurrent-uploads": 10,
  "max-download-attempts": 5,
  "registry-mirrors": [],
  "cpu-period": 100000,
  "cpu-quota": 1200000,
  "memory": 24000000000,
  "memory-swap": 28000000000,
  "cpus": "12.0"
}
EOF

echo "Docker configuration updated."
echo ""
echo "To apply changes:"
echo "1. Open Docker Desktop"
echo "2. Go to Settings > Docker Engine"
echo "3. Merge the settings from ~/docker-config.json"
echo "4. Click 'Apply & Restart'"
echo ""
echo "Recommended Docker Desktop settings:"
echo "- CPUs: 12"
echo "- Memory: 20 GB (leaving 4GB for system)"
echo "- Swap: 4 GB"
echo "- Disk image size: 100 GB+"

# Create Docker buildx builders for parallel builds
echo ""
echo "Creating Docker buildx builders for parallel builds..."

for i in {1..3}; do
    BUILDER_NAME="neural-builder-$i"

    # Remove existing builder if exists
    docker buildx rm $BUILDER_NAME 2>/dev/null || true

    # Create new builder
    docker buildx create \
        --name $BUILDER_NAME \
        --driver docker-container \
        --config ~/docker-config.json \
        --use

    echo "Created builder: $BUILDER_NAME"
done

# Set default builder
docker buildx use neural-builder-1

echo ""
echo "Docker buildx builders created!"
docker buildx ls

echo ""
echo "Runner resource recommendations:"
echo "- Each runner typically uses: 2-4GB RAM, 2-3 CPUs during builds"
echo "- With 6 runners, peak usage: ~18GB RAM, 12 CPUs"
echo "- This leaves headroom for system operations"
