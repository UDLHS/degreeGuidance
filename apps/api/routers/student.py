"""Student router: OAuth upsert + conversation history.

POST /api/v1/student/auth            — called server-side by Auth.js on Google sign-in
GET  /api/v1/student/conversations   — list student's past conversations (requires X-Student-Id header)
GET  /api/v1/student/conversations/{id} — messages for one conversation
"""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from apps.api.dependencies import get_db
from core.models.auth import User
from core.models.chat import Conversation, Message

router = APIRouter(prefix="/api/v1/student", tags=["student"])


# ── Auth upsert ────────────────────────────────────────────────────────────────

class StudentAuthRequest(BaseModel):
    google_id: str
    email: str
    name: Optional[str] = None


class StudentAuthResponse(BaseModel):
    user_id: str
    role: str


@router.post("/auth", response_model=StudentAuthResponse)
async def student_auth(
    payload: StudentAuthRequest,
    db: AsyncSession = Depends(get_db),
) -> StudentAuthResponse:
    """Upsert a student from a Google OAuth profile. Public — called server-side only."""
    user = await db.scalar(select(User).where(User.google_id == payload.google_id))

    if user is None:
        user = await db.scalar(select(User).where(User.email == payload.email))

    if user is None:
        user = User(
            email=payload.email,
            display_name=payload.name,
            google_id=payload.google_id,
            role="student",
        )
        db.add(user)
        await db.flush()
    else:
        await db.execute(
            update(User)
            .where(User.user_id == user.user_id)
            .values(
                google_id=payload.google_id,
                display_name=payload.name or user.display_name,
                updated_at=func.now(),
            )
        )

    await db.commit()
    await db.refresh(user)
    return StudentAuthResponse(user_id=str(user.user_id), role=user.role)


# ── Conversation listing ────────────────────────────────────────────────────────

class ConversationSummary(BaseModel):
    conversation_id: str
    preview: str
    updated_at: str
    message_count: int


def _parse_student(header: str) -> uuid.UUID:
    try:
        return uuid.UUID(header)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid X-Student-Id")


@router.get("/conversations", response_model=list[ConversationSummary])
async def list_conversations(
    x_student_id: str = Header(...),
    db: AsyncSession = Depends(get_db),
) -> list[ConversationSummary]:
    student_uuid = _parse_student(x_student_id)

    rows = await db.execute(
        select(Conversation)
        .where(Conversation.student_id == student_uuid)
        .order_by(Conversation.updated_at.desc())
        .limit(20)
    )
    conversations = rows.scalars().all()

    results = []
    for conv in conversations:
        first_user_msg = await db.scalar(
            select(Message.content)
            .where(Message.conversation_id == conv.conversation_id)
            .where(Message.role == "user")
            .order_by(Message.created_at)
            .limit(1)
        )
        msg_count = await db.scalar(
            select(func.count(Message.message_id))
            .where(Message.conversation_id == conv.conversation_id)
        ) or 0
        results.append(ConversationSummary(
            conversation_id=str(conv.conversation_id),
            preview=(first_user_msg or "New conversation")[:80],
            updated_at=conv.updated_at.isoformat(),
            message_count=msg_count,
        ))

    return results


# ── Single conversation messages ───────────────────────────────────────────────

class MessageOut(BaseModel):
    role: str
    content: str


@router.get("/conversations/{conversation_id}", response_model=list[MessageOut])
async def get_conversation_messages(
    conversation_id: str,
    x_student_id: str = Header(...),
    db: AsyncSession = Depends(get_db),
) -> list[MessageOut]:
    student_uuid = _parse_student(x_student_id)

    try:
        cid = uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid conversation_id")

    conv = await db.scalar(
        select(Conversation)
        .where(Conversation.conversation_id == cid)
        .where(Conversation.student_id == student_uuid)
        .options(selectinload(Conversation.messages))
    )
    if conv is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    return [
        MessageOut(role=m.role, content=m.content)
        for m in conv.messages
        if m.role in ("user", "assistant")
    ]
