# NeuraScale Scripts

This directory contains all scripts for the NeuraScale project, organized by functionality.

## Directory Structure

### `/runners`

GitHub Actions self-hosted runner management scripts:

- `auto-setup-runners.sh` - Automated setup for multiple runners
- `clone-runner.sh` - Clone runner configuration
- `monitor-pipeline.sh` - Monitor CI/CD pipeline status
- `quick-runner-config.sh` - Quick runner configuration
- `quick-runner-setup.sh` - Quick runner setup
- `restart-runner-max-performance.sh` - Restart runners with max performance
- `setup-multi-runners.sh` - Set up multiple runners
- `start-configured-runners.sh` - Start all configured runners

### `/infrastructure`

Infrastructure and deployment scripts:

- `setup-permissions.sh` - Set up GCP IAM permissions
- `optimize-docker-builds.sh` - Docker build optimization
- `fix-production-permissions.sh` - Fix production IAM permissions
- `grant-production-permissions.sh` - Grant production permissions

### `/neural-engine`

Neural Engine specific scripts:

- `configure-gcp.sh` - Configure GCP for Neural Engine
- `prepare-runner-cache.sh` - Prepare runner cache
- `runner-control.sh` - Control runner instances
- `setup-github-runner.sh` - Set up GitHub runner for Neural Engine
- `setup.sh` - Main setup script

### `/dev-tools`

Development and tooling scripts:

- `run-black.sh` - Python code formatter (pre-commit hook)

## Usage

Most scripts should be run from the project root:

```bash
# Example: Start all runners
./scripts/runners/start-configured-runners.sh

# Example: Monitor pipeline
./scripts/runners/monitor-pipeline.sh
```

## Script Conventions

1. All scripts use bash (`#!/bin/bash`)
2. Scripts include error handling and validation
3. Configuration is done via environment variables
4. Scripts provide clear output and status messages
5. Dangerous operations require confirmation

## Security Notes

- Never commit credentials or tokens
- Scripts requiring elevated permissions are clearly marked
- IAM scripts follow principle of least privilege
- All scripts validate inputs before execution
