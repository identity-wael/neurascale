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

# Enable required APIs using the project_apis module
module "project_apis" {
  source = "./modules/project-apis"

  project_id = var.project_id
}

# Create the main service account for neural ingestion
resource "google_service_account" "neural_ingestion" {
  account_id   = "neural-ingestion-${local.env_short}"
  display_name = "Neural Ingestion Service Account"
  description  = "Service account for neural data ingestion functions and services"
  project      = var.project_id

  depends_on = [module.project_apis]
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

# Create custom role for GitHub Actions with minimal permissions
resource "google_project_iam_custom_role" "github_deploy" {
  role_id     = "githubDeployRole"
  title       = "GitHub Actions Deploy Role"
  description = "Custom role for GitHub Actions with minimal required permissions"
  permissions = [
    "cloudfunctions.functions.create",
    "cloudfunctions.functions.update",
    "cloudfunctions.functions.delete",
    "cloudfunctions.functions.get",
    "cloudfunctions.functions.list",
    "cloudfunctions.operations.get",
    "cloudfunctions.operations.list",
    "iam.serviceAccounts.actAs",
    "storage.buckets.get",
    "storage.buckets.list",
    "storage.objects.create",
    "storage.objects.delete",
    "storage.objects.get",
    "storage.objects.list",
    "artifactregistry.repositories.get",
    "artifactregistry.repositories.list",
    "artifactregistry.repositories.uploadArtifacts",
    "artifactregistry.repositories.downloadArtifacts",
    "run.services.create",
    "run.services.update",
    "run.services.get",
    "run.services.list",
    "resourcemanager.projects.get",
    "serviceusage.services.use",
    "pubsub.topics.get",
    "pubsub.topics.list",
    "pubsub.subscriptions.get",
    "pubsub.subscriptions.list",
    "bigtable.instances.get",
    "bigtable.instances.list",
    "bigtable.tables.get",
    "bigtable.tables.list",
    "logging.logEntries.create",
    "monitoring.timeSeries.create"
  ]

  depends_on = [module.project_apis]
}

# Grant custom role to GitHub Actions service account
resource "google_project_iam_member" "github_actions_custom_role" {
  project = var.project_id
  role    = google_project_iam_custom_role.github_deploy.id
  member  = "serviceAccount:${var.github_actions_service_account}"

  depends_on = [google_project_iam_custom_role.github_deploy]
}

# Additional minimal roles for GitHub Actions (kept for compatibility during migration)
# TODO: Review and remove redundant permissions after custom role is verified
resource "google_project_iam_member" "github_actions_deploy" {
  for_each = toset([
    "roles/serviceusage.serviceUsageConsumer",
  ])

  project = var.project_id
  role    = each.key
  member  = "serviceAccount:${var.github_actions_service_account}"

  depends_on = [module.project_apis]
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

# Deploy monitoring infrastructure
module "monitoring" {
  source = "./modules/monitoring"

  project_id                = var.project_id
  environment               = var.environment
  enable_monitoring_alerts  = var.enable_monitoring_alerts
  notification_channels     = var.alert_notification_channels

  depends_on = [
    module.project_apis,
    module.neural_ingestion
  ]
}

# Include cost optimization configuration
# This is included directly rather than as a module since it needs access to other modules
# and the billing_account_id may not be available in all environments

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

output "monitoring_dashboard" {
  value = module.monitoring.custom_metrics
  description = "Custom monitoring metrics"
}

output "function_topics" {
  value = module.neural_ingestion.function_topics
}
