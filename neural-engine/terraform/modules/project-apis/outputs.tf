# Output to ensure proper dependency chain
output "apis_enabled" {
  value       = true
  description = "Indicates that all APIs have been enabled"
  depends_on  = [time_sleep.wait_for_apis]
}
