# Cost Optimization Configuration for NeuraScale Neural Engine
# This file contains budget alerts and cost management resources

# Data source for project information
data "google_project" "project" {
  project_id = var.project_id
}

# Budget for the project
resource "google_billing_budget" "neural_engine" {
  count = var.billing_account_id != "" ? 1 : 0

  billing_account = var.billing_account_id
  display_name    = "${var.environment}-neural-engine-budget"

  budget_filter {
    projects = ["projects/${data.google_project.project.number}"]

    # Filter by specific services if needed
    services = var.budget_services

    # Filter by labels
    labels = {
      environment = var.environment
      cost_center = var.cost_center
    }
  }

  amount {
    specified_amount {
      currency_code = "USD"
      units         = var.budget_amount
    }
  }

  threshold_rules {
    threshold_percent = 0.5
    spend_basis       = "CURRENT_SPEND"
  }

  threshold_rules {
    threshold_percent = 0.75
    spend_basis       = "CURRENT_SPEND"
  }

  threshold_rules {
    threshold_percent = 0.9
    spend_basis       = "CURRENT_SPEND"
  }

  threshold_rules {
    threshold_percent = 1.0
    spend_basis       = "CURRENT_SPEND"
  }

  threshold_rules {
    threshold_percent = 1.2
    spend_basis       = "FORECASTED_SPEND"
  }

  # Email notifications
  dynamic "notifications_rule" {
    for_each = length(var.budget_notification_emails) > 0 ? [1] : []
    content {
      monitoring_notification_channels = []
      schema_version                   = "1.0"

      # Send to specified email addresses
      disable_default_iam_recipients = false
    }
  }

  # Pub/Sub notifications for automated responses
  dynamic "notifications_rule" {
    for_each = var.budget_pubsub_topic != "" ? [1] : []
    content {
      pubsub_topic                   = var.budget_pubsub_topic
      schema_version                 = "1.0"
      disable_default_iam_recipients = true
    }
  }
}

# Scheduled scaling for development/staging environments
resource "google_cloud_scheduler_job" "scale_down" {
  count = var.enable_scheduled_scaling && var.environment != "production" ? 1 : 0

  name        = "${var.environment}-scale-down"
  description = "Scale down resources after hours"
  schedule    = "0 20 * * 1-5" # 8 PM weekdays
  time_zone   = "America/Toronto"
  project     = var.project_id
  region      = var.region

  pubsub_target {
    topic_name = google_pubsub_topic.scaling_events[0].id
    data = base64encode(jsonencode({
      action      = "scale_down"
      environment = var.environment
    }))
  }
}

resource "google_cloud_scheduler_job" "scale_up" {
  count = var.enable_scheduled_scaling && var.environment != "production" ? 1 : 0

  name        = "${var.environment}-scale-up"
  description = "Scale up resources before hours"
  schedule    = "0 7 * * 1-5" # 7 AM weekdays
  time_zone   = "America/Toronto"
  project     = var.project_id
  region      = var.region

  pubsub_target {
    topic_name = google_pubsub_topic.scaling_events[0].id
    data = base64encode(jsonencode({
      action      = "scale_up"
      environment = var.environment
    }))
  }
}

# Pub/Sub topic for scaling events
resource "google_pubsub_topic" "scaling_events" {
  count = var.enable_scheduled_scaling ? 1 : 0

  name    = "${var.environment}-scaling-events"
  project = var.project_id

  labels = {
    environment = var.environment
    purpose     = "cost-optimization"
  }
}

# Cloud Function for automated scaling (simplified example)
resource "google_cloudfunctions2_function" "auto_scaler" {
  count = var.enable_scheduled_scaling ? 1 : 0

  name        = "${var.environment}-auto-scaler"
  location    = var.region
  description = "Automated resource scaling for cost optimization"
  project     = var.project_id

  build_config {
    runtime     = "python310"
    entry_point = "scale_resources"

    source {
      storage_source {
        bucket = module.neural_ingestion.functions_bucket
        object = google_storage_bucket_object.scaler_source[0].name
      }
    }
  }

  service_config {
    max_instance_count    = 1
    available_memory      = "256Mi"
    timeout_seconds       = 300
    service_account_email = google_service_account.neural_ingestion.email

    environment_variables = {
      ENVIRONMENT       = var.environment
      PROJECT_ID        = var.project_id
      BIGTABLE_INSTANCE = module.neural_ingestion.bigtable_instance_id
    }
  }

  event_trigger {
    event_type   = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic = google_pubsub_topic.scaling_events[0].id
  }
}

