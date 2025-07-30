#!/bin/bash
# Setup Artifact Registry repositories for Neural Engine

set -e

# Configuration
REGIONS=("northamerica-northeast1")
PROJECTS=("development-neurascale" "staging-neurascale" "production-neurascale")
REPOSITORY_NAME="neural-engine-development"
SERVICE_ACCOUNT="github-actions@neurascale.iam.gserviceaccount.com"

echo "Setting up Artifact Registry repositories..."

for PROJECT in "${PROJECTS[@]}"; do
    echo "Processing project: $PROJECT"

    for REGION in "${REGIONS[@]}"; do
        echo "  Checking/creating repository in region: $REGION"

        # Check if repository exists
        if gcloud artifacts repositories describe $REPOSITORY_NAME \
            --location=$REGION \
            --project=$PROJECT &>/dev/null; then
            echo "    Repository already exists"
        else
            echo "    Creating repository..."
            gcloud artifacts repositories create $REPOSITORY_NAME \
                --repository-format=docker \
                --location=$REGION \
                --project=$PROJECT \
                --description="Neural Engine Docker images" || echo "    Failed to create repository"
        fi

        # Grant permissions to service account
        echo "    Granting permissions to $SERVICE_ACCOUNT..."
        gcloud artifacts repositories add-iam-policy-binding $REPOSITORY_NAME \
            --location=$REGION \
            --project=$PROJECT \
            --member="serviceAccount:$SERVICE_ACCOUNT" \
            --role="roles/artifactregistry.writer" || echo "    Failed to grant permissions"
    done
done

echo "Setup complete!"
