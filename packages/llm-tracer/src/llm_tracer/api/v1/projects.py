"""Project routes."""

from fastapi import APIRouter, Depends, HTTPException, status

from llm_tracer.api.dependencies import require_auth
from llm_tracer.api.v1.schemas import ProjectCreate, ProjectResponse
from llm_tracer.db.models import Project

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=list[ProjectResponse])
async def list_projects(user: dict = Depends(require_auth)):
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


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(data: ProjectCreate, user: dict = Depends(require_auth)):
    """Create a new project."""
    # Check for duplicate name
    existing = await Project.select().where(Project.name == data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project with this name already exists",
        )

    project = Project(
        name=data.name,
        description=data.description,
        owner=user["id"],
    )
    await project.save()

    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, user: dict = Depends(require_auth)):
    """Get a project by ID."""
    project = await Project.select().where(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    return ProjectResponse(
        id=project["id"],
        name=project["name"],
        description=project["description"],
        created_at=project["created_at"],
        updated_at=project["updated_at"],
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: int, user: dict = Depends(require_auth)):
    """Delete a project."""
    project = await Project.select().where(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    await Project.delete().where(Project.id == project_id)
    return None
