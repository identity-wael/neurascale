# Google Cloud Platform Setup for Neural Engine

This document describes how to set up Google Cloud authentication for the Neural Engine CI/CD pipeline.

## Prerequisites

- Google Cloud SDK installed (`gcloud` command)
- Access to the `neurascale` GCP project
- Permissions to create service accounts and grant IAM roles

## Setup Instructions

### 1. Authenticate with Google Cloud

First, authenticate with your Google account:

```bash
gcloud auth login
```

### 2. Run the Setup Script

We've provided a script that automates the setup process:

```bash
cd neural-engine
./scripts/setup-gcp-auth.sh
```

This script will:

- Create a service account named `neural-engine-ci`
- Grant necessary IAM roles for:
  - Container Registry (for Docker images)
  - Cloud Run (for API deployment)
  - Cloud Functions (for data ingestion)
  - Pub/Sub (for real-time data streaming)
  - Secret Manager (for secure credential storage)
- Enable required Google Cloud APIs
- Generate a service account key

### 3. Add the Service Account Key to GitHub

After running the script:

1. The script will create a file named `neural-engine-ci-key.json`
2. Copy the entire contents of this file
3. Go to the repository settings: https://github.com/identity-wael/neurascale/settings/secrets/actions
4. Click "New repository secret"
5. Name: `GCP_SA_KEY`
6. Value: Paste the contents of the JSON key file
7. Click "Add secret"

### 4. Clean Up

After adding the key to GitHub, delete the local key file for security:

```bash
rm neural-engine-ci-key.json
```

## Manual Setup (Alternative)

If you prefer to set up manually or need to customize the permissions:

### Create Service Account

```bash
gcloud iam service-accounts create neural-engine-ci \
    --display-name="Neural Engine CI/CD Service Account" \
    --project=neurascale
```

### Grant IAM Roles

```bash
# Container Registry
gcloud projects add-iam-policy-binding neurascale \
    --member="serviceAccount:neural-engine-ci@neurascale.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# Cloud Run
gcloud projects add-iam-policy-binding neurascale \
    --member="serviceAccount:neural-engine-ci@neurascale.iam.gserviceaccount.com" \
    --role="roles/run.admin"

# Cloud Functions
gcloud projects add-iam-policy-binding neurascale \
    --member="serviceAccount:neural-engine-ci@neurascale.iam.gserviceaccount.com" \
    --role="roles/cloudfunctions.admin"

# Service Account User
gcloud projects add-iam-policy-binding neurascale \
    --member="serviceAccount:neural-engine-ci@neurascale.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

# Pub/Sub
gcloud projects add-iam-policy-binding neurascale \
    --member="serviceAccount:neural-engine-ci@neurascale.iam.gserviceaccount.com" \
    --role="roles/pubsub.admin"

# Cloud Build
gcloud projects add-iam-policy-binding neurascale \
    --member="serviceAccount:neural-engine-ci@neurascale.iam.gserviceaccount.com" \
    --role="roles/cloudbuild.builds.editor"
```

### Enable APIs

```bash
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    cloudfunctions.googleapis.com \
    containerregistry.googleapis.com \
    pubsub.googleapis.com \
    secretmanager.googleapis.com \
    artifactregistry.googleapis.com \
    --project=neurascale
```

### Create Service Account Key

```bash
gcloud iam service-accounts keys create neural-engine-ci-key.json \
    --iam-account=neural-engine-ci@neurascale.iam.gserviceaccount.com \
    --project=neurascale
```

## Using Google Secret Manager (Recommended)

For enhanced security, we recommend using Google Secret Manager instead of storing secrets in GitHub:

### 1. Create the secret in Secret Manager

```bash
gcloud secrets create neural-engine-ci-key \
    --data-file=neural-engine-ci-key.json \
    --project=neurascale
```

### 2. Grant access to the secret

```bash
gcloud secrets add-iam-policy-binding neural-engine-ci-key \
    --member="serviceAccount:neural-engine-ci@neurascale.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --project=neurascale
```

### 3. Update the workflow to use Workload Identity Federation

This approach eliminates the need to store long-lived credentials in GitHub. See the [Workload Identity Federation documentation](https://cloud.google.com/iam/docs/workload-identity-federation) for more details.

## Troubleshooting

### Authentication Issues

If you encounter authentication errors:

1. Ensure you're logged in: `gcloud auth list`
2. Set the correct project: `gcloud config set project neurascale`
3. Refresh authentication: `gcloud auth application-default login`

### Permission Denied Errors

If you get permission errors when creating resources:

1. Check your current roles: `gcloud projects get-iam-policy neurascale --flatten="bindings[].members" --format='table(bindings.role)' --filter="bindings.members:YOUR_EMAIL"`
2. Ensure you have `roles/iam.serviceAccountAdmin` and `roles/resourcemanager.projectIamAdmin`

### API Not Enabled Errors

If you get errors about APIs not being enabled:

```bash
# Enable the specific API
gcloud services enable SERVICE_NAME.googleapis.com --project=neurascale
```

## Security Best Practices

1. **Rotate Keys Regularly**: Service account keys should be rotated periodically
2. **Use Least Privilege**: Only grant the minimum necessary permissions
3. **Monitor Usage**: Regularly audit service account activity in Cloud Logging
4. **Prefer Workload Identity**: When possible, use Workload Identity Federation instead of service account keys
5. **Secure Storage**: Never commit service account keys to version control
