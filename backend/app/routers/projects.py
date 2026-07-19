from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.routers.auth import get_current_user
from app.models.user import User
from app.services.project_service import (
    create_project,
    get_user_projects,
    get_project,
    update_project,
    delete_project,
    get_project_versions,
)
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, CodeVersionResponse

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=List[ProjectResponse])
async def list_projects(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    projects = await get_user_projects(db, user.id)
    return [ProjectResponse.model_validate(p) for p in projects]


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create(data: ProjectCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    project = await create_project(db, user.id, data)
    return ProjectResponse.model_validate(project)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get(project_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    project = await get_project(db, project_id)
    if not project or project.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return ProjectResponse.model_validate(project)


@router.put("/{project_id}", response_model=ProjectResponse)
@router.patch("/{project_id}", response_model=ProjectResponse)
async def update(
    project_id: str,
    data: ProjectUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await get_project(db, project_id)
    if not project or project.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    project = await update_project(db, project, data)
    return ProjectResponse.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(project_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    project = await get_project(db, project_id)
    if not project or project.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    await delete_project(db, project)


@router.get("/{project_id}/versions", response_model=List[CodeVersionResponse])
async def list_versions(project_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    project = await get_project(db, project_id)
    if not project or project.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    versions = await get_project_versions(db, project_id)
    return [CodeVersionResponse.model_validate(v) for v in versions]


@router.get("/{project_id}/latest-code")
async def get_latest_code(project_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    project = await get_project(db, project_id)
    if not project or project.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    from app.services.chat_service import _get_latest_code
    code = await _get_latest_code(db, project_id)
    return {"code": code}
