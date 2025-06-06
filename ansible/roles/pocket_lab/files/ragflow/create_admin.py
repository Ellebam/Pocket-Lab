import os
import base64
from werkzeug.security import generate_password_hash
from api.db.db_models import init_database_tables as init_web_db
from api.db.init_data import init_superuser
from api.db.services.user_service import UserService, TenantService, UserTenantService
from api.db.services.llm_service import LLMService, TenantLLMService
from api.db import UserTenantRole
from api import settings


def main():
    email = os.getenv("RAGFLOW_ADMIN_EMAIL", "admin@ragflow.io")
    password = os.getenv("RAGFLOW_ADMIN_PASSWORD", "admin")

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