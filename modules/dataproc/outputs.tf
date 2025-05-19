# Outputs for the Dataproc module

output "cluster_name" {
  description = "The name of the created Dataproc cluster"
  value       = google_dataproc_cluster.cluster.name
}

# output "cluster_self_link" {
#   description = "The self link of the created Dataproc cluster"
#   value       = google_dataproc_cluster.cluster.self_link
# }

output "master_instance_names" {
  description = "The list of master instance names"
  value       = google_dataproc_cluster.cluster.cluster_config[0].master_config[0].instance_names
}

output "worker_instance_names" {
  description = "The list of worker instance names"
  value       = google_dataproc_cluster.cluster.cluster_config[0].worker_config[0].instance_names
}