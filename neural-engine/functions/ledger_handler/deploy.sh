#!/bin/bash
# Deploy the Neural Ledger Cloud Function

PROJECT_ID=${PROJECT_ID:-neurascale-production}
REGION=${REGION:-northamerica-northeast1}
FUNCTION_NAME="ledger-event-processor"
TOPIC_NAME="neural-ledger-events"

echo "Deploying Neural Ledger Cloud Function..."
echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo "Function: $FUNCTION_NAME"
echo "Topic: $TOPIC_NAME"

# Deploy the function
gcloud functions deploy $FUNCTION_NAME \
  --gen2 \
  --runtime=python311 \
  --region=$REGION \
  --source=. \
  --entry-point=process_ledger_event \
  --trigger-topic=$TOPIC_NAME \
  --service-account=ledger-processor@$PROJECT_ID.iam.gserviceaccount.com \
  --set-env-vars="GCP_PROJECT=$PROJECT_ID,GCP_LOCATION=$REGION" \
  --memory=512MB \
  --timeout=60s \
  --max-instances=100 \
  --min-instances=1 \
  --ingress-settings=internal-only \
  --set-secrets="LEDGER_KMS_KEY=neural-ledger-kms-key:latest"

# Deploy health check endpoint
gcloud functions deploy "${FUNCTION_NAME}-health" \
  --gen2 \
  --runtime=python311 \
  --region=$REGION \
  --source=. \
  --entry-point=health_check \
  --trigger-http \
  --allow-unauthenticated \
  --service-account=ledger-processor@$PROJECT_ID.iam.gserviceaccount.com \
  --set-env-vars="GCP_PROJECT=$PROJECT_ID,GCP_LOCATION=$REGION" \
  --memory=256MB \
  --timeout=10s \
  --max-instances=10

echo "Deployment complete!"
