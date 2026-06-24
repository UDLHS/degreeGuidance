"""Tool implementations called by the Gemini agentic loop.

Five tools:
  find_course       — fuzzy name/abbreviation search on the courses DB table
  search_knowledge  — RAG search across all 50 factsheets
  lookup_course     — full factsheet + recent cutoffs for one course number
  get_cutoff_trend  — year-by-year Z-score history for a course-university code
  search_web        — live DuckDuckGo search filtered to trusted sources
"""

from __future__ import annotations

import asyncio
import logging
from urllib.parse import urlparse

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from google import genai

from core.rag.retrieval import retrieve

log = logging.getLogger(__name__)

# Domains we consider authoritative for Sri Lanka higher-education advice
_TRUSTED_DOMAINS = {
    "ugc.ac.lk", "moe.gov.lk", "cbsl.gov.lk", "statistics.gov.lk",
    "iesl.lk", "slmc.lk", "icasl.lk", "slaas.lk",
    "cmb.ac.lk", "pdn.ac.lk", "sjp.ac.lk", "kln.ac.lk", "mrt.ac.lk",
    "ruh.ac.lk", "ucsc.cmb.ac.lk", "uja.ac.lk", "seusl.ac.lk",
    "dailyft.lk", "dailymirror.lk", "theisland.lk", "sundayobserver.lk",
    "lmd.lk", "bizenglish.adaderana.lk",
    "worldbank.org", "ilo.org", "adb.org", "undp.org",
    "topuniversities.com", "timeshighereducation.com",
    "linkedin.com", "icaew.com", "accaglobal.com", "cimaglobal.com",
}

def _trust_score(url: str) -> int:
    """Return 2 = trusted domain, 1 = .lk or .ac, 0 = unknown."""
    try:
        host = urlparse(url).netloc.lower().lstrip("www.")
    except Exception:
        return 0
    if host in _TRUSTED_DOMAINS or any(host.endswith("." + d) for d in _TRUSTED_DOMAINS):
        return 2
    if host.endswith(".lk") or host.endswith(".ac"):
        return 1
    return 0


# Common abbreviations students use → expanded search terms
_ABBREV_MAP: dict[str, str] = {
    "ECS": "Electronics Computer Science",
    "CS": "Computer Science",
    "IT": "Information Technology",
    "ICT": "Information Communication Technology",
    "ET": "Engineering Technology",
    "BST": "Biosystems Technology",
    "BIT": "Bachelor Information Technology",
    "MIS": "Management Information Systems",
    "SE": "Software Engineering",
    "AI": "Artificial Intelligence",
    "DS": "Data Science",
    "QS": "Quantity Surveying",
    "TP": "Town Planning",
    "EM": "Estate Management",
    "FM": "Facilities Management",
    "SCI": "Science",
    "AGRI": "Agriculture",
    "BIO": "Biological",
    "CHEM": "Chemistry",
    "PHYS": "Physics",
    "MATH": "Mathematics",
    "STATS": "Statistics",
    "ECON": "Economics",
    "MGMT": "Management",
    "LAW": "Law",
    "MED": "Medicine",
    "DENT": "Dentistry",
    "VET": "Veterinary",
    "ARCH": "Architecture",
    "NURS": "Nursing",
    "PHARM": "Pharmacy",
}


async def _course_search(session: AsyncSession, terms: list[str], require_all: bool = True) -> list:
    """Run a DB search requiring all terms (or any term) to appear in course name."""
    if not terms:
        return []
    if require_all:
        conditions = " AND ".join(f"c.name_en ILIKE :t{i}" for i in range(len(terms)))
    else:
        conditions = " OR ".join(f"c.name_en ILIKE :t{i}" for i in range(len(terms)))
    params = {f"t{i}": f"%{term}%" for i, term in enumerate(terms)}
    rows = (await session.execute(
        text(
            f"SELECT c.course_code, c.course_number, c.name_en, u.name_en AS university_name "
            f"FROM courses c JOIN universities u ON u.university_id = c.university_id "
            f"WHERE ({conditions}) AND c.is_active = TRUE ORDER BY c.course_code LIMIT 20"
        ),
        params,
    )).fetchall()
    return list(rows)


async def find_course(session: AsyncSession, name_query: str) -> str:
    """Search courses table by name/abbreviation. Returns matching course codes and names."""
    raw = name_query.strip().upper()

    # Expand known abbreviations
    expanded = _ABBREV_MAP.get(raw, name_query)
    if expanded != name_query:
        log.info("find_course: expanded '%s' -> '%s'", name_query, expanded)

    # Build search terms from the (possibly expanded) query
    terms = [t for t in expanded.replace(",", " ").split() if len(t) > 1]
    if not terms:
        return "Please provide a course name or keyword to search."

    # Strategy 1: all terms must match
    rows = await _course_search(session, terms, require_all=True)

    # Strategy 2: if no results, try pairs of terms (drop the least specific)
    if not rows and len(terms) >= 3:
        for skip in range(len(terms)):
            subset = [t for i, t in enumerate(terms) if i != skip]
            rows = await _course_search(session, subset, require_all=True)
            if rows:
                break

    # Strategy 3: any single meaningful term
    if not rows:
        meaningful = [t for t in terms if len(t) > 3]
        for term in meaningful:
            rows = await _course_search(session, [term], require_all=True)
            if rows:
                break

    if not rows:
        return (
            f"No courses found matching '{name_query}' in the database. "
            "Try search_knowledge or search_web for more information."
        )

    lines = [f"Courses matching '{name_query}' (expanded: '{expanded}'):\n"]
    prev_number = None
    for r in rows:
        if r.course_number != prev_number:
            lines.append(f"\n**{r.name_en.split('(')[0].strip()}** — course number {r.course_number}")
            prev_number = r.course_number
        lines.append(f"  - {r.course_code}: {r.university_name}")

    lines.append(
        "\nCall lookup_course with the course number (e.g. '119') to get the full "
        "factsheet and Z-score cutoffs, or get_cutoff_trend with the full code "
        "(e.g. '119D') for year-by-year history."
    )
    return "\n".join(lines)


