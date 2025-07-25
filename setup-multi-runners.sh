#!/bin/bash

# GitHub Actions Multi-Runner Setup Script
# Optimized for 24GB RAM, 12 CPUs

set -e

# Configuration
RUNNER_VERSION="2.327.0"  # Match your existing runner version
RUNNER_COUNT=6  # 6 runners for optimal parallel execution
BASE_DIR="/Users/weg"
REPO_URL="https://github.com/identity-wael/neurascale"

echo "Setting up $RUNNER_COUNT GitHub Actions runners..."

# Get registration token (you'll need to provide this)
echo "Please get a registration token from:"
echo "https://github.com/identity-wael/neurascale/settings/actions/runners/new"
echo ""
read -p "Enter registration token: " REGISTRATION_TOKEN

if [ -z "$REGISTRATION_TOKEN" ]; then
    echo "Registration token is required!"
    exit 1
fi

# Setup each runner
for i in $(seq 2 $RUNNER_COUNT); do
    RUNNER_NAME="neurascale-local-${i}"
    RUNNER_DIR="${BASE_DIR}/actions-runner-${i}"

    echo ""
    echo "Setting up runner $i: $RUNNER_NAME"
    echo "Directory: $RUNNER_DIR"

    # Check if directory already exists
    if [ -d "$RUNNER_DIR" ]; then
        echo "Runner directory already exists. Skipping..."
        continue
    fi

    # Create runner directory
    mkdir -p "$RUNNER_DIR"
    cd "$RUNNER_DIR"

    # Download runner
    echo "Downloading runner..."
    curl -o actions-runner-osx-arm64-${RUNNER_VERSION}.tar.gz -L \
        https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-osx-arm64-${RUNNER_VERSION}.tar.gz

    # Extract
    echo "Extracting runner..."
    tar xzf ./actions-runner-osx-arm64-${RUNNER_VERSION}.tar.gz
    rm actions-runner-osx-arm64-${RUNNER_VERSION}.tar.gz

    # Configure runner
    echo "Configuring runner..."
    ./config.sh --url "$REPO_URL" \
        --token "$REGISTRATION_TOKEN" \
        --name "$RUNNER_NAME" \
        --labels "self-hosted,macOS,ARM64,neural-engine" \
        --work "_work" \
        --unattended \
        --replace

    # Install as service
    echo "Installing service..."
    ./svc.sh install

    # Start service
    echo "Starting service..."
    ./svc.sh start

    echo "Runner $RUNNER_NAME setup complete!"
done

echo ""
echo "All runners setup complete!"
echo ""
echo "Runner status:"
for i in $(seq 1 $RUNNER_COUNT); do
    if [ $i -eq 1 ]; then
        RUNNER_DIR="${BASE_DIR}/actions-runner"
    else
        RUNNER_DIR="${BASE_DIR}/actions-runner-${i}"
    fi

    if [ -d "$RUNNER_DIR" ]; then
        echo -n "Runner $i: "
        cd "$RUNNER_DIR"
        ./svc.sh status || echo "Not running as service"
    fi
done

echo ""
echo "To manage runners:"
echo "  Start:  /Users/weg/actions-runner-N/svc.sh start"
echo "  Stop:   /Users/weg/actions-runner-N/svc.sh stop"
echo "  Status: /Users/weg/actions-runner-N/svc.sh status"

# Create runner management script
cat > "${BASE_DIR}/manage-runners.sh" << 'EOF'
#!/bin/bash

ACTION=$1
RUNNER_COUNT=6

if [ -z "$ACTION" ]; then
    echo "Usage: $0 [start|stop|status|restart]"
    exit 1
fi

for i in $(seq 1 $RUNNER_COUNT); do
    if [ $i -eq 1 ]; then
        RUNNER_DIR="/Users/weg/actions-runner"
    else
        RUNNER_DIR="/Users/weg/actions-runner-${i}"
    fi

    if [ -d "$RUNNER_DIR" ]; then
        echo "Runner $i: $ACTION"
        cd "$RUNNER_DIR"
        ./svc.sh $ACTION || ./run.sh &
    fi
done
EOF

chmod +x "${BASE_DIR}/manage-runners.sh"

echo ""
echo "Created runner management script: ${BASE_DIR}/manage-runners.sh"
echo "Usage: ${BASE_DIR}/manage-runners.sh [start|stop|status|restart]"
