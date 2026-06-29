"""Chat router: POST /api/v1/chat

Stateless from the client's perspective — the client sends session_id and
optionally conversation_id; the server loads/creates the conversation,
runs the Gemini agentic loop, persists the exchange, and returns the reply.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from google import genai
from pydantic import BaseModel, Field
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from apps.api.dependencies import get_db
from core.chat.orchestrator import chat as run_chat
from core.config import settings
from core.models.chat import Conversation, Message

router = APIRouter(prefix="/api/v1", tags=["chat"])

# Module-level Gemini clients (cheap to create, reused across requests)
_gen_client: genai.Client | None = None
_embed_client: genai.Client | None = None


def _get_clients() -> tuple[genai.Client, genai.Client]:
    global _gen_client, _embed_client
    if _gen_client is None:
        _gen_client = genai.Client(api_key=settings.gemini_api_key)
    if _embed_client is None:
        _embed_client = genai.Client(api_key=settings.gemini_api_key)
    return _gen_client, _embed_client


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=64)
    conversation_id: str | None = Field(default=None)
    student_id: str | None = Field(default=None)
    message: str = Field(..., min_length=1, max_length=2000)
    context: dict[str, Any] | None = Field(default=None)
    web_search: bool = Field(default=True)


class ChatResponse(BaseModel):
    conversation_id: str
    reply: str
    tools_used: list[str]


@router.post("/chat", response_model=ChatResponse)
async def post_chat(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    gen_client, embed_client = _get_clients()

    # Resolve or create conversation
    existing_messages: list[Message] = []
    conversation: Conversation | None = None
    if payload.conversation_id:
        try:
            cid = uuid.UUID(payload.conversation_id)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid conversation_id")
        conversation = await db.scalar(
            select(Conversation)
            .where(Conversation.conversation_id == cid)
            .options(selectinload(Conversation.messages))
        )
        if conversation is not None:
            existing_messages = list(conversation.messages or [])

    if conversation is None:
        student_uuid: uuid.UUID | None = None
        if payload.student_id:
            try:
                student_uuid = uuid.UUID(payload.student_id)
            except ValueError:
                pass
        conversation = Conversation(session_id=payload.session_id, student_id=student_uuid)
        db.add(conversation)
        await db.flush()

    # Build history from persisted messages (last 10 turns = 20 messages)
    history = [
        {"role": m.role, "content": m.content}
        for m in existing_messages[-20:]
    ]

    # Run agentic loop
    try:
        reply, tools_used = await run_chat(
            session=db,
            gen_client=gen_client,
            embed_client=embed_client,
            history=history,
            new_message=payload.message,
            context=payload.context,
            web_search=payload.web_search,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI service error: {exc}",
        )

    # Persist user message + assistant reply
    db.add(Message(
        conversation_id=conversation.conversation_id,
        role="user",
        content=payload.message,
    ))
    db.add(Message(
        conversation_id=conversation.conversation_id,
        role="assistant",
        content=reply,
        tool_calls=tools_used or None,
    ))

    # Bump updated_at on conversation
    await db.execute(
        update(Conversation)
        .where(Conversation.conversation_id == conversation.conversation_id)
        .values(updated_at=func.now())
    )
    await db.commit()

    return ChatResponse(
        conversation_id=str(conversation.conversation_id),
        reply=reply,
        tools_used=tools_used,
    )
