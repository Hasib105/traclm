"""LLM Tracer - A LangSmith-like observability platform for LangChain/LangGraph."""

try:
    from importlib.metadata import version

    __version__ = version("llm-tracer")
except Exception:
    __version__ = "0.1.0"

from llm_tracer.app import create_app

__all__ = ["__version__", "create_app"]
