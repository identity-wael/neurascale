#!/bin/bash
set -e

echo "🏃 Setting up GitHub Actions self-hosted runner for NeuraScale"

# Configuration
RUNNER_DIR="${HOME}/actions-runner"
REPO_URL="https://github.com/identity-wael/neurascale"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Prerequisites:${NC}"
echo "1. You need a GitHub Personal Access Token with 'repo' scope"
echo "2. Go to: https://github.com/settings/tokens/new"
echo "3. Or use the repository settings to get a runner token"
echo ""

# Create runner directory
mkdir -p $RUNNER_DIR
cd $RUNNER_DIR

# Detect OS and architecture
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

if [ "$ARCH" = "x86_64" ]; then
    ARCH="x64"
elif [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; then
    ARCH="arm64"
fi

# Download runner based on OS
RUNNER_VERSION="2.319.1"
if [ "$OS" = "darwin" ]; then
    RUNNER_FILE="actions-runner-osx-${ARCH}-${RUNNER_VERSION}.tar.gz"
elif [ "$OS" = "linux" ]; then
    RUNNER_FILE="actions-runner-linux-${ARCH}-${RUNNER_VERSION}.tar.gz"
else
    echo "Unsupported OS: $OS"
    exit 1
fi

echo -e "${GREEN}Downloading GitHub Actions Runner v${RUNNER_VERSION}...${NC}"
curl -o runner.tar.gz -L "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/${RUNNER_FILE}"

echo "Extracting runner..."
tar xzf runner.tar.gz
rm runner.tar.gz

echo -e "${YELLOW}To complete setup:${NC}"
echo "1. Go to: https://github.com/identity-wael/neurascale/settings/actions/runners/new"
echo "2. Get your runner token"
echo "3. Run the following command with your token:"
echo ""
echo "cd $RUNNER_DIR"
echo "./config.sh --url $REPO_URL --token YOUR_RUNNER_TOKEN --name neurascale-local --labels self-hosted,macOS,neural-engine --work _work"
echo ""
echo "4. Then start the runner:"
echo "./run.sh"
echo ""
echo "Or install as a service (macOS):"
echo "./svc.sh install"
echo "./svc.sh start"

# Create a convenience script
cat > $RUNNER_DIR/start-runner.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
./run.sh
EOF

chmod +x $RUNNER_DIR/start-runner.sh

echo -e "${GREEN}✅ Runner downloaded and ready for configuration!${NC}"
