# Redis Instance for NeuraScale Neural Engine
# High-performance caching for neural data and session management

resource "google_redis_instance" "cache" {
  name                    = "${var.environment}-neural-cache"
  memory_size_gb          = var.redis_memory_gb
  region                  = var.region
  location_id             = var.redis_zone
  alternative_location_id = var.redis_alternative_zone

  # Redis version
  redis_version = var.redis_version

  # Display name
  display_name = "${title(var.environment)} Neural Engine Cache"

  # High availability tier
  tier = var.redis_tier

  # Network configuration
  authorized_network = var.vpc_id
  connect_mode       = "PRIVATE_SERVICE_ACCESS"

  # Redis configuration
  redis_configs = merge(
    {
      "maxmemory-policy" = var.redis_eviction_policy
    },
    var.redis_configs
  )

  # Persistence configuration
  persistence_config {
    persistence_mode        = var.redis_persistence_mode
    rdb_snapshot_period     = var.redis_snapshot_period
    rdb_snapshot_start_time = var.redis_snapshot_start_time
  }

  # Maintenance policy
  maintenance_policy {
    weekly_maintenance_window {
      day = var.maintenance_day_redis
      start_time {
        hours   = var.maintenance_hour_redis
        minutes = 0
        seconds = 0
        nanos   = 0
      }
    }
  }

  # Labels
  labels = merge(
    var.labels,
    {
      environment = var.environment
      component   = "cache"
      type        = "redis"
    }
  )

  # Enable AUTH for security
  auth_enabled = true

  # Transit encryption
  transit_encryption_mode = "SERVER_AUTHENTICATION"

  depends_on = [var.private_service_connection_id]
}

# Redis instance for real-time neural data streaming (if enabled)
resource "google_redis_instance" "streaming" {
  count = var.enable_streaming_redis ? 1 : 0

  name           = "${var.environment}-neural-streaming"
  memory_size_gb = var.streaming_redis_memory_gb
  region         = var.region
  location_id    = var.redis_zone

  # Redis version
  redis_version = var.redis_version

  # Display name
  display_name = "${title(var.environment)} Neural Streaming Cache"

  # Basic tier for cost optimization (streaming doesn't need HA)
  tier = "BASIC"

  # Network configuration
  authorized_network = var.vpc_id
  connect_mode       = "PRIVATE_SERVICE_ACCESS"

  # Redis configuration optimized for streaming
  redis_configs = {
    "maxmemory-policy" = "allkeys-lru"
    "timeout"          = "300"
    "tcp-keepalive"    = "60"
    "maxclients"       = "10000"
  }

  # No persistence for streaming cache
  persistence_config {
    persistence_mode = "DISABLED"
  }

  # Labels
  labels = merge(
    var.labels,
    {
      environment = var.environment
      component   = "cache"
      type        = "redis"
      purpose     = "streaming"
    }
  )

  # Enable AUTH
  auth_enabled = true

  # Transit encryption
  transit_encryption_mode = "SERVER_AUTHENTICATION"

  depends_on = [var.private_service_connection_id]
}
