# Ansible specific guidelines

- YAML files use two space indentation and no document start markers.
- Playbooks live in `ansible/plays/` and roles in `ansible/roles/`.
- Keep variable names snake_case.
- `.env.j2` and role defaults follow the same block-comment convention as
  other variable files.
