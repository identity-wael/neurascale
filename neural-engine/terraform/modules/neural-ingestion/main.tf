# Neural Ingestion Infrastructure Module

locals {
  env_short = substr(var.environment, 0, 4) # prod, stag, dev
}

# Artifact Registry for Docker images
resource "google_artifact_registry_repository" "neural_engine" {
  location      = var.region
  repository_id = "neural-engine-${var.environment}"
  description   = "Neural Engine Docker images for ${var.environment}"
  format        = "DOCKER"

  lifecycle {
    create_before_destroy = true
  }
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

# Bigtable instance with autoscaling
resource "google_bigtable_instance" "neural_data" {
  name         = "neural-data-${var.environment}"
  display_name = "Neural Data - ${var.environment}"

  deletion_protection = var.enable_deletion_protection && var.environment == "production"

  cluster {
    cluster_id   = "neural-data-cluster-${local.env_short}"
    storage_type = "SSD"
    zone         = "${var.region}-a"
    num_nodes    = var.bigtable_min_nodes
  }

  labels = {
    environment = var.environment
    managed_by  = "terraform"
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

# Note: Cloud Functions will be deployed separately after infrastructure
# This is a placeholder for the function configuration
# In a real deployment, we would either:
# 1. Use a separate step to deploy functions after Terraform
# 2. Use inline source code
# 3. Pre-upload the functions package

# For now, we'll create the necessary IAM bindings for functions
# Using authoritative binding to avoid conflicts
resource "google_project_iam_binding" "pubsub_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"

  members = [
    "serviceAccount:service-${data.google_project.project.number}@gcp-sa-pubsub.iam.gserviceaccount.com",
  ]

  # Add lifecycle to prevent recreation on every apply
  lifecycle {
    create_before_destroy = true
  }
}

# Data source for project info
data "google_project" "project" {
  project_id = var.project_id
}

# Service account for ingestion (legacy - for state compatibility)
resource "google_service_account" "ingestion" {
  account_id   = "neural-ingestion-${local.env_short}"
  display_name = "Neural Ingestion Service Account"
  description  = "Service account for neural data ingestion"
  project      = var.project_id

  lifecycle {
    create_before_destroy = true
  }
}

# IAM permissions for the ingestion service account (legacy - for state compatibility)
resource "google_project_iam_member" "ingestion_permissions" {
  for_each = toset([
    "roles/pubsub.publisher",
    "roles/pubsub.subscriber",
    "roles/storage.objectViewer",
    "roles/monitoring.metricWriter",
  ])

  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.ingestion.email}"
}

# Cloud Build permissions (legacy - for state compatibility)
resource "google_project_iam_member" "cloud_build_permissions" {
  for_each = toset([
    "roles/compute.admin",
    "roles/storage.admin",
    "roles/storage.objectAdmin",
    "roles/cloudfunctions.developer",
    "roles/eventarc.developer",
    "roles/iam.serviceAccountUser",
    "roles/artifactregistry.admin",
    "roles/logging.logWriter",
    "roles/run.admin",
  ])

  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${data.google_project.project.number}@cloudbuild.gserviceaccount.com"
}

# Functions service account permissions (legacy - for state compatibility)
resource "google_project_iam_member" "functions_service_account_permissions" {
  for_each = toset([
    "roles/eventarc.eventReceiver",
    "roles/logging.logWriter",
    "roles/artifactregistry.reader",
  ])

  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${var.project_id}@appspot.gserviceaccount.com"
}

# Outputs moved to outputs.tf
