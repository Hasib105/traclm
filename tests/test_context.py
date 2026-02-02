"""Tests for SDK context management."""

from llm_tracer_sdk.context import (
    add_metadata,
    add_tag,
    clear_context,
    get_context,
    get_metadata,
    get_session,
    get_tags,
    get_user,
    set_metadata,
    set_session,
    set_tags,
    set_user,
    trace_context,
)


class TestContextManagement:
    """Tests for context management functions."""

    def setup_method(self):
        """Clear context before each test."""
        clear_context()

    def teardown_method(self):
        """Clear context after each test."""
        clear_context()

    def test_set_and_get_user(self):
        """Test setting and getting user."""
        set_user("user-123")
        assert get_user() == "user-123"

    def test_set_and_get_session(self):
        """Test setting and getting session."""
        set_session("session-456")
        assert get_session() == "session-456"

    def test_set_and_get_tags(self):
        """Test setting and getting tags."""
        set_tags(["tag1", "tag2"])
        assert get_tags() == ["tag1", "tag2"]

    def test_add_tag(self):
        """Test adding a single tag."""
        set_tags(["tag1"])
        add_tag("tag2")
        assert get_tags() == ["tag1", "tag2"]

    def test_add_tag_empty(self):
        """Test adding tag when empty."""
        add_tag("tag1")
        assert get_tags() == ["tag1"]

    def test_set_and_get_metadata(self):
        """Test setting and getting metadata."""
        set_metadata({"key": "value"})
        assert get_metadata() == {"key": "value"}

    def test_add_metadata(self):
        """Test adding to metadata."""
        set_metadata({"key1": "value1"})
        add_metadata("key2", "value2")
        assert get_metadata() == {"key1": "value1", "key2": "value2"}

    def test_add_metadata_empty(self):
        """Test adding metadata when empty."""
        add_metadata("key", "value")
        assert get_metadata() == {"key": "value"}

    def test_clear_context(self):
        """Test clearing context."""
        set_user("user-123")
        set_session("session-456")
        set_tags(["tag1"])
        set_metadata({"key": "value"})

        clear_context()

        assert get_user() is None
        assert get_session() is None
        assert get_tags() == []
        assert get_metadata() == {}

    def test_get_context(self):
        """Test getting full context."""
        set_user("user-123")
        set_session("session-456")
        set_tags(["tag1", "tag2"])
        set_metadata({"key": "value"})

        ctx = get_context()

        assert ctx["user_id"] == "user-123"
        assert ctx["session_id"] == "session-456"
        assert ctx["tags"] == ["tag1", "tag2"]
        assert ctx["metadata"] == {"key": "value"}


class TestTraceContext:
    """Tests for trace_context context manager."""

    def setup_method(self):
        """Clear context before each test."""
        clear_context()

    def teardown_method(self):
        """Clear context after each test."""
        clear_context()

    def test_trace_context_sets_values(self):
        """Test that trace_context sets values within block."""
        with trace_context(
            user_id="ctx-user", session_id="ctx-session", tags=["ctx-tag"], metadata={"ctx": "data"}
        ):
            assert get_user() == "ctx-user"
            assert get_session() == "ctx-session"
            assert get_tags() == ["ctx-tag"]
            assert get_metadata() == {"ctx": "data"}

    def test_trace_context_restores_values(self):
        """Test that trace_context restores previous values."""
        set_user("original-user")
        set_session("original-session")
        set_tags(["original-tag"])
        set_metadata({"original": "data"})

        with trace_context(
            user_id="new-user", session_id="new-session", tags=["new-tag"], metadata={"new": "data"}
        ):
            pass  # Values changed inside

        # Original values restored
        assert get_user() == "original-user"
        assert get_session() == "original-session"
        assert get_tags() == ["original-tag"]
        assert get_metadata() == {"original": "data"}

    def test_trace_context_partial_override(self):
        """Test trace_context with partial override."""
        set_user("original-user")
        set_session("original-session")

        with trace_context(user_id="new-user"):
            assert get_user() == "new-user"
            assert get_session() == "original-session"

    def test_trace_context_nested(self):
        """Test nested trace_context."""
        with trace_context(user_id="outer-user"):
            assert get_user() == "outer-user"

            with trace_context(user_id="inner-user"):
                assert get_user() == "inner-user"

            assert get_user() == "outer-user"

    def test_trace_context_with_exception(self):
        """Test that context is restored even on exception."""
        set_user("original-user")

        try:
            with trace_context(user_id="new-user"):
                raise ValueError("Test error")
        except ValueError:
            pass

        assert get_user() == "original-user"
