#!/bin/bash
# Apply cross-project IAM permissions

cd "$(dirname "$0")"

echo "=== APPLYING CROSS-PROJECT IAM PERMISSIONS ==="
echo ""
echo "This will grant github-actions@neurascale.iam.gserviceaccount.com"
echo "permissions to push to Artifact Registry in development-neurascale project"
echo ""

# Initialize Terraform
terraform init

# Plan the changes
terraform plan -out=tfplan

# Apply the changes
terraform apply tfplan

echo ""
echo "Permissions have been applied. Production builds should now work."
