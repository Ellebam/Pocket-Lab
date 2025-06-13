import logging
import os
from werkzeug.security import generate_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from api.db.db_models import init_database_tables as init_web_db
from api.db.init_data import init_superuser
from api.db.services.user_service import UserService, TenantService
from api import settings



def main():
    email = os.getenv("RAGFLOW_ADMIN_EMAIL", "admin@ragflow.io")
    password = os.getenv("RAGFLOW_ADMIN_PASSWORD", "admin")

    logger.info("Using admin email '%s'", email)

    logger.info("Initializing settings and database")
    try:
        settings.init_settings()
        init_web_db()
    except Exception:  # pragma: no cover - startup failures
        logger.exception("Setup failed")
        return

    # bootstrap only if no admin exists yet
    if not UserService.query(email=email) and not UserService.query(email="admin@ragflow.io"):
        logger.info("Creating initial superuser")
        try:
            init_superuser()
        except Exception as exc:  # pragma: no cover - startup failures
            env_keys = [
                "RAGFLOW_ADMIN_EMAIL",
                "LLM_FACTORY",
                "LLM_API_BASE",
                "LLM_CHAT_MODEL",
                "LLM_EMBEDDING_MODEL",
                "LLM_RERANK_MODEL",
                "LLM_ASR_MODEL",
                "LLM_IMAGE2TEXT_MODEL",
            ]
            env_snapshot = {k: os.getenv(k) for k in env_keys}
            logger.exception("Superuser creation failed: %s", exc)
            logger.error("Environment: %s", env_snapshot)
            logger.error("Check your .env and language model configuration")
            return
    user = None
    if UserService.query(email=email):
        user = UserService.query(email=email)[0]
    elif UserService.query(email="admin@ragflow.io"):
        user = UserService.query(email="admin@ragflow.io")[0]
    else:
        logger.error("Admin user not found")
        return

    updates = {}
    if user.email != email:
        logger.info("Updating email from '%s'", user.email)
        updates["email"] = email
    if password:
        logger.info("Setting admin password")
        updates["password"] = generate_password_hash(password)
    if updates:
        UserService.update_user(user.id, updates)

    # ensure tenant association exists
    if not TenantService.get_info_by(user.id):
        logger.info("Fixing tenant association for admin user")
        try:
            init_superuser()
        except LookupError as exc:
            logger.error("Tenant fix failed: %s", exc)


if __name__ == "__main__":
    main()
    logger.info("Admin initialization finished")