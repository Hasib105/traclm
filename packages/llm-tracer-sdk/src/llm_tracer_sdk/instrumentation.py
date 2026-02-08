"""
Auto-instrumentation for LangChain.

This module patches LangChain to automatically add tracing callbacks.
"""

import functools
import logging
import random
from collections.abc import Callable
from typing import Any

logger = logging.getLogger("llm_tracer_sdk")

# Store original methods for uninstrumentation
_original_methods: dict[str, Any] = {}
_instrumented = False


def instrument_langchain() -> None:
    """
    Instrument LangChain to automatically trace all LLM calls.

    This patches the base Runnable class to inject our callback.
    """
    global _instrumented

    if _instrumented:
        return

    try:
        from langchain_core.runnables import Runnable
    except ImportError:
        logger.warning("langchain-core not installed. Auto-instrumentation disabled.")
        return

    # Patch invoke
    if hasattr(Runnable, "invoke"):
        _original_methods["Runnable.invoke"] = Runnable.invoke
        Runnable.invoke = _wrap_method(Runnable.invoke, "invoke")

    # Patch ainvoke
    if hasattr(Runnable, "ainvoke"):
        _original_methods["Runnable.ainvoke"] = Runnable.ainvoke
        Runnable.ainvoke = _wrap_async_method(Runnable.ainvoke, "ainvoke")

    # Patch stream
    if hasattr(Runnable, "stream"):
        _original_methods["Runnable.stream"] = Runnable.stream
        Runnable.stream = _wrap_method(Runnable.stream, "stream")

    # Patch astream
    if hasattr(Runnable, "astream"):
        _original_methods["Runnable.astream"] = Runnable.astream
        Runnable.astream = _wrap_async_method(Runnable.astream, "astream")

    # Patch batch
    if hasattr(Runnable, "batch"):
        _original_methods["Runnable.batch"] = Runnable.batch
        Runnable.batch = _wrap_method(Runnable.batch, "batch")

    # Patch abatch
    if hasattr(Runnable, "abatch"):
        _original_methods["Runnable.abatch"] = Runnable.abatch
        Runnable.abatch = _wrap_async_method(Runnable.abatch, "abatch")

    _instrumented = True
    logger.debug("LangChain instrumentation complete")


def uninstrument_langchain() -> None:
    """Remove instrumentation from LangChain."""
    global _instrumented

    if not _instrumented:
        return

    try:
        from langchain_core.runnables import Runnable
    except ImportError:
        return

    # Restore original methods
    for key, method in _original_methods.items():
        cls_name, method_name = key.split(".")
        if cls_name == "Runnable":
            setattr(Runnable, method_name, method)

    _original_methods.clear()
    _instrumented = False
    logger.debug("LangChain uninstrumentation complete")


def _should_trace(obj: Any) -> bool:
    """Determine if this object should be traced."""
    from llm_tracer_sdk.sdk import get_config

    config = get_config()
    if not config or not config.enabled:
        return False

    # Sample rate check
    if config.sample_rate < 1.0:
        if random.random() > config.sample_rate:
            return False

    # Check if it's an LLM-like object (has model-related attributes)
    is_llm = hasattr(obj, "model_name") or hasattr(obj, "model") or hasattr(obj, "llm")

    return is_llm


def _get_callback() -> Any:
    """Create a callback with current context."""
    from llm_tracer_sdk.callback import LLMTracerCallback
    from llm_tracer_sdk.context import get_metadata, get_session, get_tags, get_user
    from llm_tracer_sdk.sdk import get_config

    config = get_config()
    if not config:
        return None

    # Merge default and context metadata/tags
    metadata = {**config.default_metadata, **get_metadata()}
    tags = list(set(config.default_tags + get_tags()))

    return LLMTracerCallback(
        session_id=get_session(),
        user_id=get_user(),
        metadata=metadata,
        tags=tags,
    )


def _inject_callback(config: dict[str, Any] | None, callback: Any) -> dict[str, Any]:
    """Inject our callback into the config."""
    if config is None:
        config = {}
    else:
        config = dict(config)

    callbacks = list(config.get("callbacks", []) or [])
    callbacks.append(callback)
    config["callbacks"] = callbacks
    return config


def _wrap_method(original: Callable[..., Any], method_name: str) -> Callable[..., Any]:
    """Wrap a sync method to add tracing."""

    @functools.wraps(original)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        if not _should_trace(self):
            return original(self, *args, **kwargs)

        callback = _get_callback()
        if callback:
            kwargs["config"] = _inject_callback(kwargs.get("config"), callback)

        return original(self, *args, **kwargs)

    return wrapper


def _wrap_async_method(original: Callable[..., Any], method_name: str) -> Callable[..., Any]:
    """Wrap an async method to add tracing."""

    @functools.wraps(original)
    async def wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        if not _should_trace(self):
            return await original(self, *args, **kwargs)

        callback = _get_callback()
        if callback:
            kwargs["config"] = _inject_callback(kwargs.get("config"), callback)

        return await original(self, *args, **kwargs)

    return wrapper
