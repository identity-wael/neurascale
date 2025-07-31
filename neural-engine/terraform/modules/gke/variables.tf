# Variables for GKE Module

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

variable "zone" {
  description = "The GCP zone (for zonal clusters)"
  type        = string
  default     = ""
}

variable "regional_cluster" {
  description = "Whether to create a regional cluster (true) or zonal cluster (false)"
  type        = bool
  default     = true
}

# Network configuration
variable "vpc_id" {
  description = "The VPC network ID"
  type        = string
}

variable "subnet_id" {
  description = "The subnet ID for the cluster"
  type        = string
}

variable "pods_secondary_range_name" {
  description = "The name of the secondary range for pods"
  type        = string
}

variable "services_secondary_range_name" {
  description = "The name of the secondary range for services"
  type        = string
}

variable "master_cidr" {
  description = "CIDR block for the cluster master"
  type        = string
  default     = "172.16.0.0/28"
}

# Cluster configuration
variable "kubernetes_version" {
  description = "The Kubernetes version for the cluster"
  type        = string
  default     = "" # Let GKE choose the default version
}

variable "enable_private_endpoint" {
  description = "Whether to enable private endpoint (no public access to master)"
  type        = bool
  default     = false
}

variable "authorized_networks" {
  description = "List of authorized networks for master access"
  type = list(object({
    cidr_block   = string
    display_name = string
  }))
  default = []
}

# Security configuration
variable "enable_binary_authorization" {
  description = "Enable binary authorization for container images"
  type        = bool
  default     = true
}

variable "database_encryption_key" {
  description = "The Cloud KMS key for database encryption"
  type        = string
  default     = ""
}

variable "node_service_account_email" {
  description = "Service account email for node pools"
  type        = string
}

# Node pool configurations

## General pool
variable "general_pool_node_count" {
  description = "Initial node count for general pool"
  type        = number
  default     = 3
}

variable "general_pool_min_nodes" {
  description = "Minimum nodes for general pool autoscaling"
  type        = number
  default     = 1
}

variable "general_pool_max_nodes" {
  description = "Maximum nodes for general pool autoscaling"
  type        = number
  default     = 10
}

variable "general_pool_machine_type" {
  description = "Machine type for general pool"
  type        = string
  default     = "n2-standard-4"
}

variable "general_pool_disk_size" {
  description = "Disk size in GB for general pool nodes"
  type        = number
  default     = 100
}

## Neural compute pool
variable "neural_pool_node_count" {
  description = "Initial node count for neural compute pool"
  type        = number
  default     = 2
}

variable "neural_pool_min_nodes" {
  description = "Minimum nodes for neural pool autoscaling"
  type        = number
  default     = 1
}

variable "neural_pool_max_nodes" {
  description = "Maximum nodes for neural pool autoscaling"
  type        = number
  default     = 8
}

variable "neural_pool_machine_type" {
  description = "Machine type for neural compute pool"
  type        = string
  default     = "n2-highmem-8"
}

variable "neural_pool_disk_size" {
  description = "Disk size in GB for neural pool nodes"
  type        = number
  default     = 200
}

variable "neural_pool_local_ssd_count" {
  description = "Number of local SSDs for neural pool nodes"
  type        = number
  default     = 0
}

## GPU pool
variable "enable_gpu_pool" {
  description = "Whether to create a GPU node pool"
  type        = bool
  default     = false
}

variable "gpu_pool_node_count" {
  description = "Initial node count for GPU pool"
  type        = number
  default     = 1
}

variable "gpu_pool_min_nodes" {
  description = "Minimum nodes for GPU pool autoscaling"
  type        = number
  default     = 0
}

variable "gpu_pool_max_nodes" {
  description = "Maximum nodes for GPU pool autoscaling"
  type        = number
  default     = 3
}

variable "gpu_pool_machine_type" {
  description = "Machine type for GPU pool"
  type        = string
  default     = "n1-standard-4"
}

variable "gpu_pool_preemptible" {
  description = "Whether GPU nodes should be preemptible"
  type        = bool
  default     = false
}

variable "gpu_type" {
  description = "Type of GPU to attach"
  type        = string
  default     = "nvidia-tesla-t4"
}

variable "gpu_count_per_node" {
  description = "Number of GPUs per node"
  type        = number
  default     = 1
}

# Maintenance window
variable "maintenance_start_time" {
  description = "Start time for maintenance window"
  type        = string
  default     = "2025-01-01T09:00:00Z"
}

variable "maintenance_end_time" {
  description = "End time for maintenance window"
  type        = string
  default     = "2025-01-01T17:00:00Z"
}

# Resource usage export
variable "resource_usage_dataset_id" {
  description = "BigQuery dataset ID for resource usage export"
  type        = string
  default     = ""
}

# Labels
variable "labels" {
  description = "Labels to apply to resources"
  type        = map(string)
  default     = {}
}
