from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.project import Project
from app.models.code_version import CodeVersion
from app.schemas.project import ProjectCreate, ProjectUpdate


async def create_project(db: AsyncSession, user_id: str, data: ProjectCreate) -> Project:
    project = Project(
        user_id=user_id,
        name=data.name,
        description=data.description,
        mode=data.mode,
    )
    db.add(project)
    await db.flush()
    return project


async def get_user_projects(db: AsyncSession, user_id: str) -> list[Project]:
    result = await db.execute(
        select(Project).where(Project.user_id == user_id).order_by(Project.updated_at.desc())
    )
    return list(result.scalars().all())


async def get_project(db: AsyncSession, project_id: str) -> Optional[Project]:
    result = await db.execute(select(Project).where(Project.id == project_id))
    return result.scalar_one_or_none()


async def update_project(db: AsyncSession, project: Project, data: ProjectUpdate) -> Project:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    await db.flush()
    return project


async def delete_project(db: AsyncSession, project: Project) -> None:
    await db.delete(project)
    await db.flush()


async def save_code_version(
    db: AsyncSession,
    project_id: str,
    code: str,
    code_html: Optional[str] = None,
    code_css: Optional[str] = None,
    code_js: Optional[str] = None,
) -> CodeVersion:
    result = await db.execute(
        select(CodeVersion)
        .where(CodeVersion.project_id == project_id)
        .order_by(CodeVersion.version.desc())
    )
    latest = result.scalar_one_or_none()
    next_version = (latest.version + 1) if latest else 1

    version = CodeVersion(
        project_id=project_id,
        version=next_version,
        code_html=code_html,
        code_css=code_css,
        code_js=code_js,
        code_full=code,
    )
    db.add(version)
    await db.flush()
    return version


async def get_project_versions(db: AsyncSession, project_id: str) -> list[CodeVersion]:
    result = await db.execute(
        select(CodeVersion)
        .where(CodeVersion.project_id == project_id)
        .order_by(CodeVersion.version.desc())
    )
    return list(result.scalars().all())


async def get_latest_version(db: AsyncSession, project_id: str) -> Optional[CodeVersion]:
    result = await db.execute(
        select(CodeVersion)
        .where(CodeVersion.project_id == project_id)
        .order_by(CodeVersion.version.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()
