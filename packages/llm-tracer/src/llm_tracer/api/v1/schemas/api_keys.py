"""API Key schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class APIKeyCreate(BaseModel):
    """Schema for creating an API key."""

    name: str = Field(..., min_length=1, max_length=255)
    project_id: int | None = None


class APIKeyResponse(BaseModel):
    """Schema for API key response."""

    id: int
    name: str
    key: str | None = None  # Only returned on creation
    key_prefix: str
    project_id: int | None
    is_active: bool
    created_at: datetime
    last_used_at: datetime | None
