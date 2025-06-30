resource "google_compute_instance" "default" {
  name         = var.instance_name
  machine_type = var.machine_type
  zone         = var.zone
  project      = var.project_id

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
    }
  }

  network_interface {
    subnetwork = var.subnet

    access_config {}
  }

  service_account {
    email  = var.service_account_email
    scopes = ["cloud-platform"]
  }

  tags = ["vm"]

   # Prevent accidental deletion
  lifecycle {
    prevent_destroy = true
    # Ensures new instance is created before destroying the old one (best-effort)
    create_before_destroy = true
    # Optional: ignore external metadata changes like SSH keys
    ignore_changes = [metadata["ssh-keys"], tags]
  }
}
