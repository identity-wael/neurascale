#!/bin/bash
set -euo pipefail

# Script to create service account and key for Neural Engine CI/CD
# This version assumes you're already authenticated with gcloud

PROJECT_ID="neurascale"
SERVICE_ACCOUNT_NAME="neural-engine-ci"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
KEY_FILE="neural-engine-ci-key.json"

echo "Creating service account for Neural Engine CI/CD..."
echo "Project: $PROJECT_ID"
echo "Service Account: $SERVICE_ACCOUNT_EMAIL"
echo ""

# Check if service account exists
if gcloud iam service-accounts describe $SERVICE_ACCOUNT_EMAIL --project=$PROJECT_ID &> /dev/null; then
    echo "✓ Service account already exists"
else
    echo "Creating service account..."
    gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
        --display-name="Neural Engine CI/CD Service Account" \
        --description="Service account for Neural Engine CI/CD pipeline" \
        --project=$PROJECT_ID
fi

echo ""
echo "Granting IAM roles..."

# List of roles to grant
ROLES=(
    "roles/storage.admin"
    "roles/run.admin"
    "roles/cloudfunctions.admin"
    "roles/iam.serviceAccountUser"
    "roles/pubsub.admin"
    "roles/cloudbuild.builds.editor"
)

for role in "${ROLES[@]}"; do
    echo "  - Granting $role..."
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
        --role="$role" \
        --project=$PROJECT_ID \
        --condition=None \
        --quiet
done

echo ""
echo "Enabling Google Cloud APIs..."

APIS=(
    "cloudbuild.googleapis.com"
    "run.googleapis.com"
    "cloudfunctions.googleapis.com"
    "containerregistry.googleapis.com"
    "pubsub.googleapis.com"
    "secretmanager.googleapis.com"
    "artifactregistry.googleapis.com"
)

for api in "${APIS[@]}"; do
    echo "  - Enabling $api..."
    gcloud services enable $api --project=$PROJECT_ID
done

echo ""
echo "Creating service account key..."
gcloud iam service-accounts keys create $KEY_FILE \
    --iam-account=$SERVICE_ACCOUNT_EMAIL \
    --project=$PROJECT_ID

echo ""
echo "=========================================="
echo "✅ Service account setup complete!"
echo "=========================================="
echo ""
echo "Key file created: $KEY_FILE"
echo ""
echo "Next steps:"
echo "1. Copy the key contents:"
echo "   cat $KEY_FILE | pbcopy"
echo ""
echo "2. Add to GitHub secrets:"
echo "   https://github.com/identity-wael/neurascale/settings/secrets/actions"
echo "   - Name: GCP_SA_KEY"
echo "   - Value: Paste the JSON contents"
echo ""
echo "3. Also add GCP_PROJECT_ID secret:"
echo "   - Name: GCP_PROJECT_ID"
echo "   - Value: neurascale"
echo ""
echo "4. Delete the local key file:"
echo "   rm $KEY_FILE"
echo ""
