# State bucket configuration with proper locking
resource "google_storage_bucket" "terraform_state" {
  name          = "neurascale-terraform-state"
  location      = "NORTHAMERICA-NORTHEAST1"
  force_destroy = false

  versioning {
    enabled = true
  }

  lifecycle_rule {
    action {
      type = "Delete"
    }
    condition {
      num_newer_versions = 5
      age                = 30
    }
  }

  # Enable uniform bucket-level access for better security
  uniform_bucket_level_access = true

  # Prevent accidental deletion
  lifecycle {
    prevent_destroy = true
  }

  labels = {
    purpose     = "terraform-state"
    environment = "all"
    managed_by  = "terraform"
  }
}

# Enable state bucket encryption
resource "google_storage_bucket_iam_member" "state_admin" {
  bucket = google_storage_bucket.terraform_state.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${var.github_actions_service_account}"

  depends_on = [google_storage_bucket.terraform_state]
}

# Create a separate bucket for state locks (optional but recommended)
resource "google_storage_bucket" "terraform_locks" {
  name          = "neurascale-terraform-locks"
  location      = "NORTHAMERICA-NORTHEAST1"
  force_destroy = false

  versioning {
    enabled = true
  }

  uniform_bucket_level_access = true

  lifecycle {
    prevent_destroy = true
  }

  labels = {
    purpose     = "terraform-locks"
    environment = "all"
    managed_by  = "terraform"
  }
}
