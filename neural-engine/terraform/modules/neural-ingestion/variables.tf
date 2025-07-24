# Input variables for the neural-ingestion module

variable "project_id" {
  type        = string
  description = "GCP Project ID"
}

variable "environment" {
  type        = string
  description = "Environment name (development, staging, production)"

  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production."
  }
}

variable "env_short" {
  type        = string
  description = "Short environment name (dev, stg, prod)"

  validation {
    condition     = contains(["dev", "stg", "prod"], var.env_short)
    error_message = "Short environment name must be one of: dev, stg, prod."
  }
}

variable "region" {
  type        = string
  description = "GCP region for resources"
}

variable "common_labels" {
  type        = map(string)
  description = "Common labels to apply to all resources"
  default     = {}
}

variable "ingestion_sa_email" {
  type        = string
  description = "Email of the ingestion service account"
}
