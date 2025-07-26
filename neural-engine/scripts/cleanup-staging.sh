#!/bin/bash

# Neural Ledger Staging Cleanup Script
# This script cleans up the staging environment to save costs

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

# Confirm cleanup
confirm_cleanup() {
    echo ""
    log_warning "This will DELETE all Neural Ledger resources in staging environment:"
    echo "  - Project: ${PROJECT_ID}"
    echo "  - Region: ${REGION}"
    echo "  - ALL DATA WILL BE LOST"
    echo ""

    read -p "Are you sure you want to continue? (type 'yes' to confirm): " confirmation

    if [[ "${confirmation}" != "yes" ]]; then
        log_info "Cleanup cancelled by user"
        exit 0
    fi
}

# Delete Cloud Functions
cleanup_functions() {
    log_info "Deleting Cloud Functions..."

    if gcloud functions describe neural-ledger-processor --region="${REGION}" --project="${PROJECT_ID}" &> /dev/null; then
        log_info "Deleting neural-ledger-processor function..."
        gcloud functions delete neural-ledger-processor \
            --region="${REGION}" \
            --project="${PROJECT_ID}" \
            --quiet
        log_success "Cloud Function deleted"
    else
        log_info "Cloud Function not found, skipping"
    fi
}

# Delete monitoring resources
cleanup_monitoring() {
    log_info "Cleaning up monitoring resources..."

    # List and delete custom dashboards
    local dashboards
    dashboards=$(gcloud alpha monitoring dashboards list --project="${PROJECT_ID}" --format="value(name)" --filter="displayName:neural-ledger" 2>/dev/null || true)

    if [[ -n "${dashboards}" ]]; then
        while IFS= read -r dashboard; do
            log_info "Deleting dashboard: ${dashboard}"
            gcloud alpha monitoring dashboards delete "${dashboard}" --project="${PROJECT_ID}" --quiet
        done <<< "${dashboards}"
        log_success "Monitoring dashboards deleted"
    else
        log_info "No monitoring dashboards found"
    fi
}

# Destroy infrastructure with Terraform
cleanup_infrastructure() {
    log_info "Destroying infrastructure with Terraform..."

    if [[ -d "infrastructure/ledger" ]]; then
        cd infrastructure/ledger

        # Check if terraform state exists
        if [[ -f ".terraform/terraform.tfstate" || -f "terraform.tfstate" ]]; then
            log_info "Destroying Terraform-managed resources..."

            # Create terraform.tfvars if it doesn't exist
            if [[ ! -f "terraform.tfvars" ]]; then
                cat > terraform.tfvars <<EOF
project_id = "${PROJECT_ID}"
region = "${REGION}"
environment = "${ENVIRONMENT}"
bigtable_num_nodes = 1
enable_deletion_protection = false
monitoring_retention_days = 7
EOF
            fi

            # Destroy resources
            terraform destroy -var-file=terraform.tfvars -auto-approve
            log_success "Infrastructure destroyed"
        else
            log_warning "No Terraform state found, skipping Terraform destroy"
        fi

        cd ../..
    else
        log_warning "Infrastructure directory not found, skipping Terraform cleanup"
    fi
}

