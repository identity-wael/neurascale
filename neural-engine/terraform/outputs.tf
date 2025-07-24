# Outputs from Neural Engine infrastructure

output "environment" {
  description = "The deployment environment"
  value       = local.environment
}

output "project_id" {
  description = "The GCP project ID"
  value       = var.project_id
}

output "region" {
  description = "The GCP region"
  value       = var.region
}

output "ingestion_service_account" {
  description = "Email of the neural ingestion service account"
  value       = google_service_account.neural_ingestion.email
}

output "pubsub_topics" {
  description = "Map of signal types to Pub/Sub topic IDs"
  value       = module.neural_ingestion.pubsub_topics
}

output "bigtable_instance" {
  description = "Bigtable instance ID for neural data storage"
  value       = module.neural_ingestion.bigtable_instance_id
}

output "cloud_functions_bucket" {
  description = "GCS bucket for Cloud Functions source code"
  value       = module.neural_ingestion.functions_bucket
}

output "artifact_registry_url" {
  description = "URL of the Artifact Registry repository"
  value       = module.neural_ingestion.artifact_registry_url
}

output "cloud_functions" {
  description = "Map of deployed Cloud Functions"
  value       = module.neural_ingestion.cloud_functions
}
