terraform {
  required_version = ">= 1.5.0"

  cloud {
    hostname     = "app.terraform.io"
    organization = "neurascale"

    workspaces {
      tags = ["neural-engine"]
    }
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

# Provider for the orchestration project
provider "google" {
  project = var.orchestration_project_id
  region  = var.region
}

provider "google-beta" {
  project = var.orchestration_project_id
  region  = var.region
}

# Provider aliases for each environment
provider "google" {
  alias   = "production"
  project = var.production_project_id
  region  = var.region
}

provider "google" {
  alias   = "staging"
  project = var.staging_project_id
  region  = var.region
}

provider "google" {
  alias   = "development"
  project = var.development_project_id
  region  = var.region
}

# Enable APIs for each environment
module "production_apis" {
  source = "./modules/project-apis"
  providers = {
    google = google.production
  }
  project_id = var.production_project_id
}

module "staging_apis" {
  source = "./modules/project-apis"
  providers = {
    google = google.staging
  }
  project_id = var.staging_project_id
}

module "development_apis" {
  source = "./modules/project-apis"
  providers = {
    google = google.development
  }
  project_id = var.development_project_id
}

# Neural ingestion infrastructure for each environment
module "production_ingestion" {
  source = "./modules/neural-ingestion"
  providers = {
    google = google.production
  }

  project_id  = var.production_project_id
  environment = "production"
  region      = var.region

  depends_on = [module.production_apis]
}

module "staging_ingestion" {
  source = "./modules/neural-ingestion"
  providers = {
    google = google.staging
  }

  project_id  = var.staging_project_id
  environment = "staging"
  region      = var.region

  depends_on = [module.staging_apis]
}

module "development_ingestion" {
  source = "./modules/neural-ingestion"
  providers = {
    google = google.development
  }

  project_id  = var.development_project_id
  environment = "development"
  region      = var.region

  depends_on = [module.development_apis]
}

# Cross-project IAM permissions for CI/CD
resource "google_project_iam_member" "ci_cd_permissions" {
  for_each = {
    production  = var.production_project_id
    staging     = var.staging_project_id
    development = var.development_project_id
  }

  project = each.value
  role    = "roles/owner" # Adjust as needed
  member  = "serviceAccount:${var.ci_cd_service_account}"
}
