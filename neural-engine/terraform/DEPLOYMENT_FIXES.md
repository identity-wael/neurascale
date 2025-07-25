# Deployment Fixes and Setup Guide

## Overview

This document describes the fixes applied to resolve GitHub deployment failures and the setup process for the NeuraScale Neural Engine infrastructure.

## Issues Fixed

### 1. Security - Removed Owner Role from GitHub Actions

- **Issue**: GitHub Actions service account had `roles/owner` permissions
- **Fix**: Created custom IAM role with minimal required permissions
- **File**: `main.tf` - Added `google_project_iam_custom_role.github_deploy`

### 2. Terraform State Management

- **Issue**: State bucket being managed by Terraform (chicken-and-egg problem)
- **Fix**: Created bootstrap script and changed to data source reference
- **Files**:
  - `bootstrap-state-bucket.sh` - Creates state bucket manually
  - `state.tf` - Changed from resource to data source

### 3. CI/CD Pipeline Issues

- **Issue**: Linting and type checking were disabled
- **Fix**: Created proper configuration files and re-enabled checks
- **Files**:
  - `.flake8` - Python linting configuration
  - `mypy.ini` - Python type checking configuration
  - `.github/workflows/neural-engine-deploy-simplified.yml` - Re-enabled checks

### 4. Docker Build Issues

- **Issue**: Docker builds were skipped with `if: false`
- **Fix**: Changed to `if: success()` and added Artifact Registry check
- **Added**: Docker layer caching for faster builds

### 5. Monitoring Configuration

- **Issue**: Missing `combiner` field in alert policies
- **Fix**: Added `combiner = "OR"` to all alert policies
- **File**: `monitoring.tf`

### 6. Environment Configuration

- **Issue**: Variables hardcoded in CI/CD pipeline
- **Fix**: Created environment-specific tfvars files
- **Files**: `environments/*.tfvars`

## Setup Instructions

### 1. Bootstrap State Bucket (One-time setup)

Before using Terraform, create the state bucket:

```bash
cd neural-engine/terraform
./bootstrap-state-bucket.sh <PROJECT_ID>
# Example: ./bootstrap-state-bucket.sh production-neurascale
```

### 2. Initialize Terraform

```bash
terraform init \
  -backend-config="bucket=neurascale-terraform-state" \
  -backend-config="prefix=neural-engine/${ENVIRONMENT}"
```

### 3. Deploy Infrastructure

The GitHub Actions workflow will automatically:

1. Run linting and type checking
2. Build and push Docker images (if Artifact Registry exists)
3. Package Cloud Functions
4. Deploy infrastructure using environment-specific variables
5. Log deployment events for monitoring

### 4. Manual Deployment

For manual deployment:

```bash
# Plan
terraform plan -var-file=environments/${ENVIRONMENT}.tfvars

# Apply
terraform apply -var-file=environments/${ENVIRONMENT}.tfvars
```

## Environment Variables

Each environment has its own tfvars file with:

- Resource sizing (Bigtable nodes, storage)
- Security settings (deletion protection, VPC controls)
- Monitoring configuration
- Cost optimization settings

## Monitoring

The deployment now includes:

- Comprehensive dashboards for all services
- Alert policies for high CPU, errors, and backlogs
- Deployment event tracking
- Email notifications for alerts

## Security Improvements

1. **Least Privilege**: GitHub Actions uses custom role instead of owner
2. **State Security**: State bucket has versioning and access controls
3. **Environment Isolation**: Separate configurations per environment
4. **Audit Logging**: All deployments are tracked in Cloud Logging

## Next Steps

1. Run `bootstrap-state-bucket.sh` for each project
2. Update notification channels in tfvars files
3. Test deployment in staging environment
4. Monitor for any remaining issues
