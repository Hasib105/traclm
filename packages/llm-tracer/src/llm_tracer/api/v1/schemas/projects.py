"""Project schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    """Schema for creating a project."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class ProjectResponse(BaseModel):
    """Schema for project response."""

    id: int
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
