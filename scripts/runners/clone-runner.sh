#!/bin/bash

# Clone existing runner configuration
echo "Setting up additional runners by cloning existing configuration..."

# Check if original runner exists
if [ ! -d "/Users/weg/actions-runner" ]; then
    echo "Error: Original runner not found at /Users/weg/actions-runner"
    exit 1
fi

# Function to setup a runner
setup_runner() {
    local NUM=$1
    local RUNNER_DIR="/Users/weg/actions-runner-${NUM}"
    local RUNNER_NAME="neurascale-local-${NUM}"

    echo ""
    echo "Setting up Runner ${NUM}..."

    # Skip if already exists
    if [ -d "$RUNNER_DIR" ]; then
        echo "Runner ${NUM} directory already exists. Checking if configured..."
        if [ -f "$RUNNER_DIR/.runner" ]; then
            echo "Runner ${NUM} is already configured. Starting it..."
            cd "$RUNNER_DIR"
            nohup ./run.sh > runner-${NUM}.log 2>&1 &
            echo "Runner ${NUM} started with PID $!"
            return
        fi
    fi

    # Create directory
    mkdir -p "$RUNNER_DIR"

    # Copy runner files from original
    echo "Copying runner files..."
    cp -R /Users/weg/actions-runner/* "$RUNNER_DIR/" 2>/dev/null || {
        echo "Failed to copy runner files. Downloading fresh..."
        cd "$RUNNER_DIR"
        curl -o actions-runner-osx-arm64-2.327.0.tar.gz -L \
            https://github.com/actions/runner/releases/download/v2.327.0/actions-runner-osx-arm64-2.327.0.tar.gz
        tar xzf ./actions-runner-osx-arm64-2.327.0.tar.gz
        rm actions-runner-osx-arm64-2.327.0.tar.gz
    }

    # Remove existing runner config
    rm -f "$RUNNER_DIR/.runner"
    rm -f "$RUNNER_DIR/.credentials"
    rm -f "$RUNNER_DIR/.credentials_rsaparams"

    # Configure runner (will prompt for token)
    cd "$RUNNER_DIR"
    echo ""
    echo "Now you need to configure Runner ${NUM}:"
    echo "1. Go to: https://github.com/identity-wael/neurascale/settings/actions/runners/new"
    echo "2. Copy the token"
    echo "3. Paste it below when prompted"
    echo ""

    ./config.sh \
        --url https://github.com/identity-wael/neurascale \
        --name "$RUNNER_NAME" \
        --labels "self-hosted,macOS,ARM64,neural-engine" \
        --work "_work"

    # Start the runner
    echo "Starting Runner ${NUM}..."
    nohup ./run.sh > runner-${NUM}.log 2>&1 &
    echo "Runner ${NUM} started with PID $!"
}

# Setup runners 2-6
for i in {2..6}; do
    setup_runner $i
done

echo ""
echo "All runners set up!"
echo ""
echo "Check status with:"
echo "  gh api repos/identity-wael/neurascale/actions/runners --jq '.runners[] | {name: .name, status: .status}'"
echo ""
echo "View logs with:"
echo "  tail -f /Users/weg/actions-runner-*/runner-*.log"
echo ""
echo "Stop all runners with:"
echo "  pkill -f 'Runner.Listener'"
