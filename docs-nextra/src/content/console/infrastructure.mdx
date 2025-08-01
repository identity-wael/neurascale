# NeuraScale Console Infrastructure

This directory contains Terraform configuration for the NeuraScale Console infrastructure on Google Cloud Platform.

## Prerequisites

1. **Google Cloud SDK**: Install and configure the gcloud CLI
2. **Terraform**: Install Terraform >= 1.0
3. **GCP Project**: Create a GCP project with billing enabled

## Required APIs

Enable the following APIs in your GCP project:

```bash
gcloud services enable sqladmin.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable iam.googleapis.com
```

## Setup

1. **Copy the variables file**:

   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

2. **Edit terraform.tfvars** with your project details:

   ```hcl
   project_id  = "your-gcp-project-id"
   region      = "us-central1"
   db_tier     = "db-f1-micro"
   db_username = "neurascale_user"
   environment = "dev"
   ```

3. **Initialize Terraform**:

   ```bash
   terraform init
   ```

4. **Plan the deployment**:

   ```bash
   terraform plan
   ```

5. **Apply the configuration**:
   ```bash
   terraform apply
   ```

## Resources Created

- **Cloud SQL PostgreSQL Instance**: Database for the console application
- **Cloud SQL Database**: `neurascale_console` database
- **Cloud SQL User**: Application database user
- **Service Account**: For application authentication
- **Secret Manager**: For storing sensitive data (DB password, service account key)
- **IAM Bindings**: Appropriate permissions for the service account

## Outputs

After deployment, Terraform will output:

- Database connection details
- Service account information
- Database URL (sensitive)

## Environment Variables

Add these to your `.env.local` file in the console application:

```bash
DATABASE_URL="postgresql://username:password@host:5432/neurascale_console"
GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
```

## Security Notes

- The database is configured with SSL required
- Backup is enabled with 7-day retention
- Query insights are enabled for monitoring
- All sensitive data is stored in Secret Manager

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

**Warning**: This will permanently delete all data in the database.
