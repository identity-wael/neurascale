#!/bin/bash
# Script to run Black using Homebrew Python 3.12.11 in a virtual environment

set -e

# Use Homebrew Python 3.12
PYTHON="/opt/homebrew/bin/python3.12"
VENV_DIR=".pre-commit-venv"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    $PYTHON -m venv $VENV_DIR
fi

# Activate virtual environment
source $VENV_DIR/bin/activate

# Install black if not installed
pip install black==24.10.0 >/dev/null 2>&1 || true

# Run black on the files passed as arguments
black "$@"
