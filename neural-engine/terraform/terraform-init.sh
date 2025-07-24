#!/bin/bash
set -e

# Script to initialize and apply Terraform configuration

echo "Initializing Terraform with GCS backend..."
cd "$(dirname "$0")"

# Set the orchestration project
export GOOGLE_PROJECT="neurascale"
gcloud config set project $GOOGLE_PROJECT

# Initialize Terraform
terraform init

# Create workspace for each environment if they don't exist
for env in development staging production; do
    terraform workspace new $env 2>/dev/null || echo "Workspace $env already exists"
done

echo ""
echo "Terraform initialized successfully!"
echo ""
echo "Available workspaces:"
terraform workspace list
echo ""
echo "To deploy to an environment, run:"
echo "  terraform workspace select <environment>"
echo "  terraform plan"
echo "  terraform apply"
echo ""
echo "Example:"
echo "  terraform workspace select development"
echo "  terraform apply -var-file=environments/development.tfvars"
