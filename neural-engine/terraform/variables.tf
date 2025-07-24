# Input variables for Neural Engine infrastructure

variable "project_id" {
  type        = string
  description = "GCP Project ID (e.g., development-neurascale, staging-neurascale, production-neurascale)"

  validation {
    condition = can(regex("^(development|staging|production)-neurascale$", var.project_id))
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
