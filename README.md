# Pocket-Lab

Pocket-Lab provisions a small AI lab on any fresh Linux host. It uses
Docker Compose to run several services and ships Ansible playbooks to
prepare and deploy everything automatically.

## Stack highlights

The lab bundles the following components:

- **Traefik** – reverse proxy with automatic TLS
- **RAGFlow** – document and knowledge base management
- **n8n** – workflow automation
- **Ollama** and **Open WebUI** – LLM management
- **MySQL** – relational database
- **MinIO** – S3 compatible object store
- **Valkey** – Redis compatible cache
- **Twingate connectors** – secure remote access
- **Prometheus**, **Node exporter**, **Grafana** and **Loki** – observability

## Repository map

| Path | Purpose |
| --- | --- |
| `Taskfile.yaml` | Developer shortcuts for Go Task and Docker Compose |
| `.env.template` | Copy to `.env` to provide environment variables |
| `ansible/` | Inventory, plays, roles and Galaxy requirements |
| `ansible/plays/00-30-*.yaml` | Four atomic plays (detect → bootstrap → harden → deploy) |
| `ansible/roles/ensure_conn_user` | Detect a working SSH user and cache it |
| `ansible/roles/pocket_lab` | Docker stack logic and templates |
| `ansible/roles/pocket_lab/files/compose.yaml` | The Docker Compose specification |

## Getting started

1. **Clone** the repository
   ```bash
   git clone https://github.com/your-org/ellebam-pocket-lab.git && cd ellebam-pocket-lab
   ```
2. **Create an env file**
   ```bash
   cp .env.template .env && edit .env  # domain, TLS e-mail, secrets …
   ```
3. **Configure Ansible inventory and users**
   - `ansible/inventory/hosts.yaml.template` → `hosts.yaml`; enter the server IP
   - Open `ansible/roles/pocket_lab/defaults/main.yaml.template` and set at least:
     - `l3d_users__local_users`
     - any service passwords
4. **Bootstrap the Python environment**
   ```bash
   task venv:init
   ```
5. **Provision the lab**
   ```bash
   task ansible_full  # detect → bootstrap → harden → deploy
   ```

### Manual compose run

For quick experiments without Ansible:

```bash
cp ansible/roles/pocket_lab/files/compose.yaml ./compose.yaml
cp .env.template .env
docker compose up -d
```

This skips OS hardening and user management.

---

## Task catalogue

| Command | What it does |
| --- | --- |
| `task ansible_detect` | Cache a working SSH login |
| `task ansible_bootstrap` | Create users only |
| `task ansible_harden` | Apply DevSec OS and SSH hardening |
| `task ansible_deploy` | Copy compose files and launch the stack |
| `task ansible_full` | Full pipeline |
| `task docker-*` | Shortcuts for Compose up/down/logs |

---

## Variables you will likely change

| Variable | Default | Notes |
| --- | --- | --- |
| `stack_domain`, `stack_email` | `ai.lab.example.com`, `admin@example.com` | Traefik host and ACME mail |
| `basic_auth` | bcrypt hash | Use `htpasswd -nbB` to generate |
| `tenant_name`, `*_TOKEN*` | – | Twingate connector |
| `n8n_user`, `n8n_password` | `admin` / `changeme` | Web UI credentials |
| `elastic_password`, `mysql_password`, `minio_password`, … | `changeme` | Service credentials |
| `compose_repo` | `/opt/pocket_lab` | Where compose files are deployed |
| `mem_limit` | `4g` | Memory limit for ES and Infinity |
| everything in `.env.template` | – | Mirrors compose environment |

The full list of defaults lives in
`ansible/roles/pocket_lab/defaults/main.yaml.template` and
`ansible/roles/ensure_conn_user/defaults/main.yaml`.

---

## After cloning – quick checklist

1. Add hosts to `ansible/inventory/hosts.yaml`
2. Define `l3d_users__local_users` with SSH keys
3. Set strong passwords in `.env` and defaults file
4. Run `task ansible_full` and enjoy your lab
