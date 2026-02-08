"""User model for dashboard authentication."""

import hashlib
import secrets
from datetime import datetime

from piccolo.columns import Boolean, Timestamp, Varchar
from piccolo.table import Table


class User(Table, tablename="app_user"):
    """User account for dashboard access."""

    username = Varchar(length=100, unique=True, index=True)
    email = Varchar(length=255, unique=True, index=True)
    password_hash = Varchar(length=255)
    is_active = Boolean(default=True)
    is_admin = Boolean(default=False)
    created_at = Timestamp(default=datetime.now)
    last_login = Timestamp(null=True)

    @classmethod
    def hash_password(cls, password: str) -> str:
        """Hash a password using SHA-256 with salt."""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.sha256((salt + password).encode())
        return f"{salt}:{hash_obj.hexdigest()}"

    @classmethod
    def verify_password(cls, password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        try:
            salt, stored_hash = password_hash.split(":")
            hash_obj = hashlib.sha256((salt + password).encode())
            return hash_obj.hexdigest() == stored_hash
        except ValueError:
            return False
