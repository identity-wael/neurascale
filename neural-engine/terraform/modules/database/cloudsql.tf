# Cloud SQL PostgreSQL Instance for NeuraScale Neural Engine
# HIPAA-compliant configuration with high availability

resource "google_sql_database_instance" "postgres" {
  name             = "${var.environment}-neural-postgres"
  database_version = var.postgres_version
  region           = var.region
  project          = var.project_id

  settings {
    tier                  = var.db_tier
    availability_type     = var.enable_high_availability ? "REGIONAL" : "ZONAL"
    disk_size             = var.db_disk_size
    disk_type             = "PD_SSD"
    disk_autoresize       = true
    disk_autoresize_limit = var.db_disk_autoresize_limit

    # Backup configuration for HIPAA compliance
    backup_configuration {
      enabled                        = true
      start_time                     = var.backup_start_time
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = var.transaction_log_retention_days
      location                       = var.backup_location

      backup_retention_settings {
        retained_backups = var.backup_retention_count
        retention_unit   = "COUNT"
      }
    }

    # IP configuration
    ip_configuration {
      ipv4_enabled    = false # Private IP only for security
      private_network = var.vpc_self_link
      require_ssl     = true
    }

    # Database flags for performance and security
    dynamic "database_flags" {
      for_each = var.database_flags
      content {
        name  = database_flags.key
        value = database_flags.value
      }
    }

    # Query insights for monitoring
    insights_config {
      query_insights_enabled  = true
      query_string_length     = 1024
      record_application_tags = true
      record_client_address   = true
    }

    # Maintenance window
    maintenance_window {
      day          = var.maintenance_day
      hour         = var.maintenance_hour
      update_track = "stable"
    }

    # User labels
    user_labels = merge(
      var.labels,
      {
        environment = var.environment
        component   = "database"
        type        = "postgresql"
      }
    )
  }

  # Database encryption with Cloud KMS
  encryption_key_name = var.database_encryption_key

  # Deletion protection
  deletion_protection = var.deletion_protection

  depends_on = [var.private_service_connection_id]
}

# Database creation
resource "google_sql_database" "neural_db" {
  name      = var.database_name
  instance  = google_sql_database_instance.postgres.name
  charset   = "UTF8"
  collation = "en_US.UTF8"
}

# Generate random password if not provided
resource "random_password" "db_password" {
  count   = var.db_password == "" ? 1 : 0
  length  = 32
  special = true
}

# Database user
resource "google_sql_user" "app_user" {
  name     = var.db_user
  instance = google_sql_database_instance.postgres.name
  password = var.db_password != "" ? var.db_password : random_password.db_password[0].result
}

# Generate random readonly password if not provided
resource "random_password" "db_readonly_password" {
  count   = var.create_readonly_user && var.db_readonly_password == "" ? 1 : 0
  length  = 32
  special = true
}

# Additional read-only user for analytics
resource "google_sql_user" "readonly_user" {
  count = var.create_readonly_user ? 1 : 0

  name     = "${var.db_user}_readonly"
  instance = google_sql_database_instance.postgres.name
  password = var.db_readonly_password != "" ? var.db_readonly_password : random_password.db_readonly_password[0].result
}

# Database replica for read scaling (if enabled)
resource "google_sql_database_instance" "read_replica" {
  count = var.enable_read_replica ? 1 : 0

  name                 = "${var.environment}-neural-postgres-replica"
  database_version     = var.postgres_version
  region               = var.replica_region != "" ? var.replica_region : var.region
  master_instance_name = google_sql_database_instance.postgres.name

  replica_configuration {
    failover_target = false
  }

  settings {
    tier              = var.replica_tier != "" ? var.replica_tier : var.db_tier
    availability_type = "ZONAL"
    disk_size         = var.db_disk_size
    disk_type         = "PD_SSD"
    disk_autoresize   = true

    ip_configuration {
      ipv4_enabled    = false
      private_network = var.vpc_self_link
      require_ssl     = true
    }

    database_flags {
      name  = "max_connections"
      value = "1000"
    }

    user_labels = merge(
      var.labels,
      {
        environment = var.environment
        component   = "database"
        type        = "postgresql"
        role        = "read-replica"
      }
    )
  }

  depends_on = [google_sql_database_instance.postgres]
}
