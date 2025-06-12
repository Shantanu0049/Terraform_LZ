resource "google_storage_bucket" "buckets" {
  count                      = length(var.buckets)
  name                       = var.buckets[count.index].name
  location                   = var.buckets[count.index].location
  storage_class              = var.buckets[count.index].storage_class
  uniform_bucket_level_access = var.buckets[count.index].uniform_access
  force_destroy = true

  versioning {
    enabled = var.buckets[count.index].versioning_enabled
  }

  public_access_prevention = var.buckets[count.index].public_access_prevention

  dynamic "encryption" {
    for_each = var.buckets[count.index].encryption != null ? [1] : []
    content {
      default_kms_key_name = var.buckets[count.index].encryption.kms_key_name
    }
  }

  dynamic "lifecycle_rule" {
    for_each = var.buckets[count.index].lifecycle_rules != null ? var.buckets[count.index].lifecycle_rules : []
    content {
      action {
        type          = lifecycle_rule.value.action.type
        storage_class = lookup(lifecycle_rule.value.action, "storage_class", null)
      }
      condition {
        age                   = lookup(lifecycle_rule.value.condition, "age", null)
        created_before        = lookup(lifecycle_rule.value.condition, "created_before", null)
        with_state            = lookup(lifecycle_rule.value.condition, "with_state", null)
        matches_storage_class = lookup(lifecycle_rule.value.condition, "matches_storage_class", null)
        num_newer_versions    = lookup(lifecycle_rule.value.condition, "num_newer_versions", null)
      }
    }
  }

  depends_on = [google_storage_bucket.buckets]
}
