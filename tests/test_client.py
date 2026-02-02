"""Tests for the TracerClient."""

import time
from unittest.mock import MagicMock, patch

from llm_tracer_sdk.client import TracerClient


class TestTracerClient:
    """Tests for TracerClient."""

    def test_init(self):
        """Test client initialization."""
        client = TracerClient(api_key="lt-test-key", endpoint="http://localhost:8000")

        assert client.api_key == "lt-test-key"
        assert client.endpoint == "http://localhost:8000"
        assert client._running is False

    def test_start(self):
        """Test starting the client."""
        client = TracerClient(api_key="lt-test-key", endpoint="http://localhost:8000")

        client.start()
        assert client._running is True
        assert client._worker is not None
        assert client._worker.is_alive()

        client.stop()

    def test_stop(self):
        """Test stopping the client."""
        client = TracerClient(api_key="lt-test-key", endpoint="http://localhost:8000")

        client.start()
        client.stop()

        assert client._running is False

    def test_stop_not_started(self):
        """Test stopping when not started."""
        client = TracerClient(api_key="lt-test-key", endpoint="http://localhost:8000")

        # Should not raise
        client.stop()

    def test_send_trace(self):
        """Test sending a trace."""
        client = TracerClient(api_key="lt-test-key", endpoint="http://localhost:8000")
        client.start()

        trace_data = {"trace_id": "test-123", "model_name": "gpt-4"}
        client.send_trace(trace_data)

        # Allow time for queue processing
        time.sleep(0.1)

        # Trace should be in pending
        assert "test-123" in client._pending_traces

        client.stop()

    def test_update_trace(self):
        """Test updating a trace."""
        client = TracerClient(api_key="lt-test-key", endpoint="http://localhost:8000")
        client.start()

        # Send initial trace
        trace_data = {"trace_id": "test-123", "status": "running"}
        client.send_trace(trace_data)
        time.sleep(0.1)

        # Update trace
        client.update_trace("test-123", {"status": "success"})
        time.sleep(0.1)

        # Check update was applied
        assert client._pending_traces.get("test-123", {}).get("status") == "success"

        client.stop()

    def test_update_nonexistent_trace(self):
        """Test updating a trace that doesn't exist."""
        client = TracerClient(api_key="lt-test-key", endpoint="http://localhost:8000")
        client.start()

        # Should not raise
        client.update_trace("nonexistent", {"status": "success"})

        client.stop()

    def test_flush(self):
        """Test flushing traces."""
        client = TracerClient(api_key="lt-test-key", endpoint="http://localhost:8000")

        with patch.object(client, "_send_traces") as mock_send:
            client.start()

            trace_data = {"trace_id": "test-123", "status": "success"}
            client.send_trace(trace_data)
            time.sleep(0.1)

            client.flush()

            # Flush should trigger send
            time.sleep(0.2)

        client.stop()

    def test_context_manager(self):
        """Test using client as context manager."""
        with TracerClient(api_key="lt-test-key", endpoint="http://localhost:8000") as client:
            assert client._running is True

        assert client._running is False


class TestTracerClientHTTP:
    """Tests for TracerClient HTTP operations."""

    @patch("httpx.post")
    def test_send_traces_success(self, mock_post):
        """Test successful trace sending."""
        mock_post.return_value = MagicMock(status_code=200, json=lambda: {"success": True})

        client = TracerClient(api_key="lt-test-key", endpoint="http://localhost:8000")

        traces = [{"trace_id": "test-123"}]
        client._send_traces(traces)

        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "X-API-Key" in call_args.kwargs["headers"]

    @patch("httpx.post")
    def test_send_traces_failure(self, mock_post):
        """Test trace sending failure handling."""
        mock_post.side_effect = Exception("Network error")

        client = TracerClient(api_key="lt-test-key", endpoint="http://localhost:8000")

        traces = [{"trace_id": "test-123"}]

        # Should not raise
        client._send_traces(traces)

    @patch("httpx.post")
    def test_batch_sending(self, mock_post):
        """Test batch trace sending."""
        mock_post.return_value = MagicMock(status_code=200)

        client = TracerClient(api_key="lt-test-key", endpoint="http://localhost:8000", batch_size=2)

        traces = [
            {"trace_id": "test-1"},
            {"trace_id": "test-2"},
            {"trace_id": "test-3"},
        ]
        client._send_traces(traces)

        # Should be called twice for batch of 2
        assert mock_post.call_count == 2
