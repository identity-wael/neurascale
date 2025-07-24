# Terraform Cloud Setup Checklist

## Account Setup

- [ ] Create account at https://app.terraform.io/public/signup/account
- [ ] Create organization named: `neurascale`
- [ ] Generate API token at https://app.terraform.io/app/settings/tokens

## Local Setup

- [ ] Run `./setup-tf-token.sh` and paste token
- [ ] Run `terraform init`
- [ ] Verify workspaces are created

## Workspace Configuration

For each workspace (neural-engine-development, neural-engine-staging, neural-engine-production):

- [ ] Go to workspace → Settings → Variables
- [ ] Add Environment Variable: `GOOGLE_CREDENTIALS`
  - Value: Service account JSON (get from existing neural-engine-ci-key.json)
  - Mark as Sensitive
- [ ] Add Terraform Variable: `environment`
  - Value: development/staging/production (based on workspace)

## GitHub Secrets

- [ ] Add `TF_CLOUD_TOKEN` to repository secrets
  - Value: Your API token from Terraform Cloud

## Test Deployment

- [ ] Run `export TF_WORKSPACE=neural-engine-development`
- [ ] Run `terraform plan`
- [ ] Verify plan shows resources to be created

## Notes

- The workspaces will be created automatically when you run `terraform init`
- Make sure the organization name is exactly `neurascale`
- The service account JSON can be found in `neural-engine/neural-engine-ci-key.json`
