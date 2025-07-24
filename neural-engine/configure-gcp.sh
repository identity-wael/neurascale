#!/bin/bash
set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Error: PROJECT_ID not set. Please update .env file."
    exit 1
fi

echo "🔧 Configuring Google Cloud for project: $PROJECT_ID"

# Set project
gcloud config set project $PROJECT_ID

echo "📡 Enabling required APIs..."
gcloud services enable compute.googleapis.com
gcloud services enable container.googleapis.com
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable pubsub.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable bigtable.googleapis.com
gcloud services enable dataflow.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable cloudiot.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable cloudbuild.googleapis.com

echo "🔐 Creating service account..."
gcloud iam service-accounts create neurascale-dev \
    --display-name="NeuraScale Development" \
    --description="Service account for Neural Engine development" \
    || echo "Service account already exists"

# Grant necessary roles
echo "🔑 Assigning IAM roles..."
SERVICE_ACCOUNT="neurascale-dev@${PROJECT_ID}.iam.gserviceaccount.com"

roles=(
    "roles/pubsub.editor"
    "roles/datastore.user"
    "roles/bigquery.dataEditor"
    "roles/bigtable.admin"
    "roles/storage.admin"
    "roles/dataflow.developer"
    "roles/cloudfunctions.developer"
    "roles/cloudiot.editor"
    "roles/monitoring.metricWriter"
    "roles/logging.logWriter"
)

for role in "${roles[@]}"; do
    echo "Granting $role..."
    gcloud projects add-iam-policy-binding $PROJECT_ID \
        --member="serviceAccount:$SERVICE_ACCOUNT" \
        --role="$role" \
        --quiet
done

# Create key if it doesn't exist
if [ ! -f key.json ]; then
    echo "🔐 Creating service account key..."
    gcloud iam service-accounts keys create key.json \
        --iam-account=$SERVICE_ACCOUNT
    echo "✅ Service account key created: key.json"
else
    echo "ℹ️  Service account key already exists: key.json"
fi

# Create Cloud Storage buckets
echo "🪣 Creating Cloud Storage buckets..."
gsutil mb -p $PROJECT_ID -l $REGION gs://${PROJECT_ID}-neural-data || echo "Bucket already exists"
gsutil mb -p $PROJECT_ID -l $REGION gs://${PROJECT_ID}-models || echo "Bucket already exists"
gsutil mb -p $PROJECT_ID -l $REGION gs://${PROJECT_ID}-temp || echo "Bucket already exists"

# Create Pub/Sub topics
echo "📨 Creating Pub/Sub topics..."
topics=(
    "neural-signals-eeg"
    "neural-signals-ecog"
    "neural-signals-spikes"
    "neural-signals-lfp"
    "neural-signals-emg"
    "neural-signals-accelerometer"
    "decoded-movements"
    "system-metrics"
)

for topic in "${topics[@]}"; do
    gcloud pubsub topics create $topic --quiet || echo "Topic $topic already exists"
done

# Create BigQuery dataset
echo "📊 Creating BigQuery datasets..."
bq mk --dataset --location=$REGION --description="Neural signal features" ${PROJECT_ID}:neural_features || echo "Dataset already exists"
bq mk --dataset --location=$REGION --description="Decoded movements" ${PROJECT_ID}:decoded_movements || echo "Dataset already exists"
bq mk --dataset --location=$REGION --description="System metrics" ${PROJECT_ID}:system_metrics || echo "Dataset already exists"

# Create Bigtable instance (commented out due to cost)
echo "📋 Bigtable instance creation skipped (uncomment to create)..."
# gcloud bigtable instances create neural-timeseries \
#     --display-name="Neural Time Series Data" \
#     --cluster-config=id=neural-cluster,zone=$ZONE,nodes=1 \
#     || echo "Bigtable instance already exists"

# Set up Firestore
echo "🔥 Setting up Firestore..."
gcloud firestore databases create --region=$REGION --quiet || echo "Firestore already exists"

echo "✅ Google Cloud configuration complete!"
echo ""
echo "📋 Summary:"
echo "  - Project: $PROJECT_ID"
echo "  - Region: $REGION"
echo "  - Service Account: $SERVICE_ACCOUNT"
echo "  - Key File: key.json"
echo ""
echo "🚀 You're ready to start developing!"
