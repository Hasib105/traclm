"""Type definitions for LLM Tracer SDK."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SDKConfig:
    """SDK configuration."""

    api_key: str
    endpoint: str = "http://localhost:8000"
    enabled: bool = True
    debug: bool = False
    batch_size: int = 10
    flush_interval: float = 5.0
    sample_rate: float = 1.0  # 1.0 = trace everything
    default_tags: list[str] = field(default_factory=list)
    default_metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Normalize endpoint URL."""
        self.endpoint = self.endpoint.rstrip("/")


@dataclass
class TraceData:
    """Trace data structure for sending to server."""

    trace_id: str
    model_name: str = "unknown"
    model_provider: str | None = None
    status: str = "running"
    error_message: str | None = None
    input_data: dict[str, Any] = field(default_factory=dict)
    output_data: dict[str, Any] = field(default_factory=dict)
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    start_time: str | None = None
    end_time: str | None = None
    latency_ms: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    session_id: str | None = None
    user_id: str | None = None
    parent_trace_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "trace_id": self.trace_id,
            "parent_trace_id": self.parent_trace_id,
            "model_name": self.model_name,
            "model_provider": self.model_provider,
            "status": self.status,
            "error_message": self.error_message,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "tool_calls": self.tool_calls,
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "latency_ms": self.latency_ms,
            "metadata": self.metadata,
            "tags": self.tags,
            "session_id": self.session_id,
            "user_id": self.user_id,
        }
