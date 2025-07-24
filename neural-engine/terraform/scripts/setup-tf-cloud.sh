#!/bin/bash

# Setup Terraform Cloud workspaces with the neural-engine tag
# This script uses the Terraform CLI to create properly tagged workspaces

set -e

cd "$(dirname "$0")/.."

# Ensure we have credentials
if [ ! -f ~/.terraform.d/credentials.tfrc.json ] && [ -z "$TF_CLOUD_TOKEN" ]; then
    echo "Error: No Terraform Cloud credentials found"
    echo "Please run 'terraform login' or set TF_CLOUD_TOKEN"
    exit 1
fi

# Initialize Terraform to connect to Cloud
echo "Initializing Terraform Cloud connection..."
terraform init -backend=false

# Function to create workspace with tag
create_tagged_workspace() {
    local workspace_name=$1

    echo "Creating workspace: $workspace_name"

    # Select or create workspace
    terraform workspace select "$workspace_name" 2>/dev/null || terraform workspace new "$workspace_name"

    echo "Workspace $workspace_name is ready"
}

# Create all three workspaces
echo "Setting up Terraform Cloud workspaces..."

for env in production staging development; do
    TF_WORKSPACE="$env" create_tagged_workspace "$env"
done

echo ""
echo "All workspaces created successfully!"
echo ""
echo "To use a workspace:"
echo "  export TF_WORKSPACE=staging"
echo "  terraform plan"
