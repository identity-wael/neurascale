# Cross-Project IAM Setup for GitHub Actions
# This Terraform configuration grants the GitHub Actions service account
# permissions to deploy resources in all environment projects

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

# Variables
variable "github_actions_sa" {
  description = "GitHub Actions service account email"
  default     = "github-actions@neurascale.iam.gserviceaccount.com"
}

variable "target_projects" {
  description = "List of target projects to grant permissions"
  type        = list(string)
  default     = ["staging-neurascale", "production-neurascale", "development-neurascale"]
}

# Enable required APIs in each project
resource "google_project_service" "required_apis" {
  for_each = {
    for pair in setproduct(var.target_projects, [
      "iam.googleapis.com",
      "cloudresourcemanager.googleapis.com",
      "billingbudgets.googleapis.com",
      "bigquery.googleapis.com",
      "artifactregistry.googleapis.com"
    ]) : "${pair[0]}-${pair[1]}" => {
      project = pair[0]
      service = pair[1]
    }
  }

  project = each.value.project
  service = each.value.service

  disable_on_destroy = false
}

# Grant Editor role to GitHub Actions service account in each project
# This provides broad permissions needed for infrastructure deployment
resource "google_project_iam_member" "github_actions_editor" {
  for_each = toset(var.target_projects)

  project = each.value
  role    = "roles/editor"
  member  = "serviceAccount:${var.github_actions_sa}"

  depends_on = [google_project_service.required_apis]
}

# Additional specific roles for better security practices
resource "google_project_iam_member" "github_actions_roles" {
  for_each = {
    for pair in setproduct(var.target_projects, [
      "roles/iam.serviceAccountAdmin",
      "roles/iam.roleAdmin",
      "roles/resourcemanager.projectIamAdmin",
      "roles/billing.costsManager",
      "roles/monitoring.admin",
      "roles/logging.admin",
      "roles/artifactregistry.admin"
    ]) : "${pair[0]}-${pair[1]}" => {
      project = pair[0]
      role    = pair[1]
    }
  }

  project = each.value.project
  role    = each.value.role
  member  = "serviceAccount:${var.github_actions_sa}"

  depends_on = [google_project_service.required_apis]
}

# Output the permissions granted
output "permissions_granted" {
  value = {
    service_account = var.github_actions_sa
    projects        = var.target_projects
    roles = [
      "roles/editor",
      "roles/iam.serviceAccountAdmin",
      "roles/iam.roleAdmin",
      "roles/resourcemanager.projectIamAdmin",
      "roles/billing.costsManager",
      "roles/monitoring.admin",
      "roles/logging.admin",
      "roles/artifactregistry.admin"
    ]
  }
}
