project_id             = "terraform-458410"
region                 = "us-central1"
network_name           = "landing-zone-vpc1"
subnet_names           = ["database-subnet", "processing-subnet", "storage-subnet"]
subnet_cidrs           = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
subnet_regions         = ["us-central1", "us-central1", "us-central1"]
custom_role_id         = "wsd"
role_permissions       = ["storage.objects.get"]
bucket_configs = [
{
      name                      = "okijhgfthmcry"
      location                  = "us-central1"
      storage_class             = "ARCHIVE"
      versioning_enabled        = false
      uniform_bucket_level_access = false
      public_access_prevention     = "enforced"
      uniform_access               = false
      force_destroy                = true
    }
]
dataproc_cluster_name  = "landing-zone-cluster1"
bq_dataset_id          = "landing_zone_dataset1"
bq_table_ids           = ["raw_data", "processed_data", "final_output"]
