"""SDK trace ingestion routes."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from llm_tracer.api.dependencies import require_api_key
from llm_tracer.api.v1.schemas import IngestBatch, IngestTrace, TraceUpdate
from llm_tracer.db.models import LLMTrace

router = APIRouter(prefix="/ingest", tags=["Ingest"])


def parse_datetime(dt_str: str | None) -> datetime | None:
    """Parse ISO datetime string."""
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except ValueError:
        return None


@router.post("/trace", status_code=status.HTTP_201_CREATED)
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
        cost_cents=data.cost_cents,
        metadata=data.metadata,
        tags=data.tags,
        session_id=data.session_id,
        user_id=data.user_id,
    )

    if data.start_time:
        trace.start_time = parse_datetime(data.start_time) or datetime.now()
    if data.end_time:
        trace.end_time = parse_datetime(data.end_time)
        trace.latency_ms = trace.calculate_latency()

    await trace.save()

    return {"status": "ok", "trace_id": data.trace_id}


@router.post("/batch", status_code=status.HTTP_201_CREATED)
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
            cost_cents=trace_data.cost_cents,
            metadata=trace_data.metadata,
            tags=trace_data.tags,
            session_id=trace_data.session_id,
            user_id=trace_data.user_id,
        )

        if trace_data.start_time:
            trace.start_time = parse_datetime(trace_data.start_time) or datetime.now()
        if trace_data.end_time:
            trace.end_time = parse_datetime(trace_data.end_time)
            trace.latency_ms = trace.calculate_latency()

        await trace.save()
        count += 1

    return {"status": "ok", "ingested": count}


@router.patch("/trace/{trace_id}")
async def update_trace(
    trace_id: str,
    data: TraceUpdate,
    api_key: dict = Depends(require_api_key),
):
    """Update an existing trace (for streaming updates)."""
    trace = await LLMTrace.select().where(
        LLMTrace.trace_id == trace_id,
        LLMTrace.project == api_key["project"],
    ).first()

    if not trace:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trace not found")

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
        update_data[LLMTrace.end_time] = parse_datetime(data.end_time)
    if data.latency_ms is not None:
        update_data[LLMTrace.latency_ms] = data.latency_ms
    if data.metadata is not None:
        update_data[LLMTrace.metadata] = data.metadata
    if data.tags is not None:
        update_data[LLMTrace.tags] = data.tags

    if update_data:
        await LLMTrace.update(update_data).where(LLMTrace.id == trace["id"])

    return {"status": "ok", "trace_id": trace_id}
