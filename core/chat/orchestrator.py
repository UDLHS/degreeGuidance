"""Gemini agentic loop for the degree guidance chatbot.

Tool priority:
  1. lookup_course / get_cutoff_trend  — structured DB data; used for exact cutoffs and course facts
  2. search_knowledge                  — factsheet KB; used for curriculum, career paths in factsheets
  3. Google Search (built-in grounding) — live web; used for current job market, salaries, industry
     trends, employer data, postgraduate options, professional body requirements

The model decides which tools to use; the system prompt guides the decision.
"""

from __future__ import annotations

import logging
from typing import Any

from google import genai
from google.genai import types
from sqlalchemy.ext.asyncio import AsyncSession

from core.chat.agent_config import AgentSettings, resolve_agent_settings
from core.chat.tools import find_course, get_cutoff_trend, lookup_course, search_knowledge, search_web

log = logging.getLogger(__name__)

MAX_TOOL_TURNS = 6   # fallback bound; the active AgentConfig can override (1..12)

# ---------------------------------------------------------------------------
# Tool declarations (function-calling tools backed by our DB / factsheet KB)
# ---------------------------------------------------------------------------

FUNCTION_DECLARATIONS = [
    types.FunctionDeclaration(
        name="find_course",
        description=(
            "Search the database for degree programmes by name, abbreviation, or keyword. "
            "Use this FIRST whenever a student mentions a course you don't immediately have "
            "a code for — e.g. 'ECS', 'Electronics', 'Bio Systems', 'ICT', 'Law', 'Architecture', "
            "'Quantity Surveying', 'Textile', 'Town Planning', 'Nursing', etc. "
            "Returns matching course codes and university names so you can then call "
            "lookup_course or get_cutoff_trend with the exact code."
        ),
        parameters=types.Schema(
            type="OBJECT",
            properties={
                "name_query": types.Schema(
                    type="STRING",
                    description=(
                        "Course name, abbreviation, or keyword. E.g. 'Electronics Computer Science', "
                        "'ECS', 'Quantity Surveying', 'Law', 'Bio Systems Technology', 'Nursing'."
                    ),
                )
            },
            required=["name_query"],
        ),
    ),
    types.FunctionDeclaration(
        name="search_knowledge",
        description=(
            "Search the curated factsheet knowledge base for information about Sri Lankan state "
            "university degree programmes — curriculum details, subject areas, career paths "
            "mentioned in the factsheet, entry requirements, and university comparisons. "
            "Use this FIRST for general degree or career questions before doing a web search."
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
            "Get the complete factsheet AND recent UGC Z-score cutoffs for a specific course "
            "identified by its 3-digit course number. "
            "Examples: '001'=Medicine, '008'=Engineering, '012'=Computer Science, "
            "'016'=Management, '032'=Law, '050'=Architecture. "
            "Always call this when the student asks about a specific degree programme or its cutoffs."
        ),
        parameters=types.Schema(
            type="OBJECT",
            properties={
                "course_number": types.Schema(
                    type="STRING",
                    description="3-digit course number, zero-padded, e.g. '008', '001', '012'",
                )
            },
            required=["course_number"],
        ),
    ),
    types.FunctionDeclaration(
        name="get_cutoff_trend",
        description=(
            "Get the year-by-year UGC Z-score cutoff history (every recorded year) for a "
            "specific course at a specific university, identified by its full Uni-Code "
            "(course number + university letter). "
            "Examples: '008B'=Engineering at Moratuwa, '001A'=Medicine at Colombo, "
            "'012A'=Computer Science at UCSC, '008A'=Engineering at Peradeniya. "
            "Use when the student asks about cutoff trends, whether cutoffs are rising or falling, "
            "or wants a multi-year view."
        ),
        parameters=types.Schema(
            type="OBJECT",
            properties={
                "course_code": types.Schema(
                    type="STRING",
                    description="Full Uni-Code e.g. '008B', '001A', '012A'",
                )
            },
            required=["course_code"],
        ),
    ),
    types.FunctionDeclaration(
        name="search_web",
        description=(
            "Search the live internet for current, real-world information. "
            "Use this for: graduate salary ranges, job market demand, top employers hiring "
            "in Sri Lanka, industry growth trends, professional body membership requirements "
            "(IESL, SLMC, ACCA, CIMA, ICASL), postgraduate scholarship opportunities, "
            "overseas study options, university rankings, and any question requiring "
            "up-to-date data not found in the factsheets. "
            "Results are ranked by source trustworthiness — prefer [Trusted source] results. "
            "Do NOT use this for Z-score cutoffs — use lookup_course or get_cutoff_trend instead."
        ),
        parameters=types.Schema(
            type="OBJECT",
            properties={
                "query": types.Schema(
                    type="STRING",
                    description=(
                        "The search query. Be specific — include the field, country, and year "
                        "if relevant. E.g. 'Computer Science graduate salary Sri Lanka 2024' or "
                        "'IESL membership requirements for civil engineers Sri Lanka'."
                    ),
                )
            },
            required=["query"],
        ),
    ),
]


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

