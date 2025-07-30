# Neural Engine Terraform Infrastructure

This directory contains the simplified Terraform configuration for deploying Neural Engine infrastructure across multiple environments.

## Quick Start

### Prerequisites

1. Google Cloud SDK installed and configured
2. Terraform >= 1.5.0 installed
3. Appropriate GCP permissions (or use GitHub Actions)

### Cross-Project API Requirements

When deploying from a service account in a different project (e.g., neurascale project 555656387124), the following APIs must be manually enabled in that source project:

- `servicenetworking.googleapis.com` - Required for VPC peering with Cloud SQL/Redis
- `cloudkms.googleapis.com` - Required for KMS encryption features

Until these APIs are enabled in the source project, the following features are disabled:

- Private service connection (Cloud SQL/Redis private IPs)
- KMS encryption
- Enhanced security features
- Scheduled scaling (Cloud Functions)

### Local Deployment

1. **Initialize Terraform** (replace `development` with your target environment):

   ```bash
   terraform init \
     -backend-config="bucket=neurascale-terraform-state" \
     -backend-config="prefix=neural-engine/development"
   ```

2. **Plan the deployment**:

   ```bash
   terraform plan \
     -var="project_id=development-neurascale" \
     -var="region=northamerica-northeast1"
   ```

3. **Apply the changes**:
   ```bash
   terraform apply \
     -var="project_id=development-neurascale" \
     -var="region=northamerica-northeast1"
   ```

### GitHub Actions Deployment

Push your changes to the appropriate branch:

- `develop` branch → deploys to development environment
- Pull request to `main` → deploys to staging environment
- `main` branch → deploys to production environment

Or trigger manually:

1. Go to Actions tab in GitHub
2. Select "Neural Engine Deploy - Simplified"
3. Click "Run workflow"
4. Choose your target environment

## Architecture Overview

### Resources Created

1. **Service Account**: `neural-ingestion-{env}` for running Cloud Functions
2. **Pub/Sub Topics**: One per signal type (eeg, ecog, lfp, spikes, emg, accelerometer)
3. **Pub/Sub Subscriptions**: With retry and dead-letter policies
4. **Bigtable Instance**: For storing time-series neural data
5. **Cloud Functions**: For processing each signal type
6. **Storage Bucket**: For Cloud Functions source code
7. **Artifact Registry**: For Docker images

### Module Structure

```
terraform/
├── main.tf                    # Root configuration
├── variables.tf              # Input variables
├── outputs.tf               # Output values
├── README.md                # This file
├── SIMPLIFIED_ARCHITECTURE.md # Detailed architecture docs
└── modules/
    └── neural-ingestion/    # All ingestion infrastructure
        ├── main.tf          # Module resources
        ├── variables.tf     # Module inputs
        └── outputs.tf       # Module outputs
```

## Environment Configuration

| Environment | Project ID             | Short Name | Usage                   |
| ----------- | ---------------------- | ---------- | ----------------------- |
| development | development-neurascale | dev        | Development and testing |
| staging     | staging-neurascale     | stg        | Pre-production testing  |
| production  | production-neurascale  | prod       | Production workloads    |

## Key Features

1. **Simplified IAM**: Single service account with minimal permissions
2. **Integrated Deployment**: Infrastructure and functions deployed together
3. **Proper Dependencies**: Explicit resource ordering prevents race conditions
4. **GCS State Backend**: Reliable state management without Terraform Cloud
5. **Environment Isolation**: Complete separation between environments

## Monitoring and Debugging

### View Deployed Resources

```bash
# List all resources
terraform state list

# Show specific resource details
terraform state show google_service_account.neural_ingestion

# Get outputs
terraform output
```

### Check Cloud Functions

```bash
# List functions
gcloud functions list --gen2 --region=northamerica-northeast1

# View function logs
gcloud functions logs read process-neural-eeg-dev \
  --gen2 \
  --region=northamerica-northeast1
```

### Monitor Pub/Sub

```bash
# List topics
gcloud pubsub topics list

# View subscriptions
gcloud pubsub subscriptions list

# Check dead letter messages
gcloud pubsub subscriptions pull neural-data-dead-letter-development-sub --auto-ack
```

## Troubleshooting

### Common Issues

1. **"API not enabled" errors**

   - The configuration automatically enables APIs
   - Wait ~30 seconds after initialization

2. **"Permission denied" errors**

   - Ensure you're authenticated: `gcloud auth application-default login`
   - Check service account permissions

3. **State lock errors**

   - Someone else might be running Terraform
   - Use `terraform force-unlock <lock-id>` if needed

4. **Function deployment failures**
   - Check the functions bucket exists
   - Verify the zip file was uploaded correctly

### Clean Up

To destroy all resources in an environment:

```bash
terraform destroy \
  -var="project_id=development-neurascale" \
  -var="region=northamerica-northeast1"
```

⚠️ **Warning**: This will delete all resources including data in Bigtable!

## Next Steps

1. Review [SIMPLIFIED_ARCHITECTURE.md](./SIMPLIFIED_ARCHITECTURE.md) for detailed documentation
2. Check function code in `neural-engine/functions/`
3. Monitor deployments in GitHub Actions
4. Set up alerts in Google Cloud Monitoring

## Support

For issues or questions:

1. Check the [troubleshooting guide](#troubleshooting)
2. Review GitHub Actions logs
3. Check Google Cloud logs
4. Open an issue in the repository
