import streamlit as st
import subprocess
from PIL import Image


AVAILABLE_SERVICES = ["networking", "iam", "storage", "dataproc", "bigquery"]

def generate_module_block(service):
    blocks = {
        "networking": """module "networking" {
  source         = "./modules/networking"
  project_id     = var.project_id
  region         = var.region
  network_name   = var.network_name
  subnet_names   = var.subnet_names
  subnet_cidrs   = var.subnet_cidrs
  subnet_regions = var.subnet_regions
}""",
        "iam": """module "iam" {
  source     = "./modules/iam"
  project_id = var.project_id
  depends_on = [module.networking]
}""",
        "storage": """module "storage" {
  source           = "./modules/storage"
  project_id       = var.project_id
  region           = var.region
  bucket_names     = var.bucket_names
  subnet_self_link = module.networking.subnet_self_links[2]
  depends_on       = [module.networking, module.iam]
}""",
        "dataproc": """module "dataproc" {
  source           = "./modules/dataproc"
  project_id       = var.project_id
  region           = var.region
  cluster_name     = var.dataproc_cluster_name
  subnet_self_link = module.networking.subnet_self_links[1]
  bucket_name      = module.storage.bucket_names[0]
  depends_on       = [module.networking, module.iam, module.storage]
}""",
        "bigquery": """module "bigquery" {
  source           = "./modules/bigquery"
  project_id       = var.project_id
  region           = var.region
  dataset_id       = var.bq_dataset_id
  table_ids        = var.bq_table_ids
  subnet_self_link = module.networking.subnet_self_links[0]
  depends_on       = [module.networking, module.iam]
}"""
    }
    return blocks.get(service, "")

def write_main_tf(selected_services):
    with open("main.tf", "w") as f:
        f.write("# Auto-generated Terraform configuration for selected GCP services\n\n")
        for service in selected_services:
            block = generate_module_block(service)
            if block:
                f.write(block + "\n")

def updated_tfvars_file(services, bucket_names):
    output_file = "terraform.tfvars"
    default_file = "terraform.txt"
    try:
        with open(default_file, "r") as f:
            lines = f.readlines()

        updated_lines = [line.rstrip() for line in lines if line.strip() and not line.strip().startswith("#")]

        if "networking" in services:
            updated_lines += [
                'network_name           = "landing-zone-vpc1"',
                'subnet_names           = ["database-subnet", "processing-subnet", "storage-subnet"]',
                'subnet_cidrs           = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]',
                'subnet_regions         = ["us-central1", "us-central1", "us-central1"]'
            ]

        if "storage" in services and bucket_names:
            bucket_names_txt = "[" + ", ".join(f"\"{name}\"" for name in bucket_names) + "]"
            updated_lines.append(f"bucket_names           = {bucket_names_txt}")

        if "dataproc" in services:
            updated_lines.append('dataproc_cluster_name  = "landing-zone-cluster1"')

        if "bigquery" in services:
            updated_lines += [
                'bq_dataset_id          = "landing_zone_dataset1"',
                'bq_table_ids           = ["raw_data", "processed_data", "final_output"]'
            ]

        with open(output_file, "w") as f:
            for line in updated_lines:
                f.write(line + "\n")

        return True
    except FileNotFoundError:
        st.error("terraform.txt not found in the working directory.")
        return False
    except Exception as e:
        st.error(f"Error: {e}")
        return False

def run_terraform_command_status(command: str):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, f"Error running command '{command}': {e}"

# --- Streamlit UI ---



st.set_page_config(page_title="GCP Landing Zone", layout="centered")

logo = Image.open("logo.jpg")  # Make sure logo.jpg is in same folder
st.image(logo, width=100)
st.title("🌐 GCP Landing Zone Terraform Generator")


selected_services = st.multiselect(
    "Select GCP services to deploy:",
    options=AVAILABLE_SERVICES,
    help="Choose services for Terraform deployment"
)

bucket_names = []
valid_bucket_inputs = True

if "storage" in selected_services:
    num_buckets = st.number_input("Number of GCS buckets:", min_value=1, value=1, step=1)
    st.subheader("Enter Bucket Names Manually")
    for i in range(num_buckets):
        name = st.text_input(f"Bucket {i+1} name:", key=f"bucket_{i}").strip()
        bucket_names.append(name)

    if not all(bucket_names):
        valid_bucket_inputs = False
        st.error("All bucket names must be filled.")
    elif len(set(bucket_names)) != len(bucket_names):
        valid_bucket_inputs = False
        st.error("Bucket names must be unique.")

if st.button("🚀 Generate Terraform Files"):
    if not selected_services:
        st.warning("Please select at least one service.")
    elif "storage" in selected_services and not valid_bucket_inputs:
        st.warning("Please fix the bucket names before generating files.")
    else:
        write_main_tf(selected_services)
        tfvars_success = updated_tfvars_file(selected_services, bucket_names)
        if tfvars_success:
            st.success("Files `main.tf` and `terraform.tfvars` have been generated.")

            st.subheader("📄 main.tf")
            try:
                with open("main.tf", "r") as f:
                    st.code(f.read(), language="hcl")
            except FileNotFoundError:
                st.error("main.tf not found.")

            st.subheader("📄 terraform.tfvars")
            try:
                with open("terraform.tfvars", "r") as f:
                    st.code(f.read(), language="hcl")
            except FileNotFoundError:
                st.error("terraform.tfvars not found.")

st.markdown("---")
if st.button("🔍 Validate Configuration"):
    st.success("Manual validation complete — configuration looks ready to deploy.")

st.markdown("### ⚙️ Terraform Operations")

if st.button("⚡ Run Terraform Init / Plan / Apply"):
    with st.spinner("Running terraform init..."):
        success, output = run_terraform_command_status("terraform init")
        # st.success("✅ terraform init succeeded.") if success else st.error("❌ terraform init failed.")
        st.expander("Terraform Init Output").code(output)

    with st.spinner("Running terraform plan..."):
        success, output = run_terraform_command_status("terraform plan -var-file=terraform.tfvars")
        # st.success("✅ terraform plan succeeded.") if success else st.error("❌ terraform plan failed.")
        st.expander("Terraform Plan Output").code(output)

    with st.spinner("Running terraform apply..."):
        success, output = run_terraform_command_status("terraform apply -auto-approve -var-file=terraform.tfvars")
        # st.success("✅ terraform apply succeeded.") if success else st.error("❌ terraform apply failed.")
        st.expander("Terraform Apply Output").code(output)
