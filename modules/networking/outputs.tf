# Outputs for the networking module

output "vpc_id" {
  description = "The ID of the VPC"
  value       = google_compute_network.vpc.id
}

output "vpc_name" {
  description = "The name of the VPC"
  value       = google_compute_network.vpc.name
}

output "subnet_names" {
  description = "The names of subnets"
  value       = google_compute_subnetwork.subnets[*].name
}

# output "subnet_self_links" {
#   description = "The self-links of subnets"
#   value       = google_compute_subnetwork.subnets[*].self_link
# }

output "subnet_regions" {
  description = "The regions of subnets"
  value       = google_compute_subnetwork.subnets[*].region
}

output "subnet_cidrs" {
  description = "The CIDR ranges of subnets"
  value       = google_compute_subnetwork.subnets[*].ip_cidr_range
}

output "subnet_self_links" {
  value = [for s in google_compute_subnetwork.subnets : s.self_link]
}
