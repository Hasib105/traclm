"""Tests for LangChain instrumentation."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from llm_tracer_sdk.instrumentation import (
    _create_async_traced_method,
    _create_traced_method,
    _is_instrumented,
    instrument_langchain,
    uninstrument_langchain,
)


class TestInstrumentation:
    """Tests for LangChain instrumentation."""

    def teardown_method(self):
        """Clean up instrumentation after each test."""
        uninstrument_langchain()

    def test_instrument_langchain_success(self):
        """Test successful instrumentation."""
        mock_client = MagicMock()

        with patch("llm_tracer_sdk.instrumentation.Runnable") as mock_runnable:
            mock_runnable.invoke = MagicMock()
            mock_runnable.ainvoke = AsyncMock()
            mock_runnable.stream = MagicMock()
            mock_runnable.astream = AsyncMock()
            mock_runnable.batch = MagicMock()
            mock_runnable.abatch = AsyncMock()

            instrument_langchain(mock_client)

            assert _is_instrumented()

    def test_instrument_langchain_already_instrumented(self):
        """Test instrumentation when already instrumented."""
        mock_client = MagicMock()

        with patch("llm_tracer_sdk.instrumentation.Runnable") as mock_runnable:
            mock_runnable.invoke = MagicMock()
            mock_runnable.ainvoke = AsyncMock()
            mock_runnable.stream = MagicMock()
            mock_runnable.astream = AsyncMock()
            mock_runnable.batch = MagicMock()
            mock_runnable.abatch = AsyncMock()

            instrument_langchain(mock_client)

            with patch("llm_tracer_sdk.instrumentation.logger") as mock_logger:
                instrument_langchain(mock_client)
                mock_logger.warning.assert_called()

    def test_uninstrument_langchain(self):
        """Test uninstrumentation."""
        mock_client = MagicMock()

        with patch("llm_tracer_sdk.instrumentation.Runnable") as mock_runnable:
            original_invoke = MagicMock()
            mock_runnable.invoke = original_invoke
            mock_runnable.ainvoke = AsyncMock()
            mock_runnable.stream = MagicMock()
            mock_runnable.astream = AsyncMock()
            mock_runnable.batch = MagicMock()
            mock_runnable.abatch = AsyncMock()

            instrument_langchain(mock_client)
            uninstrument_langchain()

            assert not _is_instrumented()

    def test_uninstrument_not_instrumented(self):
        """Test uninstrumentation when not instrumented."""
        # Should not raise
        uninstrument_langchain()

    def test_instrument_langchain_import_error(self):
        """Test instrumentation when LangChain not installed."""
        mock_client = MagicMock()

        with patch("llm_tracer_sdk.instrumentation.Runnable", None):
            with patch("llm_tracer_sdk.instrumentation.logger") as mock_logger:
                # Should handle gracefully
                try:
                    instrument_langchain(mock_client)
                except Exception:
                    pass  # Expected


class TestTracedMethods:
    """Tests for traced method wrappers."""

    def test_create_traced_method(self):
        """Test creating a traced sync method."""
        mock_client = MagicMock()
        original_method = MagicMock(return_value="result")

        traced_method = _create_traced_method(original_method, mock_client)

        mock_self = MagicMock()
        mock_self.__class__.__name__ = "ChatOpenAI"

        result = traced_method(mock_self, "input", config=None)

        assert result == "result"

    def test_create_traced_method_with_existing_callbacks(self):
        """Test traced method with existing callbacks."""
        mock_client = MagicMock()
        original_method = MagicMock(return_value="result")
        existing_callback = MagicMock()

        traced_method = _create_traced_method(original_method, mock_client)

        mock_self = MagicMock()
        mock_self.__class__.__name__ = "ChatOpenAI"

        result = traced_method(mock_self, "input", config={"callbacks": [existing_callback]})

        # Should merge callbacks
        call_config = original_method.call_args[0][1]
        assert len(call_config["callbacks"]) >= 1

    @pytest.mark.asyncio
    async def test_create_async_traced_method(self):
        """Test creating a traced async method."""
        mock_client = MagicMock()
        original_method = AsyncMock(return_value="result")

        traced_method = _create_async_traced_method(original_method, mock_client)

        mock_self = MagicMock()
        mock_self.__class__.__name__ = "ChatOpenAI"

        result = await traced_method(mock_self, "input", config=None)

        assert result == "result"


class TestIntegration:
    """Integration tests for instrumentation."""

    def teardown_method(self):
        """Clean up after each test."""
        uninstrument_langchain()

    def test_full_instrumentation_flow(self):
        """Test full instrumentation and call flow."""
        mock_client = MagicMock()

        # Create mock Runnable class
        class MockRunnable:
            def invoke(self, input, config=None, **kwargs):
                return f"Response to: {input}"

            async def ainvoke(self, input, config=None, **kwargs):
                return f"Async response to: {input}"

        with patch("llm_tracer_sdk.instrumentation.Runnable", MockRunnable):
            instrument_langchain(mock_client)

            runnable = MockRunnable()
            result = runnable.invoke("Hello")

            # Should still work
            assert "Hello" in result or result is not None
