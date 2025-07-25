# Enable required APIs for a project
variable "project_id" {
  type        = string
  description = "Project ID to enable APIs for"
}

variable "apis" {
  type        = list(string)
  description = "List of APIs to enable"
  default = [
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
    "eventarc.googleapis.com",       # For Cloud Function triggers
    "cloudscheduler.googleapis.com", # For scheduled functions
    "secretmanager.googleapis.com",  # For secure credential storage
    "billingbudgets.googleapis.com", # For budget alerts
    "bigquery.googleapis.com",       # For cost export dataset
  ]
}

resource "google_project_service" "apis" {
  for_each = toset(var.apis)

  project = var.project_id
  service = each.value

  disable_on_destroy = false
}

# Add a time delay to ensure APIs are fully enabled
resource "time_sleep" "wait_for_apis" {
  depends_on = [google_project_service.apis]

  create_duration = "30s"
}
