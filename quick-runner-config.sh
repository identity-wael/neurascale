#!/bin/bash

# Quick runner configuration with automatic token retrieval
echo "Quick GitHub Actions Runner Configuration"
echo "========================================"

# Check if gh is authenticated
if ! gh auth status >/dev/null 2>&1; then
    echo "Error: GitHub CLI not authenticated"
    echo "Run: gh auth login"
    exit 1
fi

# Configuration
RUNNER_VERSION="2.327.0"
REPO_URL="https://github.com/identity-wael/neurascale"

# Function to configure a single runner
configure_runner() {
    local NUM=$1
    local RUNNER_DIR="/Users/weg/actions-runner-${NUM}"
    local RUNNER_NAME="neurascale-local-${NUM}"

    echo ""
    echo "Configuring Runner $NUM: $RUNNER_NAME"
    echo "--------------------------------------"

    # Check if already configured
    if [ -f "$RUNNER_DIR/.runner" ]; then
        echo "Runner $NUM is already configured. Skipping..."
        return 0
    fi

    # Create directory if needed
    if [ ! -d "$RUNNER_DIR" ]; then
        echo "Creating runner directory..."
        mkdir -p "$RUNNER_DIR"
    fi

    # Check if runner package exists
    if [ ! -f "$RUNNER_DIR/config.sh" ]; then
        echo "Downloading runner package..."
        cd "$RUNNER_DIR"
        curl -o actions-runner-osx-arm64-${RUNNER_VERSION}.tar.gz -L \
            https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-osx-arm64-${RUNNER_VERSION}.tar.gz

        echo "Extracting..."
        tar xzf ./actions-runner-osx-arm64-${RUNNER_VERSION}.tar.gz
        rm actions-runner-osx-arm64-${RUNNER_VERSION}.tar.gz
    fi

    # Get fresh token
    echo "Getting registration token..."
    TOKEN=$(gh api \
        --method POST \
        -H "Accept: application/vnd.github+json" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        /repos/identity-wael/neurascale/actions/runners/registration-token \
        --jq .token 2>/dev/null)

    if [ -z "$TOKEN" ]; then
        echo "Failed to get registration token. You may need admin access."
        return 1
    fi

    echo "Got token: ${TOKEN:0:10}..."

    # Configure runner
    cd "$RUNNER_DIR"
    echo "Configuring runner..."
    ./config.sh \
        --url "$REPO_URL" \
        --token "$TOKEN" \
        --name "$RUNNER_NAME" \
        --labels "self-hosted,macOS,ARM64,neural-engine" \
        --work "_work" \
        --unattended \
        --replace

    if [ $? -eq 0 ]; then
        echo "Runner $NUM configured successfully!"

        # Start the runner
        echo "Starting runner..."
        nohup ./run.sh > runner.log 2>&1 &
        local PID=$!
        echo "Runner started with PID: $PID"

        return 0
    else
        echo "Failed to configure runner $NUM"
        return 1
    fi
}

# Ask which runners to configure
echo "Which runners do you want to configure?"
echo "1. All runners (2-6)"
echo "2. Specific runners"
echo "3. Exit"
echo ""
read -p "Enter choice (1-3): " CHOICE

case $CHOICE in
    1)
        # Configure all runners
        for i in {2..6}; do
            configure_runner $i
            sleep 2  # Brief pause between runners
        done
        ;;
    2)
        # Configure specific runners
        read -p "Enter runner numbers (e.g., '2 3 5'): " RUNNERS
        for i in $RUNNERS; do
            if [[ $i =~ ^[2-6]$ ]]; then
                configure_runner $i
            else
                echo "Invalid runner number: $i (must be 2-6)"
            fi
        done
        ;;
    3)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "========================================"
echo "Configuration complete!"
echo ""

# Wait a moment for runners to register
sleep 5

# Check status
echo "Current runner status:"
gh api repos/identity-wael/neurascale/actions/runners --jq '.runners[] | "\(.name): \(.status)"'

echo ""
echo "Local runner processes:"
ps aux | grep -E "Runner.Listener" | grep -v grep | awk '{print $2, $11}' | while read pid path; do
    runner_dir=$(dirname $(dirname "$path"))
    runner_name=$(basename "$runner_dir")
    echo "  PID $pid: $runner_name"
done

echo ""
echo "To stop all runners: pkill -f 'Runner.Listener'"
echo "To view logs: tail -f /Users/weg/actions-runner-*/runner.log"
