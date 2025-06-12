# BigQuery module - creates datasets and tables

# Create a BigQuery dataset
resource "google_bigquery_dataset" "dataset" {
  dataset_id                  = var.dataset_id
  friendly_name               = "Landing Zone Dataset"
  description                 = "Dataset for the GCP landing zone data"
  location                    = var.region
  project                     = var.project_id
  default_table_expiration_ms = 3600000 * 24 * 90 # 90 days
  
  # Access control
  access {
    role          = "OWNER"
    special_group = "projectOwners"
  }
  
  access {
    role          = "READER"
    special_group = "projectReaders"
  }
  
  access {
    role          = "WRITER"
    special_group = "projectWriters"
  }
  
  # Optional: Add labels
  labels = {
    environment = "landing-zone"
  }
}

# Create BigQuery tables
resource "google_bigquery_table" "tables" {
  count      = length(var.table_ids)
  dataset_id = google_bigquery_dataset.dataset.dataset_id
  table_id   = var.table_ids[count.index]
  project    = var.project_id
  deletion_protection = false

  
  # Define schema for each table
  schema = <<EOF
[
  {
    "name": "id",
    "type": "STRING",
    "mode": "REQUIRED",
    "description": "Unique identifier"
  },
  {
    "name": "created_timestamp",
    "type": "TIMESTAMP",
    "mode": "REQUIRED",
    "description": "Record creation timestamp"
  },
  {
    "name": "data",
    "type": "STRING",
    "mode": "NULLABLE",
    "description": "Data content"
  }
]
EOF
  
  # Optional: Set time partitioning
  time_partitioning {
    type  = "DAY"
    field = "created_timestamp"
  }
  
  # Optional: Add clustering
  clustering = ["id"]
  
  # Optional: Add description
  description = "Table ${var.table_ids[count.index]} for landing zone data"
  
  # Optional: Set labels
  labels = {
    environment = "landing-zone"
  }
}

# Optional: Create a BigQuery connection to VPC
resource "google_bigquery_connection" "connection" {
  count           = 0 # Set to 1 if you want to create a VPC connection
  connection_id   = "landing-zone-connection"
  friendly_name   = "Landing Zone VPC Connection"
  description     = "VPC connection for BigQuery to access private resources"
  project         = var.project_id
  location        = var.region
  
  cloud_resource {
    service_account_id = "bigquery-sa@${var.project_id}.iam.gserviceaccount.com"
  }
}