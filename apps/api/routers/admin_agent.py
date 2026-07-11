"""Admin control of the AI advisor's behavior (Phase 4 of
docs/PHASE2_STUDENT_ADMIN_PLAN.md — migration 40).

GET  /api/admin/agent-configs           — all versions + which is active +
                                          whether the built-in default is in use
GET  /api/admin/agent-configs/default   — the built-in template (starting point)
POST /api/admin/agent-configs           — save a NEW version (optionally activate)
POST /api/admin/agent-configs/{id}/activate   — activate (also = one-click rollback)
POST /api/admin/agent-configs/deactivate      — revert to the built-in default
POST /api/admin/agent-configs/test      — sandbox: run the REAL agent loop against
                                          a draft config; nothing is persisted

Every mutation is audited. Activation invalidates the in-process settings cache
immediately (other processes converge within the cache TTL).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from google import genai
from pydantic import BaseModel, Field
from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.admin_audit import log_admin_action
from apps.api.dependencies import get_current_admin, get_db
from core.chat.agent_config import (
    DEFAULT_PROMPT_TEMPLATE,
    AgentSettings,
    _load_facts,
    invalidate_agent_config_cache,
    render_template,
    resolve_agent_settings,
)
from core.chat.orchestrator import chat as run_chat
from core.config import settings
from core.models.auth import User
from core.models.chat import AgentConfig

router = APIRouter(
    prefix="/api/admin",
    tags=["admin:agent"],
    dependencies=[Depends(get_current_admin)],
)


class AgentConfigOut(BaseModel):
    config_id: int
    name: str
    system_prompt_template: str
    model_name: str
    web_search_default: bool
    max_tool_turns: int
    notes: str | None
    is_active: bool
    created_at: datetime


class AgentConfigListResponse(BaseModel):
    active_source: str  # "db:<id>" or "builtin"
    items: list[AgentConfigOut]


class AgentConfigCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    system_prompt_template: str = Field(..., min_length=50, max_length=40_000)
    model_name: str = Field(..., min_length=1, max_length=100)
    web_search_default: bool = True
    max_tool_turns: int = Field(default=6, ge=1, le=12)
    notes: str | None = Field(default=None, max_length=2000)
    activate: bool = False


class AgentTestRequest(BaseModel):
    """Sandbox a DRAFT config (fields optional — omitted ones fall back to the
    currently-active behavior) against one message. No conversation is saved."""

    message: str = Field(..., min_length=1, max_length=2000)
    system_prompt_template: str | None = Field(default=None, max_length=40_000)
    model_name: str | None = Field(default=None, max_length=100)
    web_search: bool = False  # default off in the sandbox: cheaper + deterministic
    max_tool_turns: int = Field(default=6, ge=1, le=12)
    context: dict[str, Any] | None = None


class AgentTestResponse(BaseModel):
    reply: str
    tools_used: list[str]
    rendered_prompt_preview: str  # first part of the exact prompt that ran


def _out(c: AgentConfig) -> AgentConfigOut:
    return AgentConfigOut(
        config_id=c.config_id,
        name=c.name,
        system_prompt_template=c.system_prompt_template,
        model_name=c.model_name,
        web_search_default=c.web_search_default,
        max_tool_turns=c.max_tool_turns,
        notes=c.notes,
        is_active=c.is_active,
        created_at=c.created_at,
    )


@router.get("/agent-configs", response_model=AgentConfigListResponse)
async def list_configs(db: AsyncSession = Depends(get_db)) -> AgentConfigListResponse:
    rows = (
        await db.execute(select(AgentConfig).order_by(AgentConfig.config_id.desc()))
    ).scalars().all()
    active = next((r for r in rows if r.is_active), None)
    return AgentConfigListResponse(
        active_source=f"db:{active.config_id}" if active else "builtin",
        items=[_out(r) for r in rows],
    )


@router.get("/agent-configs/default")
async def get_default(db: AsyncSession = Depends(get_db)) -> dict:
    """The built-in template + the live facts it would render with — the
    starting point for an admin writing their first custom version."""
    facts = await _load_facts(db)
    return {
        "system_prompt_template": DEFAULT_PROMPT_TEMPLATE,
        "model_name": settings.gemini_chat_model,
        "web_search_default": True,
        "max_tool_turns": 6,
        "live_facts": facts,
        "placeholders": ["{available_years}", "{latest_year}", "{course_count}", "{today}"],
    }


@router.post("/agent-configs", response_model=AgentConfigOut, status_code=status.HTTP_201_CREATED)
async def create_config(
    payload: AgentConfigCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> AgentConfigOut:
    cfg = AgentConfig(
        name=payload.name.strip(),
        system_prompt_template=payload.system_prompt_template,
        model_name=payload.model_name.strip(),
        web_search_default=payload.web_search_default,
        max_tool_turns=payload.max_tool_turns,
        notes=payload.notes,
        is_active=False,
        created_by=admin.user_id,
    )
    db.add(cfg)
    await db.flush()
    if payload.activate:
        await db.execute(update(AgentConfig).values(is_active=False))
        cfg.is_active = True
    await log_admin_action(
        db, admin=admin, action_type="agent_config.create",
        target_table="agent_configs", target_id=str(cfg.config_id),
        before=None,
        after={"name": cfg.name, "model_name": cfg.model_name, "activated": payload.activate},
        request=request,
    )
    await db.commit()
    invalidate_agent_config_cache()
    await db.refresh(cfg)
    return _out(cfg)


@router.post("/agent-configs/{config_id}/activate", response_model=AgentConfigOut)
async def activate_config(
    config_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> AgentConfigOut:
    cfg = await db.get(AgentConfig, config_id)
    if cfg is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Config not found")
    await db.execute(update(AgentConfig).values(is_active=False))
    cfg.is_active = True
    await log_admin_action(
        db, admin=admin, action_type="agent_config.activate",
        target_table="agent_configs", target_id=str(config_id),
        before=None, after={"name": cfg.name}, request=request,
    )
    await db.commit()
    invalidate_agent_config_cache()
    await db.refresh(cfg)
    return _out(cfg)


@router.post("/agent-configs/deactivate")
async def deactivate_all(
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
) -> dict:
    """Revert the agent to the built-in default prompt/model."""
    await db.execute(update(AgentConfig).values(is_active=False))
    await log_admin_action(
        db, admin=admin, action_type="agent_config.deactivate_all",
        target_table="agent_configs", target_id="*",
        before=None, after={"active_source": "builtin"}, request=request,
    )
    await db.commit()
    invalidate_agent_config_cache()
    return {"active_source": "builtin"}


@router.post("/agent-configs/test", response_model=AgentTestResponse)
async def test_config(
    payload: AgentTestRequest,
    db: AsyncSession = Depends(get_db),
) -> AgentTestResponse:
    """Run the real agent loop once with a draft config. Nothing is persisted —
    no conversation row, no cache change. Uses the same Gemini key as the live
    chat, so treat it as a real (billable/quota) call."""
    from apps.api.guards import gemini_budget

    if not gemini_budget.try_spend(1):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Daily Gemini budget exhausted — the sandbox shares the live chat's budget.",
        )

    current = await resolve_agent_settings(db)
    facts = await _load_facts(db)
    draft = AgentSettings(
        base_prompt=render_template(
            payload.system_prompt_template or DEFAULT_PROMPT_TEMPLATE, facts
        ) if payload.system_prompt_template is not None else current.base_prompt,
        model_name=payload.model_name or current.model_name,
        max_tool_turns=payload.max_tool_turns,
        web_search_default=payload.web_search,
        source="sandbox",
    )
    client = genai.Client(api_key=settings.gemini_api_key)
    try:
        reply, tools_used = await run_chat(
            session=db,
            gen_client=client,
            embed_client=client,
            history=[],
            new_message=payload.message,
            context=payload.context,
            web_search=payload.web_search,
            agent=draft,
        )
    except Exception as exc:  # surfacing the provider error is the point here
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail=f"AI service error: {exc}"
        )
    return AgentTestResponse(
        reply=reply,
        tools_used=tools_used,
        rendered_prompt_preview=draft.base_prompt[:600],
    )
