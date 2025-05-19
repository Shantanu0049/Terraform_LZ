# Outputs for the BigQuery module

output "dataset_id" {
  description = "The ID of the created BigQuery dataset"
  value       = google_bigquery_dataset.dataset.dataset_id
}

output "dataset_self_link" {
  description = "The self link of the created BigQuery dataset"
  value       = google_bigquery_dataset.dataset.self_link
}

output "table_ids" {
  description = "The IDs of created BigQuery tables"
  value       = google_bigquery_table.tables[*].table_id
}

output "table_self_links" {
  description = "The self links of created BigQuery tables"
  value       = google_bigquery_table.tables[*].self_link
}