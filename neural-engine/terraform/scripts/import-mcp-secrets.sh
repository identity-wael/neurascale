#!/bin/bash
# Script to import existing MCP secrets into Terraform state

set -e

echo "Importing existing MCP secrets into Terraform state..."

# Set the environment
ENVIRONMENT="${1:-staging}"
PROJECT_ID="${ENVIRONMENT}-neurascale"

echo "Environment: $ENVIRONMENT"
echo "Project ID: $PROJECT_ID"

# Navigate to terraform directory
cd "$(dirname "$0")/.."

# Initialize Terraform with backend config
terraform init -backend-config="prefix=neural-engine/${ENVIRONMENT}"

# Import the secrets
echo "Importing mcp-api-key-salt secret..."
terraform import \
  -var="project_id=${PROJECT_ID}" \
  -var="environment=${ENVIRONMENT}" \
  -var="github_actions_service_account=github-actions@neurascale.iam.gserviceaccount.com" \
  -var="mcp_server_image=northamerica-northeast1-docker.pkg.dev/${PROJECT_ID}/neural-engine-${ENVIRONMENT}/mcp-server:latest" \
  module.mcp_server.google_secret_manager_secret.mcp_api_key_salt \
  "projects/${PROJECT_ID}/secrets/mcp-api-key-salt" || echo "Secret already imported or doesn't exist"

echo "Importing mcp-jwt-secret secret..."
terraform import \
  -var="project_id=${PROJECT_ID}" \
  -var="environment=${ENVIRONMENT}" \
  -var="github_actions_service_account=github-actions@neurascale.iam.gserviceaccount.com" \
  -var="mcp_server_image=northamerica-northeast1-docker.pkg.dev/${PROJECT_ID}/neural-engine-${ENVIRONMENT}/mcp-server:latest" \
  module.mcp_server.google_secret_manager_secret.mcp_jwt_secret \
  "projects/${PROJECT_ID}/secrets/mcp-jwt-secret" || echo "Secret already imported or doesn't exist"

# Import the secret versions
echo "Importing secret versions..."
terraform import \
  -var="project_id=${PROJECT_ID}" \
  -var="environment=${ENVIRONMENT}" \
  -var="github_actions_service_account=github-actions@neurascale.iam.gserviceaccount.com" \
  -var="mcp_server_image=northamerica-northeast1-docker.pkg.dev/${PROJECT_ID}/neural-engine-${ENVIRONMENT}/mcp-server:latest" \
  module.mcp_server.google_secret_manager_secret_version.mcp_api_key_salt \
  "projects/${PROJECT_ID}/secrets/mcp-api-key-salt/versions/1" || echo "Version already imported or doesn't exist"

terraform import \
  -var="project_id=${PROJECT_ID}" \
  -var="environment=${ENVIRONMENT}" \
  -var="github_actions_service_account=github-actions@neurascale.iam.gserviceaccount.com" \
  -var="mcp_server_image=northamerica-northeast1-docker.pkg.dev/${PROJECT_ID}/neural-engine-${ENVIRONMENT}/mcp-server:latest" \
  module.mcp_server.google_secret_manager_secret_version.mcp_jwt_secret \
  "projects/${PROJECT_ID}/secrets/mcp-jwt-secret/versions/1" || echo "Version already imported or doesn't exist"

echo "Import complete!"
