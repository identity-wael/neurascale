#!/bin/bash
# Check all GCP resources across projects to identify what's running and costs

set -e

echo "🔍 Checking all GCP resources across projects..."
echo "This will help identify costly resources like large storage volumes"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Projects
PROJECTS=("neurascale-production" "neurascale-staging" "neurascale-development")

for PROJECT in "${PROJECTS[@]}"; do
    echo ""
    echo -e "${BLUE}=== PROJECT: $PROJECT ===${NC}"
    gcloud config set project $PROJECT 2>/dev/null || continue

    # Check Compute Engine Disks
    echo -e "\n${YELLOW}Persistent Disks:${NC}"
    gcloud compute disks list --format="table(name,sizeGb,type,status,users.scope():label=ATTACHED_TO)" 2>/dev/null || echo "No disks found"

    # Check for large disks (> 100GB)
    echo -e "\n${RED}Large Disks (>100GB):${NC}"
    gcloud compute disks list --filter="sizeGb>100" --format="table(name,sizeGb,type,zone)" 2>/dev/null || echo "No large disks found"

    # Check Cloud SQL storage
    echo -e "\n${YELLOW}Cloud SQL Instances:${NC}"
    gcloud sql instances list --format="table(name,settings.dataDiskSizeGb:label=DISK_GB,state)" 2>/dev/null || echo "No Cloud SQL instances found"

    # Check Cloud Storage buckets
    echo -e "\n${YELLOW}Cloud Storage Buckets:${NC}"
    gsutil ls -p $PROJECT 2>/dev/null || echo "No buckets found"

    # Check Filestore instances
    echo -e "\n${YELLOW}Filestore Instances:${NC}"
    gcloud filestore instances list --format="table(name,tier,fileShares[0].capacityGb:label=SIZE_GB,state)" 2>/dev/null || echo "No Filestore instances found"

    # Check GKE Persistent Volumes
    echo -e "\n${YELLOW}GKE Persistent Volume Claims:${NC}"
    for cluster in $(gcloud container clusters list --format="value(name,location)" 2>/dev/null); do
        cluster_name=$(echo $cluster | cut -d' ' -f1)
        location=$(echo $cluster | cut -d' ' -f2)
        echo "Cluster: $cluster_name"
        gcloud container clusters get-credentials $cluster_name --location=$location 2>/dev/null
        kubectl get pvc --all-namespaces -o custom-columns=NAMESPACE:.metadata.namespace,NAME:.metadata.name,SIZE:.spec.resources.requests.storage,STATUS:.status.phase 2>/dev/null || echo "Could not access cluster"
    done
done

echo ""
echo -e "${BLUE}=== COST RECOMMENDATIONS ===${NC}"
echo "If you found a 5TB disk, you can:"
echo "1. Delete it if not needed: gcloud compute disks delete DISK_NAME --zone=ZONE"
echo "2. Resize it smaller: gcloud compute disks resize DISK_NAME --size=100GB --zone=ZONE"
echo "3. Create a snapshot first: gcloud compute disks snapshot DISK_NAME --zone=ZONE"
echo ""
echo "💡 To see detailed billing: https://console.cloud.google.com/billing"
