# Outputs from neural-ingestion module

output "artifact_registry_url" {
  value       = google_artifact_registry_repository.neural_engine.name
  description = "URL of the Artifact Registry repository"
}

output "pubsub_topics" {
  value = {
    for k, v in google_pubsub_topic.neural_data : k => v.id
  }
  description = "Map of signal types to Pub/Sub topic IDs"
}

output "bigtable_instance_id" {
  value       = google_bigtable_instance.neural_data.id
  description = "Bigtable instance ID"
}

output "functions_bucket" {
  value       = google_storage_bucket.functions.name
  description = "GCS bucket for Cloud Functions source code"
}

output "function_topics" {
  value = {
    for k, v in google_pubsub_topic.neural_data : k => v.name
  }
  description = "Pub/Sub topics for Cloud Functions to subscribe to"
}

# Outputs from cloud_functions.tf
output "cloud_function_urls" {
  value = var.enable_cloud_functions ? {
    for k, v in google_cloudfunctions2_function.process_neural_stream : k => v.service_config[0].uri
  } : {}
  description = "URLs of deployed Cloud Functions"
}

output "cloud_function_names" {
  value = var.enable_cloud_functions ? {
    for k, v in google_cloudfunctions2_function.process_neural_stream : k => v.name
  } : {}
  description = "Names of deployed Cloud Functions"
}

output "service_account_email" {
  value       = google_service_account.ingestion.email
  description = "Email of the ingestion service account"
}
