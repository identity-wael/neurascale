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
mcp_server_image         = "gcr.io/production-neurascale/mcp-server:latest"
mcp_min_instances        = 2 # Always keep minimum instances for availability
mcp_max_instances        = 20
enable_mcp_public_access = true # Production may need public access with proper security
