#!/usr/bin/env python3
"""
openwebui-bootstrap.py  –  first-admin initialiser for Open WebUI
• honours GLOBAL_LOG_LEVEL & other Open WebUI logging env-vars
• idempotent – re-runs just update the row
• never throws: all failures are logged, then we exit 0
"""

import contextlib, logging, os, pathlib, sqlite3, sys, time, traceback, uuid, bcrypt 

# ---------------------------------------------------------------------------
# 0.-  logging  
# ---------------------------------------------------------------------------
try:
    from open_webui.env import GLOBAL_LOG_LEVEL  
except Exception:
    GLOBAL_LOG_LEVEL = os.getenv("GLOBAL_LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, GLOBAL_LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    force=True,
)
log = logging.getLogger("open_webui.bootstrap")

# ---------------------------------------------------------------------------
# 1.-  config & helpers
# ---------------------------------------------------------------------------
DB      = pathlib.Path("/app/backend/data/webui.db")
EMAIL   = os.getenv("OPENWEBUI_ADMIN_EMAIL",    "admin@example.com").lower()
PASSWORD= os.getenv("OPENWEBUI_ADMIN_PASSWORD", "changeme").encode()

def _wait_for_db(timeout=60):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if DB.exists() and DB.stat().st_size:
            return True
        time.sleep(1)
    return False

def _detect_user_table(cur):
    """‘auth’ (≥ v0.3.17) or legacy ‘user’ table.”"""
    for tbl in ("auth", "user"):
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (tbl,))
        if cur.fetchone():
            return tbl
    raise RuntimeError("no suitable user table found")  # schema drift

def _ensure_admin(cur, tbl):
    cur.execute(f"SELECT id FROM {tbl} WHERE email=?;", (EMAIL,))
    uid = cur.fetchone()
    hashed = bcrypt.hashpw(PASSWORD, bcrypt.gensalt()).decode()

    if uid:
        log.info("Admin already exists – refreshing password")
        cur.execute(f"UPDATE {tbl} SET password=?, role='admin', active=1 WHERE id=?;",
                    (hashed, uid[0]))
        return uid[0]

    uid = str(uuid.uuid4())
    log.info("Creating admin user uid=%s", uid)
    cur.execute(
        f"INSERT INTO {tbl} (id,email,password,role,active) VALUES (?,?,?,?,1);",
        (uid, EMAIL, hashed, "admin"),
    )
    return uid

def _verify(cur, tbl):
    cur.execute(f"SELECT role,active FROM {tbl} WHERE email=?;", (EMAIL,))
    row = cur.fetchone()
    return row and row[0] == "admin" and row[1] == 1

# ---------------------------------------------------------------------------
# 2.-  main
# ---------------------------------------------------------------------------
def main():
    if not _wait_for_db():
        log.error("webui.db never appeared – giving up")
        return

    with contextlib.closing(sqlite3.connect(DB)) as conn:
        try:
            tbl  = _detect_user_table(conn.cursor())   # auth vs user
            uid  = _ensure_admin(conn.cursor(), tbl)
            conn.commit()

            if _verify(conn.cursor(), tbl):
                log.info("Bootstrap succeeded (uid=%s)", uid)
            else:
                log.error("Verification failed – admin row not correct")
        except Exception:
            log.exception("☠ bootstrap crashed")
            # fall through to exit 0

if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        log.critical("Fatal error bubbled out – continuing (exit 0)")
    finally:
        sys.exit(0)
