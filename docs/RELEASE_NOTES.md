## Pocket-Lab Subnet Routing via Tailscale

This release replaces the legacy Twingate connectors with a single Tailscale subnet router container.

### Migration
1. Generate a Tailscale auth key and set it as `TS_AUTHKEY` in your `.env` or host variables.
2. Remove any existing Twingate connector containers before bringing the stack back up.
