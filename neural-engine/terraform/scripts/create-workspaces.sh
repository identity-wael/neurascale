#!/bin/bash

# Script to create Terraform Cloud workspaces for NeuraScale
# This script should be run with the TF_CLOUD_TOKEN environment variable set

set -e

ORGANIZATION="neurascale"
API_URL="https://app.terraform.io/api/v2"

# Check if token is set
if [ -z "$TF_CLOUD_TOKEN" ]; then
    echo "Error: TF_CLOUD_TOKEN environment variable is not set"
    echo "Please set it with: export TF_CLOUD_TOKEN='your-token-here'"
    exit 1
fi

# Function to create a workspace
create_workspace() {
    local workspace_name=$1
    local project_id=$2

    echo "Creating workspace: $workspace_name for project: $project_id"

    # Create the workspace
    response=$(curl -s -X POST \
        -H "Authorization: Bearer $TF_CLOUD_TOKEN" \
        -H "Content-Type: application/vnd.api+json" \
        "$API_URL/organizations/$ORGANIZATION/workspaces" \
        -d @- <<EOF
{
  "data": {
    "type": "workspaces",
    "attributes": {
      "name": "$workspace_name",
      "execution-mode": "remote",
      "auto-apply": false,
      "description": "Neural Engine workspace for $workspace_name environment",
      "terraform-version": "1.6.0"
    }
  }
}
EOF
    )

    # Check if workspace was created or already exists
    if echo "$response" | grep -q '"id"'; then
        echo "✓ Workspace $workspace_name created successfully"
        workspace_id=$(echo "$response" | jq -r '.data.id')
    elif echo "$response" | grep -q "already exists"; then
        echo "✓ Workspace $workspace_name already exists, getting ID..."
        # Get workspace ID
        workspace_response=$(curl -s \
            -H "Authorization: Bearer $TF_CLOUD_TOKEN" \
            "$API_URL/organizations/$ORGANIZATION/workspaces/$workspace_name")
        workspace_id=$(echo "$workspace_response" | jq -r '.data.id')
    else
        echo "✗ Failed to create workspace $workspace_name"
        echo "$response"
        return 1
    fi

    echo "Workspace ID: $workspace_id"

    # Set environment variables for the workspace
    echo "Setting environment variables for $workspace_name..."

    # Variables to set based on the workspace
    case "$workspace_name" in
        "production")
            gcp_project_num="1088620953058"
            ;;
        "staging")
            gcp_project_num="221358080383"
            ;;
        "development")
            gcp_project_num="761791897607"
            ;;
    esac

    # Common WIF variables (same for all workspaces)
    wif_pool_id="github-actions"
    wif_provider_id="github"

    # Create environment variables
    vars=(
        "TFC_GCP_PROVIDER_AUTH|true|false|env"
        "TFC_GCP_PROJECT_NUMBER|$gcp_project_num|false|env"
        "TFC_GCP_WORKLOAD_POOL_ID|$wif_pool_id|false|env"
        "TFC_GCP_WORKLOAD_PROVIDER_ID|$wif_provider_id|false|env"
        "TFC_GCP_RUN_SERVICE_ACCOUNT_EMAIL|terraform@$project_id.iam.gserviceaccount.com|false|env"
    )

    for var_def in "${vars[@]}"; do
        IFS='|' read -r key value sensitive category <<< "$var_def"

        echo "  Setting $key..."

        var_response=$(curl -s -X POST \
            -H "Authorization: Bearer $TF_CLOUD_TOKEN" \
            -H "Content-Type: application/vnd.api+json" \
            "$API_URL/workspaces/$workspace_id/vars" \
            -d @- <<EOF
{
  "data": {
    "type": "vars",
    "attributes": {
      "key": "$key",
      "value": "$value",
      "category": "$category",
      "sensitive": $sensitive
    }
  }
}
EOF
        )

        if echo "$var_response" | grep -q '"id"'; then
            echo "  ✓ $key set successfully"
        elif echo "$var_response" | grep -q "already exists"; then
            echo "  ✓ $key already exists"
        else
            echo "  ✗ Failed to set $key"
            echo "$var_response"
        fi
    done

    echo ""
}

# Main execution
echo "Creating Terraform Cloud workspaces for NeuraScale..."
echo ""

# Create workspaces
create_workspace "production" "production-neurascale"
create_workspace "staging" "staging-neurascale"
create_workspace "development" "development-neurascale"

echo ""
echo "Workspace creation complete!"
echo ""
echo "To use these workspaces:"
echo "  export TF_WORKSPACE=staging"
echo "  terraform init"
echo "  terraform plan"
