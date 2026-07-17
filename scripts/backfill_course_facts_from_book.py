"""Backfill duration, mediums and aptitude flags from the handbook (Phase 9.6).

The book prints, for every course of study, its Duration and Medium — and, in
one definitive table, exactly which Uni-Codes require a practical/aptitude
test. None of that was ever read: duration_years is NULL and course_mediums is
EMPTY across the whole catalog, and the aptitude flags were hand-seeded. This
reads the book and fills the gaps.

What it does, and refuses to do:

- **duration_years** — filled per course NUMBER where currently NULL. A
  non-NULL value is never overwritten; if the book disagrees with an existing
  value it is REPORTED for a human, not "corrected".
- **course_mediums** — filled per course CODE, only where the course currently
  has NO medium rows, and only when the book's Medium field parsed to
  unambiguous language names ("English", "Sinhala / English"). A
  per-institution medium (Siddha/036: Jaffna-Tamil, Trincomalee-English) is
  REPORTED verbatim with its page — a human assigns those per Uni-Code.
- **requires_aptitude_test** — compared per CODE against the book's own test
  table. Disagreements are reported; --apply aligns the catalog to the book
  (the table is definitive and the flag drives the student-facing conditional
  badge). If the table cannot be read, nothing is compared and nothing changes.

Safety: DRY RUN by default; one transaction; idempotent; every change printed
with its book page. Same credential rule as fix_catalog_streams_from_book.py —
PROD_DATABASE_URL is yours and never lives in the repo. Rehearse on dev first:

    PROD_DATABASE_URL='postgresql://…local…' \\
        uv run python scripts/backfill_course_facts_from_book.py data/raw_handbooks/handbook_2024.pdf

    # then, once the report reads correctly:
    PROD_DATABASE_URL='postgresql://…' \\
        uv run python scripts/backfill_course_facts_from_book.py data/raw_handbooks/handbook_2024.pdf --apply
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncpg  # noqa: E402

from core.ingestion.aptitude_section import parse_aptitude_codes  # noqa: E402
from core.ingestion.course_details import parse_section_22  # noqa: E402
from core.ingestion.pdf_pages import iter_pages_chunked  # noqa: E402


async def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf", help="handbook PDF to read the truth from")
    ap.add_argument("--apply", action="store_true", help="write the changes (default: dry run)")
    args = ap.parse_args()

    url = os.environ.get("PROD_DATABASE_URL", "").strip()
    if not url:
        print("ERROR: set PROD_DATABASE_URL (the Supabase connection string).")
        return 2
    url = url.replace("postgresql+asyncpg://", "postgresql://")
    if not Path(args.pdf).exists():
        print(f"ERROR: no such handbook: {args.pdf}")
        return 2

    print(f"Reading {args.pdf} …")
    pages = [(pno, page.extract_text() or "") for pno, page in iter_pages_chunked(args.pdf)]
    book = parse_section_22(pages)
    apt_codes, apt_page, apt_warnings = parse_aptitude_codes(pages)
    print(f"  the book documents {len(book)} courses; aptitude table: "
          f"{len(apt_codes)} codes on p.{apt_page}")
    for w in apt_warnings:
        print(f"  WARNING: {w}")
    print()

    is_local = "localhost" in url or "127.0.0.1" in url
    print(f"Target: {'LOCAL dev database' if is_local else 'REMOTE (production)'}")
    conn = await asyncpg.connect(url, ssl=None if is_local else "require")
    try:
        medium_ids = {
            r["code"]: r["medium_id"] for r in await conn.fetch("SELECT medium_id, code FROM mediums")
        }
        rows = await conn.fetch(
            """
            SELECT c.course_code, c.course_number, c.name_en, c.duration_years,
                   c.requires_aptitude_test,
                   EXISTS (SELECT 1 FROM course_mediums m
                            WHERE m.course_code = c.course_code) AS has_mediums
              FROM courses c
             WHERE c.is_active AND c.course_number IS NOT NULL
             ORDER BY c.course_code
            """
        )

        dur_fills: list[tuple] = []      # (code, name, years, page)
        dur_conflicts: list[tuple] = []  # (code, name, db_years, book_years, page)
        med_fills: list[tuple] = []      # (code, name, codes, page)
        med_review: list[tuple] = []     # (number, name, verbatim, page)
        apt_changes: list[tuple] = []    # (code, name, db_flag, book_flag)
        seen_review_numbers: set[str] = set()

        for r in rows:
            d = book.get(r["course_number"])
            if d is not None:
                if d.duration_years is not None:
                    if r["duration_years"] is None:
                        dur_fills.append(
                            (r["course_code"], r["name_en"], d.duration_years, d.page_number)
                        )
                    elif float(r["duration_years"]) != d.duration_years:
                        dur_conflicts.append(
                            (r["course_code"], r["name_en"], float(r["duration_years"]),
                             d.duration_years, d.page_number)
                        )
                if d.medium_text:
                    if d.medium_needs_review:
                        if r["course_number"] not in seen_review_numbers:
                            seen_review_numbers.add(r["course_number"])
                            med_review.append(
                                (r["course_number"], r["name_en"], d.medium_text, d.page_number)
                            )
                    elif d.medium_codes and not r["has_mediums"]:
                        med_fills.append(
                            (r["course_code"], r["name_en"], d.medium_codes, d.page_number)
                        )
            if apt_codes:  # empty = table unreadable = compare nothing
                book_flag = r["course_code"] in set(apt_codes)
                if book_flag != bool(r["requires_aptitude_test"]):
                    apt_changes.append(
                        (r["course_code"], r["name_en"], bool(r["requires_aptitude_test"]),
                         book_flag)
                    )

        print(f"duration: {len(dur_fills)} to fill (currently NULL), "
              f"{len(dur_conflicts)} conflict(s) reported, never overwritten")
        for code, name, years, page in dur_fills:
            print(f"  FILL {code}  {str(name)[:44]:44s} -> {years:g} years  (book p.{page})")
        for code, name, db_y, book_y, page in dur_conflicts:
            print(f"  CONFLICT {code}  {str(name)[:40]:40s} we say {db_y:g}, "
                  f"book p.{page} says {book_y:g} — decide by reading the page")

        print(f"\nmediums: {len(med_fills)} course(s) to fill (currently none), "
              f"{len(med_review)} flagged for a human")
        for code, name, codes, page in med_fills:
            print(f"  FILL {code}  {str(name)[:44]:44s} -> {','.join(codes)}  (book p.{page})")
        for num, name, verbatim, page in med_review:
            print(f"  REVIEW {num}  {str(name)[:42]:42s} (book p.{page}) — per-institution:")
            for line in verbatim.splitlines():
                print(f"         {line}")

        print(f"\naptitude: {len(apt_changes)} flag(s) disagree with the book's table"
              + (f" (p.{apt_page})" if apt_page else ""))
        for code, name, db_f, book_f in apt_changes:
            print(f"  {'SET' if book_f else 'CLEAR'} {code}  {str(name)[:42]:42s} "
                  f"we say {db_f}, book says {book_f}")

        total = len(dur_fills) + len(med_fills) + len(apt_changes)
        if not args.apply:
            print(f"\nDRY RUN — {total} change(s) planned, nothing written. "
                  "Re-run with --apply to write them.")
            return 0
        if total == 0:
            print("\nNothing to write.")
            return 0

        async with conn.transaction():
            for code, _n, years, _p in dur_fills:
                await conn.execute(
                    "UPDATE courses SET duration_years = $1, updated_at = now() "
                    "WHERE course_code = $2 AND duration_years IS NULL",
                    years, code,
                )
            for code, _n, codes, _p in med_fills:
                for mc in codes:
                    await conn.execute(
                        "INSERT INTO course_mediums (course_code, medium_id) "
                        "VALUES ($1, $2) ON CONFLICT DO NOTHING",
                        code, medium_ids[mc],
                    )
            for code, _n, _db, book_f in apt_changes:
                await conn.execute(
                    "UPDATE courses SET requires_aptitude_test = $1, updated_at = now() "
                    "WHERE course_code = $2",
                    book_f, code,
                )

        # verify after write, inside the same connection
        n_dur = await conn.fetchval(
            "SELECT count(*) FROM courses WHERE is_active AND duration_years IS NOT NULL"
        )
        n_med = await conn.fetchval("SELECT count(DISTINCT course_code) FROM course_mediums")
        print(f"\nAPPLIED {total} change(s). Now: {n_dur} active courses with a duration, "
              f"{n_med} with medium rows.")
        return 0
    finally:
        await conn.close()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
