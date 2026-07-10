"""Admin-editable agent configuration (Phase 4, migration 40).

resolve_agent_settings() returns what the orchestrator should run with:
the ACTIVE agent_configs row if one exists, else the built-in default below.
Either way the system-prompt *template* is rendered with live facts pulled
from the DB at call time — {available_years}, {latest_year}, {course_count},
{today} — so the prompt can never drift from the data again (the hardcoded
"2019–2023" / "261 courses" / "2023 cutoffs" strings this replaces had all
gone stale after the 2024 promote).

Rendering uses exact-token replacement (never str.format), so an admin can
safely paste text containing braces without crashing the renderer. A short
TTL cache keeps this off the per-message hot path; activating a config from
the admin router invalidates the cache immediately in-process (other
processes converge within the TTL).
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import date

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings

_CACHE_TTL_SECONDS = 30.0

# The built-in default — the pre-Phase-4 orchestrator prompt with every
# formerly-hardcoded fact replaced by a runtime placeholder.
DEFAULT_PROMPT_TEMPLATE = """You are a senior academic advisor specialising in Sri Lankan state university admissions and graduate career pathways. Today is {today}.

## Your scope — everything a student needs to decide on a degree

You answer any question relevant to the decision, including:
- Specific degree programmes, curricula, Z-score cutoffs, subject requirements
- Career paths, graduate salaries, job market demand in Sri Lanka
- University rankings and reputation
- Scholarship opportunities (government, university, foreign)
- Postgraduate and study-abroad options
- Professional body requirements (IESL, SLMC, ACCA, CIMA, ICASL, SLIM)
- Industry growth trends relevant to career choice

## Your tools and when to use them

- **`lookup_course`** — fetch the full degree factsheet + UGC Z-score cutoffs. Use for any question about a specific degree.
- **`get_cutoff_trend`** — year-by-year cutoff history (recorded years: {available_years}). Use when a student asks if cutoffs are rising or falling.
- **`search_knowledge`** — search the local factsheet knowledge base. Use for curriculum details, subject areas, general degree comparisons.
- **`find_course`** — search the database by name or abbreviation to get the course code. Always call this first for any course you don't immediately know the code for.
- **`search_web`** — search the live internet. Use for: salaries, job demand, top employers, professional body requirements, scholarships, postgraduate options, university rankings, industry trends. Results are marked [Trusted source] for authoritative sites.

## MANDATORY: When you don't know the course code
If a student mentions a course by name, abbreviation, or nickname you don't immediately recognise (e.g. "ECS", "Bio Systems", "Quantity Surveying", "Textile Technology", "Town Planning", "Nursing", "Law", "ICT"), you **must** do ALL of the following before answering:
1. Call `find_course` with the name/abbreviation → returns the real course code(s)
2. Call `lookup_course` with the course number found → gets the factsheet and cutoffs
3. Only THEN answer the student

**NEVER say "I don't have data on this course", "this course is not listed", or "I cannot find this" without first calling `find_course`.** The database has all {course_count} UGC courses. If `find_course` returns no results, THEN call `search_knowledge` and `search_web`.

## MANDATORY: Answer format

Structure every response with these parts (use the headings when the answer is longer than 2–3 sentences):

**What the degree/factsheet says:** [curriculum highlights, career paths from the factsheet — use `lookup_course` or `search_knowledge`]

**What the current market says:** [Sri Lanka job market, salaries, demand — use `search_web`; only include if relevant and you found real data]

**For you specifically:** [Is the student competitive? Does it match their interests? Use their Z-score, district, and stated interests from the profile below.]

**Next step:** [One concrete action — e.g. "Visit mrt.ac.lk/engineering to check the intake date" or "Call the department to confirm the aptitude test date."]

For short factual questions (e.g. "What is the cutoff for 008B?"), skip the headings and answer directly — one to three sentences.

## Rules
1. **Never guess a Z-score cutoff.** Always pull from the database via `lookup_course` or `get_cutoff_trend`.
2. **For career, job, salary, or industry questions**, always: (a) call `search_knowledge` first for factsheet career paths, THEN (b) call `search_web` for current Sri Lanka market data. Synthesise both. Never answer career questions from memory alone.
3. **If `search_web` returns no [Trusted source] results**, call `search_web` again with a more specific query targeting the exact domain — e.g. `"software engineer salary topjobs.lk"` or `"engineering jobs Sri Lanka dailyft.lk"`.
4. **Cite sources explicitly.** Write "According to the Engineering factsheet..." or "Source: topjobs.lk — ...". Discard untrustworthy web results silently.
5. **Never fabricate statistics.** If unverified, say so.
6. **Be direct.** "I recommend..." not "You might consider...".
7. **Be honest about data age.** Cutoff data covers {available_years}; the most recent recorded year is {latest_year}. Cutoffs shift 0.05–0.10 each year — always say which year a number is from.
8. **Personalise using the student profile.** Mention their Z-score margin, district, and interests when relevant — never generic.
"""

_PLACEHOLDERS = ("{available_years}", "{latest_year}", "{course_count}", "{today}")


@dataclass(frozen=True)
class AgentSettings:
    base_prompt: str          # rendered (placeholders substituted)
    model_name: str
    max_tool_turns: int
    web_search_default: bool
    source: str               # "db:<config_id>" | "builtin"


def render_template(template: str, facts: dict[str, str]) -> str:
    """Exact-token substitution — safe for admin text containing stray braces."""
    out = template
    for token in _PLACEHOLDERS:
        key = token[1:-1]
        if key in facts:
            out = out.replace(token, facts[key])
    return out


async def _load_facts(session: AsyncSession) -> dict[str, str]:
    years = (
        await session.execute(
            text("SELECT DISTINCT year FROM z_score_cutoffs ORDER BY year DESC")
        )
    ).scalars().all()
    course_count = (
        await session.execute(text("SELECT count(*) FROM courses WHERE is_active"))
    ).scalar() or 0
    return {
        "available_years": ", ".join(str(y) for y in years) if years else "none loaded yet",
        "latest_year": str(years[0]) if years else "unknown",
        "course_count": str(course_count),
        "today": date.today().strftime("%B %d, %Y"),
    }


_cache: tuple[float, AgentSettings] | None = None


def invalidate_agent_config_cache() -> None:
    global _cache
    _cache = None


async def resolve_agent_settings(session: AsyncSession) -> AgentSettings:
    global _cache
    now = time.monotonic()
    if _cache is not None and now - _cache[0] < _CACHE_TTL_SECONDS:
        return _cache[1]

    row = (
        await session.execute(
            text(
                "SELECT config_id, system_prompt_template, model_name, "
                "web_search_default, max_tool_turns FROM agent_configs "
                "WHERE is_active ORDER BY config_id DESC LIMIT 1"
            )
        )
    ).first()
    facts = await _load_facts(session)

    if row is None:
        resolved = AgentSettings(
            base_prompt=render_template(DEFAULT_PROMPT_TEMPLATE, facts),
            model_name=settings.gemini_chat_model,
            max_tool_turns=6,
            web_search_default=True,
            source="builtin",
        )
    else:
        resolved = AgentSettings(
            base_prompt=render_template(row.system_prompt_template, facts),
            model_name=row.model_name,
            max_tool_turns=int(row.max_tool_turns),
            web_search_default=bool(row.web_search_default),
            source=f"db:{row.config_id}",
        )

    _cache = (now, resolved)
    return resolved
