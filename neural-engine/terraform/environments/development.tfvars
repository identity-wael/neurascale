# Development environment configuration
project_id  = "development-neurascale"
environment = "development"
region      = "northamerica-northeast1"

# Bigtable configuration
bigtable_nodes       = 1
bigtable_min_nodes   = 1
bigtable_max_nodes   = 2
bigtable_ssd_size_gb = 128
bigtable_cpu_target  = 80

# Security settings
enable_deletion_protection  = false
enable_vpc_service_controls = false

# Monitoring
enable_monitoring_alerts    = false
alert_notification_channels = []

# Cost optimization
enable_scheduled_scaling    = true # Scale down during off-hours
enable_bigtable_autoscaling = false
bigtable_nodes_dev          = 2
bigtable_min_nodes_dev      = 1
budget_amount               = "1000"
cost_center                 = "neural-research-dev"

# MCP Server configuration
enable_mcp_cloud_run     = true
mcp_server_image         = "northamerica-northeast1-docker.pkg.dev/development-neurascale/neural-engine-development/mcp-server:latest"
mcp_min_instances        = 0
mcp_max_instances        = 3
enable_mcp_public_access = false # Keep private in development

# Networking configuration
gke_subnet_cidr     = "10.0.0.0/20"
private_subnet_cidr = "10.0.16.0/20"
pods_cidr           = "10.1.0.0/16"
services_cidr       = "10.2.0.0/20"

# GKE configuration (disabled by default in dev)
enable_gke_cluster       = false
gke_general_machine_type = "n2-standard-2" # Smaller for dev
gke_neural_machine_type  = "n2-highmem-4"  # Smaller for dev
enable_gpu_pool          = false
gpu_type                 = "nvidia-tesla-t4"

# Database configuration
db_tier                     = "db-g1-small"
db_disk_size                = 50 # Smaller for dev
redis_memory_gb             = 2  # Smaller for dev
redis_tier                  = "BASIC"
enable_db_high_availability = false
