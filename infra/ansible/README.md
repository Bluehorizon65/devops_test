# Ansible IaC (Cloud Agnostic)

This folder provides Infrastructure as Code and deployment automation without requiring Azure.

## What is automated

- Server provisioning (Docker Engine + Docker Compose plugin)
- Application checkout/update from Git
- Runtime configuration via Ansible variables
- Container build and deployment via Docker Compose

## Prerequisites

- Control machine with Ansible installed
- Ubuntu VM reachable by SSH
- SSH key access to deployment user

Install Ansible on control machine:

```bash
pip install ansible
ansible-galaxy collection install community.docker
```

## Configure inventory and variables

1. Default `inventory/hosts.ini` is already set for local execution (`ansible_connection=local`).
2. If deploying to remote VM, replace with remote host/user/key details.
2. Edit `group_vars/all.yml` with your environment URLs and origins.

## Run IaC

Provision host:

```bash
ansible-playbook playbooks/provision.yml
```

Deploy app:

```bash
ansible-playbook playbooks/deploy.yml
```

## Verify deployment

SSH into VM and check containers:

```bash
docker ps
```

Check app endpoints:

- `http://<server-ip>/`
- `http://<server-ip>:3000/health`
- `http://<server-ip>:8005/health`
