"""Tests for the SDK initialization and core functionality."""

import os
from unittest.mock import MagicMock, patch

import pytest

import llm_tracer_sdk
import llm_tracer_sdk.sdk as sdk_mod
from llm_tracer_sdk.sdk import (
    get_config,
    get_trace_id,
    init,
    is_initialized,
    shutdown,
)


class TestSDKInit:
    """Tests for SDK initialization."""

    def setup_method(self):
        """Reset state before each test."""
        sdk_mod._initialized = False
        sdk_mod._config = None

    def teardown_method(self):
        """Clean up after each test."""
        if is_initialized():
            shutdown()

    def test_init_with_api_key(self):
        """Test initialization with API key."""
        with patch("llm_tracer_sdk.instrumentation.instrument_langchain"):
            with patch("llm_tracer_sdk.client.get_client") as mock_get_client:
                mock_get_client.return_value = MagicMock()
                init(api_key="lt-test-key", endpoint="http://localhost:8000")

        assert is_initialized()

    def test_init_with_env_var(self, mock_env_vars):
        """Test initialization with environment variable."""
        with patch("llm_tracer_sdk.instrumentation.instrument_langchain"):
            with patch("llm_tracer_sdk.client.get_client") as mock_get_client:
                mock_get_client.return_value = MagicMock()
                init()

        assert is_initialized()

    def test_init_without_api_key_does_not_initialize(self):
        """Test that init without API key does not initialize (logs warning)."""
        with patch.dict(os.environ, {}, clear=True):
            init(api_key=None)

        assert not is_initialized()

    def test_init_already_initialized(self):
        """Test that double init logs warning."""
        with patch("llm_tracer_sdk.instrumentation.instrument_langchain"):
            with patch("llm_tracer_sdk.client.get_client") as mock_get_client:
                mock_get_client.return_value = MagicMock()
                init(api_key="lt-test-key")

        with patch("llm_tracer_sdk.sdk.logger") as mock_logger:
            init(api_key="lt-test-key")
            mock_logger.warning.assert_called_once()

    def test_shutdown(self):
        """Test SDK shutdown."""
        with patch("llm_tracer_sdk.instrumentation.instrument_langchain"):
            with patch("llm_tracer_sdk.client.get_client") as mock_get_client:
                mock_get_client.return_value = MagicMock()
                init(api_key="lt-test-key")

        assert is_initialized()

        with patch("llm_tracer_sdk.instrumentation.uninstrument_langchain"):
            with patch("llm_tracer_sdk.client.get_client") as mock_get_client:
                mock_get_client.return_value = MagicMock()
                shutdown()

        assert not is_initialized()

    def test_shutdown_not_initialized(self):
        """Test shutdown when not initialized."""
        # Should not raise
        shutdown()

    def test_get_trace_id_not_initialized(self):
        """Test getting trace ID when not initialized."""
        trace_id = get_trace_id()
        assert trace_id is None

    def test_get_config(self):
        """Test getting config."""
        with patch("llm_tracer_sdk.instrumentation.instrument_langchain"):
            with patch("llm_tracer_sdk.client.get_client") as mock_get_client:
                mock_get_client.return_value = MagicMock()
                init(api_key="lt-test-key", endpoint="http://localhost:8000")

        config = get_config()
        assert config is not None
        assert config.api_key == "lt-test-key"
        assert config.endpoint == "http://localhost:8000"

    def test_get_config_not_initialized(self):
        """Test getting config when not initialized."""
        config = get_config()
        assert config is None


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
