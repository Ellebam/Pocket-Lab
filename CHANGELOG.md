# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-09-23
### Added
- Initial public release of Pocket-Lab with Ansible and Docker Compose deployment paths.
- Traefik (TLS via ACME DNS-01), Ollama, Open WebUI, RAGFlow, Elasticsearch/Infinity, MySQL, MinIO, Valkey, SearXNG, Stirling-PDF, Portainer.
- Observability stack: Prometheus, Grafana, Loki.
- First-run helpers for admin bootstrap where needed.
- Single `.env` management flow (`.env.template`).

### Fixed
- Documentation alignment for `OFFLINE_MODE` default (`true`) across README, `.env.template`, and `docs/ENVIRONMENT.md`.

### Notes
- Ansible is the authoritative path; plain Docker Compose works for quick experiments.
