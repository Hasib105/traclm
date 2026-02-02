"""Tests for Piccolo database tables."""

from llm_tracer.db.tables import APIKey, LLMTrace, Project


class TestProjectTable:
    """Tests for Project table."""

    def test_project_fields(self):
        """Test Project has required fields."""
        project = Project()

        assert hasattr(project, "id")
        assert hasattr(project, "name")
        assert hasattr(project, "description")
        assert hasattr(project, "created_at")
        assert hasattr(project, "updated_at")

    def test_project_table_name(self):
        """Test Project table name."""
        assert Project._table_str == "project"


class TestAPIKeyTable:
    """Tests for APIKey table."""

    def test_api_key_fields(self):
        """Test APIKey has required fields."""
        api_key = APIKey()

        assert hasattr(api_key, "id")
        assert hasattr(api_key, "key")
        assert hasattr(api_key, "name")
        assert hasattr(api_key, "project")
        assert hasattr(api_key, "is_active")
        assert hasattr(api_key, "created_at")
        assert hasattr(api_key, "last_used_at")

    def test_api_key_table_name(self):
        """Test APIKey table name."""
        assert APIKey._table_str == "api_key"


class TestLLMTraceTable:
    """Tests for LLMTrace table."""

    def test_trace_fields(self):
        """Test LLMTrace has required fields."""
        trace = LLMTrace()

        # Core fields
        assert hasattr(trace, "id")
        assert hasattr(trace, "trace_id")
        assert hasattr(trace, "parent_trace_id")
        assert hasattr(trace, "project")

        # Model info
        assert hasattr(trace, "model_name")
        assert hasattr(trace, "model_provider")

        # Status
        assert hasattr(trace, "status")
        assert hasattr(trace, "error_message")

        # Data
        assert hasattr(trace, "input_data")
        assert hasattr(trace, "output_data")
        assert hasattr(trace, "tool_calls")

        # Metrics
        assert hasattr(trace, "prompt_tokens")
        assert hasattr(trace, "completion_tokens")
        assert hasattr(trace, "total_tokens")
        assert hasattr(trace, "latency_ms")

        # Timestamps
        assert hasattr(trace, "start_time")
        assert hasattr(trace, "end_time")
        assert hasattr(trace, "created_at")

        # Context
        assert hasattr(trace, "metadata")
        assert hasattr(trace, "tags")
        assert hasattr(trace, "session_id")
        assert hasattr(trace, "user_id")

    def test_trace_table_name(self):
        """Test LLMTrace table name."""
        assert LLMTrace._table_str == "llm_trace"


class TestTableRelationships:
    """Tests for table relationships."""

    def test_api_key_project_relationship(self):
        """Test APIKey has project foreign key."""

        # Check that project is a ForeignKey
        project_field = APIKey.project
        assert project_field is not None

    def test_trace_project_relationship(self):
        """Test LLMTrace has project foreign key."""
        project_field = LLMTrace.project
        assert project_field is not None
