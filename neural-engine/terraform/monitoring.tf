# Monitoring and alerting configuration

# Create a notification channel for alerts
resource "google_monitoring_notification_channel" "email" {
  display_name = "Email Notification - ${local.environment}"
  type         = "email"

  labels = {
    email_address = "devops-alerts@neurascale.com"
  }

  enabled = var.enable_monitoring_alerts
}

# Create a comprehensive monitoring dashboard
resource "google_monitoring_dashboard" "infrastructure" {
  dashboard_json = jsonencode({
    displayName = "Neural Engine Infrastructure - ${local.environment}"
    mosaicLayout = {
      columns = 12
      tiles = [
        {
          # Bigtable CPU utilization
          width  = 6
          height = 4
          widget = {
            title = "Bigtable CPU Utilization"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "metric.type=\"bigtable.googleapis.com/cluster/cpu_load\" resource.type=\"bigtable_cluster\" resource.label.\"cluster\":\"neural-data-${local.environment}\""
                    aggregation = {
                      alignmentPeriod  = "60s"
                      perSeriesAligner = "ALIGN_MEAN"
                    }
                  }
                }
                plotType = "LINE"
              }]
              timeshiftDuration = "0s"
              yAxis = {
                label = "CPU Load"
                scale = "LINEAR"
              }
            }
          }
        },
        {
          # Pub/Sub message flow
          xPos   = 6
          width  = 6
          height = 4
          widget = {
            title = "Pub/Sub Message Flow"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "metric.type=\"pubsub.googleapis.com/topic/send_message_operation_count\" resource.type=\"pubsub_topic\" resource.label.\"topic_id\":\"${local.environment}\""
                    aggregation = {
                      alignmentPeriod    = "60s"
                      perSeriesAligner   = "ALIGN_RATE"
                      crossSeriesReducer = "REDUCE_SUM"
                      groupByFields      = ["resource.topic_id"]
                    }
                  }
                }
                plotType = "STACKED_AREA"
              }]
            }
          }
        },
        {
          # Cloud Functions execution count
          yPos   = 4
          width  = 6
          height = 4
          widget = {
            title = "Cloud Functions Executions"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "metric.type=\"cloudfunctions.googleapis.com/function/execution_count\" resource.type=\"cloud_function\" resource.label.\"function_name\"=\"process-neural-stream-${local.environment}\""
                    aggregation = {
                      alignmentPeriod  = "60s"
                      perSeriesAligner = "ALIGN_RATE"
                    }
                  }
                }
                plotType = "LINE"
              }]
            }
          }
        },
        {
          # Cloud Functions errors
          xPos   = 6
          yPos   = 4
          width  = 6
          height = 4
          widget = {
            title = "Cloud Functions Errors"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "metric.type=\"cloudfunctions.googleapis.com/function/execution_count\" resource.type=\"cloud_function\" metric.label.\"status\"!=\"ok\""
                    aggregation = {
                      alignmentPeriod    = "60s"
                      perSeriesAligner   = "ALIGN_RATE"
                      crossSeriesReducer = "REDUCE_SUM"
                      groupByFields      = ["metric.status"]
                    }
                  }
                }
                plotType = "STACKED_BAR"
              }]
            }
          }
        },
        {
          # Bigtable storage usage
          yPos   = 8
          width  = 6
          height = 4
          widget = {
            title = "Bigtable Storage Usage"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "metric.type=\"bigtable.googleapis.com/table/storage_utilized_bytes\" resource.type=\"bigtable_table\""
                    aggregation = {
                      alignmentPeriod  = "3600s"
                      perSeriesAligner = "ALIGN_MEAN"
                    }
                  }
                }
                plotType = "LINE"
              }]
              yAxis = {
                label = "Storage (bytes)"
                scale = "LINEAR"
              }
            }
          }
        },
        {
          # API latency percentiles
          xPos   = 6
          yPos   = 8
          width  = 6
          height = 4
          widget = {
            title = "API Latency Percentiles"
            xyChart = {
              dataSets = [{
                timeSeriesQuery = {
                  timeSeriesFilter = {
                    filter = "metric.type=\"loadbalancing.googleapis.com/https/backend_latencies\" resource.type=\"https_lb_rule\""
                    aggregation = {
                      alignmentPeriod    = "60s"
                      perSeriesAligner   = "ALIGN_DELTA"
                      crossSeriesReducer = "REDUCE_PERCENTILE_95"
                    }
                  }
                }
                plotType = "LINE"
              }]
            }
          }
        }
      ]
    }
  })
}

