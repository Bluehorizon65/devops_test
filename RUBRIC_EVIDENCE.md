# Rubric Evidence Guide

Use this file during your demo/presentation to show clear proof for each DevOps criterion.

## Key Clarification

- Render is a deployment platform (PaaS).
- Ansible is Infrastructure as Code (IaC) and automation.
- They are not the same thing.

You can use both:

- Docker images for packaging apps
- Render for hosting/deployment
- Ansible to prove infra/deploy automation from code

## 1) Containerization (Local End-to-End)

Proof files:

- `docker-compose.yml`
- `frontend/Dockerfile`
- `backend/Dockerfile`
- `AI/Dockerfile`
- `pv_simulation/Dockerfile`
- `satellite/Dockerfile`
- `stl/Dockerfile`

Demo commands:

```bash
docker compose up --build -d
docker compose ps
curl http://localhost:3000/health
curl http://localhost:8005/health
```

Expected result:

- All 6 services are `Up`
- Health endpoints return `200`

## 2) CI/CD Proof

Proof file:

- `.github/workflows/ci-cd.yml`

Demo proof:

- Show latest successful run in GitHub Actions
- Open job logs for build, test, and container stages

## 3) Deployment Proof (Render/Netlify)

Proof files:

- `render.yaml`
- `netlify.toml`
- `DEPLOYMENT.md`

What to show:

- Render backend URL: `/health` returns OK
- Netlify frontend URL loads and calls backend

## 4) IaC Proof (Ansible)

Proof files:

- `infra/ansible/playbooks/provision.yml`
- `infra/ansible/playbooks/deploy.yml`
- `infra/ansible/templates/docker-compose.prod.yml.j2`
- `infra/ansible/group_vars/all.yml`

Demo commands:

```bash
cd infra/ansible
ansible-playbook playbooks/provision.yml
ansible-playbook playbooks/deploy.yml
```

What this proves:

- Server setup is automated from code
- Deployment is repeatable from code
- This is IaC/automation evidence for marks

## 5) How to Explain in 20 Seconds

Use this line:

"We package everything with Docker, run all services locally with Compose, deploy app services to Render/Netlify, and use Ansible playbooks as IaC to automate provisioning and deployment."
