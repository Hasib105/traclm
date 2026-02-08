"""
Context management for LLM Tracer SDK.

Provides thread-local and async-safe context for trace metadata.
"""

import contextvars
import uuid
from contextlib import contextmanager
from typing import Any, Generator

# Context variables for trace metadata
_trace_id: contextvars.ContextVar[str | None] = contextvars.ContextVar("trace_id", default=None)
_session_id: contextvars.ContextVar[str | None] = contextvars.ContextVar("session_id", default=None)
_user_id: contextvars.ContextVar[str | None] = contextvars.ContextVar("user_id", default=None)
_tags: contextvars.ContextVar[list[str]] = contextvars.ContextVar("tags", default=[])
_metadata: contextvars.ContextVar[dict[str, Any]] = contextvars.ContextVar("metadata", default={})


def set_user(user_id: str) -> None:
    """
    Set the user ID for the current context.

    All traces in this context will be tagged with this user ID.

    Args:
        user_id: The user identifier (email, UUID, etc.)

    Example:
        >>> llm_tracer_sdk.set_user("user@example.com")
    """
    _user_id.set(user_id)


def get_user() -> str | None:
    """Get the current user ID."""
    return _user_id.get()


def set_session(session_id: str) -> None:
    """
    Set the session ID for the current context.

    Use this to group related traces together.

    Args:
        session_id: The session identifier.

    Example:
        >>> llm_tracer_sdk.set_session("conversation-123")
    """
    _session_id.set(session_id)


def get_session() -> str | None:
    """Get the current session ID."""
    return _session_id.get()


def set_tags(tags: list[str]) -> None:
    """
    Set tags for the current context.

    Tags are merged with default tags from init().

    Args:
        tags: List of tag strings.

    Example:
        >>> llm_tracer_sdk.set_tags(["production", "chatbot"])
    """
    _tags.set(list(tags))


def add_tag(tag: str) -> None:
    """Add a single tag to the current context."""
    current = list(_tags.get())
    if tag not in current:
        current.append(tag)
        _tags.set(current)


def get_tags() -> list[str]:
    """Get current context tags."""
    return list(_tags.get())


def set_metadata(metadata: dict[str, Any]) -> None:
    """
    Set metadata for the current context.

    Metadata is merged with default metadata from init().

    Args:
        metadata: Dictionary of metadata.

    Example:
        >>> llm_tracer_sdk.set_metadata({"environment": "prod", "version": "1.0"})
    """
    _metadata.set(dict(metadata))


def add_metadata(key: str, value: Any) -> None:
    """Add a single metadata key-value pair to the current context."""
    current = dict(_metadata.get())
    current[key] = value
    _metadata.set(current)


def get_metadata() -> dict[str, Any]:
    """Get current context metadata."""
    return dict(_metadata.get())


def set_trace_id(trace_id: str) -> None:
    """Set the current trace ID."""
    _trace_id.set(trace_id)


def get_current_trace_id() -> str | None:
    """Get the current trace ID if available."""
    return _trace_id.get()


def clear_context() -> None:
    """Clear all context variables."""
    _trace_id.set(None)
    _session_id.set(None)
    _user_id.set(None)
    _tags.set([])
    _metadata.set({})


def get_context() -> dict[str, Any]:
    """Get the full current context as a dictionary."""
    return {
        "user_id": get_user(),
        "session_id": get_session(),
        "tags": get_tags(),
        "metadata": get_metadata(),
        "trace_id": get_current_trace_id(),
    }


@contextmanager
def trace_context(
    user_id: str | None = None,
    session_id: str | None = None,
    tags: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
    trace_id: str | None = None,
) -> Generator[str, None, None]:
    """
    Context manager for setting trace context.

    Use this to set context for a specific block of code.

    Args:
        user_id: User ID for this context.
        session_id: Session ID for this context.
        tags: Tags for this context.
        metadata: Metadata for this context.
        trace_id: Optional trace ID (auto-generated if not provided).

    Yields:
        The trace ID for this context.

    Example:
        >>> with llm_tracer_sdk.trace_context(user_id="user-123", tags=["demo"]) as trace_id:
        ...     response = llm.invoke("Hello!")
        ...     print(f"Trace ID: {trace_id}")
    """
    # Save current state
    old_trace_id = _trace_id.get()
    old_session_id = _session_id.get()
    old_user_id = _user_id.get()
    old_tags = _tags.get()
    old_metadata = _metadata.get()

    # Set new context
    new_trace_id = trace_id or str(uuid.uuid4())
    _trace_id.set(new_trace_id)

    if user_id is not None:
        _user_id.set(user_id)
    if session_id is not None:
        _session_id.set(session_id)
    if tags is not None:
        _tags.set(tags)
    if metadata is not None:
        _metadata.set(metadata)

    try:
        yield new_trace_id
    finally:
        # Restore old state
        _trace_id.set(old_trace_id)
        _session_id.set(old_session_id)
        _user_id.set(old_user_id)
        _tags.set(old_tags)
        _metadata.set(old_metadata)
