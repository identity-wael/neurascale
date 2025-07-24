#!/bin/bash
set -e

echo "🚀 Restarting GitHub Actions runner with M3 Pro maximum performance settings"

# First, let's check system info
echo "System information:"
sysctl -n hw.ncpu || echo "CPU cores: Unable to detect"
sysctl -n hw.memsize | awk '{print "Total RAM: " $1/1024/1024/1024 " GB"}' || echo "RAM: Unable to detect"

# Kill any existing runner processes
echo "Stopping existing runner processes..."
pkill -f "Runner.Listener" || true
pkill -f "Runner.Worker" || true
sleep 2

# Set maximum performance environment variables
export PARALLEL_JOBS=12
export MAKEFLAGS="-j12"
export CMAKE_BUILD_PARALLEL_LEVEL=12
export PYTHONUNBUFFERED=1
export PIP_PARALLEL_DOWNLOADS=10
export TF_ENABLE_ONEDNN_OPTS=1
export NODE_OPTIONS="--max-old-space-size=8192"
export RUNNER_ALLOW_RUNASROOT=0

# Update runner .env file with performance settings
cat >> /Users/weg/actions-runner/.env << EOF

# M3 Pro Performance Settings
PARALLEL_JOBS=12
MAKEFLAGS=-j12
CMAKE_BUILD_PARALLEL_LEVEL=12
PYTHONUNBUFFERED=1
PIP_PARALLEL_DOWNLOADS=10
TF_ENABLE_ONEDNN_OPTS=1
NODE_OPTIONS=--max-old-space-size=8192
EOF

# Start the runner with maximum priority
echo "Starting runner with maximum performance..."
cd /Users/weg/actions-runner

# Run with nice priority for maximum CPU
nice -n -20 ./run.sh &

echo "✅ Runner restarted with maximum performance settings!"
echo ""
echo "Performance settings applied:"
echo "  - CPU Priority: Maximum (nice -20)"
echo "  - Parallel Jobs: 12 cores"
echo "  - Memory: 8GB for Node.js processes"
echo "  - Parallel pip downloads: 10"
echo "  - TensorFlow optimizations enabled"
echo ""
echo "The runner is now using most of your M3 Pro's power!"