def _build_system_prompt(
    base_prompt: str, context: dict[str, Any] | None, web_search: bool = False
) -> str:
    """Append the structural sections (web-search mode + student profile) to
    the admin-configurable base prompt. The base comes from
    core/chat/agent_config.py — the active agent_configs row (or the built-in
    default), rendered with live facts ({available_years}, {latest_year},
    {course_count}, {today}). The profile/eligible-table blocks below stay
    code-owned: they are data plumbing, not admin-tunable tone/policy."""
    prompt = base_prompt

    if web_search:
        prompt += (
            "\n## Enhanced web search mode (user-activated)\n"
            "The student has turned on live web search. For EVERY question — not just career questions — "
            "call `search_web` to find the most current information before answering. "
            "Prioritise freshness: salary figures, job market trends, scholarship deadlines, university news, "
            "and professional body requirements change frequently. Always note when information comes from a live source.\n"
        )

    if context:
        z = context.get("z_score")
        district = context.get("district_code", "").replace("_", " ").title()
        stream = context.get("stream_code", "").replace("_", " ").title()
        exam_year = context.get("exam_year")
        subjects = context.get("subjects")
        interests = context.get("interests")
        eligible_courses: list[dict] = context.get("eligible_courses") or []

        lines = ["\n## This student's profile (from the eligibility form they just filled in)"]
        if z is not None:
            lines.append(f"- Z-score: **{z}**")
        if exam_year:
            lines.append(
                f"- Viewing cutoffs for exam year: **{exam_year}** — their eligible-course "
                f"list below is computed against {exam_year} cutoffs; when quoting cutoffs, "
                f"say which year they are from."
            )
        if district:
            lines.append(f"- District: **{district}**")
        if stream:
            lines.append(f"- A/L stream: **{stream}**")
        if subjects:
            subj_str = ", ".join(f"{s['subject']} ({s['grade']})" for s in subjects)
            lines.append(f"- A/L subjects: {subj_str}")
        if interests:
            lines.append(f"- What they told us they're interested in: \"{interests}\"")

        if eligible_courses:
            lines.append(
                f"\n## Courses this student is eligible for ({len(eligible_courses)} total)\n"
                "These are already verified against their Z-score and district cutoffs. "
                "**When they ask about interests, career paths, or 'what should I choose', "
                "always filter THIS list first — never recommend a course they cannot get into.**\n"
            )
            lines.append("| Course | Code | University | Cutoff | Margin | Status |")
            lines.append("|--------|------|-----------|--------|--------|--------|")
            for c in eligible_courses[:40]:
                margin = c.get("margin", 0)
                margin_str = f"+{margin:.4f}" if margin >= 0 else f"{margin:.4f}"
                bucket = c.get("bucket", "").capitalize()
                lines.append(
                    f"| {c['course_name']} | {c['course_code']} | {c['university']} "
                    f"| {c['cutoff']:.4f} | {margin_str} | {bucket} |"
                )
            lines.append(
                "\n**Safe** = comfortably above the cutoff. "
                "**Consider** = eligible, with less headroom above the cutoff.\n"
                "(Every course in this table is one the student is ELIGIBLE for. Courses that "
                "sit just ABOVE their score — the separate 'Ambitious'/later-rounds set — are "
                "NOT in this table; never present those as courses they can currently get into.)\n"
                "When the student asks 'I like X, what should I choose?' — scan this table for "
                "courses matching their interest, then explain WHY each one fits, using "
                "`lookup_course` to get more detail if needed."
            )
        else:
            lines.append(
                "\nNo eligible course list available — use `lookup_course` and compare the "
                "cutoff against the student's Z-score and district manually."
            )

        prompt += "\n".join(lines)

    return prompt


# ---------------------------------------------------------------------------
# Tool executor
# ---------------------------------------------------------------------------

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
        if name == "search_web":
            return await search_web(args["query"])
        if name == "find_course":
            return await find_course(session, args["name_query"])
        return f"Unknown tool: {name}"
    except Exception as exc:
        log.exception("Tool %s failed: %s", name, exc)
        return f"Tool error: {exc}"


# ---------------------------------------------------------------------------
# Agentic loop
# ---------------------------------------------------------------------------

async def chat(
    session: AsyncSession,
    gen_client: genai.Client,
    embed_client: genai.Client,
    history: list[dict[str, str]],
    new_message: str,
    context: dict[str, Any] | None = None,
    web_search: bool | None = None,
    agent: AgentSettings | None = None,
) -> tuple[str, list[str]]:
    """Run the agentic loop. Returns (reply_text, tools_used_names).

    Behavior (prompt/model/turn-bound/web-search default) comes from the active
    admin AgentConfig, or the built-in default when none is active. `agent` may
    be passed explicitly (the admin sandbox tests a draft config this way);
    `web_search=None` means "use the config's default"."""

    if agent is None:
        agent = await resolve_agent_settings(session)
    if web_search is None:
        web_search = agent.web_search_default

    system_prompt = _build_system_prompt(agent.base_prompt, context, web_search=web_search)

    # Build Gemini contents from saved history
    contents: list[types.Content] = []
    for msg in history:
        role = "model" if msg["role"] == "assistant" else "user"
        contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))

    contents.append(types.Content(role="user", parts=[types.Part(text=new_message)]))

    tools_used: list[str] = []

    tool_config = [
        types.Tool(function_declarations=FUNCTION_DECLARATIONS),
    ]

    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        tools=tool_config,
    )

    for turn in range(agent.max_tool_turns):
        response = gen_client.models.generate_content(
            model=agent.model_name,
            contents=contents,
            config=config,
        )

        candidate = response.candidates[0]

        # Scan all parts for function calls
        fc_part = None
        text_parts: list[str] = []
        for part in candidate.content.parts:
            if getattr(part, "function_call", None):
                fc_part = part
            elif getattr(part, "text", None):
                text_parts.append(part.text)

        if fc_part is not None:
            fc = fc_part.function_call
            tools_used.append(fc.name)
            tool_result = await _execute_tool(session, embed_client, fc.name, dict(fc.args))

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
            # Text response (possibly grounded via web search)
            reply = " ".join(text_parts).strip() or "(no response)"
            return reply, tools_used

    return "I wasn't able to complete that in time. Please try a more specific question.", tools_used
