 **Pocket‑Lab**  is a self‑contained infrastructure tool that lets you spin up a hardened, Docker‑based AI lab on any fresh Linux host .

## Repository map

| Path                                 | What it is / why it exists                                                                                                                      |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `Taskfile.yaml`                      | Developer UX wrapper around both **go‑task** and **docker compose**; exposes one‑liners like `task ansible_full` or `task docker-compose-logs`. |
| `.env.template`                      | Minimal env‑file you copy to `.env` for _manual_ `docker compose` runs.                                                                         |
| `ansible/`                           | Control‑plane: inventory, plays, roles, galaxy requirements & config.                                                                           |
| `ansible/plays/00‑30‑*.yaml`         | Four atomic playbooks (detect → bootstrap → harden → deploy).                                                                                   |
| `ansible/roles/ensure_conn_user`     | Detects **root**, inventory‑defined user, or first user in `l3d_users__local_users`, caches the winner for 24 h (Ansible jsonfile fact cache).  |
| `ansible/roles/pocket_lab`           | All Docker‑stack logic (pre‑reqs + deploy + cleanup). Uses `community.docker.docker_compose_v2`.                                                |
| `stack.yaml` & subordinate `files/*` | The actual compose spec (Traefik label routing, ES, RAGFlow, etc.).                                                                             |

## Getting started

1. **Clone** the repo
	```bash
	git clone https://github.com/your‑org/ellebam-pocket-lab.git && cd ellebam-pocket-lab
	```
2. **Create an env‑file**
   ```bash
      cp .env.template .env && edit .env   # domain, TLS e‑mail, secrets …
	```
3. **Configure Ansible inventory & users**
	- `ansible/inventory/hosts.yaml.template` → `hosts.yaml`; enter the server’s IP.
	- Open `ansible/roles/pocket_lab/defaults/main.yaml.template`; fill **at least**
    - `l3d_users__local_users` → list of dictionaries (`name`, `pubkeys`, `admin: true`).
    - Any stack passwords (`elastic_password`, `mysql_password`, …).
4. **Bootstrap a local Python venv & collections**
	   ```bash
	   task venv:init
		```
5. **One‑shot full provision**
6. 
	```bash
	task ansible_full  # detect → bootstrap → harden → deploy
	```

### Running the stack **without** Ansible

For quick local experiments:

```bash
	task docker-compose-up        # pull & start every service
	task docker-compose-logs      # follow logs
	task docker-compose-down      # stop & wipe volumes

```


These tasks invoke `docker compose` directly with the top‑level `stack.yaml` and your `.env`. No hardening or user management is touched.

---

## Task catalogue (prefix‑based)

|Command|What it does|
|---|---|
|`task ansible_detect`|Cache a working SSH login (uses `ensure_conn_user`).|
|`task ansible_bootstrap`|Only create users (roles `l3d.users.*`). [Ansible Galaxy](https://galaxy.ansible.com/ui/repo/published/l3d/users/content/role/user/?utm_source=chatgpt.com)|
|`task ansible_harden`|Apply DevSec OS/SSH hardening + Docker install. [GitHub](https://github.com/dev-sec/ansible-collection-hardening?utm_source=chatgpt.com)|
|`task ansible_deploy`|Copy compose files, render `.env`, launch stack.|
|`task ansible_full`|Full pipeline.|
|`task docker-*`|Pure compose helpers (up/down/logs/restart/prune).|

---

## Variables you’ll likely customise

|Variable|Default|Notes|
|---|---|---|
|`stack_domain`, `stack_email`|`ai.lab.example.com`, `admin@example.com`|Traefik ACME & router labels.|
|`basic_auth`|_bcrypt hash_|Re‑generate via `htpasswd -nbB`.|
|`tenant_name`, `*_TOKEN*`|–|Twingate connector.|
|`n8n_user`, `n8n_password`|`admin` / `changeme`|Basic auth for n8n frontend.|
|`elastic_password`, `mysql_password`, `minio_password`, …|`changeme`|Service creds.|
|`docker_version`, `docker_compose_version`|`latest`, `v2.27.1`|Pin if you need deterministic builds.|
|`compose_repo`|`/opt/pocket_lab`|Where compose files land on the host.|
|`mem_limit`|`4g`|Propagated to ES & Infinity containers.|
|`ssh_harden`, `firewall_open_tcp`|`true`, `[80,443,22]`|Toggle DevSec hardening or open extra ports.|
|`sshd_max_auth_tries`, `sshd_max_startups`|`10`, `10:30:100`|Mitigate “Too many authentication failures”. [GitHub](https://github.com/geerlingguy/ansible-role-docker?utm_source=chatgpt.com)|
|`l3d_users__local_users`|`[]`|The authoritative user list (managed & sudo‑enabled).|
|_Everything in `.env.template`_|–|Mirrors compose‑time environment.|

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
|**geerlingguy.docker**|Install Docker CE + CLI & Compose v2. [GitHub](https://github.com/geerlingguy/ansible-role-docker?utm_source=chatgpt.com)|
|**pocket_lab**|Copy compose files, render `.env`, run `community.docker.docker_compose_v2` (pull policy `missing`). [Ansible Documentation](https://docs.ansible.com/ansible/latest/collections/community/docker/docker_compose_v2_module.html?utm_source=chatgpt.com)|

---

## After cloning – quick checklist

1. **Add hosts**: copy `ansible/inventory/hosts.yaml.template` → `hosts.yaml`, fill IP/FQDN.
    
2. **Define users**: edit `l3d_users__local_users` with `pubkeys` and `admin: true`.
    
3. **Secret variables**: set strong passwords in `.env` and defaults file.
    
4. _(Optional)_ Pin Docker/Compose versions for reproducibility.
    
5. Run `task ansible_full` – enjoy your hardened AI lab!
****