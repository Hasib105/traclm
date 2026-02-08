"""FastAPI application factory and entry point."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from llm_tracer.api.v1 import router as api_router
from llm_tracer.config import settings
from llm_tracer.db.models import APIKey, LLMTrace, Project, User


async def create_tables() -> None:
    """Create database tables if they don't exist."""
    from piccolo.table import create_db_tables

    await create_db_tables(User, Project, APIKey, LLMTrace, if_not_exists=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    await create_tables()
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        description="A LangSmith-like observability platform for LangChain and LangGraph applications",
        version=settings.APP_VERSION,
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # Session middleware for user auth
    app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(api_router)

    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "version": settings.APP_VERSION}

    # Mount static files for frontend (if exists)
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

    return app


# Create the app instance
app = create_app()


def run() -> None:
    """Run the application with uvicorn."""
    import uvicorn

    uvicorn.run(
        "llm_tracer.app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )


if __name__ == "__main__":
    run()
