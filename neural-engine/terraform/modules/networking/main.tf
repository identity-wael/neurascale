# Networking Module for NeuraScale Neural Engine
# Creates VPC, subnets, firewall rules, and networking components

# VPC Network
resource "google_compute_network" "vpc" {
  name                            = "${var.environment}-neural-vpc"
  auto_create_subnetworks         = false
  routing_mode                    = "REGIONAL"
  delete_default_routes_on_create = false
  mtu                             = 1460

  description = "VPC network for ${var.environment} Neural Engine infrastructure"
}

# Private subnet for GKE cluster
resource "google_compute_subnetwork" "gke" {
  name                     = "${var.environment}-gke-subnet"
  ip_cidr_range            = var.gke_subnet_cidr
  network                  = google_compute_network.vpc.id
  region                   = var.region
  private_ip_google_access = true

  # Secondary ranges for pods and services
  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = var.pods_cidr
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = var.services_cidr
  }

  # Enable VPC flow logs for security monitoring
  log_config {
    aggregation_interval = "INTERVAL_5_SEC"
    flow_sampling        = 0.5
    metadata             = "INCLUDE_ALL_METADATA"
  }

  description = "Subnet for GKE cluster nodes in ${var.environment}"
}

# Private subnet for databases and internal services
resource "google_compute_subnetwork" "private" {
  name                     = "${var.environment}-private-subnet"
  ip_cidr_range            = var.private_subnet_cidr
  network                  = google_compute_network.vpc.id
  region                   = var.region
  private_ip_google_access = true

  description = "Private subnet for databases and internal services in ${var.environment}"
}

# Cloud Router for NAT
resource "google_compute_router" "router" {
  name    = "${var.environment}-router"
  network = google_compute_network.vpc.id
  region  = var.region

  bgp {
    asn = 64514
  }
}

# Cloud NAT for outbound connectivity
resource "google_compute_router_nat" "nat" {
  name                               = "${var.environment}-nat"
  router                             = google_compute_router.router.name
  region                             = google_compute_router.router.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# Reserve IP range for Private Service Connection (Cloud SQL)
resource "google_compute_global_address" "private_service_connection" {
  count = var.enable_private_service_connection ? 1 : 0

  name          = "${var.environment}-private-service-connection"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.vpc.id
}

# Create Private Service Connection
resource "google_service_networking_connection" "private_service_connection" {
  count = var.enable_private_service_connection ? 1 : 0

  network                 = google_compute_network.vpc.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_service_connection[0].name]
}

# Firewall Rules

# Allow internal communication within VPC
resource "google_compute_firewall" "allow_internal" {
  name    = "${var.environment}-allow-internal"
  network = google_compute_network.vpc.name

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "udp"
    ports    = ["0-65535"]
  }

  allow {
    protocol = "icmp"
  }

  source_ranges = [
    var.gke_subnet_cidr,
    var.private_subnet_cidr,
    var.pods_cidr,
    var.services_cidr
  ]

  priority = 1000

  log_config {
    metadata = "INCLUDE_ALL_METADATA"
  }
}

# Allow health checks from Google Load Balancers
resource "google_compute_firewall" "allow_health_checks" {
  name    = "${var.environment}-allow-health-checks"
  network = google_compute_network.vpc.name

  allow {
    protocol = "tcp"
    ports    = ["80", "443", "8080"]
  }

  # Google health check source ranges
  source_ranges = [
    "35.191.0.0/16",
    "130.211.0.0/22"
  ]

  target_tags = ["allow-health-checks"]
  priority    = 900
}

# Allow SSH from IAP (Identity-Aware Proxy) for secure access
resource "google_compute_firewall" "allow_iap_ssh" {
  name    = "${var.environment}-allow-iap-ssh"
  network = google_compute_network.vpc.name

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  # IAP source range
  source_ranges = ["35.235.240.0/20"]
  target_tags   = ["allow-iap-ssh"]
  priority      = 800
}

# Deny all egress by default (for high security environments)
resource "google_compute_firewall" "deny_all_egress" {
  count = var.enable_restrictive_egress ? 1 : 0

  name      = "${var.environment}-deny-all-egress"
  network   = google_compute_network.vpc.name
  direction = "EGRESS"

  deny {
    protocol = "all"
  }

  destination_ranges = ["0.0.0.0/0"]
  priority           = 65534

  log_config {
    metadata = "INCLUDE_ALL_METADATA"
  }
}

# Allow specific egress for required services
resource "google_compute_firewall" "allow_required_egress" {
  count = var.enable_restrictive_egress ? 1 : 0

  name      = "${var.environment}-allow-required-egress"
  network   = google_compute_network.vpc.name
  direction = "EGRESS"

  allow {
    protocol = "tcp"
    ports    = ["443", "80"]
  }

  # Allow access to Google APIs and services
  destination_ranges = [
    "199.36.153.8/30", # restricted.googleapis.com
    "199.36.153.4/30", # private.googleapis.com
  ]

  priority = 1000
}

# DNS configuration for Private Google Access
resource "google_dns_managed_zone" "private_google_apis" {
  count = var.create_private_dns_zone ? 1 : 0

  name        = "${var.environment}-googleapis"
  dns_name    = "googleapis.com."
  description = "Private DNS zone for Google APIs"

  visibility = "private"

  private_visibility_config {
    networks {
      network_url = google_compute_network.vpc.id
    }
  }
}

resource "google_dns_record_set" "restricted_googleapis" {
  count = var.create_private_dns_zone ? 1 : 0

  name         = "restricted.googleapis.com."
  managed_zone = google_dns_managed_zone.private_google_apis[0].name
  type         = "A"
  ttl          = 300

  rrdatas = [
    "199.36.153.8",
    "199.36.153.9",
    "199.36.153.10",
    "199.36.153.11"
  ]
}

resource "google_dns_record_set" "private_googleapis" {
  count = var.create_private_dns_zone ? 1 : 0

  name         = "private.googleapis.com."
  managed_zone = google_dns_managed_zone.private_google_apis[0].name
  type         = "A"
  ttl          = 300

  rrdatas = [
    "199.36.153.4",
    "199.36.153.5",
    "199.36.153.6",
    "199.36.153.7"
  ]
}
