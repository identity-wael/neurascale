#!/bin/bash
# Configure Terraform Cloud workspaces with Workload Identity Federation

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

# Environments and their corresponding GCP projects
ENVIRONMENTS="development:development-neurascale staging:staging-neurascale production:production-neurascale"

echo "Configuring Terraform Cloud workspaces for Workload Identity Federation..."
echo ""

for ENV_PAIR in $ENVIRONMENTS; do
    ENV=$(echo "$ENV_PAIR" | cut -d: -f1)
    PROJECT_ID=$(echo "$ENV_PAIR" | cut -d: -f2)
    WORKSPACE_NAME="neural-engine-$ENV"

    echo "Configuring workspace: $WORKSPACE_NAME"
    echo "Target GCP Project: $PROJECT_ID"

    # Get workspace ID
    WORKSPACE_ID=$(curl -s \
        --header "Authorization: Bearer $TF_CLOUD_TOKEN" \
        --header "Content-Type: application/vnd.api+json" \
        https://app.terraform.io/api/v2/organizations/$ORG/workspaces/$WORKSPACE_NAME \
        | jq -r '.data.id')

    if [ "$WORKSPACE_ID" == "null" ]; then
        echo "Creating workspace $WORKSPACE_NAME..."

        # Create workspace
        RESPONSE=$(curl -s \
            --header "Authorization: Bearer $TF_CLOUD_TOKEN" \
            --header "Content-Type: application/vnd.api+json" \
            --request POST \
            --data @- \
            https://app.terraform.io/api/v2/organizations/$ORG/workspaces <<EOF
{
  "data": {
    "type": "workspaces",
    "attributes": {
      "name": "$WORKSPACE_NAME",
      "terraform-version": "1.6.0",
      "execution-mode": "remote",
      "auto-apply": false,
      "description": "Neural Engine $ENV environment",
      "tag-names": ["neural-engine", "$ENV"]
    }
  }
}
EOF
)

        WORKSPACE_ID=$(echo "$RESPONSE" | jq -r '.data.id')
        echo "Created workspace with ID: $WORKSPACE_ID"
    fi

    echo "Setting environment variables for WIF..."

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
            # Update existing variable
            curl -s \
                --header "Authorization: Bearer $TF_CLOUD_TOKEN" \
                --header "Content-Type: application/vnd.api+json" \
                --request PATCH \
                --data @- \
                https://app.terraform.io/api/v2/workspaces/$WORKSPACE_ID/vars/$EXISTING_VAR <<EOF
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
            # Create new variable
            curl -s \
                --header "Authorization: Bearer $TF_CLOUD_TOKEN" \
                --header "Content-Type: application/vnd.api+json" \
                --request POST \
                --data @- \
                https://app.terraform.io/api/v2/workspaces/$WORKSPACE_ID/vars <<EOF
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

    # Set WIF environment variables
    create_or_update_var "TFC_GCP_PROVIDER_AUTH" "true" "env" false "Enable GCP provider authentication"
    create_or_update_var "TFC_GCP_WORKLOAD_IDENTITY_AUDIENCE" "//iam.googleapis.com/projects/$WORKLOAD_IDENTITY_POOL_ID/locations/global/workloadIdentityPools/terraform-cloud-pool/providers/terraform-cloud-provider" "env" false "GCP Workload Identity audience"
    create_or_update_var "TFC_GCP_RUN_SERVICE_ACCOUNT_EMAIL" "$SERVICE_ACCOUNT" "env" false "Service account to impersonate"

    # Set Terraform variables
    create_or_update_var "project_id" "$PROJECT_ID" "terraform" false "Target GCP project for this environment"
    create_or_update_var "orchestration_project_id" "neurascale" "terraform" false "Main orchestration project"
    create_or_update_var "region" "northamerica-northeast1" "terraform" false "GCP region (Montreal)"

    echo "✓ Workspace $WORKSPACE_NAME configured successfully!"
    echo ""
done

echo "All workspaces configured for Workload Identity Federation!"
echo ""
echo "You can now run Terraform operations in each workspace."
echo "The workspaces will authenticate using the $SERVICE_ACCOUNT service account."
