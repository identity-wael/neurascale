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
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
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

# Service account for GKE nodes (if GKE is enabled)
resource "google_service_account" "gke_nodes" {
  count        = var.enable_gke_cluster ? 1 : 0
  account_id   = "gke-nodes-${local.env_short}"
  display_name = "GKE Nodes Service Account"
  description  = "Service account for GKE cluster nodes"
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

  # Handle case where role might already exist
  lifecycle {
    create_before_destroy = true
  }

  permissions = [
    # Cloud Functions permissions
    "cloudfunctions.functions.create",
    "cloudfunctions.functions.update",
    "cloudfunctions.functions.delete",
    "cloudfunctions.functions.get",
    "cloudfunctions.functions.list",
    "cloudfunctions.operations.get",
    "cloudfunctions.operations.list",

    # IAM permissions
    "iam.serviceAccounts.actAs",
    "iam.serviceAccounts.create",
    "iam.serviceAccounts.delete",
    "iam.serviceAccounts.get",
    "iam.serviceAccounts.list",
    "iam.serviceAccounts.getIamPolicy",
    "iam.serviceAccounts.setIamPolicy",
    "iam.roles.create",
    "iam.roles.delete",
    "iam.roles.get",
    "iam.roles.list",
    "iam.roles.update",
    "resourcemanager.projects.getIamPolicy",
    "resourcemanager.projects.setIamPolicy",

    # Storage permissions
    "storage.buckets.get",
    "storage.buckets.list",
    "storage.objects.create",
    "storage.objects.delete",
    "storage.objects.get",
    "storage.objects.list",

    # Artifact Registry permissions
    "artifactregistry.repositories.get",
    "artifactregistry.repositories.list",
    "artifactregistry.repositories.uploadArtifacts",
    "artifactregistry.repositories.downloadArtifacts",

    # Cloud Run permissions
    "run.services.create",
    "run.services.update",
    "run.services.get",
    "run.services.list",

    # Project permissions
    "resourcemanager.projects.get",
    "serviceusage.services.use",

    # Pub/Sub permissions
    "pubsub.topics.get",
    "pubsub.topics.list",
    "pubsub.subscriptions.get",
    "pubsub.subscriptions.list",

    # Bigtable permissions
    "bigtable.instances.get",
    "bigtable.instances.list",
    "bigtable.tables.get",
    "bigtable.tables.list",

    # Logging and Monitoring permissions
    "logging.logEntries.create",
    "logging.logMetrics.create",
    "logging.logMetrics.get",
    "logging.logMetrics.list",
    "monitoring.timeSeries.create",
    "monitoring.dashboards.create",
    "monitoring.dashboards.get",
    "monitoring.dashboards.list",
    "monitoring.notificationChannels.create",
    "monitoring.notificationChannels.get",
    "monitoring.notificationChannels.list",

    # BigQuery permissions
    "bigquery.datasets.create",
    "bigquery.datasets.get",
    "bigquery.datasets.getIamPolicy",
    "bigquery.datasets.setIamPolicy"
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

# Note: GitHub Actions service account has been granted Editor role in the target projects
# via the cross-project IAM setup. The custom role above provides a template for future
# migration to least-privilege permissions.

# Grant additional required roles to GitHub Actions service account
resource "google_project_iam_member" "github_actions_service_networking" {
  project = var.project_id
  role    = "roles/servicenetworking.networksAdmin"
  member  = "serviceAccount:${var.github_actions_service_account}"

  depends_on = [module.project_apis]
}

resource "google_project_iam_member" "github_actions_kms" {
  project = var.project_id
  role    = "roles/cloudkms.admin"
  member  = "serviceAccount:${var.github_actions_service_account}"

  depends_on = [module.project_apis]
}

resource "google_project_iam_member" "github_actions_sql_admin" {
  project = var.project_id
  role    = "roles/cloudsql.admin"
  member  = "serviceAccount:${var.github_actions_service_account}"

  depends_on = [module.project_apis]
}

resource "google_project_iam_member" "github_actions_cloudbuild_builds_builder" {
  project = var.project_id
  role    = "roles/cloudbuild.builds.builder"
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

  project_id             = var.project_id
  environment            = local.environment
  region                 = var.region
  service_account_email  = google_service_account.neural_ingestion.email
  enable_cloud_functions = var.enable_cloud_functions

  depends_on = [
    google_project_iam_member.neural_ingestion_roles,
    google_project_iam_member.github_actions_custom_role,
  ]
}

# Deploy MCP server infrastructure
module "mcp_server" {
  source = "./modules/mcp-server"

  project_id                     = var.project_id
  environment                    = local.environment
  region                         = var.region
  apis_enabled                   = module.project_apis.apis_enabled
  enable_cloud_run               = var.enable_mcp_cloud_run
  enable_monitoring              = var.enable_monitoring_alerts
  notification_channels          = var.alert_notification_channels
  mcp_server_image               = var.mcp_server_image
  min_instances                  = var.mcp_min_instances
  max_instances                  = var.mcp_max_instances
  enable_public_access           = var.enable_mcp_public_access
  github_actions_service_account = var.github_actions_service_account

  depends_on = [
    module.project_apis,
    google_service_account.neural_ingestion
  ]
}

# Deploy networking infrastructure
module "networking" {
  source = "./modules/networking"

  project_id          = var.project_id
  environment         = local.environment
  region              = var.region
  gke_subnet_cidr     = var.gke_subnet_cidr
  private_subnet_cidr = var.private_subnet_cidr
  pods_cidr           = var.pods_cidr
  services_cidr       = var.services_cidr
  apis_enabled        = module.project_apis.apis_enabled

  depends_on = [
    module.project_apis
  ]
}

# Deploy GKE cluster (if enabled)
module "gke" {
  count  = var.enable_gke_cluster ? 1 : 0
  source = "./modules/gke"

  project_id                    = var.project_id
  environment                   = local.environment
  region                        = var.region
  vpc_id                        = module.networking.vpc_id
  subnet_id                     = module.networking.gke_subnet_id
  pods_secondary_range_name     = module.networking.pods_secondary_range_name
  services_secondary_range_name = module.networking.services_secondary_range_name
  node_service_account_email    = google_service_account.gke_nodes[0].email

  # Node pool configurations from variables
  general_pool_machine_type = var.gke_general_machine_type
  neural_pool_machine_type  = var.gke_neural_machine_type
  enable_gpu_pool           = var.enable_gpu_pool
  gpu_type                  = var.gpu_type

  depends_on = [
    module.networking,
    google_service_account.gke_nodes[0]
  ]
}

# Deploy database infrastructure
module "database" {
  source = "./modules/database"

  project_id                    = var.project_id
  environment                   = local.environment
  region                        = var.region
  vpc_id                        = module.networking.vpc_id
  vpc_self_link                 = module.networking.vpc_self_link
  private_service_connection_id = module.networking.private_service_connection_id

  # Database configurations
  db_tier                  = var.db_tier
  db_disk_size             = var.db_disk_size
  db_password              = var.db_password
  redis_memory_gb          = var.redis_memory_gb
  redis_tier               = var.redis_tier
  enable_high_availability = var.enable_db_high_availability

  # Service accounts
  dataset_owner_email          = google_service_account.neural_ingestion.email
  neural_service_account_email = google_service_account.neural_ingestion.email

  depends_on = [
    module.networking
  ]
}

# Deploy storage infrastructure
module "storage" {
  source = "./modules/storage"

  project_id                   = var.project_id
  environment                  = local.environment
  storage_location             = var.storage_location
  backup_location              = var.backup_location
  neural_service_account_email = google_service_account.neural_ingestion.email
  storage_encryption_key       = var.enable_kms_encryption ? module.security[0].storage_key_id : ""

  # Lifecycle policies
  enable_lifecycle_policies = var.enable_storage_lifecycle_policies
  retention_period_days     = var.data_retention_days

  depends_on = [
    module.project_apis,
    google_service_account.neural_ingestion
  ]
}

# Deploy security infrastructure
module "security" {
  count  = var.enable_enhanced_security ? 1 : 0
  source = "./modules/security"

  project_id                  = var.project_id
  environment                 = local.environment
  region                      = var.region
  organization_id             = var.organization_id
  database_service_account    = "service-${data.google_project.project.number}@gcp-sa-cloud-sql.iam.gserviceaccount.com"
  storage_service_account     = google_service_account.neural_ingestion.email
  application_service_account = google_service_account.neural_ingestion.email

  # VPC Service Controls
  enable_vpc_service_controls = var.enable_vpc_service_controls
  access_policy_id            = var.access_policy_id

  # Binary Authorization
  enable_binary_authorization = var.enable_binary_authorization
  gke_cluster_name            = var.enable_gke_cluster ? module.gke[0].cluster_name : ""

  # API dependency
  apis_enabled = module.project_apis.apis_enabled

  depends_on = [
    module.project_apis,
    google_service_account.neural_ingestion
  ]
}

# Deploy monitoring infrastructure
module "monitoring" {
  source = "./modules/monitoring"

  project_id               = var.project_id
  environment              = var.environment
  region                   = var.region
  enable_monitoring_alerts = var.enable_monitoring_alerts
  notification_channels    = var.alert_notification_channels

  depends_on = [
    module.project_apis,
    module.neural_ingestion,
    module.mcp_server,
    module.gke,
    module.database,
    module.storage
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
  value       = module.monitoring.custom_metrics
  description = "Custom monitoring metrics"
}

output "function_topics" {
  value = module.neural_ingestion.function_topics
}

# MCP Server Outputs
output "mcp_server_info" {
  value       = module.mcp_server.deployment_info
  description = "MCP server deployment information"
}

output "mcp_server_service_account" {
  value       = module.mcp_server.mcp_server_service_account_email
  description = "MCP server service account email"
}

output "mcp_secret_uris" {
  value       = module.mcp_server.secret_uris
  description = "Secret Manager URIs for MCP server configuration"
}

output "mcp_server_url" {
  value       = module.mcp_server.cloud_run_service_url
  description = "MCP server Cloud Run service URL"
}

# Networking Outputs
output "vpc_id" {
  value       = module.networking.vpc_id
  description = "VPC network ID"
}

output "gke_subnet_id" {
  value       = module.networking.gke_subnet_id
  description = "GKE subnet ID"
}

output "private_subnet_id" {
  value       = module.networking.private_subnet_id
  description = "Private subnet ID"
}

# GKE Outputs (if enabled)
output "gke_cluster_endpoint" {
  value       = var.enable_gke_cluster ? module.gke[0].cluster_endpoint : null
  description = "GKE cluster endpoint"
  sensitive   = true
}

output "gke_cluster_name" {
  value       = var.enable_gke_cluster ? module.gke[0].cluster_name : null
  description = "GKE cluster name"
}

# Database Outputs
output "postgres_connection_name" {
  value       = module.database.postgres_connection_name
  description = "Cloud SQL PostgreSQL connection name"
}

output "redis_host" {
  value       = module.database.redis_host
  description = "Redis instance host"
  sensitive   = true
}

output "bigquery_dataset_id" {
  value       = module.database.bigquery_dataset_id
  description = "BigQuery dataset ID for analytics"
}

# Storage Outputs
output "neural_data_bucket" {
  value       = module.storage.neural_data_bucket_name
  description = "Neural data storage bucket name"
}

output "ml_models_bucket" {
  value       = module.storage.ml_models_bucket_name
  description = "ML models storage bucket name"
}

output "backups_bucket" {
  value       = module.storage.backups_bucket_name
  description = "Backups storage bucket name"
}

# Security Outputs (if enabled)
output "kms_keyring_id" {
  value       = var.enable_enhanced_security ? module.security[0].keyring_id : null
  description = "KMS keyring ID"
}

output "database_key_id" {
  value       = var.enable_enhanced_security ? module.security[0].database_key_id : null
  description = "Database encryption key ID"
}

output "storage_key_id" {
  value       = var.enable_enhanced_security ? module.security[0].storage_key_id : null
  description = "Storage encryption key ID"
}
