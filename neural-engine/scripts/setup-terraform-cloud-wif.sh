#!/bin/bash
set -e

# Script to set up Workload Identity Federation for Terraform Cloud

PROJECT_ID="neurascale"
POOL_NAME="terraform-cloud-pool"
PROVIDER_NAME="terraform-cloud-provider"
SERVICE_ACCOUNT="terraform-cloud@${PROJECT_ID}.iam.gserviceaccount.com"
TFC_ORG="neurascale"
TFC_PROJECT="Default Project"
TFC_WORKSPACE_PREFIX="neural-engine"

echo "Setting up Workload Identity Federation for Terraform Cloud..."

# Enable required APIs
echo "Enabling required APIs..."
gcloud services enable iamcredentials.googleapis.com \
    iam.googleapis.com \
    cloudresourcemanager.googleapis.com \
    --project=$PROJECT_ID

# Create service account for Terraform Cloud
echo "Creating service account..."
gcloud iam service-accounts create terraform-cloud \
    --display-name="Terraform Cloud Service Account" \
    --description="Service account for Terraform Cloud to manage infrastructure" \
    --project=$PROJECT_ID || echo "Service account already exists"

# Grant necessary permissions
echo "Granting permissions to service account..."
for role in \
    "roles/owner" \
    "roles/resourcemanager.projectIamAdmin" \
    "roles/iam.serviceAccountUser" \
    "roles/storage.admin"; do

    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$SERVICE_ACCOUNT" \
        --role="$role" \
        --quiet
done

# Also grant permissions on environment projects
for ENV_PROJECT in production-neurascale staging-neurascale development-neurascale; do
    echo "Granting permissions on $ENV_PROJECT..."
    for role in \
        "roles/owner" \
        "roles/resourcemanager.projectIamAdmin"; do

        gcloud projects add-iam-policy-binding $ENV_PROJECT \
            --member="serviceAccount:$SERVICE_ACCOUNT" \
            --role="$role" \
            --quiet || echo "Failed to grant $role on $ENV_PROJECT (project might not be accessible)"
    done
done

# Create workload identity pool
echo "Creating workload identity pool..."
gcloud iam workload-identity-pools create $POOL_NAME \
    --location="global" \
    --display-name="Terraform Cloud Pool" \
    --description="Pool for Terraform Cloud authentication" \
    --project=$PROJECT_ID || echo "Pool already exists"

# Create workload identity provider
echo "Creating workload identity provider..."
gcloud iam workload-identity-pools providers create-oidc $PROVIDER_NAME \
    --location="global" \
    --workload-identity-pool=$POOL_NAME \
    --display-name="Terraform Cloud Provider" \
    --attribute-mapping="google.subject=assertion.sub,attribute.org_id=assertion.terraform_organization_id,attribute.project_id=assertion.terraform_project_id,attribute.workspace_id=assertion.terraform_workspace_id,attribute.workspace_name=assertion.terraform_workspace_name" \
    --issuer-uri="https://app.terraform.io" \
    --attribute-condition="assertion.terraform_organization_id == '${TFC_ORG}'" \
    --project=$PROJECT_ID || echo "Provider already exists"

# Get the pool ID
POOL_ID=$(gcloud iam workload-identity-pools describe $POOL_NAME \
    --location="global" \
    --project=$PROJECT_ID \
    --format="value(name)")

# Grant workload identity user role
echo "Granting workload identity user role..."
gcloud iam service-accounts add-iam-policy-binding $SERVICE_ACCOUNT \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/${POOL_ID}/attribute.org_id/${TFC_ORG}" \
    --project=$PROJECT_ID

# Output the provider resource name
PROVIDER_RESOURCE_NAME="projects/${PROJECT_ID}/locations/global/workloadIdentityPools/${POOL_NAME}/providers/${PROVIDER_NAME}"

echo ""
echo "✓ Workload Identity Federation setup complete!"
echo ""
echo "Now configure your Terraform Cloud workspaces with these environment variables:"
echo ""
echo "1. Go to each workspace in Terraform Cloud:"
echo "   - neural-engine-development"
echo "   - neural-engine-staging"
echo "   - neural-engine-production"
echo ""
echo "2. Add these Environment Variables:"
echo "   TFC_GCP_PROVIDER_AUTH = true"
echo "   TFC_GCP_RUN_SERVICE_ACCOUNT_EMAIL = $SERVICE_ACCOUNT"
echo "   TFC_GCP_WORKLOAD_PROVIDER_NAME = $PROVIDER_RESOURCE_NAME"
echo ""
echo "3. The authentication will work automatically without service account keys!"
