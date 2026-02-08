"""LangChain callback handler for LLM Tracer.

This module provides the core callback handler that captures LLM and tool
executions and sends them to the LLM Tracer server.
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult

if TYPE_CHECKING:
    from llm_tracer_sdk.client import TracerClient


class LLMTracerCallback(BaseCallbackHandler):
    """
    LangChain callback handler that tracks LLM and Tool calls.

    This callback is automatically injected by the SDK when you call `init()`.
    You typically don't need to use this class directly.

    Example (manual usage if needed):
        >>> from llm_tracer_sdk.callback import LLMTracerCallback
        >>> from langchain_openai import ChatOpenAI
        >>>
        >>> callback = LLMTracerCallback()
        >>> llm = ChatOpenAI(model="gpt-4")
        >>> response = llm.invoke("Hello!", config={"callbacks": [callback]})
    """

    def __init__(
        self,
        client: Optional["TracerClient"] = None,
        trace_id: str | None = None,
        parent_trace_id: str | None = None,
        session_id: str | None = None,
        user_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        tags: list[str] | None = None,
    ) -> None:
        """
        Initialize the callback handler.

        Args:
            client: TracerClient instance for sending traces.
            trace_id: Optional trace ID (auto-generated if not provided).
            parent_trace_id: Optional parent trace ID for nested traces.
            session_id: Optional session ID for grouping traces.
            user_id: Optional user ID for filtering.
            metadata: Optional metadata to attach to all traces.
            tags: Optional tags to attach to all traces.
        """
        super().__init__()
        self._client = client
        self.trace_id = trace_id or str(uuid.uuid4())
        self.parent_trace_id = parent_trace_id
        self.session_id = session_id
        self.user_id = user_id
        self.metadata = metadata or {}
        self.tags = tags or []
        self._trace_data: dict[str, Any] | None = None
        self._pending_tools: dict[str, dict[str, Any]] = {}
        self._start_time: datetime | None = None

    def _get_client(self) -> Optional["TracerClient"]:
        """Get the tracer client."""
        if self._client:
            return self._client

        from llm_tracer_sdk.client import get_client

        return get_client()

    def _serialize_message(self, msg: Any) -> dict[str, Any]:
        """Serialize a LangChain message to dict."""
        return {
            "type": msg.__class__.__name__,
            "content": getattr(msg, "content", str(msg)),
        }

    def on_chat_model_start(
        self,
        serialized: dict[str, Any],
        messages: list[list[Any]],
        *,
        run_id: uuid.UUID,
        **kwargs: Any,
    ) -> None:
        """Handle chat model start."""
        self._start_time = datetime.now()

        # Serialize messages
        msgs = []
        for msg_list in messages:
            for msg in msg_list:
                msgs.append(self._serialize_message(msg))

        # Extract model name
        invocation_params = kwargs.get("invocation_params", {})
        model_name = (
            invocation_params.get("model")
            or invocation_params.get("model_name")
            or serialized.get("kwargs", {}).get("model_name")
            or "unknown"
        )

        self._trace_data = {
            "trace_id": self.trace_id,
            "parent_trace_id": self.parent_trace_id,
            "model_name": model_name,
            "model_provider": serialized.get("id", ["unknown"])[-1]
            if serialized.get("id")
            else None,
            "status": "running",
            "input_data": {"messages": msgs},
            "output_data": {},
            "tool_calls": [],
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "start_time": self._start_time.isoformat(),
            "metadata": self.metadata,
            "tags": self.tags,
            "session_id": self.session_id,
            "user_id": self.user_id,
        }

        # Send initial trace
        client = self._get_client()
        if client:
            client.send_trace(self._trace_data)

    def on_llm_start(
        self,
        serialized: dict[str, Any],
        prompts: list[str],
        *,
        run_id: uuid.UUID,
        **kwargs: Any,
    ) -> None:
        """Handle LLM start (for non-chat models)."""
        self._start_time = datetime.now()

        model_name = (
            serialized.get("kwargs", {}).get("model_name")
            or serialized.get("kwargs", {}).get("model")
            or "unknown"
        )

        self._trace_data = {
            "trace_id": self.trace_id,
            "parent_trace_id": self.parent_trace_id,
            "model_name": model_name,
            "model_provider": serialized.get("id", ["unknown"])[-1]
            if serialized.get("id")
            else None,
            "status": "running",
            "input_data": {"prompts": prompts},
            "output_data": {},
            "tool_calls": [],
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "start_time": self._start_time.isoformat(),
            "metadata": self.metadata,
            "tags": self.tags,
            "session_id": self.session_id,
            "user_id": self.user_id,
        }

        client = self._get_client()
        if client:
            client.send_trace(self._trace_data)

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Handle LLM completion."""
        end_time = datetime.now()

        # Extract output
        output_data: dict[str, Any] = {}
        if response.generations:
            generations = []
            for gen_list in response.generations:
                for gen in gen_list:
                    generations.append({
                        "text": gen.text if hasattr(gen, "text") else str(gen),
                        "type": gen.__class__.__name__,
                    })
            output_data["generations"] = generations

        # Extract token usage
        token_usage = {}
        if response.llm_output:
            token_usage = response.llm_output.get("token_usage", {})

        # Calculate latency
        latency_ms = 0
        if self._start_time:
            latency_ms = int((end_time - self._start_time).total_seconds() * 1000)

        update_data = {
            "status": "success",
            "output_data": output_data,
            "prompt_tokens": token_usage.get("prompt_tokens", 0),
            "completion_tokens": token_usage.get("completion_tokens", 0),
            "total_tokens": token_usage.get("total_tokens", 0),
            "end_time": end_time.isoformat(),
            "latency_ms": latency_ms,
        }

        client = self._get_client()
        if client:
            client.update_trace(self.trace_id, update_data)

    def on_llm_error(self, error: BaseException, **kwargs: Any) -> None:
        """Handle LLM error."""
        end_time = datetime.now()

        latency_ms = 0
        if self._start_time:
            latency_ms = int((end_time - self._start_time).total_seconds() * 1000)

        update_data = {
            "status": "error",
            "error_message": str(error),
            "end_time": end_time.isoformat(),
            "latency_ms": latency_ms,
        }

        client = self._get_client()
        if client:
            client.update_trace(self.trace_id, update_data)

    def on_tool_start(
        self,
        serialized: dict[str, Any],
        input_str: str,
        *,
        run_id: uuid.UUID,
        **kwargs: Any,
    ) -> None:
        """Handle tool start."""
        tool_name = serialized.get("name", "unknown")
        self._pending_tools[str(run_id)] = {
            "name": tool_name,
            "input": input_str,
            "start_time": datetime.now().isoformat(),
        }

    def on_tool_end(self, output: str, *, run_id: uuid.UUID, **kwargs: Any) -> None:
        """Handle tool completion."""
        tool_data = self._pending_tools.pop(str(run_id), None)
        if not tool_data:
            return

        tool_data["output"] = output
        tool_data["end_time"] = datetime.now().isoformat()
        tool_data["status"] = "success"

        # Update trace with tool call
        if self._trace_data:
            tool_calls = self._trace_data.get("tool_calls", [])
            tool_calls.append(tool_data)

            client = self._get_client()
            if client:
                client.update_trace(self.trace_id, {"tool_calls": tool_calls})

    def on_tool_error(
        self, error: BaseException, *, run_id: uuid.UUID, **kwargs: Any
    ) -> None:
        """Handle tool error."""
        tool_data = self._pending_tools.pop(str(run_id), None)
        if not tool_data:
            return

        tool_data["error"] = str(error)
        tool_data["end_time"] = datetime.now().isoformat()
        tool_data["status"] = "error"

        if self._trace_data:
            tool_calls = self._trace_data.get("tool_calls", [])
            tool_calls.append(tool_data)

            client = self._get_client()
            if client:
                client.update_trace(self.trace_id, {"tool_calls": tool_calls})
