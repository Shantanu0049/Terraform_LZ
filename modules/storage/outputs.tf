# Outputs for the storage module

output "bucket_names" {
  description = "The names of created GCS buckets"
  value       = google_storage_bucket.buckets[*].name
}

output "bucket_urls" {
  description = "The URLs of created GCS buckets"
  value       = [for b in google_storage_bucket.buckets : "gs://${b.name}"]
}

output "bucket_self_links" {
  description = "The self-links of created GCS buckets"
  value       = google_storage_bucket.buckets[*].self_link
}