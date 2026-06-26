"""
Auto-generate factsheets for all courses missing content in content/factsheets/.

Strategy per course:
  1. Pull course name + universities from the DB
  2. DuckDuckGo search for curriculum, duration, specializations, careers
  3. Feed to Gemini Flash with strict template prompt
  4. Save to content/factsheets/{course_number}.md

Run:
    uv run python scripts/generate_factsheets.py

Re-running is safe — skips courses that already have a factsheet file.
Use --force to regenerate even existing files.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import time
from pathlib import Path

import asyncpg
from ddgs import DDGS
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

FACTSHEETS_DIR = Path(__file__).parent.parent / "content" / "factsheets"

# Use the same model the app uses — same API key quota
GEMINI_MODEL = "models/gemini-3.1-flash-lite"

# Seconds between Gemini calls — conservative to avoid 429s
GEMINI_DELAY = 8.0

# Max retries on 429
MAX_RETRIES = 4

# Seconds between DuckDuckGo calls
DDG_DELAY = 2.0

FACTSHEET_TEMPLATE = """\
You are writing a factsheet for a degree guidance system used by Sri Lankan A/L students
choosing their university degree. The factsheet must be accurate, practical, and Sri Lanka-specific.

Write a factsheet for the following degree programme using EXACTLY this markdown structure.
Do not add or remove sections. Do not include placeholder text — every section must have real content.

---

# {course_name}
**Course Number:** {course_number}
**Degree:** [Full official degree name, e.g. "Bachelor of Science (Honours) in ..."]
**Duration:** [e.g. "3 years" or "4 years"]
**Entry Stream:** [A/L stream(s) accepted, e.g. "Physical Science, Biological Science"]
**Available at:** [List each university with its course code, e.g. "University of Kelaniya (119D)"]

---

## Overview

[2-3 paragraphs. Explain what this degree is, why it matters in Sri Lanka, what the industry
or sector looks like locally, and what makes this particular university/faculty notable.
Be specific — mention actual Sri Lankan institutions, industries, and context.]

---

## What You Will Study

[Year-by-year curriculum breakdown. Use bold headings for each year.
Include all major subject areas, specializations (if any), and final year project/research.
If there are tracks or specializations students choose between, list them clearly with what
each covers. Be specific about the academic content — not just vague subject names.]

---

## Career Paths in Sri Lanka

[Bullet points. Each bullet = one career pathway with:
- The role/sector
- Actual Sri Lankan employers or organisations in that sector
- What the day-to-day work involves
Include at least 5-6 distinct pathways. Include postgraduate study options.]

---

## Entry Requirements

[A/L stream, required subjects, any aptitude tests, language of instruction,
physical requirements if any (e.g. Nursing). Mention Z-score competitiveness
in general terms without giving specific numbers — those come from the database.]

---

## Differences Between Universities

[Only include this section if the programme is offered at more than one university.
Compare the universities on: faculty size, specializations offered, research focus,
industry links, location advantages, and any unique features.]

---

## Special Notes

[Any important details not covered above: professional body recognition (IESL, SLMC, ACCA etc.),
registration or licensing requirements after graduation, overseas employment demand,
postgraduate conversion pathways, medium of instruction, or anything else a student
making a life decision should know.]

---

Use this research context to write the factsheet:

COURSE: {course_name} (Number: {course_number})
UNIVERSITIES OFFERING IT: {universities}

WEB SEARCH RESULTS:
{web_context}

Write only the factsheet markdown. No preamble, no explanation, no sign-off.
"""


async def get_missing_courses(conn: asyncpg.Connection) -> list[dict]:
    """Return all course numbers that don't have a factsheet file yet."""
    rows = await conn.fetch(
        """
        SELECT c.course_number,
               MIN(c.name_en) as name_en,
               STRING_AGG(
                   c.name_en || ' (' || c.course_code || ') at ' ||
                   u.name_en, ' | '
                   ORDER BY c.course_code
               ) as universities
        FROM courses c
        JOIN universities u ON u.university_id = c.university_id
        WHERE c.is_active = TRUE
        GROUP BY c.course_number
        ORDER BY c.course_number::int
        """
    )
    missing = []
    for r in rows:
        path = FACTSHEETS_DIR / f"{r['course_number']}.md"
        if not path.exists():
            missing.append({
                "course_number": r["course_number"],
                "name_en": r["name_en"],
                "universities": r["universities"],
            })
    return missing


