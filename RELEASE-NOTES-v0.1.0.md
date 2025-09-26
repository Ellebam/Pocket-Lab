# Pocket-Lab v0.1.0 — first public release

## Highlights
- One repo, two primary deploy paths: **Ansible** (authoritative) and **plain Docker Compose** for quick experiments.
- TLS-by-default via **Traefik** (ACME DNS-01), plus basic-auth middleware for UIs lacking native auth.
- Self-hosted AI components: **Ollama**, **Open WebUI**, **RAGFlow**, **Elasticsearch/Infinity**, **MySQL**, **MinIO**, **Valkey**, **SearXNG**, **Stirling PDF**, **Portainer**.
- Observability with **Prometheus + Grafana + Loki**.
- Single `.env` flow; first-run helpers for admin/bootstrap where applicable.

## Quick Start (Ansible)
```bash
cp ansible/inventory/hosts.yaml.template ansible/inventory/hosts.yaml
# optional: task venv:init
ansible-playbook ansible/site.yaml --syntax-check
```

## Quick Start (plain Compose)
```bash
cp ansible/roles/pocket_lab/files/compose.yaml .
cp .env.template .env
# Set strong secrets, review OFFLINE_MODE=true
docker compose up -d
```

## Known Notes
- Change demo/basic-auth credentials before exposing any UI.
- `OFFLINE_MODE=true` is the default for Open WebUI; adjust if you need online features.
