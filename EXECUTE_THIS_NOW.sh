#!/bin/bash
# EXECUTE THIS TO FIX PRODUCTION IMMEDIATELY

echo "=== FIXING PRODUCTION 403 ERRORS ==="
echo ""
echo "Running gcloud command to grant permissions..."

gcloud projects add-iam-policy-binding development-neurascale \
  --member='serviceAccount:github-actions@neurascale.iam.gserviceaccount.com' \
  --role='roles/artifactregistry.writer'

echo ""
echo "Checking if permission was granted..."
gcloud projects get-iam-policy development-neurascale \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:github-actions@neurascale.iam.gserviceaccount.com" \
  --format="table(bindings.role)"

echo ""
echo "Production should now be fixed. Trigger a new build to verify."
