#!/bin/bash
# Grant production permissions to GitHub Actions service account

SERVICE_ACCOUNT="github-actions@neurascale.iam.gserviceaccount.com"
PRODUCTION_PROJECT="production-neurascale"

echo "Granting permissions to $SERVICE_ACCOUNT on $PRODUCTION_PROJECT"

# Grant Artifact Registry Writer role (for Docker push)
gcloud projects add-iam-policy-binding $PRODUCTION_PROJECT \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/artifactregistry.writer"

echo "✓ Granted Artifact Registry Writer role"