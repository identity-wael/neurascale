# Outputs for Networking Module

output "vpc_id" {
  description = "The ID of the VPC"
  value       = google_compute_network.vpc.id
}

output "vpc_name" {
  description = "The name of the VPC"
  value       = google_compute_network.vpc.name
}

output "vpc_self_link" {
  description = "The self link of the VPC"
  value       = google_compute_network.vpc.self_link
}

# Subnet outputs
output "gke_subnet_id" {
  description = "The ID of the GKE subnet"
  value       = google_compute_subnetwork.gke.id
}

output "gke_subnet_name" {
  description = "The name of the GKE subnet"
  value       = google_compute_subnetwork.gke.name
}

output "gke_subnet_cidr" {
  description = "The CIDR range of the GKE subnet"
  value       = google_compute_subnetwork.gke.ip_cidr_range
}

output "private_subnet_id" {
  description = "The ID of the private subnet"
  value       = google_compute_subnetwork.private.id
}

output "private_subnet_name" {
  description = "The name of the private subnet"
  value       = google_compute_subnetwork.private.name
}

output "private_subnet_cidr" {
  description = "The CIDR range of the private subnet"
  value       = google_compute_subnetwork.private.ip_cidr_range
}

# Secondary ranges for GKE
output "pods_secondary_range_name" {
  description = "The name of the pods secondary range"
  value       = google_compute_subnetwork.gke.secondary_ip_range[0].range_name
}

output "services_secondary_range_name" {
  description = "The name of the services secondary range"
  value       = google_compute_subnetwork.gke.secondary_ip_range[1].range_name
}

# Router and NAT
output "router_id" {
  description = "The ID of the Cloud Router"
  value       = google_compute_router.router.id
}

output "nat_id" {
  description = "The ID of the Cloud NAT"
  value       = google_compute_router_nat.nat.id
}

# Private Service Connection
output "private_service_connection_id" {
  description = "The ID of the private service connection"
  value       = google_service_networking_connection.private_service_connection.id
}

output "private_service_connection_ip" {
  description = "The IP address range of the private service connection"
  value       = google_compute_global_address.private_service_connection.address
}

# DNS zone (if created)
output "private_dns_zone_id" {
  description = "The ID of the private DNS zone for Google APIs"
  value       = var.create_private_dns_zone ? google_dns_managed_zone.private_google_apis[0].id : null
}

output "private_dns_zone_name" {
  description = "The name of the private DNS zone for Google APIs"
  value       = var.create_private_dns_zone ? google_dns_managed_zone.private_google_apis[0].name : null
}
