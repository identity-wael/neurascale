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
enable_deletion_protection  = true # Production parity
enable_vpc_service_controls = true # Production parity

# Monitoring
enable_monitoring_alerts    = true
alert_notification_channels = [] # Add Slack channel IDs here

# Cost optimization
enable_bigtable_autoscaling = false
bigtable_nodes_dev          = 2
bigtable_min_nodes_dev      = 1

# Cloud functions enabled for production parity
enable_cloud_functions = true

# MCP Server configuration
enable_mcp_cloud_run     = false # Temporarily disabled - similar to production
mcp_server_image         = "northamerica-northeast1-docker.pkg.dev/staging-neurascale/neural-engine-staging/mcp-server:latest"
mcp_min_instances        = 2 # Match production - always keep minimum instances
mcp_max_instances        = 20 # Match production
enable_mcp_public_access = true # Production parity - with proper security

# Networking configuration
gke_subnet_cidr     = "10.0.0.0/20"
private_subnet_cidr = "10.0.16.0/20"
pods_cidr           = "10.1.0.0/16"
services_cidr       = "10.2.0.0/20"

# GKE configuration
enable_gke_cluster       = true # Enabled for PR testing with production parity
gke_general_machine_type = "n2-standard-4"
gke_neural_machine_type  = "n2-highmem-8"
enable_gpu_pool          = true # Enabled for production parity
gpu_type                 = "nvidia-tesla-t4"

# GKE node pool configurations for staging (minimal for cost optimization)
general_pool_node_count = 2
general_pool_min_nodes  = 1
general_pool_max_nodes  = 5
neural_pool_node_count  = 1
neural_pool_min_nodes   = 0
neural_pool_max_nodes   = 3

# Database configuration
enable_database             = true # Enabled for production parity
db_tier                     = "db-custom-2-7680"
db_disk_size                = 200
redis_memory_gb             = 32 # Match production
redis_tier                  = "STANDARD_HA"
enable_db_high_availability = true

# Storage configuration
storage_location                  = "US"
backup_location                   = "ASIA-SOUTHEAST1" # Different continent for DR (match production)
enable_storage_lifecycle_policies = true
data_retention_days               = 2555 # 7 years for HIPAA compliance (match production)

# Security configuration
enable_enhanced_security    = true # Full security for production parity
enable_kms_encryption       = true # KMS encryption for production parity
enable_binary_authorization = true # Binary authorization for production parity

# Cost optimization
enable_scheduled_scaling   = false # Match production - no auto-scaling
enable_cost_analysis       = false # Temporarily disabled - BigQuery Data Transfer API issue (match production)
budget_amount              = "5000" # Higher budget for production parity testing
cost_center                = "neural-research-staging"
budget_notification_emails = [] # Add team emails here
billing_export_dataset     = "" # Temporarily disabled - BigQuery Data Transfer API issue (match production)
