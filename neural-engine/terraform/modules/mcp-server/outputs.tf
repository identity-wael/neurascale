# Outputs for MCP Server Infrastructure Module

# Secret Manager Outputs
output "mcp_api_key_salt_secret_name" {
  description = "Name of the MCP API key salt secret"
  value       = google_secret_manager_secret.mcp_api_key_salt.name
}

output "mcp_jwt_secret_name" {
  description = "Name of the MCP JWT secret"
  value       = google_secret_manager_secret.mcp_jwt_secret.name
}

output "mcp_api_key_salt_secret_id" {
  description = "Secret ID of the MCP API key salt"
  value       = google_secret_manager_secret.mcp_api_key_salt.secret_id
}

output "mcp_jwt_secret_id" {
  description = "Secret ID of the MCP JWT secret"
  value       = google_secret_manager_secret.mcp_jwt_secret.secret_id
}

# Service Account Outputs
output "mcp_server_service_account_email" {
  description = "Email of the MCP server service account"
  value       = google_service_account.mcp_server.email
}

output "mcp_server_service_account_id" {
  description = "ID of the MCP server service account"
  value       = google_service_account.mcp_server.id
}

output "mcp_server_service_account_name" {
  description = "Name of the MCP server service account"
  value       = google_service_account.mcp_server.name
}

# Cloud Run Outputs (if enabled)
output "cloud_run_service_url" {
  description = "URL of the Cloud Run service"
  value       = var.enable_cloud_run ? google_cloud_run_v2_service.mcp_server[0].uri : null
}

output "cloud_run_service_name" {
  description = "Name of the Cloud Run service"
  value       = var.enable_cloud_run ? google_cloud_run_v2_service.mcp_server[0].name : null
}

output "cloud_run_service_location" {
  description = "Location of the Cloud Run service"
  value       = var.enable_cloud_run ? google_cloud_run_v2_service.mcp_server[0].location : null
}

# Load Balancer Outputs (if enabled)
output "load_balancer_ip" {
  description = "IP address of the load balancer"
  value       = var.enable_load_balancer ? google_compute_global_address.mcp_server_ip[0].address : null
}

output "load_balancer_ip_name" {
  description = "Name of the load balancer IP"
  value       = var.enable_load_balancer ? google_compute_global_address.mcp_server_ip[0].name : null
}

# Configuration URIs for application deployment
output "secret_uris" {
  description = "Secret Manager URIs for MCP server configuration"
  value = {
    api_key_salt = "gcp-secret://projects/${var.project_id}/secrets/${google_secret_manager_secret.mcp_api_key_salt.secret_id}/versions/latest"
    jwt_secret   = "gcp-secret://projects/${var.project_id}/secrets/${google_secret_manager_secret.mcp_jwt_secret.secret_id}/versions/latest"
  }
}

# Environment Configuration
output "environment_variables" {
  description = "Environment variables for MCP server deployment"
  value = {
    GCP_PROJECT_ID = var.project_id
    ENVIRONMENT    = var.environment
    MCP_PORT       = var.mcp_server_port
  }
}

# Monitoring Outputs
output "monitoring_alert_policy_name" {
  description = "Name of the monitoring alert policy"
  value       = var.enable_monitoring ? google_monitoring_alert_policy.mcp_server_health[0].name : null
}

output "log_metric_name" {
  description = "Name of the log-based metric"
  value       = var.enable_monitoring ? google_logging_metric.mcp_server_errors[0].name : null
}

# Deployment Information
output "deployment_info" {
  description = "Complete deployment information for MCP server"
  value = {
    project_id            = var.project_id
    environment           = var.environment
    region                = var.region
    service_account       = google_service_account.mcp_server.email
    secrets_created       = true
    cloud_run_enabled     = var.enable_cloud_run
    monitoring_enabled    = var.enable_monitoring
    load_balancer_enabled = var.enable_load_balancer
  }
  sensitive = false
}

# Security Information
output "security_info" {
  description = "Security configuration information"
  value = {
    secrets_encrypted        = true
    iam_configured           = true
    service_account_created  = true
    compute_access_granted   = var.enable_compute_access
    appengine_access_granted = var.enable_appengine_access
  }
  sensitive = false
}

# Connection Information
output "connection_info" {
  description = "Connection information for MCP server"
  value = {
    service_url   = var.enable_cloud_run ? google_cloud_run_v2_service.mcp_server[0].uri : null
    port          = var.mcp_server_port
    protocol      = "https"
    public_access = var.enable_public_access
  }
  sensitive = false
}
