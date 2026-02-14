"""LLM Trace model for storing trace data."""

from datetime import datetime
from enum import Enum

from piccolo.columns import JSON, UUID, ForeignKey, Integer, Text, Timestamp, Varchar
from piccolo.table import Table

from llm_tracer.db.models.project import Project


class TraceStatus(str, Enum):
    """Status of an LLM trace."""

    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"


class LLMTrace(Table):
    """Individual LLM trace record."""

    trace_id = Varchar(index=True)
    parent_trace_id = Varchar(null=True, index=True)
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
