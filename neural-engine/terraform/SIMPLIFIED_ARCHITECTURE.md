# Neural Engine Simplified Terraform Architecture

This document describes the simplified Terraform architecture for the Neural Engine infrastructure.

## Overview

The new architecture addresses the following issues from the previous implementation:

- Complex permission chains and race conditions
- Terraform Cloud workspace management issues
- Separation between infrastructure and function deployment
- Unclear dependencies and resource ordering
- Overly complex IAM permission structure

## Key Improvements

### 1. Single Service Account Strategy

- One main service account (`neural-ingestion-{env}`) for all ingestion operations
- Clear IAM role assignments at the root level
- GitHub Actions service account has explicit permissions

### 2. GCS Backend Instead of Terraform Cloud

- Uses GCS backend for state management
- State is stored in `neurascale-terraform-state` bucket
- Environment-specific state prefixes: `neural-engine/{environment}`

### 3. Integrated Deployment

- Infrastructure and Cloud Functions are deployed together using Terraform
- Cloud Functions are defined as Terraform resources (using `google_cloudfunctions2_function`)
- Proper dependency chains ensure resources are created in the correct order

### 4. Simplified Module Structure

```
terraform/
├── main.tf                    # Root configuration
├── variables.tf              # Input variables
├── outputs.tf               # Output values
└── modules/
    └── neural-ingestion/    # Single module for all ingestion resources
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

### 5. Clear Resource Dependencies

1. Enable APIs first
2. Wait for APIs to be active (30s delay)
3. Create service account
4. Assign IAM roles
5. Create infrastructure (Pub/Sub, Bigtable, Storage)
6. Deploy Cloud Functions

## Environment Strategy

Environments are determined by the project ID pattern:

- `development-neurascale` → development environment
- `staging-neurascale` → staging environment
- `production-neurascale` → production environment

## IAM Permission Strategy

### Service Accounts

1. **Neural Ingestion Service Account** (`neural-ingestion-{env}@{project}.iam.gserviceaccount.com`)

   - Runs Cloud Functions
   - Has minimal required permissions:
     - `roles/pubsub.publisher` - Publish messages
     - `roles/pubsub.subscriber` - Subscribe to topics
     - `roles/bigtable.user` - Read/write Bigtable
     - `roles/storage.objectViewer` - Read from storage
     - `roles/monitoring.metricWriter` - Write metrics
     - `roles/logging.logWriter` - Write logs
     - `roles/cloudtrace.agent` - Write traces

2. **GitHub Actions Service Account** (`github-actions@neurascale.iam.gserviceaccount.com`)
   - Deploys infrastructure and functions
   - Has admin permissions for deployment:
     - `roles/cloudfunctions.admin` - Deploy functions
     - `roles/iam.serviceAccountUser` - Act as service accounts
     - `roles/storage.admin` - Manage storage buckets
     - `roles/pubsub.admin` - Manage Pub/Sub resources
     - `roles/bigtable.admin` - Manage Bigtable
     - `roles/artifactregistry.admin` - Manage artifact registry
     - `roles/resourcemanager.projectIamAdmin` - Manage IAM
     - `roles/serviceusage.serviceUsageAdmin` - Enable APIs

## Deployment Process

### Local Development

1. Set up authentication:

```bash
gcloud auth application-default login
```

2. Initialize Terraform:

```bash
cd neural-engine/terraform
terraform init \
  -backend-config="bucket=neurascale-terraform-state" \
  -backend-config="prefix=neural-engine/development"
```

3. Plan deployment:

```bash
terraform plan \
  -var="project_id=development-neurascale" \
  -var="region=northamerica-northeast1"
```

4. Apply changes:

```bash
terraform apply \
  -var="project_id=development-neurascale" \
  -var="region=northamerica-northeast1"
```

### GitHub Actions Deployment

The simplified workflow (`neural-engine-deploy-simplified.yml`) handles:

1. **Environment Detection**:

   - Pull requests → staging
   - Main branch → production
   - Develop branch → development
   - Manual trigger → selected environment

2. **Build Process**:

   - Runs tests
   - Packages Cloud Functions into zip file
   - Uploads to GCS bucket

3. **Deploy Process**:

   - Initializes Terraform with environment-specific state
   - Plans infrastructure changes
   - Applies changes (creates all resources)
   - Cloud Functions are deployed via Terraform

4. **Verification**:
   - Checks that all functions are deployed
   - Tests Pub/Sub publishing
   - Provides deployment summary

## State Management

### Backend Configuration

```hcl
backend "gcs" {
  bucket = "neurascale-terraform-state"
  prefix = "neural-engine/{environment}"
}
```

### State Files

- Development: `gs://neurascale-terraform-state/neural-engine/development/default.tfstate`
- Staging: `gs://neurascale-terraform-state/neural-engine/staging/default.tfstate`
- Production: `gs://neurascale-terraform-state/neural-engine/production/default.tfstate`

## Resource Naming Conventions

- Service Account: `neural-ingestion-{env_short}`
- Pub/Sub Topics: `neural-data-{signal_type}-{environment}`
- Bigtable Instance: `neural-data-{env_short}`
- Cloud Functions: `process-neural-{signal_type}-{env_short}`
- Storage Bucket: `{project_id}-gcf-source`
- Artifact Registry: `neural-engine`

Where:

- `{env_short}` = dev, stg, or prod
- `{signal_type}` = eeg, ecog, lfp, spikes, emg, or accelerometer
- `{environment}` = development, staging, or production

## Troubleshooting

### Common Issues

1. **API not enabled errors**:

   - The configuration automatically enables required APIs
   - Wait 30 seconds after API enablement before creating resources

2. **Permission denied errors**:

   - Ensure GitHub Actions service account has all required roles
   - Check that the ingestion service account has necessary permissions

3. **State lock errors**:

   - Only one Terraform operation can run at a time
   - Use `terraform force-unlock` if needed (with caution)

4. **Function deployment failures**:
   - Ensure the functions zip file is uploaded to GCS
   - Check that the bucket exists and has proper permissions

### Debugging Commands

```bash
# Check current state
terraform state list

# Show specific resource
terraform state show module.neural_ingestion.google_cloudfunctions2_function.process_neural_stream["eeg"]

# Import existing resources
terraform import google_service_account.neural_ingestion neural-ingestion-dev@development-neurascale.iam.gserviceaccount.com

# Refresh state
terraform refresh -var="project_id=development-neurascale"
```

## Migration from Old Architecture

1. **Backup existing state** (if using Terraform Cloud)
2. **Remove old resources** that won't be managed by new architecture
3. **Import existing resources** that should be preserved
4. **Run terraform plan** to see what will change
5. **Apply changes** carefully, reviewing the plan

## Best Practices

1. **Always run `terraform plan`** before applying changes
2. **Use consistent variable values** across deployments
3. **Don't modify resources outside of Terraform**
4. **Keep functions package up to date** in GCS
5. **Monitor deployment logs** in GitHub Actions
6. **Use environment-specific branches** for testing
