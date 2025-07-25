# GitHub Actions Workflows

## Neural Engine CI/CD

The main CI/CD workflow for the Neural Engine project.

### Workflow: `neural-engine-cicd.yml`

This consolidated workflow handles:

- Testing (linting, type checking, unit tests)
- Building Docker images
- Deploying infrastructure with Terraform
- Verifying deployments

### Key Features

1. **Environment Detection**: Automatically determines the target environment based on the event type:

   - Pull Requests → Staging
   - Main branch → Production
   - Other branches → Development

2. **Terraform State Management**:

   - Combined plan and apply steps to prevent stale plan errors
   - Automatic cleanup of stale locks
   - Proper state isolation per environment

3. **Optimizations**:
   - Test result caching to skip unchanged code
   - Parallel Docker builds
   - Self-hosted runners for better performance

### Known Issues and Fixes

#### Stale Terraform Plan

**Issue**: "Saved plan is stale" error when deploying to production
**Cause**: Delay between plan and apply steps allowing state changes
**Fix**: Combined plan and apply into a single step (fixed in commit)

### Troubleshooting

If you encounter deployment issues:

1. **Check for concurrent workflows**: Multiple workflows can cause state conflicts
2. **Re-run failed jobs**: Most transient issues resolve on retry
3. **Check state locks**: The workflow automatically cleans up stale locks

### Environment Variables

Required secrets:

- `TF_CLOUD_TOKEN`: Terraform Cloud token (if using)
- GitHub OIDC configured for Workload Identity Federation

### Running Locally

To test the Terraform deployment locally:

```bash
cd neural-engine/terraform
terraform init -backend-config=backend-configs/staging.hcl
terraform plan -var-file=environments/staging.tfvars
```
