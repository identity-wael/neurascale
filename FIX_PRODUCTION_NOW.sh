#!/bin/bash
# EMERGENCY FIX FOR PRODUCTION 403 ERRORS

echo "PRODUCTION IS BROKEN BECAUSE:"
echo "- Service account: github-actions@neurascale.iam.gserviceaccount.com"
echo "- Needs permission to push to: development-neurascale project"
echo ""
echo "RUN THIS COMMAND WITH GCLOUD AUTH:"
echo ""
echo "gcloud projects add-iam-policy-binding development-neurascale \\"
echo "  --member='serviceAccount:github-actions@neurascale.iam.gserviceaccount.com' \\"
echo "  --role='roles/artifactregistry.writer'"
echo ""
echo "This grants cross-project access for the service account to push images."
