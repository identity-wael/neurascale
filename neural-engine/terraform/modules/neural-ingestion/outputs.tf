# Outputs from the neural-ingestion module

output "pubsub_topics" {
  description = "Map of signal types to Pub/Sub topic IDs"
  value = {
    for k, v in google_pubsub_topic.neural_data : k => v.id
  }
}

output "dead_letter_topic" {
  description = "Dead letter topic ID"
  value       = google_pubsub_topic.dead_letter.id
}

output "pubsub_subscriptions" {
  description = "Map of signal types to Pub/Sub subscription IDs"
  value = {
    for k, v in google_pubsub_subscription.neural_data : k => v.id
  }
}

output "bigtable_instance_id" {
  description = "Bigtable instance ID"
  value       = google_bigtable_instance.neural_data.id
}

output "bigtable_instance_name" {
  description = "Bigtable instance name"
  value       = google_bigtable_instance.neural_data.name
}

output "functions_bucket" {
  description = "GCS bucket name for Cloud Functions source"
  value       = google_storage_bucket.functions.name
}

output "functions_bucket_url" {
  description = "GCS bucket URL for Cloud Functions source"
  value       = google_storage_bucket.functions.url
}

output "artifact_registry_url" {
  description = "Artifact Registry repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.neural_engine.repository_id}"
}

output "artifact_registry_id" {
  description = "Artifact Registry repository ID"
  value       = google_artifact_registry_repository.neural_engine.repository_id
}

output "cloud_functions" {
  description = "Map of signal types to Cloud Function names"
  value = {
    for k, v in google_cloudfunctions2_function.process_neural_stream : k => v.name
  }
}

output "cloud_function_urls" {
  description = "Map of signal types to Cloud Function service URLs"
  value = {
    for k, v in google_cloudfunctions2_function.process_neural_stream : k => v.service_config[0].uri
  }
}
