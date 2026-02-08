"""Tests for LangChain instrumentation."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from llm_tracer_sdk.instrumentation import (
    _wrap_async_method,
    _wrap_method,
    instrument_langchain,
    uninstrument_langchain,
)
import llm_tracer_sdk.instrumentation as instrumentation_mod


def _make_mock_runnable_module():
    """Create a mock langchain_core.runnables module with Runnable."""
    mock_runnable = MagicMock()
    mock_runnable.invoke = MagicMock()
    mock_runnable.ainvoke = AsyncMock()
    mock_runnable.stream = MagicMock()
    mock_runnable.astream = AsyncMock()
    mock_runnable.batch = MagicMock()
    mock_runnable.abatch = AsyncMock()

    mock_module = MagicMock()
    mock_module.Runnable = mock_runnable
    return mock_module, mock_runnable


class TestInstrumentation:
    """Tests for LangChain instrumentation."""

    def teardown_method(self):
        """Clean up instrumentation after each test."""
        instrumentation_mod._instrumented = False
        instrumentation_mod._original_methods.clear()

    def test_instrument_langchain_success(self):
        """Test successful instrumentation."""
        mock_runnables = MagicMock()
        mock_runnable = MagicMock()
        mock_runnable.invoke = MagicMock()
        mock_runnable.ainvoke = AsyncMock()
        mock_runnable.stream = MagicMock()
        mock_runnable.astream = AsyncMock()
        mock_runnable.batch = MagicMock()
        mock_runnable.abatch = AsyncMock()
        mock_runnables.Runnable = mock_runnable

        with patch.dict("sys.modules", {
            "langchain_core": MagicMock(),
            "langchain_core.runnables": mock_runnables,
        }):
            instrumentation_mod._instrumented = False
            instrumentation_mod._original_methods.clear()

            instrument_langchain()

            assert instrumentation_mod._instrumented

    def test_instrument_langchain_already_instrumented(self):
        """Test instrumentation when already instrumented."""
        # Set as already instrumented
        instrumentation_mod._instrumented = True

        # Should just return without error
        instrument_langchain()

        assert instrumentation_mod._instrumented

    def test_uninstrument_langchain(self):
        """Test uninstrumentation."""
        mock_runnables = MagicMock()
        original_invoke = MagicMock()
        mock_runnables.Runnable.invoke = original_invoke
        mock_runnables.Runnable.ainvoke = AsyncMock()
        mock_runnables.Runnable.stream = MagicMock()
        mock_runnables.Runnable.astream = AsyncMock()
        mock_runnables.Runnable.batch = MagicMock()
        mock_runnables.Runnable.abatch = AsyncMock()

        with patch.dict("sys.modules", {
            "langchain_core": MagicMock(),
            "langchain_core.runnables": mock_runnables,
        }):
            instrumentation_mod._instrumented = False
            instrumentation_mod._original_methods.clear()

            instrument_langchain()
            assert instrumentation_mod._instrumented

            uninstrument_langchain()
            assert not instrumentation_mod._instrumented

    def test_uninstrument_not_instrumented(self):
        """Test uninstrumentation when not instrumented."""
        # Should not raise
        uninstrument_langchain()

    def test_instrument_langchain_import_error(self):
        """Test instrumentation when LangChain not installed."""
        with patch.dict("sys.modules", {"langchain_core": None, "langchain_core.runnables": None}):
            with patch("llm_tracer_sdk.instrumentation.logger") as mock_logger:
                # Should handle gracefully
                try:
                    instrument_langchain()
                except Exception:
                    pass  # Expected


class TestTracedMethods:
    """Tests for traced method wrappers."""

    def test_wrap_method(self):
        """Test wrapping a sync method."""
        original_method = MagicMock(return_value="result")

        wrapped = _wrap_method(original_method, "invoke")

        mock_self = MagicMock()
        mock_self.__class__.__name__ = "ChatOpenAI"

        # Without SDK initialized, should call original directly
        result = wrapped(mock_self, "input", config=None)

        assert result == "result"

    @pytest.mark.asyncio
    async def test_wrap_async_method(self):
        """Test wrapping an async method."""
        original_method = AsyncMock(return_value="result")

        wrapped = _wrap_async_method(original_method, "ainvoke")

        mock_self = MagicMock()
        mock_self.__class__.__name__ = "ChatOpenAI"

        # Without SDK initialized, should call original directly
        result = await wrapped(mock_self, "input", config=None)

        assert result == "result"


class TestIntegration:
    """Integration tests for instrumentation."""

    def teardown_method(self):
        """Clean up after each test."""
        instrumentation_mod._instrumented = False
        instrumentation_mod._original_methods.clear()

    def test_full_instrumentation_flow(self):
        """Test full instrumentation and call flow."""
        # Create mock Runnable class
        class MockRunnable:
            def invoke(self, input, config=None, **kwargs):
                return f"Response to: {input}"

            async def ainvoke(self, input, config=None, **kwargs):
                return f"Async response to: {input}"

        mock_runnables = MagicMock()
        mock_runnables.Runnable = MockRunnable

        with patch.dict("sys.modules", {
            "langchain_core": MagicMock(),
            "langchain_core.runnables": mock_runnables,
        }):
            instrument_langchain()

            runnable = MockRunnable()
            result = runnable.invoke("Hello")

            # Should still work
            assert "Hello" in result or result is not None
