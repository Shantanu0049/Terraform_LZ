# Auto-generated Terraform configuration for selected GCP services

module "networking" {
  source         = "./modules/networking"
  project_id     = var.project_id
  region         = var.region
  network_name   = var.network_name
  subnet_names   = var.subnet_names
  subnet_cidrs   = var.subnet_cidrs
  subnet_regions = var.subnet_regions
}
module "iam" {
  source     = "./modules/iam"
  project_id = var.project_id
  depends_on = [module.networking]
}
module "storage" {
  source           = "./modules/storage"
  project_id       = var.project_id
  region           = var.region
  bucket_names     = var.bucket_names
  subnet_self_link = module.networking.subnet_self_links[2]
  depends_on       = [module.networking, module.iam]
}
module "dataproc" {
  source           = "./modules/dataproc"
  project_id       = var.project_id
  region           = var.region
  cluster_name     = var.dataproc_cluster_name
  subnet_self_link = module.networking.subnet_self_links[1]
  bucket_name      = module.storage.bucket_names[0]
  depends_on       = [module.networking, module.iam, module.storage]
}
module "bigquery" {
  source           = "./modules/bigquery"
  project_id       = var.project_id
  region           = var.region
  dataset_id       = var.bq_dataset_id
  table_ids        = var.bq_table_ids
  subnet_self_link = module.networking.subnet_self_links[0]
  depends_on       = [module.networking, module.iam]
}
