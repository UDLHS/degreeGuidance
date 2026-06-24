"""Tool implementations called by the Gemini agentic loop.

Three tools:
  search_knowledge  — RAG search across all 50 factsheets
  lookup_course     — full factsheet + recent cutoffs for one course number
  get_cutoff_trend  — year-by-year Z-score history for a course-university code
"""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from google import genai

from core.rag.retrieval import retrieve


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
