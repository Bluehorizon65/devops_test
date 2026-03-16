# Solar Scope

Solar Scope is a multi-service solar analysis platform with frontend, backend proxy, rooftop AI API, and supporting simulation services.

## Local Development

### AI Service

```bash
cd AI
uvicorn rooftop_fastapi:app --host 0.0.0.0 --port 8005 --reload
```

### Backend Service

```bash
cd backend
npm install
npm start
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### PV Simulation

```bash
cd pv_simulation
python main_v2.py
```

### Satellite Service

```bash
cd satellite
python satellite_zoom_server.py
```

### STL Service

```bash
cd stl/stl
uvicorn api:app --host 0.0.0.0 --port 8007 --reload
```

Simulation mode:

```bash
cd stl/stl
python web.py
```

## DevOps Additions

This repository now includes complete DevOps artifacts for project evaluation:

- Version control and collaboration: `CONTRIBUTING.md`, `.github/pull_request_template.md`, `.github/CODEOWNERS`
- CI/CD automation: `.github/workflows/ci-cd.yml`
- Containerization: `frontend/Dockerfile`, `backend/Dockerfile`, `AI/Dockerfile`, `docker-compose.yml`
- Kubernetes orchestration: `deploy/k8s/base`, `deploy/k8s/overlays/dev`
- Infrastructure as Code (Ansible): `infra/ansible`

Detailed walkthrough: `DEVOPS.md`

Rubric/demo proof checklist: `RUBRIC_EVIDENCE.md`

## Quick DevOps Commands

### Docker Compose

```bash
docker compose up --build
```

This now starts the full stack end-to-end:

- `frontend` (Vite + Nginx)
- `backend` (Node proxy)
- `ai` (rooftop detection)
- `satellite` (satellite image service)
- `pv-simulation` (solar calculator)
- `stl` (3D model generation)

### Kubernetes Deploy

```bash
kubectl apply -k deploy/k8s/overlays/dev
```

### Ansible IaC

```bash
cd infra/ansible
ansible-playbook playbooks/provision.yml
ansible-playbook playbooks/deploy.yml
```

### Terraform on AWS

```bash
cd infra/terraform/aws
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars and set ssh_key_name
terraform init
terraform apply
```

Detailed AWS instructions: `infra/terraform/aws/README.md`

