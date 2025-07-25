# GitHub Actions Service Account Permissions
# This file contains the minimal permissions needed for GitHub Actions to deploy infrastructure
#
# NOTE: The GitHub Actions service account (github-actions@neurascale.iam.gserviceaccount.com)
# needs to be granted these permissions in each target project (staging-neurascale, production-neurascale)
# by someone with Project IAM Admin permissions.
#
# Run these commands manually if Terraform cannot apply them:
#
# For staging:
# gcloud projects add-iam-policy-binding staging-neurascale \
#   --member="serviceAccount:github-actions@neurascale.iam.gserviceaccount.com" \
#   --role="roles/editor"
#
# For production:
# gcloud projects add-iam-policy-binding production-neurascale \
#   --member="serviceAccount:github-actions@neurascale.iam.gserviceaccount.com" \
#   --role="roles/editor"

# Temporary: Use Editor role until custom role can be created
# This grants sufficient permissions for deployment
resource "google_project_iam_member" "github_actions_editor" {
  count   = var.environment == "staging" ? 1 : 0 # Only apply in staging for now
  project = var.project_id
  role    = "roles/editor"
  member  = "serviceAccount:${var.github_actions_service_account}"
}
