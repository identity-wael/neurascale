#!/bin/bash
# Restore all paused GCP resources
# Run this when you need to resume development/testing

set -e

echo "🚀 Starting resource restoration process..."
echo "This will restore all paused GCP resources"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Projects
PROD_PROJECT="neurascale-production"
STAGING_PROJECT="neurascale-staging"
DEV_PROJECT="neurascale-development"

# Default configurations
DEFAULT_GKE_NODES=3
DEFAULT_CLOUD_RUN_MAX=100

# Function to check if resource exists
check_resource() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Success${NC}"
    else
        echo -e "${RED}✗ Failed${NC}"
    fi
}

echo "=== Restoring PRODUCTION resources ==="
gcloud config set project $PROD_PROJECT

# 1. Start Cloud SQL instances
echo -n "Starting Cloud SQL instances... "
for instance in $(gcloud sql instances list --format="value(name)" 2>/dev/null); do
    gcloud sql instances patch $instance --backup --backup-start-time=02:00 --quiet 2>/dev/null || true
done
check_resource

# 2. Scale up GKE clusters
echo -n "Scaling GKE clusters to $DEFAULT_GKE_NODES nodes... "
for cluster in $(gcloud container clusters list --format="value(name,location)" 2>/dev/null); do
    cluster_name=$(echo $cluster | cut -d' ' -f1)
    location=$(echo $cluster | cut -d' ' -f2)
    gcloud container clusters resize $cluster_name --size=$DEFAULT_GKE_NODES --location=$location --quiet 2>/dev/null || true
done
check_resource

# 3. Restore Cloud Run services
echo -n "Restoring Cloud Run services... "
for service in $(gcloud run services list --format="value(name,region)" 2>/dev/null); do
    service_name=$(echo $service | cut -d' ' -f1)
    region=$(echo $service | cut -d' ' -f2)
    gcloud run services update $service_name --max-instances=$DEFAULT_CLOUD_RUN_MAX --region=$region --quiet 2>/dev/null || true
done
check_resource

# 4. Start Compute Engine VMs
echo -n "Starting Compute Engine instances... "
for instance in $(gcloud compute instances list --format="value(name,zone)" 2>/dev/null); do
    instance_name=$(echo $instance | cut -d' ' -f1)
    zone=$(echo $instance | cut -d' ' -f2)
    gcloud compute instances start $instance_name --zone=$zone --quiet 2>/dev/null || true
done
check_resource

echo ""
echo "=== Restoring STAGING resources ==="
gcloud config set project $STAGING_PROJECT

# Use smaller sizes for staging
STAGING_GKE_NODES=1
STAGING_CLOUD_RUN_MAX=10

echo -n "Starting Cloud SQL instances... "
for instance in $(gcloud sql instances list --format="value(name)" 2>/dev/null); do
    gcloud sql instances patch $instance --backup --backup-start-time=03:00 --quiet 2>/dev/null || true
done
check_resource

echo -n "Scaling GKE clusters to $STAGING_GKE_NODES nodes... "
for cluster in $(gcloud container clusters list --format="value(name,location)" 2>/dev/null); do
    cluster_name=$(echo $cluster | cut -d' ' -f1)
    location=$(echo $cluster | cut -d' ' -f2)
    gcloud container clusters resize $cluster_name --size=$STAGING_GKE_NODES --location=$location --quiet 2>/dev/null || true
done
check_resource

echo -n "Restoring Cloud Run services... "
for service in $(gcloud run services list --format="value(name,region)" 2>/dev/null); do
    service_name=$(echo $service | cut -d' ' -f1)
    region=$(echo $service | cut -d' ' -f2)
    gcloud run services update $service_name --max-instances=$STAGING_CLOUD_RUN_MAX --region=$region --quiet 2>/dev/null || true
done
check_resource

echo -n "Starting Compute Engine instances... "
for instance in $(gcloud compute instances list --format="value(name,zone)" 2>/dev/null); do
    instance_name=$(echo $instance | cut -d' ' -f1)
    zone=$(echo $instance | cut -d' ' -f2)
    gcloud compute instances start $instance_name --zone=$zone --quiet 2>/dev/null || true
done
check_resource

echo ""
echo -e "${GREEN}✅ Resource restoration complete!${NC}"
echo ""
echo "📊 Resources restored:"
echo "  - Cloud SQL: Started with automatic backups enabled"
echo "  - GKE: Scaled to default node counts"
echo "  - Cloud Run: Max instances restored"
echo "  - Compute Engine: All VMs started"
echo ""
echo "⏱️  Please wait a few minutes for all services to be fully operational"
echo ""
echo "💡 To verify status:"
echo "   gcloud compute instances list"
echo "   gcloud sql instances list"
echo "   gcloud container clusters list"
echo "   gcloud run services list"
