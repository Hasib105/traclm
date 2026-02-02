"""Database tables for LLM Tracer."""

import hashlib
import secrets
from datetime import datetime
from enum import Enum

from piccolo.columns import (
    JSON,
    UUID,
    Boolean,
    ForeignKey,
    Integer,
    Serial,
    Text,
    Timestamp,
    Varchar,
)
from piccolo.table import Table


class TraceStatus(str, Enum):
    """Status of an LLM trace."""

    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"


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


class Project(Table):
    """A project that groups traces together."""

    name = Varchar(length=255, unique=True)
    description = Text(null=True)
    owner = ForeignKey(references=User, null=True)
    created_at = Timestamp(default=datetime.now)
    updated_at = Timestamp(default=datetime.now, auto_update=datetime.now)


class APIKey(Table):
    """API keys for authentication."""

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
        return f"llm-{secrets.token_urlsafe(32)}"

    @classmethod
    def hash_key(cls, key: str) -> str:
        """Hash an API key for secure storage."""
        return hashlib.sha256(key.encode()).hexdigest()

    @classmethod
    def verify_key(cls, key: str, key_hash: str) -> bool:
        """Verify an API key against its hash."""
        return cls.hash_key(key) == key_hash


class LLMTrace(Table):
    """Individual LLM trace record."""

    trace_id = UUID(index=True)
    parent_trace_id = UUID(null=True, index=True)
    project = ForeignKey(references=Project, null=True)

    # Model information
    model_name = Varchar(length=255, default="unknown")
    model_provider = Varchar(length=100, null=True)

    # Status
    status = Varchar(length=20, default=TraceStatus.RUNNING.value)
    error_message = Text(null=True)

    # Input/Output data
    input_data = JSON(default={})
    output_data = JSON(default={})

    # Tool calls
    tool_calls = JSON(default=[])

    # Token usage
    prompt_tokens = Integer(default=0)
    completion_tokens = Integer(default=0)
    total_tokens = Integer(default=0)

    # Cost tracking (in cents)
    cost_cents = Integer(default=0)

    # Timing
    start_time = Timestamp(default=datetime.now)
    end_time = Timestamp(null=True)
    latency_ms = Integer(default=0)

    # Metadata
    metadata = JSON(default={})
    tags = JSON(default=[])

    # Session tracking
    session_id = Varchar(length=100, null=True, index=True)
    user_id = Varchar(length=100, null=True, index=True)

    def calculate_latency(self) -> int:
        """Calculate latency in milliseconds."""
        if self.end_time and self.start_time:
            delta = self.end_time - self.start_time
            return int(delta.total_seconds() * 1000)
        return 0
