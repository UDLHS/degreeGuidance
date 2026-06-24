"""Gemini agentic loop for the degree guidance chatbot.

Single-turn tool-calling pattern:
  1. Build system prompt with student context
  2. Send conversation history + new message to Gemini with tool declarations
  3. If Gemini issues a function call → execute tool → send result back
  4. Repeat up to MAX_TOOL_TURNS times
  5. Return final text response
"""

from __future__ import annotations

import json
import logging
from datetime import date
from typing import Any

from google import genai
from google.genai import types
from sqlalchemy.ext.asyncio import AsyncSession

from core.chat.tools import get_cutoff_trend, lookup_course, search_knowledge
from core.config import settings

log = logging.getLogger(__name__)

MAX_TOOL_TURNS = 4

TOOL_DECLARATIONS = [
    types.FunctionDeclaration(
        name="search_knowledge",
        description=(
            "Search the factsheet knowledge base for information about Sri Lankan degree programmes, "
            "universities, career paths, entry requirements, or any admissions-related topic. "
            "Use this for general questions. Always prefer this over making up answers."
        ),
        parameters=types.Schema(
            type="OBJECT",
            properties={"query": types.Schema(type="STRING", description="The search query")},
            required=["query"],
        ),
    ),
    types.FunctionDeclaration(
        name="lookup_course",
        description=(
            "Get the complete factsheet and recent Z-score cutoffs for a specific course "
            "identified by its 3-digit course number (e.g. '001' for Medicine, '008' for "
            "Engineering, '012' for Computer Science, '016' for Management). "
            "Use when the student asks about a specific degree programme."
        ),
        parameters=types.Schema(
            type="OBJECT",
            properties={
                "course_number": types.Schema(
                    type="STRING",
                    description="3-digit course number, e.g. '008' for Engineering, '001' for Medicine",
                )
            },
            required=["course_number"],
        ),
    ),
    types.FunctionDeclaration(
        name="get_cutoff_trend",
        description=(
            "Get the year-by-year Z-score cutoff history for a specific course at a specific "
            "university, identified by its course code (course number + university letter suffix). "
            "E.g. '008A' = Engineering at Peradeniya, '001A' = Medicine at Colombo, '012A' = "
            "Computer Science at UCSC. Use when the student asks about cutoff trends or history."
        ),
        parameters=types.Schema(
            type="OBJECT",
            properties={
                "course_code": types.Schema(
                    type="STRING",
                    description="Full course code e.g. '008A', '001B', '012A'",
                )
            },
            required=["course_code"],
        ),
    ),
]


def _build_system_prompt(context: dict[str, Any] | None) -> str:
    today = date.today().strftime("%B %d, %Y")
    base = (
        f"You are an expert AI guide for Sri Lankan university admissions (today: {today}). "
        "You help A/L students understand their degree options, eligibility, Z-scores, career paths, "
        "and university differences.\n\n"
        "You have access to three tools:\n"
        "- search_knowledge: semantic search across 50 degree factsheets\n"
        "- lookup_course: full factsheet + cutoffs for a specific course number\n"
        "- get_cutoff_trend: year-by-year cutoff history for a specific course code\n\n"
        "Rules:\n"
        "- ALWAYS use a tool before answering questions about specific courses, Z-scores, or careers\n"
        "- Cite where information comes from (e.g. 'According to the Engineering factsheet...')\n"
        "- State that cutoffs change yearly and 2023 data is the most recent available\n"
        "- Be concise, practical, and encouraging\n"
        "- If unsure, search_knowledge first\n"
    )

    if context:
        z = context.get("z_score")
        district = context.get("district_code", "").replace("_", " ").title()
        stream = context.get("stream_code", "").replace("_", " ").title()
        parts = ["\nStudent profile:"]
        if z is not None:
            parts.append(f"  Z-score: {z}")
        if district:
            parts.append(f"  District: {district}")
        if stream:
            parts.append(f"  Stream: {stream}")
        subjects = context.get("subjects")
        if subjects:
            subj_str = ", ".join(f"{s['subject']} ({s['grade']})" for s in subjects)
            parts.append(f"  A/L subjects: {subj_str}")
        base += "\n".join(parts)

    return base


async def _execute_tool(
    session: AsyncSession,
    embed_client: genai.Client,
    name: str,
    args: dict[str, Any],
) -> str:
    try:
        if name == "search_knowledge":
            return await search_knowledge(session, embed_client, args["query"])
        if name == "lookup_course":
            return await lookup_course(session, args["course_number"])
        if name == "get_cutoff_trend":
            return await get_cutoff_trend(session, args["course_code"])
        return f"Unknown tool: {name}"
    except Exception as exc:
        log.exception("Tool %s failed: %s", name, exc)
        return f"Tool error: {exc}"


async def chat(
    session: AsyncSession,
    gen_client: genai.Client,
    embed_client: genai.Client,
    history: list[dict[str, str]],
    new_message: str,
    context: dict[str, Any] | None = None,
) -> tuple[str, list[str]]:
    """Run the agentic loop. Returns (reply_text, tools_used_names)."""

    system_prompt = _build_system_prompt(context)

    # Build Gemini contents from saved history
    contents: list[types.Content] = []
    for msg in history:
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))

    # Append the new user message
    contents.append(types.Content(role="user", parts=[types.Part(text=new_message)]))

    tools_used: list[str] = []
    tool_obj = types.Tool(function_declarations=TOOL_DECLARATIONS)
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        tools=[tool_obj],
    )

    for _ in range(MAX_TOOL_TURNS):
        response = gen_client.models.generate_content(
            model=settings.gemini_chat_model,
            contents=contents,
            config=config,
        )

        candidate = response.candidates[0]
        part = candidate.content.parts[0]

        # If the model returns a function call, execute it
        if part.function_call:
            fc = part.function_call
            tools_used.append(fc.name)
            tool_result = await _execute_tool(session, embed_client, fc.name, dict(fc.args))

            # Append model's function call turn + tool result turn
            contents.append(candidate.content)
            contents.append(
                types.Content(
                    role="user",
                    parts=[
                        types.Part(
                            function_response=types.FunctionResponse(
                                name=fc.name,
                                response={"result": tool_result},
                            )
                        )
                    ],
                )
            )
        else:
            # Final text response
            return part.text or "(no response)", tools_used

    return "I couldn't complete that in time. Please try a more specific question.", tools_used