def web_search(course_name: str, universities: str) -> str:
    """DuckDuckGo search for curriculum and career info."""
    # Extract first university name for targeted search
    first_uni = universities.split(" at ")[-1].split(" | ")[0].strip()
    # Clean up the course name for search
    clean_name = course_name.split("(")[0].strip()

    queries = [
        f'"{clean_name}" degree Sri Lanka curriculum specializations duration',
        f'"{clean_name}" {first_uni} undergraduate programme',
        f'"{clean_name}" graduates Sri Lanka careers jobs',
    ]

    all_results = []
    for query in queries[:2]:  # 2 queries per course to stay under rate limits
        try:
            with DDGS(timeout=15) as ddgs:
                results = list(ddgs.text(query, max_results=5))
                for r in results:
                    snippet = f"[{r.get('title', '')}]\n{r.get('body', '')}\nURL: {r.get('href', '')}"
                    all_results.append(snippet)
            time.sleep(DDG_DELAY)
        except Exception as e:
            log.warning("DDG search failed for '%s': %s", query, e)

    if not all_results:
        return f"No web results found. Generate from general knowledge about {course_name} in Sri Lanka."

    return "\n\n---\n\n".join(all_results[:8])


def generate_factsheet(
    client: genai.Client,
    course_number: str,
    course_name: str,
    universities: str,
    web_context: str,
) -> str:
    """Call Gemini to generate the factsheet markdown. Retries on 429."""
    prompt = FACTSHEET_TEMPLATE.format(
        course_name=course_name,
        course_number=course_number,
        universities=universities,
        web_context=web_context,
    )

    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=4096,
                ),
            )
            return response.text.strip()
        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err:
                wait = 60 * (attempt + 1)  # 60s, 120s, 180s, 240s
                log.warning("  Rate limited — waiting %ds (attempt %d/%d)", wait, attempt + 1, MAX_RETRIES)
                time.sleep(wait)
            else:
                raise
    raise RuntimeError(f"Gemini failed after {MAX_RETRIES} retries")


async def main(force: bool = False) -> None:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set in .env")

    db_url = os.getenv("DATABASE_URL", "").replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(db_url)
    client = genai.Client(api_key=api_key)

    FACTSHEETS_DIR.mkdir(parents=True, exist_ok=True)

    if force:
        # Re-generate all courses
        all_rows = await conn.fetch(
            """
            SELECT c.course_number,
                   MIN(c.name_en) as name_en,
                   STRING_AGG(
                       c.name_en || ' (' || c.course_code || ') at ' ||
                       u.name_en, ' | '
                       ORDER BY c.course_code
                   ) as universities
            FROM courses c
            JOIN universities u ON u.university_id = c.university_id
            WHERE c.is_active = TRUE
            GROUP BY c.course_number
            ORDER BY c.course_number::int
            """
        )
        courses = [dict(r) for r in all_rows]
    else:
        courses = await get_missing_courses(conn)

    total = len(courses)
    if total == 0:
        log.info("All factsheets already exist. Use --force to regenerate.")
        await conn.close()
        return

    log.info("Generating %d factsheets...", total)

    success = 0
    failed = []

    for i, course in enumerate(courses, 1):
        num = course["course_number"]
        name = course["name_en"].split("(")[0].strip()  # drop uni suffix from name
        unis = course["universities"]
        path = FACTSHEETS_DIR / f"{num}.md"

        log.info("[%d/%d] %s — %s", i, total, num, name)

        try:
            # Step 1: web search
            log.info("  Searching web...")
            web_ctx = web_search(name, unis)

            # Step 2: generate with Gemini
            log.info("  Generating with Gemini...")
            content = generate_factsheet(client, num, name, unis, web_ctx)

            # Step 3: save
            path.write_text(content, encoding="utf-8")
            log.info("  Saved → %s", path.name)
            success += 1

        except Exception as e:
            log.error("  FAILED: %s", e)
            failed.append((num, name, str(e)))

        # Rate limit between Gemini calls
        if i < total:
            time.sleep(GEMINI_DELAY)

    await conn.close()

    print("\n" + "=" * 60)
    print(f"DONE — {success}/{total} factsheets generated")
    if failed:
        print(f"\nFailed ({len(failed)}):")
        for num, name, err in failed:
            print(f"  {num} {name}: {err}")
    print(f"\nFiles saved to: {FACTSHEETS_DIR}")
    print("\nNext step: run the indexer to embed new factsheets:")
    print("  uv run python -m apps.worker.jobs.index_factsheets")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate missing factsheets using Gemini + DuckDuckGo")
    parser.add_argument("--force", action="store_true", help="Regenerate even existing factsheets")
    args = parser.parse_args()
    asyncio.run(main(force=args.force))
