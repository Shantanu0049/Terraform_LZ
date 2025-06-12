output "vm_instance_name" {
  description = "The name of the created VM instance"
  value       = google_compute_instance.default.name
}

output "vm_instance_self_link" {
  description = "The self link of the created VM"
  value       = google_compute_instance.default.self_link
}

output "vm_instance_network_interface" {
  description = "The network interface of the VM"
  value       = google_compute_instance.default.network_interface
}
