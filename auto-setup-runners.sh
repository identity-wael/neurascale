#!/bin/bash

# Automated runner setup using GitHub CLI
echo "Automated GitHub Actions Runner Setup"
echo "====================================="

# Check if gh is authenticated
if ! gh auth status >/dev/null 2>&1; then
    echo "Error: GitHub CLI not authenticated"
    echo "Run: gh auth login"
    exit 1
fi

# Function to get a registration token
get_runner_token() {
    echo "Getting registration token from GitHub..."

    # Get token via API (requires admin access)
    TOKEN=$(gh api \
        --method POST \
        -H "Accept: application/vnd.github+json" \
        -H "X-GitHub-Api-Version: 2022-11-28" \
        /repos/identity-wael/neurascale/actions/runners/registration-token \
        --jq .token 2>/dev/null)

    if [ -z "$TOKEN" ]; then
        echo "Could not get token automatically. Trying browser method..."
        echo ""
        echo "Opening GitHub runners page..."
        open "https://github.com/identity-wael/neurascale/settings/actions/runners/new"
        echo ""
        echo "Please copy the token from the page that just opened"
        echo "The token starts with 'AHRA...'"
        echo ""
        read -p "Paste token here: " TOKEN
    fi

    echo "$TOKEN"
}

# Get registration token
TOKEN=$(get_runner_token)

if [ -z "$TOKEN" ]; then
    echo "Error: No token provided"
    exit 1
fi

echo "Got token: ${TOKEN:0:10}..."

# Setup each runner
for i in {2..6}; do
    RUNNER_DIR="/Users/weg/actions-runner-${i}"
    RUNNER_NAME="neurascale-local-${i}"

    echo ""
    echo "Setting up Runner ${i}: ${RUNNER_NAME}"
    echo "======================================="

    # Create directory
    mkdir -p "$RUNNER_DIR"
    cd "$RUNNER_DIR"

    # Download runner if not exists
    if [ ! -f "config.sh" ]; then
        echo "Downloading runner package..."
        curl -o actions-runner-osx-arm64-2.327.0.tar.gz -L \
            https://github.com/actions/runner/releases/download/v2.327.0/actions-runner-osx-arm64-2.327.0.tar.gz

        echo "Extracting..."
        tar xzf ./actions-runner-osx-arm64-2.327.0.tar.gz
        rm actions-runner-osx-arm64-2.327.0.tar.gz
    fi

    # Configure runner
    echo "Configuring runner..."
    ./config.sh \
        --url https://github.com/identity-wael/neurascale \
        --token "$TOKEN" \
        --name "$RUNNER_NAME" \
        --labels "self-hosted,macOS,ARM64,neural-engine" \
        --work "_work" \
        --unattended \
        --replace

    # Start runner in background
    echo "Starting runner..."
    nohup ./run.sh > runner.log 2>&1 &
    RUNNER_PID=$!
    echo "Runner started with PID: $RUNNER_PID"

    # Give it a moment to start
    sleep 2
done

echo ""
echo "All runners configured!"
echo ""
echo "Checking runner status..."
sleep 5

# Check status
gh api repos/identity-wael/neurascale/actions/runners --jq '.runners[] | "\(.name): \(.status)"'

echo ""
echo "Setup complete! You now have 6 parallel runners."
echo ""
echo "Monitor with: gh api repos/identity-wael/neurascale/actions/runners --jq '.runners[] | {name: .name, status: .status, busy: .busy}'"
echo "View logs: tail -f /Users/weg/actions-runner-*/runner.log"
echo "Stop all: pkill -f Runner.Listener"
