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
    # Government / regulatory
    "ugc.ac.lk", "moe.gov.lk", "mohe.gov.lk", "cbsl.gov.lk", "statistics.gov.lk",
    "scholarship.gov.lk", "nec.gov.lk", "labourdept.gov.lk", "boi.lk",
    # Industry / tech bodies
    "icta.lk", "sltda.gov.lk",
    # Professional bodies
    "iesl.lk", "slmc.lk", "icasl.lk", "slaas.lk", "slim.lk",
    "icaew.com", "accaglobal.com", "cimaglobal.com",
    # Sri Lankan universities
    "cmb.ac.lk", "pdn.ac.lk", "sjp.ac.lk", "kln.ac.lk", "mrt.ac.lk",
    "ruh.ac.lk", "ucsc.cmb.ac.lk", "uja.ac.lk", "seusl.ac.lk",
    # Sri Lankan news / business
    "dailyft.lk", "dailymirror.lk", "theisland.lk", "sundayobserver.lk",
    "lmd.lk", "bizenglish.adaderana.lk",
    # Sri Lankan jobs / careers
    "topjobs.lk", "jobs.lk", "xjobs.lk",
    # International orgs
    "worldbank.org", "ilo.org", "adb.org", "undp.org",
    # University rankings
    "topuniversities.com", "timeshighereducation.com", "webometrics.info",
    # Professional networking / certification
    "linkedin.com", "wes.org",
}

# Topic → priority trusted domains to scope-search first.
# Ordered from most-specific to most-general so the first match wins.
_TOPIC_PRIORITY: list[tuple[list[str], list[str]]] = [
    # Professional body accreditation
    (
        ["iesl", "chartered engineer", "engineering accredit", "professional engineer"],
        ["iesl.lk", "ugc.ac.lk"],
    ),
    (
        ["slmc", "medical council", "doctor register", "medicine accredit"],
        ["slmc.lk", "ugc.ac.lk"],
    ),
    (
        ["acca", "cima", "accountan", "icasl", "chartered accountant"],
        ["accaglobal.com", "cimaglobal.com", "icasl.lk"],
    ),
    # Scholarships / funding
    (
        ["scholarship", "bursary", "mahapola", "stipend", "study abroad fund"],
        ["scholarship.gov.lk", "mohe.gov.lk", "ugc.ac.lk"],
    ),
    # Postgraduate / further study
    (
        ["postgrad", "masters", "msc", "mba", "phd", "study abroad", "overseas", "further study"],
        ["ugc.ac.lk", "topuniversities.com", "scholarship.gov.lk", "mohe.gov.lk"],
    ),
    # University rankings
    (
        ["ranking", "world rank", "qs rank", "times higher", "best university"],
        ["topuniversities.com", "timeshighereducation.com", "webometrics.info"],
    ),
    # Salary / pay
    (
        ["salary", "pay", "wage", "earning", "income", "remuneration", "how much"],
        ["topjobs.lk", "jobs.lk", "lmd.lk", "dailyft.lk"],
    ),
    # Labour market statistics
    (
        ["employment rate", "unemployment", "labour force", "workforce statistic", "survey"],
        ["statistics.gov.lk", "labourdept.gov.lk", "worldbank.org", "ilo.org"],
    ),
    # IT / tech sector
    (
        ["it sector", "software industry", "tech industry", "icta", "it export", "software job"],
        ["icta.lk", "dailyft.lk", "worldbank.org", "topjobs.lk"],
    ),
    # Tourism / hospitality
    (
        ["tourism", "hotel", "hospitality", "sltda"],
        ["sltda.gov.lk", "dailyft.lk", "worldbank.org"],
    ),
    # Economy / investment
    (
        ["industry growth", "sector growth", "gdp", "economy", "investment", "boi"],
        ["worldbank.org", "adb.org", "cbsl.gov.lk", "boi.lk", "dailyft.lk"],
    ),
    # Career paths / job opportunities — catches the most common student questions
    # ("what career", "job after", "what can I do", "prospects", "future", "work as")
    (
        ["career", "job", "work", "profession", "prospect", "future", "opportunit",
         "employ", "hire", "demand for", "what can i", "what will i"],
        ["topjobs.lk", "jobs.lk", "dailyft.lk", "lmd.lk", "worldbank.org"],
    ),
]

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

    # Recent cutoffs (latest year, national selection basis). UNIONs in the
    # per-stream overrides too (e.g. 107L Food Business Management has no
    # general cutoff -- see course_stream_cutoff_overrides) so a stream-split
    # course doesn't silently disappear from this factsheet.
    # The label must state the ACTUAL latest year (multiple A/L years are now
    # loaded) — never a hardcoded one — so the agent quotes the right year.
    latest_year = (
        await session.execute(text("SELECT MAX(year) FROM z_score_cutoffs"))
    ).scalar()
    cutoff_rows = (await session.execute(
        text(
            "SELECT cu.course_code, d.name_en AS district_name, cu.z_score, NULL AS stream_name "
            "FROM z_score_cutoffs cu "
            "JOIN districts d ON d.district_id = cu.district_id "
            "WHERE cu.course_code LIKE :prefix "
            "  AND cu.year = (SELECT MAX(year) FROM z_score_cutoffs) "
            "  AND cu.z_score IS NOT NULL "
            "UNION ALL "
            "SELECT so.course_code, d.name_en AS district_name, so.z_score, s.name_en AS stream_name "
            "FROM course_stream_cutoff_overrides so "
            "JOIN districts d ON d.district_id = so.district_id "
            "JOIN streams s ON s.stream_id = so.stream_id "
            "WHERE so.course_code LIKE :prefix "
            "  AND so.year = (SELECT MAX(year) FROM z_score_cutoffs) "
            "  AND so.z_score IS NOT NULL "
            "ORDER BY 1, 3 DESC "
            "LIMIT 40"
        ),
        {"prefix": f"{course_number}%"},
    )).fetchall()

    if cutoff_rows:
        cutoff_lines = [
            f"- {r.course_code} ({r.district_name}"
            + (f", {r.stream_name} stream" if r.stream_name else "")
            + f"): {float(r.z_score):.4f}"
            for r in cutoff_rows
        ]
        cutoff_block = (
            f"**Recent Z-score cutoffs ({latest_year}, by district):**\n" + "\n".join(cutoff_lines)
        )
        return f"{factsheet}\n\n{cutoff_block}"

    return factsheet


