terraform {
  required_version = ">= 1.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  backend "gcs" {
    bucket = "neurascale-terraform-state"
    prefix = "neural-engine/ingestion"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "pubsub.googleapis.com",
    "bigtable.googleapis.com",
    "bigtableadmin.googleapis.com",
    "cloudfunctions.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "run.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
  ])

  project = var.project_id
  service = each.value

  disable_on_destroy = false
}

# Service Account for ingestion
resource "google_service_account" "neural_ingestion" {
  account_id   = "neural-ingestion-sa"
  display_name = "Neural Data Ingestion Service Account"
  project      = var.project_id
}

# IAM roles for service account
resource "google_project_iam_member" "ingestion_roles" {
  for_each = toset([
    "roles/pubsub.publisher",
    "roles/pubsub.subscriber",
    "roles/bigtable.user",
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.neural_ingestion.email}"
}

# Pub/Sub topics for each signal type
resource "google_pubsub_topic" "neural_data" {
  for_each = toset(var.signal_types)

  name    = "neural-data-${each.value}"
  project = var.project_id

  message_retention_duration = "604800s" # 7 days

  labels = {
    environment = var.environment
    signal_type = each.value
  }

  depends_on = [google_project_service.required_apis]
}

# Pub/Sub subscriptions
resource "google_pubsub_subscription" "neural_data" {
  for_each = toset(var.signal_types)

  name    = "neural-data-${each.value}-sub"
  topic   = google_pubsub_topic.neural_data[each.value].name
  project = var.project_id

  ack_deadline_seconds       = 60
  message_retention_duration = "86400s" # 1 day

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  dead_letter_policy {
    dead_letter_topic     = google_pubsub_topic.dead_letter.id
    max_delivery_attempts = 5
  }

  labels = {
    environment = var.environment
    signal_type = each.value
  }
}

# Dead letter topic
resource "google_pubsub_topic" "dead_letter" {
  name    = "neural-data-dead-letter"
  project = var.project_id

  message_retention_duration = "2592000s" # 30 days

  labels = {
    environment = var.environment
    purpose     = "dead-letter"
  }

  depends_on = [google_project_service.required_apis]
}

# Bigtable instance
resource "google_bigtable_instance" "neural_data" {
  name    = var.bigtable_instance_id
  project = var.project_id

  display_name = "Neural Data Time Series"

  cluster {
    cluster_id   = "${var.bigtable_instance_id}-cluster"
    zone         = "${var.region}-a"
    num_nodes    = var.environment == "production" ? 3 : 1
    storage_type = "SSD"
  }

  instance_type = var.environment == "production" ? "PRODUCTION" : "DEVELOPMENT"

  labels = {
    environment = var.environment
  }

  depends_on = [google_project_service.required_apis]
}

# Bigtable table
resource "google_bigtable_table" "time_series" {
  name          = var.bigtable_table_id
  instance_name = google_bigtable_instance.neural_data.name
  project       = var.project_id

  column_family {
    family = "metadata"
  }

  column_family {
    family = "data"
  }
}

# Bigtable garbage collection policies
resource "google_bigtable_gc_policy" "metadata" {
  instance_name = google_bigtable_instance.neural_data.name
  table_name    = google_bigtable_table.time_series.name
  column_family = "metadata"

  max_version {
    number = 1
  }
}

resource "google_bigtable_gc_policy" "data" {
  instance_name = google_bigtable_instance.neural_data.name
  table_name    = google_bigtable_table.time_series.name
  column_family = "data"

  mode = "INTERSECTION"

  max_version {
    number = 1
  }

  max_age {
    duration = "2592000s" # 30 days
  }
}

# Cloud Storage bucket for function source
resource "google_storage_bucket" "function_source" {
  name     = "${var.project_id}-neural-functions"
  location = var.region
  project  = var.project_id

  force_destroy = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 7
    }
    action {
      type = "Delete"
    }
  }

  labels = {
    environment = var.environment
  }
}