# Manual cleanup of remaining resources
manual_cleanup() {
    log_info "Performing manual cleanup of remaining resources..."

    # Delete Pub/Sub resources
    log_info "Cleaning up Pub/Sub resources..."

    # Delete subscription first
    if gcloud pubsub subscriptions describe neural-ledger-processor --project="${PROJECT_ID}" &> /dev/null; then
        gcloud pubsub subscriptions delete neural-ledger-processor --project="${PROJECT_ID}" --quiet
        log_success "Deleted Pub/Sub subscription"
    fi

    # Delete topic
    if gcloud pubsub topics describe neural-ledger-events --project="${PROJECT_ID}" &> /dev/null; then
        gcloud pubsub topics delete neural-ledger-events --project="${PROJECT_ID}" --quiet
        log_success "Deleted Pub/Sub topic"
    fi

    # Delete BigQuery dataset
    log_info "Cleaning up BigQuery resources..."
    if bq show --project_id="${PROJECT_ID}" neural_ledger &> /dev/null; then
        bq rm -r -f --project_id="${PROJECT_ID}" neural_ledger
        log_success "Deleted BigQuery dataset"
    fi

    # Delete Bigtable instance
    log_info "Cleaning up Bigtable resources..."
    if gcloud bigtable instances describe neural-ledger --project="${PROJECT_ID}" &> /dev/null; then
        gcloud bigtable instances delete neural-ledger --project="${PROJECT_ID}" --quiet
        log_success "Deleted Bigtable instance"
    fi

    # Delete Firestore indexes (collections will be cleaned up automatically)
    log_info "Cleaning up Firestore resources..."
    log_warning "Note: Firestore data must be deleted manually from the console if needed"

    # Delete KMS resources
    log_info "Cleaning up KMS resources..."
    local keyring="neural-ledger"
    if gcloud kms keyrings describe "${keyring}" --location="${REGION}" --project="${PROJECT_ID}" &> /dev/null; then
        log_warning "KMS keyring '${keyring}' found. Keys cannot be deleted, only disabled."

        # List and disable keys
        local keys
        keys=$(gcloud kms keys list --keyring="${keyring}" --location="${REGION}" --project="${PROJECT_ID}" --format="value(name)" 2>/dev/null || true)

        if [[ -n "${keys}" ]]; then
            while IFS= read -r key; do
                log_info "Disabling KMS key: ${key}"
                # Note: We can't actually disable keys via CLI easily, so just log it
                log_warning "Please manually disable KMS key in console: ${key}"
            done <<< "${keys}"
        fi
    fi

    # Delete Cloud Storage buckets (if any were created)
    log_info "Checking for Cloud Storage buckets..."
    local buckets
    buckets=$(gsutil ls -p "${PROJECT_ID}" 2>/dev/null | grep "neural-ledger\|${ENVIRONMENT}" || true)

    if [[ -n "${buckets}" ]]; then
        while IFS= read -r bucket; do
            if [[ -n "${bucket}" ]]; then
                log_info "Deleting bucket: ${bucket}"
                gsutil -m rm -r "${bucket}" 2>/dev/null || log_warning "Failed to delete bucket: ${bucket}"
            fi
        done <<< "${buckets}"
    fi
}

# Verify cleanup
verify_cleanup() {
    log_info "Verifying cleanup..."

    local issues=0

    # Check Cloud Function
    if gcloud functions describe neural-ledger-processor --region="${REGION}" --project="${PROJECT_ID}" &> /dev/null; then
        log_warning "Cloud Function still exists"
        ((issues++))
    fi

    # Check Pub/Sub topic
    if gcloud pubsub topics describe neural-ledger-events --project="${PROJECT_ID}" &> /dev/null; then
        log_warning "Pub/Sub topic still exists"
        ((issues++))
    fi

    # Check BigQuery dataset
    if bq show --project_id="${PROJECT_ID}" neural_ledger &> /dev/null; then
        log_warning "BigQuery dataset still exists"
        ((issues++))
    fi

    # Check Bigtable instance
    if gcloud bigtable instances describe neural-ledger --project="${PROJECT_ID}" &> /dev/null; then
        log_warning "Bigtable instance still exists"
        ((issues++))
    fi

    if [[ ${issues} -eq 0 ]]; then
        log_success "Cleanup verification passed - no major resources found"
    else
        log_warning "Found ${issues} resources that may need manual cleanup"
    fi
}

# Main cleanup function
main() {
    log_info "Starting Neural Ledger staging cleanup..."
    log_info "Project: ${PROJECT_ID}"
    log_info "Region: ${REGION}"
    log_info "Environment: ${ENVIRONMENT}"

    confirm_cleanup

    cleanup_functions
    cleanup_monitoring
    cleanup_infrastructure
    manual_cleanup
    verify_cleanup

    log_success "Neural Ledger staging cleanup completed!"

    echo ""
    log_info "Cleanup Summary:"
    echo "  - Deleted Cloud Functions"
    echo "  - Deleted monitoring dashboards"
    echo "  - Destroyed Terraform infrastructure"
    echo "  - Cleaned up Pub/Sub, BigQuery, and Bigtable resources"
    echo ""
    log_warning "Note: Some resources like KMS keys cannot be deleted and must be disabled manually"
    log_info "Check the GCP console to verify all resources have been cleaned up"
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
