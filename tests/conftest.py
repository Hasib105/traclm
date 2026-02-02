"""Test configuration and fixtures for pytest."""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_env_vars():
    """Mock environment variables."""
    with patch.dict(
        os.environ,
        {
            "LLM_TRACER_API_KEY": "lt-test-api-key",
            "LLM_TRACER_ENDPOINT": "http://localhost:8000",
        },
    ):
        yield


@pytest.fixture
def sample_trace_data():
    """Sample trace data for testing."""
    return {
        "trace_id": "test-trace-123",
        "model_name": "gpt-4",
        "model_provider": "openai",
        "status": "success",
        "input_data": {"messages": [{"type": "HumanMessage", "content": "Hello"}]},
        "output_data": {"output": [{"text": "Hi there!"}]},
        "tool_calls": [],
        "prompt_tokens": 10,
        "completion_tokens": 5,
        "total_tokens": 15,
        "latency_ms": 500,
        "start_time": "2024-01-01T00:00:00",
        "end_time": "2024-01-01T00:00:01",
        "metadata": {"env": "test"},
        "tags": ["test"],
        "session_id": "session-123",
        "user_id": "user-456",
    }


@pytest.fixture
def mock_langchain_llm():
    """Mock LangChain LLM for testing."""
    from unittest.mock import MagicMock

    mock = MagicMock()
    mock.invoke.return_value = MagicMock(content="Hello, World!")
    return mock


@pytest.fixture
def mock_langchain_message():
    """Mock LangChain message."""
    from unittest.mock import MagicMock

    mock = MagicMock()
    mock.__class__.__name__ = "HumanMessage"
    mock.content = "Test message"
    return mock


@pytest.fixture
def mock_llm_result():
    """Mock LLMResult for callback testing."""
    from unittest.mock import MagicMock

    mock = MagicMock()
    mock.generations = [
        [
            MagicMock(
                text="Generated text",
                message=MagicMock(
                    __class__=type("AIMessage", (), {}), content="Generated text", tool_calls=[]
                ),
            )
        ]
    ]
    mock.llm_output = {
        "token_usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
    }
    return mock


@pytest.fixture
async def async_client():
    """Create async HTTP client for API testing."""
    from httpx import AsyncClient

    from llm_tracer.main import app

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
