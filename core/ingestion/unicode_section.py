"""Parser for the handbook's own "Uni-Codes Assigned for each Course of Study
of University" section — the book's authoritative (course, university) -> code
table.

Why this exists: the 2025 book dropped Uni-Codes from the cutoff tables, so
column mapping had to fall back to name-similarity against OUR catalog — which
guessed wrong on near-sibling courses (129C/130C, 016C/028C). This section
states the answer inside the same book, same year: an exact lookup, no
guessing. It also cross-checks printed header codes in 2024-style books (the
section prints 007K correctly where the cutoff table misprints 006K).

Measured structure (2024 pp.150-156 = 261 codes; 2025 pp.149-155 = 255):
- normal upright text (not mirrored), one row per line:
  [bullet] COURSE NAME | UNIVERSITY | 001A
- column x-boundaries come from each page's header line
  ("COURSE OF STUDY  UNIVERSITY  UNI - CODE") — they shift between odd/even
  pages, so they are derived per page, never hardcoded;
- long cells wrap onto codeless fragment lines above/below their row
  (e.g. 012T: "UNIVERSITY OF COLOMBO SCHOOL OF" / "COMPUTING"), assigned to
  the nearest code-bearing row by y — the same nearest-y rule proven in the
  grid extractor.

Pages are auto-detected by the header text; if the section is absent the
caller falls back to the existing suggestion ladder (purely additive).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import pdfplumber

from core.ingestion.column_mapper import normalize_label
from core.ingestion.pdf_pages import iter_pages_chunked

_HEADER_RE = re.compile(r"COURSE OF STUDY\s+UNIVERSITY\s+UNI\s*-\s*CODE", re.I)
_CODE_RE = re.compile(r"^\d{3}[A-Z]$")
# fragments further than this from any code-bearing row are page furniture
_FRAGMENT_MAX_DIST = 12.0
# words in the same visual line can jitter a point or two in `top`
_LINE_TOP_TOL = 3.0


@dataclass
class BookCodeRow:
    code: str
    course_name: str
    university: str
    page_number: int


def _find_section_pages(pdf_path: str) -> list[int]:
    # A full-document sweep just to find the ~7 section pages — iterated in
    # chunks (iter_pages_chunked) so pdfminer's per-page memory accumulation
    # is released across the book instead of stacking. The keeper pages are
    # reread fresh by the detail pass below.
    return [
        pn
        for pn, page in iter_pages_chunked(pdf_path)
        if _HEADER_RE.search(page.extract_text() or "")
    ]


def _clean(text: str) -> str:
    # strip bullet glyphs / private-use chars the table uses as row markers
    return "".join(ch for ch in text if ch.isprintable() and ord(ch) < 0xE000).strip()


def _group_lines(words: list[dict]) -> list[tuple[float, list[dict]]]:
    """Cluster words into visual lines by `top` (tolerance _LINE_TOP_TOL)."""
    lines: list[tuple[float, list[dict]]] = []
    for w in sorted(words, key=lambda w: (w["top"], w["x0"])):
        if lines and abs(w["top"] - lines[-1][0]) <= _LINE_TOP_TOL:
            lines[-1][1].append(w)
        else:
            lines.append((w["top"], [w]))
    return lines


def _parse_page(page, page_number: int) -> tuple[list[BookCodeRow], list[str]]:
    warnings: list[str] = []
    words = [w for w in page.extract_words() if _clean(w["text"])]
    lines = _group_lines(words)

    # header line -> column boundaries for THIS page
    uni_x = code_x = header_y = None
    for top, ws in lines:
        texts = {_clean(w["text"]) for w in ws}
        if {"COURSE", "STUDY", "UNIVERSITY"} <= texts and ("CODE" in texts or "UNI" in texts):
            for w in ws:
                t = _clean(w["text"])
                if t == "UNIVERSITY":
                    uni_x = w["x0"]
                elif t == "UNI":
                    code_x = w["x0"]
            header_y = top
            break
    if uni_x is None or code_x is None:
        warnings.append(f"p{page_number}: table header not found — page skipped")
        return [], warnings

    @dataclass
    class _Line:
        y: float
        name: list[str]
        uni: list[str]
        codes: list[str]

    parsed: list[_Line] = []
    for top, ws in lines:
        if top <= header_y:
            continue
        name_parts: list[str] = []
        uni_parts: list[str] = []
        codes: list[str] = []
        for w in sorted(ws, key=lambda w: w["x0"]):
            t = _clean(w["text"])
            if not t:
                continue
            if w["x0"] >= code_x - 5:
                if _CODE_RE.match(t):
                    codes.append(t)
                # non-code text in the code column is furniture; ignore
            elif w["x0"] >= uni_x - 5:
                uni_parts.append(t)
            else:
                name_parts.append(t)
        if name_parts or uni_parts or codes:
            parsed.append(_Line(top, name_parts, uni_parts, codes))

    row_lines = [l for l in parsed if len(l.codes) == 1]
    multi = [l for l in parsed if len(l.codes) > 1]
    for l in multi:
        warnings.append(
            f"p{page_number}: line at y={l.y:.0f} carries {len(l.codes)} codes "
            f"({'/'.join(l.codes)}) — skipped, falls back to the ladder"
        )
    if not row_lines:
        warnings.append(f"p{page_number}: no code rows found")
        return [], warnings

    # attach codeless fragments (wrapped cells) to the nearest row by y
    pieces: dict[int, list[_Line]] = {i: [l] for i, l in enumerate(row_lines)}
    for frag in parsed:
        if frag.codes:
            continue
        dists = [(abs(frag.y - r.y), i) for i, r in enumerate(row_lines)]
        d, i = min(dists)
        if d <= _FRAGMENT_MAX_DIST:
            pieces[i].append(frag)
        # farther fragments are headings/footers — silently ignored

    rows: list[BookCodeRow] = []
    for i, row in enumerate(row_lines):
        parts = sorted(pieces[i], key=lambda l: l.y)
        name = " ".join(" ".join(p.name) for p in parts if p.name).strip()
        uni = " ".join(" ".join(p.uni) for p in parts if p.uni).strip()
        if not name or not uni:
            warnings.append(
                f"p{page_number}: row {row.codes[0]} missing "
                f"{'name' if not name else 'university'} — skipped"
            )
            continue
        rows.append(BookCodeRow(
            code=row.codes[0], course_name=name, university=uni, page_number=page_number,
        ))
    return rows, warnings


def parse_unicode_section(
    pdf_path: str, pages: list[int] | None = None
) -> tuple[list[BookCodeRow], list[str]]:
    """Parse the section. `pages` overrides auto-detection (1-based)."""
    rows: list[BookCodeRow] = []
    warnings: list[str] = []
    page_nums = pages or _find_section_pages(pdf_path)
    if not page_nums:
        return [], ["Uni-Codes section not found in this book"]
    # The keeper set is ~7 pages — a single open handle is fine (the leak only
    # bites on whole-book sweeps, which the detection above already chunked).
    with pdfplumber.open(pdf_path) as pdf:
        for pn in page_nums:
            if not (1 <= pn <= len(pdf.pages)):
                warnings.append(f"p{pn}: out of range — skipped")
                continue
            r, w = _parse_page(pdf.pages[pn - 1], pn)
            rows.extend(r)
            warnings.extend(w)
    return rows, warnings


def build_book_lookup(rows: list[BookCodeRow]) -> tuple[dict[str, str], list[str]]:
    """Normalized 'NAME (UNIVERSITY)' -> code, matching the cutoff-label shape.

    Ambiguous keys (same normalized label, different codes) are dropped from
    the exact lookup with a warning — the ladder's fuzzy rung still sees them.
    """
    lookup: dict[str, str] = {}
    ambiguous: set[str] = set()
    warnings: list[str] = []
    for r in rows:
        key = normalize_label(f"{r.course_name} ({r.university})")
        existing = lookup.get(key)
        if existing is not None and existing != r.code:
            ambiguous.add(key)
            warnings.append(
                f"ambiguous book row {key[:60]!r}: {existing} vs {r.code} — excluded from exact lookup"
            )
            continue
        lookup[key] = r.code
    for key in ambiguous:
        lookup.pop(key, None)
    return lookup, warnings


def book_lookup_key(raw_label: str) -> str:
    """Cutoff-column label -> lookup key: markers are stripped by
    normalize_label; bracketed stream qualifiers ('[Commerce Stream]') are
    removed so per-stream twin columns hit their single section row."""
    no_brackets = re.sub(r"\[[^\]]*\]", " ", raw_label)
    return normalize_label(no_brackets)


# ── fuzzy matching against the section (wording differs from the cutoff
#    tables: 'BIO.SC' vs 'BIOLOGICAL SC.', 'SRIPALEE' vs 'Sri Palee',
#    'Eastern University - Trincomalee Campus' vs 'TRINCOMALEE CAMPUS,
#    EASTERN UNIVERSITY, SRI LANKA' — all measured, none assumed) ────────────

from difflib import SequenceMatcher  # noqa: E402  (kept with its user below)

_TOKEN_RE = re.compile(r"[A-Z0-9]+")
# accept a fuzzy winner only above this product score
_MIN_BOOK_SCORE = 0.55
# a winner this close to the runner-up is ambiguous -> confidence capped
_MIN_MARGIN = 0.08
_AMBIGUOUS_CAP = 0.70


def split_label(raw_label: str) -> tuple[str, str]:
    """'NAME ... (University …)' -> (name_part, university_part).

    The university is the LAST balanced parenthetical; inner parens like
    '(MIT)' or '(BIO.SC)' stay in the name. Bracketed stream qualifiers are
    dropped from the name."""
    s = re.sub(r"\[[^\]]*\]", " ", raw_label).strip()
    if s.endswith(")") and "(" in s:
        depth = 0
        for i in range(len(s) - 1, -1, -1):
            if s[i] == ")":
                depth += 1
            elif s[i] == "(":
                depth -= 1
                if depth == 0:
                    return s[:i].strip(), s[i + 1 : -1].strip()
    return s, ""


def _letters(text: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", text.upper())


def _name_sim(a: str, b: str) -> float:
    an, bn = normalize_label(a), normalize_label(b)
    at, bt = set(_TOKEN_RE.findall(an)), set(_TOKEN_RE.findall(bn))
    if not at or not bt:
        return 0.0
    jac = len(at & bt) / len(at | bt)
    ratio = SequenceMatcher(None, an, bn).ratio()
    # letters-only kills spacing/punct variants (URBAN BIORESOURCES vs
    # URBAN BIO RESOURCES; ARTS(SAB) vs ARTS (SAB) - B)
    lratio = SequenceMatcher(None, _letters(an), _letters(bn)).ratio()
    return 0.35 * jac + 0.35 * ratio + 0.30 * lratio


def _uni_sim(a: str, b: str) -> float:
    at = _TOKEN_RE.findall(normalize_label(a))
    bt = _TOKEN_RE.findall(normalize_label(b))
    if not at or not bt:
        return 0.0
    sa, sb = set(at), set(bt)
    jac = len(sa & sb) / len(sa | sb)
    # sorted-token join kills word-order variants (TRINCOMALEE CAMPUS,
    # EASTERN UNIVERSITY vs Eastern University - Trincomalee Campus) and
    # spacing variants via the letters reduction
    sorted_ratio = SequenceMatcher(
        None, _letters(" ".join(sorted(sa))), _letters(" ".join(sorted(sb)))
    ).ratio()
    return 0.5 * jac + 0.5 * sorted_ratio


def prepare_rows(rows: list[BookCodeRow]) -> list[tuple[BookCodeRow, str, str]]:
    """Precompute per-row (row, name, university) for repeated matching."""
    return [(r, r.course_name, r.university) for r in rows]


class BookMatcher:
    """Bundles the section's exact lookup + fuzzy matcher for the suggestion
    ladder. Passed into column_mapper.suggest_mappings (duck-typed there to
    avoid a circular import)."""

    def __init__(self, rows: list[BookCodeRow]):
        self.rows = rows
        self.lookup, self.lookup_warnings = build_book_lookup(rows)
        self._prepared = prepare_rows(rows)
        self.codes = {r.code for r in rows}

    def match(self, raw_label: str) -> tuple[str | None, float, bool]:
        """(code, raw_score, ambiguous): exact section hit -> (code, 1.0, False),
        else the fuzzy raw score with a thin-margin ambiguity flag. The RAW
        score is for comparing against other sources; ambiguity caps only the
        final confidence, never the comparison."""
        exact = self.lookup.get(book_lookup_key(raw_label))
        if exact is not None:
            return exact, 1.0, False
        return match_label(raw_label, self._prepared)


def match_label(
    raw_label: str, prepared: list[tuple[BookCodeRow, str, str]]
) -> tuple[str | None, float, bool]:
    """Best section row for a cutoff-column label -> (code, raw_score, ambiguous).

    Score = name_sim * university_sim (both must hold: the university pins the
    campus, the name separates siblings). A thin winner margin marks the match
    ambiguous — the caller caps the CONFIDENCE, but comparisons between
    sources must use the raw score."""
    name, uni = split_label(raw_label)
    if not name or not uni:
        return None, 0.0, False
    scored: list[tuple[float, str]] = []
    for row, r_name, r_uni in prepared:
        s = _name_sim(name, r_name) * _uni_sim(uni, r_uni)
        if s > 0:
            scored.append((s, row.code))
    if not scored:
        return None, 0.0, False
    scored.sort(reverse=True)
    best_score, best_code = scored[0]
    if best_score < _MIN_BOOK_SCORE:
        return None, 0.0, False
    runner_up = next((s for s, c in scored[1:] if c != best_code), 0.0)
    return best_code, round(best_score, 3), best_score - runner_up < _MIN_MARGIN
