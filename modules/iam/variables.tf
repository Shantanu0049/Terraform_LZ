# Variables for the IAM module

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "custom_role_id" {}
variable "role_permissions" {
  type = list(string)
}

variable "account_id" {
  description = "Service account ID"
  type        = string
}
