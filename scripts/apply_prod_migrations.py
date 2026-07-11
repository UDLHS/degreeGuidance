"""Apply pending schema migrations (36→41) to the PRODUCTION Supabase DB.

W2 of docs/PHASE2_STUDENT_ADMIN_PLAN.md, using the project's established
standalone-script method (Alembic-direct has SSL friction against Supabase;
see the prod-migrations notes): each step is a pre-generated, human-reviewed
SQL file from `alembic upgrade <prev>:<rev> --sql` in scripts/prod_sql/. Every
file is BEGIN/COMMIT-wrapped and its alembic_version UPDATE is guarded with
`WHERE version_num = '<prev>'`, so a file can only apply on top of the exact
expected state — and the version row is UPDATEd, never INSERTed.

Usage (from the project root):
    PROD_DATABASE_URL='postgresql://...supabase...' \
        python -m scripts.apply_prod_migrations --dry-run   # show the plan
    PROD_DATABASE_URL='postgresql://...supabase...' \
        python -m scripts.apply_prod_migrations              # apply pending

Safety rails: refuses localhost URLs (that's the dev DB — use alembic there),
verifies the version row advanced after every step, and stops at the first
mismatch.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

import asyncpg

SQL_DIR = Path(__file__).resolve().parent / "prod_sql"

# (revision, expected predecessor, sql file) — chain order matters.
CHAIN: list[tuple[str, str, str]] = [
    ("a7b8c9d0e1f2", "f4a5b6c7d8e9", "36_a7b8c9d0e1f2_extraction_columns.sql"),
    ("eb424f912bbe", "a7b8c9d0e1f2", "37_eb424f912bbe_stream_overrides.sql"),
    ("2cd4dc5ac4d2", "eb424f912bbe", "38_2cd4dc5ac4d2_unmapped_cutoffs.sql"),
    ("985e13967bd9", "2cd4dc5ac4d2", "39_985e13967bd9_conversation_flagged.sql"),
    ("093c47d4fb58", "985e13967bd9", "40_093c47d4fb58_agent_configs.sql"),
    ("e75434db887c", "093c47d4fb58", "41_e75434db887c_factsheets.sql"),
]


async def main(dry_run: bool) -> int:
    url = os.environ.get("PROD_DATABASE_URL", "").strip()
    if not url:
        print("ERROR: set PROD_DATABASE_URL (the Supabase connection string).")
        return 2
    if "localhost" in url or "127.0.0.1" in url:
        print("ERROR: PROD_DATABASE_URL points at localhost — use `alembic upgrade head` for dev.")
        return 2
    url = url.replace("postgresql+asyncpg://", "postgresql://")

    conn = await asyncpg.connect(url)
    try:
        current = await conn.fetchval("SELECT version_num FROM alembic_version")
        print(f"prod alembic_version: {current}")

        revisions = [rev for rev, _, _ in CHAIN]
        if current == revisions[-1]:
            print("Already at head (e75434db887c) — nothing to do.")
            return 0

        # find where we are in the chain
        if current in revisions:
            start = revisions.index(current) + 1
        elif current == CHAIN[0][1]:  # pre-36
            start = 0
        else:
            print(
                f"ERROR: unexpected prod version {current!r} — not in the 35→41 chain. "
                "Investigate before applying anything."
            )
            return 2

        pending = CHAIN[start:]
        print(f"pending steps ({len(pending)}):")
        for rev, prev, fname in pending:
            print(f"  {prev} -> {rev}   ({fname})")
        if dry_run:
            print("\n--dry-run: nothing applied.")
            return 0

        for rev, prev, fname in pending:
            sql = (SQL_DIR / fname).read_text(encoding="utf-8")
            print(f"\napplying {fname} …")
            await conn.execute(sql)
            now = await conn.fetchval("SELECT version_num FROM alembic_version")
            if now != rev:
                print(f"ERROR: version is {now!r} after {fname}, expected {rev!r}. STOPPING.")
                return 1
            print(f"  OK — prod now at {rev}")

        # closing sanity: the new tables exist
        for tbl in (
            "extraction_columns",
            "course_stream_cutoff_overrides",
            "unmapped_cutoffs",
            "agent_configs",
            "factsheets",
        ):
            n = await conn.fetchval(
                "SELECT count(*) FROM information_schema.tables WHERE table_name = $1", tbl
            )
            print(f"  table {tbl}: {'present' if n else 'MISSING!'}")
        seeded = await conn.fetchval("SELECT count(*) FROM factsheets")
        print(f"  factsheets seeded: {seeded}")
        print("\nDone.")
        return 0
    finally:
        await conn.close()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    sys.exit(asyncio.run(main(p.parse_args().dry_run)))
