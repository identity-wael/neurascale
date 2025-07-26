#!/bin/bash
# Script to install GPG on all self-hosted runners to fix Codecov warnings

set -e

echo "=== Installing GPG on Self-Hosted Runners ==="
echo ""

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: This script is designed for macOS runners"
    exit 1
fi

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Error: Homebrew is not installed. Please install Homebrew first."
    echo "Visit: https://brew.sh"
    exit 1
fi

# Install GPG if not already installed
echo "Checking for GPG installation..."
if command -v gpg &> /dev/null; then
    GPG_VERSION=$(gpg --version | head -n 1)
    echo "GPG is already installed: $GPG_VERSION"
    echo ""
    echo "Updating GPG to latest version..."
    brew upgrade gnupg || true
else
    echo "GPG is not installed. Installing via Homebrew..."
    brew install gnupg
fi

# Verify installation
echo ""
echo "Verifying GPG installation..."
if command -v gpg &> /dev/null; then
    GPG_VERSION=$(gpg --version | head -n 1)
    echo "✓ GPG installed successfully: $GPG_VERSION"
    echo "✓ GPG location: $(which gpg)"
else
    echo "✗ GPG installation failed"
    exit 1
fi

# Create GPG directory if it doesn't exist
echo ""
echo "Setting up GPG directories..."
mkdir -p ~/.gnupg
chmod 700 ~/.gnupg

# Configure GPG for automated use (disable interactive prompts)
echo ""
echo "Configuring GPG for CI/CD use..."
cat > ~/.gnupg/gpg.conf << 'EOF'
# Suppress the initial copyright message
no-greeting

# Disable inclusion of the version string in ASCII armored output
no-emit-version

# Disable comment string in clear text signatures and ASCII armored messages
no-comments

# Long key IDs are more collision-resistant
keyid-format 0xlong

# Display the calculated validity of user IDs during key listings
list-options show-uid-validity
verify-options show-uid-validity

# Try to use the GnuPG-Agent
use-agent

# Disable expensive trust model checks
trust-model always
EOF

# Set proper permissions
chmod 600 ~/.gnupg/gpg.conf

# Add GPG to PATH in runner environment
echo ""
echo "Adding GPG to runner environment..."
RUNNER_ENV_FILE="$HOME/.github_runner_env"
if [ -f "$RUNNER_ENV_FILE" ]; then
    # Check if GPG_PATH is already set
    if ! grep -q "GPG_PATH" "$RUNNER_ENV_FILE"; then
        echo "export GPG_PATH=$(which gpg)" >> "$RUNNER_ENV_FILE"
        echo "✓ Added GPG_PATH to runner environment"
    else
        echo "✓ GPG_PATH already set in runner environment"
    fi
else
    # Create the file if it doesn't exist
    echo "export GPG_PATH=$(which gpg)" > "$RUNNER_ENV_FILE"
    echo "✓ Created runner environment file with GPG_PATH"
fi

echo ""
echo "=== GPG Installation Complete ==="
echo ""
echo "GPG has been installed and configured for CI/CD use."
echo "The Codecov warnings about GPG signature verification should now be resolved."
echo ""
echo "Note: You may need to restart your GitHub Actions runners for changes to take effect."
echo ""
echo "To restart runners, run: ./scripts/runners/restart-runner-max-performance.sh"
