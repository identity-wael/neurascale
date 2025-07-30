# Staging environment configuration
project_id  = "staging-neurascale"
environment = "staging"
region      = "northamerica-northeast1"

# Bigtable configuration
bigtable_nodes       = 1
bigtable_min_nodes   = 1
bigtable_max_nodes   = 3
bigtable_ssd_size_gb = 256
bigtable_cpu_target  = 70

# Security settings
enable_deletion_protection  = false
enable_vpc_service_controls = false

# Monitoring
enable_monitoring_alerts    = true
alert_notification_channels = [] # Add Slack channel IDs here

# Cost optimization
enable_bigtable_autoscaling = false
bigtable_nodes_dev          = 2
bigtable_min_nodes_dev      = 1

# Temporarily disable cloud functions to debug timeout
enable_cloud_functions = false

# MCP Server configuration
enable_mcp_cloud_run     = false # Disabled to prevent deployment conflicts
mcp_server_image         = "northamerica-northeast1-docker.pkg.dev/staging-neurascale/neural-engine-staging/mcp-server:latest"
mcp_min_instances        = 1
mcp_max_instances        = 5
enable_mcp_public_access = false # Keep private, access via VPN/IAP

# Networking configuration
gke_subnet_cidr     = "10.0.0.0/20"
private_subnet_cidr = "10.0.16.0/20"
pods_cidr           = "10.1.0.0/16"
services_cidr       = "10.2.0.0/20"

# GKE configuration
enable_gke_cluster       = false # Temporarily disabled - GKE API error
gke_general_machine_type = "n2-standard-4"
gke_neural_machine_type  = "n2-highmem-8"
enable_gpu_pool          = false # Can enable for ML testing
gpu_type                 = "nvidia-tesla-t4"

# Database configuration
enable_database             = false # Temporarily disabled - Cloud SQL API error in source project
db_tier                     = "db-custom-2-7680"
db_disk_size                = 200
redis_memory_gb             = 8
redis_tier                  = "STANDARD_HA"
enable_db_high_availability = true

# Storage configuration
storage_location                  = "US"
backup_location                   = "EUROPE-WEST1" # Different continent for DR
enable_storage_lifecycle_policies = true
data_retention_days               = 365 # 1 year for staging

# Security configuration
enable_enhanced_security    = false # Disabled - requires KMS API in neurascale project
enable_kms_encryption       = false # Disabled - requires KMS API in neurascale project
enable_binary_authorization = false

# Cost optimization
enable_scheduled_scaling   = false # Disabled - Cloud Build permissions issue
budget_amount              = "2000"
cost_center                = "neural-research-staging"
budget_notification_emails = [] # Add team emails here
