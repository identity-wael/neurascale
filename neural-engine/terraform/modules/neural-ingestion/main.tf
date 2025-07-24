# Neural Ingestion Infrastructure Module

# Variables
variable "project_id" {
  type        = string
  description = "Project ID"
}

variable "environment" {
  type        = string
  description = "Environment name (production, staging, development)"
}

variable "region" {
  type        = string
  description = "Google Cloud region"
}

variable "service_account_email" {
  type        = string
  description = "Service account email for running the services"
}

locals {
  env_short = substr(var.environment, 0, 4) # prod, stag, dev
}

# Artifact Registry for Docker images
resource "google_artifact_registry_repository" "neural_engine" {
  location      = var.region
  repository_id = "neural-engine-${var.environment}"
  description   = "Neural Engine Docker images for ${var.environment}"
  format        = "DOCKER"
}

# Storage bucket for Cloud Functions source code
resource "google_storage_bucket" "functions" {
  name          = "${var.project_id}-functions-${local.env_short}"
  location      = var.region
  force_destroy = var.environment != "production"

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  labels = {
    environment = var.environment
  }
}

# Pub/Sub topics for different signal types
resource "google_pubsub_topic" "neural_data" {
  for_each = toset(["eeg", "ecog", "lfp", "spikes", "emg", "accelerometer"])

  name = "neural-data-${each.key}-${var.environment}"

  labels = {
    environment = var.environment
    signal_type = each.key
  }
}

# Dead letter topic
resource "google_pubsub_topic" "dead_letter" {
  name = "neural-data-dead-letter-${var.environment}"

  labels = {
    environment = var.environment
    purpose     = "dead-letter"
  }
}

# Pub/Sub subscriptions with dead letter policy
resource "google_pubsub_subscription" "neural_data" {
  for_each = google_pubsub_topic.neural_data

  name  = "${each.value.name}-sub"
  topic = each.value.name

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.dead_letter.id
    max_delivery_attempts = 10
  }

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  labels = {
    environment = var.environment
    signal_type = each.key
  }
}

# Bigtable instance
resource "google_bigtable_instance" "neural_data" {
  name         = "neural-data-${var.environment}"
  display_name = "Neural Data Storage - ${var.environment}"

  cluster {
    cluster_id   = "neural-data-cluster-${local.env_short}"
    num_nodes    = var.environment == "production" ? 3 : 1
    storage_type = "SSD"
    zone         = "${var.region}-a"
  }

  labels = {
    environment = var.environment
  }
}

# Bigtable tables
resource "google_bigtable_table" "time_series" {
  name          = "neural-time-series"
  instance_name = google_bigtable_instance.neural_data.name

  column_family {
    family = "data"
  }

  column_family {
    family = "metadata"
  }
}

resource "google_bigtable_table" "sessions" {
  name          = "neural-sessions"
  instance_name = google_bigtable_instance.neural_data.name

  column_family {
    family = "info"
  }
}

resource "google_bigtable_table" "devices" {
  name          = "neural-devices"
  instance_name = google_bigtable_instance.neural_data.name

  column_family {
    family = "info"
  }
}

# Cloud Functions (Gen2) for processing neural data streams
resource "google_cloudfunctions2_function" "process_neural_stream" {
  for_each = google_pubsub_topic.neural_data

  name        = "process-neural-${each.key}-${var.environment}"
  location    = var.region
  description = "Process ${each.key} neural data streams"

  build_config {
    runtime     = "python312"
    entry_point = "process_neural_stream"
    source {
      storage_source {
        bucket = google_storage_bucket.functions.name
        object = "functions-${var.environment}.zip"
      }
    }
  }

  service_config {
    max_instance_count               = var.environment == "production" ? 100 : 10
    min_instance_count               = 0
    available_memory                 = "512M"
    timeout_seconds                  = 60
    service_account_email           = var.service_account_email
    ingress_settings                = "ALLOW_INTERNAL_ONLY"
    all_traffic_on_latest_revision  = true

    environment_variables = {
      GCP_PROJECT  = var.project_id
      ENVIRONMENT  = var.environment
      SIGNAL_TYPE  = each.key
      BIGTABLE_INSTANCE = google_bigtable_instance.neural_data.name
    }
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic   = each.value.id
    retry_policy   = "RETRY_POLICY_RETRY"
  }

  depends_on = [
    google_bigtable_table.time_series,
    google_bigtable_table.sessions,
    google_bigtable_table.devices,
  ]
}

# Outputs
output "artifact_registry_url" {
  value = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.neural_engine.repository_id}"
}

output "pubsub_topics" {
  value = {
    for k, v in google_pubsub_topic.neural_data : k => v.id
  }
}

output "bigtable_instance_id" {
  value = google_bigtable_instance.neural_data.id
}

output "functions_bucket" {
  value = google_storage_bucket.functions.name
}

output "function_urls" {
  value = {
    for k, v in google_cloudfunctions2_function.process_neural_stream : k => v.service_config[0].uri
  }
}
