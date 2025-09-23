# Pocket-Lab 🧪

**Pocket‑Lab** provisions a full‑stack, self‑hosted AI laboratory on any fresh Linux host.\
Everything – from reverse‑proxy, observability, vector and relational stores up to LLM tooling is bootstrapped with repeatable automation.

[<img src="./docs/assets/pocket_lab.png" style="margin: auto; width: 75%"/>](./docs/assets/pocket_lab.png)



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
    - [Stirling PDF 📄](#stirling-pdf-)
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
    - [Web search (Open WebUI + SearXNG) 🔎](#web-search-open-webui--searxng-)
    - [No-Code Architects Toolkit 🧰](#no-code-architects-toolkit-)
    - [Typical workflows](#typical-workflows)
    - [Provisioning with Ansible](#provisioning-with-ansible)
      - [First-time setup (day-0 guide)](#first-time-setup-day-0-guide)
    - [Private / no-public-IP deployments (localhost or tailnet)](#private--no-public-ip-deployments-localhost-or-tailnet)
      - [Task catalogue](#task-catalogue)
      - [Variables you will likely change](#variables-you-will-likely-change)
      - [Role overview](#role-overview)
    - [Table of all Variables](#table-of-all-variables)
  - [Contributing \& CI hints](#contributing--ci-hints)


---

## Stack overview

| Layer           | Component(s)                              |
| --------------- | ----------------------------------------- |
| Reverse‑proxy   | Traefik                                   |
| LLMs & chat     | Ollama, Open WebUI                        |
| Workflow        | n8n                                       |
| Document tools  | Stirling PDF                              |
| Retrieval & RAG | RAGFlow, Elasticsearch, Infinity          |
| Data plane      | MySQL, MinIO (S3), Valkey (Redis)         |
| Observability   | Prometheus + Node‑Exporter, Grafana, Loki |
| Secure access   | Tailscale subnet router                   |
| Dev UX          | Portainer                                 |

---

## Key features

- ✨ **One code base – three ways to deploy**

  1. **Ansible** – run `task ansible_full` to install Docker and start the stack.
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

## Repository map

| Path | Purpose |
| --- | --- |
| `Taskfile.yaml` | Developer shortcuts for Go Task and Docker Compose |
| `.env.template` | Copy to `.env` to provide environment variables |
| `ansible/` | Inventory, plays, roles and Galaxy requirements |
| `ansible/plays/00-deploy.yaml` | Install Docker and deploy the stack |
| `ansible/roles/pocket_lab` | Docker stack logic and templates |
| `ansible/roles/pocket_lab/files/compose.yaml` | The Docker Compose specification |
| `docs/ENVIRONMENT.md` | Autogenerated env reference |
| `scripts/sync_env.py` | Detect drift between `.env.template` and Ansible template |

## Requirements

- Linux host with [Docker](https://docs.docker.com/get-docker/) and
  [docker compose](https://docs.docker.com/compose/) installed
- Python 3.11 or newer
- Optional: [Go Task](https://taskfile.dev) for the helper commands


---

## Quick start (Ansible path) 🚀

1. **Add your target server to the inventory**

   ```bash
   cp ansible/inventory/hosts.yaml.template ansible/inventory/hosts.yaml
   ```

2. **Set up the Python virtual‑env (installs Ansible + collections)**

   ```bash
   task venv:init
   ```

3. **Provision the lab**

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

> **Note:** this manual path skips Ansible – use for quick experiments only.

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

> **Auth exceptions:** UIs that already have their own authentication (e.g. **Grafana**, Open WebUI) are **not** protected by Traefik Basic-Auth. Grafana remains reachable without the middleware and uses its own login page.

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

n8n is served through Traefik at `https://n8n.${TRAEFIK_DOMAIN}`. The env
file wires this domain into `WEBHOOK_URL`, `N8N_HOST` and `N8N_PROTOCOL`
(optionally `N8N_EDITOR_BASE_URL`) so OAuth callbacks use the correct HTTPS
origin.

---

### Open WebUI 🌐

The `openwebui-bootstrap` container executes `create_admin.py` once before
the actual service comes up. It creates or updates the administrator defined
via `OPENWEBUI_ADMIN_EMAIL` and `OPENWEBUI_ADMIN_PASSWORD`. Registration
behaviour is controlled through `ENABLE_SIGNUP`, the default role via
`DEFAULT_USER_ROLE` and configuration persistence via
`ENABLE_PERSISTENT_CONFIG`.

- Open WebUI is wired to Ollama via `OLLAMA_BASE_URL` (defaults to internal `http://ollama:11434`), `OFFLINE_MODE=true` by default (no version pings/online features), but Web Search is enabled out-of-the-box and points to the bundled SearXNG instance.

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
### Stirling PDF 📄

Stirling PDF offers browser-based PDF manipulation at `https://pdf.${TRAEFIK_DOMAIN}`. Its own login is disabled by default (`STIRLING_PDF_ENABLE_LOGIN=false`) and access is protected through Traefik's Basic-Auth middleware. Set `STIRLING_PDF_ENABLE_LOGIN=true` to enable the application's sign-in page. Configuration and data persist in dedicated volumes.

---

### Ollama 🦙

Ollama runs the local language models used by the lab. The service exposes the
standard API at `https://ollama.${TRAEFIK_DOMAIN}` and acts as the default LLM
backend for Open WebUI and RAGFlow. On first start a short-lived
`ollama-bootstrap` companion downloads all models listed in `OLLAMA_PULL_MODELS` so
they are available locally. The variable accepts a space-separated list and
defaults to `llama3.1:8b deepseek-r1:7b qwen2.5-coder:7b bge-m3`. The helper exits successfully if all models are
already present so it is safe to rerun.

- Default pre-pulled models on first run: `llama3.1:8b` (general), `deepseek-r1:7b` (reasoning), `qwen2.5-coder:7b` (coding), plus `bge-m3` embeddings.

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

- `ansible/roles/pocket_lab/defaults/main.yaml`


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
### Web search (Open WebUI + SearXNG) 🔎

Pocket-Lab ships a private [SearXNG](https://docs.searxng.org) instance (internal-only) and wires it into **Open WebUI** as the default web search backend. JSON output is enabled and rate limiting is disabled for private use.

**Defaults (override in `.env` / Ansible vars):**

```env
# endpoints & privacy
WEBUI_URL=https://chat.<your-domain>
OFFLINE_MODE=true
ENABLE_VERSION_UPDATE_CHECK=false
OLLAMA_BASE_URL=http://ollama:11434

# web search
ENABLE_WEB_SEARCH=true
WEB_SEARCH_ENGINE=searxng
SEARXNG_QUERY_URL=http://searxng:8080/search?q=<query>&format=json
WEB_SEARCH_RESULT_COUNT=5
WEB_SEARCH_CONCURRENT_REQUESTS=2
ENABLE_SEARCH_QUERY_GENERATION=false
```

> Why SearXNG? It avoids public-instance rate limits and API blocks while keeping search local to your stack. Open WebUI discovers it through `WEB_SEARCH_ENGINE=searxng` + `SEARXNG_QUERY_URL`. See Open WebUI env config & tutorial. Also ensure SearXNG exposes JSON (`search.formats: [html, json]`). :contentReference[oaicite:2]{index=2}

### No-Code Architects Toolkit 🧰

Internal toolkit service available on the private network at `http://ncat:8080`. It targets the bundled MinIO (`http://minio:9000`) and stores data in the `pocket_lab` bucket by default. Configure it with `NCA_VERSION`, `NCA_API_KEY`, `NCA_S3_ENDPOINT`, `NCA_S3_BUCKET`, `NCA_S3_ACCESS_KEY` and `NCA_S3_SECRET_KEY`.

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
task ansible_full  # deploy the stack
```

Run `task ansible_deploy` to execute the play directly.

#### First-time setup (day-0 guide)

**You can deploy with almost all defaults.** The only values you typically *must* provide are:
* `cloudflare_api_token` (for automatic TLS via DNS-01), and/or
* `ts_authkey` (if you want private tailnet access).

For **full control** over passwords/users/ports, copy the role defaults into host-specific vars and override only what you need:
```bash
mkdir -p ansible/host_vars
cp ansible/roles/pocket_lab/defaults/main.yaml ansible/host_vars/genai-vm.yaml
# edit ansible/host_vars/genai-vm.yaml and change only the vars you care about
```
> You can also use `group_vars/<group>.yaml` if you target multiple machines.

**1) Inventory**
```bash
cp ansible/inventory/hosts.yaml.template ansible/inventory/hosts.yaml
# set ansible_host and ansible_user
```
**2) Install Ansible toolchain**
```bash
task venv:init
```
**3) Deploy**
```bash
task ansible_full
```
**4) Local/self-deploy (no SSH)**
If you run Ansible on the target itself:
```yaml
# ansible/inventory/hosts.yaml
genai_servers:
  hosts:
    localhost:
      ansible_connection: local
      ansible_python_interpreter: /usr/bin/python3
      ansible_user: root
```
Then `task ansible_full`.

**Idempotent helpers**
```bash
task ansible_check   # dry-run
task ansible_deploy  # re-run deploy play
```

### Private / no-public-IP deployments (localhost or tailnet)

You can run Pocket-Lab on a host with **no public IP** and still get HTTPS + Traefik routing.

**A) DNS-01 + /etc/hosts (recommended)**
1. Set a Cloudflare token (`CLOUDFLARE_DNS_API_TOKEN` / `cloudflare_api_token`).
2. Deploy the stack.
3. On the *client* you browse from (or on the server itself), add host entries mapping service names to the server IP (use `127.0.0.1` when browsing on the server):
```
127.0.0.1  traefik.${TRAEFIK_DOMAIN} grafana.${TRAEFIK_DOMAIN} \
           prometheus.${TRAEFIK_DOMAIN} portainer.${TRAEFIK_DOMAIN} \
           n8n.${TRAEFIK_DOMAIN} chat.${TRAEFIK_DOMAIN} \
           ragflow.${TRAEFIK_DOMAIN} minio.${TRAEFIK_DOMAIN} \
           ollama.${TRAEFIK_DOMAIN}
```
> ACME DNS-01 only checks TXT records, so you don’t need public A/AAAA records.

**B) Tailscale-only access**
1. Set `TS_AUTHKEY` / `ts_authkey` and deploy.
2. Find the host’s tailnet IP or MagicDNS name (`tailscale status` / `tailscale ip`).
3. Add `/etc/hosts` on your client mapping the same service names to that tailnet IP.

**Sanity checks**
```bash
curl -I -k -H "Host: grafana.${TRAEFIK_DOMAIN}" https://127.0.0.1
```

---

#### Task catalogue

| Command | What it does |
| --- | --- |
| `task ansible_deploy` | Install Docker and deploy the stack |
| `task ansible_full` | Same as above via `ansible/site.yaml` |
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

| Role | Purpose |
| --- | --- |
| **geerlingguy.docker** | Install Docker and Compose |
| **pocket_lab** | Deploy the Pocket-Lab stack |

---

### Table of all Variables

| Variable | Default value | Service | Description | Comments |
| --- | --- | --- | --- | --- |
| `CLOUDFLARE_DNS_API_TOKEN` | `-` | Traefik | Cloudflare token for DNS-01 ACME challenges. |  |
| `DEFAULT_MODELS` | `llama3.1:8b` | Web search | Default models offered. |  |
| `DEFAULT_PROMPT_SUGGESTIONS` | `see .env.template` | Web search | JSON array of prompt suggestions. |  |
| `DOCKER_BRIDGE_SUBNET` | `172.20.0.0/16` | Tailscale | Definition of the Subnet used by the Docker Compose Setup. This variable is used by Tailscale to determine to which subnet to route private traffic to | Variable has implication for the complete setup since all IPs of the services are dependent on it. It is currently only used by Tailscale for actively. |
| `DOC_ENGINE` | `elasticsearch` | RAGFlow | Which backend vector/semantic engine RAGFlow uses. |  |
| `ENABLE_SEARCH_QUERY_GENERATION` | `true` | Web search | Auto-generate search queries. |  |
| `ENABLE_VERSION_UPDATE_CHECK` | `false` | Open WebUI | Allow WebUI to check for updates. |  |
| `ENABLE_WEB_SEARCH` | `true` | Web search | Enable Web search feature. |  |
| `ES_HOST` | `es01` | Elasticsearch | Elasticsearch host for RAGFlow. |  |
| `ES_PASSWORD` | `changeme` | Elasticsearch | Elasticsearch super‑user password. |  |
| `ES_PORT` | `9200` | Elasticsearch | Elasticsearch HTTP port. |  |
| `ES_VERSION` | `8.13.4` | Elasticsearch | Elasticsearch image tag. |  |
| `GF_ANALYTICS_CHECK_FOR_UPDATES` | `false` | Misc | Let Grafana check for updates. |  |
| `GF_ANALYTICS_REPORTING_ENABLED` | `false` | Misc | Allow Grafana usage stats. |  |
| `GRAFANA_ADMIN_PASSWORD` | `admin` | Misc | Initial Grafana admin password. |  |
| `GRAFANA_ADMIN_USER` | `admin` | Misc | Initial Grafana admin user. |  |
| `GRAFANA_VERSION` | `10.4.3` | Misc | Grafana image tag. |  |
| `HF_ENDPOINT` | `https://huggingface.co` | RAGFlow | HuggingFace API base‑URL. |  |
| `INFINITY_HOST` | `infinity` | Infinity | Infinity host name. |  |
| `INFINITY_HTTP_PORT` | `23820` | Infinity | Infinity REST API port. |  |
| `INFINITY_PSQL_PORT` | `15432` | Infinity | Infinity Postgres compatibility port. |  |
| `INFINITY_THRIFT_PORT` | `23817` | Infinity | Infinity Thrift RPC port. |  |
| `INFINITY_VERSION` | `v0.6.0-dev3` | Infinity | Infinity vector database image tag. |  |
| `LOKI_VERSION` | `3.0.0` | Misc | Grafana Loki log aggregator version. |  |
| `MACOS` | `false` | Global | Set true when building on MacOS (disables some optimisations). |  |
| `MEM_LIMIT` | `4g` | Global | Memory limit for Elasticsearch and Infinity. |  |
| `MINIO_CONSOLE_PORT` | `9001` | MinIO | MinIO web console port. |  |
| `MINIO_PORT` | `9000` | MinIO | MinIO S3 API port. |  |
| `MINIO_ROOT_PASSWORD` | `minioadmin` | MinIO | MinIO root password. |  |
| `MINIO_ROOT_USER` | `minioadmin` | MinIO | MinIO root user. |  |
| `MINIO_VERSION` | `RELEASE.2025-04-22T22-12-26Z` | MinIO | MinIO object storage version. |  |
| `MYSQL_DATABASE` | `pocket_lab` | MySQL | MySQL schema for RAGFlow. |  |
| `MYSQL_HOST` | `mysql` | MySQL | MySQL host. |  |
| `MYSQL_PORT` | `3306` | MySQL | MySQL TCP port. |  |
| `MYSQL_ROOT_HOST` | `%` | MySQL | Allowed root origin hosts. |  |
| `MYSQL_ROOT_PASSWORD` | `changeme` | MySQL | MySQL root password. |  |
| `MYSQL_VERSION` | `8.0.39` | MySQL | MySQL database version. |  |
| `N8N_ADMIN_EMAIL` | `admin@example.com` | n8n | n8n owner e‑mail. |  |
| `N8N_ADMIN_PASSWORD` | `changeme` | n8n | n8n owner password. |  |
| `N8N_BASIC_AUTH_ACTIVE` | `false` | n8n | Enable n8n basic auth before the UI loads. |  |
| `N8N_DIAGNOSTICS_ENABLED` | `false` | n8n | Share diagnostic data. |  |
| `N8N_EDITOR_BASE_URL` | `https://n8n.ai.lab.example.com/` | n8n | Base URL for the n8n editor. |  |
| `N8N_EMAIL_MODE` | `smtp` | n8n | E‑mail mode for n8n notifications. |  |
| `N8N_HOST` | `n8n.ai.lab.example.com` | n8n | Domain used by n8n. |  |
| `N8N_PERSONALIZATION_ENABLED` | `false` | n8n | Share anonymous telemetry (false recommended). |  |
| `N8N_PROTOCOL` | `https` | n8n | Protocol for building callback URLs. |  |
| `N8N_SMTP_HOST` | `smtp` | n8n | SMTP relay host for n8n e‑mails. |  |
| `N8N_SMTP_PORT` | `25` | n8n | SMTP relay port. |  |
| `N8N_SMTP_SENDER` | `"n8n <admin@example.com>"` | n8n | “From:” address used in n8n mails. |  |
| `N8N_SMTP_SSL` | `false` | n8n | Use TLS for SMTP. |  |
| `N8N_TEMPLATES_ENABLED` | `false` | n8n | Enable community workflow templates. |  |
| `N8N_USER_MANAGEMENT_DISABLED` | `true` | n8n | Disable n8n built‑in sign‑up pages. |  |
| `N8N_VERSION` | `1.50.0` | n8n | n8n automation tool version. |  |
| `N8N_VERSION_NOTIFICATIONS_ENABLED` | `false` | n8n | Allow update notifications. |  |
| `NODE_EXPORTER_VERSION` | `v1.9.1` | Misc | Prometheus node exporter version. |  |
| `OFFLINE_MODE` | `true` | Open WebUI | Disable network access. |  |
| `OLLAMA_BASE_URL` | `http://ollama:11434` | Open WebUI | Base URL for the Ollama API. |  |
| `OLLAMA_CONTEXT_SIZE` | `4096` | Ollama | Default context window. |  |
| `OLLAMA_IDLE_TIMEOUT` | `120s` | Ollama | Time before idle models unload. |  |
| `OLLAMA_KEEP_ALIVE` | `5m` | Ollama | How long models stay in memory after last use. |  |
| `OLLAMA_MAX_LOADED_MODELS` | `3` | Ollama | Maximum models kept loaded. |  |
| `OLLAMA_MAX_QUEUE` | `512` | Ollama | Request queue size. |  |
| `OLLAMA_MAX_REPLICAS` | `4` | Ollama | Maximum model replicas. |  |
| `OLLAMA_MMAP` | `true` | Ollama | Enable memory-mapped model loading. |  |
| `OLLAMA_NUM_PARALLEL` | `8` | Ollama | Concurrent requests limit. |  |
| `OLLAMA_PULL_MODELS` | `llama3.1:8b deepseek-r1:7b qwen2.5-coder:7b bge-m3` | Ollama | Models preloaded by `ollama-bootstrap` |  |
| `OLLAMA_VERSION` | `0.10.0` | Misc | Ollama model server version. |  |
| `OPENWEBUI_ADMIN_EMAIL` | `admin@example.com` | Open WebUI | Bootstrapped Open WebUI admin account. |  |
| `OPENWEBUI_ADMIN_PASSWORD` | `changeme` | Open WebUI | Password for Open WebUI admin. |  |
| `OPENWEBUI_DEFAULT_USER_ROLE` | `pending` | Open WebUI | Role newly signed‑up users get. |  |
| `OPENWEBUI_ENABLE_PERSISTENT_CONFIG` | `true` | Open WebUI | Keep configuration across container restarts. |  |
| `OPENWEBUI_ENABLE_SIGNUP` | `false` | Open WebUI | Allow self‑registration (true/false). |  |
| `OPENWEBUI_PORT` | `8080` | Open WebUI | Internal UI port inside container. |  |
| `OPENWEBUI_VERSION` | `v0.6.22` | Open WebUI | Open WebUI image tag. |  |
| `PORTAINER_PORT` | `9000` | Misc | Portainer web UI port. |  |
| `PORTAINER_VERSION` | `2.20.3` | Misc | Portainer version. |  |
| `PROMETHEUS_VERSION` | `v3.3.1` | Misc | Prometheus image tag. |  |
| `RAGFLOW_ADMIN_EMAIL` | `admin@ragflow.io` | RAGFlow | Bootstrapped RAGFlow admin account. |  |
| `RAGFLOW_ADMIN_PASSWORD` | `changeme` | RAGFlow | RAGFlow admin password. |  |
| `RAGFLOW_EXTRA_PORTS` | `9382` | RAGFlow | Additional exposed ports (MCP). |  |
| `RAGFLOW_HISTORY_DIR` | `./ragflow/history_data_agent` | RAGFlow | Host path for chat history. |  |
| `RAGFLOW_LOG_DIR` | `./ragflow/ragflow-logs` | RAGFlow | Host path for RAGFlow logs. |  |
| `RAGFLOW_NGINX_CONF_DIR` | `\`\` | RAGFlow | Optional mount to inject custom nginx.conf. |  |
| `RAGFLOW_VERSION` | `v0.18.0` | RAGFlow | RAGFlow image tag. |  |
| `REDIS_HOST` | `redis` | Valkey | Valkey/Redis host. |  |
| `REDIS_PASSWORD` | `changeme` | Valkey | Valkey password. |  |
| `REDIS_PORT` | `6379` | Valkey | Valkey port. |  |
| `REDIS_VERSION` | `8.1.0` | Valkey | Valkey image tag. |  |
| `REGISTER_ENABLED` | `0` | RAGFlow | Allow public sign‑up in RAGFlow. |  |
| `SEARXNG_QUERY_URL` | `http://searxng:8080/search?q=<query>&format=json` | Web search | Template URL for SearXNG queries. |  |
| `SMTP_HOST` | `smtp` | SMTP relay | Container name / hostname for SMTP relay. |  |
| `SMTP_IMAGE` | `boky/postfix:latest` | SMTP relay | Docker image for SMTP relay. |  |
| `SMTP_PORT` | `25` | SMTP relay | Port the SMTP relay listens on. |  |
| `SMTP_SSL` | `false` | SMTP relay | Enable STARTTLS (true/false). |  |
| `SVR_HTTP_PORT` | `9380` | RAGFlow | RAGFlow backend HTTP port. |  |
| `TIMEZONE` | `Europe/Berlin` | Global | Container timezone. |  |
| `TRAEFIK_BASIC_AUTH` | `admin:$2y$05$F6KSt6mnvnqqPhQ3VTLIAugnQuhhtJAhdi09Qf0oxBysbbZacqbXK` | Traefik | htpasswd‑style `user:hash`.  Demo credentials = **admin / admin** – replace for production. | user\:hash used by Traefik basic-auth middleware for most UIs. |
| `TRAEFIK_DOMAIN` | `ai.lab.example.com` | Traefik | Apex domain under which all sub‑services are published. |  |
| `TRAEFIK_LE_EMAIL` | `admin@example.com` | Traefik | Contact e‑mail for Let’s Encrypt. |  |
| `TRAEFIK_VERSION` | `3.4.1` | Traefik | Traefik docker image tag. |  |
| `TS_AUTHKEY` | `-` | Tailscale | Authentication key used to connect to your personal Tailscale tenant |  |
| `WEBHOOK_URL` | `https://n8n.ai.lab.example.com/` | n8n | External webhook base URL for n8n. |  |
| `WEBUI_URL` | `` | Open WebUI | External URL for the WebUI. |  |
| `WEB_SEARCH_CONCURRENT_REQUESTS` | `2` | Web search | Parallel search requests. |  |
| `WEB_SEARCH_ENGINE` | `searxng` | Web search | Search engine to use. |  |
| `WEB_SEARCH_RESULT_COUNT` | `5` | Web search | Number of results to fetch. |  |

For deep‑links and automatic change‑tracking the same table is regenerated in `docs/ENVIRONMENT.md` whenever `scripts/sync_env.py --docs` is executed.

---

## Contributing & CI hints

- Use two‑space YAML indentation and keep block‑comment separators.
- Run a quick syntax check before committing:\
  `ansible-playbook --syntax-check ansible/site.yaml && docker compose -f ansible/roles/pocket_lab/files/compose.yaml config`
- Keep this README and `docs/ENVIRONMENT.md` up‑to‑date when touching variables or behaviour.

## Release Process

We follow SemVer. Tag releases and publish notes.

```bash
git tag -a v0.1.0 -m "Pocket-Lab v0.1.0 — first public release"
git push origin v0.1.0
```
