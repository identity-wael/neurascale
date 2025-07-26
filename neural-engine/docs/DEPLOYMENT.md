# Neural Ledger Deployment Guide

This guide covers the deployment of the Neural Ledger system to staging and production environments.

## Overview

The Neural Ledger uses a multi-tier architecture deployed on Google Cloud Platform:

- **Pub/Sub**: Event ingestion
- **Cloud Functions**: Event processing
- **Bigtable**: High-frequency queries
- **Firestore**: Real-time queries
- **BigQuery**: Long-term storage and analytics
- **Cloud KMS**: Digital signatures
- **Cloud Monitoring**: Metrics and alerting

## Prerequisites

Before deploying, ensure you have:

1. **Google Cloud SDK** installed and configured
2. **Terraform** >= 1.0 installed
3. **Python 3.12** environment
4. **Required GCP APIs** enabled
5. **Appropriate IAM permissions**

### Required GCP APIs

```bash
gcloud services enable cloudresourcemanager.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable pubsub.googleapis.com
gcloud services enable bigtable.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable cloudkms.googleapis.com
gcloud services enable monitoring.googleapis.com
gcloud services enable logging.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### Required IAM Permissions

Your deployment account needs these roles:

- `roles/editor` or more granular permissions:
  - `roles/pubsub.admin`
  - `roles/cloudfunctions.admin`
  - `roles/bigtable.admin`
  - `roles/datastore.owner`
  - `roles/bigquery.admin`
  - `roles/cloudkms.admin`
  - `roles/monitoring.admin`
  - `roles/logging.admin`

## Staging Deployment

### Quick Start

1. **Set environment variables:**

   ```bash
   export GCP_PROJECT_ID="neurascale-staging"
   export GCP_REGION="northamerica-northeast1"
   ```

2. **Deploy to staging:**

   ```bash
   ./scripts/deploy-staging.sh
   ```

3. **Run tests:**

   ```bash
   RUN_TESTS=true ./scripts/deploy-staging.sh
   # OR separately:
   ./scripts/test-staging.sh
   ```

4. **Clean up when done:**
   ```bash
   ./scripts/cleanup-staging.sh
   ```

### Manual Staging Deployment

If you prefer to deploy manually:

1. **Deploy infrastructure:**

   ```bash
   cd infrastructure/ledger
   terraform init
   terraform plan -var="project_id=${GCP_PROJECT_ID}" -var="environment=staging"
   terraform apply
   ```

2. **Deploy Cloud Function:**

   ```bash
   cd functions/ledger_handler
   gcloud functions deploy neural-ledger-processor \
     --source=. \
     --entry-point=process_ledger_event \
     --runtime=python312 \
     --trigger-topic=neural-ledger-events \
     --project="${GCP_PROJECT_ID}"
   ```

3. **Set up monitoring:**
   ```bash
   python3 -c "
   from ledger.monitoring import create_monitoring_dashboard
   create_monitoring_dashboard('${GCP_PROJECT_ID}', 'neural-ledger-staging')
   "
   ```

## Production Deployment

### Prerequisites for Production

1. **Security review** of all configurations
2. **Backup strategy** implemented
3. **Monitoring and alerting** configured
4. **Disaster recovery plan** in place
5. **Compliance approval** (HIPAA, GDPR)

### Production Deployment Steps

1. **Update Terraform variables:**

   ```bash
   cd infrastructure/ledger
   cat > terraform.tfvars <<EOF
   project_id = "neurascale-production"
   region = "northamerica-northeast1"
   environment = "production"

   # Production-specific settings
   bigtable_num_nodes = 3
   enable_deletion_protection = true
   monitoring_retention_days = 30

   # Security settings
   enable_audit_logs = true
   enable_vpc_flow_logs = true
   enable_private_ip = true
   EOF
   ```

2. **Deploy infrastructure:**

   ```bash
   terraform plan -var-file=terraform.tfvars
   terraform apply -var-file=terraform.tfvars
   ```

3. **Deploy Cloud Function with production settings:**

   ```bash
   gcloud functions deploy neural-ledger-processor \
     --source=functions/ledger_handler \
     --entry-point=process_ledger_event \
     --runtime=python312 \
     --trigger-topic=neural-ledger-events \
     --memory=1024MB \
     --timeout=540s \
     --max-instances=500 \
     --vpc-connector=neural-ledger-connector \
     --egress-settings=private-ranges-only \
     --project="${GCP_PROJECT_ID}"
   ```

4. **Configure monitoring and alerting:**

   ```bash
   # Create production dashboard
   python3 -c "
   from ledger.monitoring import create_monitoring_dashboard
   create_monitoring_dashboard('${GCP_PROJECT_ID}', 'neural-ledger-production')
   "

   # Set up alerting policies
   gcloud alpha monitoring policies create --policy-from-file=monitoring/alerting-policies.yaml
   ```

## Configuration

### Environment Variables

The system uses these environment variables:

| Variable            | Description          | Default                   |
| ------------------- | -------------------- | ------------------------- |
| `GCP_PROJECT_ID`    | GCP project ID       | Required                  |
| `GCP_REGION`        | GCP region           | `northamerica-northeast1` |
| `ENVIRONMENT`       | Environment name     | `production`              |
| `BIGTABLE_INSTANCE` | Bigtable instance ID | `neural-ledger`           |
| `BIGQUERY_DATASET`  | BigQuery dataset ID  | `neural_ledger`           |
| `KMS_KEYRING`       | KMS keyring name     | `neural-ledger`           |
| `KMS_KEY`           | KMS key name         | `signing-key`             |

### Terraform Variables

Key Terraform variables for customization:

```hcl
# terraform.tfvars
project_id = "your-project-id"
region = "your-region"
environment = "staging|production"

