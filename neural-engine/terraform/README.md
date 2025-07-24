# NeuraScale Terraform Configuration

This directory contains the Terraform configuration for managing NeuraScale's multi-environment infrastructure.

## Architecture

- **Orchestration Project**: `neurascale` - Main project that manages all environments
- **Environment Projects**:
  - `development-neurascale` - Development environment
  - `staging-neurascale` - Staging environment (PR deployments)
  - `production-neurascale` - Production environment

## State Management

We use **Terraform Cloud** for state management with **GCS backup**:

1. **Primary**: Terraform Cloud (app.terraform.io)

   - Organization: `neurascale`
   - Workspaces: `neural-engine-development`, `neural-engine-staging`, `neural-engine-production`

2. **Backup**: Google Cloud Storage
   - Bucket: `neurascale-terraform-state`
   - Automated sync via `scripts/sync-terraform-state.sh`

## Setup Instructions

### 1. Terraform Cloud Setup

1. Create account at https://app.terraform.io
2. Create organization named `neurascale`
3. Generate API token: https://app.terraform.io/app/settings/tokens
4. Create three workspaces with tag `neural-engine`:
   - `neural-engine-development`
   - `neural-engine-staging`
   - `neural-engine-production`

### 2. Configure Workspaces

For each workspace in Terraform Cloud:

1. Go to workspace settings → Variables
2. Add environment variables:
   ```
   GOOGLE_CREDENTIALS = <service-account-json>
   TF_VAR_environment = development|staging|production
   ```

### 3. Local Setup

```bash
# Login to Terraform Cloud
terraform login

# Initialize Terraform
cd neural-engine/terraform
./setup-terraform-cloud.sh

# Select workspace and plan
export TF_WORKSPACE=neural-engine-development
terraform plan
```

### 4. CI/CD Setup

Add these secrets to GitHub:

- `TF_CLOUD_TOKEN` - Terraform Cloud API token
- `WIF_PROVIDER` - Workload Identity Provider for GCP
- `WIF_SERVICE_ACCOUNT` - Service account for CI/CD

## Usage

### Deploy to Development

```bash
export TF_WORKSPACE=neural-engine-development
terraform plan
terraform apply
```

### Deploy to Staging (via PR)

- Create PR to main branch
- CI/CD automatically deploys to staging

### Deploy to Production

- Merge PR to main branch
- CI/CD automatically deploys to production

## Backup and Recovery

### Automated Backup

Set up a Cloud Scheduler job to run:

```bash
export TF_CLOUD_TOKEN=<your-token>
./scripts/sync-terraform-state.sh
```

### Manual Recovery

```bash
# Download state from GCS
gsutil cp gs://neurascale-terraform-state/backup/production/terraform.tfstate ./

# Import to Terraform Cloud (emergency only)
terraform state push terraform.tfstate
```

## Module Structure

```
terraform/
├── main.tf                    # Main configuration
├── variables.tf              # Variable definitions
├── backend-gcs-backup.tf     # GCS backup configuration
├── modules/
│   ├── project-apis/         # API enablement module
│   └── neural-ingestion/     # Neural data ingestion infrastructure
└── environments/             # Environment-specific tfvars (optional)
```

## Security Notes

1. Service account keys are stored in Terraform Cloud, not in code
2. State files contain sensitive data - handle with care
3. GCS backup bucket has versioning enabled
4. All projects use separate service accounts per environment
