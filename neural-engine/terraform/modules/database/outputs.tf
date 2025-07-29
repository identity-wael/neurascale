# Outputs for Database Module

# Cloud SQL Outputs
output "postgres_instance_name" {
  description = "The name of the PostgreSQL instance"
  value       = google_sql_database_instance.postgres.name
}

output "postgres_connection_name" {
  description = "The connection name of the PostgreSQL instance"
  value       = google_sql_database_instance.postgres.connection_name
}

output "postgres_ip_address" {
  description = "The IP address of the PostgreSQL instance"
  value       = google_sql_database_instance.postgres.ip_address[0].ip_address
  sensitive   = true
}

output "postgres_database_name" {
  description = "The name of the PostgreSQL database"
  value       = google_sql_database.neural_db.name
}

output "postgres_user" {
  description = "The PostgreSQL user name"
  value       = google_sql_user.app_user.name
}

output "postgres_password" {
  description = "The PostgreSQL password (generated if not provided)"
  value       = var.db_password != "" ? var.db_password : (length(random_password.db_password) > 0 ? random_password.db_password[0].result : "")
  sensitive   = true
}

output "postgres_readonly_user" {
  description = "The PostgreSQL readonly user name (if created)"
  value       = var.create_readonly_user ? google_sql_user.readonly_user[0].name : null
}

output "postgres_replica_names" {
  description = "The names of PostgreSQL read replicas"
  value       = var.enable_read_replica ? [google_sql_database_instance.read_replica[0].name] : []
}

output "postgres_replica_connection_names" {
  description = "The connection names of PostgreSQL read replicas"
  value       = var.enable_read_replica ? [google_sql_database_instance.read_replica[0].connection_name] : []
}

# Redis Outputs
output "redis_host" {
  description = "The hostname of the Redis instance"
  value       = google_redis_instance.cache.host
  sensitive   = true
}

output "redis_port" {
  description = "The port of the Redis instance"
  value       = google_redis_instance.cache.port
}

output "redis_auth_string" {
  description = "The auth string for the Redis instance"
  value       = google_redis_instance.cache.auth_string
  sensitive   = true
}

output "redis_instance_id" {
  description = "The ID of the Redis instance"
  value       = google_redis_instance.cache.id
}

output "redis_current_location_id" {
  description = "The current location of the Redis instance"
  value       = google_redis_instance.cache.current_location_id
}

output "streaming_redis_host" {
  description = "The hostname of the streaming Redis instance (if enabled)"
  value       = var.enable_streaming_redis ? google_redis_instance.streaming[0].host : null
  sensitive   = true
}

output "streaming_redis_port" {
  description = "The port of the streaming Redis instance (if enabled)"
  value       = var.enable_streaming_redis ? google_redis_instance.streaming[0].port : null
}

output "streaming_redis_auth_string" {
  description = "The auth string for the streaming Redis instance (if enabled)"
  value       = var.enable_streaming_redis ? google_redis_instance.streaming[0].auth_string : null
  sensitive   = true
}

# BigQuery Outputs
output "bigquery_dataset_id" {
  description = "The ID of the BigQuery dataset"
  value       = google_bigquery_dataset.neural_analytics.dataset_id
}

output "bigquery_dataset_location" {
  description = "The location of the BigQuery dataset"
  value       = google_bigquery_dataset.neural_analytics.location
}

output "bigquery_sessions_table_id" {
  description = "The ID of the neural sessions table"
  value       = google_bigquery_table.neural_sessions.table_id
}

output "bigquery_metrics_table_id" {
  description = "The ID of the neural metrics table"
  value       = google_bigquery_table.neural_metrics.table_id
}

output "bigquery_ml_training_table_id" {
  description = "The ID of the ML training data table"
  value       = google_bigquery_table.ml_training_data.table_id
}

# Connection strings (for application configuration)
output "postgres_connection_string" {
  description = "PostgreSQL connection string (without password)"
  value       = "postgresql://${google_sql_user.app_user.name}@${google_sql_database_instance.postgres.connection_name}/${google_sql_database.neural_db.name}"
  sensitive   = true
}

output "redis_connection_string" {
  description = "Redis connection string (without auth)"
  value       = "redis://${google_redis_instance.cache.host}:${google_redis_instance.cache.port}"
  sensitive   = true
}
