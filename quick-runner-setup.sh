#!/bin/bash

# Quick runner setup - requires token as argument
TOKEN=$1

if [ -z "$TOKEN" ]; then
    echo "Usage: $0 <registration-token>"
    echo "Get token from: https://github.com/identity-wael/neurascale/settings/actions/runners/new"
    exit 1
fi

# Runner 2
cd /Users/weg
mkdir -p actions-runner-2 && cd actions-runner-2
curl -o actions-runner-osx-arm64-2.327.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.327.0/actions-runner-osx-arm64-2.327.0.tar.gz
tar xzf ./actions-runner-osx-arm64-2.327.0.tar.gz
./config.sh --url https://github.com/identity-wael/neurascale --token $TOKEN --name neurascale-local-2 --labels "self-hosted,macOS,ARM64,neural-engine" --unattended
./run.sh &

# Runner 3
cd /Users/weg
mkdir -p actions-runner-3 && cd actions-runner-3
curl -o actions-runner-osx-arm64-2.327.0.tar.gz -L https://github.com/actions/runner/releases/download/v2.327.0/actions-runner-osx-arm64-2.327.0.tar.gz
tar xzf ./actions-runner-osx-arm64-2.327.0.tar.gz
./config.sh --url https://github.com/identity-wael/neurascale --token $TOKEN --name neurascale-local-3 --labels "self-hosted,macOS,ARM64,neural-engine" --unattended
./run.sh &

echo "Runners 2 and 3 are starting..."
echo "Check status with: gh api repos/identity-wael/neurascale/actions/runners"
