# Terraform Backend Configurations

This directory contains backend configurations for different environments.

## Usage

To initialize Terraform for a specific environment:

```bash
# Development
terraform init -backend-config=backend-configs/development.hcl

# Staging
terraform init -backend-config=backend-configs/staging.hcl

# Production
terraform init -backend-config=backend-configs/production.hcl
```

## State Locking

The GCS backend automatically provides state locking using Cloud Storage's built-in object versioning and atomic operations. No additional configuration is required.

## State Recovery

To recover from a corrupted state:

1. List available state versions:

   ```bash
   gsutil ls -la gs://neurascale-terraform-state/neural-engine/<environment>/
   ```

2. Download a previous version:

   ```bash
   gsutil cp gs://neurascale-terraform-state/neural-engine/<environment>/default.tfstate#<version> recovered.tfstate
   ```

3. Push the recovered state:
   ```bash
   terraform state push recovered.tfstate
   ```

## Best Practices

1. Always run `terraform plan` before `terraform apply`
2. Use `-lock=false` only in emergency situations
3. Keep backups of state before major changes
4. Use workspaces for feature branches, not environments
