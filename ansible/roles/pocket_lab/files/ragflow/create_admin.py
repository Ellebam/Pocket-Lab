import os
<<<<<<< HEAD
from werkzeug.security import generate_password_hash
from api.db.db_models import init_database_tables as init_web_db
from api.db.init_data import init_superuser
from api.db.services.user_service import UserService, TenantService
=======
import base64
from werkzeug.security import generate_password_hash
from api.db.db_models import init_database_tables as init_web_db
from api.db.init_data import init_superuser
from api.db.services.user_service import UserService, TenantService, UserTenantService
from api.db.services.llm_service import LLMService, TenantLLMService
from api.db import UserTenantRole
>>>>>>> 31c69a2 (feat: admin user creation for ragflow)
from api import settings


def main():
    email = os.getenv("RAGFLOW_ADMIN_EMAIL", "admin@ragflow.io")
    password = os.getenv("RAGFLOW_ADMIN_PASSWORD", "admin")

<<<<<<< HEAD
    settings.init_settings()
    init_web_db()

    # bootstrap only if no admin exists yet
    if not UserService.query(email=email) and not UserService.query(email="admin@ragflow.io"):
        init_superuser()

    user = None
    if UserService.query(email=email):
        user = UserService.query(email=email)[0]
    elif UserService.query(email="admin@ragflow.io"):
        user = UserService.query(email="admin@ragflow.io")[0]
    else:
        return

    updates = {}
    if user.email != email:
        updates["email"] = email
    if password:
        updates["password"] = generate_password_hash(password)
    if updates:
        UserService.update_user(user.id, updates)

    # ensure tenant association exists
    if not TenantService.get_info_by(user.id):
        init_superuser()


if __name__ == "__main__":
    main()
=======
    init_web_db()

    if not UserService.query(email=email):
        if not UserService.query(email="admin@ragflow.io"):
            init_superuser()
        user = UserService.query(email="admin@ragflow.io")[0]
        if email != "admin@ragflow.io":
            UserService.update_user(user.id, {"email": email})
        if password != "admin":
            pwd_hash = generate_password_hash(base64.b64encode(password.encode()).decode())
            UserService.update_user(user.id, {"password": pwd_hash})
    else:
        # admin already exists with desired email, ensure password matches if provided
        if password:
            user = UserService.query(email=email)[0]
            pwd_hash = generate_password_hash(base64.b64encode(password.encode()).decode())
            UserService.update_user(user.id, {"password": pwd_hash})


if __name__ == "__main__":
    main()
>>>>>>> 31c69a2 (feat: admin user creation for ragflow)
