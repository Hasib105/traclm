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

    # Check sample rate
    if config.sample_rate < 1.0 and random.random() > config.sample_rate:
        return False

    # Only trace language models
    try:
        from langchain_core.language_models.base import BaseLanguageModel

        if isinstance(obj, BaseLanguageModel):
            return True
    except ImportError:
        pass

    return False


def _inject_callback(config: dict | None, _obj: Any) -> dict:
    """Inject our callback into the config."""
    from llm_tracer_sdk import context
    from llm_tracer_sdk.callback import LLMTrackerCallback
    from llm_tracer_sdk.sdk import get_config

    sdk_config = get_config()
    if not sdk_config:
        return config or {}

    config = dict(config) if config else {}

    # Get existing callbacks
    callbacks = list(config.get("callbacks", []) or [])

    # Check if we already have our callback
    for cb in callbacks:
        if isinstance(cb, LLMTrackerCallback):
            return config

    # Merge context with defaults
    tags = list(sdk_config.default_tags) + context.get_tags()
    metadata = {**sdk_config.default_metadata, **context.get_metadata()}

    # Create our callback
    tracker = LLMTrackerCallback(
        session_id=context.get_session(),
        user_id=context.get_user(),
        metadata=metadata,
        tags=tags,
    )

    callbacks.append(tracker)
    config["callbacks"] = callbacks

    return config


def _wrap_method(original: Callable, _method_name: str) -> Callable:
    """Wrap a sync method to inject tracing."""

    @functools.wraps(original)
    def wrapper(self, *args, **kwargs):
        if not _should_trace(self):
            return original(self, *args, **kwargs)

        # Get config from args
        config = None
        if len(args) >= 2:
            config = args[1]
            args = (args[0], *args[2:])
        else:
            config = kwargs.pop("config", None)

        # Inject callback
        config = _inject_callback(config, self)

        return original(self, args[0] if args else kwargs.get("input"), config=config, **kwargs)

    return wrapper


def _wrap_async_method(original: Callable, _method_name: str) -> Callable:
    """Wrap an async method to inject tracing."""

    @functools.wraps(original)
    async def wrapper(self, *args, **kwargs):
        if not _should_trace(self):
            return await original(self, *args, **kwargs)

        # Get config from args
        config = None
        if len(args) >= 2:
            config = args[1]
            args = (args[0], *args[2:])
        else:
            config = kwargs.pop("config", None)

        # Inject callback
        config = _inject_callback(config, self)

        return await original(
            self, args[0] if args else kwargs.get("input"), config=config, **kwargs
        )

    return wrapper
