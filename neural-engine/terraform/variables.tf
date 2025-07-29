# Input variables for Neural Engine infrastructure

variable "project_id" {
  type        = string
  description = "GCP Project ID (e.g., development-neurascale, staging-neurascale, production-neurascale)"

  validation {
    condition     = can(regex("^(development|staging|production)-neurascale$", var.project_id))
    error_message = "Project ID must be in format: {environment}-neurascale where environment is development, staging, or production."
  }
}

variable "environment" {
  type        = string
  description = "Environment name (development, staging, production)"

  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production."
  }
}

variable "region" {
  type        = string
  description = "GCP region for resources"
  default     = "northamerica-northeast1"
}

variable "github_actions_service_account" {
  type        = string
  description = "Service account email used by GitHub Actions for deployments"
  default     = "github-actions@neurascale.iam.gserviceaccount.com"
}

# Monitoring and alerting variables
variable "enable_monitoring_alerts" {
  type        = bool
  description = "Enable monitoring alerts"
  default     = true
}

variable "alert_notification_channels" {
  type        = list(string)
  description = "List of notification channel IDs for alerts"
  default     = []
}

variable "api_endpoint_url" {
  type        = string
  description = "API endpoint URL for uptime checks (leave empty to skip)"
  default     = ""
}

# Bigtable configuration variables
variable "bigtable_nodes" {
  type        = number
  description = "Number of Bigtable nodes"
  default     = 1
}

variable "bigtable_min_nodes" {
  type        = number
  description = "Minimum number of Bigtable nodes for autoscaling"
  default     = 1
}

variable "bigtable_max_nodes" {
  type        = number
  description = "Maximum number of Bigtable nodes for autoscaling"
  default     = 3
}

variable "bigtable_ssd_size_gb" {
  type        = number
  description = "Bigtable SSD size in GB"
  default     = 256
}

variable "bigtable_cpu_target" {
  type        = number
  description = "Target CPU utilization for Bigtable autoscaling"
  default     = 60
}

# Security configuration
variable "enable_deletion_protection" {
  type        = bool
  description = "Enable deletion protection for critical resources"
  default     = false
}

variable "enable_vpc_service_controls" {
  type        = bool
  description = "Enable VPC Service Controls"
  default     = false
}

# Cost optimization
variable "enable_scheduled_scaling" {
  type        = bool
  description = "Enable scheduled scaling for non-production environments"
  default     = false
}

variable "enable_bigtable_autoscaling" {
  type        = bool
  description = "Enable Bigtable autoscaling for production"
  default     = false
}

variable "bigtable_nodes_dev" {
  type        = number
  description = "Number of Bigtable nodes for development during business hours"
  default     = 1
}

variable "bigtable_min_nodes_dev" {
  type        = number
  description = "Minimum number of Bigtable nodes for development after hours"
  default     = 1
}

variable "cost_center" {
  type        = string
  description = "Cost center for billing allocation"
  default     = "neural-research"
}

variable "budget_amount" {
  type        = string
  description = "Monthly budget amount in USD"
  default     = "1000"
}

variable "billing_account_id" {
  type        = string
  description = "Billing account ID for budget alerts"
  default     = ""
}

variable "budget_notification_channels" {
  type        = list(string)
  description = "Notification channels for budget alerts"
  default     = []
}

variable "enable_cloud_functions" {
  type        = bool
  description = "Enable Cloud Functions deployment"
  default     = false
}

# MCP Server Configuration
variable "enable_mcp_cloud_run" {
  type        = bool
  description = "Deploy MCP server as Cloud Run service"
  default     = false
}

variable "mcp_server_image" {
  type        = string
  description = "Container image for MCP server"
  default     = "gcr.io/PROJECT_ID/mcp-server:latest"
}

variable "mcp_min_instances" {
  type        = number
  description = "Minimum number of MCP server instances"
  default     = 0
}

variable "mcp_max_instances" {
  type        = number
  description = "Maximum number of MCP server instances"
  default     = 10
}

variable "enable_mcp_public_access" {
  type        = bool
  description = "Allow public access to MCP server"
  default     = false
}

variable "mcp_server_port" {
  type        = number
  description = "Port for MCP server"
  default     = 8080
}
