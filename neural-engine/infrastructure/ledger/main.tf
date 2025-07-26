terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "northamerica-northeast1"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "prod"
}

locals {
  labels = {
    environment = var.environment
    component   = "neural-ledger"
    compliance  = "hipaa"
  }
}

# Service Account for Ledger Processor
resource "google_service_account" "ledger_processor" {
  account_id   = "ledger-processor"
  display_name = "Neural Ledger Processor"
  description  = "Service account for Neural Ledger event processing"
  project      = var.project_id
}

# IAM Roles for Service Account
resource "google_project_iam_member" "ledger_processor_roles" {
  for_each = toset([
    "roles/pubsub.subscriber",
    "roles/bigtable.user",
    "roles/datastore.user",
    "roles/bigquery.dataEditor",
    "roles/cloudkms.cryptoKeyEncrypterDecrypter",
    "roles/monitoring.metricWriter",
    "roles/errorreporting.writer",
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.ledger_processor.email}"
}

# Pub/Sub Topic
resource "google_pubsub_topic" "neural_ledger_events" {
  name    = "neural-ledger-events"
  project = var.project_id

  message_retention_duration = "604800s" # 7 days

  labels = local.labels
}

# Pub/Sub Subscription
resource "google_pubsub_subscription" "neural_ledger_processor" {
  name    = "neural-ledger-processor"
  topic   = google_pubsub_topic.neural_ledger_events.name
  project = var.project_id

  ack_deadline_seconds = 60

  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"
  }

  enable_message_ordering = false

  expiration_policy {
    ttl = "" # Never expire
  }

  labels = local.labels
}

# Dead Letter Topic for failed messages
resource "google_pubsub_topic" "neural_ledger_dlq" {
  name    = "neural-ledger-events-dlq"
  project = var.project_id

  labels = local.labels
}

resource "google_pubsub_subscription" "neural_ledger_dlq" {
  name    = "neural-ledger-dlq-subscription"
  topic   = google_pubsub_topic.neural_ledger_dlq.name
  project = var.project_id

  ack_deadline_seconds = 300

  labels = local.labels
}

# Bigtable Instance
resource "google_bigtable_instance" "neural_ledger" {
  name    = "neural-ledger"
  project = var.project_id

  cluster {
    cluster_id   = "neural-ledger-${var.region}"
    zone         = "${var.region}-a"
    num_nodes    = var.environment == "prod" ? 3 : 1
    storage_type = "SSD"
  }

  labels = local.labels

  deletion_protection = var.environment == "prod" ? true : false
}

# Bigtable Table
resource "google_bigtable_table" "events" {
  name          = "events"
  instance_name = google_bigtable_instance.neural_ledger.name
  project       = var.project_id

  column_family {
    family = "event"
  }

  column_family {
    family = "metadata"
  }

  column_family {
    family = "chain"
  }
}

# BigQuery Dataset
resource "google_bigquery_dataset" "neural_ledger" {
  dataset_id    = "neural_ledger"
  project       = var.project_id
  location      = var.region
  friendly_name = "Neural Ledger Audit Trail"
  description   = "HIPAA-compliant audit trail for neural data operations"

  default_table_expiration_ms = 220752000000 # 7 years

  labels = local.labels
}

# BigQuery Table
resource "google_bigquery_table" "events" {
  dataset_id = google_bigquery_dataset.neural_ledger.dataset_id
  table_id   = "events"
  project    = var.project_id

  time_partitioning {
    type  = "DAY"
    field = "timestamp"

    expiration_ms = 220752000000 # 7 years
  }

  clustering = ["event_type", "session_id"]

  schema = jsonencode([
    {
      name = "event_id"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "timestamp"
      type = "TIMESTAMP"
      mode = "REQUIRED"
    },
    {
      name = "event_type"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "session_id"
      type = "STRING"
      mode = "NULLABLE"
    },
    {
      name = "device_id"
      type = "STRING"
      mode = "NULLABLE"
    },
    {
      name = "user_id"
      type = "STRING"
      mode = "NULLABLE"
    },
    {
      name = "data_hash"
      type = "STRING"
      mode = "NULLABLE"
    },
    {
      name = "metadata"
      type = "JSON"
      mode = "NULLABLE"
    },
    {
      name = "previous_hash"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "event_hash"
      type = "STRING"
      mode = "REQUIRED"
    },
    {
      name = "signature"
      type = "STRING"
      mode = "NULLABLE"
    },
    {
      name = "signing_key_id"
      type = "STRING"
      mode = "NULLABLE"
    }
  ])

  labels = local.labels
}

# KMS Keyring
resource "google_kms_key_ring" "neural_ledger" {
  name     = "neural-ledger"
  location = var.region
  project  = var.project_id
}

# KMS Crypto Key for Signing
resource "google_kms_crypto_key" "signing_key" {
  name     = "signing-key"
  key_ring = google_kms_key_ring.neural_ledger.id
  purpose  = "ASYMMETRIC_SIGN"

  version_template {
    algorithm        = "RSA_SIGN_PSS_2048_SHA256"
    protection_level = "HSM"
  }

  rotation_period = "7776000s" # 90 days

  labels = local.labels
}

# Firestore indexes
resource "google_firestore_index" "events_by_session" {
  project    = var.project_id
  collection = "ledger_events"

  fields {
    field_path = "session_id"
    order      = "ASCENDING"
  }

  fields {
    field_path = "timestamp"
    order      = "DESCENDING"
  }
}

resource "google_firestore_index" "events_by_user" {
  project    = var.project_id
  collection = "ledger_events"

  fields {
    field_path = "user_id"
    order      = "ASCENDING"
  }

  fields {
    field_path = "timestamp"
    order      = "DESCENDING"
  }
}

# Cloud Monitoring Alert Policies
resource "google_monitoring_alert_policy" "chain_integrity_violation" {
  display_name = "Neural Ledger Chain Integrity Violation"
  project      = var.project_id
  combiner     = "OR"

  conditions {
    display_name = "Hash chain violation detected"

    condition_threshold {
      filter          = "metric.type=\"custom.googleapis.com/neural_ledger/chain_violations\" AND resource.type=\"cloud_function\""
      duration        = "0s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0
    }
  }

  notification_channels = [] # Add notification channels

  alert_strategy {
    auto_close = "86400s" # 24 hours
  }
}

resource "google_monitoring_alert_policy" "high_latency" {
  display_name = "Neural Ledger High Processing Latency"
  project      = var.project_id
  combiner     = "OR"

  conditions {
    display_name = "Processing latency > 100ms"

    condition_threshold {
      filter          = "metric.type=\"custom.googleapis.com/neural_ledger/ledger_processing_latency\" AND resource.type=\"cloud_function\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 100

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_PERCENTILE_99"
      }
    }
  }

  notification_channels = [] # Add notification channels
}

# Outputs
output "service_account_email" {
  value = google_service_account.ledger_processor.email
}

output "pubsub_topic" {
  value = google_pubsub_topic.neural_ledger_events.id
}

output "bigtable_instance" {
  value = google_bigtable_instance.neural_ledger.id
}

output "bigquery_dataset" {
  value = google_bigquery_dataset.neural_ledger.id
}

output "kms_signing_key" {
  value = google_kms_crypto_key.signing_key.id
}
