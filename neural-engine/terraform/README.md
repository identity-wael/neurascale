# NeuraScale Terraform Configuration

This directory contains the Terraform configuration for managing NeuraScale's multi-environment infrastructure.

## Architecture

- **Orchestration Project**: `neurascale` - Main project that manages all environments
- **Environment Projects**:
  - `development-neurascale` - Development environment
  - `staging-neurascale` - Staging environment (PR deployments)
  - `production-neurascale` - Production environment

## State Management

We use **Google Cloud Storage (GCS)** for Terraform state management:

- **Bucket**: `neurascale-terraform-state` (in the orchestration project)
- **State Files**:
  - Development: `gs://neurascale-terraform-state/neural-engine/development/`
  - Staging: `gs://neurascale-terraform-state/neural-engine/staging/`
  - Production: `gs://neurascale-terraform-state/neural-engine/production/`

## Setup Instructions

### 1. Google Cloud Setup

```bash
# Authenticate with Google Cloud
gcloud auth login
gcloud auth application-default login

# Set default project
gcloud config set project neurascale

# Create state bucket (if not exists)
./setup-gcs-backend.sh
```

### 2. Local Terraform Setup

```bash
# Initialize Terraform with appropriate backend
cd neural-engine/terraform

# For staging environment
terraform init -backend-config=backend-staging.conf

# For production environment
terraform init -backend-config=backend-production.conf

# For development environment
terraform init -backend-config=backend-development.conf
```

### 3. Deploy Infrastructure

```bash
# Plan changes
terraform plan \
  -var="project_id=staging-neurascale" \
  -var="orchestration_project_id=neurascale" \
  -var="region=northamerica-northeast1"

# Apply changes
terraform apply \
  -var="project_id=staging-neurascale" \
  -var="orchestration_project_id=neurascale" \
  -var="region=northamerica-northeast1"
```

## CI/CD Setup

GitHub Actions automatically deploys:

- **Pull Requests** → Staging environment
- **Main branch** → Production environment
- **Develop branch** → Development environment

### Required GitHub Secrets

- `WIF_PROVIDER` - Workload Identity Provider for GCP
- `WIF_SERVICE_ACCOUNT` - Service account for CI/CD

## Module Structure

```
terraform/
├── main.tf                    # Main configuration
├── variables.tf               # Variable definitions
├── backend-*.conf             # Backend configurations per environment
├── modules/
│   ├── project-apis/          # API enablement module
│   └── neural-ingestion/      # Neural data ingestion infrastructure
└── setup-gcs-backend.sh       # Script to create GCS bucket
```

## Security Notes

1. State files are stored in GCS with versioning enabled
2. Access to state bucket is controlled via IAM
3. Each environment uses separate service accounts
4. No credentials are stored in code

## Troubleshooting

### State Lock Issues

If you encounter state lock errors:

```bash
# List locks in GCS
gsutil ls -r gs://neurascale-terraform-state/neural-engine/

# Remove stale lock (use with caution)
gsutil rm gs://neurascale-terraform-state/neural-engine/<environment>/default.tflock
```
