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

## Requirements

- Linux host with [Docker](https://docs.docker.com/get-docker/) and
  [docker compose](https://docs.docker.com/compose/) installed
- Python 3.11 or newer
- Optional: [Go Task](https://taskfile.dev) for the helper commands

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

### Provisioning with Ansible

The repository bundles a small automation layer under `ansible/`. After
preparing your `.env` and inventory you only need two commands:

```bash
task venv:init  # install Ansible and required collections
task ansible_full  # detect → bootstrap → harden → deploy
```

The individual phases live in `ansible/plays/00-30-*.yaml` and can be run via
`task ansible_detect`, `task ansible_bootstrap`, `task ansible_harden` and
`task ansible_deploy` if you want to execute them separately.

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
| `tg_tenant_name`, `*_TOKEN*` | – | Twingate connector |
| `n8n_admin_email`, `n8n_admin_password` | `admin@example.com` / `changeme` | n8n owner account |
| `es_password`, `mysql_password`, `minio_root_password`, … | `changeme` | Service credentials |
| `compose_repo` | `/opt/pocket_lab` | Where compose files are deployed |
| `mem_limit` | `4g` | Memory limit for ES and Infinity |
| everything in `.env.template` | – | Mirrors compose environment |

## MinIO

The lab ships with a [MinIO](https://min.io) server used as the S3 backend for
other services. Traefik simply forwards `https://minio.${TRAEFIK_DOMAIN}` to the
MinIO container, which serves both the API and the web console.

Key variables:

- `MINIO_ROOT_USER` / `MINIO_ROOT_PASSWORD` – console credentials.
- `MINIO_SERVER_URL` – external URL of the API and console (defaults to the
  Traefik hostname).

If you customise `TRAEFIK_DOMAIN`, adjust `MINIO_SERVER_URL` accordingly so the
dashboard can reach the backend.


Full variable reference lives in:

- `ansible/roles/pocket_lab/defaults/main.yaml.template`
    
- `ansible/roles/ensure_conn_user/defaults/main.yaml`
    

---

## Role overview

|Role|Purpose|
|---|---|
|**ensure_conn_user**|Probe `root`, inventory user, first in `l3d_users__local_users`; cache winner for 24 h so every play can rely on `hostvars[host].conn_user`.|
|**l3d.users.user / .admin**|Create regular + sudo users with SSH keys. [Ansible Galaxy](https://galaxy.ansible.com/ui/repo/published/l3d/users/content/role/user/?utm_source=chatgpt.com)|
|**devsec.hardening.os_hardening / ssh_hardening**|CIS‑style OS tweaks, secure `sshd_config`. [GitHub](https://github.com/dev-sec/ansible-collection-hardening?utm_source=chatgpt.com)|

## n8n

The lab bootstraps its n8n instance automatically. A short‑lived
`n8n-bootstrap` container runs `initial_admin_setup.sh` before the main
service starts. The script resets user management once and uses
`N8N_ADMIN_EMAIL` and `N8N_ADMIN_PASSWORD` from the env file to create the
global owner account. It marks the database so this runs only once. If the
bootstrap fails the stack still starts but no owner will exist.
## RAGFlow

RAGFlow runs behind an internal nginx with Traefik handling the public endpoint.
User sign‑up is disabled by default (`REGISTER_ENABLED=0`).
On container startup `create_admin.py` ensures the admin account defined via
`RAGFLOW_ADMIN_EMAIL` and `RAGFLOW_ADMIN_PASSWORD` exists and belongs to the
default tenant. Visit `https://ragflow.${TRAEFIK_DOMAIN}` to access the UI.

Tune registration behaviour or credentials in `.env` or the corresponding
Ansible defaults. RAGFlow talks to MySQL, MinIO and Valkey using the variables in
the env‑file (`MINIO_USER`, `MINIO_PASSWORD`, `REDIS_HOST`, …).

If `LLM_CHAT_MODEL` points to a model your provider does not authorise, the
admin bootstrap may fail. Before launching the stack set `LLM_FACTORY` and
`LLM_CHAT_MODEL` to a locally served model (for example via Ollama) or leave
them blank so RAGFlow uses its internal default.

The default language model backend is controlled via the `user_default_llm`
block in `service_conf.yaml`. Override values such as `LLM_FACTORY`,
`LLM_API_KEY` or `LLM_CHAT_MODEL` in your `.env` to point RAGFlow at a
different provider or model.

---

## After cloning – quick checklist

1. **Add hosts**: copy `ansible/inventory/hosts.yaml.template` → `hosts.yaml`, fill IP/FQDN.

2. **Define users**: edit `l3d_users__local_users` with `pubkeys` and `admin: true`.

3. **Secret variables**: set strong passwords in `.env` and defaults file.

4. _(Optional)_ Pin Docker/Compose versions for reproducibility.

5. Run `task venv:init` once, then `task ansible_full` – enjoy your hardened AI lab!
