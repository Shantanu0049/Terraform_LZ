import os

def get_services():
    print("Enter the GCP services to deploy, separated by commas.")
    print("Available options: networking, iam, storage, dataproc, bigquery")
    services = input("Services to deploy: ").strip().lower().split(',')
    return [s.strip() for s in services if s.strip()]

def get_bucket_names():
    try:
        count = int(input("Enter the number of GCS buckets to create: ").strip())
        prefix = input("Enter a prefix for bucket names (default: 'bucket'): ").strip() or "bucket"
        lst = [f"{prefix}-{i+1}" for i in range(count)]
        return lst 
    except ValueError:
        print("Invalid input. Using default: 1 bucket named 'bucket-1'.")
        return ["bucket-1"]

def generate_module_block(service):
    blocks = {
        "networking": """
module "networking" {
  source         = "./modules/networking"
  project_id     = var.project_id
  region         = var.region
  network_name   = var.network_name
  subnet_names   = var.subnet_names
  subnet_cidrs   = var.subnet_cidrs
  subnet_regions = var.subnet_regions
}
""",
        "iam": """
module "iam" {
  source     = "./modules/iam"
  project_id = var.project_id
  depends_on = [module.networking]
}
""",
        "storage": f"""
module "storage" {{
  source           = "./modules/storage"
  project_id       = var.project_id
  region           = var.region
  bucket_names     = var.bucket_names
  subnet_self_link = module.networking.subnet_self_links[2] # Storage subnet
  depends_on       = [module.networking, module.iam]
}}
""",
        "dataproc": """
module "dataproc" {
  source           = "./modules/dataproc"
  project_id       = var.project_id
  region           = var.region
  cluster_name     = var.dataproc_cluster_name
  subnet_self_link = module.networking.subnet_self_links[1] # Processing subnet
  bucket_name      = module.storage.bucket_names[0]
  depends_on       = [module.networking, module.iam, module.storage]
}
""",
        "bigquery": """
module "bigquery" {
  source           = "./modules/bigquery"
  project_id       = var.project_id
  region           = var.region
  dataset_id       = var.bq_dataset_id
  table_ids        = var.bq_table_ids
  subnet_self_link = module.networking.subnet_self_links[0] # Database subnet
  depends_on       = [module.networking, module.iam]
}
"""
    }
    return blocks.get(service, "")

def write_main_tf(selected_services):
    with open("TR_main.tf", "w") as f:
        f.write("# Auto-generated Terraform configuration for selected GCP services\n\n")
        for service in selected_services:
            
            block = generate_module_block(service)
            if block:
                f.write(block + "\n")
            else:
                print(f"Warning: No configuration found for '{service}'.")

def updated_tfvars_file(services, len_bucket_names, bucket_names):
    default_file = "terraform.txt"
    output_file = "req_terraform.tfvars"

    try:
        # Read the default file
        with open(default_file, "r") as f:
            lines = f.readlines()

        # Prepare updated values
        updated_lines = []

        # Always keep the original lines (filter out empty lines and comments)
        for line in lines:
            if line.strip() and not line.strip().startswith("#"):
                updated_lines.append(line.rstrip())

        # Add or override based on selected services
        if "networking" in services:
            updated_lines.append('network_name           = "landing-zone-vpc"')
            updated_lines.append('subnet_names           = ["database-subnet", "processing-subnet", "storage-subnet"]')
            updated_lines.append('subnet_cidrs           = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]')
            updated_lines.append('subnet_regions         = ["us-central1", "us-central1", "us-central1"]')

        if "storage" in services and bucket_names:
            updated_lines.append(f"bucket_names           = {bucket_names_txt}")
            updated_lines.append(f"num_buckets            = {len_bucket_names}")
            # Optional: use a prefix
            prefix = bucket_names[0].rsplit("-", 1)[0] if "-" in bucket_names[0] else "bucket"
            updated_lines.append(f'bucket_name_pre     = "{prefix}"')

        if "dataproc" in services:
            updated_lines.append('dataproc_cluster_name  = "landing-zone-cluster"')

        if "bigquery" in services:
            updated_lines.append('bq_dataset_id          = "landing_zone_dataset"')
            updated_lines.append('bq_table_ids           = ["raw_data", "processed_data", "final_output"]')

        # Write to terraform.tfvars
        with open(output_file, "w") as f:
            for line in updated_lines:
                f.write(line + "\n")

        print(f" terraform.tfvars generated successfully with selected services: {', '.join(services)}")

    except FileNotFoundError:
        print(" Error: default_terraform.tfvars not found.")
    except Exception as e:
        print(f" Unexpected error: {e}")


if __name__ == "__main__":
    services = get_services()
    bucket_names = None

    if "storage" in services:
        bucket_names = get_bucket_names()
        print(bucket_names, type(bucket_names))
        # Convert list to Terraform list syntax
        bucket_names_txt = "[" + ", ".join(f"\"{name}\"" for name in bucket_names) + "]"
        print(bucket_names_txt)

    if services:
        write_main_tf(services)
        updated_tfvars_file(services, len(bucket_names), bucket_names)
        print("main.tf has been generated successfully.")
    else:
        print("No valid services entered. Exiting.")
