# GCP Landing Zone using Terraform

This repository contains Terraform configuration for setting up a comprehensive GCP landing zone with multiple services distributed across multiple subnets.

## Architecture

The landing zone includes:
- VPC with 3 subnets:
  - Subnet 1: Database Services (BigQuery)
  - Subnet 2: Processing Services (Dataproc)
  - Subnet 3: Storage Services (GCS)
- IAM roles and permissions
- Google Cloud Storage buckets
- Dataproc cluster
- BigQuery datasets and tables

## Prerequisites

- Terraform >= 1.0.0
- Google Cloud SDK
- Appropriate GCP permissions to create resources

## How to Use

1. Clone this repository
2. Update the `terraform.tfvars` file with your specific values
3. Initialize Terraform:
   ```
   terraform init
   ```
4. Plan the deployment:
   ```
   terraform plan
   ```
5. Apply the configuration:
   ```
   terraform apply
   ```

## Folder Structure

```
.
├── main.tf                 # Main configuration
├── variables.tf            # Input variables
├── outputs.tf              # Output variables
├── terraform.tfvars        # Variable values
├── providers.tf            # Provider configuration
└── modules/
    ├── networking/         # VPC and subnets
    ├── iam/                # Identity and Access Management
    ├── storage/            # Google Cloud Storage
    ├── dataproc/           # Dataproc cluster
    └── bigquery/           # BigQuery datasets and tables
```

## Customization

Modify the `terraform.tfvars` file to customize the deployment for your specific needs.