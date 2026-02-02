"""Authentication and authorization utilities."""

from datetime import datetime

from fastapi import Depends, Header, HTTPException, status

from llm_tracer.db.tables import APIKey, Project


async def get_api_key(x_api_key: str | None = Header(None, alias="X-API-Key")) -> APIKey | None:
    """Validate API key from header."""
    if not x_api_key:
        return None

    # Query API key
    api_key = await APIKey.select().where(APIKey.key == x_api_key, APIKey.is_active == 1).first()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or inactive API key"
        )

    # Update last used timestamp
    await APIKey.update({APIKey.last_used_at: datetime.now()}).where(APIKey.id == api_key["id"])

    return api_key


async def require_api_key(api_key: dict | None = Depends(get_api_key)) -> dict:
    """Require a valid API key."""
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Include X-API-Key header.",
        )
    return api_key


async def get_project_from_api_key(api_key: dict = Depends(require_api_key)) -> Project:
    """Get the project associated with an API key."""
    project = await Project.select().where(Project.id == api_key["project"]).first()

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    return project
