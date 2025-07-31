# GKE Cluster Module for NeuraScale Neural Engine
# Creates a HIPAA-compliant GKE cluster with GPU support

# GKE Cluster
resource "google_container_cluster" "neural_engine" {
  name     = "${var.environment}-neural-engine"
  location = var.regional_cluster ? var.region : var.zone

  # Don't create default node pool
  initial_node_count       = 1
  remove_default_node_pool = true

  # Network configuration
  network    = var.vpc_id
  subnetwork = var.subnet_id

  # Cluster version - only set if specified
  min_master_version = var.kubernetes_version != "" ? var.kubernetes_version : null

  # HIPAA-compliant security settings
  enable_shielded_nodes       = true
  enable_intranode_visibility = true

  # Binary authorization for container image security
  binary_authorization {
    evaluation_mode = var.enable_binary_authorization ? "PROJECT_SINGLETON_POLICY_ENFORCE" : "DISABLED"
  }

  # Private cluster configuration
  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = var.enable_private_endpoint
    master_ipv4_cidr_block  = var.master_cidr
  }

  # IP allocation policy for pods and services
  ip_allocation_policy {
    cluster_secondary_range_name  = var.pods_secondary_range_name
    services_secondary_range_name = var.services_secondary_range_name
  }

  # Workload identity for pod-level IAM
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Add-on configurations
  addons_config {
    http_load_balancing {
      disabled = false
    }

    horizontal_pod_autoscaling {
      disabled = false
    }

    network_policy_config {
      disabled = false
    }

    gce_persistent_disk_csi_driver_config {
      enabled = true
    }

    dns_cache_config {
      enabled = true
    }
  }

  # Monitoring and logging
  monitoring_service = "monitoring.googleapis.com/kubernetes"
  logging_service    = "logging.googleapis.com/kubernetes"

  monitoring_config {
    enable_components = ["SYSTEM_COMPONENTS", "WORKLOADS"]

    managed_prometheus {
      enabled = true
    }
  }

  # Security settings
  master_auth {
    client_certificate_config {
      issue_client_certificate = false
    }
  }

  # Network security
  master_authorized_networks_config {
    dynamic "cidr_blocks" {
      for_each = var.authorized_networks
      content {
        cidr_block   = cidr_blocks.value.cidr_block
        display_name = cidr_blocks.value.display_name
      }
    }
  }

  # Maintenance window
  maintenance_policy {
    recurring_window {
      start_time = var.maintenance_start_time
      end_time   = var.maintenance_end_time
      recurrence = "FREQ=WEEKLY;BYDAY=SA"
    }
  }

  # Database encryption
  database_encryption {
    state    = var.database_encryption_key != "" ? "ENCRYPTED" : "DECRYPTED"
    key_name = var.database_encryption_key
  }

  # Enable cluster telemetry via logging config
  # Note: cluster_telemetry block was deprecated in favor of monitoring_config

  # Resource usage export to BigQuery - disabled for now
  # dynamic "resource_usage_export_config" {
  #   for_each = var.resource_usage_dataset_id != "" ? [1] : []
  #   content {
  #     enable_network_egress_metering       = true
  #     enable_resource_consumption_metering = true

  #     bigquery_destination {
  #       dataset_id = var.resource_usage_dataset_id
  #     }
  #   }
  # }

  # Labels
  resource_labels = merge(
    var.labels,
    {
      environment = var.environment
      managed_by  = "terraform"
    }
  )

  # Lifecycle
  lifecycle {
    prevent_destroy = true
    ignore_changes  = [node_pool]
  }
}

