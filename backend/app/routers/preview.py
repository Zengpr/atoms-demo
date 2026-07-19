from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.routers.auth import get_current_user
from app.models.user import User
from app.services.project_service import get_project, get_latest_version

router = APIRouter(prefix="/api/preview", tags=["preview"])


@router.get("/{project_id}/html", response_class=HTMLResponse)
async def get_preview_html(
    project_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await get_project(db, project_id)
    if not project or project.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    version = await get_latest_version(db, project_id)
    if not version or not version.code_full:
        return "<html><body><h2>No preview available yet. Send a message to generate code.</h2></body></html>"
    return version.code_full


@router.post("/{project_id}/deploy")
async def deploy_project(
    project_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await get_project(db, project_id)
    if not project or project.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    project.status = "completed"
    await db.flush()
    return {"status": "deployed", "project_id": project_id}
