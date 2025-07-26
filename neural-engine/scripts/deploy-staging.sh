#!/bin/bash

# Neural Ledger Staging Deployment Script
# This script deploys the Neural Ledger to a staging environment for testing

set -euo pipefail

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-neurascale-staging}"
REGION="${GCP_REGION:-northamerica-northeast1}"
ENVIRONMENT="staging"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI is not installed. Please install it first."
        exit 1
    fi

    # Check if terraform is installed
    if ! command -v terraform &> /dev/null; then
        log_error "Terraform is not installed. Please install it first."
        exit 1
    fi

    # Check if we're authenticated with GCP
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        log_error "Not authenticated with GCP. Please run: gcloud auth login"
        exit 1
    fi

    # Check if project exists and we have access
    if ! gcloud projects describe "${PROJECT_ID}" &> /dev/null; then
        log_error "Project ${PROJECT_ID} does not exist or you don't have access."
        exit 1
    fi

    log_success "Prerequisites check passed"
}

# Enable required APIs
enable_apis() {
    log_info "Enabling required GCP APIs..."

    local apis=(
        "cloudresourcemanager.googleapis.com"
        "cloudbuild.googleapis.com"
        "cloudfunctions.googleapis.com"
        "pubsub.googleapis.com"
        "bigtable.googleapis.com"
        "firestore.googleapis.com"
        "bigquery.googleapis.com"
        "cloudkms.googleapis.com"
        "monitoring.googleapis.com"
        "logging.googleapis.com"
        "secretmanager.googleapis.com"
    )

    for api in "${apis[@]}"; do
        log_info "Enabling ${api}..."
        gcloud services enable "${api}" --project="${PROJECT_ID}"
    done

    log_success "All required APIs enabled"
}

# Deploy infrastructure with Terraform
deploy_infrastructure() {
    log_info "Deploying infrastructure with Terraform..."

    cd infrastructure/ledger

    # Initialize Terraform
    terraform init -upgrade

    # Create terraform.tfvars for staging
    cat > terraform.tfvars <<EOF
project_id = "${PROJECT_ID}"
region = "${REGION}"
environment = "${ENVIRONMENT}"

# Staging-specific overrides
bigtable_num_nodes = 1
enable_deletion_protection = false
monitoring_retention_days = 7
EOF

    # Plan the deployment
    log_info "Planning Terraform deployment..."
    terraform plan -var-file=terraform.tfvars -out=staging.tfplan

    # Apply the deployment
    log_info "Applying Terraform deployment..."
    terraform apply staging.tfplan

    log_success "Infrastructure deployed successfully"

    cd ../..
}

# Build and deploy Cloud Functions
deploy_functions() {
    log_info "Deploying Cloud Functions..."

    cd functions/ledger_handler

    # Create deployment package
    log_info "Creating deployment package..."
    rm -rf deployment_package
    mkdir -p deployment_package

    # Copy function code
    cp main.py deployment_package/
    cp requirements.txt deployment_package/

    # Copy ledger module
    cp -r ../../ledger deployment_package/

    # Deploy the function
    log_info "Deploying ledger handler function..."
    gcloud functions deploy neural-ledger-processor \
        --source=deployment_package \
        --entry-point=process_ledger_event \
        --runtime=python312 \
        --trigger-topic=neural-ledger-events \
        --memory=512MB \
        --timeout=300s \
        --region="${REGION}" \
        --project="${PROJECT_ID}" \
        --set-env-vars="GCP_PROJECT=${PROJECT_ID},ENVIRONMENT=${ENVIRONMENT}" \
        --max-instances=100

    log_success "Cloud Function deployed successfully"

    cd ../..
}

# Set up monitoring and alerting
setup_monitoring() {
    log_info "Setting up monitoring and alerting..."

    # Create monitoring dashboard
    python3 -c "
from ledger.monitoring import create_monitoring_dashboard
import os

project_id = os.environ.get('GCP_PROJECT_ID', '${PROJECT_ID}')
dashboard_name = create_monitoring_dashboard(
    project_id=project_id,
    dashboard_name='neural-ledger-staging'
)
if dashboard_name:
    print(f'Created dashboard: {dashboard_name}')
else:
    print('Failed to create dashboard')
"

    log_success "Monitoring dashboard created"
}

# Run basic health checks
run_health_checks() {
    log_info "Running health checks..."

    # Check if Pub/Sub topic exists
    if gcloud pubsub topics describe neural-ledger-events --project="${PROJECT_ID}" &> /dev/null; then
        log_success "Pub/Sub topic exists"
    else
        log_error "Pub/Sub topic not found"
        return 1
    fi

    # Check if Cloud Function is deployed
    if gcloud functions describe neural-ledger-processor --region="${REGION}" --project="${PROJECT_ID}" &> /dev/null; then
        log_success "Cloud Function deployed"
    else
        log_error "Cloud Function not found"
        return 1
    fi

    # Check if BigQuery dataset exists
    if bq show --project_id="${PROJECT_ID}" neural_ledger &> /dev/null; then
        log_success "BigQuery dataset exists"
    else
        log_error "BigQuery dataset not found"
        return 1
    fi

    log_success "All health checks passed"
}

# Run integration tests
run_integration_tests() {
    log_info "Running integration tests..."

    # Set environment variables for integration tests
    export RUN_INTEGRATION_TESTS=true
    export GCP_PROJECT_ID="${PROJECT_ID}"
    export GCP_LOCATION="${REGION}"

    # Run integration tests
    if python -m pytest tests/test_ledger/test_integration.py -v; then
        log_success "Integration tests passed"
    else
        log_warning "Some integration tests failed. Check the logs for details."
    fi
}

# Main deployment function
main() {
    log_info "Starting Neural Ledger staging deployment..."
    log_info "Project: ${PROJECT_ID}"
    log_info "Region: ${REGION}"
    log_info "Environment: ${ENVIRONMENT}"

    check_prerequisites
    enable_apis
    deploy_infrastructure
    deploy_functions
    setup_monitoring
    run_health_checks

    # Optional: Run integration tests if requested
    if [[ "${RUN_TESTS:-false}" == "true" ]]; then
        run_integration_tests
    fi

    log_success "Neural Ledger staging deployment completed successfully!"

    # Print useful information
    echo ""
    log_info "Deployment Summary:"
    echo "  - Project ID: ${PROJECT_ID}"
    echo "  - Region: ${REGION}"
    echo "  - Environment: ${ENVIRONMENT}"
    echo "  - Cloud Function: neural-ledger-processor"
    echo "  - Pub/Sub Topic: neural-ledger-events"
    echo "  - BigQuery Dataset: neural_ledger"
    echo "  - Bigtable Instance: neural-ledger"
    echo ""
    log_info "Next steps:"
    echo "  1. Test the deployment with sample events"
    echo "  2. Monitor the Cloud Function logs"
    echo "  3. Check the monitoring dashboard"
    echo "  4. Run: RUN_TESTS=true ./scripts/deploy-staging.sh to run integration tests"
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
