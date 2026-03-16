# AWS Terraform Deployment

This Terraform stack provisions an EC2 instance and deploys Solar Scope using Docker Compose.

## What It Creates

- EC2 instance (default `t3.medium`)
- Security group with:
  - `22` for SSH
  - `5173` for frontend
  - `3000` for backend health/API
  - optional `8000/8001/8005/8007` when `expose_service_ports=true`
- Bootstrap script that installs Docker, clones repo, and runs:

```bash
docker compose up -d --build
```

This run starts the full stack including `stl`.

## Prerequisites

1. AWS account + Free Tier
2. AWS CLI configured (`aws configure`)
3. Terraform installed (`>= 1.6`)
4. Existing EC2 Key Pair in target region

## Deploy

```bash
cd infra/terraform/aws
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars and set at least ssh_key_name
terraform init
terraform plan
terraform apply
```

After apply, Terraform outputs:

- `frontend_url`
- `backend_health_url`
- `ssh_command`

## Verify

```bash
curl http://<public-ip>:3000/health
# open in browser
http://<public-ip>:5173
```

## Sizing Notes

- `t3.medium` is the recommended baseline for all 6 containers.
- You can scale down to `t3.small` if usage is light.
- First bootstrap can take several minutes while Docker images build.

## Destroy

```bash
terraform destroy
```
