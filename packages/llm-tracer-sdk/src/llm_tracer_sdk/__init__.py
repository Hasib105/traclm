"""LLM Tracer SDK - Automatic tracing for LangChain and LangGraph.

Usage:
    import llm_tracer_sdk

    # Initialize once at startup - that's it!
    llm_tracer_sdk.init(
        api_key="lt-your-api-key",
        endpoint="http://localhost:8000"
    )

    # All LangChain calls are now automatically traced!
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-4")
    response = llm.invoke("Hello!")  # <-- Automatically traced
"""

try:
    from importlib.metadata import version

    __version__ = version("llm-tracer-sdk")
except Exception:
    __version__ = "0.1.0"

from llm_tracer_sdk.callback import LLMTracerCallback
from llm_tracer_sdk.context import (
    add_metadata,
    add_tag,
    get_current_trace_id,
    set_metadata,
    set_session,
    set_tags,
    set_user,
    trace_context,
)
from llm_tracer_sdk.sdk import get_trace_id, init, is_initialized, shutdown

__all__ = [
    # Core SDK functions
    "init",
    "shutdown",
    "is_initialized",
    "get_trace_id",
    # Context management
    "set_user",
    "set_session",
    "set_tags",
    "add_tag",
    "set_metadata",
    "add_metadata",
    "get_current_trace_id",
    "trace_context",
    # Callback (for manual usage)
    "LLMTracerCallback",
    # Version
    "__version__",
]
