#!/bin/sh
# ---------------------------------------------------------------------------
# initial_admin_setup.sh  –  bootstrap first (owner) account for n8n
# ---------------------------------------------------------------------------
# * Idempotent        (safe to run multiple times)
# * Requires env      N8N_ADMIN_EMAIL  N8N_ADMIN_PASSWORD
# * Always exits 0    (writes .bootstrap_done  OR  .bootstrap_failed)
# ---------------------------------------------------------------------------

set -eu
trap 'printf "[%s] ⚠ bootstrap failed – inspect logs\n" "$(date "+%H:%M:%S")"; \
      touch "$DATA_DIR/.bootstrap_failed"; exit 0' ERR INT TERM

# enable pipefail on shells that support it
if (set -o 2>/dev/null | grep -q pipefail); then
  set -o pipefail
fi

##############################################################################
# helpers
##############################################################################
log() { printf '[%s] %s\n' "$(date '+%H:%M:%S')" "$*"; }
die() { log "❌ $*"; touch "$DATA_DIR/.bootstrap_failed"; exit 0; }

##############################################################################
# configuration from environment / defaults
##############################################################################
DATA_DIR="${N8N_USER_FOLDER:-/home/node/.n8n}"
DB_FILE="$DATA_DIR/database.sqlite"
SQLITE_BIN="$DATA_DIR/sqlite3"
MARK_FILE="$DATA_DIR/.bootstrap_done"
FAIL_FILE="$DATA_DIR/.bootstrap_failed"

ADMIN_EMAIL="${N8N_ADMIN_EMAIL:?N8N_ADMIN_EMAIL missing}"
ADMIN_PASSWORD="${N8N_ADMIN_PASSWORD:?N8N_ADMIN_PASSWORD missing}"

# ---------------------------------------------------------------------------
# static-sqlite3 binary (musl-linked) – see
# https://github.com/CompuRoot/static-sqlite3/releases
# ---------------------------------------------------------------------------
SQLITE_TAG="3.46.1_01"
case "$(uname -m)" in
  x86_64)  SQLITE_ASSET="sqlite3"         ;;
  aarch64) SQLITE_ASSET="sqlite3-aarch64" ;;
  *) die "unsupported architecture ‘$(uname -m)’" ;;
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
  wget -qO "$SQLITE_BIN" --header="Accept: application/octet-stream" "$SQLITE_URL" \
    || die "download failed"
  chmod +x "$SQLITE_BIN"
fi

# convenience wrapper
sql() { "$SQLITE_BIN" "$DB_FILE" "$@" ; } 2>/dev/null

##############################################################################
# short-circuit if bootstrap already succeeded
##############################################################################
if [ -f "$MARK_FILE" ]; then
  log "✔ bootstrap already completed – skipping"
  exit 0
fi

##############################################################################
# wipe DB schema to pristine ‘no-users’ state
##############################################################################
log "🧹 running n8n user-management:reset … (idempotent)"
n8n user-management:reset --force   

##############################################################################
# detect actual user table name (user vs user_entity) and sanity-check row count
##############################################################################
USER_TABLE=$(sql "SELECT name FROM sqlite_master \
                  WHERE type='table' AND name IN ('user','user_entity') LIMIT 1;")
[ -n "$USER_TABLE" ] || die "no user table found – n8n schema changed?"
ROW_COUNT=$(sql "SELECT COUNT(*) FROM $USER_TABLE;" | tr -d '[:space:]')
[ "$ROW_COUNT" -eq 1 ] || die "unexpected row count in $USER_TABLE ($ROW_COUNT ≠ 1)"

##############################################################################
# build bcrypt hash via the bundled module
##############################################################################
export NODE_PATH="/usr/local/lib/node_modules/n8n/node_modules"
HASH=$(node -e 'const b=require("bcryptjs");console.log(b.hashSync(process.argv[1],10))' \
      "$ADMIN_PASSWORD")

##############################################################################
# promote the placeholder row to a real global:owner account
##############################################################################
log "📝 writing owner row in table $USER_TABLE"
sql "UPDATE $USER_TABLE SET \
        email      = lower('$ADMIN_EMAIL'), \
        password   = '$HASH', \
        role       = 'global:owner', \
        settings   = '{\"userActivated\": true}', \
        updatedAt  = datetime('now') \
      WHERE id IS NOT NULL;"

##############################################################################
# ---------------------------------------------------------------------------
# Mark the instance as “owner already set up”  ➜  settings table
# ---------------------------------------------------------------------------
##############################################################################
SETTINGS_TABLE=$(sql "SELECT name FROM sqlite_master \
                      WHERE type='table' AND name='settings' LIMIT 1;")
[ -n "$SETTINGS_TABLE" ] || die "no settings table found"

sql "INSERT OR REPLACE INTO $SETTINGS_TABLE (key,value,loadOnStartup) \
     VALUES ('userManagement.isInstanceOwnerSetUp','true',1);"  # 1 = true for SQLite 

##############################################################################
# verify & finish
##############################################################################
OWNER_OK=$(sql "SELECT COUNT(*) FROM $USER_TABLE \
                WHERE email = lower('$ADMIN_EMAIL') \
                  AND role = 'global:owner';" | tr -d '[:space:]')
FLAG_OK=$(sql "SELECT value FROM $SETTINGS_TABLE \
               WHERE key='userManagement.isInstanceOwnerSetUp';")

if [ "$OWNER_OK" -eq 1 ] && [ "$FLAG_OK" = "true" ]; then
  log "✔ owner row & settings flag confirmed – bootstrap finished"
  touch "$MARK_FILE"
else
  die "verification failed – owner or settings flag incorrect"
fi

exit 0   # ALWAYS succeed
