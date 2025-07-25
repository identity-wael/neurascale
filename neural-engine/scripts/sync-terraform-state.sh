#!/bin/bash
set -e

# Script to backup Terraform Cloud state to GCS
# Run this periodically (e.g., via cron or Cloud Scheduler)

ORGANIZATION="neurascale"
BUCKET="neurascale-terraform-state"
WORKSPACES=("neural-engine-development" "neural-engine-staging" "neural-engine-production")

# Check for Terraform Cloud token
if [ -z "$TF_CLOUD_TOKEN" ]; then
    echo "Error: TF_CLOUD_TOKEN environment variable not set"
    echo "Generate a token at: https://app.terraform.io/app/settings/tokens"
    exit 1
fi

echo "Syncing Terraform state from Terraform Cloud to GCS..."

for WORKSPACE in "${WORKSPACES[@]}"; do
    echo ""
    echo "Processing workspace: $WORKSPACE"

    # Get the latest state version ID
    STATE_VERSION_ID=$(curl -s \
        -H "Authorization: Bearer $TF_CLOUD_TOKEN" \
        -H "Content-Type: application/vnd.api+json" \
        "https://app.terraform.io/api/v2/workspaces/$WORKSPACE/current-state-version" \
        | jq -r '.data.id')

    if [ "$STATE_VERSION_ID" == "null" ] || [ -z "$STATE_VERSION_ID" ]; then
        echo "No state found for workspace $WORKSPACE"
        continue
    fi

    # Download the state
    echo "Downloading state version: $STATE_VERSION_ID"
    curl -s \
        -H "Authorization: Bearer $TF_CLOUD_TOKEN" \
        "https://app.terraform.io/api/v2/state-versions/$STATE_VERSION_ID/download" \
        -o "/tmp/$WORKSPACE.tfstate"

    # Upload to GCS
    ENV_NAME=${WORKSPACE#neural-engine-}
    echo "Uploading to gs://$BUCKET/backup/$ENV_NAME/terraform.tfstate"
    gsutil cp "/tmp/$WORKSPACE.tfstate" "gs://$BUCKET/backup/$ENV_NAME/terraform.tfstate"

    # Also create a timestamped backup
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    gsutil cp "/tmp/$WORKSPACE.tfstate" "gs://$BUCKET/backup/$ENV_NAME/archive/terraform-$TIMESTAMP.tfstate"

    # Clean up
    rm "/tmp/$WORKSPACE.tfstate"

    echo "✓ Backed up $WORKSPACE state"
done

echo ""
echo "State sync complete!"
