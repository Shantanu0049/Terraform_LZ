import os
import subprocess
import streamlit as st
from PIL import Image
import google.generativeai as genai
import git
from github import Github

# === CONFIGURATION ===
AVAILABLE_SERVICES = ["networking", "iam", "storage", "dataproc", "bigquery", "vm"]
REPO_NAME = "Shantanu0049/Terraform_LZ"
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
gh = Github(os.getenv("GITHUB_TOKEN"))

# === TERRAFORM FUNCTIONS ===
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
  source           = "./modules/storage"
  project_id       = var.project_id
  region           = var.region
  buckets          = var.bucket_configs
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
        for svc in selected_services:
            blk = generate_module_block(svc)
            if blk:
                f.write(blk + "\n\n")

def updated_tfvars_file(services, bucket_configs, iam_inputs):
    try:
        with open("terraform.txt", "r") as tf:
            lines = [l.strip() for l in tf if l.strip() and not l.startswith("#")]
        if "networking" in services:
            lines += [
                'network_name           = "landing-zone-vpc-testing"',
                'subnet_names           = ["database-subnet","processing-subnet","storage-subnet"]',
                'subnet_cidrs           = ["10.0.1.0/24","10.0.2.0/24","10.0.3.0/24"]',
                'subnet_regions         = ["us-central1","us-central1","us-central1"]'
            ]
        if "iam" in services:
            lines.append(f'custom_role_id = "{iam_inputs["custom_role_id"]}"')
            perms = "[" + ", ".join(f'"{p}"' for p in iam_inputs["role_permissions"]) + "]"
            lines.append(f'role_permissions = {perms}')
        if "storage" in services and bucket_configs:
            storage_list = []
            for cfg in bucket_configs:
                rule = f""", lifecycle_rule = {{
    action = {{ type = "Delete" }}
    condition = {{ age = {cfg["lifecycle_age"]} }}
}}""" if cfg["lifecycle_age"] else ""
                storage_list.append(f"""{{
  name                      = "{cfg["name"]}"
  location                  = "{cfg["location"]}"
  storage_class             = "{cfg["storage_class"]}"
  versioning_enabled        = {str(cfg["versioning"]).lower()}
  uniform_bucket_level_access = {str(cfg["ubla"]).lower()}{rule}
  public_access_prevention = "{cfg["public_access_prevention"]}"
  force_destroy            = true
}}""")
            lines.append("bucket_configs = [\n" + ",\n".join(storage_list) + "\n]")
        if "dataproc" in services:
            lines.append('dataproc_cluster_name = "landing-zone-cluster-testing"')
        if "bigquery" in services:
            lines += [
                'bq_dataset_id = "landing_zone_dataset_testing"',
                'bq_table_ids = ["raw_data","processed_data","final_output"]'
            ]
        with open("terraform.tfvars", "w") as out:
            out.write("\n".join(lines) + "\n")
        return True
    except Exception as e:
        st.error(f"Error updating terraform.tfvars: {e}")
        return False

def generate_iam_permissions(prompt: str):
    try:
        resp = genai.GenerativeModel("gemini-1.5-flash-latest").generate_content(
            f"List the GCP IAM permissions required for: {prompt}. Respond comma-separated."
        )
        return [p.strip().strip("`") for p in resp.text.split(",") if p.strip()]
    except Exception as e:
        st.error(f"AI generation error: {e}")
        return []

# === STREAMLIT UI & STATE ===
st.set_page_config(page_title="GCP Landing Zone Generator", layout="centered")
st.image(Image.open("logo.jpg"), width=100)
st.title("🌐 GCP Landing Zone Terraform Generator")

st.session_state.setdefault("iam_permissions", [])
st.session_state.setdefault("custom_role_id", "")
st.session_state.setdefault("got_files", False)
st.session_state.setdefault("branch_mode", "Select existing")
st.session_state.setdefault("branch_name", "")

selected = st.multiselect("Select GCP services:", AVAILABLE_SERVICES)
bucket_configs, iam_inputs = [], {}

