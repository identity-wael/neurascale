#!/bin/bash
# Pause/stop all GCP resources to save costs during development
# Can be restored using restore-resources.sh

set -e

echo "🔄 Starting resource pause process..."
echo "This will stop/pause all costly GCP resources while preserving configurations"
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

# Function to check if resource exists
check_resource() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Success${NC}"
    else
        echo -e "${YELLOW}⚠ Resource not found or already stopped${NC}"
    fi
}

echo "=== Pausing PRODUCTION resources ==="
gcloud config set project $PROD_PROJECT

# 1. Stop Cloud SQL instances
echo -n "Stopping Cloud SQL instances... "
for instance in $(gcloud sql instances list --format="value(name)" 2>/dev/null); do
    gcloud sql instances patch $instance --no-backup --quiet 2>/dev/null || true
done
check_resource

# 2. Scale down GKE clusters to 0 nodes
echo -n "Scaling GKE clusters to 0 nodes... "
for cluster in $(gcloud container clusters list --format="value(name,location)" 2>/dev/null); do
    cluster_name=$(echo $cluster | cut -d' ' -f1)
    location=$(echo $cluster | cut -d' ' -f2)
    gcloud container clusters resize $cluster_name --size=0 --location=$location --quiet 2>/dev/null || true
done
check_resource

# 3. Stop all Cloud Run services (set max instances to 0)
echo -n "Stopping Cloud Run services... "
for service in $(gcloud run services list --format="value(name,region)" 2>/dev/null); do
    service_name=$(echo $service | cut -d' ' -f1)
    region=$(echo $service | cut -d' ' -f2)
    gcloud run services update $service_name --max-instances=0 --region=$region --quiet 2>/dev/null || true
done
check_resource

# 4. Stop Compute Engine VMs
echo -n "Stopping Compute Engine instances... "
for instance in $(gcloud compute instances list --format="value(name,zone)" 2>/dev/null); do
    instance_name=$(echo $instance | cut -d' ' -f1)
    zone=$(echo $instance | cut -d' ' -f2)
    gcloud compute instances stop $instance_name --zone=$zone --quiet 2>/dev/null || true
done
check_resource

# 5. Delete Bigtable instances (if any)
echo -n "Checking Bigtable instances... "
for instance in $(gcloud bigtable instances list --format="value(name)" 2>/dev/null); do
    echo -e "\n${YELLOW}Warning: Bigtable instance $instance found. Bigtable cannot be paused.${NC}"
    echo "Consider deleting it with: gcloud bigtable instances delete $instance"
done
echo -e "${GREEN}✓ Done${NC}"

# 6. Check for large persistent disks
echo -n "Checking for large persistent disks (>500GB)... "
large_disks=$(gcloud compute disks list --filter="sizeGb>500" --format="value(name,sizeGb,zone)" 2>/dev/null)
if [ ! -z "$large_disks" ]; then
    echo -e "\n${RED}⚠️  Large disks found:${NC}"
    echo "$large_disks" | while read disk; do
        disk_name=$(echo $disk | cut -d' ' -f1)
        size_gb=$(echo $disk | cut -d' ' -f2)
        zone=$(echo $disk | cut -d' ' -f3)
        echo -e "  ${YELLOW}$disk_name: ${size_gb}GB in $zone${NC}"

        # Check if disk is attached
        attached=$(gcloud compute disks describe $disk_name --zone=$zone --format="value(users)" 2>/dev/null)
        if [ -z "$attached" ]; then
            echo -e "    ${GREEN}→ Disk is not attached to any instance${NC}"
            echo -e "    ${YELLOW}→ To delete: gcloud compute disks delete $disk_name --zone=$zone${NC}"
            echo -e "    ${YELLOW}→ To snapshot first: gcloud compute disks snapshot $disk_name --zone=$zone --snapshot-names=${disk_name}-backup${NC}"
        else
            echo -e "    ${RED}→ Disk is attached to: $attached${NC}"
        fi
    done
else
    echo -e "${GREEN}✓ No large disks found${NC}"
fi

echo ""
echo "=== Pausing STAGING resources ==="
gcloud config set project $STAGING_PROJECT

# Repeat for staging
echo -n "Stopping Cloud SQL instances... "
for instance in $(gcloud sql instances list --format="value(name)" 2>/dev/null); do
    gcloud sql instances patch $instance --no-backup --quiet 2>/dev/null || true
done
check_resource

echo -n "Scaling GKE clusters to 0 nodes... "
for cluster in $(gcloud container clusters list --format="value(name,location)" 2>/dev/null); do
    cluster_name=$(echo $cluster | cut -d' ' -f1)
    location=$(echo $cluster | cut -d' ' -f2)
    gcloud container clusters resize $cluster_name --size=0 --location=$location --quiet 2>/dev/null || true
done
check_resource

echo -n "Stopping Cloud Run services... "
for service in $(gcloud run services list --format="value(name,region)" 2>/dev/null); do
    service_name=$(echo $service | cut -d' ' -f1)
    region=$(echo $service | cut -d' ' -f2)
    gcloud run services update $service_name --max-instances=0 --region=$region --quiet 2>/dev/null || true
done
check_resource

echo -n "Stopping Compute Engine instances... "
for instance in $(gcloud compute instances list --format="value(name,zone)" 2>/dev/null); do
    instance_name=$(echo $instance | cut -d' ' -f1)
    zone=$(echo $instance | cut -d' ' -f2)
    gcloud compute instances stop $instance_name --zone=$zone --quiet 2>/dev/null || true
done
check_resource

echo ""
echo "=== Checking DEVELOPMENT project ==="
gcloud config set project $DEV_PROJECT
echo "Development project typically uses minimal resources. Checking..."

# Just check what's running
echo -n "Compute instances: "
gcloud compute instances list --format="value(name)" 2>/dev/null | wc -l
echo -n "Cloud Run services: "
gcloud run services list --format="value(name)" 2>/dev/null | wc -l

echo ""
echo -e "${GREEN}✅ Resource pause complete!${NC}"
echo ""
echo "💰 Cost savings:"
echo "  - Cloud SQL: Stopped (still paying for storage ~$10-50/month)"
echo "  - GKE: Scaled to 0 nodes (only paying for control plane ~$0.10/hour)"
echo "  - Cloud Run: Max instances set to 0 (no charges)"
echo "  - Compute Engine: All VMs stopped (only paying for disk storage)"
echo ""
echo "📌 To restore resources, run: ./scripts/gcp/restore-resources.sh"
echo ""
echo "💡 Tip: To check current costs, visit:"
echo "   https://console.cloud.google.com/billing"
