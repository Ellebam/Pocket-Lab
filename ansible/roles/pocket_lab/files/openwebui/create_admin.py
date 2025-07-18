#!/usr/bin/env python3
"""
openwebui-bootstrap.py – create/refresh first admin account.
Idempotent, verbose, and ALWAYS exits 0.
"""
import contextlib, logging, os, pathlib, sqlite3, sys, time, traceback, uuid

# ───────── logging ───────────────────────────────────────────────
try:
    from open_webui.env import GLOBAL_LOG_LEVEL            # optional import
except Exception:
    GLOBAL_LOG_LEVEL = os.getenv("GLOBAL_LOG_LEVEL", "INFO")

logging.basicConfig(
    level=getattr(logging, GLOBAL_LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-7s | openwebui.bootstrap | %(message)s",
    force=True,
)
log = logging.getLogger()

# ───────── config ────────────────────────────────────────────────
DB      = pathlib.Path("/app/backend/data/webui.db")
EMAIL   = os.getenv("OPENWEBUI_ADMIN_EMAIL", "admin@example.com").lower()
NAME    = os.getenv("OPENWEBUI_ADMIN_NAME", EMAIL.split("@")[0].title())
PWD     = os.getenv("OPENWEBUI_ADMIN_PASSWORD", "changeme").encode()
NOW     = int(time.time_ns())

# ───────── helpers ───────────────────────────────────────────────
def bootstrap_schema_if_missing() -> None:
    """Import the internal DB module once – this runs all Peewee/Alembic
    migrations and creates `webui.db` on a blank volume."""
    if DB.exists():
        log.debug("DB already exists (%s bytes) – skipping migrations", DB.stat().st_size)
        return
    log.info("webui.db does not exist – triggering built-in migrations")
    try:
        import open_webui.internal.db  # noqa: F401  ※ side-effect: creates DB
        log.info("Migrations finished – DB created")
    except ModuleNotFoundError as exc:
        log.error("Cannot import open_webui.internal.db – image layout changed? %s", exc)
        raise

def wait_db(timeout: int = 90) -> bool:
    t_end = time.time() + timeout
    while time.time() < t_end:
        if DB.exists() and DB.stat().st_size:
            return True
        log.debug("Waiting for DB … (%ds left)", int(t_end - time.time()))
        time.sleep(2)
    return False

def log_schema(cur, tbl):
    cur.execute(f"PRAGMA table_info({tbl});")
    cols = ", ".join(f"{c[1]}[{c[3]}]" for c in cur.fetchall())    # c[3] => NOT-NULL flag
    log.debug("Schema %s → %s", tbl, cols)

def ensure_admin(conn):
    import bcrypt                                               # already in the image
    cur = conn.cursor()
    for tbl in ("auth", "user"):
        log_schema(cur, tbl)

    # ---------- auth ----------
    cur.execute("SELECT id FROM auth WHERE email=?;", (EMAIL,))
    row = cur.fetchone()
    hashed = bcrypt.hashpw(PWD, bcrypt.gensalt()).decode()

    if row:
        uid = row[0]
        log.info("Updating auth row uid=%s", uid)
        cur.execute(
            "UPDATE auth SET password=?, active=1 WHERE id=?;", (hashed, uid)
        )
    else:
        uid = str(uuid.uuid4())
        log.info("Creating auth row uid=%s", uid)
        cur.execute(
            "INSERT INTO auth (id,email,password,active) VALUES (?,?,?,1);",
            (uid, EMAIL, hashed),
        )

    # ---------- user ----------
    cur.execute("SELECT id FROM user WHERE id=?;", (uid,))
    if cur.fetchone():
        log.info("Updating user row uid=%s", uid)
        cur.execute(
            """
            UPDATE user
               SET name=?,
                   email=?,
                   role='admin',
                   updated_at=?
             WHERE id=?;
            """,
            (NAME, EMAIL, NOW, uid),
        )
    else:
        log.info("Creating user row uid=%s", uid)
        cur.execute(
            """
            INSERT INTO user
                   (id,  name, email, role, profile_image_url,
                    last_active_at, updated_at, created_at)
            VALUES (?,   ?,    ?,     'admin', '', ?,            ?,          ?);
            """,
            (uid, NAME, EMAIL, NOW, NOW, NOW),
        )
    return uid

def verify(cur):
    cur.execute(
        """
        SELECT u.role, u.name, a.active
          FROM user u JOIN auth a USING(id)
         WHERE u.email=?;
        """,
        (EMAIL,),
    )
    r = cur.fetchone()
    return r and r[0] == "admin" and r[2] == 1

# ───────── main ────────────────────────────────────────────────
def main():
    # -----------------------------------------------------------------
    # minimal env that Open WebUI MUST see before any db setup  happens
    # -----------------------------------------------------------------
    os.environ.setdefault("DATA_DIR", "/app/backend/data")
    if not os.environ.get("WEBUI_SECRET_KEY"):
        os.environ["WEBUI_SECRET_KEY"] = uuid.uuid4().hex  # 32-char random
    pathlib.Path(os.environ["DATA_DIR"]).mkdir(parents=True, exist_ok=True)

    bootstrap_schema_if_missing()

    if not wait_db():
        log.error("webui.db never appeared – giving up")
        return
    with contextlib.closing(sqlite3.connect(DB)) as conn:
        try:
            uid = ensure_admin(conn)
            conn.commit()
            if verify(conn.cursor()):
                log.info("Bootstrap finished ✔ (uid=%s)", uid)
            else:
                log.error("Verification failed – admin row inconsistent")
        except Exception:
            log.exception("☠ bootstrap crashed – continuing so UI can start")

if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        log.critical("Uncaught error – continuing (exit 0)")
    finally:
        sys.exit(0)
