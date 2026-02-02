"""Main FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from llm_tracer.api.routes import router
from llm_tracer.config import settings
from llm_tracer.db.tables import APIKey, LLMTrace, Project


async def create_tables() -> None:
    """Create database tables."""
    from piccolo.table import create_db_tables

    await create_db_tables(Project, APIKey, LLMTrace, if_not_exists=True)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan handler."""
    # Startup
    await create_tables()
    yield
    # Shutdown


app = FastAPI(
    title="LLM Tracer",
    description="A LangSmith-like tracer for LangChain and LangGraph applications",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates
templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))

# Include API routes
app.include_router(router, prefix="/api/v1")


# ============== Web UI Routes ==============


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page - redirect to traces list."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/traces", response_class=HTMLResponse)
async def traces_list_page(request: Request):
    """Traces list page."""
    traces = await LLMTrace.select().order_by(LLMTrace.start_time, ascending=False).limit(100)
    return templates.TemplateResponse("traces_list.html", {"request": request, "traces": traces})


@app.get("/traces/{trace_id}", response_class=HTMLResponse)
async def trace_detail_page(request: Request, trace_id: str):
    """Trace detail page."""
    trace = await LLMTrace.select().where(LLMTrace.trace_id == trace_id).first()
    if not trace:
        return HTMLResponse(content="Trace not found", status_code=404)

    return templates.TemplateResponse("trace_detail.html", {"request": request, "trace": trace})


@app.get("/projects", response_class=HTMLResponse)
async def projects_page(request: Request):
    """Projects management page."""
    projects = await Project.select().order_by(Project.created_at, ascending=False)
    return templates.TemplateResponse("projects.html", {"request": request, "projects": projects})


@app.get("/api-keys", response_class=HTMLResponse)
async def api_keys_page(request: Request):
    """API keys management page."""
    keys = await APIKey.select().order_by(APIKey.created_at, ascending=False)
    projects = await Project.select()
    return templates.TemplateResponse(
        "api_keys.html", {"request": request, "api_keys": keys, "projects": projects}
    )


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


def run():
    """Run the application."""
    import uvicorn

    uvicorn.run(
        "llm_tracer.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG
    )


if __name__ == "__main__":
    run()
