#!/bin/bash

# Start already configured runners
echo "Starting configured GitHub Actions runners..."
echo "========================================"

# Function to check and start a runner
start_runner() {
    local NUM=$1
    local RUNNER_DIR="/Users/weg/actions-runner-${NUM}"
    local RUNNER_NAME="neurascale-local-${NUM}"

    if [ ! -d "$RUNNER_DIR" ]; then
        echo "Runner $NUM directory not found at $RUNNER_DIR"
        return 1
    fi

    # Check if runner is configured
    if [ ! -f "$RUNNER_DIR/.runner" ]; then
        echo "Runner $NUM is not configured. Skipping..."
        return 1
    fi

    # Check if already running
    if pgrep -f "$RUNNER_DIR/bin/Runner.Listener" > /dev/null; then
        echo "Runner $NUM is already running"
        return 0
    fi

    echo "Starting Runner $NUM..."
    cd "$RUNNER_DIR" && nohup ./run.sh > runner.log 2>&1 &
    local PID=$!
    echo "Runner $NUM started with PID: $PID"

    # Give it a moment to start
    sleep 2

    # Verify it started
    if ps -p $PID > /dev/null; then
        echo "Runner $NUM is running successfully"
    else
        echo "Runner $NUM failed to start. Check $RUNNER_DIR/runner.log"
        return 1
    fi
}

# Check original runner
echo "Checking original runner..."
if pgrep -f "/Users/weg/actions-runner/bin/Runner.Listener" > /dev/null; then
    echo "Original runner is running"
else
    echo "Original runner is not running. Starting..."
    cd /Users/weg/actions-runner && nohup ./run.sh > runner.log 2>&1 &
    echo "Original runner started with PID: $!"
fi

echo ""

# Start runners 2-6
STARTED=0
FAILED=0

for i in {2..6}; do
    echo "Checking Runner $i..."
    if start_runner $i; then
        ((STARTED++))
    else
        ((FAILED++))
    fi
    echo ""
done

echo "========================================"
echo "Summary:"
echo "  Runners started: $STARTED"
echo "  Runners failed/skipped: $FAILED"
echo ""

# Check GitHub for connected runners
echo "Checking GitHub for connected runners..."
sleep 5
gh api repos/identity-wael/neurascale/actions/runners --jq '.runners[] | "\(.name): \(.status)"'

echo ""
echo "To configure missing runners, run:"
echo "  ./quick-runner-config.sh <registration-token>"
echo ""
echo "To monitor runners:"
echo "  watch 'ps aux | grep Runner.Listener | grep -v grep'"
echo ""
echo "To view logs:"
echo "  tail -f /Users/weg/actions-runner*/runner.log"
