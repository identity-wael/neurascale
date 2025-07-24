terraform {
  required_version = ">= 1.5.0"

  backend "gcs" {
    bucket = "neurascale-terraform-state"
    prefix = "neural-engine"
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
}

# Determine environment from project_id
locals {
  environment = endswith(var.project_id, "-neurascale") ? split("-", var.project_id)[0] : "development"
}

# Provider for the target environment
provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Provider for orchestration project (for cross-project resources)
provider "google" {
  alias   = "orchestration"
  project = var.orchestration_project_id
  region  = var.region
}

# Enable APIs for the target environment
module "project_apis" {
  source     = "./modules/project-apis"
  project_id = var.project_id
}

# Neural ingestion infrastructure for the target environment
module "neural_ingestion" {
  source = "./modules/neural-ingestion"

  project_id  = var.project_id
  environment = local.environment
  region      = var.region

  depends_on = [module.project_apis]
}

# IAM permissions for CI/CD in the target environment
resource "google_project_iam_member" "ci_cd_permissions" {
  project = var.project_id
  role    = "roles/owner" # Adjust as needed
  member  = "serviceAccount:${var.ci_cd_service_account}"
}
