# Variables for Storage Module

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
}

variable "storage_location" {
  description = "Location for storage buckets"
  type        = string
  default     = "US"
}

variable "backup_location" {
  description = "Location for backup buckets (different region for disaster recovery)"
  type        = string
  default     = ""
}

variable "storage_class" {
  description = "Default storage class for buckets"
  type        = string
  default     = "STANDARD"
}

# Lifecycle policies
variable "enable_lifecycle_policies" {
  description = "Enable lifecycle policies for cost optimization"
  type        = bool
  default     = true
}

variable "nearline_transition_days" {
  description = "Days before transitioning to Nearline storage"
  type        = number
  default     = 30
}

variable "coldline_transition_days" {
  description = "Days before transitioning to Coldline storage"
  type        = number
  default     = 90
}

variable "archive_transition_days" {
  description = "Days before transitioning to Archive storage"
  type        = number
  default     = 365
}

variable "version_retention_days" {
  description = "Days to retain non-current versions (0 to keep forever)"
  type        = number
  default     = 90
}

variable "temp_retention_days" {
  description = "Days to retain temporary processing files"
  type        = number
  default     = 7
}

variable "log_retention_days" {
  description = "Days to retain storage logs"
  type        = number
  default     = 90
}

variable "model_archive_days" {
  description = "Days before archiving ML models"
  type        = number
  default     = 180
}

variable "model_version_retention_count" {
  description = "Number of model versions to retain"
  type        = number
  default     = 10
}

# Retention policies
variable "retention_period_days" {
  description = "Retention period for neural data in days"
  type        = number
  default     = 2555 # 7 years for HIPAA compliance
}

variable "lock_retention_policy" {
  description = "Lock the retention policy (cannot be reduced)"
  type        = bool
  default     = false
}

variable "backup_retention_days" {
  description = "Retention period for backups in days"
  type        = number
  default     = 365
}

variable "lock_backup_retention" {
  description = "Lock the backup retention policy"
  type        = bool
  default     = false
}

# Encryption
variable "storage_encryption_key" {
  description = "Cloud KMS key for storage encryption"
  type        = string
  default     = ""
}

# Service account
variable "neural_service_account_email" {
  description = "Service account email for neural engine"
  type        = string
}

# CORS configuration
variable "enable_cors" {
  description = "Enable CORS for web access"
  type        = bool
  default     = false
}

variable "cors_origins" {
  description = "Allowed CORS origins"
  type        = list(string)
  default     = ["*"]
}

# Logging
variable "enable_logging" {
  description = "Enable storage access logging"
  type        = bool
  default     = true
}

# Storage Transfer Service
variable "enable_storage_transfer" {
  description = "Enable automated backup transfers"
  type        = bool
  default     = false
}

variable "backup_path_prefix" {
  description = "Path prefix for files to backup"
  type        = string
  default     = ""
}

variable "backup_hour" {
  description = "Hour of day for backup transfers (0-23)"
  type        = number
  default     = 2
}

# Notifications
variable "enable_notifications" {
  description = "Enable Pub/Sub notifications for bucket events"
  type        = bool
  default     = false
}

variable "notification_topic_id" {
  description = "Pub/Sub topic ID for notifications"
  type        = string
  default     = ""
}

# Labels
variable "labels" {
  description = "Labels to apply to all resources"
  type        = map(string)
  default     = {}
}
