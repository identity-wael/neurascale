#!/bin/bash
# Fix Terraform Cloud authentication configuration

set -e

# Check if TF_CLOUD_TOKEN is set
if [ -z "$TF_CLOUD_TOKEN" ]; then
    echo "Error: TF_CLOUD_TOKEN environment variable is not set"
    echo "Please run: export TF_CLOUD_TOKEN=<your-token>"
    exit 1
fi

# Configuration
ORG="neurascale"
WORKLOAD_IDENTITY_POOL_ID="555656387124"
SERVICE_ACCOUNT="terraform-cloud@neurascale.iam.gserviceaccount.com"
PROVIDER_NAME="projects/555656387124/locations/global/workloadIdentityPools/terraform-cloud-pool/providers/terraform-cloud-provider"

# Workspaces to fix
WORKSPACES=("neural-engine-development" "neural-engine-staging" "neural-engine-production")

echo "Fixing Terraform Cloud authentication configuration..."
echo ""

for WORKSPACE_NAME in "${WORKSPACES[@]}"; do
    echo "Fixing workspace: $WORKSPACE_NAME"

    # Get workspace ID
    WORKSPACE_ID=$(curl -s \
        --header "Authorization: Bearer $TF_CLOUD_TOKEN" \
        --header "Content-Type: application/vnd.api+json" \
        https://app.terraform.io/api/v2/organizations/$ORG/workspaces/$WORKSPACE_NAME \
        | jq -r '.data.id')

    if [ "$WORKSPACE_ID" == "null" ] || [ -z "$WORKSPACE_ID" ]; then
        echo "Error: Workspace $WORKSPACE_NAME not found"
        continue
    fi

    echo "Workspace ID: $WORKSPACE_ID"

    # Function to create or update a variable
    create_or_update_var() {
        local KEY=$1
        local VALUE=$2
        local CATEGORY=$3
        local SENSITIVE=${4:-false}
        local DESCRIPTION=$5

        # Check if variable exists
        EXISTING_VAR=$(curl -s \
            --header "Authorization: Bearer $TF_CLOUD_TOKEN" \
            --header "Content-Type: application/vnd.api+json" \
            https://app.terraform.io/api/v2/workspaces/$WORKSPACE_ID/vars \
            | jq -r ".data[] | select(.attributes.key==\"$KEY\") | .id")

        if [ -n "$EXISTING_VAR" ] && [ "$EXISTING_VAR" != "null" ]; then
            echo "  Updating $KEY..."
            # Update existing variable
            curl -s \
                --header "Authorization: Bearer $TF_CLOUD_TOKEN" \
                --header "Content-Type: application/vnd.api+json" \
                --request PATCH \
                --data @- \
                https://app.terraform.io/api/v2/workspaces/$WORKSPACE_ID/vars/$EXISTING_VAR <<EOF > /dev/null
{
  "data": {
    "type": "vars",
    "id": "$EXISTING_VAR",
    "attributes": {
      "value": "$VALUE",
      "description": "$DESCRIPTION"
    }
  }
}
EOF
        else
            echo "  Creating $KEY..."
            # Create new variable
            curl -s \
                --header "Authorization: Bearer $TF_CLOUD_TOKEN" \
                --header "Content-Type: application/vnd.api+json" \
                --request POST \
                --data @- \
                https://app.terraform.io/api/v2/workspaces/$WORKSPACE_ID/vars <<EOF > /dev/null
{
  "data": {
    "type": "vars",
    "attributes": {
      "key": "$KEY",
      "value": "$VALUE",
      "description": "$DESCRIPTION",
      "category": "$CATEGORY",
      "hcl": false,
      "sensitive": $SENSITIVE
    }
  }
}
EOF
        fi
    }

    # Update WIF environment variables with corrected values
    create_or_update_var "TFC_GCP_PROVIDER_AUTH" "true" "env" false "Enable GCP provider authentication"
    create_or_update_var "TFC_GCP_WORKLOAD_IDENTITY_AUDIENCE" "$PROVIDER_NAME" "env" false "GCP Workload Identity audience (full provider name)"
    create_or_update_var "TFC_GCP_RUN_SERVICE_ACCOUNT_EMAIL" "$SERVICE_ACCOUNT" "env" false "Service account to impersonate"
    create_or_update_var "TFC_GCP_WORKLOAD_PROVIDER_NAME" "$PROVIDER_NAME" "env" false "Full workload identity provider name"

    echo "✓ Workspace $WORKSPACE_NAME fixed!"
    echo ""
done

echo "All workspaces have been updated with the correct authentication configuration!"
echo ""
echo "The workspaces should now be able to authenticate with GCP using Workload Identity Federation."
