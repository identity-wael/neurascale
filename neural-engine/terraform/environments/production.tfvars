# Production environment configuration
project_id  = "production-neurascale"
environment = "production"
region      = "northamerica-northeast1"

# Bigtable configuration
bigtable_nodes       = 3
bigtable_min_nodes   = 2
bigtable_max_nodes   = 10
bigtable_ssd_size_gb = 1024
bigtable_cpu_target  = 60

# Security settings
enable_deletion_protection  = true
enable_vpc_service_controls = true

# Monitoring
enable_monitoring_alerts    = true
alert_notification_channels = [] # Add PagerDuty channel IDs here

# Cost optimization
enable_scheduled_scaling    = false # Production runs 24/7
enable_bigtable_autoscaling = true  # Enable autoscaling for production
budget_amount               = "10000"
cost_center                 = "neural-research-prod"

# MCP Server configuration
enable_mcp_cloud_run     = true
mcp_server_image         = "northamerica-northeast1-docker.pkg.dev/production-neurascale/neural-engine-production/mcp-server:latest"
mcp_min_instances        = 2 # Always keep minimum instances for availability
mcp_max_instances        = 20
enable_mcp_public_access = true # Production may need public access with proper security

# Networking configuration
gke_subnet_cidr     = "10.0.0.0/20"
private_subnet_cidr = "10.0.16.0/20"
pods_cidr           = "10.1.0.0/16"
services_cidr       = "10.2.0.0/20"

# GKE configuration
enable_gke_cluster       = true
gke_general_machine_type = "n2-standard-8"
gke_neural_machine_type  = "n2-highmem-16"
enable_gpu_pool          = true
gpu_type                 = "nvidia-tesla-t4"

# Database configuration
db_tier                     = "db-n1-highmem-8"
db_disk_size                = 1000
redis_memory_gb             = 32
redis_tier                  = "STANDARD_HA"
enable_db_high_availability = true
