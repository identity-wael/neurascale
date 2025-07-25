#!/bin/bash
set -e

# Script to set up IAM permissions for multi-environment deployment

ORCHESTRATION_PROJECT="neurascale"
ENVIRONMENTS=("production-neurascale" "staging-neurascale" "development-neurascale")
SERVICE_ACCOUNT_NAME="github-actions"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${ORCHESTRATION_PROJECT}.iam.gserviceaccount.com"

echo "Setting up multi-environment IAM permissions..."

# Create service account in orchestration project if it doesn't exist
gcloud config set project $ORCHESTRATION_PROJECT

if ! gcloud iam service-accounts describe $SERVICE_ACCOUNT_EMAIL &>/dev/null; then
    echo "Creating service account: $SERVICE_ACCOUNT_EMAIL"
    gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
        --display-name="GitHub Actions CI/CD" \
        --description="Service account for GitHub Actions to deploy to all environments"
fi

# Grant permissions in orchestration project
echo "Granting permissions in orchestration project..."
for role in \
    "roles/resourcemanager.projectIamAdmin" \
    "roles/iam.serviceAccountUser" \
    "roles/storage.admin" \
    "roles/cloudresourcemanager.projectGet"; do

    gcloud projects add-iam-policy-binding $ORCHESTRATION_PROJECT \
        --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
        --role="$role" \
        --quiet
done

# Grant permissions in each environment project
for PROJECT in "${ENVIRONMENTS[@]}"; do
    echo ""
    echo "Granting permissions in $PROJECT..."

    # Core permissions
    for role in \
        "roles/owner" \
        "roles/resourcemanager.projectIamAdmin" \
        "roles/compute.admin" \
        "roles/storage.admin" \
        "roles/pubsub.admin" \
        "roles/bigtable.admin" \
        "roles/cloudfunctions.admin" \
        "roles/artifactregistry.admin" \
        "roles/iam.serviceAccountAdmin" \
        "roles/iam.serviceAccountKeyAdmin" \
        "roles/cloudbuild.builds.editor" \
        "roles/run.admin"; do

        gcloud projects add-iam-policy-binding $PROJECT \
            --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
            --role="$role" \
            --quiet || echo "Failed to add $role to $PROJECT (might not exist yet)"
    done
done

echo ""
echo "IAM setup complete!"
echo ""
echo "Service Account: $SERVICE_ACCOUNT_EMAIL"
echo ""
echo "Next steps:"
echo "1. Set up Workload Identity Federation for GitHub Actions"
echo "2. Configure GitHub secrets:"
echo "   - WIF_PROVIDER: The workload identity provider"
echo "   - WIF_SERVICE_ACCOUNT: $SERVICE_ACCOUNT_EMAIL"
