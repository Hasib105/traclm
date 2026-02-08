"""Tests for the TracerClient."""

from unittest.mock import MagicMock, patch

from llm_tracer_sdk.client import TracerClient, get_client, reset_client


class TestTracerClient:
    """Tests for TracerClient."""

    def test_init(self):
        """Test client initialization."""
        client = TracerClient()

        assert client._started is False
        assert client._queue.empty()

    def test_start(self):
        """Test starting the client."""
        client = TracerClient()

        client.start()
        assert client._started is True
        assert client._worker_thread is not None
        assert client._worker_thread.is_alive()

        client.shutdown()

    def test_start_idempotent(self):
        """Test that calling start() twice is safe."""
        client = TracerClient()

        client.start()
        thread1 = client._worker_thread

        client.start()
        thread2 = client._worker_thread

        # Should be the same thread
        assert thread1 is thread2

        client.shutdown()

    def test_shutdown(self):
        """Test stopping the client."""
        client = TracerClient()

        client.start()
        client.shutdown()

        assert client._started is False

    def test_shutdown_not_started(self):
        """Test shutdown when not started."""
        client = TracerClient()

        # Should not raise
        client.shutdown()

    def test_send_trace(self):
        """Test queueing a trace."""
        client = TracerClient()

        mock_config = MagicMock(enabled=True)
        with patch.object(TracerClient, "config", new_callable=lambda: property(lambda self: mock_config)):
            client.send_trace({"trace_id": "test-123", "model_name": "gpt-4"})

        assert not client._queue.empty()
        item = client._queue.get_nowait()
        assert item["action"] == "send"
        assert item["data"]["trace_id"] == "test-123"

    def test_send_trace_disabled(self):
        """Test that send_trace is a no-op when disabled."""
        client = TracerClient()

        with patch.object(TracerClient, "config", new_callable=lambda: property(lambda self: None)):
            client.send_trace({"trace_id": "test-123"})

        assert client._queue.empty()

    def test_update_trace(self):
        """Test queueing a trace update."""
        client = TracerClient()

        mock_config = MagicMock(enabled=True)
        with patch.object(TracerClient, "config", new_callable=lambda: property(lambda self: mock_config)):
            client.update_trace("test-123", {"status": "success"})

        assert not client._queue.empty()
        item = client._queue.get_nowait()
        assert item["action"] == "update"
        assert item["trace_id"] == "test-123"
        assert item["data"]["status"] == "success"

    def test_flush(self):
        """Test flushing the queue."""
        client = TracerClient()

        # Manually enqueue items
        client._queue.put({"action": "send", "data": {"trace_id": "test-1"}})
        client._queue.put({"action": "send", "data": {"trace_id": "test-2"}})

        mock_config = MagicMock(enabled=True)
        with patch.object(TracerClient, "config", new_callable=lambda: property(lambda self: mock_config)):
            with patch.object(client, "_process_item") as mock_process:
                client.flush()

        assert mock_process.call_count == 2
        assert client._queue.empty()


class TestTracerClientSingleton:
    """Tests for singleton client management."""

    def teardown_method(self):
        """Clean up singleton."""
        reset_client()

    def test_get_client_returns_singleton(self):
        """Test get_client returns the same instance."""
        client1 = get_client()
        client2 = get_client()

        assert client1 is client2

    def test_reset_client(self):
        """Test reset_client replaces the singleton."""
        client1 = get_client()
        reset_client()
        client2 = get_client()

        assert client1 is not client2


class TestTracerClientHTTP:
    """Tests for TracerClient HTTP operations."""

    def test_process_item_send(self):
        """Test processing a send item."""
        client = TracerClient()
        mock_config = MagicMock(
            enabled=True,
            endpoint="http://localhost:8000",
            debug=False,
        )

        with patch.object(type(client), "config", new_callable=lambda: property(lambda self: mock_config)):
            with patch("llm_tracer_sdk.client.httpx.Client") as mock_http_cls:
                mock_http = MagicMock()
                mock_http.__enter__ = MagicMock(return_value=mock_http)
                mock_http.__exit__ = MagicMock(return_value=False)
                mock_http.post.return_value = MagicMock(status_code=200)
                mock_http_cls.return_value = mock_http

                client._process_item({"action": "send", "data": {"trace_id": "test-1"}})

                mock_http.post.assert_called_once()

    def test_process_item_update(self):
        """Test processing an update item."""
        client = TracerClient()
        mock_config = MagicMock(
            enabled=True,
            endpoint="http://localhost:8000",
            debug=False,
        )

        with patch.object(type(client), "config", new_callable=lambda: property(lambda self: mock_config)):
            with patch("llm_tracer_sdk.client.httpx.Client") as mock_http_cls:
                mock_http = MagicMock()
                mock_http.__enter__ = MagicMock(return_value=mock_http)
                mock_http.__exit__ = MagicMock(return_value=False)
                mock_http.patch.return_value = MagicMock(status_code=200)
                mock_http_cls.return_value = mock_http

                client._process_item({"action": "update", "trace_id": "t-1", "data": {"status": "success"}})

                mock_http.patch.assert_called_once()

    def test_process_item_disabled(self):
        """Test processing when disabled does nothing."""
        client = TracerClient()
        mock_config = MagicMock(enabled=False)

        with patch.object(type(client), "config", new_callable=lambda: property(lambda self: mock_config)):
            with patch("llm_tracer_sdk.client.httpx.Client") as mock_http_cls:
                client._process_item({"action": "send", "data": {"trace_id": "test-1"}})
                mock_http_cls.assert_not_called()
