# Guidelines for AI agents

This repository contains Ansible playbooks and Docker Compose files. When
modifying files keep the following in mind:

- Use two spaces for YAML indentation and keep the existing formatting.
- Update `README.md` whenever behaviour or variables change.
- If you change Ansible or Compose files, try to run a syntax check:
  - `ansible-playbook --syntax-check ansible/site.yaml` (requires Ansible)
  - `docker compose -f ansible/roles/pocket_lab/files/compose.yaml config`
    (requires Docker)
  These checks are optional if the tools are unavailable in the
  environment.
- Commit messages should be concise and in the imperative mood.

No automated tests are provided.
