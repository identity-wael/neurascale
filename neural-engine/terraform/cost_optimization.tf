# Cost Optimization Configuration

# Data source for project
data "google_project" "project" {
  project_id = var.project_id
}

# Bigtable Autoscaling for Production
resource "google_bigtable_app_profile" "autoscaling" {
  count = var.enable_bigtable_autoscaling && var.environment == "production" ? 1 : 0

  instance       = module.neural_ingestion.bigtable_instance_id
  app_profile_id = "autoscaling-profile"

  single_cluster_routing {
    cluster_id                 = "${module.neural_ingestion.bigtable_instance_id}-cluster"
    allow_transactional_writes = false
  }
}

# Scheduled Scaling for Non-Production
resource "google_cloud_scheduler_job" "scale_down_dev" {
  count = var.environment == "development" ? 1 : 0

  name             = "bigtable-scale-down-${var.environment}"
  description      = "Scale down Bigtable nodes after hours"
  schedule         = "0 19 * * 1-5" # 7 PM weekdays
  time_zone        = "America/New_York"
  attempt_deadline = "320s"

  http_target {
    http_method = "POST"
    uri         = "https://bigtableadmin.googleapis.com/v2/projects/${var.project_id}/instances/${module.neural_ingestion.bigtable_instance_id}/clusters/${module.neural_ingestion.bigtable_instance_id}-cluster"

    body = base64encode(jsonencode({
      serveNodes = var.bigtable_min_nodes_dev
    }))

    oauth_token {
      service_account_email = google_service_account.scheduler_sa[0].email
      scope                 = "https://www.googleapis.com/auth/cloud-platform"
    }
  }
}

resource "google_cloud_scheduler_job" "scale_up_dev" {
  count = var.environment == "development" ? 1 : 0

  name             = "bigtable-scale-up-${var.environment}"
  description      = "Scale up Bigtable nodes for business hours"
  schedule         = "0 8 * * 1-5" # 8 AM weekdays
  time_zone        = "America/New_York"
  attempt_deadline = "320s"

  http_target {
    http_method = "POST"
    uri         = "https://bigtableadmin.googleapis.com/v2/projects/${var.project_id}/instances/${module.neural_ingestion.bigtable_instance_id}/clusters/${module.neural_ingestion.bigtable_instance_id}-cluster"

    body = base64encode(jsonencode({
      serveNodes = var.bigtable_nodes_dev
    }))

    oauth_token {
      service_account_email = google_service_account.scheduler_sa[0].email
      scope                 = "https://www.googleapis.com/auth/cloud-platform"
    }
  }
}

# Service Account for Scheduler
resource "google_service_account" "scheduler_sa" {
  count = var.environment == "development" ? 1 : 0

  account_id   = "bigtable-scheduler-${var.environment}"
  display_name = "Bigtable Scheduler Service Account"
}

resource "google_project_iam_member" "scheduler_bigtable_admin" {
  count = var.environment == "development" ? 1 : 0

  project = var.project_id
  role    = "roles/bigtable.admin"
  member  = "serviceAccount:${google_service_account.scheduler_sa[0].email}"
}

# Cost Allocation Tags
locals {
  cost_tags = {
    environment   = var.environment
    team          = "neural-engineering"
    cost_center   = var.cost_center
    project_phase = "phase-2"
    service       = "neural-data-platform"
  }
}

# Budget Alerts
resource "google_billing_budget" "neural_platform_budget" {
  count = var.billing_account_id != "" ? 1 : 0

  billing_account = var.billing_account_id
  display_name    = "Neural Platform - ${var.environment}"

  budget_filter {
    projects = ["projects/${data.google_project.project.number}"]

    labels = {
      environment = var.environment
      service     = "neural-data-platform"
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

  all_updates_rule {
    monitoring_notification_channels = var.budget_notification_channels
    disable_default_iam_recipients   = false
  }
}

# Cost Optimization Dashboard
resource "google_monitoring_dashboard" "cost_optimization" {
  dashboard_json = jsonencode({
    displayName = "Cost Optimization - ${var.environment}"

    gridLayout = {
      widgets = [
        {
          title = "Monthly Spend by Service"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "metric.type=\"billing.googleapis.com/billing/cost\" AND resource.label.\"project_id\"=\"${var.project_id}\""
                  aggregation = {
                    alignmentPeriod    = "86400s"
                    perSeriesAligner   = "ALIGN_SUM"
                    crossSeriesReducer = "REDUCE_SUM"
                    groupByFields      = ["resource.label.\"service\""]
                  }
                }
              }
            }]
          }
        },
        {
          title = "Bigtable Node Utilization"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "metric.type=\"bigtable.googleapis.com/cluster/cpu_load\" AND resource.label.\"instance\"=\"${module.neural_ingestion.bigtable_instance_id}\""
                  aggregation = {
                    alignmentPeriod  = "60s"
                    perSeriesAligner = "ALIGN_MEAN"
                  }
                }
              }
            }]
          }
        },
        {
          title = "Cloud Functions Invocations"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "metric.type=\"cloudfunctions.googleapis.com/function/execution_count\" AND resource.label.\"function_name\"=~\"neural-.*\""
                  aggregation = {
                    alignmentPeriod    = "60s"
                    perSeriesAligner   = "ALIGN_RATE"
                    crossSeriesReducer = "REDUCE_SUM"
                    groupByFields      = ["resource.label.\"function_name\""]
                  }
                }
              }
            }]
          }
        },
        {
          title = "Storage Growth Rate"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "metric.type=\"bigtable.googleapis.com/table/storage_utilization\" AND resource.label.\"instance\"=\"${module.neural_ingestion.bigtable_instance_id}\""
                  aggregation = {
                    alignmentPeriod  = "3600s"
                    perSeriesAligner = "ALIGN_MEAN"
                  }
                }
              }
            }]
          }
        }
      ]
    }
  })
}

# Export cost optimization metrics
resource "google_bigquery_dataset" "cost_export" {
  dataset_id                  = "billing_export_${replace(var.environment, "-", "_")}"
  friendly_name               = "Billing Export - ${var.environment}"
  description                 = "BigQuery export of billing data for cost analysis"
  location                    = var.region
  default_table_expiration_ms = 7776000000 # 90 days

  labels = local.cost_tags
}

# Outputs for cost tracking
output "cost_optimization_config" {
  value = {
    budget_id           = google_billing_budget.neural_platform_budget.id
    cost_dashboard_url  = "https://console.cloud.google.com/monitoring/dashboards/custom/${google_monitoring_dashboard.cost_optimization.id}"
    scheduled_scaling   = var.environment == "development"
    autoscaling_enabled = var.enable_bigtable_autoscaling && var.environment == "production"
    cost_export_dataset = google_bigquery_dataset.cost_export.dataset_id
  }
  description = "Cost optimization configuration details"
}