# General compute node pool
resource "google_container_node_pool" "general" {
  name       = "${var.environment}-general-pool"
  cluster    = google_container_cluster.neural_engine.name
  location   = google_container_cluster.neural_engine.location
  node_count = var.general_pool_node_count

  node_config {
    preemptible  = var.environment != "production"
    machine_type = var.general_pool_machine_type
    disk_size_gb = var.general_pool_disk_size
    disk_type    = "pd-ssd"
    image_type   = "COS_CONTAINERD"

    # Service account
    service_account = var.node_service_account_email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    # Security hardening
    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }

    # Metadata
    metadata = {
      disable-legacy-endpoints = "true"
    }

    # Labels
    labels = merge(
      var.labels,
      {
        environment = var.environment
        node_pool   = "general"
      }
    )

    # Workload metadata
    workload_metadata_config {
      mode = "GKE_METADATA"
    }
  }

  # Autoscaling
  autoscaling {
    min_node_count  = var.general_pool_min_nodes
    max_node_count  = var.general_pool_max_nodes
    location_policy = "BALANCED"
  }

  # Management
  management {
    auto_repair  = true
    auto_upgrade = true
  }

  # Upgrade settings
  upgrade_settings {
    max_surge       = 1
    max_unavailable = 0
  }
}

# Neural compute node pool (high memory/CPU)
resource "google_container_node_pool" "neural_compute" {
  name       = "${var.environment}-neural-compute-pool"
  cluster    = google_container_cluster.neural_engine.name
  location   = google_container_cluster.neural_engine.location
  node_count = var.neural_pool_node_count

  node_config {
    preemptible  = false # Neural processing needs stability
    machine_type = var.neural_pool_machine_type
    disk_size_gb = var.neural_pool_disk_size
    disk_type    = "pd-ssd"
    image_type   = "COS_CONTAINERD"

    # Service account
    service_account = var.node_service_account_email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    # Security hardening
    shielded_instance_config {
      enable_secure_boot          = true
      enable_integrity_monitoring = true
    }

    # Labels
    labels = merge(
      var.labels,
      {
        environment = var.environment
        node_pool   = "neural-compute"
        workload    = "neural-processing"
      }
    )

    # Taints for dedicated neural workloads
    taint {
      key    = "neural-compute"
      value  = "true"
      effect = "NO_SCHEDULE"
    }

    # Local SSD for high-performance data processing
    local_ssd_count = var.neural_pool_local_ssd_count
  }

  # Autoscaling
  autoscaling {
    min_node_count  = var.neural_pool_min_nodes
    max_node_count  = var.neural_pool_max_nodes
    location_policy = "BALANCED"
  }

  # Management
  management {
    auto_repair  = true
    auto_upgrade = true
  }
}

# GPU node pool for ML workloads (if enabled)
resource "google_container_node_pool" "gpu" {
  count = var.enable_gpu_pool ? 1 : 0

  name       = "${var.environment}-gpu-pool"
  cluster    = google_container_cluster.neural_engine.name
  location   = google_container_cluster.neural_engine.location
  node_count = var.gpu_pool_node_count

  node_config {
    preemptible  = var.gpu_pool_preemptible
    machine_type = var.gpu_pool_machine_type
    disk_size_gb = 100
    disk_type    = "pd-ssd"
    image_type   = "COS_CONTAINERD"

    # GPU configuration
    guest_accelerator {
      type  = var.gpu_type
      count = var.gpu_count_per_node
    }

    # Service account
    service_account = var.node_service_account_email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    # Metadata for GPU driver installation
    metadata = {
      "install-nvidia-driver" = "true"
    }

    # Labels
    labels = merge(
      var.labels,
      {
        environment = var.environment
        node_pool   = "gpu"
        workload    = "ml-training"
      }
    )

    # Taints for GPU workloads
    taint {
      key    = "nvidia.com/gpu"
      value  = "present"
      effect = "NO_SCHEDULE"
    }
  }

  # Autoscaling
  autoscaling {
    min_node_count  = var.gpu_pool_min_nodes
    max_node_count  = var.gpu_pool_max_nodes
    location_policy = "ANY"
  }

  # Management
  management {
    auto_repair  = true
    auto_upgrade = false # Manual upgrades for GPU drivers
  }

  # Lifecycle to handle GPU availability
  lifecycle {
    create_before_destroy = true
  }
}
