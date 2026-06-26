"""Check what the agent actually gets when it calls lookup_course for ECS (119)."""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()


async def main():
    url = os.getenv("DATABASE_URL").replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(url)

    # What lookup_course returns for 119
    chunks = await conn.fetch(
        """
        SELECT c.heading, LEFT(c.content, 100) as preview
        FROM chunks c
        JOIN document_sources d ON d.source_id = c.source_id
        WHERE d.course_number = '119'
        ORDER BY c.chunk_index
        """
    )

    cutoffs = await conn.fetch(
        """
        SELECT cu.course_code, d.name_en as district, cu.z_score
        FROM z_score_cutoffs cu
        JOIN districts d ON d.district_id = cu.district_id
        WHERE cu.course_code LIKE '119%'
          AND cu.year = (SELECT MAX(year) FROM z_score_cutoffs)
          AND cu.z_score IS NOT NULL
        LIMIT 5
        """
    )

    # Also check a course WITH a factsheet for comparison
    chunks_008 = await conn.fetch(
        """
        SELECT c.heading, LEFT(c.content, 100) as preview
        FROM chunks c
        JOIN document_sources d ON d.source_id = c.source_id
        WHERE d.course_number = '008'
        ORDER BY c.chunk_index
        LIMIT 6
        """
    )

    print("=== lookup_course('119') — ECS at Kelaniya ===")
    print(f"Factsheet chunks found: {len(chunks)}")
    if chunks:
        for r in chunks:
            print(f"  [{r['heading']}] {r['preview']}...")
    else:
        print("  !! NO FACTSHEET — agent only gets cutoffs, nothing about")
        print("     duration, specializations, curriculum, career paths")

    print()
    print("Cutoffs returned:")
    for r in cutoffs:
        print(f"  {r['course_code']} {r['district']}: {float(r['z_score']):.4f}")

    print()
    print("=== lookup_course('008') — Engineering (HAS factsheet) ===")
    print(f"Factsheet chunks found: {len(chunks_008)} (showing 6)")
    for r in chunks_008:
        print(f"  [{r['heading']}] {r['preview']}...")

    await conn.close()


asyncio.run(main())
