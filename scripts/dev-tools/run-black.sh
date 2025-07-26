#!/bin/bash
# Script to run Black using Homebrew Python 3.12.11 in a virtual environment

set -e

# Use Homebrew Python 3.12
PYTHON="/opt/homebrew/bin/python3.12"
# Use neural-engine venv
VENV_DIR="neural-engine/venv"

# Verify Python version
PYTHON_VERSION=$($PYTHON --version 2>&1 | cut -d' ' -f2)
if [[ ! "$PYTHON_VERSION" =~ ^3\.12\.11 ]]; then
    echo "Error: Python version $PYTHON_VERSION found, but 3.12.11 is required"
    echo "Please ensure Homebrew Python 3.12.11 is installed"
    exit 1
fi

# Create virtual environment if it doesn't exist or has wrong Python version
if [ ! -d "$VENV_DIR" ] || [ ! -f "$VENV_DIR/bin/python" ]; then
    echo "Creating venv with Python $PYTHON_VERSION..."
    $PYTHON -m venv $VENV_DIR
elif [ -f "$VENV_DIR/bin/python" ]; then
    VENV_PYTHON_VERSION=$("$VENV_DIR/bin/python" --version 2>&1 | cut -d' ' -f2)
    if [[ ! "$VENV_PYTHON_VERSION" =~ ^3\.12\.11 ]]; then
        echo "Venv has Python $VENV_PYTHON_VERSION, recreating with Python $PYTHON_VERSION..."
        rm -rf $VENV_DIR
        $PYTHON -m venv $VENV_DIR
    fi
fi

# Activate virtual environment
source $VENV_DIR/bin/activate

# Install black if not installed
pip install black==24.10.0 >/dev/null 2>&1 || true

# Run black on the files passed as arguments
black "$@"
