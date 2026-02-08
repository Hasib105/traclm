"""API dependencies for authentication and authorization."""

from datetime import datetime
from typing import Optional

from fastapi import Depends, Header, HTTPException, Request, status

from llm_tracer.db.models import APIKey


def get_current_user(request: Request) -> Optional[dict]:
    """Get current user from session."""
    return request.session.get("user")


def require_auth(request: Request) -> dict:
    """Require user authentication via session."""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user


async def get_api_key_from_header(
    x_api_key: str | None = Header(None, alias="X-API-Key"),
) -> Optional[dict]:
    """Validate API key from header."""
    if not x_api_key:
        return None

    # Hash the provided key and look it up
    from llm_tracer.db.models import APIKey

    key_hash = APIKey.hash_key(x_api_key)
    api_key = await APIKey.select().where(
        APIKey.key_hash == key_hash,
        APIKey.is_active == 1,
    ).first()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key",
        )

    # Update last used timestamp
    await APIKey.update({APIKey.last_used_at: datetime.now()}).where(
        APIKey.id == api_key["id"]
    )

    return api_key


async def require_api_key(api_key: dict | None = Depends(get_api_key_from_header)) -> dict:
    """Require a valid API key."""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Include X-API-Key header.",
        )
    return api_key
