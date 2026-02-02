"""
Context management for LLM Tracer SDK.

Provides thread-local and async-safe context for trace metadata.
"""

import contextvars
import uuid
from typing import Any

# Context variables for trace metadata
_trace_id: contextvars.ContextVar[str | None] = contextvars.ContextVar("trace_id", default=None)
_session_id: contextvars.ContextVar[str | None] = contextvars.ContextVar("session_id", default=None)
_user_id: contextvars.ContextVar[str | None] = contextvars.ContextVar("user_id", default=None)
_tags: contextvars.ContextVar[list] = contextvars.ContextVar("tags", default=[])
_metadata: contextvars.ContextVar[dict] = contextvars.ContextVar("metadata", default={})


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
    """Add a single metadata key-value pair."""
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
    """Get the current trace ID."""
    return _trace_id.get()


def new_trace_id() -> str:
    """Generate and set a new trace ID."""
    trace_id = str(uuid.uuid4())
    _trace_id.set(trace_id)
    return trace_id


def clear_context() -> None:
    """Clear all context variables."""
    _trace_id.set(None)
    _session_id.set(None)
    _user_id.set(None)
    _tags.set([])
    _metadata.set({})


class trace_context:
    """
    Context manager for setting trace context.

    Example:
        >>> with llm_tracer_sdk.trace_context(user="john", session="abc"):
        ...     llm.invoke("Hello")
    """

    def __init__(
        self,
        user: str | None = None,
        session: str | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        self.user = user
        self.session = session
        self.tags = tags
        self.metadata = metadata
        self._prev_user = None
        self._prev_session = None
        self._prev_tags = None
        self._prev_metadata = None

    def __enter__(self):
        self._prev_user = get_user()
        self._prev_session = get_session()
        self._prev_tags = get_tags()
        self._prev_metadata = get_metadata()

        if self.user:
            set_user(self.user)
        if self.session:
            set_session(self.session)
        if self.tags:
            set_tags(self.tags)
        if self.metadata:
            set_metadata(self.metadata)

        return self

    def __exit__(self, *args):
        if self._prev_user:
            set_user(self._prev_user)
        if self._prev_session:
            set_session(self._prev_session)
        if self._prev_tags:
            set_tags(self._prev_tags)
        if self._prev_metadata:
            set_metadata(self._prev_metadata)