# Upload function source code
resource "google_storage_bucket_object" "function_source" {
  name   = "ingestion/source-${filemd5("${path.module}/../../functions/stream_ingestion/main.py")}.zip"
  bucket = google_storage_bucket.function_source.name
  source = data.archive_file.function_source.output_path
}

data "archive_file" "function_source" {
  type        = "zip"
  output_path = "${path.module}/function-source.zip"

  source {
    content  = file("${path.module}/../../functions/stream_ingestion/main.py")
    filename = "main.py"
  }

  source {
    content  = file("${path.module}/../../functions/stream_ingestion/requirements.txt")
    filename = "requirements.txt"
  }

  # Include ingestion module
  source {
    content  = file("${path.module}/../../src/ingestion/__init__.py")
    filename = "src/ingestion/__init__.py"
  }

  source {
    content  = file("${path.module}/../../src/ingestion/data_types.py")
    filename = "src/ingestion/data_types.py"
  }

  source {
    content  = file("${path.module}/../../src/ingestion/neural_data_ingestion.py")
    filename = "src/ingestion/neural_data_ingestion.py"
  }

  source {
    content  = file("${path.module}/../../src/ingestion/validators.py")
    filename = "src/ingestion/validators.py"
  }

  source {
    content  = file("${path.module}/../../src/ingestion/anonymizer.py")
    filename = "src/ingestion/anonymizer.py"
  }
}

# Cloud Function for stream processing
resource "google_cloudfunctions2_function" "process_neural_stream" {
  name     = "process-neural-stream"
  location = var.region
  project  = var.project_id

  description = "Process neural data streams from Pub/Sub"

  build_config {
    runtime     = "python312"
    entry_point = "process_neural_stream"

    source {
      storage_source {
        bucket = google_storage_bucket.function_source.name
        object = google_storage_bucket_object.function_source.name
      }
    }
  }

  service_config {
    max_instance_count             = 100
    min_instance_count             = 1
    available_memory               = "1Gi"
    timeout_seconds                = 60
    ingress_settings               = "ALLOW_INTERNAL_ONLY"
    all_traffic_on_latest_revision = true
    service_account_email          = google_service_account.neural_ingestion.email

    environment_variables = {
      GCP_PROJECT = var.project_id
    }
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic   = google_pubsub_topic.neural_data["eeg"].id
    retry_policy   = "RETRY_POLICY_RETRY"
  }

  labels = {
    environment = var.environment
  }

  depends_on = [
    google_project_service.required_apis,
    google_storage_bucket_object.function_source,
  ]
}

# Cloud Function for batch ingestion
resource "google_cloudfunctions2_function" "ingest_batch" {
  name     = "ingest-neural-batch"
  location = var.region
  project  = var.project_id

  description = "HTTP endpoint for batch neural data ingestion"

  build_config {
    runtime     = "python312"
    entry_point = "ingest_batch"

    source {
      storage_source {
        bucket = google_storage_bucket.function_source.name
        object = google_storage_bucket_object.function_source.name
      }
    }
  }

  service_config {
    max_instance_count             = 50
    min_instance_count             = 0
    available_memory               = "2Gi"
    timeout_seconds                = 300
    ingress_settings               = "ALLOW_ALL"
    all_traffic_on_latest_revision = true
    service_account_email          = google_service_account.neural_ingestion.email

    environment_variables = {
      GCP_PROJECT = var.project_id
    }
  }

  labels = {
    environment = var.environment
  }

  depends_on = [
    google_project_service.required_apis,
    google_storage_bucket_object.function_source,
  ]
}

# Outputs
output "pubsub_topics" {
  value = {
    for k, v in google_pubsub_topic.neural_data : k => v.id
  }
  description = "Map of signal types to Pub/Sub topic IDs"
}

output "bigtable_instance" {
  value       = google_bigtable_instance.neural_data.id
  description = "Bigtable instance ID"
}

output "batch_ingestion_url" {
  value       = google_cloudfunctions2_function.ingest_batch.service_config[0].uri
  description = "URL for batch ingestion endpoint"
}

output "service_account_email" {
  value       = google_service_account.neural_ingestion.email
  description = "Service account email for ingestion"
}
