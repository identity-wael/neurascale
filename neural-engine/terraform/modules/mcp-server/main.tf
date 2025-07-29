# MCP Server Infrastructure Module
# Provisions Secret Manager resources and IAM permissions for NeuraScale MCP Server

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.4"
    }
  }
}

# Generate secure random values for MCP secrets
resource "random_password" "mcp_api_key_salt" {
  length  = 32
  special = false
}

resource "random_password" "mcp_jwt_secret" {
  length  = 64
  special = true
}

# MCP API Key Salt Secret
resource "google_secret_manager_secret" "mcp_api_key_salt" {
  project   = var.project_id
  secret_id = "mcp-api-key-salt"

  labels = {
    environment = var.environment
    component   = "mcp-server"
    managed_by  = "terraform"
  }

  replication {
    auto {}
  }

  depends_on = [var.apis_enabled]
}

resource "google_secret_manager_secret_version" "mcp_api_key_salt" {
  secret      = google_secret_manager_secret.mcp_api_key_salt.name
  secret_data = random_password.mcp_api_key_salt.result
}

# MCP JWT Secret
resource "google_secret_manager_secret" "mcp_jwt_secret" {
  project   = var.project_id
  secret_id = "mcp-jwt-secret"

  labels = {
    environment = var.environment
    component   = "mcp-server"
    managed_by  = "terraform"
  }

  replication {
    auto {}
  }

  depends_on = [var.apis_enabled]
}

resource "google_secret_manager_secret_version" "mcp_jwt_secret" {
  secret      = google_secret_manager_secret.mcp_jwt_secret.name
  secret_data = random_password.mcp_jwt_secret.result
}

# Service Account for MCP Server
resource "google_service_account" "mcp_server" {
  project      = var.project_id
  account_id   = "${var.environment}-mcp-server"
  display_name = "${title(var.environment)} MCP Server Service Account"
  description  = "Service account for NeuraScale MCP Server in ${var.environment} environment"
}

# IAM binding for Secret Manager access
resource "google_secret_manager_secret_iam_member" "mcp_api_key_salt_access" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.mcp_api_key_salt.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.mcp_server.email}"
}

resource "google_secret_manager_secret_iam_member" "mcp_jwt_secret_access" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.mcp_jwt_secret.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.mcp_server.email}"
}

# Grant compute service account access to secrets (for Cloud Run, GCE, etc.)
resource "google_secret_manager_secret_iam_member" "compute_api_key_salt_access" {
  count     = var.enable_compute_access ? 1 : 0
  project   = var.project_id
  secret_id = google_secret_manager_secret.mcp_api_key_salt.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.project_id}-compute@developer.gserviceaccount.com"
}

resource "google_secret_manager_secret_iam_member" "compute_jwt_secret_access" {
  count     = var.enable_compute_access ? 1 : 0
  project   = var.project_id
  secret_id = google_secret_manager_secret.mcp_jwt_secret.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.project_id}-compute@developer.gserviceaccount.com"
}

# Grant App Engine service account access to secrets (if App Engine is used)
resource "google_secret_manager_secret_iam_member" "appengine_api_key_salt_access" {
  count     = var.enable_appengine_access ? 1 : 0
  project   = var.project_id
  secret_id = google_secret_manager_secret.mcp_api_key_salt.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.project_id}@appspot.gserviceaccount.com"
}

resource "google_secret_manager_secret_iam_member" "appengine_jwt_secret_access" {
  count     = var.enable_appengine_access ? 1 : 0
  project   = var.project_id
  secret_id = google_secret_manager_secret.mcp_jwt_secret.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${var.project_id}@appspot.gserviceaccount.com"
}

# Cloud Run service for MCP Server (optional)
resource "google_cloud_run_v2_service" "mcp_server" {
  count    = var.enable_cloud_run ? 1 : 0
  project  = var.project_id
  location = var.region
  name     = "${var.environment}-mcp-server"

  template {
    service_account = google_service_account.mcp_server.email

    containers {
      image = var.mcp_server_image

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }

      env {
        name  = "PORT"
        value = "8080"
      }

      resources {
        limits = {
          cpu    = "1000m"
          memory = "1Gi"
        }
        cpu_idle = true
      }

      ports {
        container_port = 8080
      }
    }

    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    annotations = {
      "autoscaling.knative.dev/minScale"  = tostring(var.min_instances)
      "autoscaling.knative.dev/maxScale"  = tostring(var.max_instances)
      "run.googleapis.com/cpu-throttling" = "false"
    }
  }

  traffic {
    percent = 100
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
  }

  depends_on = [
    google_secret_manager_secret_version.mcp_api_key_salt,
    google_secret_manager_secret_version.mcp_jwt_secret
  ]
}

# IAM policy for Cloud Run service (if enabled)
resource "google_cloud_run_service_iam_member" "mcp_server_invoker" {
  count    = var.enable_cloud_run && var.enable_public_access ? 1 : 0
  project  = var.project_id
  location = google_cloud_run_v2_service.mcp_server[0].location
  service  = google_cloud_run_v2_service.mcp_server[0].name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Load Balancer (optional, for production environments)
resource "google_compute_global_address" "mcp_server_ip" {
  count   = var.enable_load_balancer ? 1 : 0
  project = var.project_id
  name    = "${var.environment}-mcp-server-ip"
}

# Monitoring and alerting resources
resource "google_monitoring_alert_policy" "mcp_server_health" {
  count        = var.enable_monitoring ? 1 : 0
  project      = var.project_id
  display_name = "${title(var.environment)} MCP Server Health Alert"
  combiner     = "OR"

  conditions {
    display_name = "MCP Server Down"

    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"${var.environment}-mcp-server\""
      duration        = "300s"
      comparison      = "COMPARISON_LESS_THAN"
      threshold_value = 1

      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = var.notification_channels

  alert_strategy {
    auto_close = "1800s"
  }
}

# Log-based metrics for MCP Server
resource "google_logging_metric" "mcp_server_errors" {
  count   = var.enable_monitoring ? 1 : 0
  project = var.project_id
  name    = "${var.environment}_mcp_server_errors"
  filter  = "resource.type=\"cloud_run_revision\" AND resource.labels.service_name=\"${var.environment}-mcp-server\" AND severity>=ERROR"

  metric_descriptor {
    metric_kind  = "DELTA"
    value_type   = "INT64"
    display_name = "${title(var.environment)} MCP Server Errors"
  }
}
