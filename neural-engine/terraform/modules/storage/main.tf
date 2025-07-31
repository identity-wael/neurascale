# Storage Module for NeuraScale Neural Engine
# Manages GCS buckets with lifecycle policies and security

# Random suffix for bucket names to ensure uniqueness
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# Main data storage bucket for neural recordings
resource "google_storage_bucket" "neural_data" {
  name     = "${var.project_id}-neural-data-${random_id.bucket_suffix.hex}"
  location = var.storage_location

  # HIPAA-compliant storage class
  storage_class = var.storage_class

  # Uniform bucket-level access for better security
  uniform_bucket_level_access = true

  # Versioning for data protection
  versioning {
    enabled = true
  }

  # Lifecycle rules for cost optimization
  dynamic "lifecycle_rule" {
    for_each = var.enable_lifecycle_policies ? [1] : []
    content {
      condition {
        age                   = var.nearline_transition_days
        matches_storage_class = ["STANDARD"]
      }
      action {
        type          = "SetStorageClass"
        storage_class = "NEARLINE"
      }
    }
  }

  dynamic "lifecycle_rule" {
    for_each = var.enable_lifecycle_policies ? [1] : []
    content {
      condition {
        age                   = var.coldline_transition_days
        matches_storage_class = ["NEARLINE"]
      }
      action {
        type          = "SetStorageClass"
        storage_class = "COLDLINE"
      }
    }
  }

  dynamic "lifecycle_rule" {
    for_each = var.enable_lifecycle_policies ? [1] : []
    content {
      condition {
        age                   = var.archive_transition_days
        matches_storage_class = ["COLDLINE"]
      }
      action {
        type          = "SetStorageClass"
        storage_class = "ARCHIVE"
      }
    }
  }

  # Delete old versions after retention period
  dynamic "lifecycle_rule" {
    for_each = var.version_retention_days > 0 ? [1] : []
    content {
      condition {
        age                = var.version_retention_days
        num_newer_versions = 1
      }
      action {
        type = "Delete"
      }
    }
  }

  # Retention policy for compliance
  retention_policy {
    retention_period = var.retention_period_days * 86400 # Convert to seconds
    is_locked        = var.lock_retention_policy
  }

  # CORS configuration for web access
  dynamic "cors" {
    for_each = var.enable_cors ? [1] : []
    content {
      origin          = var.cors_origins
      method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
      response_header = ["*"]
      max_age_seconds = 3600
    }
  }

  # Encryption with customer-managed keys
  dynamic "encryption" {
    for_each = var.storage_encryption_key != "" ? [1] : []
    content {
      default_kms_key_name = var.storage_encryption_key
    }
  }

  # Logging configuration
  dynamic "logging" {
    for_each = var.enable_logging ? [1] : []
    content {
      log_bucket        = google_storage_bucket.logs[0].name
      log_object_prefix = "neural-data/"
    }
  }

  labels = merge(
    var.labels,
    {
      environment = var.environment
      data_type   = "neural-recordings"
      compliance  = "hipaa"
    }
  )

  # Prevent accidental deletion
  force_destroy = false

  lifecycle {
    prevent_destroy = true
  }
}

# ML model storage bucket
resource "google_storage_bucket" "ml_models" {
  name     = "${var.project_id}-ml-models-${random_id.bucket_suffix.hex}"
  location = var.storage_location

  storage_class               = "STANDARD"
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  # Keep multiple model versions for rollback
  lifecycle_rule {
    condition {
      num_newer_versions = var.model_version_retention_count
      with_state         = "ARCHIVED"
    }
    action {
      type = "Delete"
    }
  }

  # Archive old models
  dynamic "lifecycle_rule" {
    for_each = var.enable_lifecycle_policies ? [1] : []
    content {
      condition {
        age = var.model_archive_days
      }
      action {
        type          = "SetStorageClass"
        storage_class = "COLDLINE"
      }
    }
  }

  dynamic "encryption" {
    for_each = var.storage_encryption_key != "" ? [1] : []
    content {
      default_kms_key_name = var.storage_encryption_key
    }
  }

  labels = merge(
    var.labels,
    {
      environment = var.environment
      data_type   = "ml-models"
    }
  )
}

