# Staging environment configuration
project_id = "staging-neurascale"
environment = "staging"
region = "northamerica-northeast1"

# Bigtable configuration
bigtable_nodes = 1
bigtable_min_nodes = 1
bigtable_max_nodes = 3
bigtable_ssd_size_gb = 256
bigtable_cpu_target = 70

# Security settings
enable_deletion_protection = false
enable_vpc_service_controls = false

# Monitoring
enable_monitoring_alerts = true
alert_notification_channels = []  # Add Slack channel IDs here

# Cost optimization
enable_scheduled_scaling = true  # Scale down during off-hours
enable_bigtable_autoscaling = false
bigtable_nodes_dev = 2
bigtable_min_nodes_dev = 1
budget_amount = "2000"
cost_center = "neural-research-staging"
