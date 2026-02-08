"""
LLM Tracer SDK - Main initialization and auto-instrumentation.

This module provides Sentry-like initialization where you just call init()
and all LangChain/LangGraph calls are automatically traced.
"""

import atexit
import logging
import os
import threading
from typing import Any

from llm_tracer_sdk.types import SDKConfig

logger = logging.getLogger("llm_tracer_sdk")

# Global state
_initialized = False
_config: SDKConfig | None = None
_lock = threading.Lock()


def init(
    api_key: str | None = None,
    endpoint: str | None = None,
    enabled: bool = True,
    debug: bool = False,
    batch_size: int = 10,
    flush_interval: float = 5.0,
    sample_rate: float = 1.0,
    default_tags: list[str] | None = None,
    default_metadata: dict[str, Any] | None = None,
) -> None:
    """
    Initialize LLM Tracer SDK. Call this once at application startup.

    After calling init(), all LangChain LLM calls will be automatically traced.

    Args:
        api_key: Your LLM Tracer API key. Falls back to LLM_TRACER_API_KEY env var.
        endpoint: Server endpoint. Falls back to LLM_TRACER_ENDPOINT or localhost:8000.
        enabled: Whether tracing is enabled. Set to False to disable.
        debug: Enable debug logging.
        batch_size: Number of traces to batch before sending.
        flush_interval: How often to flush traces (seconds).
        sample_rate: Sampling rate (0.0 to 1.0). 1.0 traces everything.
        default_tags: Default tags to add to all traces.
        default_metadata: Default metadata to add to all traces.

    Example:
        >>> import llm_tracer_sdk
        >>> llm_tracer_sdk.init(api_key="lt-xxx")
        >>>
        >>> # Now all LangChain calls are traced automatically!
        >>> from langchain_openai import ChatOpenAI
        >>> llm = ChatOpenAI()
        >>> llm.invoke("Hello!")  # Traced!
    """
    global _initialized, _config

    with _lock:
        if _initialized:
            logger.warning(
                "LLM Tracer SDK already initialized. Call shutdown() first to reinitialize."
            )
            return

        # Resolve configuration
        resolved_api_key = api_key or os.getenv("LLM_TRACER_API_KEY")
        if not resolved_api_key:
            if enabled:
                logger.warning(
                    "LLM Tracer SDK: No API key provided. "
                    "Set api_key parameter or LLM_TRACER_API_KEY environment variable. "
                    "Tracing disabled."
                )
            return

        resolved_endpoint = endpoint or os.getenv(
            "LLM_TRACER_ENDPOINT", "http://localhost:8000"
        )

        _config = SDKConfig(
            api_key=resolved_api_key,
            endpoint=resolved_endpoint,
            enabled=enabled,
            debug=debug,
            batch_size=batch_size,
            flush_interval=flush_interval,
            sample_rate=sample_rate,
            default_tags=default_tags or [],
            default_metadata=default_metadata or {},
        )

        # Configure logging
        if debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.setLevel(logging.DEBUG)
            logger.debug("LLM Tracer SDK debug mode enabled")

        # Instrument LangChain
        from llm_tracer_sdk.instrumentation import instrument_langchain

        instrument_langchain()

        # Start the background sender
        from llm_tracer_sdk.client import get_client

        client = get_client()
        client.start()

        # Register shutdown handler
        atexit.register(shutdown)

        _initialized = True
        logger.info(f"LLM Tracer SDK initialized. Endpoint: {resolved_endpoint}")


def shutdown() -> None:
    """
    Shutdown the SDK and flush any pending traces.

    Called automatically at program exit, but can be called manually.
    """
    global _initialized, _config

    with _lock:
        if not _initialized:
            return

        logger.debug("Shutting down LLM Tracer SDK...")

        # Flush and stop the client
        from llm_tracer_sdk.client import get_client

        client = get_client()
        client.shutdown()

        # Uninstrument
        from llm_tracer_sdk.instrumentation import uninstrument_langchain

        uninstrument_langchain()

        _initialized = False
        _config = None
        logger.info("LLM Tracer SDK shutdown complete")


def is_initialized() -> bool:
    """Check if SDK is initialized."""
    return _initialized


def get_config() -> SDKConfig | None:
    """Get current SDK configuration."""
    return _config


def get_trace_id() -> str | None:
    """Get the current trace ID if available."""
    from llm_tracer_sdk.context import get_current_trace_id

    return get_current_trace_id()
