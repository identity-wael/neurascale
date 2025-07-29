# MCP Server Terraform Module

This Terraform module provisions the infrastructure required for the NeuraScale MCP (Model Context Protocol) server, including Secret Manager resources, IAM permissions, and optional Cloud Run deployment.

## Features

- **Secret Management**: Automatic creation of secure secrets in GCP Secret Manager
- **Service Accounts**: Dedicated service account with minimal required permissions
- **Cloud Run Deployment**: Optional containerized deployment with auto-scaling
- **Monitoring**: Built-in health checks and alerting
- **Security**: IAM permissions following principle of least privilege
- **Multi-Environment**: Support for development, staging, and production configurations

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Client    │───▶│   Cloud Run      │───▶│  Secret Manager │
│                 │    │   MCP Server     │◀───│                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                          │
                              ▼                          ▼
                       ┌──────────────┐         ┌──────────────┐
                       │  Monitoring  │         │ Service      │
                       │  & Alerting  │         │ Account      │
                       └──────────────┘         └──────────────┘
```

## Resources Created

### Secret Manager
- `mcp-api-key-salt`: Salt for API key hashing
- `mcp-jwt-secret`: Secret for JWT token signing

### IAM
- Service account for MCP server
- Secret Manager accessor permissions
- Optional compute/App Engine service account permissions

### Cloud Run (Optional)
- Containerized MCP server deployment
- Auto-scaling configuration
- Health checks and monitoring

### Monitoring (Optional)
- Health check alert policies
- Log-based error metrics
- Performance monitoring

## Usage

### Basic Usage

```hcl
module "mcp_server" {
  source = "./modules/mcp-server"

  project_id  = "your-project-id"
  environment = "development"
  region      = "us-central1"
}
```

### Advanced Usage

```hcl
module "mcp_server" {
  source = "./modules/mcp-server"

  project_id  = "your-project-id"
  environment = "production"
  region      = "us-central1"

  # Cloud Run Configuration
  enable_cloud_run     = true
  mcp_server_image     = "gcr.io/your-project/mcp-server:v1.0.0"
  min_instances        = 2
  max_instances        = 20
  enable_public_access = true

  # Monitoring
  enable_monitoring     = true
  notification_channels = ["projects/your-project/notificationChannels/123"]

  # Security
  enable_compute_access    = true
  enable_appengine_access  = false
}
```

## Variables

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| `project_id` | GCP Project ID | `string` | n/a | yes |
| `environment` | Environment name | `string` | n/a | yes |
| `region` | GCP region | `string` | `"us-central1"` | no |
| `enable_cloud_run` | Deploy as Cloud Run service | `bool` | `false` | no |
| `mcp_server_image` | Container image | `string` | `"gcr.io/PROJECT_ID/mcp-server:latest"` | no |
| `min_instances` | Minimum instances | `number` | `0` | no |
| `max_instances` | Maximum instances | `number` | `10` | no |
| `enable_monitoring` | Enable monitoring | `bool` | `true` | no |
| `enable_public_access` | Allow public access | `bool` | `false` | no |

## Outputs

| Name | Description |
|------|-------------|
| `mcp_server_service_account_email` | Service account email |
| `secret_uris` | Secret Manager URIs for configuration |
| `cloud_run_service_url` | Cloud Run service URL |
| `deployment_info` | Complete deployment information |

## Security Considerations

### Secrets Management
- Secrets are automatically generated with secure random values
- Access is granted only to the specific service account
- Secrets support versioning and rotation

### IAM Permissions
- Dedicated service account with minimal permissions
- Optional compute/App Engine access for flexibility
- No overly broad permissions granted

### Network Security
- Private-by-default configuration
- Optional public access with proper authentication
- VPC integration support

## Environment-Specific Configurations

### Development
```hcl
enable_mcp_cloud_run    = true
mcp_min_instances       = 0
mcp_max_instances       = 3
enable_mcp_public_access = false
```

### Staging
```hcl
enable_mcp_cloud_run    = true
mcp_min_instances       = 1
mcp_max_instances       = 5
enable_mcp_public_access = false
```

### Production
```hcl
enable_mcp_cloud_run    = true
mcp_min_instances       = 2
mcp_max_instances       = 20
enable_mcp_public_access = true
```

## Deployment

### Prerequisites

1. **Terraform**: Version >= 1.5.0
2. **GCP Authentication**: Service account with appropriate permissions
3. **APIs Enabled**: Secret Manager, Cloud Run, IAM APIs

### Required Permissions

The Terraform service account needs:
- `roles/secretmanager.admin`
- `roles/iam.serviceAccountAdmin`
- `roles/run.admin` (if using Cloud Run)
- `roles/monitoring.editor` (if enabling monitoring)

### Deployment Steps

1. **Initialize Terraform**:
   ```bash
   terraform init
   ```

2. **Plan Deployment**:
   ```bash
   terraform plan -var-file="environments/development.tfvars"
   ```

3. **Deploy Infrastructure**:
   ```bash
   terraform apply -var-file="environments/development.tfvars"
   ```

4. **Verify Deployment**:
   ```bash
   terraform output
   ```

## Integration with MCP Server

The module outputs Secret Manager URIs that can be used directly in the MCP server configuration:

```yaml
# server_config.yaml
auth:
  api_key_salt: "gcp-secret://projects/PROJECT_ID/secrets/mcp-api-key-salt/versions/latest"
  jwt_secret: "gcp-secret://projects/PROJECT_ID/secrets/mcp-jwt-secret/versions/latest"
```

The MCP server will automatically resolve these URIs at runtime using the service account credentials.

## Monitoring and Alerting

### Health Checks
- Cloud Run service availability
- Secret Manager access
- Service account permissions

### Metrics
- Request latency and throughput
- Error rates and types
- Resource utilization

### Alerts
- Service downtime
- High error rates
- Resource limits

## Cost Optimization

### Development
- Scale to zero when not in use
- Minimal resource allocation
- Reduced monitoring

### Production
- Appropriate minimum instance count
- Auto-scaling based on demand
- Comprehensive monitoring

## Troubleshooting

### Common Issues

1. **Secret Access Denied**
   - Verify service account permissions
   - Check IAM bindings
   - Ensure APIs are enabled

2. **Cloud Run Deployment Fails**
   - Verify container image exists
   - Check service account configuration
   - Review Cloud Run logs

3. **Monitoring Not Working**
   - Verify notification channels
   - Check alert policy configuration
   - Review monitoring permissions

### Debug Commands

```bash
# Check secrets
gcloud secrets list --project=PROJECT_ID

# Check service accounts
gcloud iam service-accounts list --project=PROJECT_ID

# Check Cloud Run services
gcloud run services list --project=PROJECT_ID

# View Terraform state
terraform show
```

## Contributing

When modifying this module:

1. Update variable descriptions and defaults
2. Add appropriate validation rules
3. Update documentation
4. Test with all environment configurations
5. Follow Terraform best practices

## Version History

- **v1.0.0**: Initial release with basic Secret Manager and Cloud Run support
- **v1.1.0**: Added monitoring and alerting capabilities
- **v1.2.0**: Enhanced security and IAM configurations