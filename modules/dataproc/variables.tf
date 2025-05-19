# Variables for the Dataproc module

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The region for the Dataproc cluster"
  type        = string
}

variable "cluster_name" {
  description = "The name of the Dataproc cluster"
  type        = string
}

variable "subnet_self_link" {
  description = "The self link of the subnet where Dataproc will be deployed"
  type        = string
}

variable "bucket_name" {
  description = "The name of the GCS bucket for Dataproc staging"
  type        = string
}

variable "service_account_email" {
  description = "The service account email for Dataproc"
  type        = string
  default     = ""
}