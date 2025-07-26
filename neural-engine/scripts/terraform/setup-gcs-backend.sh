#!/bin/bash

# Script to create GCS bucket for Terraform state storage
# This bucket will be created in the orchestration project (neurascale)

set -e

ORCHESTRATION_PROJECT="neurascale"
BUCKET_NAME="neurascale-terraform-state"
REGION="northamerica-northeast1"

echo "Setting up GCS backend for Terraform state..."

# Check if bucket already exists
if gsutil ls -b gs://${BUCKET_NAME} &>/dev/null; then
    echo "Bucket gs://${BUCKET_NAME} already exists"
else
    echo "Creating bucket gs://${BUCKET_NAME}..."
    gsutil mb -p ${ORCHESTRATION_PROJECT} -c STANDARD -l ${REGION} -b on gs://${BUCKET_NAME}

    # Enable versioning for state file protection
    gsutil versioning set on gs://${BUCKET_NAME}

    # Set lifecycle rule to delete old versions after 30 days
    cat > /tmp/lifecycle.json <<EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "age": 30,
          "isLive": false
        }
      }
    ]
  }
}
EOF

    gsutil lifecycle set /tmp/lifecycle.json gs://${BUCKET_NAME}
    rm -f /tmp/lifecycle.json

    echo "Bucket created successfully"
fi

echo "GCS backend setup complete!"
echo ""
echo "To use this backend, run:"
echo "  terraform init -backend-config=\"bucket=${BUCKET_NAME}\""
