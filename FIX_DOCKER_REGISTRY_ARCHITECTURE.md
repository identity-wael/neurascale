# Docker Registry Architecture Fix

## Current Problem

The `docker-build.yml` workflow is hardcoded to always push images to `development-neurascale`, even when deploying to production. This makes no sense and breaks the isolation between environments.

## Root Cause

- DevOps confusion between the `neurascale` project (555656387124) which hosts Workload Identity Federation and the actual environment projects
- Attempted to change PROJECT_ID to `neurascale` instead of implementing proper environment routing

## Proper Architecture

### Projects Structure

1. **neurascale (555656387124)** - Control plane project hosting:

   - Workload Identity Federation for GitHub Actions
   - Cross-project IAM permissions
   - NOT for storing Docker images

2. **Environment Projects**:
   - `development-neurascale` - Development environment and images
   - `staging-neurascale` - Staging environment and images
   - `production-neurascale` - Production environment and images

### How It Should Work

1. **Branch-based Routing**:

   ```
   main branch / v* tags → production-neurascale
   staging branch → staging-neurascale
   develop branch → development-neurascale
   ```

2. **Image Paths**:

   ```
   Dev:  northamerica-northeast1-docker.pkg.dev/development-neurascale/neural-engine-development/[service]
   Stg:  northamerica-northeast1-docker.pkg.dev/staging-neurascale/neural-engine-staging/[service]
   Prod: northamerica-northeast1-docker.pkg.dev/production-neurascale/neural-engine-production/[service]
   ```

3. **Authentication Flow**:
   - GitHub Actions authenticates via `neurascale` project's Workload Identity
   - Gets permissions to push to the appropriate environment project
   - Pushes images to the correct project's Artifact Registry

## Implementation

I've created `docker-build-fixed.yml` that:

- Dynamically determines environment based on branch/tag
- Sets PROJECT_ID accordingly
- Uses GitHub environments for additional security
- Maintains proper separation between environments

## Next Steps

1. **Enable Artifact Registry API** in staging and production projects:

   ```bash
   gcloud services enable artifactregistry.googleapis.com --project=staging-neurascale
   gcloud services enable artifactregistry.googleapis.com --project=production-neurascale
   ```

2. **Create repositories** in each project:

   ```bash
   # Staging
   gcloud artifacts repositories create neural-engine-staging \
     --repository-format=docker \
     --location=northamerica-northeast1 \
     --project=staging-neurascale

   # Production
   gcloud artifacts repositories create neural-engine-production \
     --repository-format=docker \
     --location=northamerica-northeast1 \
     --project=production-neurascale
   ```

3. **Verify IAM permissions** for the service account in each project:

   ```bash
   # The github-actions@neurascale.iam.gserviceaccount.com needs:
   # - Artifact Registry Writer
   # - Storage Object Viewer (for pulling base images)
   ```

4. **Update Terraform** to pull images from the correct project based on environment

5. **Test the new workflow** with the staging branch first

This architecture ensures proper isolation between environments and follows GCP best practices for multi-environment setups.
