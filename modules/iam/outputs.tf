# Outputs for the IAM module

output "storage_service_account_email" {
  description = "The email of the storage service account"
  value       = google_service_account.storage_account.email
}

output "dataproc_service_account_email" {
  description = "The email of the Dataproc service account"
  value       = google_service_account.dataproc_account.email
}

output "bigquery_service_account_email" {
  description = "The email of the BigQuery service account"
  value       = google_service_account.bigquery_account.email
}