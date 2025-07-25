#!/bin/bash
# Script to set up cross-project permissions for GitHub Actions service account

set -e

# Configuration
GITHUB_SA="github-actions@neurascale.iam.gserviceaccount.com"
PROJECTS=("staging-neurascale" "production-neurascale" "development-neurascale")

# Roles to grant
ROLES=(
  "roles/editor"
  "roles/iam.serviceAccountAdmin"
  "roles/iam.roleAdmin"
  "roles/resourcemanager.projectIamAdmin"
  "roles/billing.costsManager"
  "roles/monitoring.admin"
  "roles/logging.admin"
)

# APIs to enable
APIS=(
  "iam.googleapis.com"
  "cloudresourcemanager.googleapis.com"
  "billingbudgets.googleapis.com"
  "bigquery.googleapis.com"
)

echo "Setting up cross-project permissions for $GITHUB_SA"
echo "==========================================="

for PROJECT in "${PROJECTS[@]}"; do
  echo ""
  echo "Processing project: $PROJECT"
  echo "-----------------------------------"

  # Set the project
  gcloud config set project "$PROJECT" --quiet

  # Enable APIs
  echo "Enabling APIs..."
  for API in "${APIS[@]}"; do
    echo "  - Enabling $API"
    gcloud services enable "$API" --project="$PROJECT" || echo "    (may already be enabled)"
  done

  # Grant IAM roles
  echo "Granting IAM roles..."
  for ROLE in "${ROLES[@]}"; do
    echo "  - Granting $ROLE"
    gcloud projects add-iam-policy-binding "$PROJECT" \
      --member="serviceAccount:$GITHUB_SA" \
      --role="$ROLE" \
      --quiet || echo "    (may already exist)"
  done
done

echo ""
echo "Setup complete!"
echo ""
echo "Summary:"
echo "- Service Account: $GITHUB_SA"
echo "- Projects: ${PROJECTS[*]}"
echo "- Roles granted: ${#ROLES[@]} roles"
echo "- APIs enabled: ${#APIS[@]} APIs"
