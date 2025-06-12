variable "project_id" {
  type = string
}

variable "region" {
  type = string
}

variable "buckets" {
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

variable "subnet_self_link" {
  type = string
}
