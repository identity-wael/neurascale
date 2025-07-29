#!/bin/bash
# Script to clean up orphaned resources from Terraform state

set -e

echo "Cleaning up MCP module Terraform state..."

# Set the environment
ENVIRONMENT="${1:-staging}"
PROJECT_ID="${ENVIRONMENT}-neurascale"

echo "Environment: $ENVIRONMENT"
echo "Project ID: $PROJECT_ID"

# Navigate to terraform directory
cd "$(dirname "$0")/.."

# Initialize Terraform with backend config
terraform init -backend-config="prefix=neural-engine/${ENVIRONMENT}"

# List all resources in the state
echo "Current state resources:"
terraform state list | grep mcp_server || echo "No MCP server resources in state"

# Remove orphaned random_password resources if they exist
echo "Removing orphaned random_password resources..."
terraform state rm module.mcp_server.random_password.mcp_api_key_salt 2>/dev/null || echo "No mcp_api_key_salt random_password to remove"
terraform state rm module.mcp_server.random_password.mcp_jwt_secret 2>/dev/null || echo "No mcp_jwt_secret random_password to remove"

# List deposed resources
echo "Checking for deposed resources..."
terraform state list | grep deposed || echo "No deposed resources found"

# If there are deposed secret versions, we need to handle them
if terraform state list | grep -q "deposed"; then
    echo "Found deposed resources. Removing them..."
    # Get all deposed resources and remove them
    terraform state list | grep deposed | while read -r resource; do
        echo "Removing deposed resource: $resource"
        terraform state rm "$resource" || echo "Failed to remove $resource"
    done
fi

echo "State cleanup complete!"

# Show final state
echo "Final state resources:"
terraform state list | grep mcp_server || echo "No MCP server resources in state"
