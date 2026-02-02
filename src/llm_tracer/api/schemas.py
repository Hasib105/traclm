"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

# ============== Project Schemas ==============


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


# ============== API Key Schemas ==============


class APIKeyCreate(BaseModel):
    """Schema for creating an API key."""

    name: str = Field(..., min_length=1, max_length=255)
    project_id: int


class APIKeyResponse(BaseModel):
    """Schema for API key response."""

    id: int
    key: str
    name: str
    project_id: int
    is_active: bool
    created_at: datetime
    last_used_at: datetime | None


# ============== Trace Schemas ==============


class TraceCreate(BaseModel):
    """Schema for creating a trace via SDK."""

    trace_id: str
    parent_trace_id: str | None = None
    model_name: str = "unknown"
    model_provider: str | None = None
    status: str = "running"
    error_message: str | None = None
    input_data: dict[str, Any] = Field(default_factory=dict)
    output_data: dict[str, Any] = Field(default_factory=dict)
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost_cents: int = 0
    start_time: datetime | None = None
    end_time: datetime | None = None
    latency_ms: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    session_id: str | None = None
    user_id: str | None = None


class TraceUpdate(BaseModel):
    """Schema for updating a trace."""

    status: str | None = None
    error_message: str | None = None
    output_data: dict[str, Any] | None = None
    tool_calls: list[dict[str, Any]] | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    cost_cents: int | None = None
    end_time: datetime | None = None
    latency_ms: int | None = None
    metadata: dict[str, Any] | None = None
    tags: list[str] | None = None


class TraceResponse(BaseModel):
    """Schema for trace response."""

    id: int
    trace_id: str
    parent_trace_id: str | None
    project_id: int | None
    model_name: str
    model_provider: str | None
    status: str
    error_message: str | None
    input_data: dict[str, Any]
    output_data: dict[str, Any]
    tool_calls: list[dict[str, Any]]
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_cents: int
    start_time: datetime
    end_time: datetime | None
    latency_ms: int
    metadata: dict[str, Any]
    tags: list[str]
    session_id: str | None
    user_id: str | None


class TraceListResponse(BaseModel):
    """Schema for trace list response."""

    traces: list[TraceResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============== Ingest Schemas (for SDK) ==============


class IngestTrace(BaseModel):
    """Schema for ingesting trace data from SDK."""

    trace_id: str
    parent_trace_id: str | None = None
    model_name: str = "unknown"
    model_provider: str | None = None
    status: str = "running"
    error_message: str | None = None
    input_data: dict[str, Any] = Field(default_factory=dict)
    output_data: dict[str, Any] = Field(default_factory=dict)
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    start_time: str | None = None
    end_time: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    session_id: str | None = None
    user_id: str | None = None


class IngestBatch(BaseModel):
    """Schema for batch ingesting traces."""

    traces: list[IngestTrace]
