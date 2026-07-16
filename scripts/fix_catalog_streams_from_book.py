"""Correct catalog stream eligibility to match the handbook (Phase 9).

The bug this fixes, measured: Financial Economics (131) was offered to all six
streams. The 2024 book, p.117, grants two:

    "At least a 'B' grade in Economics and at least 'S' grades for any other
     two subjects in Art Stream or Commerce Stream"

So a Biological Science student was told they were eligible for a degree the
handbook says they cannot read — and if they trusted us and listed it in their
UGC application, they spent a slot on something they could never be selected
for. The restriction was not unknown: whoever seeded the course wrote it into
the requirement's notes ("Other 2 subjects from Arts or Commerce stream"). A
note is prose. Nothing read it. It sat wrong for a year.

The book is the source of truth, so this reads the book and makes the catalog
agree with it. It is NOT a one-off for 131 — it fixes every course the book
contradicts, which is the only version worth having when a new book lands every
year.

Safety, in order of how much they matter:

- DRY RUN by default. Nothing is written without --apply.
- Courses the book cannot state are SKIPPED, never touched. Where the book also
  grants entry through a subject list without naming a stream (see
  course_details.subject_only_alternative — Indigenous Pharmaceutical
  Technology/124 is the measured case), what we can read is a FLOOR, not the
  truth. "Correcting" the catalog down to a floor would hide a course from
  students who genuinely qualify: the exact bug, in a nicer costume.
- Every change is printed before/after, with its book page, so a human can
  check it against the PDF.
- One transaction: it all lands or none of it does.
- Idempotent — running it twice changes nothing the second time.

Usage (the credential is yours; it never lives in the repo):

    PROD_DATABASE_URL='postgresql://...supabase...' \\
        uv run python scripts/fix_catalog_streams_from_book.py data/raw_handbooks/handbook_2024.pdf

    # then, once the report reads correctly:
    PROD_DATABASE_URL='postgresql://...' \\
        uv run python scripts/fix_catalog_streams_from_book.py data/raw_handbooks/handbook_2024.pdf --apply
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncpg  # noqa: E402

from core.ingestion.course_details import parse_course_details  # noqa: E402


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
    book = parse_course_details(args.pdf)
    print(f"  the book documents {len(book)} courses\n")

    # Supabase requires TLS; a local dev postgres has none — so the same script
    # can be rehearsed against dev before it is ever pointed at students' data.
    is_local = "localhost" in url or "127.0.0.1" in url
    print(f"Target: {'LOCAL dev database' if is_local else 'REMOTE (production)'}")
    conn = await asyncpg.connect(url, ssl=None if is_local else "require")
    try:
        stream_ids = {r["code"]: r["stream_id"] for r in await conn.fetch("SELECT stream_id, code FROM streams")}
        rows = await conn.fetch(
            """
            SELECT c.course_number,
                   min(c.name_en)                       AS name_en,
                   array_agg(DISTINCT c.course_code)    AS course_codes,
                   (SELECT array_agg(DISTINCT s.code)
                      FROM course_stream_eligibility cse
                      JOIN streams s  ON s.stream_id = cse.stream_id
                      JOIN courses c2 ON c2.course_code = cse.course_code
                     WHERE c2.course_number = c.course_number) AS streams
              FROM courses c
             WHERE c.is_active AND c.course_number IS NOT NULL
             GROUP BY c.course_number ORDER BY c.course_number
            """
        )

        planned: list[tuple] = []
        skipped: list[tuple] = []
        for r in rows:
            detail = book.get(r["course_number"])
            if detail is None or not detail.stream_codes:
                continue  # the book says nothing — silence is not a claim
            db_streams = sorted(set(r["streams"] or []))
            if not db_streams:
                continue  # zero-stream courses are the onboarding panel's job
            book_streams = sorted(detail.stream_codes)
            if book_streams == db_streams:
                continue
            entry = (r, db_streams, book_streams, detail)
            (skipped if detail.streams_may_be_incomplete else planned).append(entry)

        for r, db_s, book_s, d in skipped:
            print(f"SKIP {r['course_number']}  {str(r['name_en'])[:44]}   (book p{d.page_number})")
            print(f"     we serve {db_s}")
            print(f"     book reads {book_s} — but it also admits by subject list, so that is a")
            print("     FLOOR. We are probably right; a human must settle this one.\n")

        if not planned:
            print("Nothing to correct: the catalog agrees with this book.")
            return 0

        for r, db_s, book_s, d in planned:
            add = sorted(set(book_s) - set(db_s))
            rm = sorted(set(db_s) - set(book_s))
            print(f"FIX  {r['course_number']}  {str(r['name_en'])[:44]}   (book p{d.page_number})")
            print(f"     before: {db_s}")
            print(f"     after : {book_s}")
            if rm:
                print(f"     REMOVE {rm}  -> those students are currently shown a course they cannot enter")
            if add:
                print(f"     ADD    {add}  -> those students currently cannot see a course they may enter")
            print()

        if not args.apply:
            print(f"DRY RUN — {len(planned)} course(s) would change, {len(skipped)} skipped.")
            print("Re-run with --apply to write them.")
            return 0

        async with conn.transaction():
            for r, _db_s, book_s, _d in planned:
                codes = list(r["course_codes"])
                await conn.execute(
                    "DELETE FROM course_stream_eligibility "
                    "WHERE course_code = ANY($1::varchar[]) AND stream_id <> ALL($2::int[])",
                    codes,
                    [stream_ids[s] for s in book_s],
                )
                for code in codes:
                    for s in book_s:
                        await conn.execute(
                            "INSERT INTO course_stream_eligibility (course_code, stream_id) "
                            "VALUES ($1, $2) ON CONFLICT DO NOTHING",
                            code,
                            stream_ids[s],
                        )

        # verify from the DB, not from what we intended to write
        print("Verifying …")
        ok = True
        for r, _db_s, book_s, _d in planned:
            after = sorted(
                x["code"]
                for x in await conn.fetch(
                    "SELECT DISTINCT s.code FROM course_stream_eligibility cse "
                    "JOIN streams s  ON s.stream_id = cse.stream_id "
                    "JOIN courses c2 ON c2.course_code = cse.course_code "
                    "WHERE c2.course_number = $1",
                    r["course_number"],
                )
            )
            mark = "OK " if after == book_s else "BAD"
            ok &= after == book_s
            print(f"  {mark} {r['course_number']}: {after}")
        print("\nDone." if ok else "\nFAILED: a course did not land as intended.")
        return 0 if ok else 1
    finally:
        await conn.close()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
