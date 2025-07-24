#!/bin/bash
set -euo pipefail

# Script to set up Google Cloud authentication for Neural Engine CI/CD

PROJECT_ID="neurascale"
SERVICE_ACCOUNT_NAME="neural-engine-ci"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
KEY_FILE="neural-engine-ci-key.json"

echo "Setting up Google Cloud authentication for Neural Engine CI/CD..."
echo "Project ID: $PROJECT_ID"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "Error: gcloud CLI is not installed. Please install it first."
    exit 1
fi

# Set the project
echo "Setting active project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# Create service account if it doesn't exist
if ! gcloud iam service-accounts describe $SERVICE_ACCOUNT_EMAIL &> /dev/null; then
    echo "Creating service account $SERVICE_ACCOUNT_NAME..."
    gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
        --display-name="Neural Engine CI/CD Service Account" \
        --description="Service account for Neural Engine CI/CD pipeline"
else
    echo "Service account $SERVICE_ACCOUNT_NAME already exists."
fi

# Grant necessary roles
echo "Granting necessary roles to service account..."

# Container Registry permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/storage.admin" \
    --condition=None

# Cloud Run permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/run.admin" \
    --condition=None

# Cloud Functions permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/cloudfunctions.admin" \
    --condition=None

# Service account permissions (to act as service account)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/iam.serviceAccountUser" \
    --condition=None

# Pub/Sub permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/pubsub.admin" \
    --condition=None

# Cloud Build permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/cloudbuild.builds.editor" \
    --condition=None

# Enable necessary APIs
echo "Enabling necessary Google Cloud APIs..."
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    cloudfunctions.googleapis.com \
    containerregistry.googleapis.com \
    pubsub.googleapis.com \
    secretmanager.googleapis.com \
    artifactregistry.googleapis.com

# Create a new key for the service account
echo "Creating service account key..."
gcloud iam service-accounts keys create $KEY_FILE \
    --iam-account=$SERVICE_ACCOUNT_EMAIL

echo ""
echo "Service account setup complete!"
echo ""
echo "IMPORTANT: Next steps:"
echo "1. The service account key has been saved to: $KEY_FILE"
echo "2. Add this key to your GitHub repository secrets:"
echo "   - Go to: https://github.com/identity-wael/neurascale/settings/secrets/actions"
echo "   - Click 'New repository secret'"
echo "   - Name: GCP_SA_KEY"
echo "   - Value: Copy the entire contents of $KEY_FILE"
echo ""
echo "3. The key file contains sensitive information. After adding it to GitHub:"
echo "   - Delete the local file: rm $KEY_FILE"
echo "   - Or move it to a secure location"
echo ""
echo "To view the key contents (for copying to GitHub):"
echo "cat $KEY_FILE"
