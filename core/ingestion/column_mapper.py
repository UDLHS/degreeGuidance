"""Deterministic column -> course mapping suggestions (Gate 2 input).

For every extracted grid column, propose which catalog course it is:

1. code   — the printed Uni-Code exists in the catalog (confidence 1.0).
2. alias  — the printed label (or code) matches course_aliases.alias_text
            exactly (confidence 1.0). Confirmed mappings are written back as
            aliases, so each year's corrections make the next year automatic.
3. name   — normalized-text similarity between the printed label and
            courses.name_en (which includes the university). Deterministic
            (difflib + token overlap), never an LLM. Confidence = blended
            score; below _MIN_CONFIDENCE no suggestion is made.

The admin confirms every mapping at Gate 2 — suggestions only pre-fill.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.ingestion.grid_extractor import GridColumn
from core.models import Course, CourseAlias

_MIN_CONFIDENCE = 0.55

_WORD_RE = re.compile(r"[A-Z0-9]+")
# printed flags + bracketed stream qualifiers are not part of the course name
_MARKS_RE = re.compile(r"[#*]")
# a trailing single-letter track marker in the NAME part, e.g. ' - A' / ' - B'.
# These mark admission tracks of ONE course (a stream/quota split), not
# separate courses — the book's Uni-Code section lists only the base name.
_VARIANT_SUFFIX_RE = re.compile(r"\s*-\s*[A-Z]\b")


def strip_variant_suffix(label: str) -> str:
    """'Management Studies (TV) - B [Any subject…] (Univ…)' ->
       'Management Studies (TV) [Any subject…] (Univ…)'. Only single-letter
    A/B/C track markers are removed; multi-word suffixes like ' - Mass Media'
    are left intact (that ' - M' is not a bare letter)."""
    return _VARIANT_SUFFIX_RE.sub(" ", label)


def normalize_label(text: str) -> str:
    s = _MARKS_RE.sub(" ", text.upper())
    s = s.replace("&", " AND ")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _tokens(text: str) -> set[str]:
    return set(_WORD_RE.findall(normalize_label(text)))


def _letters(text: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", text.upper())


def label_similarity(a_norm: str, a_tok: set[str], b_norm: str, b_tok: set[str]) -> float:
    """Shared 3-way blend: token overlap + string ratio + letters-only ratio.

    The letters-only component kills spacing/punctuation variants that break
    tokenization — 'URBAN BIORESOURCES' vs 'Urban Bio Resources' is a single
    differing space, but token-Jaccard sees BIORESOURCES != BIO+RESOURCES."""
    if not a_tok or not b_tok:
        return 0.0
    jaccard = len(a_tok & b_tok) / len(a_tok | b_tok)
    ratio = SequenceMatcher(None, a_norm, b_norm).ratio()
    lratio = SequenceMatcher(None, _letters(a_norm), _letters(b_norm)).ratio()
    return 0.35 * jaccard + 0.35 * ratio + 0.30 * lratio


# thin winner margins are ambiguous — cap so bulk-confirm never auto-takes them
_CATALOG_MARGIN = 0.06
_AMBIGUOUS_CAP = 0.70


@dataclass
class MappingSuggestion:
    column_key: str
    raw_label: str | None
    suggested_course_code: str | None
    confidence: float | None
    source: str | None  # 'code' | 'alias' | 'name' | None


async def suggest_mappings(
    db: AsyncSession, columns: list[GridColumn], book=None
) -> list[MappingSuggestion]:
    """`book` is a unicode_section.BookMatcher (duck-typed to avoid a circular
    import): the handbook's own Uni-Code section, the authoritative same-year
    (course, university) -> code table. Ladder:

      1. printed header code that the book section AGREES with (or no book) -> 1.0 'code'
         — a section DISAGREEMENT means a header misprint (006K-style):
           the section's code is suggested at <=0.95 'book' and is never
           auto-confirmed
      2. exact section hit                                  -> 1.0  'book'
      3. exact alias (label or code)                        -> 1.0  'alias'
      4. fuzzy section match                                -> conf 'book'
      5. catalog name similarity                            -> conf 'name'

    A section code missing from our catalog (a genuinely NEW course) is
    surfaced as 'book_new' below the auto-confirm threshold — the admin
    creates the course first, then maps."""
    course_rows = (
        await db.execute(select(Course.course_code, Course.name_en))
    ).all()
    catalog = {code: name for code, name in course_rows}
    prepared = [
        (code, normalize_label(name), _tokens(name)) for code, name in course_rows
    ]

    alias_rows = (
        await db.execute(select(CourseAlias.alias_text, CourseAlias.course_code))
    ).all()
    aliases = {text: code for text, code in alias_rows}

    def catalog_best(label: str) -> tuple[str | None, float, bool]:
        # bracketed stream qualifiers are matching noise here — the variant
        # discriminator the catalog carries is the '- A'/'- B' name suffix
        clean = re.sub(r"\[[^\]]*\]", " ", label)
        l_norm, l_tok = normalize_label(clean), _tokens(clean)
        best_code, best_score, runner_up = None, 0.0, 0.0
        for code, c_norm, c_tok in prepared:
            s = label_similarity(l_norm, l_tok, c_norm, c_tok)
            if s > best_score:
                if code != best_code:
                    runner_up = best_score
                best_code, best_score = code, s
            elif s > runner_up and code != best_code:
                runner_up = s
        # raw score for source comparison; ambiguity caps only the confidence
        return best_code, best_score, best_score - runner_up < _CATALOG_MARGIN

    out: list[MappingSuggestion] = []
    for col in columns:
        label = col.raw_label or ""

        # 1) a printed header code that exists in the catalog always wins.
        #    (The Uni-Code section does NOT list stream-variant codes like
        #    042L/271D/040R/040W — the header is the only place they're
        #    printed, so it must never be demoted by a section fuzzy match.)
        if col.code and col.code in catalog:
            out.append(MappingSuggestion(col.column_key, label, col.code, 1.0, "code"))
            continue

        book_code: str | None = None
        book_conf = 0.0
        book_ambig = False
        if book is not None and label:
            book_code, book_conf, book_ambig = book.match(label)

        # 2) exact section hit
        if book_code and book_conf >= 0.999:
            if book_code in catalog:
                out.append(MappingSuggestion(col.column_key, label, book_code, 1.0, "book"))
            else:
                out.append(MappingSuggestion(col.column_key, label, book_code, 0.99, "book_new"))
            continue

        # 3) exact alias on the label or the (possibly misprinted) code
        alias_hit = aliases.get(label.strip()) or (
            aliases.get(col.code) if col.code else None
        )
        if alias_hit and alias_hit in catalog:
            out.append(MappingSuggestion(col.column_key, label, alias_hit, 1.0, "alias"))
            continue

        # 3.5) same-course track variant. When THIS book prints no code for the
        #      column (name-only format) and the label carries a ' - A'/' - B'
        #      track marker, the book's section lists only the BASE course. So
        #      strip the marker and match the base against the section: both
        #      'X - A' and 'X - B' resolve to the base's one code (e.g. 022R for
        #      Management Studies (TV), 021L for Arts (SAB)) as stream variants.
        #      This must beat the catalog rung below, because a catalog code
        #      carrying the '- B' suffix (040R/040W/042L) only exists there from
        #      a DIFFERENT year's book — it is not in THIS book, so it must not
        #      be applied to this year. Kept below the auto-confirm threshold:
        #      the admin still confirms and assigns streams (the existing
        #      duplicate/stream-override flow), never silent.
        if col.code is None and book is not None and label and _VARIANT_SUFFIX_RE.search(label):
            base_code, base_conf, _ = book.match(strip_variant_suffix(label))
            if base_code and base_conf >= _MIN_CONFIDENCE and base_code in catalog:
                out.append(MappingSuggestion(
                    col.column_key, label, base_code, min(round(base_conf, 3), 0.95),
                    "book_variant",
                ))
                continue

        # 4) fuzzy duel: book section vs catalog names — RAW scores compared,
        #    book preferred on near-ties (same-year authority). The catalog
        #    wins stream variants (its names carry the '- A'/'- B' suffixes the
        #    section lacks); the book wins wording drift (URBAN BIO RESOURCES,
        #    SRIPALEE, BIOLOGICAL SC.) and knows codes for genuinely new
        #    courses ('book_new' — below every auto-confirm threshold).
        #    Ambiguity (thin winner margin) caps only the final confidence.
        cat_code, cat_score, cat_ambig = catalog_best(label) if label else (None, 0.0, False)
        prefer_book = (
            book_code is not None
            and book_conf >= _MIN_CONFIDENCE
            and book_conf >= cat_score - 0.02
        )
        if prefer_book:
            conf = min(book_conf, _AMBIGUOUS_CAP) if book_ambig else book_conf
            if book_code in catalog:
                out.append(MappingSuggestion(
                    col.column_key, label, book_code, round(conf, 3), "book"
                ))
            else:
                out.append(MappingSuggestion(
                    col.column_key, label, book_code, min(round(conf, 3), 0.9), "book_new"
                ))
            continue
        if cat_code is not None and cat_score >= _MIN_CONFIDENCE:
            conf = min(cat_score, _AMBIGUOUS_CAP) if cat_ambig else cat_score
            out.append(MappingSuggestion(
                col.column_key, label, cat_code, round(conf, 3), "name"
            ))
            continue

        out.append(MappingSuggestion(col.column_key, label or None, None, None, None))
    return out
