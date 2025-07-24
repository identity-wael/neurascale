#!/bin/bash
set -euo pipefail

# Setup Workload Identity Federation for GitHub Actions
# This allows GitHub Actions to authenticate without service account keys

PROJECT_ID="neurascale"
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
POOL_NAME="github-actions"
PROVIDER_NAME="github"
SERVICE_ACCOUNT_EMAIL="neural-engine-ci@neurascale.iam.gserviceaccount.com"
GITHUB_REPO="identity-wael/neurascale"

echo "Setting up Workload Identity Federation for GitHub Actions..."
echo "Project: $PROJECT_ID (Number: $PROJECT_NUMBER)"
echo "Repository: $GITHUB_REPO"
echo ""

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable iam.googleapis.com \
    iamcredentials.googleapis.com \
    cloudresourcemanager.googleapis.com \
    --project=$PROJECT_ID

# Create workload identity pool
echo "Creating workload identity pool..."
gcloud iam workload-identity-pools create $POOL_NAME \
    --location="global" \
    --description="GitHub Actions identity pool" \
    --project=$PROJECT_ID || echo "Pool already exists"

# Create workload identity provider
echo "Creating workload identity provider..."
gcloud iam workload-identity-pools providers create-oidc $PROVIDER_NAME \
    --location="global" \
    --workload-identity-pool=$POOL_NAME \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
    --project=$PROJECT_ID || echo "Provider already exists"

# Grant service account permissions to workload identity
echo "Configuring service account permissions..."
gcloud iam service-accounts add-iam-policy-binding $SERVICE_ACCOUNT_EMAIL \
    --project=$PROJECT_ID \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$POOL_NAME/attribute.repository/$GITHUB_REPO"

# Get the workload identity provider resource name
WORKLOAD_IDENTITY_PROVIDER="projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$POOL_NAME/providers/$PROVIDER_NAME"

echo ""
echo "=========================================="
echo "✅ Workload Identity Federation setup complete!"
echo "=========================================="
echo ""
echo "Update your GitHub workflow to use:"
echo ""
echo "- name: Authenticate to Google Cloud"
echo "  uses: google-github-actions/auth@v1"
echo "  with:"
echo "    workload_identity_provider: '$WORKLOAD_IDENTITY_PROVIDER'"
echo "    service_account: '$SERVICE_ACCOUNT_EMAIL'"
echo ""
echo "Add these as GitHub secrets:"
echo "1. Go to: https://github.com/$GITHUB_REPO/settings/secrets/actions"
echo ""
echo "2. Add secret: GCP_WIF_PROVIDER"
echo "   Value: $WORKLOAD_IDENTITY_PROVIDER"
echo ""
echo "3. Add secret: GCP_WIF_SERVICE_ACCOUNT"
echo "   Value: $SERVICE_ACCOUNT_EMAIL"
echo ""
echo "4. Add secret: GCP_PROJECT_ID"
echo "   Value: $PROJECT_ID"
echo ""
