#!/bin/sh
# -----------------------------------------------------------------------------
# initial_admin_setup.sh – seed the first (owner) account for n8n
#
# * Idempotent: safe to run many times.
# * Exits non‑zero if it cannot guarantee that the owner exists.
# -----------------------------------------------------------------------------

# Fail fast: -e stop on error, -u on undefined var.
# pipefail is useful but not available in every /bin/sh; enable if supported.
set -eu
if (set -o 2>/dev/null | grep -q pipefail); then
  set -o pipefail
fi


# ── config (all values come from docker-compose/.env) ────────────────
DATA_DIR="${N8N_DATA_DIR:-/home/node}"
DB="$DATA_DIR/database.sqlite"
ADMIN_EMAIL="${N8N_ADMIN_EMAIL:?unset}"
ADMIN_PASSWORD="${N8N_ADMIN_PASSWORD:?unset}"
MARK="$DATA_DIR/.bootstrap_done"

# ── prepare folders & permissions ───────────────────────────────────
install -d -m 700 "$DATA_DIR"

# ── tiny helper to ask SQLite (no jq, no list cmd) ──────────────────
owner_exists() {
  [ -f "$DB" ] || return 1
  sqlite3 "$DB" "SELECT 1 FROM \"user\" \
                 WHERE globalRoleId=1 AND email='$ADMIN_EMAIL' LIMIT 1;" \
    | grep -q 1
}

# ── idempotent bootstrap logic ──────────────────────────────────────
if [ -f "$MARK" ] || owner_exists; then
  echo "✔ owner already present – skipping"
  exit 0
fi

echo "⏳ seeding owner account …"
n8n user-management:reset \
      --email "$ADMIN_EMAIL" \
      --password "$ADMIN_PASSWORD" \
      --force

if owner_exists; then
  touch "$MARK"
  echo "✔ owner created successfully"
  exit 0
else
  echo "❌ owner not found after reset; aborting" >&2
  exit 20
fi

