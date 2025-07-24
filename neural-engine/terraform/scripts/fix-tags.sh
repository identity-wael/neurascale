#!/bin/bash

# Fix tags using the correct API format

if [ -z "$TF_CLOUD_TOKEN" ]; then
    echo "Error: TF_CLOUD_TOKEN environment variable is not set"
    exit 1
fi

API_URL="https://app.terraform.io/api/v2"
ORG="neurascale"

# Function to get workspace ID
get_workspace_id() {
    local workspace_name=$1
    curl -s \
        -H "Authorization: Bearer $TF_CLOUD_TOKEN" \
        "$API_URL/organizations/$ORG/workspaces/$workspace_name" | \
        jq -r '.data.id'
}

# Function to add tag binding
add_tag_binding() {
    local workspace_id=$1
    local workspace_name=$2

    echo "Adding neural-engine tag to $workspace_name (ID: $workspace_id)..."

    # First, we need to create the tag if it doesn't exist
    tag_response=$(curl -s -X POST \
        -H "Authorization: Bearer $TF_CLOUD_TOKEN" \
        -H "Content-Type: application/vnd.api+json" \
        "$API_URL/organizations/$ORG/tags" \
        -d '{
          "data": {
            "type": "tags",
            "attributes": {
              "name": "neural-engine"
            }
          }
        }')

    # Now add the tag to the workspace
    response=$(curl -s -X POST \
        -H "Authorization: Bearer $TF_CLOUD_TOKEN" \
        -H "Content-Type: application/vnd.api+json" \
        "$API_URL/workspaces/$workspace_id/relationships/tags" \
        -d '{
          "data": [
            {
              "type": "tags",
              "id": "neural-engine"
            }
          ]
        }')

    if echo "$response" | grep -q "errors"; then
        echo "Error response: $response"
    else
        echo "✓ Tag added to $workspace_name"
    fi
}

# Get workspace IDs and add tags
echo "Fixing workspace tags..."

for workspace in production staging development; do
    workspace_id=$(get_workspace_id "$workspace")
    if [ "$workspace_id" != "null" ] && [ -n "$workspace_id" ]; then
        add_tag_binding "$workspace_id" "$workspace"
    else
        echo "✗ Could not find workspace: $workspace"
    fi
done

echo "Done!"
