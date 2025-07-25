# Core Variables (moved from main.tf)
variable "project_id" {
  type        = string
  description = "Project ID"
}

variable "environment" {
  type        = string
  description = "Environment name (production, staging, development)"
}

variable "region" {
  type        = string
  description = "Google Cloud region"
}

variable "service_account_email" {
  type        = string
  description = "Service account email for running the services"
}

# Monitoring Variables
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
  description = "API endpoint URL for uptime checks"
  default     = ""
}

# Bigtable Autoscaling Variables
variable "bigtable_min_nodes" {
  type        = number
  description = "Minimum number of Bigtable nodes"
  default     = 1
}

variable "bigtable_max_nodes" {
  type        = number
  description = "Maximum number of Bigtable nodes"
  default     = 3
}

variable "bigtable_cpu_target" {
  type        = number
  description = "Target CPU utilization for Bigtable autoscaling (0-100)"
  default     = 60
}

variable "bigtable_ssd_size_gb" {
  type        = number
  description = "SSD size per Bigtable node in GB"
  default     = 1024
}

# Security Variables
variable "enable_deletion_protection" {
  type        = bool
  description = "Enable deletion protection for critical resources"
  default     = true
}

variable "enable_vpc_service_controls" {
  type        = bool
  description = "Enable VPC Service Controls"
  default     = false
}

# Cost Optimization Variables
variable "enable_scheduled_scaling" {
  type        = bool
  description = "Enable scheduled scaling for non-production environments"
  default     = false
}

variable "enable_idle_resource_cleanup" {
  type        = bool
  description = "Enable automatic cleanup of idle resources"
  default     = false
}

variable "budget_amount" {
  type        = number
  description = "Monthly budget amount in USD"
  default     = 1000
}

variable "budget_alert_thresholds" {
  type        = list(number)
  description = "Budget alert threshold percentages"
  default     = [50, 80, 90, 100]
}
