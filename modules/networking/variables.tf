# Variables for the networking module

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The default region for resources"
  type        = string
}

variable "network_name" {
  description = "The name of the VPC network"
  type        = string
}

variable "subnet_names" {
  description = "Names of subnets to create"
  type        = list(string)
}

variable "subnet_cidrs" {
  description = "CIDR ranges for subnets"
  type        = list(string)
}

variable "subnet_regions" {
  description = "Regions for subnets"
  type        = list(string)
}