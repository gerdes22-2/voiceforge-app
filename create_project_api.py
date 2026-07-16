import os

with open("backend/app/api/v1/projects.py", "w") as f:
    f.write("""from typing import Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api import deps
from app.schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.schemas.timeline import ProjectEventRead
from app.crud.crud_project import project as crud_project
from app.crud.crud_timeline import timeline as crud_timeline
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    *,
    db: AsyncSession = Depends(deps.get_db),
    project_in: ProjectCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    \"\"\"
    Create new project.
    \"\"\"
    project = await crud_project.create_with_owner(db=db, obj_in=project_in, user_id=current_user.id)
    await crud_timeline.create(
        db=db, 
        project_id=project.id, 
        event_type="project_created", 
        description="Project was created."
    )
    return project

@router.get("/", response_model=List[ProjectRead])
async def read_projects(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    \"\"\"
    Retrieve projects for the current user.
    \"\"\"
    projects = await crud_project.get_multi_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)
    return projects

@router.get("/{project_id}", response_model=ProjectRead)
async def read_project(
    *,
    db: AsyncSession = Depends(deps.get_db),
    project_id: UUID,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    \"\"\"
    Get project by ID.
    \"\"\"
    project = await crud_project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return project

@router.put("/{project_id}", response_model=ProjectRead)
async def update_project(
    *,
    db: AsyncSession = Depends(deps.get_db),
    project_id: UUID,
    project_in: ProjectUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    \"\"\"
    Update a project.
    \"\"\"
    project = await crud_project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        
    project = await crud_project.update(db=db, db_obj=project, obj_in=project_in)
    await crud_timeline.create(
        db=db, 
        project_id=project.id, 
        event_type="project_updated", 
        description="Project settings were updated."
    )
    return project

@router.delete("/{project_id}", response_model=ProjectRead)
async def delete_project(
    *,
    db: AsyncSession = Depends(deps.get_db),
    project_id: UUID,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    \"\"\"
    Delete a project (soft delete).
    \"\"\"
    project = await crud_project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        
    project = await crud_project.remove(db=db, id=project_id)
    # Could log this in audit log
    return project

@router.get("/{project_id}/timeline", response_model=List[ProjectEventRead])
async def read_project_timeline(
    *,
    db: AsyncSession = Depends(deps.get_db),
    project_id: UUID,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    \"\"\"
    Get event history for a project.
    \"\"\"
    project = await crud_project.get(db=db, id=project_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        
    events = await crud_timeline.get_by_project(db=db, project_id=project_id)
    return events
""")

# Register it in a router if needed (e.g. backend/app/api/v1/api.py)
# Or we can do it via a script
