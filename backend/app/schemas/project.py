from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.schemas.config import CAMEL_CONFIG


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    mode: str = "engineer"


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    mode: Optional[str] = None
    status: Optional[str] = None
    thumbnail: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    mode: str
    status: str
    thumbnail: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = CAMEL_CONFIG


class CodeVersionResponse(BaseModel):
    id: str
    project_id: str
    version: int
    code_html: Optional[str] = None
    code_css: Optional[str] = None
    code_js: Optional[str] = None
    code_full: Optional[str] = None
    created_at: datetime

    model_config = CAMEL_CONFIG
