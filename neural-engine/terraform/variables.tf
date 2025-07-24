variable "orchestration_project_id" {
  type        = string
  description = "The main orchestration project ID"
  default     = "neurascale"
}


variable "region" {
  type        = string
  description = "Google Cloud region"
  default     = "northamerica-northeast1"
}

variable "ci_cd_service_account" {
  type        = string
  description = "Service account email for CI/CD"
  default     = "github-actions@neurascale.iam.gserviceaccount.com"
}

variable "project_id" {
  type        = string
  description = "Target project ID for deployment (dynamically set based on environment)"
}
