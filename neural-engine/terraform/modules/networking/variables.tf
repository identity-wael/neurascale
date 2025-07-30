# Variables for Networking Module

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production."
  }
}

variable "region" {
  description = "The GCP region for resources"
  type        = string
  default     = "us-central1"
}

# Network CIDR configurations
variable "gke_subnet_cidr" {
  description = "CIDR range for GKE subnet"
  type        = string
  default     = "10.0.0.0/20" # 4,096 IPs
}

variable "private_subnet_cidr" {
  description = "CIDR range for private subnet (databases, internal services)"
  type        = string
  default     = "10.0.16.0/20" # 4,096 IPs
}

variable "pods_cidr" {
  description = "Secondary CIDR range for GKE pods"
  type        = string
  default     = "10.1.0.0/16" # 65,536 IPs
}

variable "services_cidr" {
  description = "Secondary CIDR range for GKE services"
  type        = string
  default     = "10.2.0.0/20" # 4,096 IPs
}

# Security settings
variable "enable_restrictive_egress" {
  description = "Enable restrictive egress rules (deny all by default)"
  type        = bool
  default     = false
}

variable "create_private_dns_zone" {
  description = "Create private DNS zone for Google APIs"
  type        = bool
  default     = true
}

# Additional allowed CIDR ranges
variable "additional_allowed_ranges" {
  description = "Additional CIDR ranges to allow in firewall rules"
  type        = list(string)
  default     = []
}

# Tags
variable "labels" {
  description = "Labels to apply to all resources"
  type        = map(string)
  default     = {}
}

variable "apis_enabled" {
  description = "Flag indicating that all APIs have been enabled"
  type        = bool
  default     = true
}
