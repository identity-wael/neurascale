#!/bin/bash

# Script to add tags to Terraform Cloud workspaces

if [ -z "$TF_CLOUD_TOKEN" ]; then
    echo "Error: TF_CLOUD_TOKEN environment variable is not set"
    exit 1
fi

API_URL="https://app.terraform.io/api/v2"
ORGANIZATION="neurascale"

# Function to add tag to workspace
add_tag() {
    local workspace_name=$1
    local tag=$2

    echo "Adding tag '$tag' to workspace '$workspace_name'..."

    # Get workspace ID
    workspace_response=$(curl -s \
        -H "Authorization: Bearer $TF_CLOUD_TOKEN" \
        "$API_URL/organizations/$ORGANIZATION/workspaces/$workspace_name")

    if echo "$workspace_response" | grep -q '"id"'; then
        workspace_id=$(echo "$workspace_response" | jq -r '.data.id')

        # Update workspace with tag
        update_response=$(curl -s -X PATCH \
            -H "Authorization: Bearer $TF_CLOUD_TOKEN" \
            -H "Content-Type: application/vnd.api+json" \
            "$API_URL/workspaces/$workspace_id" \
            -d @- <<EOF
{
  "data": {
    "type": "workspaces",
    "attributes": {
      "tag-names": ["neural-engine"]
    }
  }
}
EOF
        )

        if echo "$update_response" | grep -q '"id"'; then
            echo "✓ Tag added to $workspace_name"
        else
            echo "✗ Failed to add tag to $workspace_name"
            echo "$update_response" | jq '.'
        fi
    else
        echo "✗ Could not find workspace $workspace_name"
    fi
}

# Add tags to all workspaces
add_tag "production" "neural-engine"
add_tag "staging" "neural-engine"
add_tag "development" "neural-engine"

echo "Done!"
