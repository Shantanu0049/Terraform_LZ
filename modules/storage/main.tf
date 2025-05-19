# Storage module - creates GCS buckets

# Create GCS buckets
resource "google_storage_bucket" "buckets" {
  count        = var.num_buckets
  name         = var.bucket_names
  location      = var.region
  force_destroy = true
  project       = var.project_id
  
  
  
  # Use Standard storage class
  storage_class = "STANDARD"
  
  # Enable versioning for data protection
  versioning {
    enabled = true
  }
  
  # Enable uniform bucket-level access
  uniform_bucket_level_access = true

  # Set lifecycle rules (example: delete objects older than 30 days)
  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }
}

# Configure VPC Service Controls for private access
resource "google_access_context_manager_service_perimeter" "storage_perimeter" {
  count          = 0 # Set to 1 if you want to enable VPC Service Controls
  parent         = "accessPolicies/${var.access_policy_id}"
  name           = "accessPolicies/${var.access_policy_id}/servicePerimeters/storage_perimeter"
  perimeter_type = "PERIMETER_TYPE_REGULAR"
  
  title          = "Storage Service Perimeter"
  
  status {
    restricted_services = ["storage.googleapis.com"]
    
    vpc_accessible_services {
      enable_restriction = true
      allowed_services   = ["storage.googleapis.com"]
    }
    
    resources = ["projects/${var.project_number}"]
    
    access_levels = ["accessPolicies/${var.access_policy_id}/accessLevels/storage_access_level"]
  }
}