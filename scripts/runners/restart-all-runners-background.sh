#!/bin/bash
set -e

echo "🚀 Restarting ALL GitHub Actions runners with maximum performance settings"
echo "=============================================================="

# Check system info
echo "System information:"
sysctl -n hw.ncpu || echo "CPU cores: Unable to detect"
sysctl -n hw.memsize | awk '{print "Total RAM: " $1/1024/1024/1024 " GB"}' || echo "RAM: Unable to detect"

# Stop all existing runner processes
echo ""
echo "Stopping all existing runner processes..."
pkill -f "Runner.Listener" || true
pkill -f "Runner.Worker" || true
sleep 3

# Performance settings for M3 Pro
export PARALLEL_JOBS=12
export MAKEFLAGS="-j12"
export CMAKE_BUILD_PARALLEL_LEVEL=12
export PYTHONUNBUFFERED=1
export PIP_PARALLEL_DOWNLOADS=10
export TF_ENABLE_ONEDNN_OPTS=1
export NODE_OPTIONS="--max-old-space-size=8192"
export RUNNER_ALLOW_RUNASROOT=0
export GPG_PATH="/opt/homebrew/bin/gpg"

# Function to update runner .env file
update_runner_env() {
    local runner_dir=$1
    local env_file="$runner_dir/.env"

    # Remove old performance settings if they exist
    if [ -f "$env_file" ]; then
        grep -v "M3 Pro Performance Settings" "$env_file" | \
        grep -v "PARALLEL_JOBS=" | \
        grep -v "MAKEFLAGS=" | \
        grep -v "CMAKE_BUILD_PARALLEL_LEVEL=" | \
        grep -v "PYTHONUNBUFFERED=" | \
        grep -v "PIP_PARALLEL_DOWNLOADS=" | \
        grep -v "TF_ENABLE_ONEDNN_OPTS=" | \
        grep -v "NODE_OPTIONS=" | \
        grep -v "GPG_PATH=" > "$env_file.tmp" || true
        mv "$env_file.tmp" "$env_file"
    fi

    # Add new performance settings
    cat >> "$env_file" << EOF

# M3 Pro Performance Settings
PARALLEL_JOBS=12
MAKEFLAGS=-j12
CMAKE_BUILD_PARALLEL_LEVEL=12
PYTHONUNBUFFERED=1
PIP_PARALLEL_DOWNLOADS=10
TF_ENABLE_ONEDNN_OPTS=1
NODE_OPTIONS=--max-old-space-size=8192
GPG_PATH=/opt/homebrew/bin/gpg
EOF
}

# Find all configured runners
echo ""
echo "Finding all configured runners..."
RUNNER_DIRS=()

# Check standard locations
for i in "" {2..6}; do
    dir="/Users/weg/actions-runner${i:+-$i}"
    if [ -d "$dir" ] && [ -f "$dir/config.sh" ]; then
        RUNNER_DIRS+=("$dir")
        echo "  Found runner: $dir"
    fi
done

if [ ${#RUNNER_DIRS[@]} -eq 0 ]; then
    echo "No configured runners found!"
    exit 1
fi

echo ""
echo "Starting ${#RUNNER_DIRS[@]} runners with maximum performance..."
echo ""

# Start each runner
for runner_dir in "${RUNNER_DIRS[@]}"; do
    runner_name=$(basename "$runner_dir")
    echo "Starting $runner_name..."

    # Update environment file
    update_runner_env "$runner_dir"

    # Start runner in background with maximum priority
    cd "$runner_dir"
    nohup nice -n -20 ./run.sh > runner.log 2>&1 &
    RUNNER_PID=$!

    echo "  ✓ Started with PID: $RUNNER_PID"
    echo "  ✓ Log file: $runner_dir/runner.log"

    # Give it a moment to start
    sleep 2
done

echo ""
echo "✅ All runners restarted with maximum performance settings!"
echo ""
echo "Performance settings applied to all runners:"
echo "  - CPU Priority: Maximum (nice -20)"
echo "  - Parallel Jobs: 12 cores"
echo "  - Memory: 8GB for Node.js processes"
echo "  - Parallel pip downloads: 10"
echo "  - TensorFlow optimizations enabled"
echo "  - GPG path configured for Codecov"
echo ""
echo "Monitor runners:"
echo "  - View all logs: tail -f /Users/weg/actions-runner*/runner.log"
echo "  - Check status: ps aux | grep Runner.Listener"
echo "  - GitHub status: gh api repos/identity-wael/neurascale/actions/runners --jq '.runners[] | {name: .name, status: .status, busy: .busy}'"
echo ""
echo "Stop all runners:"
echo "  - pkill -f Runner.Listener"
