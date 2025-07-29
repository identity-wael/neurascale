# Outputs for Security Module

output "keyring_id" {
  description = "ID of the KMS keyring"
  value       = google_kms_key_ring.neural_engine.id
}

output "database_key_id" {
  description = "ID of the database encryption key"
  value       = google_kms_crypto_key.database.id
}

output "storage_key_id" {
  description = "ID of the storage encryption key"
  value       = google_kms_crypto_key.storage.id
}

output "application_key_id" {
  description = "ID of the application secrets encryption key"
  value       = google_kms_crypto_key.application.id
}

output "bigquery_key_id" {
  description = "ID of the BigQuery encryption key"
  value       = google_kms_crypto_key.bigquery.id
}

output "kms_admin_service_account" {
  description = "Email of the KMS admin service account"
  value       = google_service_account.kms_admin.email
}

output "database_password_secret_id" {
  description = "ID of the database password secret"
  value       = google_secret_manager_secret.database_password.id
}

output "database_password_secret_name" {
  description = "Name of the database password secret"
  value       = google_secret_manager_secret.database_password.name
}

output "api_keys_secret_id" {
  description = "ID of the API keys secret"
  value       = google_secret_manager_secret.api_keys.id
}

output "jwt_secret_id" {
  description = "ID of the JWT secret"
  value       = google_secret_manager_secret.jwt_secret.id
}

output "vpc_service_perimeter_name" {
  description = "Name of the VPC Service Control perimeter"
  value       = var.enable_vpc_service_controls ? google_access_context_manager_service_perimeter.neural_engine[0].name : null
}

output "binary_authorization_policy_id" {
  description = "ID of the Binary Authorization policy"
  value       = var.enable_binary_authorization ? google_binary_authorization_policy.policy[0].id : null
}

output "attestor_name" {
  description = "Name of the Binary Authorization attestor"
  value       = var.enable_binary_authorization ? google_binary_authorization_attestor.neural_engine[0].name : null
}
