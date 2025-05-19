# Output values from the GCP Landing Zone

output "vpc_id" {
  description = "The ID of the VPC"
  value       = module.networking.vpc_id
}

output "subnet_self_links" {
  description = "The self-links of subnets"
  value       = module.networking.subnet_self_links
}

output "bucket_names" {
  description = "The names of created GCS buckets"
  value       = module.storage.bucket_names
}

output "bucket_urls" {
  description = "The URLs of created GCS buckets"
  value       = module.storage.bucket_urls
}

output "dataproc_cluster_name" {
  description = "The name of the Dataproc cluster"
  value       = module.dataproc.cluster_name
}

output "bigquery_dataset_id" {
  description = "The ID of the BigQuery dataset"
  value       = module.bigquery.dataset_id
}

output "bigquery_tables" {
  description = "The IDs of BigQuery tables"
  value       = module.bigquery.table_ids
}