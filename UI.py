import streamlit as st
import subprocess
from PIL import Image
import google.generativeai as genai
import os

AVAILABLE_SERVICES = ["networking", "iam", "storage", "dataproc", "bigquery", "vm"]

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

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
  source           = "./modules/iam"
  account_id       = "vm-service-account"
  project_id       = var.project_id
  custom_role_id   = var.custom_role_id
  role_permissions = var.role_permissions
  depends_on       = [module.networking]
}""",
        "storage": """module "storage" {
  source                     = "./modules/storage"
  project_id                 = var.project_id
  region                     = var.region
  buckets                = var.bucket_configs
  subnet_self_link           = module.networking.subnet_self_links[2]
  depends_on                 = [module.networking, module.iam]
  

}""",
        "dataproc": """module "dataproc" {
  source           = "./modules/dataproc"
  project_id       = var.project_id
  region           = var.region
  cluster_name     = var.dataproc_cluster_name
  subnet_self_link = module.networking.subnet_self_links[1]
  bucket_name = module.storage.bucket_names[0]
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
}""",
        "vm": """module "vm" {
  source                = "./modules/vm"
  project_id            = var.project_id
  zone                  = var.zone
  instance_name         = var.instance_name
  machine_type          = var.machine_type
  service_account_email = module.iam.service_account_email
  subnet                = module.networking.subnet_self_links[0]
  depends_on            = [module.networking, module.iam]
}"""
    }
    return blocks.get(service, "")

def write_main_tf(selected_services):
    with open("main.tf", "w") as f:
        f.write("# Auto-generated Terraform configuration\n\n")
        for service in selected_services:
            block = generate_module_block(service)
            if block:
                f.write(block + "\n\n")

def updated_tfvars_file(services, bucket_configs, iam_inputs):
    try:
        with open("terraform.txt", "r") as f:
            base_lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]

        if "networking" in services:
            base_lines += [
                'network_name           = "landing-zone-vpc-testing"',
                'subnet_names           = ["database-subnet", "processing-subnet", "storage-subnet"]',
                'subnet_cidrs           = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]',
                'subnet_regions         = ["us-central1", "us-central1", "us-central1"]'
            ]

        if "iam" in services:
            base_lines.append(f'custom_role_id         = "{iam_inputs["custom_role_id"]}"')
            permissions = "[" + ", ".join(f"\"{p}\"" for p in iam_inputs["role_permissions"]) + "]"
            base_lines.append(f'role_permissions       = {permissions}')

        if "storage" in services and bucket_configs:
            storage_list = []
            for config in bucket_configs:
                rule_block = f''',
        lifecycle_rule = {{
        action = {{ type = "Delete" }}
        condition = {{ age = {config["lifecycle_age"]} }}
      }}''' if config["lifecycle_age"] else ""
                storage_list.append(f'''{{
      name                      = "{config["name"]}"
      location                  = "{config["location"]}"
      storage_class             = "{config["storage_class"]}"
      versioning_enabled        = {str(config["versioning"]).lower()}
      uniform_bucket_level_access = {str(config["ubla"]).lower()}{rule_block}
      public_access_prevention     = "enforced"
      uniform_access               = false
      force_destroy                = true
    }}''')
            full_block = "bucket_configs = [\n" + ",\n".join(storage_list) + "\n]"
            base_lines.append(full_block)

        if "dataproc" in services:
            base_lines.append('dataproc_cluster_name  = "landing-zone-cluster-testing"')

        if "bigquery" in services:
            base_lines += [
                'bq_dataset_id          = "landing_zone_dataset_testing"',
                'bq_table_ids           = ["raw_data", "processed_data", "final_output"]'
            ]

        with open("terraform.tfvars", "w") as f:
            for line in base_lines:
                f.write(line + "\n")

        return True
    except Exception as e:
        st.error(f"Error updating terraform.tfvars: {e}")
        return False

def run_terraform_command_status(command: str):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

def generate_iam_permissions(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content(
            f"List the GCP IAM permissions required for: {prompt}. Respond in a comma-separated list."
        )
        perms = response.text.strip().replace("\n", "")
        return [p.strip().replace("`", "") for p in perms.split(",") if p.strip()]
    except Exception as e:
        st.error(f"Failed to generate IAM permissions: {e}")
        return []

# ========== Streamlit UI ==========

st.set_page_config(page_title="GCP Landing Zone Generator", layout="centered")
st.image(Image.open("logo.jpg"), width=100)
st.title("🌐 GCP Landing Zone Terraform Generator")

if "iam_permissions" not in st.session_state:
    st.session_state["iam_permissions"] = []
if "custom_role_id" not in st.session_state:
    st.session_state["custom_role_id"] = ""

selected_services = st.multiselect("Select GCP services to deploy:", AVAILABLE_SERVICES)

bucket_configs = []
iam_inputs = {}

if "storage" in selected_services:
    st.subheader("🪣 GCS Bucket Configuration")
    num_buckets = st.number_input("Number of buckets:", min_value=1, value=1, step=1)

    for i in range(num_buckets):
        st.markdown(f"**Bucket {i+1}**")
        name = st.text_input(f"Name", key=f"name_{i}").strip()
        location = st.text_input(f"Location (e.g., us-central1)", key=f"loc_{i}").strip()
        storage_class = st.selectbox(f"Storage Class", ["STANDARD", "NEARLINE", "COLDLINE", "ARCHIVE"], key=f"sc_{i}")
        versioning = st.checkbox(f"Enable Versioning?", key=f"vers_{i}")
        ubla = st.checkbox(f"Uniform Bucket-Level Access?", key=f"ubla_{i}")
        lifecycle_age = st.number_input("Auto-delete objects after X days (optional)", min_value=0, key=f"age_{i}")

        bucket_configs.append({
            "name": name,
            "location": location,
            "storage_class": storage_class,
            "versioning": versioning,
            "ubla": ubla,
            "lifecycle_age": lifecycle_age if lifecycle_age > 0 else None
        })

if "iam" in selected_services:
    st.subheader("🔐 IAM Role Configuration")
    st.session_state["custom_role_id"] = st.text_input("Custom Role ID", value=st.session_state["custom_role_id"]).strip()
    prompt = st.text_area("Describe what this IAM role should be able to do")

    if st.button("💡 Generate IAM Permissions from AI"):
        if prompt:
            perms = generate_iam_permissions(prompt)
            st.session_state["iam_permissions"] = perms
            st.success("Permissions generated:")
            st.code("\n".join(perms))
        else:
            st.warning("Please enter a description.")

    if st.session_state["iam_permissions"]:
        st.markdown("#### Current IAM Permissions")
        st.code("\n".join(st.session_state["iam_permissions"]))

    if st.session_state["custom_role_id"] and st.session_state["iam_permissions"]:
        iam_inputs = {
            "custom_role_id": st.session_state["custom_role_id"],
            "role_permissions": st.session_state["iam_permissions"]
        }

if st.button("🚀 Generate Terraform Files"):
    if not selected_services:
        st.warning("Please select at least one service.")
    else:
        success = updated_tfvars_file(selected_services, bucket_configs, iam_inputs)
        write_main_tf(selected_services)
        if success:
            st.success("Terraform files generated successfully.")
            with open("main.tf") as f:
                st.subheader("📄 main.tf")
                st.code(f.read(), language="hcl")
            with open("terraform.tfvars") as f:
                st.subheader("📄 terraform.tfvars")
                st.code(f.read(), language="hcl")

if st.button("⚡ Run Terraform Init / Plan / Apply"):
    with st.spinner("Running terraform init..."):
        _, out = run_terraform_command_status("terraform init")
        st.expander("Terraform Init Output").code(out)

    with st.spinner("Running terraform plan..."):
        _, out = run_terraform_command_status("terraform plan -var-file=terraform.tfvars")
        st.expander("Terraform Plan Output").code(out)

    with st.spinner("Running terraform apply..."):
        _, out = run_terraform_command_status("terraform apply -auto-approve -var-file=terraform.tfvars")
        st.expander("Terraform Apply Output").code(out)
