# LLM Tracer SDK

Python SDK for [LLM Tracer](https://github.com/yourusername/llm-tracer) - automatic tracing for LangChain and LangGraph applications.

## Installation

```bash
pip install llm-tracer-sdk
```

## Quick Start

```python
import llm_tracer_sdk

# Initialize once at startup - that's it!
llm_tracer_sdk.init(
    api_key="lt-your-api-key",
    endpoint="http://localhost:8000"  # Your LLM Tracer server
)

# All LangChain calls are now automatically traced!
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4")
response = llm.invoke("Hello!")  # <-- Automatically traced
```

## Configuration

### Environment Variables

```bash
export LLM_TRACER_API_KEY="lt-your-api-key"
export LLM_TRACER_ENDPOINT="http://localhost:8000"
```

### Programmatic Configuration

```python
llm_tracer_sdk.init(
    api_key="lt-xxx",
    endpoint="http://localhost:8000",
    enabled=True,           # Enable/disable tracing
    debug=False,            # Enable debug logging
    sample_rate=1.0,        # Trace 100% of requests (0.0-1.0)
    default_tags=["production"],
    default_metadata={"environment": "prod"},
)
```

## Context Management

Add context to your traces:

```python
# Set user/session for all subsequent traces
llm_tracer_sdk.set_user("user-123")
llm_tracer_sdk.set_session("session-456")
llm_tracer_sdk.set_tags(["chatbot", "customer-support"])

# Or use context manager for specific operations
with llm_tracer_sdk.trace_context(
    user_id="user-123",
    session_id="session-456",
    tags=["demo"],
    metadata={"feature": "chat"},
) as trace_id:
    response = llm.invoke("Hello!")
    print(f"Trace ID: {trace_id}")
```

## Manual Callback Usage

If you need more control, use the callback directly:

```python
from llm_tracer_sdk import LLMTracerCallback

callback = LLMTracerCallback(
    session_id="my-session",
    user_id="user-123",
    tags=["manual"],
)

response = llm.invoke("Hello!", config={"callbacks": [callback]})
```

## License

MIT
