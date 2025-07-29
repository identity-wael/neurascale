# Variables for MCP Server Infrastructure Module

variable "project_id" {
  type        = string
  description = "GCP Project ID"
}

variable "region" {
  type        = string
  description = "GCP region for resources"
  default     = "us-central1"
}

variable "environment" {
  type        = string
  description = "Environment name (development, staging, production)"
  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production."
  }
}

variable "apis_enabled" {
  type        = any
  description = "Dependency on enabled APIs (from project-apis module)"
  default     = null
}

# Service Account Configuration
variable "enable_compute_access" {
  type        = bool
  description = "Grant compute service account access to MCP secrets"
  default     = true
}

variable "enable_appengine_access" {
  type        = bool
  description = "Grant App Engine service account access to MCP secrets"
  default     = false
}

variable "github_actions_service_account" {
  type        = string
  description = "Service account email used by GitHub Actions"
  default     = "github-actions@neurascale.iam.gserviceaccount.com"
}

# Cloud Run Configuration
variable "enable_cloud_run" {
  type        = bool
  description = "Deploy MCP server as Cloud Run service"
  default     = false
}

variable "mcp_server_image" {
  type        = string
  description = "Container image for MCP server"
  default     = "gcr.io/PROJECT_ID/mcp-server:latest"
}

variable "min_instances" {
  type        = number
  description = "Minimum number of Cloud Run instances"
  default     = 0
}

variable "max_instances" {
  type        = number
  description = "Maximum number of Cloud Run instances"
  default     = 10
}

variable "enable_public_access" {
  type        = bool
  description = "Allow public access to Cloud Run service"
  default     = false
}

# Load Balancer Configuration
variable "enable_load_balancer" {
  type        = bool
  description = "Create load balancer for MCP server"
  default     = false
}

# Monitoring Configuration
variable "enable_monitoring" {
  type        = bool
  description = "Enable monitoring and alerting for MCP server"
  default     = true
}

variable "notification_channels" {
  type        = list(string)
  description = "Notification channels for alerts"
  default     = []
}

# Network Configuration
variable "vpc_network" {
  type        = string
  description = "VPC network for MCP server"
  default     = "default"
}

variable "subnet_name" {
  type        = string
  description = "Subnet name for MCP server"
  default     = "default"
}

# Security Configuration
variable "allowed_source_ranges" {
  type        = list(string)
  description = "Source IP ranges allowed to access MCP server"
  default     = ["0.0.0.0/0"]
}

# MCP Server Configuration
variable "mcp_server_port" {
  type        = number
  description = "Port for MCP server"
  default     = 8080
}

variable "websocket_timeout" {
  type        = number
  description = "WebSocket timeout in seconds"
  default     = 300
}

variable "rate_limit_requests_per_minute" {
  type        = number
  description = "Rate limit for MCP server requests per minute"
  default     = 60
}

# Secret Management Configuration
variable "secret_rotation_enabled" {
  type        = bool
  description = "Enable automatic secret rotation"
  default     = false
}

variable "secret_rotation_period" {
  type        = string
  description = "Secret rotation period (e.g., '90d')"
  default     = "90d"
}

# Backup and Recovery
variable "enable_secret_backup" {
  type        = bool
  description = "Enable secret backup to Cloud Storage"
  default     = false
}

variable "backup_bucket_name" {
  type        = string
  description = "Cloud Storage bucket for secret backups"
  default     = ""
}

# Cost Optimization
variable "enable_cost_optimization" {
  type        = bool
  description = "Enable cost optimization features"
  default     = true
}

variable "cost_budget_amount" {
  type        = number
  description = "Monthly budget amount for MCP server resources"
  default     = 100
}

# Development and Testing
variable "enable_development_features" {
  type        = bool
  description = "Enable development and testing features"
  default     = false
}

variable "mock_data_enabled" {
  type        = bool
  description = "Enable mock data generation for testing"
  default     = false
}
