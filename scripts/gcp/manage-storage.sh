#!/bin/bash
# Manage GCP storage resources - find and handle large/unused storage
# Especially useful for finding that 5TB disk!

set -e

echo "💾 GCP Storage Management Tool"
echo "Finding and managing large storage resources across all projects"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Projects
PROJECTS=("neurascale-production" "neurascale-staging" "neurascale-development" "neurascale")

# Track total costs
TOTAL_DISK_GB=0
TOTAL_UNATTACHED_GB=0

echo -e "${BLUE}Scanning all projects for storage resources...${NC}"
echo ""

for PROJECT in "${PROJECTS[@]}"; do
    echo -e "${MAGENTA}=== PROJECT: $PROJECT ===${NC}"

    # Set project
    if ! gcloud config set project $PROJECT 2>/dev/null; then
        echo -e "${YELLOW}Skipping $PROJECT (no access)${NC}"
        continue
    fi

    # 1. Check Persistent Disks
    echo -e "\n${BLUE}Persistent Disks:${NC}"
    disks=$(gcloud compute disks list --format="csv(name,sizeGb,type,zone,users.basename())" 2>/dev/null | tail -n +2)

    if [ -z "$disks" ]; then
        echo "  No persistent disks found"
    else
        project_disk_total=0
        echo -e "  ${YELLOW}Name                    Size(GB)  Type              Zone                   Status${NC}"
        echo "  ---------------------------------------------------------------------------------"

        while IFS=',' read -r name size type zone users; do
            project_disk_total=$((project_disk_total + size))
            TOTAL_DISK_GB=$((TOTAL_DISK_GB + size))

            # Format output based on size
            if [ "$size" -gt 1000 ]; then
                size_display="${RED}${size}GB${NC}"
            elif [ "$size" -gt 500 ]; then
                size_display="${YELLOW}${size}GB${NC}"
            else
                size_display="${size}GB"
            fi

            # Check if attached
            if [ -z "$users" ] || [ "$users" == "None" ]; then
                status="${GREEN}UNATTACHED${NC}"
                TOTAL_UNATTACHED_GB=$((TOTAL_UNATTACHED_GB + size))

                # Add delete command for large unattached disks
                if [ "$size" -gt 100 ]; then
                    status="$status ${YELLOW}[DELETE ME]${NC}"
                fi
            else
                status="Attached to: $users"
            fi

            printf "  %-23s %-9s %-17s %-22s %s\n" "$name" "$size_display" "$type" "$zone" "$status"
        done <<< "$disks"

        echo "  ---------------------------------------------------------------------------------"
        echo -e "  ${BLUE}Project disk total: ${project_disk_total}GB${NC}"
    fi

    # 2. Check Cloud SQL storage
    echo -e "\n${BLUE}Cloud SQL Instances:${NC}"
    sql_instances=$(gcloud sql instances list --format="csv(name,settings.dataDiskSizeGb,state)" 2>/dev/null | tail -n +2)

    if [ -z "$sql_instances" ]; then
        echo "  No Cloud SQL instances found"
    else
        echo -e "  ${YELLOW}Instance                Size(GB)  State${NC}"
        echo "  ----------------------------------------"
        while IFS=',' read -r name size state; do
            printf "  %-23s %-9s %s\n" "$name" "${size}GB" "$state"
        done <<< "$sql_instances"
    fi

    # 3. Check Cloud Storage buckets with size
    echo -e "\n${BLUE}Cloud Storage Buckets:${NC}"
    buckets=$(gsutil ls -p $PROJECT 2>/dev/null || echo "")

    if [ -z "$buckets" ]; then
        echo "  No buckets found"
    else
        for bucket in $buckets; do
            # Get bucket size (this can be slow for large buckets)
            size=$(gsutil du -s $bucket 2>/dev/null | awk '{print $1}' || echo "0")
            size_gb=$((size / 1073741824))  # Convert to GB

            if [ "$size_gb" -gt 10 ]; then
                echo -e "  $bucket: ${YELLOW}${size_gb}GB${NC}"
            else
                echo "  $bucket: ${size_gb}GB"
            fi
        done
    fi

    echo ""
done

# Summary and recommendations
echo -e "${MAGENTA}=== STORAGE SUMMARY ===${NC}"
echo -e "Total persistent disk storage: ${YELLOW}${TOTAL_DISK_GB}GB${NC}"
echo -e "Total unattached disk storage: ${GREEN}${TOTAL_UNATTACHED_GB}GB${NC}"
echo ""

# Calculate potential savings
DISK_COST_PER_GB_MONTH=0.04  # Standard persistent disk cost
POTENTIAL_SAVINGS=$(echo "$TOTAL_UNATTACHED_GB * $DISK_COST_PER_GB_MONTH" | bc -l 2>/dev/null || echo "0")

echo -e "${MAGENTA}=== COST ANALYSIS ===${NC}"
echo -e "Unattached disks cost: ${RED}\$${POTENTIAL_SAVINGS} per month${NC}"
echo ""

# Provide cleanup commands
if [ "$TOTAL_UNATTACHED_GB" -gt 0 ]; then
    echo -e "${MAGENTA}=== CLEANUP COMMANDS ===${NC}"
    echo "To delete all unattached disks, run these commands:"
    echo ""

    for PROJECT in "${PROJECTS[@]}"; do
        gcloud config set project $PROJECT 2>/dev/null || continue

        unattached_disks=$(gcloud compute disks list --filter="users:NULL" --format="value(name,zone)" 2>/dev/null)
        if [ ! -z "$unattached_disks" ]; then
            echo "# Project: $PROJECT"
            echo "$unattached_disks" | while read disk; do
                disk_name=$(echo $disk | cut -d' ' -f1)
                zone=$(echo $disk | cut -d' ' -f2)
                echo "gcloud compute disks delete $disk_name --zone=$zone --project=$PROJECT"
            done
            echo ""
        fi
    done

    echo -e "${YELLOW}⚠️  WARNING: Make sure to snapshot any important data before deleting!${NC}"
    echo "To create a snapshot: gcloud compute disks snapshot DISK_NAME --zone=ZONE"
fi

echo ""
echo -e "${BLUE}💡 Tips:${NC}"
echo "1. That 5TB disk is likely an unattached persistent disk"
echo "2. Unattached disks still cost money (~\$200/month for 5TB)"
echo "3. Always snapshot before deleting if unsure"
echo "4. Consider using smaller disks or object storage (GCS) instead"
