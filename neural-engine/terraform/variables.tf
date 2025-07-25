# Input variables for Neural Engine infrastructure

variable "project_id" {
  type        = string
  description = "GCP Project ID (e.g., development-neurascale, staging-neurascale, production-neurascale)"

  validation {
    condition     = can(regex("^(development|staging|production)-neurascale$", var.project_id))
    error_message = "Project ID must be in format: {environment}-neurascale where environment is development, staging, or production."
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
