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
