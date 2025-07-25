# Cross-Project IAM Setup

This directory contains Terraform configuration to grant the GitHub Actions service account permissions across all environment projects.

## Purpose

The GitHub Actions service account (`github-actions@neurascale.iam.gserviceaccount.com`) needs permissions in each target project:

- `staging-neurascale`
- `production-neurascale`
- `development-neurascale`

## Usage

1. Ensure you have appropriate permissions (Project IAM Admin) in all target projects
2. Authenticate with Google Cloud:

   ```bash
   gcloud auth application-default login
   ```

3. Initialize and apply Terraform:
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

## Permissions Granted

The configuration grants the following roles:

- `roles/editor` - Broad permissions for infrastructure deployment
- `roles/iam.serviceAccountAdmin` - To create/manage service accounts
- `roles/iam.roleAdmin` - To create/manage custom roles
- `roles/resourcemanager.projectIamAdmin` - To set IAM policies
- `roles/billing.costsManager` - To create budgets
- `roles/monitoring.admin` - To create monitoring resources
- `roles/logging.admin` - To create log metrics

## Security Note

This grants broad permissions to enable full infrastructure deployment. In production, consider:

1. Using more restrictive custom roles
2. Implementing time-based access controls
3. Regular permission audits
