# Migration Guide: Simplified Terraform Architecture

This guide explains how to migrate from the current complex Terraform setup to the new simplified architecture.

## Overview of Changes

### 1. **Simplified IAM Strategy**

- **Before**: Complex service account chains with Cloud Build, multiple service agents
- **After**: Single service account per environment + GitHub Actions service account

### 2. **Integrated Deployment**

- **Before**: Terraform deploys infrastructure, then gcloud deploys functions separately
- **After**: Terraform deploys everything including Cloud Functions

### 3. **Clear Dependencies**

- **Before**: Race conditions due to missing dependencies
- **After**: Explicit dependency chains with wait times

### 4. **Cleaner Module Structure**

- **Before**: Duplicate resources, mixed concerns
- **After**: Single responsibility, no duplicates

## Migration Steps

### Step 1: Clean Up Existing Resources

First, we need to clean up the existing deployment to avoid conflicts:

```bash
# Set the environment you're working with
export ENV=staging  # or development, production
export PROJECT_ID=${ENV}-neurascale

# Delete existing Cloud Functions (if any)
gcloud functions list --project=$PROJECT_ID --format="value(name)" | \
  xargs -I {} gcloud functions delete {} --project=$PROJECT_ID --quiet

# Remove existing IAM bindings for Cloud Build
gcloud projects remove-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')@cloudbuild.gserviceaccount.com" \
  --role="roles/cloudfunctions.developer"

# Continue for other roles...
```

### Step 2: Backup Current State

```bash
# Download current state as backup
cd neural-engine/terraform
terraform init -backend-config="bucket=neurascale-terraform-state" \
              -backend-config="prefix=neural-engine/$ENV"
terraform state pull > terraform-$ENV.tfstate.backup
```

### Step 3: Switch to New Configuration

```bash
# The new files are already in place:
# - main.tf (simplified)
# - modules/neural-ingestion/main.tf (simplified)
# - .github/workflows/neural-engine-deploy-simplified.yml

# Remove the old workflow to avoid conflicts
git rm .github/workflows/neural-engine-deploy.yml
```

### Step 4: Initialize New Configuration

```bash
# Initialize with the new configuration
terraform init -reconfigure \
  -backend-config="bucket=neurascale-terraform-state" \
  -backend-config="prefix=neural-engine/$ENV"

# Import existing resources that we want to keep
# Example: Import the service account if it exists
terraform import google_service_account.neural_ingestion \
  projects/$PROJECT_ID/serviceAccounts/neural-ingestion-${ENV:0:4}@$PROJECT_ID.iam.gserviceaccount.com
```

### Step 5: Plan and Apply

```bash
# Review what will change
terraform plan \
  -var="project_id=$PROJECT_ID" \
  -var="github_actions_service_account=github-actions@neurascale.iam.gserviceaccount.com" \
  -var="region=northamerica-northeast1"

# Apply changes (this will likely recreate many resources)
terraform apply \
  -var="project_id=$PROJECT_ID" \
  -var="github_actions_service_account=github-actions@neurascale.iam.gserviceaccount.com" \
  -var="region=northamerica-northeast1"
```

### Step 6: Update GitHub Actions

```bash
# Commit the new workflow
git add .github/workflows/neural-engine-deploy-simplified.yml
git add neural-engine/terraform/
git commit -m "Migrate to simplified Terraform architecture"
git push
```

## Key Differences to Note

### 1. **Service Account Names**

- Old: Various service accounts with complex permissions
- New: `neural-ingestion-{env_short}@{project_id}.iam.gserviceaccount.com`

### 2. **Cloud Functions Deployment**

- Old: Deployed via gcloud CLI after Terraform
- New: Deployed by Terraform using uploaded zip file

### 3. **State Management**

- Old: Dynamic state file selection in GitHub Actions
- New: Consistent state file per environment

### 4. **API Enablement**

- Old: APIs enabled in separate module
- New: APIs enabled in main.tf with proper wait time

## Rollback Plan

If issues arise during migration:

```bash
# Restore from backup
terraform state push terraform-$ENV.tfstate.backup

# Switch back to old configuration
git checkout main -- neural-engine/terraform/main.tf
git checkout main -- neural-engine/terraform/modules/neural-ingestion/main.tf
git checkout main -- .github/workflows/neural-engine-deploy.yml

# Reapply old configuration
terraform init -reconfigure
terraform apply
```

## Verification

After migration, verify:

1. **Service Accounts**: Check they exist with correct permissions
2. **Cloud Functions**: Verify they're deployed and responding
3. **Pub/Sub**: Test message publishing
4. **Bigtable**: Confirm tables are accessible
5. **GitHub Actions**: Ensure workflows pass

## Common Issues

### Issue 1: State Lock

```bash
# Remove stale lock if needed
gsutil rm gs://neurascale-terraform-state/neural-engine/$ENV/default.tflock
```

### Issue 2: Permission Denied

- Ensure GitHub Actions service account has proper permissions in orchestration project
- Wait 2-3 minutes for IAM changes to propagate

### Issue 3: Functions Not Deploying

- Check that the functions zip was uploaded to GCS
- Verify the bucket name matches between upload and Terraform

## Benefits of New Architecture

1. **Simpler**: Fewer moving parts, clearer dependencies
2. **Reliable**: No race conditions, proper wait times
3. **Maintainable**: Single source of truth for all resources
4. **Secure**: Least-privilege permissions, no owner roles
5. **Debuggable**: Clear error messages, better logs
