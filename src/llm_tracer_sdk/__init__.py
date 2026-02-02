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

from importlib.metadata import version

from llm_tracer_sdk.callback import LLMTrackerCallback
from llm_tracer_sdk.context import (
    add_metadata,
    add_tag,
    set_metadata,
    set_session,
    set_tags,
    set_user,
    trace_context,
)
from llm_tracer_sdk.sdk import get_trace_id, init, is_initialized, shutdown

__all__ = [
    "LLMTrackerCallback",
    "add_metadata",
    "add_tag",
    "get_trace_id",
    "init",
    "is_initialized",
    "set_metadata",
    "set_session",
    "set_tags",
    "set_user",
    "shutdown",
    "trace_context",
]

__version__ = version("llm-tracer")
