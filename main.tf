# Auto-generated Terraform configuration

module "vm" {
  source                   = "./modules/vm"
  project_id               = var.project_id
  zone                     = var.zone
  instance_name            = var.instance_name
  machine_type             = var.machine_type
  service_account_email    = module.iam.service_account_email
  subnet                   = module.networking.subnet_self_links[0]
  depends_on               = [module.networking, module.iam]
}

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
  source           = "./modules/iam"
  account_id       = "vm-service-account"
  project_id       = var.project_id
  custom_role_id   = var.custom_role_id
  role_permissions = var.role_permissions
  depends_on       = [module.networking]
}

module "storage" {
  source                = "./modules/storage"
  project_id            = var.project_id
  region                = var.region
  buckets               = var.bucket_configs
  subnet_self_link      = module.networking.subnet_self_links[2]
  depends_on            = [module.networking, module.iam]
}

module "dataproc" {
  source                = "./modules/dataproc"
  project_id            = var.project_id
  region                = var.region
  cluster_name          = var.dataproc_cluster_name
  subnet_self_link      = module.networking.subnet_self_links[1]
  bucket_name           = module.storage.bucket_names[0]
  depends_on            = [module.networking, module.iam, module.storage]
}

module "bigquery" {
  source                = "./modules/bigquery"
  project_id            = var.project_id
  region                = var.region
  dataset_id            = var.bq_dataset_id
  table_ids             = var.bq_table_ids
  subnet_self_link      = module.networking.subnet_self_links[0]
  depends_on            = [module.networking, module.iam]
}

