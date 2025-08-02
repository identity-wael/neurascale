# GCP Cost Optimization Scripts

These scripts help manage GCP resources to minimize costs during development.

## Scripts Overview

### 1. `check-resources.sh`

Scans all projects to identify running resources and their costs.

```bash
./scripts/gcp/check-resources.sh
```

### 2. `manage-storage.sh`

Finds large storage volumes (like that 5TB disk!) and provides cleanup commands.

```bash
./scripts/gcp/manage-storage.sh
```

**Features:**

- Identifies all persistent disks across projects
- Highlights unattached disks (still costing money)
- Calculates potential savings
- Provides delete commands for cleanup

### 3. `pause-resources.sh`

Stops/pauses all costly resources while preserving configurations.

```bash
./scripts/gcp/pause-resources.sh
```

**What it does:**

- Stops Cloud SQL instances (disables backups)
- Scales GKE clusters to 0 nodes
- Sets Cloud Run max instances to 0
- Stops all Compute Engine VMs
- Identifies large disks (>500GB)
- Warns about Bigtable (can't be paused)

### 4. `restore-resources.sh`

Restores all paused resources when you need them again.

```bash
./scripts/gcp/restore-resources.sh
```

**What it does:**

- Starts Cloud SQL with backups enabled
- Scales GKE to default node counts
- Restores Cloud Run max instances
- Starts all Compute Engine VMs

## Cost Breakdown When Paused

| Resource    | Running Cost | Paused Cost                  | Savings |
| ----------- | ------------ | ---------------------------- | ------- |
| Cloud SQL   | ~$100-500/mo | ~$10-50/mo (storage only)    | 80-90%  |
| GKE Nodes   | ~$75/node/mo | $0 (control plane: $0.10/hr) | 95%     |
| Cloud Run   | Variable     | $0                           | 100%    |
| Compute VMs | ~$25-200/mo  | ~$5-20/mo (disk only)        | 80-90%  |
| 5TB Disk    | ~$200/mo     | $0 if deleted                | 100%    |

## Recommended Workflow

1. **First time - Check what you have:**

   ```bash
   ./scripts/gcp/check-resources.sh
   ./scripts/gcp/manage-storage.sh
   ```

2. **Delete that 5TB disk (if found and unattached):**

   ```bash
   # The manage-storage.sh script will show the exact command
   gcloud compute disks delete DISK_NAME --zone=ZONE --project=PROJECT
   ```

3. **Pause all resources:**

   ```bash
   ./scripts/gcp/pause-resources.sh
   ```

4. **When you need to work again:**
   ```bash
   ./scripts/gcp/restore-resources.sh
   ```

## Important Notes

- **Bigtable** cannot be paused - only deleted. Consider if you really need it during development.
- **Persistent disks** still cost money when VMs are stopped (~$0.04/GB/month).
- **Static IPs** cost money when not attached to running instances.
- **Snapshots** are cheaper than keeping large disks (~$0.026/GB/month).

## Emergency Full Shutdown

If you need to minimize costs to near-zero:

```bash
# 1. Backup anything important
gcloud compute disks snapshot DISK_NAME --zone=ZONE

# 2. Delete all unattached disks
./scripts/gcp/manage-storage.sh  # Shows delete commands

# 3. Delete Bigtable instances
gcloud bigtable instances list
gcloud bigtable instances delete INSTANCE_NAME

# 4. Release static IPs
gcloud compute addresses list
gcloud compute addresses delete ADDRESS_NAME --region=REGION
```

## Monitoring Costs

Check your current burn rate:

- [GCP Billing Console](https://console.cloud.google.com/billing)
- Set up budget alerts for > $10/day during development
