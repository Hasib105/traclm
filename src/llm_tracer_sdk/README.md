# LLM Tracer SDK

Python SDK for LLM Tracer - trace your LangChain and LangGraph applications.

## Installation

```bash
pip install llm-tracer-sdk
```

## Quick Start

```python
import llm_tracer_sdk
from langchain_openai import ChatOpenAI

# Configure
llm_tracer_sdk.configure(
    api_key="lt-your-api-key",
    endpoint="http://localhost:8000"
)

# Wrap your LLM
llm = llm_tracer_sdk.TrackerLLM(ChatOpenAI(model="gpt-4"))

# Use as normal - all calls traced!
response = llm.invoke("Hello!")
```

See the [main README](../README.md) for full documentation.
