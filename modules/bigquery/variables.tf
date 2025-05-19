# Variables for the BigQuery module

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The region for the BigQuery dataset"
  type        = string
}

variable "dataset_id" {
  description = "The ID of the BigQuery dataset"
  type        = string
}

variable "table_ids" {
  description = "The IDs of BigQuery tables to create"
  type        = list(string)
}

variable "subnet_self_link" {
  description = "The self link of the subnet where BigQuery will be accessed from"
  type        = string
}