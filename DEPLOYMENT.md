# Deployment Guide (Render + Netlify)

## Architecture

- Frontend: Netlify (React/Vite static site)
- Backend: Render (Node.js web service)
- Backend dependencies: set as environment variables (`CALCULATOR_API`, `SATELLITE_API`, `ROOFTOP_API`, `NEXT_API`)

## 1) Pre-deployment checks

Run locally first:

```bash
cd backend && npm ci && npm test
cd ../frontend && npm ci && npm run build
cd ../AI && python -m pytest -q tests/test_health.py
```

## 2) Deploy Backend on Render

### Option A: render.yaml Blueprint (recommended)

1. Push repository to GitHub.
2. Open Render -> New -> Blueprint.
3. Select this repo. Render reads `render.yaml`.
4. Set missing env vars in Render dashboard:
   - `CALCULATOR_API`
   - `SATELLITE_API`
   - `ROOFTOP_API`
   - `NEXT_API`
   - `CORS_ORIGIN` (set to your Netlify domain)
5. Deploy and confirm health endpoint:
   - `https://<your-render-service>.onrender.com/health`

### Option B: Manual service setup

- Runtime: Node
- Root Directory: `backend`
- Build Command: `npm ci`
- Start Command: `npm start`
- Health check path: `/health`
- Add same environment variables as above.

## 3) Deploy Frontend on Netlify

1. Open Netlify -> Add new site -> Import from Git.
2. Select repository.
3. Build settings:
   - Base directory: `frontend`
   - Build command: `npm ci && npm run build`
   - Publish directory: `dist`
4. Add environment variable:
   - `VITE_API_BASE_URL=https://<your-render-service>.onrender.com`
5. Deploy.

The repo includes `netlify.toml`, so Netlify can auto-detect these values.

## 4) Connect frontend to backend

After both deploy:

1. Open backend URL `/health` and confirm `{ "status": "ok" ... }`.
2. Open frontend URL and perform a solar request.
3. In browser devtools, verify calls go to your Render backend URL.

## 5) CI/CD integration

Current GitHub workflow `.github/workflows/ci-cd.yml` already runs:

- Build stage
- Test stage
- Container build/push stage (on push to `main`)
- Kubernetes deploy stage (if `KUBE_CONFIG` secret exists)

For Render/Netlify deployment, you can use their built-in Git auto-deploy:

- Render auto-deploy on push to selected branch.
- Netlify auto-deploy on push/PR.

## 6) Production checklist

- Set `CORS_ORIGIN` on Render to your exact Netlify domain (e.g. `https://your-site.netlify.app`).
- Keep secrets in platform env vars, not in repo.
- Ensure external API endpoints in backend env vars are reachable from Render.
- Use custom domains and HTTPS on both services (both platforms support this).

## 7) IaC for marks (Ansible)

Use cloud-agnostic Ansible IaC from `infra/ansible` to demonstrate reproducible infrastructure and deployment automation.

1. Update `infra/ansible/inventory/hosts.ini` with your VM details.
2. Update environment values in `infra/ansible/group_vars/all.yml`.
3. Run provisioning and deployment:

```bash
cd infra/ansible
ansible-playbook playbooks/provision.yml
ansible-playbook playbooks/deploy.yml
```

This gives you a fully code-driven infra+deploy workflow without Azure.

## 8) Quick rollback

- Render: Deploys -> choose previous deploy -> Redeploy.
- Netlify: Deploys -> Publish previous successful deploy.
