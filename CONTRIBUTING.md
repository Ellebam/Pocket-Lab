# Contributing to Pocket-Lab

Thanks for taking the time to contribute!

## Quick Start
1. Fork and clone the repo.
2. Create a feature branch: `git checkout -b feat/your-change`.
3. Make your changes and run basic checks locally:
   - `yamllint .`
   - `ansible-lint ansible` (if Ansible files changed)
   - `docker compose -f ansible/roles/pocket_lab/files/compose.yaml config`
4. Commit with sensible messages and open a Pull Request.

## Style & Expectations
- Keep PRs focused and small where possible.
- Prefer clear docs/comments over cleverness.
- Update README/docs when behavior or env vars change.

## Development Notes
- **Authoritative Compose:** `ansible/roles/pocket_lab/files/compose.yaml`.
- **Env management:** copy `.env.template` to `.env`; keep defaults sane and secure.
- **Security:** never commit secrets. Use placeholders like `CHANGEME` in examples.

## Release Process (Maintainers)
- Bump version per SemVer.
- Update `CHANGELOG.md`.
- Tag: `git tag -a vX.Y.Z -m "Pocket-Lab vX.Y.Z" && git push origin vX.Y.Z`.
- Publish a GitHub Release with notes.
