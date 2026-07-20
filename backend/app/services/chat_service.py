import json
from typing import AsyncIterator, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.agent_log import AgentLog
from app.models.project import Project
from app.agents.orchestrator import Orchestrator
from app.services.project_service import save_code_version
from app.schemas.chat import ChatMessage


orchestrator = Orchestrator()


async def get_or_create_conversation(db: AsyncSession, project_id: str, mode: str) -> Conversation:
    result = await db.execute(
        select(Conversation)
        .where(Conversation.project_id == project_id)
        .order_by(Conversation.created_at.desc())
        .limit(1)
    )
    conv = result.scalars().first()
    if conv:
        return conv
    conv = Conversation(project_id=project_id, mode=mode, title="New Conversation")
    db.add(conv)
    await db.flush()
    return conv


async def save_message(
    db: AsyncSession,
    conversation_id: str,
    role: str,
    content: str,
    agent_name: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> Message:
    msg = Message(
        conversation_id=conversation_id,
        role=role,
        agent_name=agent_name,
        content=content,
        metadata_=metadata,
    )
    db.add(msg)
    await db.flush()
    return msg


async def save_agent_log(
    db: AsyncSession,
    conversation_id: str,
    agent_name: str,
    action: str,
    input_summary: str,
    output_summary: str,
    duration_ms: int,
) -> AgentLog:
    log = AgentLog(
        conversation_id=conversation_id,
        agent_name=agent_name,
        action=action,
        input_summary=input_summary[:500] if input_summary else None,
        output_summary=output_summary[:500] if output_summary else None,
        duration_ms=duration_ms,
    )
    db.add(log)
    await db.flush()
    return log


async def process_chat(
    db: AsyncSession,
    project_id: str,
    mode: str,
    user_message: str,
) -> AsyncIterator[dict]:
    conv = await get_or_create_conversation(db, project_id, mode)

    await save_message(db, conv.id, "user", user_message)

    prev_messages = await get_conversation_history(db, project_id)
    history_lines: list[str] = []
    for pm in prev_messages[-10:]:
        role_label = "User" if pm.role == "user" else pm.agent_name or "Assistant"
        history_lines.append(f"{role_label}: {pm.content[:300]}")

    last_code = await _get_latest_code(db, project_id)

    context: dict = {
        "mode": mode,
        "project_name": project_id,
        "conversation_history": history_lines,
        "previous_code": last_code,
        "is_iteration": len(prev_messages) > 1,
    }

    accumulated_code: Optional[str] = None
    total_duration = 0

    async for event in orchestrator.run(user_message, mode, context):
        if event["event"] in ("agent_thinking", "agent_stream"):
            yield event

        elif event["event"] == "agent_action":
            data = event["data"]
            agent_name = data.get("agent", "Agent")
            action = data.get("action", "")
            duration = data.get("duration_ms", 0)
            total_duration += duration
            input_summary = user_message if agent_name == "Mike" else action
            output_summary = action
            await save_agent_log(
                db, conv.id, agent_name, action, input_summary, output_summary, duration,
            )
            yield event

        elif event["event"] == "code_generated":
            data = event["data"]
            accumulated_code = data.get("code", "")
            duration = data.get("duration_ms", 0)
            total_duration += duration
            yield event

        elif event["event"] == "message_complete":
            data = event["data"]
            message = data.get("message", "")
            total_duration += data.get("duration_ms", 0)

            await save_message(
                db, conv.id, "assistant", message,
                agent_name=data.get("agent", "System"),
                metadata={"duration_ms": total_duration, "agents_used": data.get("agents_used", [])},
            )

            if accumulated_code:
                await save_code_version(db, project_id, accumulated_code)
                from app.models.project import Project
                from sqlalchemy import select as sa_select
                result = await db.execute(sa_select(Project).where(Project.id == project_id))
                proj = result.scalar_one_or_none()
                if proj:
                    proj.status = "completed"
                    await db.flush()

            yield event

    if not accumulated_code:
        yield {
            "event": "message_complete",
            "data": {"agent": "System", "message": "Processing complete.", "duration_ms": total_duration},
        }


async def _get_latest_code(db: AsyncSession, project_id: str) -> Optional[str]:
    from app.models.code_version import CodeVersion
    result = await db.execute(
        select(CodeVersion)
        .where(CodeVersion.project_id == project_id)
        .order_by(CodeVersion.created_at.desc())
        .limit(1)
    )
    cv = result.scalar_one_or_none()
    if cv:
        return cv.code_full or cv.code_html or ""
    return None


async def get_conversation_history(db: AsyncSession, project_id: str) -> list[Message]:
    result = await db.execute(
        select(Conversation).where(Conversation.project_id == project_id)
        .order_by(Conversation.created_at.desc())
    )
    convs = list(result.scalars().all())
    if not convs:
        return []
    conv = convs[0]
    result = await db.execute(
        select(Message).where(Message.conversation_id == conv.id).order_by(Message.created_at.asc())
    )
    return list(result.scalars().all())
