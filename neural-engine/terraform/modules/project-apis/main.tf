# Enable required APIs for a project
variable "project_id" {
  type        = string
  description = "Project ID to enable APIs for"
}

# List of APIs to enable
locals {
  apis = [
    "compute.googleapis.com",
    "storage-api.googleapis.com",
    "storage-component.googleapis.com",
    "pubsub.googleapis.com",
    "bigtable.googleapis.com",
    "bigtableadmin.googleapis.com",
    "cloudfunctions.googleapis.com",
    "cloudbuild.googleapis.com",
    "artifactregistry.googleapis.com",
    "run.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "cloudtrace.googleapis.com",
    "iam.googleapis.com",
    "iamcredentials.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "serviceusage.googleapis.com",
  ]
}

resource "google_project_service" "apis" {
  for_each = toset(local.apis)

  project = var.project_id
  service = each.value

  disable_on_destroy = false
}
