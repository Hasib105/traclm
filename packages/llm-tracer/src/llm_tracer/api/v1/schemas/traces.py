"""Trace schemas for API requests and responses."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class IngestTrace(BaseModel):
    """Schema for ingesting a trace from SDK."""

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
    start_time: str | None = None
    end_time: str | None = None
    latency_ms: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    session_id: str | None = None
    user_id: str | None = None


class IngestBatch(BaseModel):
    """Schema for batch trace ingestion."""

    traces: list[IngestTrace]


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
    end_time: str | None = None
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
    """Schema for paginated trace list response."""

    traces: list[TraceResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
