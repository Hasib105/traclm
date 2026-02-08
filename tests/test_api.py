"""Tests for FastAPI server routes."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


class _Awaitable:
    """Object that can be awaited, simulating Piccolo query results."""

    def __init__(self, result=None):
        self.result = result

    def __await__(self):
        async def _coro():
            return self.result

        return _coro().__await__()


class _ColumnMock:
    """Mock for Piccolo column attributes that supports comparison operators."""

    def __ge__(self, other):
        return True

    def __le__(self, other):
        return True

    def __gt__(self, other):
        return True

    def __lt__(self, other):
        return True


class TestHealthCheck:
    """Tests for health check endpoint."""

    @pytest.mark.asyncio
    async def test_health_check(self, async_client):
        """Test health check returns ok."""
        response = await async_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestProjectsAPI:
    """Tests for projects API endpoints."""

    @pytest.mark.asyncio
    async def test_create_project(self, async_client):
        """Test creating a project."""
        with patch("llm_tracer.api.v1.projects.Project") as MockProject:
            # select().where().first() -> None (no existing project)
            MockProject.select.return_value.where.return_value.first = AsyncMock(
                return_value=None
            )

            # Instance creation and save
            mock_instance = MagicMock()
            mock_instance.id = 1
            mock_instance.name = "Test Project"
            mock_instance.description = "A test project"
            mock_instance.created_at = datetime(2024, 1, 1)
            mock_instance.updated_at = datetime(2024, 1, 1)
            mock_instance.save = AsyncMock()
            MockProject.return_value = mock_instance

            response = await async_client.post(
                "/api/v1/projects", json={"name": "Test Project", "description": "A test project"}
            )

            assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_list_projects(self, async_client):
        """Test listing projects."""
        with patch("llm_tracer.api.v1.projects.Project") as MockProject:
            # select().order_by() -> awaitable returning []
            MockProject.select.return_value.order_by = AsyncMock(return_value=[])

            response = await async_client.get("/api/v1/projects")

            assert response.status_code == 200
            assert response.json() == []


class TestAPIKeysAPI:
    """Tests for API keys endpoints."""

    @pytest.mark.asyncio
    async def test_create_api_key(self, async_client):
        """Test creating an API key."""
        with patch("llm_tracer.api.v1.api_keys.Project") as MockProject:
            with patch("llm_tracer.api.v1.api_keys.APIKey") as MockAPIKey:
                # Project exists
                MockProject.select.return_value.where.return_value.first = AsyncMock(
                    return_value={"id": 1, "name": "Test"}
                )

                # Key generation
                MockAPIKey.generate_key.return_value = "lt-testkey12345678"
                MockAPIKey.hash_key.return_value = "hashed_value"

                # Instance
                mock_instance = MagicMock()
                mock_instance.id = 1
                mock_instance.name = "Test Key"
                mock_instance.key_prefix = "lt-testkey123"
                mock_instance.created_at = datetime(2024, 1, 1)
                mock_instance.save = AsyncMock()
                MockAPIKey.return_value = mock_instance

                response = await async_client.post(
                    "/api/v1/api-keys", json={"name": "Test Key", "project_id": 1}
                )

                assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_list_api_keys(self, async_client):
        """Test listing API keys."""
        with patch("llm_tracer.api.v1.api_keys.APIKey") as MockAPIKey:
            MockAPIKey.select.return_value.order_by = AsyncMock(return_value=[])

            response = await async_client.get("/api/v1/api-keys")

            assert response.status_code == 200
            assert response.json() == []


class TestTraceIngestion:
    """Tests for trace ingestion endpoints."""

    @pytest.mark.asyncio
    async def test_ingest_trace_no_auth(self):
        """Test ingestion without API key returns 401."""
        from httpx import ASGITransport, AsyncClient

        from llm_tracer.app import create_app

        app = create_app()
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/ingest/trace",
                json={"trace_id": "test-123", "model_name": "gpt-4"},
            )
            # No X-API-Key header -> require_api_key raises 401
            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_ingest_trace_with_auth(self, async_client):
        """Test ingestion with valid API key (auth overridden by fixture)."""
        with patch("llm_tracer.api.v1.ingest.LLMTrace") as MockTrace:
            mock_instance = MagicMock()
            mock_instance.save = AsyncMock()
            mock_instance.calculate_latency = MagicMock(return_value=0)
            MockTrace.return_value = mock_instance

            response = await async_client.post(
                "/api/v1/ingest/trace",
                json={"trace_id": "test-123", "model_name": "gpt-4", "status": "success"},
            )

            assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_ingest_batch(self, async_client):
        """Test batch ingestion."""
        with patch("llm_tracer.api.v1.ingest.LLMTrace") as MockTrace:
            mock_instance = MagicMock()
            mock_instance.save = AsyncMock()
            mock_instance.calculate_latency = MagicMock(return_value=0)
            MockTrace.return_value = mock_instance

            response = await async_client.post(
                "/api/v1/ingest/batch",
                json={
                    "traces": [
                        {"trace_id": "test-1", "model_name": "gpt-4"},
                        {"trace_id": "test-2", "model_name": "gpt-3.5"},
                    ]
                },
            )

            assert response.status_code == 201


class TestTraceQuery:
    """Tests for trace query endpoints."""

    @pytest.mark.asyncio
    async def test_list_traces(self, async_client):
        """Test listing traces."""
        with patch("llm_tracer.api.v1.traces.LLMTrace") as MockTrace:
            # count() returns awaitable
            MockTrace.count.return_value = _Awaitable(0)

            # select().order_by().limit().offset() chain
            mock_q = MagicMock()
            MockTrace.select.return_value = mock_q
            mock_q.where.return_value = mock_q
            mock_q.order_by.return_value = mock_q
            mock_q.limit.return_value = mock_q
            mock_q.offset.return_value = _Awaitable([])

            response = await async_client.get("/api/v1/traces")

            assert response.status_code == 200
            data = response.json()
            assert data["traces"] == []
            assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_get_trace(self, async_client):
        """Test getting a single trace."""
        with patch("llm_tracer.api.v1.traces.LLMTrace") as MockTrace:
            MockTrace.select.return_value.where.return_value.first = AsyncMock(
                return_value={
                    "id": 1,
                    "trace_id": "550e8400-e29b-41d4-a716-446655440000",
                    "parent_trace_id": None,
                    "project": 1,
                    "model_name": "gpt-4",
                    "model_provider": "openai",
                    "status": "success",
                    "error_message": None,
                    "input_data": {},
                    "output_data": {},
                    "tool_calls": [],
                    "prompt_tokens": 10,
                    "completion_tokens": 20,
                    "total_tokens": 30,
                    "cost_cents": 0,
                    "start_time": datetime(2024, 1, 1),
                    "end_time": datetime(2024, 1, 1),
                    "latency_ms": 100,
                    "metadata": {},
                    "tags": [],
                    "session_id": None,
                    "user_id": None,
                }
            )

            response = await async_client.get("/api/v1/traces/test-123")

            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_get_trace_not_found(self, async_client):
        """Test getting non-existent trace."""
        with patch("llm_tracer.api.v1.traces.LLMTrace") as MockTrace:
            MockTrace.select.return_value.where.return_value.first = AsyncMock(
                return_value=None
            )

            response = await async_client.get("/api/v1/traces/nonexistent")

            assert response.status_code == 404


class TestStatistics:
    """Tests for statistics endpoints."""

    @pytest.mark.asyncio
    async def test_get_stats_summary(self, async_client):
        """Test getting statistics summary."""
        with patch("llm_tracer.api.v1.traces.LLMTrace") as MockTrace:
            # ColumnMock for start_time to support >= comparison with datetime
            MockTrace.start_time = _ColumnMock()

            # select().where() chain -> awaitable returning empty list
            mock_q = MagicMock()
            MockTrace.select.return_value = mock_q
            mock_q.where.return_value = _Awaitable([])

            response = await async_client.get("/api/v1/traces/stats")

            assert response.status_code == 200
            data = response.json()
            assert data["total_traces"] == 0