if "storage" in selected:
    st.subheader("🪣 GCS Bucket Configuration")
    num = st.number_input("Number of buckets:", 1, 5, 1)
    for i in range(num):
        st.markdown(f"**Bucket {i+1}**")
        n = st.text_input("Name", key=f"name_{i}").strip()
        loc = st.text_input("Location", key=f"loc_{i}").strip()
        sc = st.selectbox("Storage Class", ["STANDARD","NEARLINE","COLDLINE","ARCHIVE"], key=f"sc_{i}")
        vers = st.checkbox("Versioning?", key=f"vers_{i}")
        ubla = st.checkbox("Uniform Bucket-Level Access?", key=f"ubla_{i}")
        age = st.number_input("Auto-delete days:", 0, 365, 0, key=f"age_{i}")
        bucket_configs.append({
            "name": n, "location": loc, "storage_class": sc,
            "versioning": vers, "ubla": ubla,
            "lifecycle_age": age or None,
            "public_access_prevention": "enforced"
        })

if "iam" in selected:
    st.subheader("🔐 IAM Role Configuration")
    st.session_state.custom_role_id = st.text_input("Custom Role ID", st.session_state.custom_role_id).strip()
    prompt = st.text_area("Describe what this IAM role should do")
    if st.button("💡 Generate IAM Permissions from AI"):
        if prompt:
            st.session_state.iam_permissions = generate_iam_permissions(prompt)
    if st.session_state.iam_permissions:
        st.markdown("IAM Permissions:")
        st.code("\n".join(st.session_state.iam_permissions))
    if st.session_state.custom_role_id and st.session_state.iam_permissions:
        iam_inputs = {
            "custom_role_id": st.session_state.custom_role_id,
            "role_permissions": st.session_state.iam_permissions
        }

if st.button("🚀 Generate Terraform Files"):
    if not selected:
        st.warning("Select at least one service.")
    else:
        ok = updated_tfvars_file(selected, bucket_configs, iam_inputs)
        write_main_tf(selected)
        if ok:
            st.session_state.got_files = True

if st.session_state.got_files:
    st.success("Terraform files generated.")
    st.subheader("📄 main.tf"); st.code(open("main.tf").read(), language="hcl")
    st.subheader("📄 terraform.tfvars"); st.code(open("terraform.tfvars").read(), language="hcl")
    st.markdown("---")
    st.subheader("📂 Git Branch Handling")
    repo = gh.get_repo(REPO_NAME)
    branches = [b.name for b in repo.get_branches()]
    st.radio("Branch Mode:", ["Select existing", "Create new"], key="branch_mode")
    if st.session_state.branch_mode == "Select existing":
        st.selectbox("Branch:", branches, key="branch_name")
    else:
        st.text_input("New branch name:", key="branch_name")

    b = st.session_state.branch_name
    if b:
        repo_local = git.Repo(os.getcwd())
        repo_local.git.fetch()
        repo_local.git.stash("push", "-u")
        local_heads = [h.name for h in repo_local.heads]
        if b not in local_heads:
            repo_local.git.checkout("main")
            repo_local.git.pull("origin", "main")
            repo_local.git.checkout("-b", b, "origin/main")
        else:
            repo_local.git.checkout(b)
            repo_local.git.pull("origin", b)
        try:
            repo_local.git.stash("pop")
        except:
            pass

        diff = subprocess.run(
            ["git", "diff", "--merge-base", "origin/main", b, "--", "main.tf", "terraform.tfvars"],
            capture_output=True, text=True, cwd=os.getcwd()
        ).stdout
        if diff:
            st.subheader("📄 Proposed Diff"); st.code(diff)
        else:
            st.info("No changes detected.")

        c1, c2, c3 = st.columns(3)
        with c1:
            def push_branch():
                try:
                    repo_local.git.add("main.tf", "terraform.tfvars")
                    if repo_local.is_dirty(True, True, True):
                        repo_local.index.commit(f"Update TF → {b}")
                        repo_local.remote("origin").push(b)
                        st.success(f"Pushed `{b}`")
                    else:
                        st.info("Nothing new to push.")
                except Exception as e:
                    st.error(f"Push failed: {e}")
            st.button("📤 Push to branch", on_click=push_branch)
        with c2:
            def create_pr():
                try:
                    open_prs = repo.get_pulls(state="open", head=b, base="main")
                    if open_prs.totalCount == 0:
                        pr = repo.create_pull(
                            title=f"Merge `{b}` → main",
                            body="Auto-PR via Streamlit", head=b, base="main"
                        )
                        st.success(f"PR created: {pr.html_url}")
                    else:
                        st.info("PR already exists.")
                except Exception as e:
                    st.error(f"PR creation failed: {e}")
            st.button("✅ Approve & PR", on_click=create_pr)
        with c3:
            st.button("❌ Reject", on_click=lambda: st.error("Merge request rejected ✋"))
