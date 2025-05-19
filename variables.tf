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
  default     = "landing-zone-vpc"
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
  default     = "landing-zone-cluster"
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