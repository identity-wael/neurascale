# Outputs for GKE Module

output "cluster_id" {
  description = "The ID of the GKE cluster"
  value       = google_container_cluster.neural_engine.id
}

output "cluster_name" {
  description = "The name of the GKE cluster"
  value       = google_container_cluster.neural_engine.name
}

output "cluster_endpoint" {
  description = "The endpoint of the GKE cluster"
  value       = google_container_cluster.neural_engine.endpoint
  sensitive   = true
}

output "cluster_master_version" {
  description = "The master version of the GKE cluster"
  value       = google_container_cluster.neural_engine.master_version
}

output "cluster_location" {
  description = "The location of the GKE cluster"
  value       = google_container_cluster.neural_engine.location
}

# Certificate for kubectl
output "cluster_ca_certificate" {
  description = "The cluster CA certificate"
  value       = google_container_cluster.neural_engine.master_auth[0].cluster_ca_certificate
  sensitive   = true
}

# Node pool information
output "general_pool_id" {
  description = "The ID of the general node pool"
  value       = google_container_node_pool.general.id
}

output "general_pool_instance_group_urls" {
  description = "The instance group URLs of the general node pool"
  value       = google_container_node_pool.general.instance_group_urls
}

output "neural_pool_id" {
  description = "The ID of the neural compute node pool"
  value       = google_container_node_pool.neural_compute.id
}

output "neural_pool_instance_group_urls" {
  description = "The instance group URLs of the neural compute node pool"
  value       = google_container_node_pool.neural_compute.instance_group_urls
}

output "gpu_pool_id" {
  description = "The ID of the GPU node pool (if enabled)"
  value       = var.enable_gpu_pool ? google_container_node_pool.gpu[0].id : null
}

output "gpu_pool_instance_group_urls" {
  description = "The instance group URLs of the GPU node pool (if enabled)"
  value       = var.enable_gpu_pool ? google_container_node_pool.gpu[0].instance_group_urls : []
}

# Workload Identity
output "workload_identity_pool" {
  description = "The workload identity pool for the cluster"
  value       = "${var.project_id}.svc.id.goog"
}

# Service account
output "default_service_account" {
  description = "The default service account used by nodes"
  value       = var.node_service_account_email
}

# Network details
output "cluster_ipv4_cidr" {
  description = "The IP address range of the cluster"
  value       = google_container_cluster.neural_engine.cluster_ipv4_cidr
}

output "services_ipv4_cidr" {
  description = "The IP address range of the services"
  value       = google_container_cluster.neural_engine.services_ipv4_cidr
}
