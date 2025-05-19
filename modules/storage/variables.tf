# Variables for the storage module

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The region for buckets"
  type        = string
}

variable "bucket_names" {
  description = "Names of buckets to create"
  type        = list(string)
}

variable "subnet_self_link" {
  description = "The self link of the subnet where the storage service is"
  type        = string
}

variable "project_number" {
  description = "The numeric ID of the GCP project"
  type        = string
  default     = "12345678" 
}

variable "access_policy_id" {
  description = "The ID of the access policy for VPC Service Controls"
  type        = string
  default     = "0" 
} 

variable "num_buckets" {
  description = "Number of GCS buckets to create"
  type        = number
  default     = 1
}

variable "bucket_name_pre" {
  description = "Base name for the GCS buckets"
  type        = string
  default     = "atg_sol"
}

