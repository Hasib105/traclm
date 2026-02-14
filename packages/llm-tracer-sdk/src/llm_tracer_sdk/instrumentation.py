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
        from langchain_core.language_models import BaseChatModel, BaseLLM
    except ImportError:
        logger.warning("langchain-core not installed. Auto-instrumentation disabled.")
        return

    classes_to_patch = [Runnable, BaseChatModel, BaseLLM]

    for cls in classes_to_patch:
        name = cls.__name__
        # Patch invoke
        if hasattr(cls, "invoke") and cls.invoke != Runnable.invoke:
             # Only patch if it's not already patched via inheritance or we are ensuring it
             # Actually, simpler to just patch them all if they exist in the class dict or are distinct
             pass

    # Simple approach: Patch Runnable, BaseChatModel, BaseLLM explicit methods
    # We use a helper to patch
    _patch_class(Runnable, "Runnable")
    _patch_class(BaseChatModel, "BaseChatModel")
    _patch_class(BaseLLM, "BaseLLM")

    _instrumented = True
    logger.debug("LangChain instrumentation complete")

def _patch_class(cls: Any, cls_name: str) -> None:
    """Helper to patch a class."""
    for method in ["invoke", "ainvoke", "stream", "astream", "batch", "abatch"]:
        if hasattr(cls, method):
            original = getattr(cls, method)
            # Check if already patched to avoid double wrapping if we call this multiple times improperly
            # or if it inherits from a patched class and we don't want to re-wrap?
            # Actually, we should check if 'original' is already our wrapper.
            if getattr(original, "_is_tracer_wrapper", False):
                continue
            
            # Use wrapped method
            if method.startswith("a"):
                wrapped = _wrap_async_method(original, method)
            else:
                wrapped = _wrap_method(original, method)
            
            wrapped._is_tracer_wrapper = True # Mark as ours
            
            _original_methods[f"{cls_name}.{method}"] = original
            setattr(cls, method, wrapped)


def uninstrument_langchain() -> None:
    """Remove instrumentation from LangChain."""
    global _instrumented

    if not _instrumented:
        return

    try:
        from langchain_core.runnables import Runnable
        from langchain_core.language_models import BaseChatModel, BaseLLM
        classes = {"Runnable": Runnable, "BaseChatModel": BaseChatModel, "BaseLLM": BaseLLM}
    except ImportError:
        return

    # Restore original methods
    for key, method in _original_methods.items():
        cls_name, method_name = key.split(".")
        if cls_name in classes:
            setattr(classes[cls_name], method_name, method)

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
             # Check if config is in args (usually 2nd positional arg for invoke/stream/batch)
             # invoke(self, input, config=None, ...)
             if len(args) > 1:
                 # Config is likely the 2nd argument
                 try:
                     config = args[1]
                     new_config = _inject_callback(config, callback)
                     args_list = list(args)
                     args_list[1] = new_config
                     args = tuple(args_list)
                 except Exception:
                     # Fallback if args manipulation fails
                     pass
             else:
                 # Config is in kwargs or using default
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
             if len(args) > 1:
                 try:
                     config = args[1]
                     new_config = _inject_callback(config, callback)
                     args_list = list(args)
                     args_list[1] = new_config
                     args = tuple(args_list)
                 except Exception:
                     pass
             else:
                 kwargs["config"] = _inject_callback(kwargs.get("config"), callback)

        return await original(self, *args, **kwargs)

    return wrapper
