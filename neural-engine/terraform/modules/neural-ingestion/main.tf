# Neural Ingestion Infrastructure Module

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

locals {
  env_short = substr(var.environment, 0, 4) # prod, stag, deve
}

# Artifact Registry for Docker images
resource "google_artifact_registry_repository" "neural_engine" {
  location      = var.region
  repository_id = "neural-engine-${var.environment}"
  description   = "Neural Engine Docker images for ${var.environment}"
  format        = "DOCKER"
}

# Service Account for ingestion services
resource "google_service_account" "ingestion" {
  account_id   = "neural-ingestion-${local.env_short}"
  display_name = "Neural Ingestion Service Account - ${var.environment}"
  description  = "Service account for neural data ingestion in ${var.environment}"
}

# Grant permissions to the Cloud Build service account
# This is needed for deploying Cloud Functions
resource "google_project_iam_member" "cloud_build_permissions" {
  for_each = toset([
    "roles/artifactregistry.writer",
    "roles/logging.logWriter",
    "roles/cloudfunctions.developer",
    "roles/iam.serviceAccountUser",
    "roles/eventarc.developer",
    "roles/run.developer",
    "roles/storage.objectAdmin",
    "roles/cloudbuild.builds.builder",
    "roles/compute.admin",
    "roles/storage.admin"
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
}

# Grant Cloud Build service account permission to act as the ingestion service account
resource "google_service_account_iam_member" "cloud_build_act_as" {
  service_account_id = google_service_account.ingestion.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
}

# Grant permissions to the default Cloud Functions service account
# This service account is used by Cloud Functions runtime
resource "google_project_iam_member" "functions_service_account_permissions" {
  for_each = toset([
    "roles/artifactregistry.reader",
    "roles/logging.logWriter",
    "roles/pubsub.subscriber",
    "roles/eventarc.eventReceiver"
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${var.project_id}@appspot.gserviceaccount.com"
}

# Data source to get project information
data "google_project" "project" {
  project_id = var.project_id
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

# Storage bucket for Cloud Functions
resource "google_storage_bucket" "functions" {
  name          = "${var.project_id}-functions-${var.environment}"
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

# IAM permissions
resource "google_project_iam_member" "ingestion_permissions" {
  for_each = toset([
    "roles/pubsub.publisher",
    "roles/pubsub.subscriber",
    "roles/bigtable.user",
    "roles/storage.objectViewer",
    "roles/monitoring.metricWriter",
    "roles/logging.logWriter",
  ])

  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.ingestion.email}"
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

output "service_account_email" {
  value = google_service_account.ingestion.email
}