# Temporary processing bucket
resource "google_storage_bucket" "temp_processing" {
  name     = "${var.project_id}-temp-processing-${random_id.bucket_suffix.hex}"
  location = var.storage_location

  storage_class               = "STANDARD"
  uniform_bucket_level_access = true

  # Auto-delete temporary files
  lifecycle_rule {
    condition {
      age = var.temp_retention_days
    }
    action {
      type = "Delete"
    }
  }

  # Delete incomplete multipart uploads
  lifecycle_rule {
    condition {
      age = 7
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }

  labels = merge(
    var.labels,
    {
      environment = var.environment
      data_type   = "temporary"
    }
  )

  force_destroy = true
}

# Backup bucket for critical data
resource "google_storage_bucket" "backups" {
  name     = "${var.project_id}-backups-${random_id.bucket_suffix.hex}"
  location = var.backup_location != "" ? var.backup_location : var.storage_location

  storage_class               = "NEARLINE"
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  # Lifecycle for backup rotation
  dynamic "lifecycle_rule" {
    for_each = var.backup_retention_days > 0 ? [1] : []
    content {
      condition {
        age = var.backup_retention_days
      }
      action {
        type = "Delete"
      }
    }
  }

  # Archive very old backups
  dynamic "lifecycle_rule" {
    for_each = var.enable_lifecycle_policies ? [1] : []
    content {
      condition {
        age = 180
      }
      action {
        type          = "SetStorageClass"
        storage_class = "ARCHIVE"
      }
    }
  }

  retention_policy {
    retention_period = var.backup_retention_days * 86400
    is_locked        = var.lock_backup_retention
  }

  dynamic "encryption" {
    for_each = var.storage_encryption_key != "" ? [1] : []
    content {
      default_kms_key_name = var.storage_encryption_key
    }
  }

  labels = merge(
    var.labels,
    {
      environment = var.environment
      data_type   = "backups"
      compliance  = "hipaa"
    }
  )

  lifecycle {
    prevent_destroy = true
  }
}

# Logs bucket (if logging enabled)
resource "google_storage_bucket" "logs" {
  count = var.enable_logging ? 1 : 0

  name     = "${var.project_id}-storage-logs-${random_id.bucket_suffix.hex}"
  location = var.storage_location

  storage_class               = "STANDARD"
  uniform_bucket_level_access = true

  # Auto-delete old logs
  lifecycle_rule {
    condition {
      age = var.log_retention_days
    }
    action {
      type = "Delete"
    }
  }

  # Compress old logs
  dynamic "lifecycle_rule" {
    for_each = var.enable_lifecycle_policies ? [1] : []
    content {
      condition {
        age = 30
      }
      action {
        type          = "SetStorageClass"
        storage_class = "NEARLINE"
      }
    }
  }

  labels = merge(
    var.labels,
    {
      environment = var.environment
      data_type   = "logs"
    }
  )

  force_destroy = true
}

# GCS bucket for Cloud Functions source code
resource "google_storage_bucket" "functions_source" {
  name     = "${var.project_id}-functions-source-${random_id.bucket_suffix.hex}"
  location = var.storage_location

  storage_class               = "STANDARD"
  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  # Keep limited function versions
  lifecycle_rule {
    condition {
      num_newer_versions = 10
      with_state         = "ARCHIVED"
    }
    action {
      type = "Delete"
    }
  }

  labels = merge(
    var.labels,
    {
      environment = var.environment
      data_type   = "function-source"
    }
  )
}

# IAM bindings for neural data bucket
resource "google_storage_bucket_iam_member" "neural_data_viewer" {
  bucket = google_storage_bucket.neural_data.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${var.neural_service_account_email}"
}

resource "google_storage_bucket_iam_member" "neural_data_creator" {
  bucket = google_storage_bucket.neural_data.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${var.neural_service_account_email}"
}

# IAM bindings for ML models bucket
resource "google_storage_bucket_iam_member" "ml_models_admin" {
  bucket = google_storage_bucket.ml_models.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${var.neural_service_account_email}"
}

# IAM bindings for temp processing bucket
resource "google_storage_bucket_iam_member" "temp_processing_admin" {
  bucket = google_storage_bucket.temp_processing.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${var.neural_service_account_email}"
}

# IAM bindings for backups bucket
resource "google_storage_bucket_iam_member" "backups_creator" {
  bucket = google_storage_bucket.backups.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${var.neural_service_account_email}"
}

# Storage Transfer Service for automated backups (if enabled)
resource "google_storage_transfer_job" "backup_transfer" {
  count = var.enable_storage_transfer ? 1 : 0

  description = "Automated backup transfer for neural data"
  project     = var.project_id

  transfer_spec {
    gcs_data_source {
      bucket_name = google_storage_bucket.neural_data.name
      path        = var.backup_path_prefix
    }

    gcs_data_sink {
      bucket_name = google_storage_bucket.backups.name
      path        = "neural-data-backups/"
    }

    transfer_options {
      delete_objects_unique_in_sink              = false
      overwrite_objects_already_existing_in_sink = false
    }
  }

  schedule {
    schedule_start_date {
      year  = tonumber(formatdate("YYYY", timestamp()))
      month = tonumber(formatdate("MM", timestamp()))
      day   = tonumber(formatdate("DD", timestamp()))
    }

    start_time_of_day {
      hours   = var.backup_hour
      minutes = 0
      seconds = 0
      nanos   = 0
    }

    repeat_interval = "86400s" # Daily
  }

  depends_on = [
    google_storage_bucket.neural_data,
    google_storage_bucket.backups
  ]
}

# Bucket notifications (if enabled)
resource "google_storage_notification" "neural_data_notification" {
  count = var.enable_notifications ? 1 : 0

  bucket         = google_storage_bucket.neural_data.name
  payload_format = "JSON_API_V1"
  topic          = var.notification_topic_id
  event_types    = ["OBJECT_FINALIZE", "OBJECT_DELETE"]

  custom_attributes = {
    bucket_type = "neural-data"
    environment = var.environment
  }

  depends_on = [google_storage_bucket.neural_data]
}