async def search_knowledge(
    session: AsyncSession,
    embed_client: genai.Client,
    query: str,
) -> str:
    """Semantic + keyword search across factsheet knowledge base."""
    results = await retrieve(session, embed_client, query, top_k=5)
    if not results:
        return "No relevant factsheet content found for that query."

    parts = []
    for r in results:
        heading = f" — {r.heading}" if r.heading else ""
        parts.append(f"**{r.title}{heading}**\n{r.content}")
    return "\n\n---\n\n".join(parts)


async def lookup_course(session: AsyncSession, course_number: str) -> str:
    """Return assembled factsheet content + recent Z-score cutoffs for a course number."""
    course_number = course_number.strip().zfill(3)

    # Fetch all chunks for this course ordered by position
    rows = (await session.execute(
        text(
            "SELECT c.heading, c.content "
            "FROM chunks c "
            "JOIN document_sources d ON d.source_id = c.source_id "
            "WHERE d.course_number = :cn "
            "ORDER BY c.chunk_index"
        ),
        {"cn": course_number},
    )).fetchall()

    if not rows:
        return f"No factsheet found for course number {course_number}."

    sections = []
    for r in rows:
        heading = f"## {r.heading}\n" if r.heading else ""
        sections.append(f"{heading}{r.content}")
    factsheet = "\n\n".join(sections)

    # Recent cutoffs (latest year, national selection basis)
    cutoff_rows = (await session.execute(
        text(
            "SELECT cu.course_code, d.name_en AS district_name, cu.z_score "
            "FROM z_score_cutoffs cu "
            "JOIN districts d ON d.district_id = cu.district_id "
            "WHERE cu.course_code LIKE :prefix "
            "  AND cu.year = (SELECT MAX(year) FROM z_score_cutoffs) "
            "  AND cu.z_score IS NOT NULL "
            "ORDER BY cu.course_code, cu.z_score DESC "
            "LIMIT 40"
        ),
        {"prefix": f"{course_number}%"},
    )).fetchall()

    if cutoff_rows:
        cutoff_lines = [f"- {r.course_code} ({r.district_name}): {float(r.z_score):.4f}" for r in cutoff_rows]
        cutoff_block = "**Recent Z-score cutoffs (2023, by district):**\n" + "\n".join(cutoff_lines)
        return f"{factsheet}\n\n{cutoff_block}"

    return factsheet


async def get_cutoff_trend(session: AsyncSession, course_code: str) -> str:
    """Return year-by-year Z-score cutoff history for a specific course-university code."""
    course_code = course_code.strip().upper()

    rows = (await session.execute(
        text(
            "SELECT cu.year, d.name_en AS district_name, cu.z_score "
            "FROM z_score_cutoffs cu "
            "JOIN districts d ON d.district_id = cu.district_id "
            "WHERE cu.course_code = :cc "
            "  AND cu.z_score IS NOT NULL "
            "ORDER BY cu.year DESC, cu.z_score DESC "
            "LIMIT 60"
        ),
        {"cc": course_code},
    )).fetchall()

    if not rows:
        return f"No cutoff history found for course code {course_code}. Make sure you're using a full code like '008A' (not just '008')."

    # Get course name from the first matching course code prefix
    name_row = (await session.execute(
        text("SELECT name_en FROM courses WHERE course_code = :cc"),
        {"cc": course_code},
    )).fetchone()
    course_name = name_row.name_en if name_row else course_code

    lines = [f"**Cutoff history for {course_name} ({course_code}):**"]
    current_year = None
    for r in rows:
        if r.year != current_year:
            current_year = r.year
            lines.append(f"\n*{r.year}:*")
        lines.append(f"  - {r.district_name}: {float(r.z_score):.4f}")

    lines.append(
        "\nNote: Cutoffs change annually based on the number of applicants and seats. "
        "Use the most recent year as a guide, not a guarantee."
    )
    return "\n".join(lines)


async def search_web(query: str) -> str:
    """Search the live web via DuckDuckGo. Returns top results ranked by source trustworthiness."""
    from ddgs import DDGS

    # Always append Sri Lanka context if not already in query
    if "sri lanka" not in query.lower():
        search_query = f"{query} Sri Lanka"
    else:
        search_query = query

    def _fetch() -> list[dict]:
        try:
            with DDGS() as ddgs:
                return list(ddgs.text(search_query, max_results=10))
        except Exception as e:
            log.warning("DuckDuckGo search failed: %s", e)
            return []

    loop = asyncio.get_event_loop()
    raw = await loop.run_in_executor(None, _fetch)

    if not raw:
        return "Web search returned no results. Please rely on the knowledge base for this query."

    # Sort by trust score descending
    scored = sorted(raw, key=lambda r: _trust_score(r.get("href", "")), reverse=True)

    parts = []
    for r in scored[:6]:
        title = r.get("title", "").strip()
        url = r.get("href", "").strip()
        body = r.get("body", "").strip()
        trust = _trust_score(url)
        badge = " [Trusted source]" if trust == 2 else (" [.lk source]" if trust == 1 else "")
        parts.append(f"**{title}**{badge}\nURL: {url}\n{body}")

    header = f'Web search results for: "{search_query}"\n\n'
    return header + "\n\n---\n\n".join(parts)
