#!/bin/bash
# Migration script from old Terraform architecture to simplified architecture

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if environment is provided
if [ $# -ne 1 ]; then
    print_error "Usage: $0 <environment>"
    echo "Environment must be one of: development, staging, production"
    exit 1
fi

ENVIRONMENT=$1
PROJECT_ID="${ENVIRONMENT}-neurascale"
REGION="northamerica-northeast1"
STATE_BUCKET="neurascale-terraform-state"

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
    print_error "Invalid environment: $ENVIRONMENT"
    echo "Environment must be one of: development, staging, production"
    exit 1
fi

print_info "Starting migration for environment: $ENVIRONMENT"
print_info "Project ID: $PROJECT_ID"

# Step 1: Check prerequisites
print_info "Checking prerequisites..."

if ! command -v terraform &> /dev/null; then
    print_error "Terraform not found. Please install Terraform >= 1.5.0"
    exit 1
fi

if ! command -v gcloud &> /dev/null; then
    print_error "gcloud not found. Please install Google Cloud SDK"
    exit 1
fi

# Check authentication
if ! gcloud auth application-default print-access-token &> /dev/null; then
    print_warn "Not authenticated. Running 'gcloud auth application-default login'..."
    gcloud auth application-default login
fi

# Step 2: Backup current state (if exists)
print_info "Checking for existing Terraform state..."

# Initialize with current backend to check state
cd "$(dirname "$0")"

if [ -f ".terraform/terraform.tfstate" ]; then
    print_info "Found local Terraform state, backing up..."
    cp .terraform/terraform.tfstate ".terraform/terraform.tfstate.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Step 3: Check for existing resources
print_info "Checking for existing resources in GCP..."

# Check for existing service account
SA_NAME="neural-ingestion-${ENVIRONMENT:0:3}"
if gcloud iam service-accounts describe "${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --project="${PROJECT_ID}" &> /dev/null; then
    print_warn "Service account ${SA_NAME} already exists"
    read -p "Do you want to import it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        IMPORT_SA=true
    else
        IMPORT_SA=false
    fi
else
    IMPORT_SA=false
fi

# Step 4: Initialize new backend
print_info "Initializing Terraform with new backend configuration..."

terraform init \
    -backend-config="bucket=${STATE_BUCKET}" \
    -backend-config="prefix=neural-engine/${ENVIRONMENT}" \
    -migrate-state

# Step 5: Import existing resources if needed
if [ "$IMPORT_SA" = true ]; then
    print_info "Importing existing service account..."
    terraform import \
        -var="project_id=${PROJECT_ID}" \
        -var="region=${REGION}" \
        google_service_account.neural_ingestion \
        "${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
fi

# Step 6: Create a plan
print_info "Creating Terraform plan..."

terraform plan \
    -var="project_id=${PROJECT_ID}" \
    -var="region=${REGION}" \
    -out=migration.tfplan

# Step 7: Show what will be created/changed
print_info "Summary of changes:"
terraform show -no-color migration.tfplan | grep -E "^  # |will be created|will be updated|will be destroyed" || true

# Step 8: Ask for confirmation
print_warn "Please review the plan above carefully!"
read -p "Do you want to apply these changes? (yes/no) " -r
if [[ ! $REPLY == "yes" ]]; then
    print_info "Migration cancelled"
    exit 0
fi

# Step 9: Apply the changes
print_info "Applying Terraform configuration..."

terraform apply migration.tfplan

# Step 10: Verify deployment
print_info "Verifying deployment..."

# Check service account
if gcloud iam service-accounts describe "${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --project="${PROJECT_ID}" &> /dev/null; then
    print_info "✓ Service account created successfully"
else
    print_error "✗ Service account not found"
fi

# Check Pub/Sub topics
TOPICS=$(gcloud pubsub topics list --project="${PROJECT_ID}" --format="value(name)" | grep "neural-data" || true)
if [ -n "$TOPICS" ]; then
    print_info "✓ Pub/Sub topics created successfully"
    echo "$TOPICS"
else
    print_error "✗ No Pub/Sub topics found"
fi

# Check Bigtable instance
if gcloud bigtable instances describe "neural-data-${ENVIRONMENT:0:3}" \
    --project="${PROJECT_ID}" &> /dev/null; then
    print_info "✓ Bigtable instance created successfully"
else
    print_error "✗ Bigtable instance not found"
fi

# Step 11: Show outputs
print_info "Deployment outputs:"
terraform output

# Step 12: Next steps
print_info "Migration completed!"
print_info "Next steps:"
echo "1. Update your GitHub Actions to use the new workflow: neural-engine-deploy-simplified.yml"
echo "2. Deploy Cloud Functions using the GitHub Actions workflow or manually"
echo "3. Test the deployment by publishing a message to one of the Pub/Sub topics"
echo "4. Monitor Cloud Functions logs for any issues"

# Clean up
rm -f migration.tfplan

print_info "Done!"
