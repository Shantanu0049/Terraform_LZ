# IAM module - sets up IAM roles and permissions

# Service account for GCS operations
resource "google_service_account" "storage_account" {
  account_id   = "storage-sa"
  display_name = "Storage Service Account"
  project      = var.project_id
}

# Service account for Dataproc operations
resource "google_service_account" "dataproc_account" {
  account_id   = "dataproc-sa"
  display_name = "Dataproc Service Account"
  project      = var.project_id
}

# Service account for BigQuery operations
resource "google_service_account" "bigquery_account" {
  account_id   = "bigquery-sa"
  display_name = "BigQuery Service Account"
  project      = var.project_id
}

# IAM role bindings for Storage Service Account
resource "google_project_iam_member" "storage_roles" {
  for_each = toset([
    "roles/storage.admin",
    "roles/storage.objectAdmin"
  ])
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.storage_account.email}"
}

# IAM role bindings for Dataproc Service Account
resource "google_project_iam_member" "dataproc_roles" {
  for_each = toset([
    "roles/dataproc.worker",
    "roles/dataproc.editor",
    "roles/storage.objectViewer"
  ])
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.dataproc_account.email}"
}

# IAM role bindings for BigQuery Service Account
resource "google_project_iam_member" "bigquery_roles" {
  for_each = toset([
    "roles/bigquery.dataEditor",
    "roles/bigquery.jobUser",
    "roles/bigquery.dataViewer"
  ])
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.bigquery_account.email}"
}

# Allow Dataproc to access Storage
resource "google_project_iam_binding" "dataproc_storage_access" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  members = [
    "serviceAccount:${google_service_account.dataproc_account.email}"
  ]
}

# Allow Dataproc to access BigQuery
resource "google_project_iam_binding" "dataproc_bigquery_access" {
  project = var.project_id
  role    = "roles/bigquery.dataViewer"
  members = [
    "serviceAccount:${google_service_account.dataproc_account.email}"
  ]
}