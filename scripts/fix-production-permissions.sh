#!/bin/bash
# Script to fix GitHub Actions permissions for production deployment

# The service account that needs permissions
SERVICE_ACCOUNT="github-actions@neurascale.iam.gserviceaccount.com"

# Production project
PRODUCTION_PROJECT="production-neurascale"

echo "This script documents the permissions needed for production deployment."
echo "Run these commands with appropriate permissions:"
echo ""

echo "# 1. Grant Artifact Registry Writer role for Docker image push"
echo "gcloud projects add-iam-policy-binding $PRODUCTION_PROJECT \\"
echo "  --member=serviceAccount:$SERVICE_ACCOUNT \\"
echo "  --role=roles/artifactregistry.writer"
echo ""

echo "# 2. Grant Cloud Run Developer role for service deployment"
echo "gcloud projects add-iam-policy-binding $PRODUCTION_PROJECT \\"
echo "  --member=serviceAccount:$SERVICE_ACCOUNT \\"
echo "  --role=roles/run.developer"
echo ""

echo "# 3. Grant Service Account User role to act as service accounts"
echo "gcloud projects add-iam-policy-binding $PRODUCTION_PROJECT \\"
echo "  --member=serviceAccount:$SERVICE_ACCOUNT \\"
echo "  --role=roles/iam.serviceAccountUser"
echo ""

echo "# 4. Grant Cloud Functions Developer role"
echo "gcloud projects add-iam-policy-binding $PRODUCTION_PROJECT \\"
echo "  --member=serviceAccount:$SERVICE_ACCOUNT \\"
echo "  --role=roles/cloudfunctions.developer"
echo ""

echo "# 5. Grant Storage Admin role for Terraform state"
echo "gcloud projects add-iam-policy-binding $PRODUCTION_PROJECT \\"
echo "  --member=serviceAccount:$SERVICE_ACCOUNT \\"
echo "  --role=roles/storage.admin"
echo ""

echo "# 6. Grant required roles for Terraform resources"
echo "gcloud projects add-iam-policy-binding $PRODUCTION_PROJECT \\"
echo "  --member=serviceAccount:$SERVICE_ACCOUNT \\"
echo "  --role=roles/bigtable.admin"
echo ""

echo "gcloud projects add-iam-policy-binding $PRODUCTION_PROJECT \\"
echo "  --member=serviceAccount:$SERVICE_ACCOUNT \\"
echo "  --role=roles/pubsub.admin"
echo ""

echo "gcloud projects add-iam-policy-binding $PRODUCTION_PROJECT \\"
echo "  --member=serviceAccount:$SERVICE_ACCOUNT \\"
echo "  --role=roles/logging.admin"
echo ""

echo "gcloud projects add-iam-policy-binding $PRODUCTION_PROJECT \\"
echo "  --member=serviceAccount:$SERVICE_ACCOUNT \\"
echo "  --role=roles/monitoring.metricWriter"
echo ""

echo "# Alternative: Grant Project Editor role (broader permissions)"
echo "# gcloud projects add-iam-policy-binding $PRODUCTION_PROJECT \\"
echo "#   --member=serviceAccount:$SERVICE_ACCOUNT \\"
echo "#   --role=roles/editor"