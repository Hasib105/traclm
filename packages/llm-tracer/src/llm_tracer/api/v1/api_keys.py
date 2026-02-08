"""API Key routes."""

from fastapi import APIRouter, Depends, HTTPException, status

from llm_tracer.api.dependencies import require_auth
from llm_tracer.api.v1.schemas import APIKeyCreate, APIKeyResponse
from llm_tracer.db.models import APIKey, Project

router = APIRouter(prefix="/api-keys", tags=["API Keys"])


@router.get("", response_model=list[APIKeyResponse])
async def list_api_keys(user: dict = Depends(require_auth)):
    """List all API keys."""
    keys = await APIKey.select(
        APIKey.id,
        APIKey.name,
        APIKey.key_prefix,
        APIKey.project,
        APIKey.is_active,
        APIKey.created_at,
        APIKey.last_used_at,
    ).order_by(APIKey.created_at, ascending=False)

    return [
        APIKeyResponse(
            id=k["id"],
            name=k["name"],
            key_prefix=k["key_prefix"],
            project_id=k["project"],
            is_active=bool(k["is_active"]),
            created_at=k["created_at"],
            last_used_at=k["last_used_at"],
        )
        for k in keys
    ]


@router.post("", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(data: APIKeyCreate, user: dict = Depends(require_auth)):
    """Create a new API key."""
    # Verify project exists if provided
    if data.project_id:
        project = await Project.select().where(Project.id == data.project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found",
            )

    # Generate key
    key = APIKey.generate_key()
    key_prefix = key[:12]
    key_hash = APIKey.hash_key(key)

    api_key = APIKey(
        name=data.name,
        key_hash=key_hash,
        key_prefix=key_prefix,
        project=data.project_id,
    )
    await api_key.save()

    # Return the full key only on creation
    return APIKeyResponse(
        id=api_key.id,
        name=api_key.name,
        key=key,  # Full key only returned once
        key_prefix=key_prefix,
        project_id=data.project_id,
        is_active=True,
        created_at=api_key.created_at,
        last_used_at=None,
    )


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(key_id: int, user: dict = Depends(require_auth)):
    """Revoke (deactivate) an API key."""
    api_key = await APIKey.select().where(APIKey.id == key_id).first()
    if not api_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")

    await APIKey.update({APIKey.is_active: 0}).where(APIKey.id == key_id)
    return None
