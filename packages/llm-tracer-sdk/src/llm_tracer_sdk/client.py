"""
HTTP client for sending traces to LLM Tracer server.
"""

import logging
import threading
from queue import Empty, Queue
from typing import Any, Optional

import httpx

logger = logging.getLogger("llm_tracer_sdk")

# Singleton client
_client: Optional["TracerClient"] = None
_client_lock = threading.Lock()


class TracerClient:
    """
    HTTP client for sending traces to the server.

    Uses background thread for non-blocking trace sending.
    """

    def __init__(self) -> None:
        self._queue: Queue[dict[str, Any]] = Queue()
        self._worker_thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._started = False

    @property
    def config(self) -> Any:
        """Get SDK config."""
        from llm_tracer_sdk.sdk import get_config

        return get_config()

    @property
    def _headers(self) -> dict[str, str]:
        """Get request headers with API key."""
        config = self.config
        if not config:
            return {}
        return {
            "Content-Type": "application/json",
            "X-API-Key": config.api_key,
        }

    def start(self) -> None:
        """Start the background worker thread."""
        if self._started:
            return

        self._stop_event.clear()
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()
        self._started = True
        logger.debug("Tracer client worker started")

    def _worker_loop(self) -> None:
        """Background worker loop for sending traces."""
        while not self._stop_event.is_set():
            try:
                config = self.config
                timeout = config.flush_interval if config else 5.0

                try:
                    item = self._queue.get(timeout=timeout)
                    self._process_item(item)
                except Empty:
                    pass  # Timeout, just continue

            except Exception as e:
                logger.error(f"Worker error: {e}")

    def _process_item(self, item: dict[str, Any]) -> None:
        """Process a queue item."""
        config = self.config
        if not config or not config.enabled:
            return

        action = item.get("action")

        try:
            with httpx.Client(timeout=30.0) as client:
                if action == "send":
                    response = client.post(
                        f"{config.endpoint}/api/v1/ingest/trace",
                        headers=self._headers,
                        json=item["data"],
                    )
                    if response.status_code not in (200, 201):
                        logger.warning(f"Failed to send trace: {response.status_code}")
                    elif config.debug:
                        logger.debug(f"Trace sent: {item['data'].get('trace_id')}")

                elif action == "update":
                    trace_id = item["trace_id"]
                    response = client.patch(
                        f"{config.endpoint}/api/v1/ingest/trace/{trace_id}",
                        headers=self._headers,
                        json=item["data"],
                    )
                    if response.status_code not in (200, 201):
                        logger.warning(f"Failed to update trace: {response.status_code}")
                    elif config.debug:
                        logger.debug(f"Trace updated: {trace_id}")

        except httpx.ConnectError:
            logger.warning("Cannot connect to LLM Tracer server")
        except Exception as e:
            logger.error(f"Error sending trace: {e}")

    def send_trace(self, trace_data: dict[str, Any]) -> None:
        """Queue a trace for sending."""
        if not self.config or not self.config.enabled:
            return

        self._queue.put({"action": "send", "data": trace_data})

    def update_trace(self, trace_id: str, update_data: dict[str, Any]) -> None:
        """Queue a trace update."""
        if not self.config or not self.config.enabled:
            return

        self._queue.put({"action": "update", "trace_id": trace_id, "data": update_data})

    def flush(self) -> None:
        """Flush all pending traces synchronously."""
        config = self.config
        if not config:
            return

        while not self._queue.empty():
            try:
                item = self._queue.get_nowait()
                self._process_item(item)
            except Empty:
                break

    def shutdown(self) -> None:
        """Shutdown the client and flush pending traces."""
        logger.debug("Shutting down tracer client...")

        self._stop_event.set()
        self.flush()

        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout=5.0)

        self._started = False
        logger.debug("Tracer client shutdown complete")


def get_client() -> TracerClient:
    """Get or create the singleton tracer client."""
    global _client

    with _client_lock:
        if _client is None:
            _client = TracerClient()
        return _client


def reset_client() -> None:
    """Reset the singleton client (for testing)."""
    global _client

    with _client_lock:
        if _client is not None:
            _client.shutdown()
            _client = None
