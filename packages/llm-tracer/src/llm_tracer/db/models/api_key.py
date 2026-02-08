"""API Key model for SDK authentication."""

import hashlib
import secrets
from datetime import datetime

from piccolo.columns import ForeignKey, Integer, Timestamp, Varchar
from piccolo.table import Table

from llm_tracer.db.models.project import Project


class APIKey(Table):
    """API keys for SDK authentication."""

    name = Varchar(length=255)
    key_hash = Varchar(length=128, unique=True, index=True)
    key_prefix = Varchar(length=16)  # Store first 12 chars for display
    project = ForeignKey(references=Project, null=True)
    is_active = Integer(default=1)  # 1 = active, 0 = inactive
    created_at = Timestamp(default=datetime.now)
    last_used_at = Timestamp(null=True)

    @classmethod
    def generate_key(cls) -> str:
        """Generate a new API key."""
        return f"lt-{secrets.token_urlsafe(32)}"

    @classmethod
    def hash_key(cls, key: str) -> str:
        """Hash an API key for secure storage."""
        return hashlib.sha256(key.encode()).hexdigest()

    @classmethod
    def verify_key(cls, key: str, key_hash: str) -> bool:
        """Verify an API key against its hash."""
        return cls.hash_key(key) == key_hash
