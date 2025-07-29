# Variables for Security Module

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
}

variable "region" {
  description = "The GCP region"
  type        = string
}

variable "secondary_region" {
  description = "Secondary region for multi-region resources"
  type        = string
  default     = "us-east1"
}

variable "organization_id" {
  description = "The GCP organization ID"
  type        = string
  default     = ""
}

# KMS Configuration
variable "key_rotation_period" {
  description = "Rotation period for KMS keys"
  type        = string
  default     = "7776000s" # 90 days
}

variable "hsm_protection" {
  description = "Use Hardware Security Module for key protection"
  type        = bool
  default     = false
}

# Service Accounts
variable "database_service_account" {
  description = "Service account for database encryption"
  type        = string
}

variable "storage_service_account" {
  description = "Service account for storage encryption"
  type        = string
}

variable "application_service_account" {
  description = "Service account for application secrets"
  type        = string
}

# VPC Service Controls
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

variable "access_level_name" {
  description = "Access level name for VPC Service Controls"
  type        = string
  default     = ""
}

variable "restricted_services" {
  description = "List of services to restrict in VPC Service Controls"
  type        = list(string)
  default = [
    "storage.googleapis.com",
    "bigquery.googleapis.com",
    "bigtable.googleapis.com",
    "sqladmin.googleapis.com",
    "container.googleapis.com",
    "compute.googleapis.com",
    "cloudkms.googleapis.com",
    "secretmanager.googleapis.com",
  ]
}

# Organization Policies
variable "enable_org_policies" {
  description = "Enable organization-level policy constraints"
  type        = bool
  default     = false
}

# Binary Authorization
variable "enable_binary_authorization" {
  description = "Enable Binary Authorization for container images"
  type        = bool
  default     = false
}

variable "gke_cluster_name" {
  description = "Name of the GKE cluster for Binary Authorization"
  type        = string
  default     = ""
}

variable "attestor_public_key_id" {
  description = "Public key ID for Binary Authorization attestor"
  type        = string
  default     = ""
}

variable "attestor_public_key_pem" {
  description = "Public key PEM for Binary Authorization attestor"
  type        = string
  default     = ""
}

# Workload Identity
variable "workload_identity_bindings" {
  description = "Map of Workload Identity bindings"
  type = map(object({
    service_account            = string
    namespace                  = string
    kubernetes_service_account = string
  }))
  default = {}
}

# Audit Logging
variable "audit_log_exempted_members" {
  description = "Members exempted from data access audit logs"
  type        = list(string)
  default     = []
}

# Security Command Center
variable "enable_security_center" {
  description = "Enable Security Command Center notifications"
  type        = bool
  default     = false
}

variable "security_notification_topic" {
  description = "Pub/Sub topic for security notifications"
  type        = string
  default     = ""
}

# Multi-region
variable "enable_multi_region" {
  description = "Enable multi-region replication for secrets"
  type        = bool
  default     = false
}

# Labels
variable "labels" {
  description = "Labels to apply to all resources"
  type        = map(string)
  default     = {}
}
