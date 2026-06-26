"""Check which course numbers are missing factsheets."""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()


async def main():
    url = os.getenv("DATABASE_URL").replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(url)

    total = await conn.fetchval(
        "SELECT COUNT(DISTINCT course_number) FROM courses WHERE is_active = TRUE"
    )
    indexed = await conn.fetchval(
        "SELECT COUNT(DISTINCT course_number) FROM document_sources"
    )

    missing = await conn.fetch(
        """
        SELECT c.course_number, MIN(c.name_en) as name_en,
               COUNT(DISTINCT c.course_code) as uni_count
        FROM courses c
        WHERE c.is_active = TRUE
          AND c.course_number NOT IN (SELECT DISTINCT course_number FROM document_sources)
        GROUP BY c.course_number
        ORDER BY course_number::int
        """
    )

    have = await conn.fetch(
        """
        SELECT c.course_number, MIN(c.name_en) as name_en
        FROM courses c
        WHERE c.is_active = TRUE
          AND c.course_number IN (SELECT DISTINCT course_number FROM document_sources)
        GROUP BY c.course_number
        ORDER BY course_number::int
        """
    )

    print(f"Total unique course numbers: {total}")
    print(f"Already have factsheets:     {indexed}")
    print(f"Missing factsheets:          {len(missing)}")
    print()
    print("=== HAVE factsheets ===")
    for r in have:
        print(f"  {r['course_number']} — {r['name_en']}")
    print()
    print("=== MISSING factsheets ===")
    for r in missing:
        print(f"  {r['course_number']} — {r['name_en']} ({r['uni_count']} unis)")

    await conn.close()


asyncio.run(main())
