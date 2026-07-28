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
from app.database import async_session


orchestrator = Orchestrator()


async def _db_write(fn):
    async with async_session() as db:
        try:
            result = await fn(db)
            await db.commit()
            return result
        except Exception:
            await db.rollback()
            raise


async def _get_or_create_conversation(project_id: str, mode: str) -> Conversation:
    async def _fn(db: AsyncSession):
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
    return await _db_write(_fn)


async def _save_message(
    conversation_id: str,
    role: str,
    content: str,
    agent_name: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> Message:
    async def _fn(db: AsyncSession):
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
    return await _db_write(_fn)


async def _save_agent_log(
    conversation_id: str,
    agent_name: str,
    action: str,
    input_summary: str,
    output_summary: str,
    duration_ms: int,
) -> None:
    async def _fn(db: AsyncSession):
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
    await _db_write(_fn)


async def _save_code_and_update_project(project_id: str, code: str) -> None:
    async def _fn(db: AsyncSession):
        await save_code_version(db, project_id, code)
        result = await db.execute(select(Project).where(Project.id == project_id))
        proj = result.scalars().first()
        if proj:
            proj.status = "completed"
            await db.flush()
    await _db_write(_fn)


async def _get_latest_code(project_id: str) -> Optional[str]:
    async with async_session() as db:
        from app.models.code_version import CodeVersion
        result = await db.execute(
            select(CodeVersion)
            .where(CodeVersion.project_id == project_id)
            .order_by(CodeVersion.created_at.desc())
            .limit(1)
        )
        cv = result.scalars().first()
        if cv:
            return cv.code_full or cv.code_html or ""
        return None


async def _get_conversation_history(project_id: str) -> list[Message]:
    async with async_session() as db:
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


async def process_chat(
    project_id: str,
    mode: str,
    user_message: str,
    console_errors: list[str] | None = None,
    file_contexts: list[dict] | None = None,
) -> AsyncIterator[dict]:
    conv = await _get_or_create_conversation(project_id, mode)

    await _save_message(conv.id, "user", user_message)

    prev_messages = await _get_conversation_history(project_id)
    history_lines: list[str] = []
    for pm in prev_messages[-10:]:
        role_label = "User" if pm.role == "user" else pm.agent_name or "Assistant"
        history_lines.append(f"{role_label}: {pm.content[:300]}")

    last_code = await _get_latest_code(project_id)

    context: dict = {
        "mode": mode,
        "project_name": project_id,
        "conversation_history": history_lines,
        "previous_code": last_code or "",
        "is_iteration": len(prev_messages) > 1,
        "console_errors": console_errors or [],
        "file_contexts": file_contexts or [],
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
            await _save_agent_log(
                conv.id, agent_name, action, input_summary, output_summary, duration,
            )
            yield event

        elif event["event"] == "approval_request":
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

            await _save_message(
                conv.id, "assistant", message,
                agent_name=data.get("agent", "System"),
                metadata={"duration_ms": total_duration, "agents_used": data.get("agents_used", [])},
            )

            if accumulated_code:
                await _save_code_and_update_project(project_id, accumulated_code)

            yield event

    if not accumulated_code:
        yield {
            "event": "message_complete",
            "data": {"agent": "System", "message": "Processing complete.", "duration_ms": total_duration},
        }
