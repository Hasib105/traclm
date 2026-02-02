"""Example usage of LLM Tracer SDK with LangChain.

This demonstrates the Sentry-like auto-instrumentation pattern.
Just call init() once and all LangChain calls are automatically traced!
"""

import atexit
import os

# Import and initialize the SDK - that's it!
import llm_tracer_sdk

# Initialize the SDK with your API key
# This automatically instruments all LangChain LLMs, chains, and agents
llm_tracer_sdk.init(
    api_key=os.getenv("LLM_TRACER_API_KEY", "lt-your-api-key-here"),
    endpoint=os.getenv("LLM_TRACER_ENDPOINT", "http://localhost:8000"),
    debug=True,  # Enable debug logging
)

# Ensure clean shutdown
atexit.register(llm_tracer_sdk.shutdown)


def example_basic():
    """Basic usage - no wrappers needed!"""
    from langchain_openai import ChatOpenAI

    # Just use LangChain normally - tracing is automatic!
    llm = ChatOpenAI(model="gpt-4o-mini")

    # All calls are traced automatically
    response = llm.invoke("What is the capital of France?")
    print(f"Response: {response.content}")


def example_with_context():
    """Example with user/session context."""
    from langchain_openai import ChatOpenAI

    # Set user and session context
    llm_tracer_sdk.set_user("user-123")
    llm_tracer_sdk.set_session("session-456")
    llm_tracer_sdk.set_tags(["example", "demo"])
    llm_tracer_sdk.set_metadata({"environment": "development"})

    llm = ChatOpenAI(model="gpt-4o-mini")
    response = llm.invoke("What is 2 + 2?")
    print(f"Response: {response.content}")


def example_with_tools():
    """Example with tool calling - all automatically traced."""
    from langchain_core.tools import tool
    from langchain_openai import ChatOpenAI

    @tool
    def get_weather(city: str) -> str:
        """Get the current weather for a city."""
        weather_data = {
            "Paris": "Sunny, 22°C",
            "London": "Cloudy, 15°C",
            "New York": "Rainy, 18°C",
        }
        return weather_data.get(city, f"Weather data not available for {city}")

    @tool
    def search_web(query: str) -> str:
        """Search the web for information."""
        return f"Search results for: {query}"

    # No wrapper needed - just bind tools normally
    llm = ChatOpenAI(model="gpt-4o-mini")
    llm_with_tools = llm.bind_tools([get_weather, search_web])

    # Tracing is automatic, including tool calls
    response = llm_with_tools.invoke("What's the weather like in Paris?")
    print(f"Response: {response}")


def example_trace_context():
    """Example using trace context for custom metadata per-operation."""
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(model="gpt-4o-mini")

    # Use context manager for specific trace context
    with llm_tracer_sdk.trace_context(
        user_id="custom-user",
        session_id="custom-session",
        tags=["context-example"],
        metadata={"feature": "demo"},
    ):
        response = llm.invoke("Tell me a joke")
        print(f"Response: {response.content}")


async def example_async():
    """Async example - also automatically traced."""
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(model="gpt-4o-mini")

    response = await llm.ainvoke("What is 2 + 2?")
    print(f"Async Response: {response.content}")


def example_streaming():
    """Streaming example - streaming is also traced."""
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(model="gpt-4o-mini")

    print("Streaming response: ", end="")
    for chunk in llm.stream("Count from 1 to 5"):
        print(chunk.content, end="", flush=True)
    print()  # New line at end


def example_chain():
    """Example with LangChain chains - entire chain is traced."""
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_openai import ChatOpenAI

    # Build a chain normally
    prompt = ChatPromptTemplate.from_messages(
        [("system", "You are a helpful assistant."), ("user", "{question}")]
    )
    llm = ChatOpenAI(model="gpt-4o-mini")
    chain = prompt | llm | StrOutputParser()

    # The entire chain execution is traced automatically
    response = chain.invoke({"question": "What is Python?"})
    print(f"Chain Response: {response}")


if __name__ == "__main__":
    print("=" * 50)
    print("LLM Tracer SDK Examples")
    print("Auto-instrumentation - No wrappers needed!")
    print("=" * 50)

    # Make sure you have OPENAI_API_KEY set
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  Warning: OPENAI_API_KEY not set. Examples will fail.")
        print("Set it with: export OPENAI_API_KEY='your-key'")
        exit(1)

    print("\n1. Basic Example (No wrappers!)")
    print("-" * 30)
    try:
        example_basic()
    except Exception as e:
        print(f"Error: {e}")

    print("\n2. Context Example")
    print("-" * 30)
    try:
        example_with_context()
    except Exception as e:
        print(f"Error: {e}")

    print("\n3. Tools Example")
    print("-" * 30)
    try:
        example_with_tools()
    except Exception as e:
        print(f"Error: {e}")

    print("\n4. Trace Context Example")
    print("-" * 30)
    try:
        example_trace_context()
    except Exception as e:
        print(f"Error: {e}")

    print("\n5. Streaming Example")
    print("-" * 30)
    try:
        example_streaming()
    except Exception as e:
        print(f"Error: {e}")

    print("\n6. Chain Example")
    print("-" * 30)
    try:
        example_chain()
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 50)
    print("Done! Check your traces at http://localhost:8000/traces")
    print("=" * 50)
