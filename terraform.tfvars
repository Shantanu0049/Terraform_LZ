project_id             = "terraform-458410"
region                 = "us-central1"
network_name           = "landing-zone-vpc-testing1"
subnet_names           = ["database-subnet1", "processing-subnet1", "storage-subnet1"]
subnet_cidrs           = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
subnet_regions         = ["us-central1", "us-central1", "us-central1"]
custom_role_id         = "testing006543"
role_permissions       = ["storage.objects.list", "storage.buckets.get"]
bucket_configs = [
{
      name                      = "atgeir-testing004555555555"
      location                  = "us-central1"
      storage_class             = "STANDARD"
      versioning_enabled        = false
      uniform_bucket_level_access = false
      public_access_prevention     = "enforced"
      uniform_access               = false
      force_destroy                = true
    }
]
dataproc_cluster_name  = "landing-zone-cluster-testing1"
bq_dataset_id          = "landing_zone_dataset_testing1"
bq_table_ids           = ["raw_data1", "processed_data1", "final_output1"]
