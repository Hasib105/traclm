"""API v1 package."""

from fastapi import APIRouter

from llm_tracer.api.v1 import api_keys, auth, ingest, projects, traces

router = APIRouter(prefix="/api/v1")

# Include all route modules
router.include_router(auth.router)
router.include_router(projects.router)
router.include_router(api_keys.router)
router.include_router(traces.router)
router.include_router(ingest.router)

__all__ = ["router"]