# Alert policy for high Bigtable CPU usage
resource "google_monitoring_alert_policy" "bigtable_high_cpu" {
  display_name = "Bigtable High CPU - ${local.environment}"
  enabled      = var.enable_monitoring_alerts
  combiner     = "OR"

  documentation {
    content = "Bigtable cluster CPU usage is above 80% for 5 minutes. Consider scaling up the cluster."
  }

  conditions {
    display_name = "CPU above 80%"

    condition_threshold {
      filter          = "metric.type=\"bigtable.googleapis.com/cluster/cpu_load\" resource.type=\"bigtable_cluster\" resource.label.\"cluster\":\"neural-data-${local.environment}\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.8

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]

  # notification_rate_limit is only for log-based alerts
  # Removing to fix: "only log-based alert policies may specify a notification rate limit"
}

# Alert policy for Cloud Functions errors
resource "google_monitoring_alert_policy" "function_errors" {
  display_name = "Cloud Functions Error Rate - ${local.environment}"
  enabled      = var.enable_monitoring_alerts
  combiner     = "OR"

  documentation {
    content = "Cloud Functions error rate is above 5% for 5 minutes. Check function logs for details."
  }

  conditions {
    display_name = "Error rate above 5%"

    condition_threshold {
      filter          = "metric.type=\"cloudfunctions.googleapis.com/function/execution_count\" resource.type=\"cloud_function\" resource.label.\"function_name\"=\"process-neural-stream-${local.environment}\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.05

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_MEAN"
        group_by_fields      = ["resource.function_name"]
      }

      denominator_filter = "metric.type=\"cloudfunctions.googleapis.com/function/execution_count\" resource.type=\"cloud_function\""

      denominator_aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_MEAN"
        group_by_fields      = ["resource.function_name"]
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]
}

# Alert policy for Pub/Sub message backlog
resource "google_monitoring_alert_policy" "pubsub_backlog" {
  display_name = "Pub/Sub Message Backlog - ${local.environment}"
  enabled      = var.enable_monitoring_alerts
  combiner     = "OR"

  documentation {
    content = "Pub/Sub subscription has over 1000 undelivered messages. Processing may be falling behind."
  }

  conditions {
    display_name = "Backlog over 1000 messages"

    condition_threshold {
      filter          = "metric.type=\"pubsub.googleapis.com/subscription/num_undelivered_messages\" resource.type=\"pubsub_subscription\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 1000

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.id]
}

# Uptime check for API endpoint (if applicable)
resource "google_monitoring_uptime_check_config" "api_health" {
  count = var.api_endpoint_url != "" ? 1 : 0

  display_name = "API Health Check - ${local.environment}"
  timeout      = "10s"
  period       = "60s"

  http_check {
    path         = "/health"
    port         = "443"
    use_ssl      = true
    validate_ssl = true
  }

  monitored_resource {
    type = "uptime_url"
    labels = {
      project_id = var.project_id
      host       = var.api_endpoint_url
    }
  }

  selected_regions = ["USA"]
}

# Log-based metric for deployment events
resource "google_logging_metric" "deployment_events" {
  name   = "deployment-events-${local.environment}"
  filter = "resource.type=\"global\" AND jsonPayload.environment=\"${local.environment}\" AND jsonPayload.action=\"deployment\""

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "INT64"
    unit        = "1"

    labels {
      key         = "version"
      value_type  = "STRING"
      description = "Deployment version (git SHA)"
    }

    labels {
      key         = "status"
      value_type  = "STRING"
      description = "Deployment status (success/failure)"
    }
  }

  label_extractors = {
    "version" = "EXTRACT(jsonPayload.version)"
    "status"  = "EXTRACT(jsonPayload.status)"
  }
}
