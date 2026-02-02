"""Tests for the SDK initialization and core functionality."""

import os
from unittest.mock import patch

import pytest

import llm_tracer_sdk
from llm_tracer_sdk.sdk import (
    _state,
    get_client,
    get_trace_id,
    init,
    is_initialized,
    shutdown,
)


class TestSDKInit:
    """Tests for SDK initialization."""

    def setup_method(self):
        """Reset state before each test."""
        _state.clear()

    def teardown_method(self):
        """Clean up after each test."""
        if is_initialized():
            shutdown()

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        init(api_key="lt-test-key", endpoint="http://localhost:8000", auto_instrument=False)

        assert is_initialized()

    def test_init_with_env_var(self, mock_env_vars):
        """Test initialization with environment variable."""
        init(auto_instrument=False)

        assert is_initialized()

    def test_init_without_api_key_raises(self):
        """Test that init without API key raises ValueError."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="API key is required"):
                init(api_key=None, auto_instrument=False)

    def test_init_already_initialized(self):
        """Test that double init logs warning."""
        init(api_key="lt-test-key", auto_instrument=False)

        with patch("llm_tracer_sdk.sdk.logger") as mock_logger:
            init(api_key="lt-test-key", auto_instrument=False)
            mock_logger.warning.assert_called_once()

    def test_shutdown(self):
        """Test SDK shutdown."""
        init(api_key="lt-test-key", auto_instrument=False)
        assert is_initialized()

        shutdown()
        assert not is_initialized()

    def test_shutdown_not_initialized(self):
        """Test shutdown when not initialized."""
        # Should not raise
        shutdown()

    def test_get_trace_id(self):
        """Test getting trace ID."""
        init(api_key="lt-test-key", auto_instrument=False)

        trace_id = get_trace_id()
        assert trace_id is not None
        assert len(trace_id) > 0

    def test_get_trace_id_not_initialized(self):
        """Test getting trace ID when not initialized."""
        trace_id = get_trace_id()
        assert trace_id is None

    def test_get_client(self):
        """Test getting client."""
        init(api_key="lt-test-key", auto_instrument=False)

        client = get_client()
        assert client is not None

    def test_get_client_not_initialized(self):
        """Test getting client when not initialized."""
        client = get_client()
        assert client is None

    def test_init_with_debug_mode(self):
        """Test init with debug mode."""
        with patch("llm_tracer_sdk.sdk.logging") as mock_logging:
            init(api_key="lt-test-key", debug=True, auto_instrument=False)
            mock_logging.basicConfig.assert_called()

    def test_init_with_auto_instrument(self):
        """Test init with auto instrumentation."""
        with patch("llm_tracer_sdk.instrumentation.instrument_langchain") as mock_instrument:
            init(api_key="lt-test-key", auto_instrument=True)
            mock_instrument.assert_called_once()


class TestModuleExports:
    """Test that all exports are available."""

    def test_init_exported(self):
        """Test init is exported."""
        assert hasattr(llm_tracer_sdk, "init")

    def test_shutdown_exported(self):
        """Test shutdown is exported."""
        assert hasattr(llm_tracer_sdk, "shutdown")

    def test_is_initialized_exported(self):
        """Test is_initialized is exported."""
        assert hasattr(llm_tracer_sdk, "is_initialized")

    def test_get_trace_id_exported(self):
        """Test get_trace_id is exported."""
        assert hasattr(llm_tracer_sdk, "get_trace_id")

    def test_set_user_exported(self):
        """Test set_user is exported."""
        assert hasattr(llm_tracer_sdk, "set_user")

    def test_set_session_exported(self):
        """Test set_session is exported."""
        assert hasattr(llm_tracer_sdk, "set_session")

    def test_set_tags_exported(self):
        """Test set_tags is exported."""
        assert hasattr(llm_tracer_sdk, "set_tags")

    def test_set_metadata_exported(self):
        """Test set_metadata is exported."""
        assert hasattr(llm_tracer_sdk, "set_metadata")

    def test_add_tag_exported(self):
        """Test add_tag is exported."""
        assert hasattr(llm_tracer_sdk, "add_tag")

    def test_add_metadata_exported(self):
        """Test add_metadata is exported."""
        assert hasattr(llm_tracer_sdk, "add_metadata")

    def test_trace_context_exported(self):
        """Test trace_context is exported."""
        assert hasattr(llm_tracer_sdk, "trace_context")
