variable "project_id" {
  type        = string
  description = "Google Cloud Project ID"
}

variable "region" {
  type        = string
  description = "Google Cloud region"
  default     = "northamerica-northeast1"  # Montreal
}

variable "environment" {
  type        = string
  description = "Environment (development, staging, production)"
  default     = "development"

  validation {
    condition     = contains(["development", "staging", "production"], var.environment)
    error_message = "Environment must be one of: development, staging, production"
  }
}

variable "signal_types" {
  type        = list(string)
  description = "List of neural signal types to support"
  default     = ["eeg", "ecog", "spikes", "lfp", "emg", "accelerometer", "custom"]
}

variable "bigtable_instance_id" {
  type        = string
  description = "Bigtable instance ID"
  default     = "neural-data"
}

variable "bigtable_table_id" {
  type        = string
  description = "Bigtable table ID for time series data"
  default     = "time-series"
}
