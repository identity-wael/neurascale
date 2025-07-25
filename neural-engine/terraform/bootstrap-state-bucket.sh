#!/bin/bash

# Bootstrap script to create Terraform state bucket
# This must be run before using Terraform with GCS backend

set -euo pipefail

# Configuration
BUCKET_NAME="neurascale-terraform-state"
LOCATION="NORTHAMERICA-NORTHEAST1"
PROJECT_ID="${1:-}"

if [ -z "$PROJECT_ID" ]; then
    echo "Usage: $0 <PROJECT_ID>"
    echo "Example: $0 production-neurascale"
    exit 1
fi

echo "Bootstrapping Terraform state bucket for project: $PROJECT_ID"

# Check if bucket already exists
if gsutil ls -b gs://${BUCKET_NAME} 2>/dev/null; then
    echo "✓ Bucket gs://${BUCKET_NAME} already exists"
else
    echo "Creating bucket gs://${BUCKET_NAME}..."
    gsutil mb -p ${PROJECT_ID} -l ${LOCATION} -b on gs://${BUCKET_NAME}

    # Enable versioning
    gsutil versioning set on gs://${BUCKET_NAME}

    # Set lifecycle rule to delete old versions
    cat > /tmp/lifecycle.json <<EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "numNewerVersions": 5,
          "age": 30
        }
      }
    ]
  }
}
EOF

    gsutil lifecycle set /tmp/lifecycle.json gs://${BUCKET_NAME}
    rm /tmp/lifecycle.json

    # Enable uniform bucket-level access
    gsutil ubla set on gs://${BUCKET_NAME}

    echo "✓ Bucket created successfully"
fi

# Grant access to GitHub Actions service account
GITHUB_SA="github-actions@neurascale.iam.gserviceaccount.com"
echo "Granting storage.objectAdmin role to ${GITHUB_SA}..."
gsutil iam ch serviceAccount:${GITHUB_SA}:objectAdmin gs://${BUCKET_NAME}

echo "✓ State bucket bootstrap complete!"
echo ""
echo "You can now use Terraform with the GCS backend:"
echo "  terraform init -backend-config=\"bucket=${BUCKET_NAME}\" -backend-config=\"prefix=neural-engine/\${ENVIRONMENT}\""
