# State bucket configuration
# NOTE: The state bucket must be created manually using bootstrap-state-bucket.sh
# before running Terraform. This avoids the chicken-and-egg problem of Terraform
# trying to manage the bucket where it stores its own state.

# Data source to reference the existing state bucket
data "google_storage_bucket" "terraform_state" {
  name = "neurascale-terraform-state"
}

# Ensure GitHub Actions service account has proper access
resource "google_storage_bucket_iam_member" "state_admin" {
  bucket = data.google_storage_bucket.terraform_state.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${var.github_actions_service_account}"
}