async def get_cutoff_trend(session: AsyncSession, course_code: str) -> str:
    """Return year-by-year Z-score cutoff history for a specific course-university code."""
    course_code = course_code.strip().upper()

    # UNION in per-stream overrides (e.g. 107L has no general cutoff row --
    # see course_stream_cutoff_overrides) so a stream-split course still
    # shows its real history instead of "no cutoff history found".
    rows = (await session.execute(
        text(
            "SELECT cu.year, d.name_en AS district_name, cu.z_score, NULL AS stream_name "
            "FROM z_score_cutoffs cu "
            "JOIN districts d ON d.district_id = cu.district_id "
            "WHERE cu.course_code = :cc "
            "  AND cu.z_score IS NOT NULL "
            "UNION ALL "
            "SELECT so.year, d.name_en AS district_name, so.z_score, s.name_en AS stream_name "
            "FROM course_stream_cutoff_overrides so "
            "JOIN districts d ON d.district_id = so.district_id "
            "JOIN streams s ON s.stream_id = so.stream_id "
            "WHERE so.course_code = :cc "
            "  AND so.z_score IS NOT NULL "
            "ORDER BY 1 DESC, 3 DESC "
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
        stream_suffix = f" ({r.stream_name} stream)" if r.stream_name else ""
        lines.append(f"  - {r.district_name}{stream_suffix}: {float(r.z_score):.4f}")

    lines.append(
        "\nNote: Cutoffs change annually based on the number of applicants and seats. "
        "Use the most recent year as a guide, not a guarantee."
    )
    return "\n".join(lines)


async def search_web(query: str) -> str:
    """Search live web. First queries priority trusted domains for this topic, then runs a
    general search. Both run concurrently; results are merged (trusted-domain hits first),
    deduplicated, and sorted by trust score before returning."""
    from ddgs import DDGS

    if "sri lanka" not in query.lower():
        base_query = f"{query} Sri Lanka"
    else:
        base_query = query

    # Pick priority domains based on query topic
    q_lower = query.lower()
    priority_domains: list[str] = []
    for keywords, domains in _TOPIC_PRIORITY:
        if any(kw in q_lower for kw in keywords):
            priority_domains = domains
            break

    def _fetch(q: str, n: int = 10) -> list[dict]:
        try:
            with DDGS(timeout=15) as ddgs:
                return list(ddgs.text(q, max_results=n))
        except Exception as e:
            log.warning("DuckDuckGo search failed (%s): %s", q[:60], e)
            return []

    loop = asyncio.get_event_loop()

    # Build site-scoped query for priority domains (max 4 to keep query length sane)
    scoped_raw: list[dict] = []
    if priority_domains:
        site_clause = " OR ".join(f"site:{d}" for d in priority_domains[:4])
        scoped_query = f"{base_query} ({site_clause})"
        scoped_task = loop.run_in_executor(None, lambda: _fetch(scoped_query, 6))
        general_task = loop.run_in_executor(None, lambda: _fetch(base_query, 10))
        scoped_raw, general_raw = await asyncio.gather(scoped_task, general_task)
    else:
        general_raw = await loop.run_in_executor(None, lambda: _fetch(base_query, 10))

    # Merge: scoped (trusted-domain) results first, then general; deduplicate by URL
    seen: set[str] = set()
    merged: list[dict] = []
    for r in scoped_raw + general_raw:
        url = r.get("href", "")
        if url and url not in seen:
            seen.add(url)
            merged.append(r)

    if not merged:
        return "Web search returned no results. Please rely on the knowledge base for this query."

    # Final sort: trusted-domain results rise to top
    scored = sorted(merged, key=lambda r: _trust_score(r.get("href", "")), reverse=True)

    parts = []
    for r in scored[:7]:
        title = r.get("title", "").strip()
        url = r.get("href", "").strip()
        body = r.get("body", "").strip()
        trust = _trust_score(url)
        badge = " [Trusted source]" if trust == 2 else (" [.lk source]" if trust == 1 else "")
        parts.append(f"**{title}**{badge}\nURL: {url}\n{body}")

    header = f'Web search results for: "{base_query}"\n\n'
    return header + "\n\n---\n\n".join(parts)