# Bigtable configuration
bigtable_num_nodes = 3
bigtable_storage_type = "SSD"

# Security settings
enable_deletion_protection = true
enable_audit_logs = true
enable_vpc_flow_logs = true

# Monitoring configuration
monitoring_retention_days = 30
enable_uptime_checks = true

# Backup configuration
backup_retention_days = 365
enable_point_in_time_recovery = true
```

## Monitoring and Alerting

### Key Metrics to Monitor

1. **Performance Metrics:**

   - Event processing latency (target: <100ms)
   - Storage write latency
   - Signature verification time

2. **Throughput Metrics:**

   - Events processed per second
   - Storage writes per second
   - Function invocations

3. **Error Metrics:**

   - Function errors
   - Storage failures
   - Signature verification failures
   - Chain integrity violations

4. **Resource Metrics:**
   - Function memory usage
   - Bigtable CPU utilization
   - BigQuery slot usage

### Alerting Policies

Set up alerts for:

- High error rates (>1% for 5 minutes)
- High latency (>200ms p99 for 10 minutes)
- Chain integrity violations (any occurrence)
- Function failures (>5 in 1 minute)
- Storage unavailability

### Dashboards

The deployment creates monitoring dashboards showing:

- Event processing latency (p50, p95, p99)
- Events processed per minute
- Storage write latency by tier
- Chain violations alert
- Function metrics

## Security Considerations

### Data Protection

1. **Encryption at Rest:**

   - All data encrypted with Google-managed keys
   - Critical events signed with customer-managed KMS keys

2. **Encryption in Transit:**

   - All communications use TLS 1.3
   - VPC-native networking for internal traffic

3. **Access Controls:**
   - IAM-based access controls
   - Service accounts with minimal permissions
   - VPC firewall rules

### Compliance

1. **HIPAA Compliance:**

   - Audit trails for all data access
   - Encryption of PHI data
   - Access controls and monitoring

2. **GDPR Compliance:**

   - Data minimization
   - Right to be forgotten support
   - Data processing logs

3. **FDA 21 CFR Part 11:**
   - Digital signatures for critical events
   - Audit trails for all changes
   - User access controls

## Backup and Recovery

### Automated Backups

1. **BigQuery:** Automatic table snapshots
2. **Bigtable:** Scheduled backups to Cloud Storage
3. **Firestore:** Automatic backups enabled
4. **Cloud Functions:** Source code in Cloud Source Repositories

### Recovery Procedures

1. **Point-in-time recovery** from BigQuery snapshots
2. **Cross-region replication** for high availability
3. **Disaster recovery plan** with RTO < 4 hours, RPO < 1 hour

## Troubleshooting

### Common Issues

1. **Function Timeout:**

   - Increase timeout to 540s for production
   - Monitor processing latency
   - Check for storage bottlenecks

2. **Storage Errors:**

   - Check IAM permissions
   - Verify resource quotas
   - Monitor error logs

3. **Chain Integrity Violations:**
   - Check for concurrent writes
   - Verify hash computation
   - Review event ordering

### Debugging Commands

```bash
# Check function logs
gcloud functions logs read neural-ledger-processor --project="${GCP_PROJECT_ID}"

# Check Pub/Sub message backlog
gcloud pubsub subscriptions describe neural-ledger-processor --project="${GCP_PROJECT_ID}"

# Query recent events
bq query --project_id="${GCP_PROJECT_ID}" "
SELECT event_type, COUNT(*) as count
FROM \`neural_ledger.events\`
WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
GROUP BY event_type
"

# Check Bigtable metrics
gcloud bigtable instances describe neural-ledger --project="${GCP_PROJECT_ID}"
```

## Cost Optimization

### Staging Environment

- Use minimal Bigtable nodes (1)
- Disable deletion protection
- Shorter retention periods (7 days)
- Lower function memory allocation

### Production Environment

- Use preemptible instances where possible
- Set up budget alerts
- Use committed use discounts
- Monitor and optimize storage usage

## Maintenance

### Regular Tasks

1. **Weekly:**

   - Review monitoring dashboards
   - Check error logs
   - Verify backup integrity

2. **Monthly:**

   - Update dependencies
   - Review security patches
   - Performance optimization review

3. **Quarterly:**
   - Disaster recovery testing
   - Security audit
   - Compliance review

### Updates and Patches

1. **Test in staging first**
2. **Use blue-green deployments**
3. **Monitor after deployment**
4. **Have rollback plan ready**

## Support and Documentation

- **Architecture Documentation:** See `docs/ARCHITECTURE.md`
- **API Documentation:** See `docs/API.md`
- **Compliance Documentation:** See `docs/COMPLIANCE.md`
- **Monitoring Runbook:** See `docs/MONITORING.md`

For issues or questions, contact the NeuraScale infrastructure team.
