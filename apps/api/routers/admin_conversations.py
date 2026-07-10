"""Admin oversight of the AI advisor — conversations viewer + usage stats
(Phase 2 of docs/PHASE2_STUDENT_ADMIN_PLAN.md).

GET   /api/admin/conversations            — list (filter: flagged, student/anon,
                                            search in message text; paginated)
GET   /api/admin/conversations/{id}       — full thread incl. per-reply tool calls
PATCH /api/admin/conversations/{id}       — flag/unflag for review (audited)
GET   /api/admin/usage                    — dashboard cards: chat volume, tool
                                            usage mix, recommendation usage from
                                            eligibility_audit

Everything is read-only except the flag toggle. All admins have access (plan
decision D5). Year-related stats GROUP BY whatever years exist in the data —
never hardcoded — so future handbook uploads change numbers, not code.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.admin_audit import log_admin_action
from apps.api.dependencies import get_current_admin, get_db
from core.models.auth import User
from core.models.chat import Conversation

router = APIRouter(
    prefix="/api/admin",
    tags=["admin:conversations"],
    dependencies=[Depends(get_current_admin)],
)


# ── Schemas ──────────────────────────────────────────────────────────────────

class ConversationListItem(BaseModel):
    conversation_id: str
    started_at: datetime
    updated_at: datetime
    message_count: int
    flagged: bool
    student_email: str | None  # null = anonymous session
    preview: str


class ConversationListResponse(BaseModel):
    total: int
    items: list[ConversationListItem]


class AdminMessageOut(BaseModel):
    role: str
    content: str
    tool_calls: list[str] | None
    created_at: datetime


class ConversationDetail(BaseModel):
    conversation_id: str
    started_at: datetime
    updated_at: datetime
    flagged: bool
    student_email: str | None
    messages: list[AdminMessageOut]


class ConversationUpdate(BaseModel):
    flagged: bool


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    flagged: bool | None = Query(None),
    student_only: bool | None = Query(None, description="true = signed-in students only, false = anonymous only"),
    q: str | None = Query(None, max_length=200, description="search in message text"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> ConversationListResponse:
    where = ["1=1"]
    params: dict = {"limit": limit, "offset": offset}
    if flagged is not None:
        where.append("c.flagged = :flagged")
        params["flagged"] = flagged
    if student_only is True:
        where.append("c.student_id IS NOT NULL")
    elif student_only is False:
        where.append("c.student_id IS NULL")
    if q and q.strip():
        where.append(
            "EXISTS (SELECT 1 FROM messages mq WHERE mq.conversation_id = c.conversation_id "
            "AND mq.content ILIKE :q)"
        )
        params["q"] = f"%{q.strip()}%"
    where_sql = " AND ".join(where)

    total = (
        await db.execute(text(f"SELECT count(*) FROM conversations c WHERE {where_sql}"), params)
    ).scalar()

    rows = (
        await db.execute(
            text(
                f"""
                SELECT c.conversation_id, c.created_at, c.updated_at, c.flagged,
                       u.email AS student_email,
                       (SELECT count(*) FROM messages m WHERE m.conversation_id = c.conversation_id) AS message_count,
                       (SELECT m2.content FROM messages m2
                         WHERE m2.conversation_id = c.conversation_id AND m2.role = 'user'
                         ORDER BY m2.created_at LIMIT 1) AS first_user
                FROM conversations c
                LEFT JOIN users u ON u.user_id = c.student_id
                WHERE {where_sql}
                ORDER BY c.updated_at DESC
                LIMIT :limit OFFSET :offset
                """
            ),
            params,
        )
    ).mappings().all()

    return ConversationListResponse(
        total=total or 0,
        items=[
            ConversationListItem(
                conversation_id=str(r["conversation_id"]),
                started_at=r["created_at"],
                updated_at=r["updated_at"],
                message_count=r["message_count"],
                flagged=r["flagged"],
                student_email=r["student_email"],
                preview=(r["first_user"] or "—")[:120],
            )
            for r in rows
        ],
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ConversationDetail:
    conv = (
        await db.execute(
            text(
                "SELECT c.conversation_id, c.created_at, c.updated_at, c.flagged, u.email "
                "FROM conversations c LEFT JOIN users u ON u.user_id = c.student_id "
                "WHERE c.conversation_id = :id"
            ),
            {"id": conversation_id},
        )
    ).first()
    if conv is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    msgs = (
        await db.execute(
            text(
                "SELECT role, content, tool_calls, created_at FROM messages "
                "WHERE conversation_id = :id ORDER BY created_at, message_id"
            ),
            {"id": conversation_id},
        )
    ).mappings().all()

    return ConversationDetail(
        conversation_id=str(conv[0]),
        started_at=conv[1],
        updated_at=conv[2],
        flagged=conv[3],
        student_email=conv[4],
        messages=[
            AdminMessageOut(
                role=m["role"],
                content=m["content"],
                tool_calls=list(m["tool_calls"]) if m["tool_calls"] else None,
                created_at=m["created_at"],
            )
            for m in msgs
        ],
    )


@router.patch("/conversations/{conversation_id}", response_model=ConversationDetail)
async def update_conversation(
    conversation_id: uuid.UUID,
    payload: ConversationUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> ConversationDetail:
    conv = await db.get(Conversation, conversation_id)
    if conv is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    before = {"flagged": conv.flagged}
    conv.flagged = payload.flagged
    await log_admin_action(
        db, admin=admin, action_type="conversation.flag",
        target_table="conversations", target_id=str(conversation_id),
        before=before, after={"flagged": payload.flagged}, request=request,
    )
    await db.commit()
    return await get_conversation(conversation_id, db)


@router.get("/usage")
async def usage_stats(db: AsyncSession = Depends(get_db)) -> dict:
    """Dashboard cards. Deliberately year-agnostic in code: every breakdown is
    derived from the data present at query time (new handbook years / new tools
    appear automatically)."""

    async def scalar(q: str, **p):
        return (await db.execute(text(q), p)).scalar() or 0

    conversations = {
        "total": await scalar("SELECT count(*) FROM conversations"),
        "last_7_days": await scalar(
            "SELECT count(*) FROM conversations WHERE created_at > now() - interval '7 days'"
        ),
        "today": await scalar(
            "SELECT count(*) FROM conversations WHERE created_at::date = now()::date"
        ),
        "flagged": await scalar("SELECT count(*) FROM conversations WHERE flagged"),
    }
    messages = {
        "total": await scalar("SELECT count(*) FROM messages"),
        "last_7_days": await scalar(
            "SELECT count(*) FROM messages WHERE created_at > now() - interval '7 days'"
        ),
    }
    # tool usage mix — tool_calls is a JSONB array of tool names per assistant
    # reply. Guard on jsonb_typeof: rows can carry JSON null (a scalar, which
    # passes IS NOT NULL but breaks jsonb_array_elements_text — seen in real
    # June data), and any future non-array shape is skipped rather than fatal.
    tool_rows = (
        await db.execute(
            text(
                "SELECT t.tool, count(*) FROM messages m, "
                "LATERAL jsonb_array_elements_text(m.tool_calls) AS t(tool) "
                "WHERE jsonb_typeof(m.tool_calls) = 'array' "
                "GROUP BY t.tool ORDER BY count(*) DESC"
            )
        )
    ).all()
    tool_usage = {r[0]: r[1] for r in tool_rows}

    # recommendation/eligibility usage — from the always-on audit trail
    elig = {
        "total": await scalar("SELECT count(*) FROM eligibility_audit"),
        "last_7_days": await scalar(
            "SELECT count(*) FROM eligibility_audit WHERE created_at > now() - interval '7 days'"
        ),
        "today": await scalar(
            "SELECT count(*) FROM eligibility_audit WHERE created_at::date = now()::date"
        ),
        "avg_latency_ms": int(
            await scalar("SELECT COALESCE(avg(latency_ms), 0) FROM eligibility_audit")
        ),
    }
    year_rows = (
        await db.execute(
            text(
                "SELECT cutoff_year_used, count(*) FROM eligibility_audit "
                "GROUP BY cutoff_year_used ORDER BY cutoff_year_used DESC"
            )
        )
    ).all()
    elig["by_year_viewed"] = {str(r[0]): r[1] for r in year_rows}

    return {"conversations": conversations, "messages": messages,
            "tool_usage": tool_usage, "eligibility": elig}
