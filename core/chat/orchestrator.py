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
from datetime import date
from typing import Any

from google import genai
from google.genai import types
from sqlalchemy.ext.asyncio import AsyncSession

from core.chat.tools import find_course, get_cutoff_trend, lookup_course, search_knowledge, search_web
from core.config import settings

log = logging.getLogger(__name__)

MAX_TOOL_TURNS = 6   # allow more turns when web search + DB tools both fire

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
            "Get the year-by-year UGC Z-score cutoff history (2019–2023) for a specific "
            "course at a specific university, identified by its full Uni-Code "
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

def _build_system_prompt(context: dict[str, Any] | None) -> str:
    today = date.today().strftime("%B %d, %Y")

    prompt = f"""You are a senior academic advisor specialising in Sri Lankan state university admissions and graduate career pathways. Today is {today}.

## Your tools and when to use them

- **`lookup_course`** — fetch the full degree factsheet + UGC Z-score cutoffs. Use for any question about a specific degree.
- **`get_cutoff_trend`** — year-by-year cutoff history (2019–2023). Use when a student asks if cutoffs are rising or falling.
- **`search_knowledge`** — search the local factsheet knowledge base. Use for curriculum details, subject areas, general degree comparisons.
- **`search_web`** — search the live internet. Use for: graduate salary ranges, job market demand, top employers in Sri Lanka, professional body requirements (IESL, SLMC, ACCA, CIMA), postgraduate and scholarship options, industry growth trends, university rankings. Results are marked [Trusted source] for authoritative sites.

## Rules

### When you don't know the course code — MANDATORY tool sequence
If a student mentions a course by name, abbreviation, or nickname you don't immediately recognise (e.g. "ECS", "Bio Systems", "Quantity Surveying", "Textile Technology", "Town Planning", "Nursing", "Law", "ICT"), you **must** do ALL of the following before answering:
1. Call `find_course` with the name/abbreviation → this searches the database by name and returns the real course code(s)
2. Call `lookup_course` with the course number found → get the factsheet and cutoffs
3. Only THEN answer the student

**NEVER say "I don't have data on this course", "this course is not listed", or "I cannot find this" without first calling `find_course`.** The database has all 261 UGC courses. If `find_course` returns no results, THEN call `search_knowledge` and `search_web`.

### Other rules
1. **Never guess a Z-score cutoff.** Always pull from the database via `lookup_course` or `get_cutoff_trend`.
2. **For career questions**, call `search_knowledge` first, then `search_web` for current Sri Lanka market data. Synthesise both.
3. **Cite sources.** Name them: "According to the Engineering factsheet..." or "Source: [URL]". Discard untrustworthy web results.
4. **Never fabricate statistics.** If unverified, say so explicitly.
5. **Be direct.** "I recommend..." not "You might consider...".
6. **Be honest about data age.** "These are 2023 cutoffs — they shift 0.05–0.10 each year."
7. **Personalise.** Use the student's Z-score and district to say whether they're competitive for a course.
8. **End with one actionable next step** every time.
"""

    if context:
        z = context.get("z_score")
        district = context.get("district_code", "").replace("_", " ").title()
        stream = context.get("stream_code", "").replace("_", " ").title()
        subjects = context.get("subjects")
        interests = context.get("interests")
        eligible_courses: list[dict] = context.get("eligible_courses") or []

        lines = ["\n## This student's profile (from the eligibility form they just filled in)"]
        if z is not None:
            lines.append(f"- Z-score: **{z}**")
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
                "\n**Safe** = comfortably above cutoff. "
                "**Ambitious** = right at the edge (within ~0.05). "
                "**Consider** = worth knowing about.\n"
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
) -> tuple[str, list[str]]:
    """Run the agentic loop. Returns (reply_text, tools_used_names)."""

    system_prompt = _build_system_prompt(context)

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

    for turn in range(MAX_TOOL_TURNS):
        response = gen_client.models.generate_content(
            model=settings.gemini_chat_model,
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
