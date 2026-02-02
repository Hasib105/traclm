"""Tests for LangChain callback handler."""

import uuid
from datetime import datetime
from unittest.mock import MagicMock

from llm_tracer_sdk.callback import LLMTrackerCallback


class TestLLMTrackerCallback:
    """Tests for LLMTrackerCallback."""

    def test_init_default(self):
        """Test default initialization."""
        callback = LLMTrackerCallback()

        assert callback.trace_id is not None
        assert callback.parent_trace_id is None
        assert callback.session_id is None
        assert callback.user_id is None
        assert callback.metadata == {}
        assert callback.tags == []

    def test_init_with_values(self):
        """Test initialization with custom values."""
        callback = LLMTrackerCallback(
            trace_id="custom-trace",
            parent_trace_id="parent-trace",
            session_id="session-123",
            user_id="user-456",
            metadata={"key": "value"},
            tags=["tag1", "tag2"],
        )

        assert callback.trace_id == "custom-trace"
        assert callback.parent_trace_id == "parent-trace"
        assert callback.session_id == "session-123"
        assert callback.user_id == "user-456"
        assert callback.metadata == {"key": "value"}
        assert callback.tags == ["tag1", "tag2"]

    def test_init_with_client(self):
        """Test initialization with client."""
        mock_client = MagicMock()
        callback = LLMTrackerCallback(client=mock_client)

        assert callback._get_client() == mock_client

    def test_get_client_no_client(self):
        """Test _get_client when no client set."""
        callback = LLMTrackerCallback()
        assert callback._get_client() is None


class TestCallbackEvents:
    """Tests for callback event handlers."""

    def test_on_chat_model_start(self, mock_langchain_message):
        """Test on_chat_model_start handler."""
        mock_client = MagicMock()
        callback = LLMTrackerCallback(client=mock_client)

        serialized = {"id": ["langchain", "chat_models", "openai"]}
        messages = [[mock_langchain_message]]
        run_id = uuid.uuid4()
        invocation_params = {"model": "gpt-4"}

        callback.on_chat_model_start(
            serialized=serialized,
            messages=messages,
            run_id=run_id,
            invocation_params=invocation_params,
        )

        assert callback._trace_data is not None
        assert callback._trace_data["model_name"] == "gpt-4"
        assert callback._trace_data["status"] == "running"
        mock_client.send_trace.assert_called_once()

    def test_on_llm_start(self):
        """Test on_llm_start handler."""
        mock_client = MagicMock()
        callback = LLMTrackerCallback(client=mock_client)

        serialized = {"kwargs": {"model_name": "text-davinci-003"}}
        prompts = ["Hello, world!"]
        run_id = uuid.uuid4()

        callback.on_llm_start(serialized=serialized, prompts=prompts, run_id=run_id)

        assert callback._trace_data is not None
        assert callback._trace_data["model_name"] == "text-davinci-003"
        mock_client.send_trace.assert_called_once()

    def test_on_llm_end(self, mock_llm_result):
        """Test on_llm_end handler."""
        mock_client = MagicMock()
        callback = LLMTrackerCallback(client=mock_client)

        # Simulate start first
        callback._trace_data = {"trace_id": "test-123"}
        callback._start_time = datetime.now()

        callback.on_llm_end(response=mock_llm_result, run_id=uuid.uuid4())

        mock_client.update_trace.assert_called_once()
        call_args = mock_client.update_trace.call_args
        assert call_args[0][0] == "test-123"
        assert call_args[0][1]["status"] == "success"

    def test_on_llm_end_no_trace_data(self, mock_llm_result):
        """Test on_llm_end with no trace data."""
        mock_client = MagicMock()
        callback = LLMTrackerCallback(client=mock_client)

        # No trace_data set
        callback.on_llm_end(response=mock_llm_result, run_id=uuid.uuid4())

        # Should not call update
        mock_client.update_trace.assert_not_called()

    def test_on_llm_error(self):
        """Test on_llm_error handler."""
        mock_client = MagicMock()
        callback = LLMTrackerCallback(client=mock_client)

        # Simulate start first
        callback._trace_data = {"trace_id": "test-123"}
        callback._start_time = datetime.now()

        error = ValueError("Test error")
        callback.on_llm_error(error=error, run_id=uuid.uuid4())

        mock_client.update_trace.assert_called_once()
        call_args = mock_client.update_trace.call_args
        assert call_args[0][1]["status"] == "error"
        assert "Test error" in call_args[0][1]["error_message"]

    def test_on_llm_error_no_trace_data(self):
        """Test on_llm_error with no trace data."""
        mock_client = MagicMock()
        callback = LLMTrackerCallback(client=mock_client)

        error = ValueError("Test error")
        callback.on_llm_error(error=error, run_id=uuid.uuid4())

        mock_client.update_trace.assert_not_called()


