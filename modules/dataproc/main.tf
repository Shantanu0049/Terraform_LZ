# Dataproc module - creates Dataproc clusters

# Create a Dataproc cluster
resource "google_dataproc_cluster" "cluster" {
  name     = var.cluster_name
  region   = var.region
  project  = var.project_id
  
  # Associate with the proper subnet
  cluster_config {
    staging_bucket = var.bucket_name
    
    # Set up network configuration
    gce_cluster_config {
      subnetwork = var.subnet_self_link
      internal_ip_only = true
      
      # Optional: Specify service account
      # service_account = var.service_account_email
      # service_account_scopes = ["cloud-platform"]
    }
    
    # Master node configuration
    master_config {
      num_instances = 1
      machine_type  = "n1-standard-1"  # Changed from n1-standard-4
      disk_config {
        boot_disk_type    = "pd-ssd"
        boot_disk_size_gb = 50
      }
    }
    
    # Worker node configuration
    worker_config {
      num_instances = 2
      machine_type  = "n1-standard-1"  # Changed from n1-standard-4
      disk_config {
        boot_disk_type    = "pd-standard"
        boot_disk_size_gb = 100
        num_local_ssds    = 0
      }
    }
    
    # Software configuration
    software_config {
      image_version = "1.5-debian10"
      optional_components = ["ANACONDA","JUPYTER"]
      
      # Optional: Set properties
      override_properties = {
        "dataproc:dataproc.allow.zero.workers" = "false"
      }
    }
  }
}