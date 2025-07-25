# Cloud Functions for Neural Data Processing

# Local variables for function configuration
locals {
  function_source_dir = "${path.module}/../../../functions"
  function_types      = toset(["eeg", "ecog", "lfp", "spikes", "emg", "accelerometer"])
}

# ZIP the function source code for each signal type
data "archive_file" "function_source" {
  for_each = var.enable_cloud_functions ? local.function_types : toset([])

  type        = "zip"
  source_dir  = "${local.function_source_dir}/${each.key}"
  output_path = "${path.module}/tmp/function-${each.key}.zip"
}

# Upload function source to GCS
resource "google_storage_bucket_object" "function_source" {
  for_each = var.enable_cloud_functions ? local.function_types : toset([])

  name   = "functions/${each.key}-${data.archive_file.function_source[each.key].output_md5}.zip"
  bucket = google_storage_bucket.functions.name
  source = data.archive_file.function_source[each.key].output_path
}

# Cloud Functions (2nd gen) for processing neural streams
resource "google_cloudfunctions2_function" "process_neural_stream" {
  for_each = var.enable_cloud_functions ? local.function_types : toset([])

  name     = "process-neural-${each.key}-${var.environment}"
  location = var.region

  description = "Process ${upper(each.key)} neural data streams"

  build_config {
    runtime     = "python312"
    entry_point = "process_neural_stream"

    source {
      storage_source {
        bucket = google_storage_bucket.functions.name
        object = google_storage_bucket_object.function_source[each.key].name
      }
    }

    environment_variables = {
      PROJECT_ID        = var.project_id
      ENVIRONMENT       = var.environment
      SIGNAL_TYPE       = each.key
      BIGTABLE_INSTANCE = google_bigtable_instance.neural_data.name
    }
  }

  service_config {
    max_instance_count = var.function_max_instances
    min_instance_count = var.function_min_instances
    available_memory   = "${var.function_memory_mb}M"
    timeout_seconds    = var.function_timeout_seconds

    environment_variables = {
      PROJECT_ID        = var.project_id
      ENVIRONMENT       = var.environment
      SIGNAL_TYPE       = each.key
      BIGTABLE_INSTANCE = google_bigtable_instance.neural_data.name
      LOG_LEVEL         = var.environment == "production" ? "INFO" : "DEBUG"
    }

    ingress_settings               = "ALLOW_INTERNAL_ONLY"
    all_traffic_on_latest_revision = true
    service_account_email          = var.service_account_email
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic   = google_pubsub_topic.neural_data[each.key].id
    retry_policy   = "RETRY_POLICY_RETRY"
  }

  labels = {
    environment = var.environment
    signal_type = each.key
    version     = "v1"
  }
}

# Cloud Scheduler for scaling functions based on time of day (optional)
# Variable is already defined in variables.tf

resource "google_cloud_scheduler_job" "scale_up" {
  for_each = var.enable_scheduled_scaling && var.environment != "production" ? local.function_types : toset([])

  name             = "scale-up-${each.key}-${var.environment}"
  region           = var.region
  schedule         = "0 8 * * MON-FRI" # 8 AM on weekdays
  time_zone        = "America/Los_Angeles"
  attempt_deadline = "320s"

  http_target {
    uri         = "https://cloudfunctions.googleapis.com/v2/projects/${var.project_id}/locations/${var.region}/functions/process-neural-${each.key}-${var.environment}"
    http_method = "PATCH"

    headers = {
      "Content-Type" = "application/json"
    }

    body = base64encode(jsonencode({
      serviceConfig = {
        minInstanceCount = 1
      }
    }))

    oauth_token {
      service_account_email = var.service_account_email
    }
  }
}

resource "google_cloud_scheduler_job" "scale_down" {
  for_each = var.enable_scheduled_scaling && var.environment != "production" ? local.function_types : toset([])

  name             = "scale-down-${each.key}-${var.environment}"
  region           = var.region
  schedule         = "0 20 * * MON-FRI" # 8 PM on weekdays
  time_zone        = "America/Los_Angeles"
  attempt_deadline = "320s"

  http_target {
    uri         = "https://cloudfunctions.googleapis.com/v2/projects/${var.project_id}/locations/${var.region}/functions/process-neural-${each.key}-${var.environment}"
    http_method = "PATCH"

    headers = {
      "Content-Type" = "application/json"
    }

    body = base64encode(jsonencode({
      serviceConfig = {
        minInstanceCount = 0
      }
    }))

    oauth_token {
      service_account_email = var.service_account_email
    }
  }
}

# Outputs moved to outputs.tf file