class TestToolEvents:
    """Tests for tool event handlers."""

    def test_on_tool_start(self):
        """Test on_tool_start handler."""
        callback = LLMTrackerCallback()

        serialized = {"name": "calculator"}
        input_str = "2 + 2"
        run_id = uuid.uuid4()

        callback.on_tool_start(serialized=serialized, input_str=input_str, run_id=run_id)

        assert str(run_id) in callback._pending_tools
        assert callback._pending_tools[str(run_id)]["name"] == "calculator"
        assert callback._pending_tools[str(run_id)]["input"] == "2 + 2"

    def test_on_tool_end(self):
        """Test on_tool_end handler."""
        mock_client = MagicMock()
        callback = LLMTrackerCallback(client=mock_client)

        run_id = uuid.uuid4()
        callback._trace_data = {"trace_id": "test-123", "tool_calls": []}
        callback._pending_tools[str(run_id)] = {
            "name": "calculator",
            "input": "2 + 2",
            "status": "running",
        }

        callback.on_tool_end(output="4", run_id=run_id)

        mock_client.update_trace.assert_called_once()
        call_args = mock_client.update_trace.call_args
        tool_calls = call_args[0][1]["tool_calls"]
        assert len(tool_calls) == 1
        assert tool_calls[0]["output"] == "4"
        assert tool_calls[0]["status"] == "success"

    def test_on_tool_end_no_pending(self):
        """Test on_tool_end with no pending tool."""
        mock_client = MagicMock()
        callback = LLMTrackerCallback(client=mock_client)

        callback.on_tool_end(output="4", run_id=uuid.uuid4())

        mock_client.update_trace.assert_not_called()

    def test_on_tool_error(self):
        """Test on_tool_error handler."""
        mock_client = MagicMock()
        callback = LLMTrackerCallback(client=mock_client)

        run_id = uuid.uuid4()
        callback._trace_data = {"trace_id": "test-123", "tool_calls": []}
        callback._pending_tools[str(run_id)] = {
            "name": "calculator",
            "input": "2 / 0",
            "status": "running",
        }

        error = ZeroDivisionError("division by zero")
        callback.on_tool_error(error=error, run_id=run_id)

        mock_client.update_trace.assert_called_once()
        call_args = mock_client.update_trace.call_args
        tool_calls = call_args[0][1]["tool_calls"]
        assert tool_calls[0]["status"] == "error"
        assert "division by zero" in tool_calls[0]["error"]

    def test_on_tool_error_no_pending(self):
        """Test on_tool_error with no pending tool."""
        mock_client = MagicMock()
        callback = LLMTrackerCallback(client=mock_client)

        error = ValueError("Test error")
        callback.on_tool_error(error=error, run_id=uuid.uuid4())

        mock_client.update_trace.assert_not_called()


class TestMessageSerialization:
    """Tests for message serialization."""

    def test_serialize_message(self, mock_langchain_message):
        """Test message serialization."""
        callback = LLMTrackerCallback()

        result = callback._serialize_message(mock_langchain_message)

        assert result["type"] == "HumanMessage"
        assert result["content"] == "Test message"

    def test_serialize_message_no_content(self):
        """Test serializing message without content attribute."""
        callback = LLMTrackerCallback()

        mock_msg = MagicMock()
        mock_msg.__class__.__name__ = "CustomMessage"
        del mock_msg.content  # Remove content attribute
        mock_msg.__str__ = lambda self: "string representation"

        result = callback._serialize_message(mock_msg)

        assert result["type"] == "CustomMessage"
