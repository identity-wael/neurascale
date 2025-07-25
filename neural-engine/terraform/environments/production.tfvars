# Production environment configuration
project_id = "production-neurascale"
environment = "production"
region = "northamerica-northeast1"

# Bigtable configuration
bigtable_nodes = 3
bigtable_min_nodes = 2
bigtable_max_nodes = 10
bigtable_ssd_size_gb = 1024
bigtable_cpu_target = 60

# Security settings
enable_deletion_protection = true
enable_vpc_service_controls = true

# Monitoring
enable_monitoring_alerts = true
alert_notification_channels = []  # Add PagerDuty channel IDs here

# Cost optimization
enable_scheduled_scaling = false  # Production runs 24/7
