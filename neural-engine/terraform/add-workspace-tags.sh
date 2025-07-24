#!/bin/bash
# Add tags to Terraform Cloud workspaces

set -e

# Check if TF_CLOUD_TOKEN is set
if [ -z "$TF_CLOUD_TOKEN" ]; then
    echo "Error: TF_CLOUD_TOKEN environment variable is not set"
    echo "Please run: export TF_CLOUD_TOKEN=<your-token>"
    exit 1
fi

# Configuration
ORG="neurascale"
WORKSPACES=("neural-engine-development" "neural-engine-staging" "neural-engine-production")

echo "Adding tags to Terraform Cloud workspaces..."
echo ""

for WORKSPACE_NAME in "${WORKSPACES[@]}"; do
    echo "Updating workspace: $WORKSPACE_NAME"

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

    # Extract environment from workspace name
    ENV=${WORKSPACE_NAME#neural-engine-}

    # Update workspace with tags
    curl -s \
        --header "Authorization: Bearer $TF_CLOUD_TOKEN" \
        --header "Content-Type: application/vnd.api+json" \
        --request PATCH \
        --data @- \
        https://app.terraform.io/api/v2/workspaces/$WORKSPACE_ID <<EOF > /dev/null
{
  "data": {
    "type": "workspaces",
    "id": "$WORKSPACE_ID",
    "attributes": {
      "tag-names": ["neural-engine", "$ENV"]
    }
  }
}
EOF

    echo "✓ Workspace $WORKSPACE_NAME updated with tags: neural-engine, $ENV"
done

echo ""
echo "All workspaces have been tagged!"
