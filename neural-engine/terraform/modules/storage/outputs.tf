# Outputs for Storage Module

output "neural_data_bucket_name" {
  description = "Name of the neural data storage bucket"
  value       = google_storage_bucket.neural_data.name
}

output "neural_data_bucket_url" {
  description = "URL of the neural data storage bucket"
  value       = google_storage_bucket.neural_data.url
}

output "ml_models_bucket_name" {
  description = "Name of the ML models storage bucket"
  value       = google_storage_bucket.ml_models.name
}

output "ml_models_bucket_url" {
  description = "URL of the ML models storage bucket"
  value       = google_storage_bucket.ml_models.url
}

output "temp_processing_bucket_name" {
  description = "Name of the temporary processing bucket"
  value       = google_storage_bucket.temp_processing.name
}

output "backups_bucket_name" {
  description = "Name of the backups bucket"
  value       = google_storage_bucket.backups.name
}

output "functions_source_bucket_name" {
  description = "Name of the functions source bucket"
  value       = google_storage_bucket.functions_source.name
}

output "logs_bucket_name" {
  description = "Name of the logs bucket"
  value       = var.enable_logging ? google_storage_bucket.logs[0].name : null
}

output "storage_transfer_job_name" {
  description = "Name of the storage transfer job for backups"
  value       = var.enable_storage_transfer ? google_storage_transfer_job.backup_transfer[0].name : null
}

output "bucket_suffix" {
  description = "Random suffix used for bucket names"
  value       = random_id.bucket_suffix.hex
}
