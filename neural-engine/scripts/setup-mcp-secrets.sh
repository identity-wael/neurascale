#!/bin/bash
"""
Setup script for MCP server secrets in GCP Secret Manager.

This script creates the required secrets for the MCP server authentication
system using GCP Secret Manager for secure credential storage.
"""

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

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

# Check if GCP project ID is set
check_gcp_project() {
    if [[ -z "${GCP_PROJECT_ID}" ]]; then
        log_error "GCP_PROJECT_ID environment variable is not set"
        log_info "Please set GCP_PROJECT_ID to your Google Cloud project ID"
        log_info "Example: export GCP_PROJECT_ID=your-project-id"
        exit 1
    fi
    
    log_info "Using GCP Project ID: ${GCP_PROJECT_ID}"
}

# Check if gcloud CLI is installed and authenticated
check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI is not installed"
        log_info "Please install the Google Cloud CLI: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    
    # Check if authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1 &> /dev/null; then
        log_error "gcloud CLI is not authenticated"
        log_info "Please authenticate with: gcloud auth login"
        exit 1
    fi
    
    # Set the project
    gcloud config set project "${GCP_PROJECT_ID}" &> /dev/null
    log_success "gcloud CLI is ready"
}

# Enable required GCP APIs
enable_apis() {
    log_info "Enabling required GCP APIs..."
    
    local apis=("secretmanager.googleapis.com")
    
    for api in "${apis[@]}"; do
        log_info "Enabling ${api}..."
        if gcloud services enable "${api}" --quiet; then
            log_success "Enabled ${api}"
        else
            log_error "Failed to enable ${api}"
            exit 1
        fi
    done
}

# Generate secure random string
generate_secret() {
    local length=$1
    openssl rand -base64 $((length * 3 / 4)) | tr -d "=+/" | cut -c1-${length}
}

# Create a secret in Secret Manager
create_secret() {
    local secret_name=$1
    local secret_value=$2
    
    log_info "Creating secret: ${secret_name}"
    
    # Create the secret
    if gcloud secrets create "${secret_name}" \
        --replication-policy="automatic" \
        --project="${GCP_PROJECT_ID}" \
        --quiet 2>/dev/null; then
        log_success "Created secret: ${secret_name}"
    else
        # Check if secret already exists
        if gcloud secrets describe "${secret_name}" --project="${GCP_PROJECT_ID}" &>/dev/null; then
            log_warning "Secret ${secret_name} already exists, updating with new version"
        else
            log_error "Failed to create secret: ${secret_name}"
            return 1
        fi
    fi
    
    # Add the secret version
    if echo -n "${secret_value}" | gcloud secrets versions add "${secret_name}" \
        --data-file=- \
        --project="${GCP_PROJECT_ID}" \
        --quiet; then
        log_success "Added version to secret: ${secret_name}"
    else
        log_error "Failed to add version to secret: ${secret_name}"
        return 1
    fi
}

# Create all required MCP secrets
create_mcp_secrets() {
    log_info "Creating MCP server secrets..."
    
    # Generate secure values
    local api_key_salt
    local jwt_secret
    
    api_key_salt=$(generate_secret 32)
    jwt_secret=$(generate_secret 64)
    
    # Create secrets
    create_secret "mcp-api-key-salt" "${api_key_salt}" || exit 1
    create_secret "mcp-jwt-secret" "${jwt_secret}" || exit 1
    
    log_success "All MCP secrets created successfully"
}

# Set up IAM permissions for the MCP service
setup_iam_permissions() {
    log_info "Setting up IAM permissions for MCP service..."
    
    # Get the compute service account (used by GCP services)
    local compute_sa="${GCP_PROJECT_ID}-compute@developer.gserviceaccount.com"
    
    # Grant Secret Manager accessor role
    if gcloud projects add-iam-policy-binding "${GCP_PROJECT_ID}" \
        --member="serviceAccount:${compute_sa}" \
        --role="roles/secretmanager.secretAccessor" \
        --quiet; then
        log_success "Granted Secret Manager access to compute service account"
    else
        log_warning "Failed to grant IAM permissions (may already exist)"
    fi
    
    # If App Engine service account exists, grant it access too
    local appengine_sa="${GCP_PROJECT_ID}@appspot.gserviceaccount.com"
    if gcloud iam service-accounts describe "${appengine_sa}" --project="${GCP_PROJECT_ID}" &>/dev/null; then
        if gcloud projects add-iam-policy-binding "${GCP_PROJECT_ID}" \
            --member="serviceAccount:${appengine_sa}" \
            --role="roles/secretmanager.secretAccessor" \
            --quiet; then
            log_success "Granted Secret Manager access to App Engine service account"
        fi
    fi
}

# Verify secrets are accessible
verify_secrets() {
    log_info "Verifying secrets are accessible..."
    
    local secrets=("mcp-api-key-salt" "mcp-jwt-secret")
    
    for secret in "${secrets[@]}"; do
        if gcloud secrets versions access latest \
            --secret="${secret}" \
            --project="${GCP_PROJECT_ID}" \
            --quiet > /dev/null; then
            log_success "Secret ${secret} is accessible"
        else
            log_error "Secret ${secret} is not accessible"
            exit 1
        fi
    done
}

# Display next steps
show_next_steps() {
    log_success "MCP secrets setup completed successfully!"
    echo
    log_info "Next steps:"
    echo "1. Set the GCP_PROJECT_ID environment variable in your deployment environment"
    echo "2. Ensure your MCP server has the necessary IAM permissions to access Secret Manager"
    echo "3. Deploy your MCP server with the updated configuration"
    echo
    log_info "Environment variable to set:"
    echo "export GCP_PROJECT_ID=${GCP_PROJECT_ID}"
    echo
    log_info "Secrets created:"
    echo "- mcp-api-key-salt"
    echo "- mcp-jwt-secret"
}

# Main function
main() {
    log_info "Setting up MCP server secrets in GCP Secret Manager..."
    echo
    
    # Check prerequisites
    check_gcp_project
    check_gcloud
    
    # Enable APIs
    enable_apis
    
    # Create secrets
    create_mcp_secrets
    
    # Setup IAM
    setup_iam_permissions
    
    # Verify
    verify_secrets
    
    # Show next steps
    show_next_steps
    
    log_success "Setup completed successfully!"
}

# Help function
show_help() {
    echo "MCP Secrets Setup Script"
    echo
    echo "This script sets up the required secrets for the MCP server in GCP Secret Manager."
    echo
    echo "Prerequisites:"
    echo "- Google Cloud CLI (gcloud) installed and authenticated"
    echo "- GCP_PROJECT_ID environment variable set"
    echo "- Appropriate permissions to create secrets and modify IAM"
    echo
    echo "Usage:"
    echo "  $0                    Set up MCP secrets"
    echo "  $0 --help           Show this help message"
    echo
    echo "Environment variables:"
    echo "  GCP_PROJECT_ID       Your Google Cloud project ID (required)"
    echo
    echo "Examples:"
    echo "  export GCP_PROJECT_ID=my-neurascale-project"
    echo "  $0"
}

# Parse command line arguments
case "${1:-}" in
    --help|-h)
        show_help
        exit 0
        ;;
    "")
        main
        ;;
    *)
        log_error "Unknown option: $1"
        show_help
        exit 1
        ;;
esac