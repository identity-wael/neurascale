# Terraform Cloud Setup Instructions

## Prerequisites Completed ✅

1. Created GCP projects:

   - `neurascale` (orchestration)
   - `production-neurascale`
   - `staging-neurascale`
   - `development-neurascale`

2. Set up GCS bucket for backup: `neurascale-terraform-state`

3. Created service account: `github-actions@neurascale.iam.gserviceaccount.com`

4. Configured Terraform to use Terraform Cloud backend

## Action Required

### 1. Terraform Cloud Account Setup

1. Go to https://app.terraform.io/session
2. Sign up or log in
3. Create an organization named: `neurascale`

### 2. Create API Token

1. Go to https://app.terraform.io/app/settings/tokens
2. Click "Create an API token"
3. Name: "GitHub Actions CI/CD"
4. Save this token securely

### 3. Create Workspaces

In Terraform Cloud, create three workspaces:

1. **neural-engine-development**

   - Go to Organizations → neurascale → New Workspace
   - Choose "CLI-driven workflow"
   - Name: `neural-engine-development`
   - After creation, go to Settings → General → Tags
   - Add tag: `neural-engine`

2. **neural-engine-staging**

   - Repeat above with name: `neural-engine-staging`
   - Add tag: `neural-engine`

3. **neural-engine-production**
   - Repeat above with name: `neural-engine-production`
   - Add tag: `neural-engine`

### 4. Configure Workspace Variables

For each workspace, go to Variables → Add Variable:

#### Environment Variables:

1. `GOOGLE_CREDENTIALS`

   - Type: Environment variable
   - Value: (service account JSON - get from existing key)
   - Sensitive: ✓

2. `TF_VAR_environment`
   - Type: Environment variable
   - Value: `development` / `staging` / `production` (per workspace)

### 5. GitHub Secrets

Add to repository secrets:

1. `TF_CLOUD_TOKEN`

   - Value: (API token from step 2)

2. Keep existing:
   - `WIF_PROVIDER`
   - `WIF_SERVICE_ACCOUNT`

### 6. Local Authentication

Run:

```bash
cd neural-engine/terraform
terraform login
# Follow prompts to authenticate
```

### 7. Initialize and Test

```bash
# Initialize
terraform init

# List workspaces (should show the three created)
terraform workspace list

# Test plan
export TF_WORKSPACE=neural-engine-development
terraform plan
```

## Next Steps

Once setup is complete:

1. Commit and push the changes
2. The PR will automatically deploy to staging
3. Merging to main will deploy to production
4. Set up Cloud Scheduler for state backups (optional)

## Troubleshooting

- If workspaces don't appear, check the tag `neural-engine` is added
- If authentication fails, regenerate the API token
- For GCP auth issues, check the service account JSON in workspace variables
