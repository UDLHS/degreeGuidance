"""Parser for the handbook's Section 2.2 — what the book itself says about each
course of study (Phase 9.1).

Why this exists: a new course used to arrive at the admin's review gate as a
bare Uni-Code with nothing but a cutoff number. Everything needed to onboard it
is already printed in the book; nothing read it. This does.

Measured structure (2024 book, pp.39-100; same shape in 2023/2025):

    2.2.1 ARTS STREAM                 <- section banner sets the stream context
    2. Course of Study in Arts offered by the Sabaragamuwa University ... -Arts (SAB)
    (Course Code - 021)               <- the anchor: 79 in the 2024 book, all unique
    (Proposed Intake - 350)
    Students who have satisfied the minimum requirements for admission in Arts
    Stream or Commerce Stream are eligible to seek admission for this programme.
    ...prerequisite prose...

Sections: 2.2.1 ARTS · 2.2.2 COMMERCE · 2.2.3 BIOLOGICAL SCIENCE ·
2.2.4 PHYSICAL SCIENCE · 2.2.5 ENGINEERING TECHNOLOGY ·
2.2.6 BIOSYSTEMS TECHNOLOGY · 2.2.7 Information Communication Technology
(a SUBJECT, not a stream) · 2.2.8 courses open to several streams.

The book states its own law on p.28: A/L subjects "are classified into six (06)
main streams" — Arts, Commerce, Biological Science, Physical Science,
Engineering Technology, Biosystems Technology. ICT is NOT one of them, so this
never emits ICT as a stream.

What is READ vs what is SUGGESTED — the distinction that matters:

- A course under 2.2.1-2.2.6 takes that section's stream. The book placed it
  there; that is a statement, not a guess.
- A course under 2.2.8 is cross-stream, and the book names the streams in
  PROSE ("...admission in Arts Stream or Commerce Stream..."). Prose is not a
  grammar (MASTERPLAN_v4 §66 measured five distinct shapes and deferred
  parsing it), so those streams are only ever SUGGESTED — and an unrecognised
  block yields an empty list so a human decides. Same rule as
  core.ingestion.stream_tags: suggest, never silently apply.

The prerequisite prose is carried through VERBATIM for the admin to read and a
summariser to use downstream. It is never parsed into eligibility rules here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from core.ingestion.pdf_pages import iter_pages_chunked

#: Stream name as PRINTED -> our stream code. Ordered longest-first so
#: "Biosystems Technology" never matches as bare "Technology".
#:
#: Deliberately keyed on the printed WORDS, never on a section number: the
#: stream of a section is read from its own banner ("2.2.4 PHYSICAL SCIENCE
#: STREAM" -> PHYSICAL_SCIENCE). A future book that renumbers or reorders its
#: sections therefore still reads correctly, instead of silently relabelling
#: every course — which a number->stream table would have done. ICT is absent
#: on purpose: the book classifies it as a subject (§2.2.7), not a stream, so
#: an ICT banner resolves to no stream rather than a wrong one.
#: The book is not consistent about plurals — measured in the 2024 book:
#: "Art Stream or Commerce Stream" (131) and "Biosystem Technology Stream"
#: (121) sit next to "Arts Stream" and "Biosystems Technology" elsewhere.
#: Requiring the plural silently lost a stream on those courses, so every
#: name here tolerates both forms.
_STREAM_NAMES: list[tuple[str, str]] = [
    (r"BIOSYSTEMS?\s+TECHNOLOGY", "BIOSYSTEMS_TECH"),
    (r"ENGINEERING\s+TECHNOLOGY", "ENGINEERING_TECH"),
    (r"BIOLOGICAL\s+SCIENCE", "BIO_SCIENCE"),
    (r"PHYSICAL\s+SCIENCE", "PHYSICAL_SCIENCE"),
    (r"COMMERCE", "COMMERCE"),
    (r"ARTS?", "ARTS"),
]
_STREAM_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(rf"\b{p}\b", re.I), c) for p, c in _STREAM_NAMES
]
#: In PROSE the same words are also A/L SUBJECT names ("Engineering Technology"
#: and "Biosystems Technology" are subjects, and every block lists its
#: subjects), so a bare mention proves nothing. Only "<name> Stream" is the
#: book stating eligibility. Measured: without this, Urban Informatics/030 read
#: as Biosystems+Engineering off its subject list, when the truth is all six.
#:
#: The book also shares ONE trailing "Streams" across a LIST — "the Commerce,
#: Biological Science and Physical Science Streams" (092). Matching each name
#: against an adjacent "Stream" silently kept only the last, so the whole list
#: is matched at once and every name in it counts.
_NAME_ALT = "|".join(p for p, _ in _STREAM_NAMES)
_PROSE_STREAM_LIST_RE = re.compile(
    rf"((?:{_NAME_ALT})(?:\s*(?:,|and|or|/)\s*(?:{_NAME_ALT}))*)\s+STREAMS?\b",
    re.I,
)

#: The six streams the book names on p.28. A §2.1(8)/§2.2.8 course is open to
#: "students from different subject streams", i.e. all six — its SUBJECT
#: requirements do the filtering, not its stream list. This is the handbook's
#: established cross-stream convention, already encoded in
#: core.ingestion.stream_tags (migration 16) and matching how the catalog
#: hand-seeded these courses (Architecture, Quantity Surveying, IT: all six).
ALL_SIX_STREAMS: list[str] = sorted(c for _p, c in _STREAM_NAMES)

#: The book heads a course two ways: a numbered line ("2. Course of Study in
#: Arts ... -Arts (SAB)") or a numbered SUB-SECTION ("2.2.1.1 Arts"). Only a
#: bare "2.2.N <NAME> STREAM" line is a section banner; the rest name a course.
_SECTION_RE = re.compile(r"^\s*(2\.2\.[1-8])(\.\d+)?\s+(.*?)\s*$")
_NUMBERED_TITLE_RE = re.compile(r"^\s*\d{1,3}\.\s+(\S.*?)\s*$")
_COURSE_CODE_RE = re.compile(r"\(\s*Course\s*Code\s*[-–]\s*([0-9]{2,3})\s*\)", re.I)
_INTAKE_RE = re.compile(r"\(\s*Proposed\s*Intake\s*[-–]\s*([0-9,]+)\s*\)", re.I)
#: page furniture repeated on every page — noise inside a captured block
_FOOTER_RE = re.compile(r"^\s*ACADEMIC YEAR .*$|^.*UNIVERSITY GRANTS COMMISSION.*$", re.M | re.I)


@dataclass
class BookCourseDetail:
    """What the book says about one course, keyed by its 3-digit course number."""

    course_number: str
    name: str | None = None
    #: streams the book states (2.2.1-2.2.6) or, for a 2.2.8 block, suggests
    stream_codes: list[str] = field(default_factory=list)
    #: False when stream_codes came from prose and still need a human
    streams_are_stated: bool = False
    proposed_intake: int | None = None
    #: §2.2 prerequisite prose, verbatim — never parsed into rules here
    requirements_text: str = ""
    #: the page the block starts on — provenance, so the admin can check the PDF
    page_number: int | None = None
    #: True when the book listed it under §2.2.8 (open to several streams)
    cross_stream: bool = False
    #: True when the book ALSO grants entry through an "or" clause that names no
    #: stream, only subjects — so stream_codes is knowably INCOMPLETE and a
    #: human must widen it. Never silently trusted: see subject_only_alternative.
    streams_may_be_incomplete: bool = False


def streams_named_in(text: str) -> list[str]:
    """Stream names printed in `text` -> stream codes, in book order."""
    out: list[str] = []
    for pattern, code in _STREAM_PATTERNS:
        if pattern.search(text) and code not in out:
            out.append(code)
    return sorted(out)


def stream_of_banner(banner: str) -> str | None:
    """A §2.2 section banner -> the single stream it heads, or None.

    None means "this section is not one stream": the ICT section (a subject)
    and the cross-stream section both land here, and their courses fall back to
    the prose suggestion. Read from the printed banner, so renumbering a
    section cannot silently change what it means.
    """
    named = streams_named_in(banner)
    return named[0] if len(named) == 1 else None


#: The book puts a bare "or" on its own line between alternative entry routes.
_ALT_CLAUSE_RE = re.compile(r"^\s*or\s*$", re.I | re.M)


def _eligibility_window(text: str) -> str:
    """The requirement sentence(s) only — before the degree/university blurb."""
    return re.split(r"(?i)\bDegree\s+Programmes?\b|\bAvailable\s+Universit", text)[0]


def subject_only_alternative(text: str) -> bool:
    """True when the book grants entry through an "or" route that names NO
    stream — only subjects.

    Indigenous Pharmaceutical Technology/124 is the measured case:

        ...any three subjects in Engineering Technology Stream or Biosystem
        Technology Stream ...
        or
        ...any three of the following list of subjects ...
          Chemistry / Physics / Biology / Agricultural Science

    Those subjects are Bio-Science and Physical-Science subjects, so real
    students from those streams qualify — but the book never says so, and no
    parser can read what isn't written. Reporting only the named streams would
    UNDER-grant, and an under-granted course is invisible to students who could
    have applied: the exact failure this whole gate exists to stop.

    So we do not guess and we do not stay quiet — we raise a hand. Only fires
    when SOME route names a stream and another does not; when no route names
    one, the all-six default already covers everybody.
    """
    parts = [p for p in _ALT_CLAUSE_RE.split(_eligibility_window(text)) if p.strip()]
    if len(parts) < 2:
        return False
    named = [bool(_PROSE_STREAM_LIST_RE.search(p)) for p in parts]
    return any(named) and not all(named)


def cross_stream_eligibility(text: str) -> list[str]:
    """Streams for a course the book files under "different subject streams".

    The book states these two ways, and neither is a guess:

    - it names streams explicitly ("...admission in Arts Stream or Commerce
      Stream...") -> exactly those (Management & IT/027 -> Bio + Physical,
      matching the catalog);
    - it names none, and defines the course purely by SUBJECT requirements
      ("three passes including a 'C' in Combined Mathematics ...") -> then the
      section heading itself is the statement: students from different subject
      streams are eligible, i.e. all six. The subject rules do the filtering
      downstream (core/eligibility/subject_requirements.py), which is exactly
      how Architecture/Quantity Surveying/IT are seeded today.
    """
    named: list[str] = []
    for m in _PROSE_STREAM_LIST_RE.finditer(text):
        for code in streams_named_in(m.group(1)):
            if code not in named:
                named.append(code)
    return sorted(named) if named else list(ALL_SIX_STREAMS)


def parse_section_22(pages: list[tuple[int, str]]) -> dict[str, BookCourseDetail]:
    """§2.2 -> {course_number: BookCourseDetail}.

    A block runs from its "(Course Code - NNN)" anchor to the next anchor or
    section banner. The course NAME is the numbered title line immediately
    above the anchor.
    """
    out: dict[str, BookCourseDetail] = {}
    in_section = False
    section_stream: str | None = None
    last_title: str | None = None
    current: BookCourseDetail | None = None
    buf: list[str] = []

    def _flush() -> None:
        nonlocal current, buf
        if current is not None:
            current.requirements_text = _FOOTER_RE.sub("", "\n".join(buf)).strip()
            if not current.streams_are_stated:
                current.stream_codes = cross_stream_eligibility(current.requirements_text)
                # The book granted entry by subjects alone somewhere in here:
                # what we read is a floor, not the whole truth. Say so.
                current.streams_may_be_incomplete = subject_only_alternative(
                    current.requirements_text
                )
            prev = out.get(current.course_number)
            if prev is None:
                out[current.course_number] = current
            else:
                # A course open to several streams is PRINTED ONCE PER STREAM
                # SECTION, each with its own "(Course Code - NNN)" block and its
                # own subject rules (Biomedical Technology/123 appears under both
                # Engineering Technology and Biosystems Technology). Union them:
                # letting the last block win would silently drop half the
                # streams — i.e. half the students who may apply.
                for s in current.stream_codes:
                    if s not in prev.stream_codes:
                        prev.stream_codes.append(s)
                prev.stream_codes.sort()
                prev.streams_are_stated = prev.streams_are_stated or current.streams_are_stated
                prev.cross_stream = prev.cross_stream or current.cross_stream
                prev.streams_may_be_incomplete = (
                    prev.streams_may_be_incomplete or current.streams_may_be_incomplete
                )
                prev.name = prev.name or current.name
                if current.requirements_text:
                    # keep every section's rules — they differ per stream
                    prev.requirements_text = (
                        f"{prev.requirements_text}\n\n{current.requirements_text}".strip()
                    )
                if prev.proposed_intake is None:
                    prev.proposed_intake = current.proposed_intake
        current, buf = None, []

    for pno, text in pages:
        for line in text.splitlines():
            sec = _SECTION_RE.match(line)
            if sec:
                _flush()
                in_section = True
                title = (sec.group(3) or "").strip()
                if sec.group(2):
                    # "2.2.1.1 Arts" — a numbered sub-section naming a course.
                    last_title = title or None
                else:
                    # "2.2.4 PHYSICAL SCIENCE STREAM" — a section banner: it
                    # sets the stream context and names no course. Depth, not
                    # wording, decides which this is: the cross-stream banner
                    # ends in "STREAMS" (plural) and matching on words let its
                    # courses silently inherit the previous section's stream.
                    section_stream = stream_of_banner(title)
                    last_title = None
                continue

            code = _COURSE_CODE_RE.search(line)
            if code and in_section:
                _flush()
                current = BookCourseDetail(
                    course_number=code.group(1).zfill(3),
                    name=last_title,
                    page_number=pno,
                    cross_stream=(section_stream is None),
                    streams_are_stated=(section_stream is not None),
                    stream_codes=[section_stream] if section_stream else [],
                )
                last_title = None
                continue

            if current is not None:
                intake = _INTAKE_RE.search(line)
                if intake:
                    try:
                        current.proposed_intake = int(intake.group(1).replace(",", ""))
                    except ValueError:
                        pass
                    continue
                buf.append(line)

            title = _NUMBERED_TITLE_RE.match(line)
            if title:
                # remember it: if the next anchor follows, this is its name
                last_title = title.group(1)

    _flush()
    return out


def details_from_artifact(payload: dict | None) -> dict[str, BookCourseDetail]:
    """Rehydrate parse_course_details() output from its stored artifact.

    The extraction job persists this as `course_details.json` (dataclasses.asdict);
    readers get objects back rather than hand-indexing dicts. Unknown keys are
    dropped, so an artifact written by an older build still loads instead of
    exploding a run — a missing field just means the book said nothing.
    """
    fields = BookCourseDetail.__dataclass_fields__
    out: dict[str, BookCourseDetail] = {}
    for num, raw in (payload or {}).items():
        if not isinstance(raw, dict):
            continue
        kwargs = {k: v for k, v in raw.items() if k in fields}
        kwargs.setdefault("course_number", num)
        out[num] = BookCourseDetail(**kwargs)
    return out


def parse_course_details(pdf_path: str) -> dict[str, BookCourseDetail]:
    """Read Section 2.2 of the handbook: {course_number: BookCourseDetail}.

    Pages are read via iter_pages_chunked, so peak memory stays bounded on the
    Render worker regardless of book length (see core/ingestion/pdf_pages).
    """
    pages = [(pno, page.extract_text() or "") for pno, page in iter_pages_chunked(pdf_path)]
    return parse_section_22(pages)
