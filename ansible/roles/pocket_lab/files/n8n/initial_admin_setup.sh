#!/bin/sh
# ---------------------------------------------------------------------------
# initial_admin_setup.sh  –  bootstrap first (owner) account for n8n
# ---------------------------------------------------------------------------
# * Idempotent    (safe to run multiple times)
# * Requires env  N8N_ADMIN_EMAIL  N8N_ADMIN_PASSWORD
# * Fails fast    (non-zero exit on any problem)
# ---------------------------------------------------------------------------

set -eu
# enable pipefail on shells that support it
if (set -o 2>/dev/null | grep -q pipefail); then
  set -o pipefail
fi

##############################################################################
# helpers
##############################################################################
log() { printf '[%s] %s\n' "$(date '+%H:%M:%S')" "$*"; }
die() { log "❌ $*"; exit 1; }

##############################################################################
# configuration from environment / defaults
##############################################################################
DATA_DIR="${N8N_USER_FOLDER:-/home/node/.n8n}"
DB_FILE="$DATA_DIR/database.sqlite"
SQLITE_BIN="$DATA_DIR/sqlite3"
MARK_FILE="$DATA_DIR/.bootstrap_done"

ADMIN_EMAIL="${N8N_ADMIN_EMAIL:?N8N_ADMIN_EMAIL missing}"
ADMIN_PASSWORD="${N8N_ADMIN_PASSWORD:?N8N_ADMIN_PASSWORD missing}"

# ---------------------------------------------------------------------------
# static-sqlite3 binary (musl-linked) – see
# https://github.com/CompuRoot/static-sqlite3/releases
# ---------------------------------------------------------------------------
SQLITE_TAG="3.46.1_01"
case "$(uname -m)" in
  x86_64)  SQLITE_ASSET="sqlite3"           ;;
  aarch64) SQLITE_ASSET="sqlite3-aarch64"   ;;
  *) log "unsupported architecture ‘$(uname -m)’" ;;
esac
SQLITE_URL="https://github.com/CompuRoot/static-sqlite3/releases/download/${SQLITE_TAG}/${SQLITE_ASSET}"

##############################################################################
# pre-flight checks
##############################################################################
mkdir -p "$DATA_DIR"
[ -w "$DATA_DIR" ] || log "'$DATA_DIR' not writable – check volume permissions"

##############################################################################
# fetch sqlite3 binary once
##############################################################################
if [ ! -x "$SQLITE_BIN" ] || [ ! -s "$SQLITE_BIN" ]; then
  log "📦 downloading sqlite3 from $SQLITE_URL …"
 # --header ensures we get the asset, not the HTML page
  wget -qO "$SQLITE_BIN" --header="Accept: application/octet-stream" "$SQLITE_URL" \
    || log "download failed"
  chmod +x "$SQLITE_BIN"
fi

# convenience wrapper
sql() { "$SQLITE_BIN" "$DB_FILE" "$@" ; } 2>/dev/null
user_count() { sql 'SELECT COUNT(*) FROM user_entity;' 2>/dev/null || echo 0; }

##############################################################################
# skip if we succeeded once already
##############################################################################
if [ -f "$MARK_FILE" ]; then
  log "✔ bootstrap already completed – skipping"
  exit 0
fi

##############################################################################
# create owner only when DB is empty
##############################################################################
if [ "$(user_count)" -eq 0 ]; then
  log "⏳ creating owner “$ADMIN_EMAIL”"
  n8n user-management:reset \
        --email "$ADMIN_EMAIL" \
        --password "$ADMIN_PASSWORD" \
        --force
fi

##############################################################################
# verify result
##############################################################################
OWNER_EXISTS=$(sql "SELECT COUNT(*) FROM user_entity \
                    WHERE email = lower('$ADMIN_EMAIL');" || echo 0)

if [ "$OWNER_EXISTS" = "1" ]; then
  log "✔ owner row confirmed in DB"
  touch "$MARK_FILE"
  exit 0
else
  log "owner row missing – inspect $DB_FILE manually"
fi
