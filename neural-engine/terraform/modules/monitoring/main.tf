# Monitoring Module for Neural Engine

variable "project_id" {
  type        = string
  description = "GCP Project ID"
}

variable "environment" {
  type        = string
  description = "Environment name"
}

variable "enable_monitoring_alerts" {
  type        = bool
  description = "Enable monitoring alerts"
  default     = true
}

variable "notification_channels" {
  type        = list(string)
  description = "List of notification channel IDs"
  default     = []
}

variable "create_slo" {
  type        = bool
  description = "Create SLO for services (set to false on initial deployment)"
  default     = false
}

variable "create_alerts" {
  type        = bool
  description = "Create alert policies (set to false on initial deployment to allow metrics to register)"
  default     = false
}

variable "region" {
  type        = string
  description = "GCP region for resources"
  default     = "northamerica-northeast1"
}

# Custom Metrics for Neural Data Quality
resource "google_logging_metric" "neural_data_quality" {
  name   = "neural-data-quality-${var.environment}"
  filter = "resource.type=\"cloud_function\" AND jsonPayload.metric_type=\"data_quality\""

  metric_descriptor {
    # Use DELTA with DISTRIBUTION for value extraction
    metric_kind = "DELTA"
    value_type  = "DISTRIBUTION"
    unit        = "1"

    labels {
      key         = "signal_type"
      value_type  = "STRING"
      description = "Type of neural signal"
    }

    labels {
      key         = "device_id"
      value_type  = "STRING"
      description = "Device identifier"
    }
  }

  value_extractor = "EXTRACT(jsonPayload.quality_score)"

  # Required bucket options for DISTRIBUTION metrics
  bucket_options {
    exponential_buckets {
      num_finite_buckets = 64
      growth_factor      = 2
      scale              = 0.01
    }
  }

  label_extractors = {
    "signal_type" = "EXTRACT(jsonPayload.signal_type)"
    "device_id"   = "EXTRACT(jsonPayload.device_id)"
  }
}

# Processing Latency Histogram
resource "google_logging_metric" "processing_latency" {
  name   = "neural-processing-latency-${var.environment}"
  filter = "resource.type=\"cloud_function\" AND jsonPayload.metric_type=\"processing_latency\""

  metric_descriptor {
    metric_kind = "DELTA"
    value_type  = "DISTRIBUTION"
    unit        = "ms"
  }

  value_extractor = "EXTRACT(jsonPayload.latency_ms)"

  # Required bucket options for DISTRIBUTION metrics
  bucket_options {
    exponential_buckets {
      num_finite_buckets = 64
      growth_factor      = 2
      scale              = 1
    }
  }
}

# Model Inference Performance
resource "google_logging_metric" "model_inference_time" {
  name   = "model-inference-time-${var.environment}"
  filter = "resource.type=\"cloud_run_revision\" AND jsonPayload.metric_type=\"inference_time\""

  metric_descriptor {
    metric_kind = "DELTA"
    # Use DISTRIBUTION for value extraction
    value_type = "DISTRIBUTION"
    unit       = "ms"

    labels {
      key         = "model_name"
      value_type  = "STRING"
      description = "Name of the ML model"
    }
  }

  value_extractor = "EXTRACT(jsonPayload.inference_time_ms)"

  # Required bucket options for DISTRIBUTION metrics
  bucket_options {
    exponential_buckets {
      num_finite_buckets = 64
      growth_factor      = 2
      scale              = 1
    }
  }

  label_extractors = {
    "model_name" = "EXTRACT(jsonPayload.model_name)"
  }
}

# Device Connection Reliability
resource "google_logging_metric" "device_connection_status" {
  name   = "device-connection-status-${var.environment}"
  filter = "resource.type=\"cloud_function\" AND jsonPayload.metric_type=\"device_connection\""

  metric_descriptor {
    # Use DELTA with INT64 (no value extractor)
    metric_kind = "DELTA"
    value_type  = "INT64"
    unit        = "1"

    labels {
      key         = "device_type"
      value_type  = "STRING"
      description = "Type of BCI device"
    }

    labels {
      key         = "status"
      value_type  = "STRING"
      description = "Connection status"
    }
  }

  # For INT64, the log entry represents count of 1
  # No value_extractor needed

  label_extractors = {
    "device_type" = "EXTRACT(jsonPayload.device_type)"
    "status"      = "EXTRACT(jsonPayload.status)"
  }
}

