terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Random password for database
resource "random_password" "db_password" {
  length  = 16
  special = true
}

# Cloud SQL instance
resource "google_sql_database_instance" "neurascale_console_db" {
  name             = "neurascale-console-db"
  database_version = "POSTGRES_15"
  region           = var.region
  deletion_protection = false

  settings {
    tier = var.db_tier

    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
      backup_retention_settings {
        retained_backups = 7
      }
    }

    ip_configuration {
      ipv4_enabled    = true
      require_ssl     = true
      authorized_networks {
        name  = "all"
        value = "0.0.0.0/0"
      }
    }

    database_flags {
      name  = "log_checkpoints"
      value = "on"
    }

    database_flags {
      name  = "log_connections"
      value = "on"
    }

    database_flags {
      name  = "log_disconnections"
      value = "on"
    }

    database_flags {
      name  = "log_lock_waits"
      value = "on"
    }

    insights_config {
      query_insights_enabled  = true
      record_application_tags = true
      record_client_address   = true
    }
  }
}

# Database
resource "google_sql_database" "neurascale_console" {
  name     = "neurascale_console"
  instance = google_sql_database_instance.neurascale_console_db.name
}

# Database user
resource "google_sql_user" "neurascale_console_user" {
  name     = var.db_username
  instance = google_sql_database_instance.neurascale_console_db.name
  password = random_password.db_password.result
}

# Service account for the application
resource "google_service_account" "neurascale_console_sa" {
  account_id   = "neurascale-console-sa"
  display_name = "NeuraScale Console Service Account"
  description  = "Service account for NeuraScale Console application"
}

# IAM bindings for service account
resource "google_project_iam_member" "cloudsql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.neurascale_console_sa.email}"
}

resource "google_project_iam_member" "cloudsql_instance_user" {
  project = var.project_id
  role    = "roles/cloudsql.instanceUser"
  member  = "serviceAccount:${google_service_account.neurascale_console_sa.email}"
}

# Service account key
resource "google_service_account_key" "neurascale_console_key" {
  service_account_id = google_service_account.neurascale_console_sa.name
  public_key_type    = "TYPE_X509_PEM_FILE"
}

# Secret Manager for storing sensitive data
resource "google_secret_manager_secret" "db_password" {
  secret_id = "neurascale-console-db-password"

  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_password.result
}

resource "google_secret_manager_secret" "service_account_key" {
  secret_id = "neurascale-console-service-account-key"

  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "service_account_key" {
  secret      = google_secret_manager_secret.service_account_key.id
  secret_data = base64decode(google_service_account_key.neurascale_console_key.private_key)
}
