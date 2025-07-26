#!/bin/bash
set -e

echo "Fixing staging Terraform state..."

cd /Users/weg/NeuraScale/neurascale/neural-engine/terraform

# Initialize Terraform for staging
terraform init -backend-config="bucket=neurascale-terraform-state" -backend-config="prefix=neural-engine/staging"

# Set variables
PROJECT_ID="staging-neurascale"
ENVIRONMENT="staging"
REGION="northamerica-northeast1"
GITHUB_SA="github-actions@neurascale.iam.gserviceaccount.com"

# Import existing resources that are causing conflicts
echo "Importing Artifact Registry repository..."
terraform import -var="project_id=$PROJECT_ID" -var="environment=$ENVIRONMENT" -var="region=$REGION" -var="github_actions_service_account=$GITHUB_SA" \
  module.neural_ingestion.google_artifact_registry_repository.neural_engine \
  "projects/$PROJECT_ID/locations/$REGION/repositories/neural-engine-$ENVIRONMENT" || true

echo "Importing service account..."
terraform import -var="project_id=$PROJECT_ID" -var="environment=$ENVIRONMENT" -var="region=$REGION" -var="github_actions_service_account=$GITHUB_SA" \
  module.neural_ingestion.google_service_account.ingestion \
  "neural-ingestion-stag" || true

echo "Importing Bigtable instance..."
terraform import -var="project_id=$PROJECT_ID" -var="environment=$ENVIRONMENT" -var="region=$REGION" -var="github_actions_service_account=$GITHUB_SA" \
  module.neural_ingestion.google_bigtable_instance.neural_data \
  "neural-data-$ENVIRONMENT" || true

echo "Running terraform plan to verify..."
terraform plan -var="project_id=$PROJECT_ID" -var="environment=$ENVIRONMENT" -var="region=$REGION" -var="github_actions_service_account=$GITHUB_SA" -compact-warnings

echo "Done!"
