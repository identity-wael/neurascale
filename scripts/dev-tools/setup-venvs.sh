#!/bin/bash
# Script to set up and maintain consistent Python 3.12.11 virtual environments

set -e

# Use Homebrew Python 3.12.11
PYTHON="/opt/homebrew/bin/python3.12"

# Verify Python version
PYTHON_VERSION=$($PYTHON --version 2>&1 | cut -d' ' -f2)
if [[ ! "$PYTHON_VERSION" =~ ^3\.12\.11 ]]; then
    echo "Error: Python version $PYTHON_VERSION found, but 3.12.11 is required"
    echo "Please ensure Homebrew Python 3.12.11 is installed: brew install python@3.12"
    exit 1
fi

echo "Using Python $PYTHON_VERSION"

# Function to create or recreate a venv
create_venv() {
    local venv_path=$1
    local requirements_file=$2

    echo "Setting up venv at: $venv_path"

    # Remove existing venv if it exists
    if [ -d "$venv_path" ]; then
        echo "Removing existing venv..."
        rm -rf "$venv_path"
    fi

    # Create new venv
    $PYTHON -m venv "$venv_path"

    # Activate and install requirements if provided
    if [ -n "$requirements_file" ] && [ -f "$requirements_file" ]; then
        echo "Installing requirements from: $requirements_file"
        source "$venv_path/bin/activate"
        pip install --upgrade pip
        pip install -r "$requirements_file"
        deactivate
    fi

    # Verify Python version in venv
    local venv_python_version=$("$venv_path/bin/python" --version 2>&1 | cut -d' ' -f2)
    echo "Venv Python version: $venv_python_version"
    echo ""
}

# Main venvs to set up
echo "=== Setting up virtual environments ==="

# Main project venv
if [ -f "requirements.txt" ]; then
    create_venv "venv" "requirements.txt"
fi

# Neural Engine venv
if [ -f "neural-engine/requirements.txt" ]; then
    create_venv "neural-engine/venv" "neural-engine/requirements.txt"
fi

# Check for other venvs that might need attention
echo "=== Checking for other venvs ==="
find . -name "venv" -type d -o -name ".venv" -type d | grep -v node_modules | while read -r venv_dir; do
    if [ -f "$venv_dir/bin/python" ]; then
        version=$("$venv_dir/bin/python" --version 2>&1 | cut -d' ' -f2 || echo "Unknown")
        echo "$venv_dir: Python $version"
    fi
done

echo ""
echo "=== Setup complete ==="
echo "All venvs should now be using Python 3.12.11"
echo ""
echo "To activate a venv, use:"
echo "  source venv/bin/activate          # Main project"
echo "  source neural-engine/venv/bin/activate  # Neural Engine"
