# Pocket-Lab 🧪

**Pocket‑Lab** provisions a full‑stack, self‑hosted AI laboratory on any fresh Linux host.\
Everything – from host hardening over reverse‑proxy, observability, vector and relational stores up to LLM tooling is bootstrapped with repeatable automation.

--- 

**Contents**

- [Pocket-Lab 🧪](#pocket-lab-)
  - [Stack overview](#stack-overview)
  - [Key features](#key-features)
  - [Repository map](#repository-map)
  - [Requirements](#requirements)
  - [Quick start (Ansible path) 🚀](#quick-start-ansible-path-)
    - [Developer workflow (Taskfile) 🛠️](#developer-workflow-taskfile-️)
    - [Plain Docker Compose 🐳](#plain-dockercompose-)
  - [Services \& Configuration Reference 📝](#services--configuration-reference-)
    - [Traefik Basic‑Auth 🔒](#traefik-basicauth-)
    - [n8n 🔁](#n8n-)
    - [Open WebUI 🌐](#open-webui-)
    - [RAGFlow 📚](#ragflow-)
    - [Ollama 🦙](#ollama-)
    - [MinIO ☁️](#minio-️)
    - [Secure-access layer - Tailscale 🔐](#secure-access-layer---tailscale-)
    - [MySQL 🐬](#mysql-)
    - [Infinity ♾️](#infinity-️)
    - [Valkey (Redis drop-in) 🐏](#valkey-redis-drop-in-)
    - [Elasticsearch 🔍](#elasticsearch-)
    - [Portainer 🛠️](#portainer-️)
    - [Prometheus 📊](#prometheus-)
    - [Grafana 📈](#grafana-)
    - [Loki 📜](#loki-)
    - [SMTP relay ✉️](#smtp-relay-️)
    - [Typical workflows](#typical-workflows)
    - [Provisioning with Ansible](#provisioning-with-ansible)
      - [Task catalogue](#task-catalogue)
      - [Variables you will likely change](#variables-you-will-likely-change)
      - [Role overview](#role-overview)
    - [Table of all Variables](#table-of-all-variables)
    - [MySQL 🐬](#mysql--1)
    - [Infinity ♾️](#infinity-️-1)
    - [Valkey (Redis drop-in) 🐏](#valkey-redis-drop-in--1)
    - [Elasticsearch 🔍](#elasticsearch--1)
    - [Portainer 🛠️](#portainer-️-1)
    - [Prometheus 📊](#prometheus--1)
    - [Grafana 📈](#grafana--1)
    - [Loki 📜](#loki--1)
    - [SMTP relay ✉️](#smtp-relay-️-1)
  - [Contributing \& CI hints](#contributing--ci-hints)


---

## Stack overview

| Layer           | Component(s)                              |
| --------------- | ----------------------------------------- |
| Reverse‑proxy   | Traefik                                   |
| LLMs & chat     | Ollama, Open WebUI                        |
| Workflow        | n8n                                       |
| Retrieval & RAG | RAGFlow, Elasticsearch, Infinity          |
| Data plane      | MySQL, MinIO (S3), Valkey (Redis)         |
| Observability   | Prometheus + Node‑Exporter, Grafana, Loki |
| Secure access   | Tailscale subnet router                   |
| Dev UX          | Portainer                                 |

---

## Key features

- ✨ **One code base – three ways to deploy**

  1. **Ansible** – run `task ansible_full` and get a hardened host plus a running stack.
  2. **Go Task + Docker Compose** – developer‑friendly shortcuts (`task compose‑*`) that mirror the authoritative stack assets into `./docker/`.
  3. **Plain Docker Compose** – copy `ansible/roles/pocket_lab/files/compose.yaml` next to a hand‑crafted `.env` and run `docker compose up -d`.

- ✨ **First run bootstrap for upstream projects without automated admin account creation**\
  Short‑lived helper containers/scripts create the very first administrator and disable sign‑up where the upstream image offers neither:


  | Service    | Bootstrap helper                          | Variables                                           |
  | ---------- | ----------------------------------------- | --------------------------------------------------- |
  | n8n        | `n8n-bootstrap → initial_admin_setup.sh`  | `N8N_ADMIN_EMAIL`, `N8N_ADMIN_PASSWORD`             |
  | Open WebUI | `openwebui-bootstrap → create_admin.py`   | `OPENWEBUI_ADMIN_EMAIL`, `OPENWEBUI_ADMIN_PASSWORD` |
  | RAGFlow    | `ragflow/entrypoint.sh → create_admin.py` | `RAGFLOW_ADMIN_EMAIL`, `RAGFLOW_ADMIN_PASSWORD`     |

- 🔐 **Secrets by design**
  All credentials and tunables live in a single `.env` file.
  Ansible renders it from `templates/.env.j2` – **or** – developers copy `.env.template` manually.
  A small guard script `scripts/sync_env.py` keeps both sources of truth in sync and regenerates `docs/ENVIRONMENT.md`.

- 🛡️ **Secure defaults**
  Traefik terminates TLS (Let’s Encrypt DNS‑01 via Cloudflare) and injects a Basic‑Auth middleware for every UI unless the upstream project has its own authentication.\
  OS and SSH are hardened via the Dev‑Sec hardening collection.

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
| `docs/ENVIRONMENT.md` | Autogenerated env reference                               |
| `scripts/sync_env.py` | Detect drift between `.env.template` and Ansible template |

## Requirements

- Linux host with [Docker](https://docs.docker.com/get-docker/) and
  [docker compose](https://docs.docker.com/compose/) installed
- Python 3.11 or newer
- Optional: [Go Task](https://taskfile.dev) for the helper commands


---

## Quick start (Ansible path) 🚀

Follow the five commands below in order. Each snippet is **copy‑safe** (no inline comments):

1. **Clone the repository and enter it**

   ```bash
   git clone https://github.com/your-org/ellebam-pocket-lab.git
   cd ellebam-pocket-lab
   ```

2. **Edit the [main configuration file](./ansible/roles/pocket_lab/defaults/main.yaml) (`main.yaml`)  and fill in all passwords / secrets**

   ```bash
   vim ./ansible/roles/pocket_lab/defaults/main.yaml
   ```
   Alternatively you can also a dedicated `group_vars/<group>.yaml` or `host_vars/<host>.yaml` file.

3. **Add your target server to the inventory** (edit `ansible/inventory/hosts.yaml` with its IP/FQDN; ensure your SSH user can run `sudo` without a password)

   ```bash
   cp ansible/inventory/hosts.yaml.template ansible/inventory/hosts.yaml
   ```

4. **Set up the Python virtual‑env (installs Ansible + collections)**

   ```bash
   task venv:init
   ```

5. **Provision the lab – detect → bootstrap → harden → deploy**

   ```bash
   task ansible_full
   ```

### Developer workflow (Taskfile) 🛠️

1. **Mirror stack assets and generate the `.env` file**

   ```bash
   task compose-prepare
   ```

2. **Edit and set strong passwords, API keys and any secrets marked**

   ```bash
   vim docker/.env
   ```

3. **Launch the stack locally**

   ```bash
   cd docker
   docker compose up -d
   ```

### Plain Docker Compose 🐳

1. **Copy the compose spec and create**

   ```bash
   cp ansible/roles/pocket_lab/files/compose.yaml .
   cp .env.template .env
   ```

2. **Edit the `.env` file and replace every default credential with a secure value before starting the stack.**
   
   ```bash
   vim .env
   ```

3. **Bring up the stack**

   ```bash
   docker compose up -d
   ```

> **Note:** this manual path skips user management and host hardening – use for quick experiments only.

---

## Services & Configuration Reference 📝

### Traefik Basic‑Auth 🔒

Pocket‑Lab ships with a **demo** hash (`admin / admin`) so the dashboards are reachable right away.\
Generate your own credentials with:

```bash
htpasswd -nbB admin 'myStrongP@ssw0rd'
```

- Copy the full `user:$2y$…` string **exactly as printed**.
- In all deployment modes place it in **single quotes** to preserve the `$` signs:
  - **Docker Compose / Taskfile** → in `docker/.env`:
    ```env
    TRAEFIK_BASIC_AUTH='admin:$2y$…'
    ```
  - **Ansible** → set `basic_auth: 'admin:$2y$…'` in either
    - `ansible/roles/pocket_lab/defaults/main.yaml`, **or**
    - a dedicated `group_vars/<group>.yaml` or `host_vars/<host>.yaml` file.

---

  
### n8n 🔁

The lab bootstraps its n8n instance automatically. A short‑lived
`n8n-bootstrap` container runs `initial_admin_setup.sh` before the main
service starts. The script resets user management once and uses
`N8N_ADMIN_EMAIL` and `N8N_ADMIN_PASSWORD` from the env file to create the
global owner account. It marks the database so this runs only once. If the
bootstrap fails the stack still starts but no owner will exist.

---

### Open WebUI 🌐

The `openwebui-bootstrap` container executes `create_admin.py` once before
the actual service comes up. It creates or updates the administrator defined
via `OPENWEBUI_ADMIN_EMAIL` and `OPENWEBUI_ADMIN_PASSWORD`. Registration
behaviour is controlled through `ENABLE_SIGNUP`, the default role via
`DEFAULT_USER_ROLE` and configuration persistence via
`ENABLE_PERSISTENT_CONFIG`.

---

### RAGFlow 📚

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


### Ollama 🦙

Ollama runs the local language models used by the lab. The service exposes the
standard API at `https://ollama.${TRAEFIK_DOMAIN}` and acts as the default LLM
backend for Open WebUI and RAGFlow. On first start a short-lived
`ollama-bootstrap` companion downloads all models listed in `OLLAMA_MODELS` so
they are available locally. The variable accepts a space-separated list and
defaults to `llama3.2 bge-m3`. The helper exits successfully if all models are
already present so it is safe to rerun.

---

### MinIO ☁️

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
    
- `ansible/roles/ensure_conn_user/defaults/main.yaml`


---


### Secure-access layer - Tailscale 🔐

Pocket‑Lab ships with a lightweight **[Tailscale](https://tailscale.com)** container that runs in host‑network mode, advertises the Docker bridge subnet **and** enables [Tailscale SSH](https://tailscale.com/kb/1191/tailscale-ssh/).

1. **Create an Auth Key** in the Tailscale admin console → _Keys_ → “Reusable, pre‑authorized”.  
2. Put it in `.env` as `TS_AUTHKEY`.  
3. (Optional) change `DOCKER_BRIDGE_SUBNET` if you run multiple labs or the default ‑ `172.20.0.0/16` – collides with an existing network.

```env
# .env (excerpt)
TS_AUTHKEY   = tskey-auth-ABC123...
DOCKER_BRIDGE_SUBNET = 172.20.0.0/16
```

| Variable | Default | Purpose |
|----------|---------|---------|
| `TS_AUTHKEY` |   | Auth key created in the TS admin console |
| `DOCKER_BRIDGE_SUBNET` | `172.20.0.0/16` | CIDR routed into the tailnet |

_No other Tailscale options need tweaking – advanced users can set `TS_EXTRA_ARGS` in `docker-compose.yaml`._


When the stack comes up the **tailscale** service automatically:
* joins your tailnet and appears as _pocket‑lab.tail<NNNN>.ts.net_
* advertises the subnet defined by `DOCKER_BRIDGE_SUBNET`
* enables Tailscale SSH on the host and every container (via `--ssh`)

### MySQL 🐬

RAGFlow stores its relational data in a standalone MySQL container. Set
`MYSQL_ROOT_PASSWORD` for the root account and adjust `MYSQL_DATABASE`
to change the default schema. `MYSQL_PORT` and `MYSQL_HOST` control the
exposed port and container name.

---

### Infinity ♾️

Infinity provides the vector index used by RAGFlow. The included
`infinity_conf.toml` configures storage paths while the ports are
customisable through `INFINITY_THRIFT_PORT`, `INFINITY_HTTP_PORT` and
`INFINITY_PSQL_PORT`. The service registers under
`INFINITY_HOST`.

---

### Valkey (Redis drop-in) 🐏

Valkey offers a Redis-compatible key–value store. Protect it with
`REDIS_PASSWORD` and change the image or port via `REDIS_VERSION` and
`REDIS_PORT`.

---

### Elasticsearch 🔍

Elasticsearch indexes all documents for RAGFlow. Modify
`ES_PASSWORD` for the elastic user and `ES_PORT` for the HTTP API.
`ES_HOST` chooses the hostname while `MEM_LIMIT` limits container
memory usage.

---

### Portainer 🛠️

Portainer exposes a small Docker dashboard at
`https://portainer.${TRAEFIK_DOMAIN}` protected by Traefik basic-auth.
Update `PORTAINER_VERSION` or change the UI port with `PORTAINER_PORT`.

---

### Prometheus 📊

Prometheus collects metrics from node-exporter and the stack. The image
tag is set via `PROMETHEUS_VERSION`. Additional scrape targets can be
defined in `prometheus/prometheus.yaml`.

---

### Grafana 📈

Grafana visualises metrics at `https://grafana.${TRAEFIK_DOMAIN}`.
Initial credentials come from `GRAFANA_ADMIN_USER` and
`GRAFANA_ADMIN_PASSWORD`. Use `GRAFANA_VERSION` to upgrade.

---

### Loki 📜

Loki stores container logs that Grafana can query. Change
`LOKI_VERSION` if you need a different release.

---

### SMTP relay ✉️

A lightweight Postfix relay lets services send mail. Set `SMTP_IMAGE`
to choose the container, `SMTP_PORT` for the listening port and
`SMTP_SSL` to toggle TLS. The hostname is derived from `SMTP_HOST`.

---
### Typical workflows
```bash
# list all lab containers – works from any device in the tailnet
tailscale status

# SSH into the host (root)
tailscale ssh root@pocket-lab

# SSH into a container by name
tailscale ssh root@mysql

# Expose a local dev port to the tailnet for 30 min
tailscale funnel 4040 --timeout 30m
```
---

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

#### Task catalogue

| Command | What it does |
| --- | --- |
| `task ansible_detect` | Cache a working SSH login |
| `task ansible_bootstrap` | Create users only |
| `task ansible_harden` | Apply DevSec OS and SSH hardening |
| `task ansible_deploy` | Copy compose files and launch the stack |
| `task ansible_full` | Full pipeline |
| `task docker-*` | Shortcuts for Compose up/down/logs |

---

#### Variables you will likely change

| Variable | Default | Notes |
| --- | --- | --- |
| `stack_domain`, `stack_email` | `ai.lab.example.com`, `admin@example.com` | Traefik host and ACME mail |
| `basic_auth` | bcrypt hash | Use `htpasswd -nbB` to generate |
| `ts_authkey` | – | Tailscale subnet router auth key |
| `docker_bridge_subnet` | `172.20.0.0/16` | Subnet advertised to the tailnet |
| `n8n_admin_email`, `n8n_admin_password` | `admin@example.com` / `changeme` | n8n owner account |
| `openwebui_admin_email`, `openwebui_admin_password` | `admin@example.com` / `changeme` | Open WebUI admin |
| `es_password`, `mysql_password`, `minio_root_password`, … | `changeme` | Service credentials |
| `compose_repo` | `/opt/pocket_lab` | Where compose files are deployed |
| `mem_limit` | `4g` | Memory limit for ES and Infinity |
| everything in `.env.template` | – | Mirrors compose environment |

#### Role overview

|Role|Purpose|
|---|---|
|**ensure_conn_user**|Probe `root`, inventory user, first in `l3d_users__local_users`; cache winner for 24 h so every play can rely on `hostvars[host].conn_user`.|
|**l3d.users.user / .admin**|Create regular + sudo users with SSH keys. [Ansible Galaxy](https://galaxy.ansible.com/ui/repo/published/l3d/users/content/role/user/?utm_source=chatgpt.com)|
|**devsec.hardening.os_hardening / ssh_hardening**|CIS‑style OS tweaks, secure `sshd_config`. [GitHub](https://github.com/dev-sec/ansible-collection-hardening?utm_source=chatgpt.com)|

---

### Table of all Variables

| Variable                             |  Default             value                                           |  Service      |                                           Description                                       |                       Comments                                 |
| ------------------------------------ | -------------------------------------------------------------------- | ------------- | ------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
### MySQL 🐬

RAGFlow stores its relational data in a standalone MySQL container. Set
`MYSQL_ROOT_PASSWORD` for the root account and adjust `MYSQL_DATABASE`
to change the default schema. `MYSQL_PORT` and `MYSQL_HOST` control the
exposed port and container name.

---

### Infinity ♾️

Infinity provides the vector index used by RAGFlow. The included
`infinity_conf.toml` configures storage paths while the ports are
customisable through `INFINITY_THRIFT_PORT`, `INFINITY_HTTP_PORT` and
`INFINITY_PSQL_PORT`. The service registers under
`INFINITY_HOST`.

---

### Valkey (Redis drop-in) 🐏

Valkey offers a Redis-compatible key–value store. Protect it with
`REDIS_PASSWORD` and change the image or port via `REDIS_VERSION` and
`REDIS_PORT`.

---

### Elasticsearch 🔍

Elasticsearch indexes all documents for RAGFlow. Modify
`ES_PASSWORD` for the elastic user and `ES_PORT` for the HTTP API.
`ES_HOST` chooses the hostname while `MEM_LIMIT` limits container
memory usage.

---

### Portainer 🛠️

Portainer exposes a small Docker dashboard at
`https://portainer.${TRAEFIK_DOMAIN}` protected by Traefik basic-auth.
Update `PORTAINER_VERSION` or change the UI port with `PORTAINER_PORT`.

---

### Prometheus 📊

Prometheus collects metrics from node-exporter and the stack. The image
tag is set via `PROMETHEUS_VERSION`. Additional scrape targets can be
defined in `prometheus/prometheus.yaml`.

---

### Grafana 📈

Grafana visualises metrics at `https://grafana.${TRAEFIK_DOMAIN}`.
Initial credentials come from `GRAFANA_ADMIN_USER` and
`GRAFANA_ADMIN_PASSWORD`. Use `GRAFANA_VERSION` to upgrade.

---

### Loki 📜

Loki stores container logs that Grafana can query. Change
`LOKI_VERSION` if you need a different release.

---

### SMTP relay ✉️

A lightweight Postfix relay lets services send mail. Set `SMTP_IMAGE`
to choose the container, `SMTP_PORT` for the listening port and
`SMTP_SSL` to toggle TLS. The hostname is derived from `SMTP_HOST`.

---
| Variable         |  Default value                                           |  Service      |                                           Description                                       |                       Comments                                 |
| ------------------------------------ | -------------------------------------------------------------------- | ------------- | ------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| `TRAEFIK_BASIC_AUTH`                 | `admin:$2y$12$Kz0IUpZjbNkS7N0S2E5qe <br>OeJ8V4aH.E4W2KIiMzFxLpy0X58F3Riq` | Traefik       | htpasswd‑style `user:hash`.  Demo credentials = **admin / admin** – replace for production. | user\:hash used by Traefik basic-auth middleware for most UIs. |
| `TRAEFIK_DOMAIN`                     | `ai.lab.example.com`                                                 | Traefik       | Apex domain under which all sub‑services are published.                                     |                                                                |
| `TRAEFIK_LE_EMAIL`                   | `admin@example.com`                                                  | Traefik       | Contact e‑mail for Let’s Encrypt.                                                           |                                                                |
| `TRAEFIK_VERSION`                    | `3.4.1`                                                              | Traefik       | Traefik docker image tag.                                                                   |                                                                |
| `ES_VERSION`                         | `8.13.4`                                                             | Elasticsearch | Elasticsearch image tag.                                                                    |                                                                |
| `GRAFANA_VERSION`                    | `10.4.3`                                                             | Misc          | Grafana image tag.                                                                          |                                                                |
| `INFINITY_VERSION`                   | `v0.6.0-dev3`                                                        | Infinity      | Infinity vector database image tag.                                                         |                                                                |
| `LOKI_VERSION`                       | `3.0.0`                                                              | Misc          | Grafana Loki log aggregator version.                                                        |                                                                |
| `MINIO_VERSION`                      | `RELEASE.2023-12-20T01-00-02Z`                                       | MinIO         | MinIO object storage version.                                                               |                                                                |
| `MYSQL_VERSION`                      | `8.0.39`                                                             | MySQL         | MySQL database version.                                                                     |                                                                |
| `N8N_VERSION`                        | `1.50.0`                                                             | n8n           | n8n automation tool version.                                                                |                                                                |
| `NODE_EXPORTER_VERSION`              | `v1.9.1`                                                             | Misc          | Prometheus node exporter version.                                                           |                                                                |
| `OLLAMA_VERSION`                     | `0.1.30`                                                             | Misc          | Ollama model server version.                                                                |                                                                |
| `OLLAMA_MODELS`                      | `llama3.2 bge-m3`                                                    | Ollama        | Models preloaded by `ollama-bootstrap`                                                      |                                                                |
| `OPENWEBUI_VERSION`                  | `0.6.9`                                                              | Open WebUI    | Open WebUI image tag.                                                                       |                                                                |
| `OPENWEBUI_PORT`                     | `8080`                                                               | Open WebUI    | Internal UI port inside container.                                                          |                                                                |
| `PORTAINER_VERSION`                  | `2.20.3`                                                             | Misc          | Portainer version.                                                                          |                                                                |
| `GRAFANA_ADMIN_PASSWORD`             | `admin`                                                              | Misc          | Initial Grafana admin password.                                                             |                                                                |
| `GRAFANA_ADMIN_USER`                 | `admin`                                                              | Misc          | Initial Grafana admin user.                                                                 |                                                                |
| `SMTP_HOST`                          | `smtp`                                                               | SMTP relay    | Container name / hostname for SMTP relay.                                                   |                                                                |
| `SMTP_PORT`                          | `25`                                                                 | SMTP relay    | Port the SMTP relay listens on.                                                             |                                                                |
| `SMTP_SSL`                           | `false`                                                              | SMTP relay    | Enable STARTTLS (true/false).                                                               |                                                                |
| `OPENWEBUI_ADMIN_EMAIL`              | `admin@example.com`                                                  | Open WebUI    | Bootstrapped Open WebUI admin account.                                                      |                                                                |
| `OPENWEBUI_ADMIN_PASSWORD`           | `changeme`                                                           | Open WebUI    | Password for Open WebUI admin.                                                              |                                                                |
| `OPENWEBUI_ENABLE_PERSISTENT_CONFIG` | `true`                                                               | Open WebUI    | Keep configuration across container restarts.                                               |                                                                |
| `OPENWEBUI_ENABLE_SIGNUP`            | `false`                                                              | Open WebUI    | Allow self‑registration (true/false).                                                       |                                                                |
| `OPENWEBUI_DEFAULT_USER_ROLE`        | `pending`                                                            | Open WebUI    | Role newly signed‑up users get.                                                             |                                                                |
| `N8N_BASIC_AUTH_ACTIVE`              | `false`                                                              | n8n           | Enable n8n basic auth before the UI loads.                                                  |                                                                |
| `N8N_USER_MANAGEMENT_DISABLED`       | `true`                                                               | n8n           | Disable n8n built‑in sign‑up pages.                                                         |                                                                |
| `N8N_ADMIN_EMAIL`                    | `admin@example.com`                                                  | n8n           | n8n owner e‑mail.                                                                           |                                                                |
| `N8N_EMAIL_MODE`                     | `smtp`                                                               | n8n           | E‑mail mode for n8n notifications.                                                          |                                                                |
| `N8N_SMTP_HOST`                      | `smtp`                                                               | n8n           | SMTP relay host for n8n e‑mails.                                                            |                                                                |
| `N8N_SMTP_PORT`                      | `25`                                                                 | n8n           | SMTP relay port.                                                                            |                                                                |
| `N8N_SMTP_SSL`                       | `false`                                                              | n8n           | Use TLS for SMTP.                                                                           |                                                                |
| `N8N_SMTP_SENDER`                    | `"n8n <admin@example.com>"`                                          | n8n           | “From:” address used in n8n mails.                                                          |                                                                |
| `N8N_ADMIN_PASSWORD`                 | `changeme`                                                           | n8n           | n8n owner password.                                                                         |                                                                |
| `N8N_PERSONALIZATION_ENABLED`        | `false`                                                              | n8n           | Share anonymous telemetry (false recommended).                                              |                                                                |
| `DOC_ENGINE`                         | `elasticsearch`                                                      | RAGFlow       | Which backend vector/semantic engine RAGFlow uses.                                          |                                                                |
| `ES_HOST`                            | `es01`                                                               | Elasticsearch | Elasticsearch host for RAGFlow.                                                             |                                                                |
| `ES_PASSWORD`                        | `changeme`                                                           | Elasticsearch | Elasticsearch super‑user password.                                                          |                                                                |
| `ES_PORT`                            | `9200`                                                               | Elasticsearch | Elasticsearch HTTP port.                                                                    |                                                                |
| `HF_ENDPOINT`                        | `https://huggingface.co`                                             | RAGFlow       | HuggingFace API base‑URL.                                                                   |                                                                |
| `INFINITY_HTTP_PORT`                 | `23820`                                                              | Infinity      | Infinity REST API port.                                                                     |                                                                |
| `INFINITY_HOST`                      | `infinity`                                                           | Infinity      | Infinity host name.                                                                         |                                                                |
| `INFINITY_PSQL_PORT`                 | `15432`                                                              | Infinity      | Infinity Postgres compatibility port.                                                       |                                                                |
| `INFINITY_THRIFT_PORT`               | `23817`                                                              | Infinity      | Infinity Thrift RPC port.                                                                   |                                                                |
| `MACOS`                              | `false`                                                              | Global        | Set true when building on MacOS (disables some optimisations).                              |                                                                |
| `MYSQL_DATABASE`                     | `pocket_lab`                                                         | MySQL         | MySQL schema for RAGFlow.                                                                   |                                                                |
| `MYSQL_HOST`                         | `mysql`                                                              | MySQL         | MySQL host.                                                                                 |                                                                |
| `MYSQL_PORT`                         | `3306`                                                               | MySQL         | MySQL TCP port.                                                                             |                                                                |
| `MYSQL_ROOT_HOST`                    | `%`                                                                  | MySQL         | Allowed root origin hosts.                                                                  |                                                                |
| `MYSQL_ROOT_PASSWORD`                | `changeme`                                                           | MySQL         | MySQL root password.                                                                        |                                                                |
| `MINIO_CONSOLE_PORT`                 | `9001`                                                               | MinIO         | MinIO web console port.                                                                     |                                                                |
| `MINIO_PORT`                         | `9000`                                                               | MinIO         | MinIO S3 API port.                                                                          |                                                                |
| `MINIO_ROOT_PASSWORD`                | `minioadmin`                                                         | MinIO         | MinIO root password.                                                                        |                                                                |
| `MINIO_ROOT_USER`                    | `minioadmin`                                                         | MinIO         | MinIO root user.                                                                            |                                                                |
| `REDIS_HOST`                         | `redis`                                                              | Valkey        | Valkey/Redis host.                                                                          |                                                                |
| `REDIS_PASSWORD`                     | `changeme`                                                           | Valkey        | Valkey password.                                                                            |                                                                |
| `REDIS_PORT`                         | `6379`                                                               | Valkey        | Valkey port.                                                                                |                                                                |
| `REDIS_VERSION`                      | `8.1.0`                                                              | Valkey        | Valkey image tag.                                                                           |                                                                |
| `RAGFLOW_ADMIN_EMAIL`                | `admin@ragflow.io`                                                   | RAGFlow       | Bootstrapped RAGFlow admin account.                                                         |                                                                |
| `RAGFLOW_ADMIN_PASSWORD`             | `changeme`                                                           | RAGFlow       | RAGFlow admin password.                                                                     |                                                                |
| `RAGFLOW_EXTRA_PORTS`                | `9382`                                                               | RAGFlow       | Additional exposed ports (MCP).                                                             |                                                                |
| `RAGFLOW_HISTORY_DIR`                | `./ragflow/history_data_agent`                                       | RAGFlow       | Host path for chat history.                                                                 |                                                                |
| `RAGFLOW_LOG_DIR`                    | `./ragflow/ragflow-logs`                                             | RAGFlow       | Host path for RAGFlow logs.                                                                 |                                                                |
| `RAGFLOW_NGINX_CONF_DIR`             | \`\`                                                                 | RAGFlow       | Optional mount to inject custom nginx.conf.                                                 |                                                                |
| `RAGFLOW_VERSION`                    | `v0.18.0`                                                            | RAGFlow       | RAGFlow image tag.                                                                          |                                                                |
| `REGISTER_ENABLED`                   | `0`                                                                  | RAGFlow       | Allow public sign‑up in RAGFlow.                                                            |                                                                |
| `SVR_HTTP_PORT`                      | `9380`                                                               | RAGFlow       | RAGFlow backend HTTP port.                                                                  |                                                                |
| `TS_AUTHKEY`                         | -                                                                    | Tailscale     | Authentication key used to connect to your personal Tailscale tenant                        |                                                                |
| `DOCKER_BRIDGE_SUBNET`               | `172.20.0.0/16`                                                      | Tailscale     | Definition of the Subnet used by the Docker Compose Setup. This variable is used by Tailscale to determine to which subnet to route private traffic to        | Variable has implication for the complete setup since all IPs of the services are dependent on it. It is currently only used by Tailscale for actively.                                                          |

For deep‑links and automatic change‑tracking the same table is regenerated in `docs/ENVIRONMENT.md` whenever `scripts/sync_env.py --docs` is executed.

---

## Contributing & CI hints

- Use two‑space YAML indentation and keep block‑comment separators.
- Run a quick syntax check before committing:\
  `ansible-playbook --syntax-check ansible/site.yaml && docker compose -f ansible/roles/pocket_lab/files/compose.yaml config`
- Keep this README and `docs/ENVIRONMENT.md` up‑to‑date when touching variables or behaviour.
