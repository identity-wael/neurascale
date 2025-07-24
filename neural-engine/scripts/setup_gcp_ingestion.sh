#!/bin/bash
# Setup script for Google Cloud ingestion infrastructure

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=${GCP_PROJECT_ID:-"neurascale"}
REGION=${GCP_REGION:-"us-central1"}
INSTANCE_ID="neural-data"
TABLE_ID="time-series"

echo -e "${BLUE}Setting up Neural Data Ingestion Infrastructure${NC}"
echo -e "Project: ${PROJECT_ID}"
echo -e "Region: ${REGION}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed${NC}"
    exit 1
fi

# Set the project
echo -e "\n${BLUE}Setting project...${NC}"
gcloud config set project ${PROJECT_ID}

# Enable required APIs
echo -e "\n${BLUE}Enabling required APIs...${NC}"
gcloud services enable \
    pubsub.googleapis.com \
    bigtable.googleapis.com \
    bigtableadmin.googleapis.com \
    cloudfunctions.googleapis.com \
    cloudbuild.googleapis.com \
    artifactregistry.googleapis.com \
    run.googleapis.com \
    logging.googleapis.com \
    monitoring.googleapis.com

# Create Pub/Sub topics for each signal type
echo -e "\n${BLUE}Creating Pub/Sub topics...${NC}"
SIGNAL_TYPES=("eeg" "ecog" "spikes" "lfp" "emg" "accelerometer" "custom")

for signal_type in "${SIGNAL_TYPES[@]}"; do
    topic_name="neural-data-${signal_type}"

    if gcloud pubsub topics describe ${topic_name} --project=${PROJECT_ID} &>/dev/null; then
        echo -e "${YELLOW}Topic ${topic_name} already exists${NC}"
    else
        gcloud pubsub topics create ${topic_name} \
            --project=${PROJECT_ID} \
            --message-retention-duration=7d
        echo -e "${GREEN}Created topic: ${topic_name}${NC}"
    fi

    # Create subscription for each topic
    subscription_name="${topic_name}-sub"
    if gcloud pubsub subscriptions describe ${subscription_name} --project=${PROJECT_ID} &>/dev/null; then
        echo -e "${YELLOW}Subscription ${subscription_name} already exists${NC}"
    else
        gcloud pubsub subscriptions create ${subscription_name} \
            --topic=${topic_name} \
            --project=${PROJECT_ID} \
            --ack-deadline=60 \
            --message-retention-duration=1d
        echo -e "${GREEN}Created subscription: ${subscription_name}${NC}"
    fi
done

# Create Bigtable instance
echo -e "\n${BLUE}Creating Bigtable instance...${NC}"
if gcloud bigtable instances describe ${INSTANCE_ID} --project=${PROJECT_ID} &>/dev/null; then
    echo -e "${YELLOW}Bigtable instance ${INSTANCE_ID} already exists${NC}"
else
    gcloud bigtable instances create ${INSTANCE_ID} \
        --project=${PROJECT_ID} \
        --cluster=${INSTANCE_ID}-cluster \
        --cluster-zone=${REGION}-a \
        --display-name="Neural Data Time Series" \
        --cluster-num-nodes=1 \
        --instance-type=DEVELOPMENT
    echo -e "${GREEN}Created Bigtable instance: ${INSTANCE_ID}${NC}"
fi

# Create Bigtable table
echo -e "\n${BLUE}Creating Bigtable table...${NC}"
if gcloud bigtable tables describe ${TABLE_ID} --instance=${INSTANCE_ID} --project=${PROJECT_ID} &>/dev/null; then
    echo -e "${YELLOW}Bigtable table ${TABLE_ID} already exists${NC}"
else
    # Create table with cbt command
    echo "Creating table ${TABLE_ID}..."
    cbt -project=${PROJECT_ID} -instance=${INSTANCE_ID} createtable ${TABLE_ID}

    # Create column families
    echo "Creating column families..."
    cbt -project=${PROJECT_ID} -instance=${INSTANCE_ID} createfamily ${TABLE_ID} metadata
    cbt -project=${PROJECT_ID} -instance=${INSTANCE_ID} createfamily ${TABLE_ID} data

    # Set garbage collection policies
    echo "Setting garbage collection policies..."
    cbt -project=${PROJECT_ID} -instance=${INSTANCE_ID} setgcpolicy ${TABLE_ID} metadata maxversions=1
    cbt -project=${PROJECT_ID} -instance=${INSTANCE_ID} setgcpolicy ${TABLE_ID} data maxversions=1 maxage=30d

    echo -e "${GREEN}Created Bigtable table: ${TABLE_ID}${NC}"
fi

# Create service account for Cloud Functions
echo -e "\n${BLUE}Creating service account...${NC}"
SERVICE_ACCOUNT_NAME="neural-ingestion-sa"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

if gcloud iam service-accounts describe ${SERVICE_ACCOUNT_EMAIL} --project=${PROJECT_ID} &>/dev/null; then
    echo -e "${YELLOW}Service account ${SERVICE_ACCOUNT_EMAIL} already exists${NC}"
else
    gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME} \
        --display-name="Neural Data Ingestion Service Account" \
        --project=${PROJECT_ID}
    echo -e "${GREEN}Created service account: ${SERVICE_ACCOUNT_EMAIL}${NC}"
fi

# Grant necessary permissions
echo -e "\n${BLUE}Granting permissions...${NC}"
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/pubsub.publisher" \
    --condition=None

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/pubsub.subscriber" \
    --condition=None

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/bigtable.user" \
    --condition=None

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/logging.logWriter" \
    --condition=None

# Deploy Cloud Function
echo -e "\n${BLUE}Deploying Cloud Function...${NC}"
cd functions/stream_ingestion

# Deploy Pub/Sub triggered function
gcloud functions deploy process-neural-stream \
    --gen2 \
    --runtime=python312 \
    --region=${REGION} \
    --source=. \
    --entry-point=process_neural_stream \
    --trigger-topic=neural-data-eeg \
    --memory=1GB \
    --timeout=60s \
    --max-instances=100 \
    --service-account=${SERVICE_ACCOUNT_EMAIL} \
    --set-env-vars="GCP_PROJECT=${PROJECT_ID}"

# Deploy HTTP endpoint for batch ingestion
gcloud functions deploy ingest-neural-batch \
    --gen2 \
    --runtime=python312 \
    --region=${REGION} \
    --source=. \
    --entry-point=ingest_batch \
    --trigger-http \
    --allow-unauthenticated \
    --memory=2GB \
    --timeout=300s \
    --max-instances=50 \
    --service-account=${SERVICE_ACCOUNT_EMAIL} \
    --set-env-vars="GCP_PROJECT=${PROJECT_ID}"

cd ../..

echo -e "\n${GREEN}✅ Neural Data Ingestion Infrastructure Setup Complete!${NC}"
echo -e "\nResources created:"
echo -e "- Pub/Sub topics: neural-data-{eeg,ecog,spikes,lfp,emg,accelerometer,custom}"
echo -e "- Bigtable instance: ${INSTANCE_ID}"
echo -e "- Bigtable table: ${TABLE_ID}"
echo -e "- Service account: ${SERVICE_ACCOUNT_EMAIL}"
echo -e "- Cloud Functions: process-neural-stream, ingest-neural-batch"

echo -e "\n${BLUE}Next steps:${NC}"
echo -e "1. Test the ingestion system with: python examples/ingestion_example.py"
echo -e "2. Send test data to Pub/Sub: gcloud pubsub topics publish neural-data-eeg --message='{...}'"
echo -e "3. View logs: gcloud functions logs read process-neural-stream"
