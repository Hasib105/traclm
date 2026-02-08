"""Trace query routes."""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status

from llm_tracer.api.dependencies import require_auth
from llm_tracer.api.v1.schemas import TraceListResponse, TraceResponse
from llm_tracer.db.models import LLMTrace

router = APIRouter(prefix="/traces", tags=["Traces"])


@router.get("", response_model=TraceListResponse)
async def list_traces(
    project_id: int | None = None,
    status_filter: str | None = Query(None, alias="status"),
    model_name: str | None = None,
    session_id: str | None = None,
    user_id: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    user: dict = Depends(require_auth),
):
    """List traces with filtering and pagination."""
    query = LLMTrace.select()

    if project_id:
        query = query.where(LLMTrace.project == project_id)
    if status_filter:
        query = query.where(LLMTrace.status == status_filter)
    if model_name:
        query = query.where(LLMTrace.model_name == model_name)
    if session_id:
        query = query.where(LLMTrace.session_id == session_id)
    if user_id:
        query = query.where(LLMTrace.user_id == user_id)

    # Get total count
    total = await LLMTrace.count()

    # Paginate
    offset = (page - 1) * page_size
    traces = await query.order_by(LLMTrace.start_time, ascending=False).limit(page_size).offset(offset)

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


@router.get("/recent")
async def get_recent_traces(
    limit: int = Query(5, ge=1, le=20),
    user: dict = Depends(require_auth),
):
    """Get recent traces for dashboard."""
    traces = await LLMTrace.select().order_by(LLMTrace.start_time, ascending=False).limit(limit)
    return traces


@router.get("/stats")
async def get_trace_stats(
    project_id: int | None = None,
    days: int = Query(7, ge=1, le=90),
    user: dict = Depends(require_auth),
):
    """Get trace statistics."""
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


@router.get("/{trace_id}", response_model=TraceResponse)
async def get_trace(trace_id: str, user: dict = Depends(require_auth)):
    """Get a single trace by ID."""
    trace = await LLMTrace.select().where(LLMTrace.trace_id == trace_id).first()

    if not trace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trace not found")

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


@router.delete("/{trace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trace(trace_id: str, user: dict = Depends(require_auth)):
    """Delete a trace."""
    await LLMTrace.delete().where(LLMTrace.trace_id == trace_id)
    return None
