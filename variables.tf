# Variables for the main module

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The default region for resources"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "The default zone for resources"
  type        = string
  default     = "us-central1-a"
}

variable "network_name" {
  description = "The name of the VPC network"
  type        = string
  default     = "landing-zone-vpc-testing"
}

variable "subnet_names" {
  description = "Names of subnets to create"
  type        = list(string)
  default     = ["database-subnet", "processing-subnet", "storage-subnet"]
}

variable "subnet_cidrs" {
  description = "CIDR ranges for subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "subnet_regions" {
  description = "Regions for subnets"
  type        = list(string)
  default     = ["us-central1", "us-central1", "us-central1"]
}

variable "bucket_names" {
  description = "Names of GCS buckets to create"
  type        = list(string)
  default     = ["landing-zone-data", "landing-zone-processed", "landing-zone-output"]
}

variable "dataproc_cluster_name" {
  description = "Name of the Dataproc cluster"
  type        = string
  default     = "landing-zone-cluster-testing"
}

variable "bq_dataset_id" {
  description = "ID of the BigQuery dataset"
  type        = string
  default     = "landing_zone_dataset"
}

variable "bq_table_ids" {
  description = "IDs of BigQuery tables to create"
  type        = list(string)
  default     = ["raw_data", "processed_data", "final_output"]
}




# ------------------
# IAM Module Variables
# ------------------

variable "custom_role_id" {
  description = "ID of the custom IAM role to create"
  type        = string
  default     = "customComputeViewer"  # You can customize this
}

variable "role_permissions" {
  description = "List of permissions to assign to the custom IAM role"
  type        = list(string)
  default     = [
    "compute.instances.get",
    "compute.instances.list",
    "compute.instances.start",
    "compute.instances.stop"
  ]
}

# ------------------
# VM Module Variables
# ------------------

variable "instance_name" {
  description = "Name of the VM instance"
  type        = string
  default     = "landing-zone-vm-testing"
}

variable "machine_type" {
  description = "Machine type for the VM instance"
  type        = string
  default     = "e2-medium"
}



variable "bucket_configs" {
  type = list(object({
    name                        = string
    location                    = string
    storage_class               = string
    versioning_enabled          = bool
    uniform_bucket_level_access  = bool
    uniform_access              = bool
    public_access_prevention    = string
    encryption                  = optional(object({
      kms_key_name = string
    }))
    lifecycle_rules = optional(list(object({
      action = object({
        type          = string
        storage_class = optional(string)
      })
      condition = object({
        age                        = optional(number)
        created_before             = optional(string)
        with_state                 = optional(string)
        matches_storage_class      = optional(list(string))
        num_newer_versions         = optional(number)
      })
    })))
  }))
}
