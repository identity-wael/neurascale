#!/bin/bash
# Emergency fix - create Artifact Registry in neurascale project

PROJECT="neurascale"
REGION="northamerica-northeast1"
REPO="neural-engine-development"

echo "Creating Artifact Registry repository in $PROJECT project..."

# This uses YOUR local gcloud auth
gcloud artifacts repositories create $REPO \
  --repository-format=docker \
  --location=$REGION \
  --project=$PROJECT \
  --description="Neural Engine Docker images" 2>/dev/null || echo "Repository may already exist"

echo ""
echo "Setting up authentication..."
gcloud auth configure-docker $REGION-docker.pkg.dev

echo ""
echo "Done. The service account github-actions@neurascale.iam.gserviceaccount.com"
echo "should now be able to push to $REGION-docker.pkg.dev/$PROJECT/$REPO"
