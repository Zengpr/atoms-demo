import json
import traceback
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db, async_session
from app.routers.auth import get_current_user
from app.models.user import User
from app.models.project import Project
from app.services.project_service import get_project
from app.services.chat_service import process_chat, get_conversation_history
from app.schemas.chat import ChatMessage, MessageResponse

router = APIRouter(prefix="/api/chat", tags=["chat"])


async def _get_user_project(project_id: str, user: User, db: AsyncSession) -> Project:
    project = await get_project(db, project_id)
    if not project or project.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.post("/{project_id}/message")
async def send_message(
    project_id: str,
    data: ChatMessage,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    project = await _get_user_project(project_id, user, db)
    mode = project.mode
    if data.mode and data.mode in ("engineer", "team", "race", "research", "review", "iterate", "single"):
        mode = data.mode
        project.mode = mode
        await db.commit()

    async def event_stream():
        async with async_session() as stream_db:
            try:
                async for event in process_chat(stream_db, project_id, mode, data.content):
                    yield f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n"
                await stream_db.commit()
            except Exception as e:
                traceback.print_exc()
                error_data = json.dumps({"agent": "System", "message": f"Error: {str(e)}"})
                yield f"event: message_complete\ndata: {error_data}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/{project_id}/history")
async def get_history(
    project_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _get_user_project(project_id, user, db)
    messages = await get_conversation_history(db, project_id)
    result = []
    for m in messages:
        result.append({
            "id": m.id,
            "conversationId": m.conversation_id,
            "role": m.role,
            "agentName": m.agent_name,
            "content": m.content,
            "metadata": m.metadata_,
            "createdAt": m.created_at.isoformat() if m.created_at else None,
        })
    return result
