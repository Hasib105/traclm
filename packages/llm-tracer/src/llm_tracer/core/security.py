"""Security utilities for authentication."""

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from llm_tracer.config import settings


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a simple signed token for session management."""
    import base64
    import json

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=24))
    to_encode["exp"] = expire.isoformat()

    # Simple HMAC-based token
    payload = base64.urlsafe_b64encode(json.dumps(to_encode).encode()).decode()
    signature = hmac.new(
        settings.SECRET_KEY.encode(),
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()[:32]

    return f"{payload}.{signature}"


def verify_token(token: str) -> dict[str, Any] | None:
    """Verify and decode a token."""
    import base64
    import json

    try:
        payload, signature = token.rsplit(".", 1)
        expected_sig = hmac.new(
            settings.SECRET_KEY.encode(),
            payload.encode(),
            hashlib.sha256,
        ).hexdigest()[:32]

        if not hmac.compare_digest(signature, expected_sig):
            return None

        data = json.loads(base64.urlsafe_b64decode(payload))

        # Check expiration
        exp = datetime.fromisoformat(data["exp"])
        if exp < datetime.now(timezone.utc):
            return None

        return data
    except Exception:
        return None


def generate_api_key() -> str:
    """Generate a secure API key."""
    return f"lt-{secrets.token_urlsafe(32)}"


def hash_api_key(key: str) -> str:
    """Hash an API key for storage."""
    return hashlib.sha256(key.encode()).hexdigest()
