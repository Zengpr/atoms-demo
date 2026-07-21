from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Any
from app.schemas.config import CAMEL_CONFIG


class ChatMessage(BaseModel):
    content: str
    mode: str = "engineer"
    console_errors: list[str] = []


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    agent_name: Optional[str] = None
    content: str
    metadata_: Optional[dict] = Field(None, serialization_alias="metadata")
    created_at: datetime

    model_config = CAMEL_CONFIG


class ConversationResponse(BaseModel):
    id: str
    project_id: str
    mode: str
    title: Optional[str] = None
    created_at: datetime

    model_config = CAMEL_CONFIG


class SSEEvent(BaseModel):
    event: str
    data: Any
