"""LLM Tracer - A LangSmith-like tracer for LangChain and LangGraph."""

try:
    from importlib.metadata import version
    __version__ = version("llm-tracer")
except Exception:
    __version__ = "0.1.0"
