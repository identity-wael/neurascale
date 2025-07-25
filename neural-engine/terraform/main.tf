terraform {
  required_version = ">= 1.5.0"

  backend "gcs" {
    bucket = "neurascale-terraform-state"
    prefix = "neural-engine"
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
    time = {
      source  = "hashicorp/time"
      version = "~> 0.9"
    }
  }
}

# Determine environment from project_id
locals {
  environment = endswith(var.project_id, "-neurascale") ? split("-", var.project_id)[0] : "development"
  env_short = {
    "production"  = "prod"
    "staging"     = "stag"
    "development" = "dev"
  }[local.environment]
}

# Provider configuration
provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Enable required APIs first
resource "google_project_service" "apis" {
  for_each = toset([
    "compute.googleapis.com",
    "storage.googleapis.com",
    "pubsub.googleapis.com",
    "bigtable.googleapis.com",
    "bigtableadmin.googleapis.com",
    "cloudfunctions.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "run.googleapis.com",
    "eventarc.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
  ])

  project = var.project_id
  service = each.key

  disable_on_destroy = false
}

# Wait for APIs to be enabled
resource "time_sleep" "wait_for_apis" {
  depends_on = [google_project_service.apis]

  create_duration = "30s"
}

# Create the main service account for neural ingestion
resource "google_service_account" "neural_ingestion" {
  account_id   = "neural-ingestion-${local.env_short}"
  display_name = "Neural Ingestion Service Account"
  description  = "Service account for neural data ingestion functions and services"
  project      = var.project_id

  depends_on = [time_sleep.wait_for_apis]
}

# Grant necessary permissions to the service account
resource "google_project_iam_member" "neural_ingestion_roles" {
  for_each = toset([
    "roles/pubsub.publisher",
    "roles/pubsub.subscriber",
    "roles/bigtable.user",
    "roles/storage.objectViewer",
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter",
    "roles/eventarc.eventReceiver",
  ])

  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${google_service_account.neural_ingestion.email}"

  depends_on = [google_service_account.neural_ingestion]
}

# Grant GitHub Actions service account permission to deploy
resource "google_project_iam_member" "github_actions_deploy" {
  for_each = toset([
    "roles/artifactregistry.writer",
    "roles/cloudfunctions.admin",
    "roles/iam.serviceAccountUser",
    "roles/storage.admin",
    "roles/pubsub.admin",
    "roles/bigtable.admin",
    "roles/serviceusage.serviceUsageConsumer",
  ])

  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${var.github_actions_service_account}"

  depends_on = [time_sleep.wait_for_apis]
}

# Grant GitHub Actions permission to act as the ingestion service account
resource "google_service_account_iam_member" "github_actions_act_as" {
  service_account_id = google_service_account.neural_ingestion.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${var.github_actions_service_account}"

  depends_on = [google_service_account.neural_ingestion]
}

# Deploy the neural ingestion infrastructure
module "neural_ingestion" {
  source = "./modules/neural-ingestion"

  project_id            = var.project_id
  environment           = local.environment
  region                = var.region
  service_account_email = google_service_account.neural_ingestion.email

  depends_on = [
    google_project_iam_member.neural_ingestion_roles,
    google_project_iam_member.github_actions_deploy,
  ]
}

# Outputs
output "environment" {
  value = local.environment
}

output "service_account_email" {
  value = google_service_account.neural_ingestion.email
}

output "artifact_registry_url" {
  value = module.neural_ingestion.artifact_registry_url
}

output "functions_bucket" {
  value = module.neural_ingestion.functions_bucket
}

output "function_topics" {
  value = module.neural_ingestion.function_topics
}
