import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.routers.auth import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.code_version import CodeVersion
from app.services.project_service import get_project, get_latest_version

router = APIRouter(prefix="/api/preview", tags=["preview"])

PUBLISHED_PAGES: dict[str, dict] = {}


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
    version = await get_latest_version(db, project_id)
    if not version or not version.code_full:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No code to deploy. Generate code first.")

    page_id = PUBLISHED_PAGES.get(project_id, {}).get("page_id") or str(uuid.uuid4())[:8]
    PUBLISHED_PAGES[project_id] = {
        "page_id": page_id,
        "code": version.code_full,
        "project_name": project.name,
    }
    project.status = "completed"
    await db.flush()

    base_url = str(db.bind.url) if hasattr(db.bind, 'url') else ""
    deploy_url = f"/api/preview/public/{page_id}"

    return {
        "status": "deployed",
        "project_id": project_id,
        "url": deploy_url,
        "page_id": page_id,
    }


@router.get("/public/{page_id}", response_class=HTMLResponse)
async def get_public_page(page_id: str):
    for project_id, data in PUBLISHED_PAGES.items():
        if data.get("page_id") == page_id:
            return data["code"]
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")
