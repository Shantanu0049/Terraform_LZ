variable "project_id" {
  description = "The ID of the project in which to create the VM"
  type        = string
}

variable "zone" {
  description = "The zone to deploy the VM instance in"
  type        = string
}

variable "instance_name" {
  description = "Name of the VM instance"
  type        = string
}

variable "machine_type" {
  description = "The machine type to use for the VM"
  type        = string
}

variable "service_account_email" {
  description = "The service account email to attach to the VM"
  type        = string
  default = "shantanu.gundge@atgeirsolutions.com"
}

variable "subnet" {
  description = "The self-link of the subnet for the VM"
  type        = string
}
