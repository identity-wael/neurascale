# BigQuery Dataset for NeuraScale Neural Analytics
# Data warehouse for neural data analytics and ML training

resource "google_bigquery_dataset" "neural_analytics" {
  dataset_id                  = "${var.environment}_neural_analytics"
  friendly_name               = "${title(var.environment)} Neural Analytics"
  description                 = "Neural data analytics and ML training dataset for ${var.environment}"
  location                    = var.bigquery_location
  default_table_expiration_ms = var.default_table_expiration_days * 24 * 60 * 60 * 1000
  project                     = var.project_id

  # Access controls
  access {
    role          = "OWNER"
    user_by_email = var.dataset_owner_email
  }

  access {
    role          = "WRITER"
    user_by_email = var.neural_service_account_email
  }

  access {
    role           = "READER"
    group_by_email = var.analytics_reader_group
  }

  # Encryption with Cloud KMS
  default_encryption_configuration {
    kms_key_name = var.bigquery_encryption_key
  }

  # Labels
  labels = merge(
    var.labels,
    {
      environment = var.environment
      component   = "analytics"
      type        = "bigquery"
    }
  )

  # Deletion protection
  delete_contents_on_destroy = false
}

# Partitioned table for neural sessions
resource "google_bigquery_table" "neural_sessions" {
  dataset_id = google_bigquery_dataset.neural_analytics.dataset_id
  table_id   = "neural_sessions"
  project    = var.project_id

  time_partitioning {
    type                     = "DAY"
    field                    = "session_timestamp"
    expiration_ms            = var.session_retention_days * 24 * 60 * 60 * 1000
    require_partition_filter = true
  }

  clustering = ["patient_id", "device_type", "signal_type"]

  schema = jsonencode([
    {
      name        = "session_id"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Unique session identifier"
    },
    {
      name        = "session_timestamp"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
      description = "Session start timestamp"
    },
    {
      name        = "patient_id"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "De-identified patient ID"
    },
    {
      name        = "device_type"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Type of neural recording device"
    },
    {
      name        = "signal_type"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Type of neural signal (EEG, EMG, etc.)"
    },
    {
      name        = "duration_seconds"
      type        = "INTEGER"
      mode        = "REQUIRED"
      description = "Session duration in seconds"
    },
    {
      name        = "channel_count"
      type        = "INTEGER"
      mode        = "REQUIRED"
      description = "Number of recording channels"
    },
    {
      name        = "sampling_rate"
      type        = "FLOAT"
      mode        = "REQUIRED"
      description = "Sampling rate in Hz"
    },
    {
      name        = "data_quality_score"
      type        = "FLOAT"
      mode        = "NULLABLE"
      description = "Overall data quality score (0-1)"
    },
    {
      name        = "annotations"
      type        = "JSON"
      mode        = "NULLABLE"
      description = "Session annotations and metadata"
    }
  ])

  labels = merge(
    var.labels,
    {
      environment = var.environment
      table_type  = "sessions"
    }
  )
}

# Table for aggregated neural metrics
resource "google_bigquery_table" "neural_metrics" {
  dataset_id = google_bigquery_dataset.neural_analytics.dataset_id
  table_id   = "neural_metrics"
  project    = var.project_id

  time_partitioning {
    type  = "HOUR"
    field = "timestamp"
  }

  clustering = ["session_id", "metric_type"]

  schema = jsonencode([
    {
      name        = "timestamp"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
      description = "Metric timestamp"
    },
    {
      name        = "session_id"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Session identifier"
    },
    {
      name        = "metric_type"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Type of metric (power_spectrum, coherence, etc.)"
    },
    {
      name        = "channel_id"
      type        = "INTEGER"
      mode        = "NULLABLE"
      description = "Channel identifier"
    },
    {
      name        = "value"
      type        = "FLOAT"
      mode        = "REQUIRED"
      description = "Metric value"
    },
    {
      name        = "frequency_band"
      type        = "STRING"
      mode        = "NULLABLE"
      description = "Frequency band (alpha, beta, gamma, etc.)"
    },
    {
      name        = "metadata"
      type        = "JSON"
      mode        = "NULLABLE"
      description = "Additional metric metadata"
    }
  ])

  labels = merge(
    var.labels,
    {
      environment = var.environment
      table_type  = "metrics"
    }
  )
}

# ML training dataset
resource "google_bigquery_table" "ml_training_data" {
  dataset_id = google_bigquery_dataset.neural_analytics.dataset_id
  table_id   = "ml_training_data"
  project    = var.project_id

  schema = jsonencode([
    {
      name        = "sample_id"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Unique sample identifier"
    },
    {
      name        = "features"
      type        = "FLOAT"
      mode        = "REPEATED"
      description = "Feature vector"
    },
    {
      name        = "label"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Training label"
    },
    {
      name        = "split"
      type        = "STRING"
      mode        = "REQUIRED"
      description = "Data split (train/validation/test)"
    },
    {
      name        = "created_timestamp"
      type        = "TIMESTAMP"
      mode        = "REQUIRED"
      description = "When the sample was created"
    }
  ])

  labels = merge(
    var.labels,
    {
      environment = var.environment
      table_type  = "ml_training"
    }
  )
}

# Scheduled query for data aggregation
resource "google_bigquery_data_transfer_config" "daily_aggregation" {
  count = var.enable_scheduled_queries ? 1 : 0

  display_name           = "${var.environment}_daily_neural_aggregation"
  data_source_id         = "scheduled_query"
  schedule               = "every day 02:00"
  destination_dataset_id = google_bigquery_dataset.neural_analytics.dataset_id
  project                = var.project_id
  location               = var.bigquery_location

  params = {
    query = templatefile("${path.module}/queries/daily_aggregation.sql", {
      project_id  = var.project_id
      dataset_id  = google_bigquery_dataset.neural_analytics.dataset_id
      environment = var.environment
    })
    destination_table_name_template = "daily_summary_{run_date}"
    write_disposition               = "WRITE_TRUNCATE"
  }

  disabled = false
}
