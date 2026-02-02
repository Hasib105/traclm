"""API routes for LLM Tracer."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status

from llm_tracer.api.auth import require_api_key
from llm_tracer.api.schemas import (
    APIKeyCreate,
    APIKeyResponse,
    IngestBatch,
    IngestTrace,
    ProjectCreate,
    ProjectResponse,
    TraceListResponse,
    TraceResponse,
    TraceUpdate,
)
from llm_tracer.db.tables import APIKey, LLMTrace, Project

router = APIRouter()


# ============== Project Endpoints ==============


@router.post("/projects", response_model=ProjectResponse, tags=["Projects"])
async def create_project(data: ProjectCreate):
    """Create a new project."""
    project = Project(name=data.name, description=data.description)
    await project.save()

    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.get("/projects", response_model=list[ProjectResponse], tags=["Projects"])
async def list_projects():
    """List all projects."""
    projects = await Project.select().order_by(Project.created_at, ascending=False)
    return [
        ProjectResponse(
            id=p["id"],
            name=p["name"],
            description=p["description"],
            created_at=p["created_at"],
            updated_at=p["updated_at"],
        )
        for p in projects
    ]


@router.get("/projects/{project_id}", response_model=ProjectResponse, tags=["Projects"])
async def get_project(project_id: int):
    """Get a project by ID."""
    project = await Project.select().where(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return ProjectResponse(
        id=project["id"],
        name=project["name"],
        description=project["description"],
        created_at=project["created_at"],
        updated_at=project["updated_at"],
    )


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Projects"])
async def delete_project(project_id: int):
    """Delete a project."""
    await Project.delete().where(Project.id == project_id)
    return None


# ============== API Key Endpoints ==============


@router.post("/api-keys", response_model=APIKeyResponse, tags=["API Keys"])
async def create_api_key(data: APIKeyCreate):
    """Create a new API key for a project."""
    # Verify project exists
    project = await Project.select().where(Project.id == data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    key = APIKey.generate_key()
    api_key = APIKey(key=key, name=data.name, project=data.project_id)
    await api_key.save()

    return APIKeyResponse(
        id=api_key.id,
        key=api_key.key,
        name=api_key.name,
        project_id=data.project_id,
        is_active=True,
        created_at=api_key.created_at,
        last_used_at=None,
    )


@router.get("/api-keys", response_model=list[APIKeyResponse], tags=["API Keys"])
async def list_api_keys(project_id: int | None = None):
    """List API keys, optionally filtered by project."""
    query = APIKey.select()
    if project_id:
        query = query.where(APIKey.project == project_id)

    keys = await query.order_by(APIKey.created_at, ascending=False)
    return [
        APIKeyResponse(
            id=k["id"],
            key=k["key"][:12] + "..." + k["key"][-4:],  # Mask key
            name=k["name"],
            project_id=k["project"],
            is_active=bool(k["is_active"]),
            created_at=k["created_at"],
            last_used_at=k["last_used_at"],
        )
        for k in keys
    ]


@router.delete("/api-keys/{key_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["API Keys"])
async def revoke_api_key(key_id: int):
    """Revoke an API key."""
    await APIKey.update({APIKey.is_active: 0}).where(APIKey.id == key_id)
    return None


# ============== Trace Ingest Endpoints (for SDK) ==============


@router.post("/ingest/trace", response_model=dict, tags=["Ingest"])
async def ingest_trace(data: IngestTrace, api_key: dict = Depends(require_api_key)):
    """Ingest a single trace from SDK."""
    trace = LLMTrace(
        trace_id=data.trace_id,
        parent_trace_id=data.parent_trace_id,
        project=api_key["project"],
        model_name=data.model_name,
        model_provider=data.model_provider,
        status=data.status,
        error_message=data.error_message,
        input_data=data.input_data,
        output_data=data.output_data,
        tool_calls=data.tool_calls,
        prompt_tokens=data.prompt_tokens,
        completion_tokens=data.completion_tokens,
        total_tokens=data.total_tokens,
        metadata=data.metadata,
        tags=data.tags,
        session_id=data.session_id,
        user_id=data.user_id,
    )

    if data.start_time:
        trace.start_time = datetime.fromisoformat(data.start_time.replace("Z", "+00:00"))
    if data.end_time:
        trace.end_time = datetime.fromisoformat(data.end_time.replace("Z", "+00:00"))
        trace.latency_ms = trace.calculate_latency()

    await trace.save()

    return {"status": "ok", "trace_id": data.trace_id}


@router.post("/ingest/batch", response_model=dict, tags=["Ingest"])
async def ingest_batch(data: IngestBatch, api_key: dict = Depends(require_api_key)):
    """Ingest multiple traces from SDK."""
    count = 0
    for trace_data in data.traces:
        trace = LLMTrace(
            trace_id=trace_data.trace_id,
            parent_trace_id=trace_data.parent_trace_id,
            project=api_key["project"],
            model_name=trace_data.model_name,
            model_provider=trace_data.model_provider,
            status=trace_data.status,
            error_message=trace_data.error_message,
            input_data=trace_data.input_data,
            output_data=trace_data.output_data,
            tool_calls=trace_data.tool_calls,
            prompt_tokens=trace_data.prompt_tokens,
            completion_tokens=trace_data.completion_tokens,
            total_tokens=trace_data.total_tokens,
            metadata=trace_data.metadata,
            tags=trace_data.tags,
            session_id=trace_data.session_id,
            user_id=trace_data.user_id,
        )

        if trace_data.start_time:
            trace.start_time = datetime.fromisoformat(trace_data.start_time.replace("Z", "+00:00"))
        if trace_data.end_time:
            trace.end_time = datetime.fromisoformat(trace_data.end_time.replace("Z", "+00:00"))
            trace.latency_ms = trace.calculate_latency()

        await trace.save()
        count += 1

    return {"status": "ok", "ingested": count}


@router.patch("/ingest/trace/{trace_id}", response_model=dict, tags=["Ingest"])
async def update_trace(trace_id: str, data: TraceUpdate, api_key: dict = Depends(require_api_key)):
    """Update an existing trace (for streaming updates)."""
    trace = (
        await LLMTrace.select()
        .where(LLMTrace.trace_id == trace_id, LLMTrace.project == api_key["project"])
        .first()
    )

    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")

    update_data = {}
    if data.status is not None:
        update_data[LLMTrace.status] = data.status
    if data.error_message is not None:
        update_data[LLMTrace.error_message] = data.error_message
    if data.output_data is not None:
        update_data[LLMTrace.output_data] = data.output_data
    if data.tool_calls is not None:
        update_data[LLMTrace.tool_calls] = data.tool_calls
    if data.prompt_tokens is not None:
        update_data[LLMTrace.prompt_tokens] = data.prompt_tokens
    if data.completion_tokens is not None:
        update_data[LLMTrace.completion_tokens] = data.completion_tokens
    if data.total_tokens is not None:
        update_data[LLMTrace.total_tokens] = data.total_tokens
    if data.end_time is not None:
        update_data[LLMTrace.end_time] = data.end_time
    if data.latency_ms is not None:
        update_data[LLMTrace.latency_ms] = data.latency_ms
    if data.metadata is not None:
        update_data[LLMTrace.metadata] = data.metadata
    if data.tags is not None:
        update_data[LLMTrace.tags] = data.tags

    if update_data:
        await LLMTrace.update(update_data).where(LLMTrace.id == trace["id"])

    return {"status": "ok", "trace_id": trace_id}


# ============== Trace Query Endpoints ==============


@router.get("/traces", response_model=TraceListResponse, tags=["Traces"])
async def list_traces(
    project_id: int | None = None,
    status: str | None = None,
    model_name: str | None = None,
    session_id: str | None = None,
    user_id: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    """List traces with filtering and pagination."""
    query = LLMTrace.select()

    if project_id:
        query = query.where(LLMTrace.project == project_id)
    if status:
        query = query.where(LLMTrace.status == status)
    if model_name:
        query = query.where(LLMTrace.model_name == model_name)
    if session_id:
        query = query.where(LLMTrace.session_id == session_id)
    if user_id:
        query = query.where(LLMTrace.user_id == user_id)

    # Get total count
    total = await LLMTrace.count().where(query._where_clauses[0] if query._where_clauses else True)

    # Paginate
    offset = (page - 1) * page_size
    traces = (
        await query.order_by(LLMTrace.start_time, ascending=False).limit(page_size).offset(offset)
    )

    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return TraceListResponse(
        traces=[
            TraceResponse(
                id=t["id"],
                trace_id=str(t["trace_id"]),
                parent_trace_id=str(t["parent_trace_id"]) if t["parent_trace_id"] else None,
                project_id=t["project"],
                model_name=t["model_name"],
                model_provider=t["model_provider"],
                status=t["status"],
                error_message=t["error_message"],
                input_data=t["input_data"] or {},
                output_data=t["output_data"] or {},
                tool_calls=t["tool_calls"] or [],
                prompt_tokens=t["prompt_tokens"],
                completion_tokens=t["completion_tokens"],
                total_tokens=t["total_tokens"],
                cost_cents=t["cost_cents"],
                start_time=t["start_time"],
                end_time=t["end_time"],
                latency_ms=t["latency_ms"],
                metadata=t["metadata"] or {},
                tags=t["tags"] or [],
                session_id=t["session_id"],
                user_id=t["user_id"],
            )
            for t in traces
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/traces/{trace_id}", response_model=TraceResponse, tags=["Traces"])
async def get_trace(trace_id: str):
    """Get a single trace by ID."""
    trace = await LLMTrace.select().where(LLMTrace.trace_id == trace_id).first()

    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")

    return TraceResponse(
        id=trace["id"],
        trace_id=str(trace["trace_id"]),
        parent_trace_id=str(trace["parent_trace_id"]) if trace["parent_trace_id"] else None,
        project_id=trace["project"],
        model_name=trace["model_name"],
        model_provider=trace["model_provider"],
        status=trace["status"],
        error_message=trace["error_message"],
        input_data=trace["input_data"] or {},
        output_data=trace["output_data"] or {},
        tool_calls=trace["tool_calls"] or [],
        prompt_tokens=trace["prompt_tokens"],
        completion_tokens=trace["completion_tokens"],
        total_tokens=trace["total_tokens"],
        cost_cents=trace["cost_cents"],
        start_time=trace["start_time"],
        end_time=trace["end_time"],
        latency_ms=trace["latency_ms"],
        metadata=trace["metadata"] or {},
        tags=trace["tags"] or [],
        session_id=trace["session_id"],
        user_id=trace["user_id"],
    )


@router.delete("/traces/{trace_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Traces"])
async def delete_trace(trace_id: str):
    """Delete a trace."""
    await LLMTrace.delete().where(LLMTrace.trace_id == trace_id)
    return None


# ============== Stats Endpoints ==============


@router.get("/stats/summary", tags=["Stats"])
async def get_stats_summary(project_id: int | None = None, days: int = Query(7, ge=1, le=90)):
    """Get summary statistics."""
    from datetime import timedelta

    start_date = datetime.now() - timedelta(days=days)

    query = LLMTrace.select()
    if project_id:
        query = query.where(LLMTrace.project == project_id)
    query = query.where(LLMTrace.start_time >= start_date)

    traces = await query

    total_traces = len(traces)
    success_count = sum(1 for t in traces if t["status"] == "success")
    error_count = sum(1 for t in traces if t["status"] == "error")
    total_tokens = sum(t["total_tokens"] for t in traces)
    avg_latency = sum(t["latency_ms"] for t in traces) / total_traces if total_traces > 0 else 0

    return {
        "total_traces": total_traces,
        "success_count": success_count,
        "error_count": error_count,
        "success_rate": success_count / total_traces if total_traces > 0 else 0,
        "total_tokens": total_tokens,
        "average_latency_ms": round(avg_latency, 2),
        "period_days": days,
    }
