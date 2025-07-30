# Variables for Database Module

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

variable "vpc_id" {
  description = "The VPC network ID"
  type        = string
}

variable "vpc_self_link" {
  description = "The VPC network self link"
  type        = string
}

variable "private_service_connection_id" {
  description = "Private service connection ID for VPC peering"
  type        = string
}

# Cloud SQL PostgreSQL Configuration
variable "postgres_version" {
  description = "PostgreSQL version"
  type        = string
  default     = "POSTGRES_15"
}

variable "db_tier" {
  description = "The machine type for the database"
  type        = string
  default     = "db-g1-small"
}

variable "db_disk_size" {
  description = "The disk size for the database in GB"
  type        = number
  default     = 100
}

variable "db_disk_autoresize_limit" {
  description = "The maximum disk size for autoresize in GB"
  type        = number
  default     = 1000
}

variable "database_name" {
  description = "The name of the database"
  type        = string
  default     = "neural_engine"
}

variable "db_user" {
  description = "Database user name"
  type        = string
  default     = "neural_app"
}

variable "db_password" {
  description = "Database user password"
  type        = string
  sensitive   = true
}

variable "db_readonly_password" {
  description = "Database readonly user password"
  type        = string
  sensitive   = true
  default     = ""
}

variable "create_readonly_user" {
  description = "Whether to create a readonly database user"
  type        = bool
  default     = false
}

variable "enable_high_availability" {
  description = "Enable high availability (regional) for database"
  type        = bool
  default     = false
}

variable "enable_read_replica" {
  description = "Enable read replica for database"
  type        = bool
  default     = false
}

variable "replica_region" {
  description = "Region for read replica (if different from primary)"
  type        = string
  default     = ""
}

variable "replica_tier" {
  description = "Machine type for read replica"
  type        = string
  default     = ""
}

variable "database_flags" {
  description = "Database flags for PostgreSQL tuning"
  type        = map(string)
  default = {
    "max_connections"            = "200"
    "shared_buffers"             = "256MB"
    "effective_cache_size"       = "1GB"
    "log_statement"              = "all"
    "log_min_duration_statement" = "1000" # Log queries over 1 second
  }
}

variable "backup_start_time" {
  description = "Start time for database backups (HH:MM format)"
  type        = string
  default     = "02:00"
}

variable "backup_location" {
  description = "Location for database backups"
  type        = string
  default     = ""
}

variable "backup_retention_count" {
  description = "Number of backups to retain"
  type        = number
  default     = 30
}

variable "transaction_log_retention_days" {
  description = "Number of days to retain transaction logs"
  type        = number
  default     = 7
}

variable "maintenance_day" {
  description = "Day of week for maintenance (1-7, 1 is Monday)"
  type        = number
  default     = 7
}

variable "maintenance_hour" {
  description = "Hour of day for maintenance (0-23)"
  type        = number
  default     = 3
}

variable "database_encryption_key" {
  description = "Cloud KMS key for database encryption"
  type        = string
  default     = ""
}

variable "deletion_protection" {
  description = "Enable deletion protection for database"
  type        = bool
  default     = true
}

# Redis Configuration
variable "redis_memory_gb" {
  description = "Memory size for Redis instance in GB"
  type        = number
  default     = 4
}

variable "redis_zone" {
  description = "Zone for Redis instance"
  type        = string
  default     = "us-central1-a"
}

variable "redis_alternative_zone" {
  description = "Alternative zone for Redis HA"
  type        = string
  default     = "us-central1-b"
}

variable "redis_version" {
  description = "Redis version"
  type        = string
  default     = "REDIS_7_0"
}

variable "redis_tier" {
  description = "Redis tier (BASIC or STANDARD_HA)"
  type        = string
  default     = "BASIC"
}

variable "redis_eviction_policy" {
  description = "Redis eviction policy"
  type        = string
  default     = "volatile-lru"
}

variable "redis_configs" {
  description = "Additional Redis configuration parameters"
  type        = map(string)
  default     = {}
}

variable "redis_persistence_mode" {
  description = "Redis persistence mode (DISABLED, RDB)"
  type        = string
  default     = "RDB"
}

variable "redis_snapshot_period" {
  description = "Redis snapshot period (for RDB persistence)"
  type        = string
  default     = "TWENTY_FOUR_HOURS"
}

variable "redis_snapshot_start_time" {
  description = "Redis snapshot start time in RFC3339 format"
  type        = string
  default     = "2024-01-01T04:00:00Z"
}

variable "maintenance_day_redis" {
  description = "Day of week for Redis maintenance"
  type        = string
  default     = "SUNDAY"
}

variable "maintenance_hour_redis" {
  description = "Hour of day for Redis maintenance"
  type        = number
  default     = 4
}

variable "enable_streaming_redis" {
  description = "Enable separate Redis instance for streaming"
  type        = bool
  default     = false
}

variable "streaming_redis_memory_gb" {
  description = "Memory size for streaming Redis instance"
  type        = number
  default     = 8
}

# BigQuery Configuration
variable "bigquery_location" {
  description = "Location for BigQuery dataset"
  type        = string
  default     = "US"
}

variable "default_table_expiration_days" {
  description = "Default table expiration in days"
  type        = number
  default     = 365
}

variable "session_retention_days" {
  description = "Retention period for session data in days"
  type        = number
  default     = 365
}

variable "dataset_owner_email" {
  description = "Email of the dataset owner"
  type        = string
}

variable "neural_service_account_email" {
  description = "Service account email for neural engine"
  type        = string
}

variable "analytics_reader_group" {
  description = "Google group for analytics readers"
  type        = string
  default     = ""
}

variable "bigquery_encryption_key" {
  description = "Cloud KMS key for BigQuery encryption"
  type        = string
  default     = ""
}

variable "enable_scheduled_queries" {
  description = "Enable scheduled queries for data aggregation"
  type        = bool
  default     = false
}

# Labels
variable "labels" {
  description = "Labels to apply to all resources"
  type        = map(string)
  default     = {}
}