# Placeholder for scaler source code
resource "google_storage_bucket_object" "scaler_source" {
  count = var.enable_scheduled_scaling ? 1 : 0

  name   = "cloud-functions/auto-scaler-${data.archive_file.scaler_source[0].output_md5}.zip"
  bucket = module.neural_ingestion.functions_bucket
  source = data.archive_file.scaler_source[0].output_path
}

data "archive_file" "scaler_source" {
  count = var.enable_scheduled_scaling ? 1 : 0

  type        = "zip"
  output_path = "${path.module}/tmp/auto-scaler.zip"

  source {
    content  = file("${path.module}/functions/auto_scaler.py")
    filename = "main.py"
  }

  source {
    content  = file("${path.module}/functions/requirements.txt")
    filename = "requirements.txt"
  }
}

# Recommender insights subscription
resource "google_pubsub_topic" "cost_insights" {
  name    = "${var.environment}-cost-insights"
  project = var.project_id

  labels = {
    environment = var.environment
    purpose     = "cost-optimization"
  }
}

# BigQuery dataset for cost analysis
resource "google_bigquery_dataset" "cost_analysis" {
  dataset_id                  = "${replace(var.environment, "-", "_")}_cost_analysis"
  friendly_name               = "${var.environment} Cost Analysis"
  description                 = "Dataset for analyzing costs and optimization opportunities"
  location                    = var.bigquery_location
  default_table_expiration_ms = 7776000000 # 90 days
  project                     = var.project_id

  labels = {
    environment = var.environment
    purpose     = "cost-analysis"
  }
}

# BigQuery scheduled query for cost aggregation
resource "google_bigquery_data_transfer_config" "cost_aggregation" {
  count = var.enable_cost_analysis ? 1 : 0

  display_name           = "${var.environment}-cost-aggregation"
  location               = var.bigquery_location
  data_source_id         = "scheduled_query"
  schedule               = "every day 06:00"
  destination_dataset_id = google_bigquery_dataset.cost_analysis.dataset_id
  project                = var.project_id

  params = {
    destination_table_name_template = "daily_costs_{run_date}"
    write_disposition               = "WRITE_TRUNCATE"
    query                           = <<EOF
SELECT
  service.description as service,
  sku.description as sku,
  project.id as project_id,
  location.location as location,
  SUM(cost) as total_cost,
  SUM(credits.amount) as total_credits,
  SUM(cost + credits.amount) as net_cost,
  currency,
  EXTRACT(DATE FROM usage_start_time) as usage_date
FROM
  `${var.project_id}.${var.billing_export_dataset}.gcp_billing_export_v1_${var.billing_account_id}`
WHERE
  project.id = '${var.project_id}'
  AND EXTRACT(DATE FROM usage_start_time) = CURRENT_DATE() - 1
GROUP BY
  service, sku, project_id, location, currency, usage_date
ORDER BY
  net_cost DESC
EOF
  }
}

# Alert policy for sudden cost spikes
resource "google_monitoring_alert_policy" "cost_spike" {
  display_name = "${var.environment} Cost Spike Alert"
  project      = var.project_id
  combiner     = "OR"

  conditions {
    display_name = "Daily cost increase over 50%"

    condition_threshold {
      filter          = "resource.type=\"global\" AND metric.type=\"billing.googleapis.com/project/cost\""
      duration        = "3600s"
      comparison      = "COMPARISON_GT"
      threshold_value = 1.5

      aggregations {
        alignment_period     = "86400s"
        per_series_aligner   = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_SUM"
      }
    }
  }

  notification_channels = var.alert_notification_channels

  documentation {
    content = <<EOF
Daily costs have increased by more than 50% compared to the previous day.
Check for:
- Unexpected resource provisioning
- Increased traffic or usage
- Configuration changes
EOF
  }
}

# Committed Use Discount recommendations
resource "google_monitoring_dashboard" "cost_optimization" {
  dashboard_json = jsonencode({
    displayName      = "${var.environment} Cost Optimization Dashboard"
    dashboardFilters = []
    gridLayout = {
      widgets = [
        {
          title = "Daily Costs by Service"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"global\" AND metric.type=\"billing.googleapis.com/project/cost\""
                }
              }
            }]
          }
        },
        {
          title = "Resource Utilization"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"gce_instance\" AND metric.type=\"compute.googleapis.com/instance/cpu/utilization\""
                }
              }
            }]
          }
        }
      ]
    }
  })
  project = var.project_id
}
