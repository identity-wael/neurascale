#!/bin/bash
set -e

echo "Setting up Terraform Cloud for NeuraScale"
echo ""
echo "Please ensure you have:"
echo "1. Created a Terraform Cloud account at https://app.terraform.io"
echo "2. Created an organization named 'neurascale'"
echo "3. Generated a Terraform Cloud API token"
echo ""

# Check if already logged in
if ! terraform login -check; then
    echo "Please login to Terraform Cloud:"
    terraform login
fi

# Initialize Terraform
echo ""
echo "Initializing Terraform with Terraform Cloud backend..."
terraform init

# Create workspaces for each environment
echo ""
echo "Creating environment workspaces..."

# Note: Workspaces will be created automatically when we run terraform init
# with the tags configuration

echo ""
echo "To create workspaces in Terraform Cloud:"
echo "1. Go to https://app.terraform.io/app/neurascale/workspaces"
echo "2. Create three workspaces:"
echo "   - neural-engine-development"
echo "   - neural-engine-staging"
echo "   - neural-engine-production"
echo "3. Add the tag 'neural-engine' to each workspace"
echo "4. Configure environment variables in each workspace:"
echo "   - GOOGLE_CREDENTIALS (service account JSON)"
echo "   - TF_VAR_environment (development/staging/production)"
echo ""
echo "After creating workspaces, run:"
echo "  terraform workspace list"
echo "  terraform workspace select <workspace-name>"
echo "  terraform plan"
