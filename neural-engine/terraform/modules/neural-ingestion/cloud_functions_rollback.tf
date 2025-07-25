# Cloud Functions Rollback Mechanism

# Store the current function version for rollback
resource "google_storage_bucket_object" "function_version_backup" {
  for_each = var.enable_cloud_functions ? local.function_types : toset([])

  name   = "functions/backups/${each.key}-previous.zip"
  bucket = google_storage_bucket.functions.name
  source = google_storage_bucket_object.function_source[each.key].name

  lifecycle {
    ignore_changes = [source]
  }
}

# Output rollback commands
output "rollback_commands" {
  value = var.enable_cloud_functions ? {
    for k, v in google_cloudfunctions2_function.process_neural_stream :
    k => "gcloud functions deploy ${v.name} --source=gs://${google_storage_bucket.functions.name}/functions/backups/${k}-previous.zip --region=${var.region}"
  } : {}
  description = "Commands to rollback each function to previous version"
}