# SLO Monitoring for 99.9% Uptime
resource "google_monitoring_slo" "api_availability" {
  count = var.create_slo ? 1 : 0

  service      = google_monitoring_service.neural_api.service_id
  display_name = "API Availability SLO"

  goal                = 0.999
  rolling_period_days = 30

  request_based_sli {
    good_total_ratio {
      good_service_filter  = "metric.type=\"run.googleapis.com/request_count\" AND resource.type=\"cloud_run_revision\" AND resource.label.service_name=\"neural-api-${var.environment}\" AND metric.label.response_code_class=\"2xx\""
      total_service_filter = "metric.type=\"run.googleapis.com/request_count\" AND resource.type=\"cloud_run_revision\" AND resource.label.service_name=\"neural-api-${var.environment}\""
    }
  }
}

# Service Definition
resource "google_monitoring_service" "neural_api" {
  service_id   = "neural-api-${var.environment}"
  display_name = "Neural API Service"

  basic_service {
    service_type = "CLOUD_RUN"
    service_labels = {
      location     = var.region
      service_name = "neural-api-${var.environment}"
    }
  }
}

# Alert Policy for Data Quality
resource "google_monitoring_alert_policy" "data_quality_alert" {
  count = var.create_alerts ? 1 : 0

  display_name = "Low Neural Data Quality - ${var.environment}"
  enabled      = var.enable_monitoring_alerts
  combiner     = "OR"

  # Add dependency to ensure metrics exist first
  depends_on = [google_logging_metric.neural_data_quality]

  # Add lifecycle to handle metric creation delay
  lifecycle {
    create_before_destroy = true
  }

  documentation {
    content = "Neural data quality has dropped below acceptable threshold. Check device connections and signal processing."
  }

  conditions {
    display_name = "Data quality below 0.7"

    condition_threshold {
      filter          = "metric.type=\"logging.googleapis.com/user/neural-data-quality-${var.environment}\" resource.type=\"cloud_function\""
      duration        = "300s"
      comparison      = "COMPARISON_LT"
      threshold_value = 0.7

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = var.notification_channels
}

# Alert Policy for High Latency
resource "google_monitoring_alert_policy" "high_latency_alert" {
  count = var.create_alerts ? 1 : 0

  display_name = "High Processing Latency - ${var.environment}"
  enabled      = var.enable_monitoring_alerts
  combiner     = "OR"

  documentation {
    content = "Neural data processing latency exceeds 50ms target. Scale up resources or optimize processing pipeline."
  }

  conditions {
    display_name = "P95 latency above 50ms"

    condition_threshold {
      filter          = "metric.type=\"logging.googleapis.com/user/neural-processing-latency-${var.environment}\" resource.type=\"cloud_function\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 50

      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_DELTA"
        cross_series_reducer = "REDUCE_PERCENTILE_95"
      }
    }
  }

  notification_channels = var.notification_channels
}

# Alert Policy for Device Disconnections
resource "google_monitoring_alert_policy" "device_disconnection_alert" {
  count = var.create_alerts ? 1 : 0

  display_name = "Device Disconnections - ${var.environment}"
  enabled      = var.enable_monitoring_alerts
  combiner     = "OR"

  # Add dependency to ensure metrics exist first
  depends_on = [google_logging_metric.device_connection_status]

  # Add lifecycle to handle metric creation delay
  lifecycle {
    create_before_destroy = true
  }

  documentation {
    content = "Multiple device disconnections detected. Check network connectivity and device health."
  }

  conditions {
    display_name = "More than 5 disconnections in 5 minutes"

    condition_threshold {
      filter          = "metric.type=\"logging.googleapis.com/user/device-connection-status-${var.environment}\" AND metric.label.\"status\"=\"disconnected\" AND resource.type=\"cloud_function\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 5

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = var.notification_channels
}

# PagerDuty Integration
resource "google_monitoring_notification_channel" "pagerduty" {
  count = var.environment == "production" ? 1 : 0

  display_name = "PagerDuty - ${var.environment}"
  type         = "pagerduty"

  labels = {
    "servicekey" = "YOUR_PAGERDUTY_INTEGRATION_KEY" # TODO: Use Secret Manager
  }

  enabled = true
}

# Outputs
output "notification_channel_ids" {
  value = concat(
    var.notification_channels,
    var.environment == "production" ? [google_monitoring_notification_channel.pagerduty[0].id] : []
  )
  description = "List of notification channel IDs for alerts"
}

output "slo_id" {
  value       = var.create_slo && length(google_monitoring_slo.api_availability) > 0 ? google_monitoring_slo.api_availability[0].slo_id : null
  description = "ID of the API availability SLO"
}

output "custom_metrics" {
  value = {
    data_quality       = google_logging_metric.neural_data_quality.id
    processing_latency = google_logging_metric.processing_latency.id
    inference_time     = google_logging_metric.model_inference_time.id
    device_connection  = google_logging_metric.device_connection_status.id
  }
  description = "IDs of custom metrics"
}
