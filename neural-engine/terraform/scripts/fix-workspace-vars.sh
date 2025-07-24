#!/bin/bash

# Script to add WIF variables to existing Terraform Cloud workspaces
# Usage: TF_CLOUD_TOKEN=your-token ./fix-workspace-vars.sh

set -e

if [ -z "$TF_CLOUD_TOKEN" ]; then
    echo "Error: TF_CLOUD_TOKEN environment variable is not set"
    exit 1
fi

ORGANIZATION="neurascale"
API_URL="https://app.terraform.io/api/v2"

# Function to add variables to a workspace
add_workspace_vars() {
    local workspace_name=$1

    echo "Adding WIF variables to workspace: $workspace_name"

    # Get workspace ID
    workspace_response=$(curl -s \
        -H "Authorization: Bearer $TF_CLOUD_TOKEN" \
        "$API_URL/organizations/$ORGANIZATION/workspaces/$workspace_name")

    if echo "$workspace_response" | grep -q '"id"'; then
        workspace_id=$(echo "$workspace_response" | jq -r '.data.id')
        echo "Workspace ID: $workspace_id"
    else
        echo "Error: Could not find workspace $workspace_name"
        return 1
    fi

    # WIF Configuration - using the orchestration project's WIF setup
    # The orchestration project (neurascale) has project number 555656387124
    vars=(
        "TFC_GCP_PROVIDER_AUTH|true|false|env"
        "TFC_GCP_PROJECT_NUMBER|555656387124|false|env"
        "TFC_GCP_WORKLOAD_POOL_ID|github-actions|false|env"
        "TFC_GCP_WORKLOAD_PROVIDER_ID|github|false|env"
    )

    for var_def in "${vars[@]}"; do
        IFS='|' read -r key value sensitive category <<< "$var_def"

        echo "  Setting $key..."

        # First, check if variable already exists
        existing_var=$(curl -s \
            -H "Authorization: Bearer $TF_CLOUD_TOKEN" \
            "$API_URL/workspaces/$workspace_id/vars" | \
            jq -r --arg key "$key" '.data[] | select(.attributes.key == $key) | .id')

        if [ -n "$existing_var" ]; then
            # Update existing variable
            echo "  Updating existing variable $key..."
            curl -s -X PATCH \
                -H "Authorization: Bearer $TF_CLOUD_TOKEN" \
                -H "Content-Type: application/vnd.api+json" \
                "$API_URL/workspaces/$workspace_id/vars/$existing_var" \
                -d @- <<EOF > /dev/null
{
  "data": {
    "type": "vars",
    "id": "$existing_var",
    "attributes": {
      "value": "$value"
    }
  }
}
EOF
            echo "  ✓ $key updated"
        else
            # Create new variable
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
                echo "  ✓ $key created"
            else
                echo "  ✗ Failed to create $key"
                echo "$var_response" | jq '.'
            fi
        fi
    done

    echo ""
}

# Fix all three workspaces
echo "Fixing Terraform Cloud workspace variables..."
echo ""

add_workspace_vars "production"
add_workspace_vars "staging"
add_workspace_vars "development"

echo "Done!"
