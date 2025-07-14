output "database_instance_name" {
  description = "The name of the Cloud SQL instance"
  value       = google_sql_database_instance.neurascale_console_db.name
}

output "database_connection_name" {
  description = "The connection name of the Cloud SQL instance"
  value       = google_sql_database_instance.neurascale_console_db.connection_name
}

output "database_public_ip" {
  description = "The public IP address of the Cloud SQL instance"
  value       = google_sql_database_instance.neurascale_console_db.public_ip_address
}

output "database_private_ip" {
  description = "The private IP address of the Cloud SQL instance"
  value       = google_sql_database_instance.neurascale_console_db.private_ip_address
}

output "database_name" {
  description = "The name of the database"
  value       = google_sql_database.neurascale_console.name
}

output "database_username" {
  description = "The username for the database"
  value       = google_sql_user.neurascale_console_user.name
  sensitive   = true
}

output "service_account_email" {
  description = "The email of the service account"
  value       = google_service_account.neurascale_console_sa.email
}

output "database_url" {
  description = "The database URL for the application"
  value       = "postgresql://${google_sql_user.neurascale_console_user.name}:${random_password.db_password.result}@${google_sql_database_instance.neurascale_console_db.public_ip_address}:5432/${google_sql_database.neurascale_console.name}"
  sensitive   = true
}
