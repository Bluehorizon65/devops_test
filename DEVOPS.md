# Solar Scope DevOps Blueprint

This document maps the project to the evaluation rubric and explains how to run all DevOps components.

## 1) Version Control and Collaboration

Implemented with:

- `CONTRIBUTING.md` for branching, commits, PR process
- `.github/pull_request_template.md` for structured reviews
- `.github/CODEOWNERS` for ownership and review routing

Recommended workflow:

1. Create feature branch from `develop`.
2. Commit with conventional commit messages.
3. Open PR to `develop`.
4. Merge to `main` only through release PR.

## 2) End-to-End CI/CD Pipeline

Pipeline file: `.github/workflows/ci-cd.yml`

Stages:

1. Build stage
   - Node dependency install for backend/frontend
   - Frontend production build
   - Python dependency install and compile check
2. Test stage
   - Backend API health test
   - AI FastAPI health test
3. Containerize stage
   - Build and push Docker images to GHCR
4. Deploy stage
   - Deploy manifests via `kubectl apply -k deploy/k8s/overlays/dev`

Required repository secrets:

- `KUBE_CONFIG` (base64 kubeconfig for deployment)

## 3) Containerization and Deployment

Artifacts:

- `backend/Dockerfile`
- `frontend/Dockerfile`
- `AI/Dockerfile`
- `pv_simulation/Dockerfile`
- `satellite/Dockerfile`
- `stl/Dockerfile`
- `docker-compose.yml`
- Kubernetes manifests in `deploy/k8s`

Local container run:

```bash
docker compose up --build
```

Kubernetes deployment:

```bash
kubectl apply -k deploy/k8s/overlays/dev
```

## 4) Infrastructure as Code (Ansible)

Primary IaC path is now Ansible (cloud-agnostic) in `infra/ansible`.

What it automates:

- Provisioning Ubuntu server with Docker Engine and Docker Compose plugin
- Pulling/updating project repository
- Rendering production compose configuration from template
- Building and deploying all services with Docker Compose

Ansible usage:

```bash
cd infra/ansible
ansible-playbook playbooks/provision.yml
ansible-playbook playbooks/deploy.yml
```

Additional cloud path:

- `infra/terraform/aws` provides AWS IaC (EC2 + Docker Compose bootstrap), suitable for Free Tier demo deployment.

## Presentation Tips

For your DevOps demo, show this order:

1. Branch strategy and PR template.
2. A CI/CD run in GitHub Actions.
3. Docker images and `docker compose` execution.
4. `kubectl get pods -n solar-scope` after deploy.
5. Ansible provision/deploy output and running containers (`docker ps`).
