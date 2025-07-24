# Configuration for backing up Terraform state to GCS
# This is separate from the main configuration to avoid circular dependencies

resource "google_storage_bucket_object" "terraform_state_backup" {
  for_each = toset(["development", "staging", "production"])

  name   = "backup/${each.key}/terraform.tfstate"
  bucket = "neurascale-terraform-state"
  source = "${path.module}/.terraform/terraform.tfstate"

  lifecycle {
    ignore_changes = [content, source]
  }
}

# Note: This requires running a script to periodically sync state from Terraform Cloud
# See scripts/sync-terraform-state.sh
