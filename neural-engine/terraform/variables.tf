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

# Networking variables
variable "gke_subnet_cidr" {
  description = "CIDR range for GKE subnet"
  type        = string
  default     = "10.0.0.0/20"
}

variable "private_subnet_cidr" {
  description = "CIDR range for private subnet"
  type        = string
  default     = "10.0.16.0/20"
}

variable "pods_cidr" {
  description = "CIDR range for GKE pods"
  type        = string
  default     = "10.1.0.0/16"
}

variable "services_cidr" {
  description = "CIDR range for GKE services"
  type        = string
  default     = "10.2.0.0/20"
}

# GKE variables
variable "enable_gke_cluster" {
  description = "Enable GKE cluster deployment"
  type        = bool
  default     = false
}

variable "gke_general_machine_type" {
  description = "Machine type for general GKE node pool"
  type        = string
  default     = "n2-standard-4"
}

variable "gke_neural_machine_type" {
  description = "Machine type for neural compute GKE node pool"
  type        = string
  default     = "n2-highmem-8"
}

variable "enable_gpu_pool" {
  description = "Enable GPU node pool in GKE"
  type        = bool
  default     = false
}

variable "gpu_type" {
  description = "Type of GPU for GKE nodes"
  type        = string
  default     = "nvidia-tesla-t4"
}

# Database variables
variable "db_tier" {
  description = "Cloud SQL instance tier"
  type        = string
  default     = "db-g1-small"
}

variable "db_disk_size" {
  description = "Cloud SQL disk size in GB"
  type        = number
  default     = 100
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "redis_memory_gb" {
  description = "Redis memory size in GB"
  type        = number
  default     = 4
}

variable "redis_tier" {
  description = "Redis tier (BASIC or STANDARD_HA)"
  type        = string
  default     = "BASIC"
}

variable "enable_db_high_availability" {
  description = "Enable high availability for Cloud SQL"
  type        = bool
  default     = false
}

# Storage variables
variable "storage_location" {
  description = "Location for storage buckets"
  type        = string
  default     = "US"
}

variable "backup_location" {
  description = "Location for backup buckets (different region for DR)"
  type        = string
  default     = ""
}

variable "enable_storage_lifecycle_policies" {
  description = "Enable lifecycle policies for storage cost optimization"
  type        = bool
  default     = true
}

variable "data_retention_days" {
  description = "Data retention period in days (HIPAA requires 7 years)"
  type        = number
  default     = 2555
}

# Security variables
variable "enable_enhanced_security" {
  description = "Enable enhanced security features (KMS, Secret Manager)"
  type        = bool
  default     = true
}

variable "enable_kms_encryption" {
  description = "Enable KMS encryption for storage and databases"
  type        = bool
  default     = true
}

variable "organization_id" {
  description = "GCP organization ID for org-level policies"
  type        = string
  default     = ""
}

variable "enable_vpc_service_controls" {
  description = "Enable VPC Service Controls"
  type        = bool
  default     = false
}

variable "access_policy_id" {
  description = "Access Context Manager policy ID"
  type        = string
  default     = ""
}

variable "enable_binary_authorization" {
  description = "Enable Binary Authorization for container images"
  type        = bool
  default     = false
}

# Cost optimization variables
variable "billing_account_id" {
  description = "Billing account ID for budget alerts"
  type        = string
  default     = ""
}

variable "budget_amount" {
  description = "Monthly budget amount in USD"
  type        = string
  default     = "5000"
}

variable "budget_notification_emails" {
  description = "Email addresses for budget notifications"
  type        = list(string)
  default     = []
}

variable "budget_pubsub_topic" {
  description = "Pub/Sub topic for budget notifications"
  type        = string
  default     = ""
}

variable "budget_services" {
  description = "Services to include in budget (empty for all)"
  type        = list(string)
  default     = []
}

variable "cost_center" {
  description = "Cost center label for budget tracking"
  type        = string
  default     = "neural-research"
}

variable "enable_scheduled_scaling" {
  description = "Enable scheduled scaling for dev/staging environments"
  type        = bool
  default     = false
}

variable "enable_cost_analysis" {
  description = "Enable BigQuery cost analysis"
  type        = bool
  default     = false
}

variable "billing_export_dataset" {
  description = "BigQuery dataset containing billing export"
  type        = string
  default     = ""
}

variable "bigquery_location" {
  description = "Location for BigQuery datasets"
  type        = string
  default     = "US"
}
