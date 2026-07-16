"""Audit the live catalog against the handbook (Phase 9).

Why this exists — the measured case. Financial Economics (131) was offered to
all six streams. The book (2024 p.117) grants two:

    "At least a 'B' grade in Economics and at least 'S' grades for any other
     two subjects in Art Stream or Commerce Stream"

So a Biological Science student was told they were eligible for a degree the
handbook says they cannot read. And the restriction was not unknown — whoever
seeded the course WROTE it down, in the requirement's own notes field:

    "Other 2 subjects from Arts or Commerce stream."

The knowledge was there. The enforcement wasn't: a note is prose, nothing reads
it, and nothing ever compared the catalog to the book. It sat wrong for a year
and was found by luck.

This turns that comparison into a machine's job, run against every book we
ingest. It is READ-ONLY: it reports, it never edits. A disagreement is a
question for an admin ("which is right, the book or us?"), and the two
directions are not the same question at all:

  - only_in_book -> the catalog is MISSING a stream the book grants: the course
    is invisible to students who could have applied. The silent-omission bug.
  - only_in_db   -> the catalog grants a stream the book does not: students are
    shown a course they cannot actually enter. This is what 131 was.

Where the book itself is unreadable on the point (it grants entry by subject
list without naming a stream — see course_details.subject_only_alternative),
the row is marked book_may_be_incomplete so nobody "corrects" the catalog to
match a floor rather than the truth.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.ingestion.course_details import BookCourseDetail


@dataclass
class StreamDisagreement:
    """One course where the catalog and the book do not say the same thing."""

    course_number: str
    name: str | None
    book_streams: list[str]
    db_streams: list[str]
    #: granted by the book, missing from us -> invisible to those students
    only_in_book: list[str]
    #: granted by us, not by the book -> shown to students who cannot apply
    only_in_db: list[str]
    #: the book page, so a human can settle it in one look
    page_number: int | None
    #: the book grants entry by subject list too — its stream list is a floor,
    #: so do NOT trust `only_in_db` here (course_details.subject_only_alternative)
    book_may_be_incomplete: bool = False

    @property
    def severity(self) -> str:
        """Which way it hurts. 'invisible' is the one that costs a student a
        degree they could have had; 'over_granted' shows them one they can't."""
        if self.only_in_book:
            return "invisible"
        return "over_granted"


async def audit_streams(
    db: AsyncSession, details: dict[str, BookCourseDetail]
) -> list[StreamDisagreement]:
    """Compare every catalog course's streams with what this book says.

    `details` is core.ingestion.course_details.parse_course_details() output.
    Courses the book does not mention are skipped — absence here is not a claim
    (a course can be printed outside the sections we read; see book_search for
    the same conservative rule). Read-only.
    """
    rows = (
        await db.execute(
            text(
                "SELECT c.course_number, min(c.name_en) AS name_en, "
                "  (SELECT string_agg(DISTINCT s.code, ',') "
                "     FROM course_stream_eligibility cse "
                "     JOIN streams s   ON s.stream_id = cse.stream_id "
                "     JOIN courses c2  ON c2.course_code = cse.course_code "
                "    WHERE c2.course_number = c.course_number) AS streams "
                "FROM courses c "
                "WHERE c.course_number IS NOT NULL AND c.is_active = TRUE "
                "GROUP BY c.course_number ORDER BY c.course_number"
            )
        )
    ).all()

    out: list[StreamDisagreement] = []
    for r in rows:
        detail = details.get(r.course_number)
        if detail is None or not detail.stream_codes:
            continue  # the book says nothing about it — not a disagreement
        db_streams = sorted({s for s in (r.streams or "").split(",") if s})
        if not db_streams:
            continue  # zero-stream courses are the onboarding panel's job
        book_streams = sorted(detail.stream_codes)
        if book_streams == db_streams:
            continue
        out.append(
            StreamDisagreement(
                course_number=r.course_number,
                name=r.name_en,
                book_streams=book_streams,
                db_streams=db_streams,
                only_in_book=sorted(set(book_streams) - set(db_streams)),
                only_in_db=sorted(set(db_streams) - set(book_streams)),
                page_number=detail.page_number,
                book_may_be_incomplete=detail.streams_may_be_incomplete,
            )
        )
    return out
