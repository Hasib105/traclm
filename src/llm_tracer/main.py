"""Main FastAPI application with JSON API for React frontend."""
from contextlib import asynccontextmanager
from datetime import datetime
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from typing import Optional
import secrets

from llm_tracer.api.routes import router
from llm_tracer.config import settings
from llm_tracer.db.tables import APIKey, LLMTrace, Project, User


async def create_tables() -> None:
    """Create database tables."""
    from piccolo.table import create_db_tables
    await create_db_tables(User, Project, APIKey, LLMTrace, if_not_exists=True)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan handler."""
    await create_tables()
    yield


app = FastAPI(
    title="LLM Tracer",
    description="A LangSmith-like tracer for LangChain and LangGraph applications",
    version="0.1.0",
    lifespan=lifespan,
)

# Session middleware for user auth
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", *settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include existing API routes (for SDK)
app.include_router(router, prefix="/api/v1")


# ============== Pydantic Models ==============

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class ProjectCreate(BaseModel):
    name: str
    description: str = ""

class ApiKeyCreate(BaseModel):
    name: str
    project_id: Optional[int] = None


# ============== Auth Helpers ==============

def get_current_user(request: Request) -> Optional[dict]:
    """Get current user from session."""
    return request.session.get("user")

def require_auth(request: Request) -> dict:
    """Require authentication."""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


# ============== Auth API Routes ==============

@app.get("/api/auth/me")
async def get_me(request: Request):
    """Get current user."""
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


@app.post("/api/auth/login")
async def login(request: Request, data: LoginRequest):
    """Handle login."""
    user = await User.select().where(User.username == data.username).first()

    if not user or not User.verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not user["is_active"]:
        raise HTTPException(status_code=401, detail="Account is disabled")

    # Update last login
    await User.update({User.last_login: datetime.now()}).where(User.id == user["id"])

    # Set session
    user_data = {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "is_admin": user["is_admin"],
    }
    request.session["user"] = user_data

    return {"user": user_data}


@app.post("/api/auth/register")
async def register(request: Request, data: RegisterRequest):
    """Handle registration."""
    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    existing = await User.select().where(User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    existing = await User.select().where(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        username=data.username,
        email=data.email,
        password_hash=User.hash_password(data.password),
    )
    await user.save()

    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin,
    }
    request.session["user"] = user_data

    return {"user": user_data}


@app.post("/api/auth/logout")
async def logout(request: Request):
    """Logout user."""
    request.session.clear()
    return {"message": "Logged out"}


# ============== Dashboard API Routes ==============

@app.get("/api/dashboard/stats")
async def dashboard_stats(user: dict = Depends(require_auth)):
    """Get dashboard statistics."""
    trace_count = await LLMTrace.count()
    project_count = await Project.count()
    api_key_count = await APIKey.count()
    return {
        "trace_count": trace_count,
        "project_count": project_count,
        "api_key_count": api_key_count,
    }


@app.get("/api/dashboard/recent-traces")
async def recent_traces(user: dict = Depends(require_auth)):
    """Get recent traces."""
    traces = await LLMTrace.select().order_by(LLMTrace.start_time, ascending=False).limit(5)
    return traces


# ============== Traces API Routes ==============

@app.get("/api/traces")
async def list_traces(user: dict = Depends(require_auth)):
    """List all traces."""
    traces = await LLMTrace.select().order_by(LLMTrace.start_time, ascending=False).limit(100)
    return traces


@app.get("/api/traces/{trace_id}")
async def get_trace(trace_id: str, user: dict = Depends(require_auth)):
    """Get a single trace."""
    trace = await LLMTrace.select().where(LLMTrace.trace_id == trace_id).first()
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")
    return trace


# ============== Projects API Routes ==============

@app.get("/api/projects")
async def list_projects(user: dict = Depends(require_auth)):
    """List all projects."""
    projects = await Project.select().order_by(Project.created_at, ascending=False)
    return projects


@app.post("/api/projects")
async def create_project(data: ProjectCreate, user: dict = Depends(require_auth)):
    """Create a new project."""
    project = Project(
        name=data.name,
        description=data.description,
        owner=user["id"],
    )
    await project.save()
    return {"id": project.id, "name": project.name, "description": project.description}


@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: int, user: dict = Depends(require_auth)):
    """Delete a project."""
    await Project.delete().where(Project.id == project_id)
    return {"message": "Deleted"}


# ============== API Keys Routes ==============

@app.get("/api/api-keys")
async def list_api_keys(user: dict = Depends(require_auth)):
    """List all API keys."""
    keys = await APIKey.select(
        APIKey.id,
        APIKey.name,
        APIKey.key_prefix,
        APIKey.created_at,
        APIKey.last_used_at,
        APIKey.is_active,
    ).order_by(APIKey.created_at, ascending=False)
    return keys


@app.post("/api/api-keys")
async def create_api_key(data: ApiKeyCreate, user: dict = Depends(require_auth)):
    """Create a new API key."""
    # Generate a random API key
    key = APIKey.generate_key()
    key_prefix = key[:12]

    api_key = APIKey(
        name=data.name,
        key_hash=APIKey.hash_key(key),
        key_prefix=key_prefix,
        project=data.project_id if data.project_id else None,
    )
    await api_key.save()
    
    # Return the full key only once
    return {"id": api_key.id, "name": api_key.name, "key": key, "key_prefix": key_prefix}


@app.delete("/api/api-keys/{key_id}")
async def delete_api_key(key_id: int, user: dict = Depends(require_auth)):
    """Revoke an API key."""
    await APIKey.delete().where(APIKey.id == key_id)
    return {"message": "Revoked"}


# ============== Health Check ==============

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
