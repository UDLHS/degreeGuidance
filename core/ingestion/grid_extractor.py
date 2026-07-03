"""Format-agnostic cutoff-grid extractor (Phase 1 of the handbook pipeline).

Extracts the raw cutoff table from a handbook PDF **without assuming how columns
are labelled**. Empirically verified against both known layouts:

- 2024-style: columns carry Uni-Codes ('001A') in a rotated header cluster,
  plus upright course-name labels. Codes cross-validated against the seed
  catalog via y-alignment (27/27 on p179).
- 2025-style: no codes anywhere; columns carry upright, mirror-rendered
  'COURSE NAME (University …)' labels only.
- Multi-grid pages: e.g. 2025 p190 holds two independent 25×26 grids side by
  side (row x-bands −357..−134 and 257..477, split by a 391pt gap).

Geometry (all measured, not assumed):
- District rows are rotated char clusters at constant x; values read in
  y-order. Column positions are the values' y-centers.
- Column labels are upright lines (text mirror-reversed, so un-mirrored with
  [::-1]); a label block's y-center sits within ~2pt of its column's y-center.
- Code headers are one rotated cluster; each code's y-center likewise matches
  its column.

Everything is matched by nearest-y with a tolerance of half the column pitch —
one mechanism for codes and name labels. The extractor never decides what a
column *means*; it reports raw labels for the Gate-2 mapping review.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from statistics import median

import pdfplumber

from scripts.native_pdf_extractor.extract_cutoffs import (
    DISTRICTS_ORDER,
    DISTRICTS_SORTED_BY_LEN,
    UNICODE_RE,
    ZSCORE_RE,
    cluster_by_x,
    get_rotated_chars,
    is_cutoff_page,
)

# rows within a grid sit ~9pt apart; a new grid starts after a much larger gap
_GRID_SPLIT_GAP = 50.0
# upright lines within one label block are ~6pt apart; blocks are ~19-26pt apart
_LABEL_LINE_GAP = 8.0
# chars in one label line sit a few pt apart; on two-grid pages, both grids'
# labels can share a y-row ~470pt apart — split such rows into segments
_LINE_SPLIT_X_GAP = 25.0
_MIN_ROWS_PER_GRID = 10
_MIN_CODES_FOR_HEADER = 15

_MARKER_RE = re.compile(r"[#*]")


# ── data structures ──────────────────────────────────────────────────────────

@dataclass
class GridColumn:
    column_key: str          # e.g. 'p190.g1.c05'
    page_number: int
    grid_index: int
    column_index: int        # y-order within the grid
    y_center: float
    raw_label: str | None    # printed label: code, or 'NAME (University …)'
    code: str | None         # set when the label source was a Uni-Code header
    markers: str | None      # '#' aptitude / '*' all-island flags seen in label


@dataclass
class PageGrid:
    page_number: int
    grid_index: int
    columns: list[GridColumn]
    # district -> list aligned to columns (value str, 'NQC', or None if blank)
    rows: dict[str, list[str | None]]
    warnings: list[str] = field(default_factory=list)


@dataclass
class GridExtraction:
    pages_processed: list[int]
    grids: list[PageGrid]
    warnings: list[str] = field(default_factory=list)

    @property
    def total_columns(self) -> int:
        return sum(len(g.columns) for g in self.grids)

    def all_warnings(self) -> list[str]:
        out = list(self.warnings)
        for g in self.grids:
            out.extend(f"p{g.page_number}.g{g.grid_index}: {w}" for w in g.warnings)
        return out

    def to_dict(self) -> dict:
        return {
            "pages_processed": self.pages_processed,
            "total_columns": self.total_columns,
            "warnings": self.all_warnings(),
            "grids": [
                {
                    "page_number": g.page_number,
                    "grid_index": g.grid_index,
                    "columns": [
                        {
                            "column_key": c.column_key,
                            "column_index": c.column_index,
                            "raw_label": c.raw_label,
                            "code": c.code,
                            "markers": c.markers,
                        }
                        for c in g.columns
                    ],
                    "rows": g.rows,
                }
                for g in self.grids
            ],
        }


# ── page-spec helpers ────────────────────────────────────────────────────────

def parse_pages_spec(spec: str) -> list[int]:
    """'150-156,179-188' -> [150..156, 179..188]. Raises ValueError on nonsense."""
    pages: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        m = re.fullmatch(r"(\d+)\s*-\s*(\d+)", part)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if a > b or a < 1:
                raise ValueError(f"Invalid page range: {part!r}")
            pages.extend(range(a, b + 1))
            continue
        if part.isdigit():
            pages.append(int(part))
            continue
        raise ValueError(f"Invalid page spec segment: {part!r}")
    if not pages:
        raise ValueError("Empty page spec")
    return sorted(set(pages))


# ── low-level geometry ───────────────────────────────────────────────────────

@dataclass
class _Row:
    x: float
    district: str
    values: list[tuple[str, float]]  # (text, y_center) sorted by y


def _district_rows(page) -> list[_Row]:
    rows: list[_Row] = []
    for cl in cluster_by_x(get_rotated_chars(page)):
        schars = sorted(cl, key=lambda c: c["top"])
        n = len(schars)
        rtext = "".join(c["text"] for c in schars)[::-1]
        for d in DISTRICTS_SORTED_BY_LEN:
            if rtext.startswith(d):
                vals: list[tuple[str, float]] = []
                for m in ZSCORE_RE.finditer(rtext):
                    tops = [schars[n - 1 - i]["top"] for i in range(m.start(), m.end())]
                    vals.append((m.group(), sum(tops) / len(tops)))
                if len(vals) >= 5:
                    x = sum(c["matrix"][4] for c in cl) / len(cl)
                    vals.sort(key=lambda v: v[1])
                    rows.append(_Row(x=x, district=d, values=vals))
                break
    rows.sort(key=lambda r: r.x)
    return rows


def _split_grids(rows: list[_Row]) -> list[list[_Row]]:
    if not rows:
        return []
    groups: list[list[_Row]] = [[rows[0]]]
    for prev, cur in zip(rows, rows[1:]):
        if cur.x - prev.x > _GRID_SPLIT_GAP:
            groups.append([])
        groups[-1].append(cur)
    return [g for g in groups if len(g) >= _MIN_ROWS_PER_GRID]


def _upright_lines(page) -> list[tuple[float, float, float, str]]:
    """[(y, x0, x1, un-mirrored text), ...] sorted by y.

    A y-row is split into segments on large x-gaps: on two-grid pages both
    grids' labels can share the same y (verified on 2025 p186, where one
    pdfplumber row spanned x −416..257 and interleaved two labels). Each
    segment un-mirrors independently.
    """
    by_top: dict[int, list] = {}
    for c in page.chars:
        if c["upright"]:
            by_top.setdefault(round(c["top"]), []).append(c)
    lines = []
    for top in sorted(by_top):
        row = sorted(by_top[top], key=lambda c: c["x0"])
        segments: list[list[dict]] = [[row[0]]]
        for prev, cur in zip(row, row[1:]):
            if cur["x0"] - prev["x1"] > _LINE_SPLIT_X_GAP:
                segments.append([])
            segments[-1].append(cur)
        for seg in segments:
            txt = "".join(ch["text"] for ch in seg).strip()
            if txt:
                lines.append((float(top), seg[0]["x0"], seg[-1]["x1"], txt[::-1]))
    lines.sort(key=lambda l: l[0])
    return lines


def _label_blocks(lines: list[tuple[float, float, float, str]]) -> list[tuple[float, str]]:
    """Group adjacent lines (y-gap <= _LABEL_LINE_GAP) into blocks.

    Within a block the mirror rendering puts the *last* text line first, so the
    block text is assembled bottom-up ('BIOLOGICAL SCIENCE' + '(University of
    Colombo)') — verified against the 2024 code cross-check.
    """
    blocks: list[tuple[float, str]] = []
    cur_ys: list[float] = []
    cur_txts: list[str] = []
    for y, _x0, _x1, t in lines:
        if cur_ys and y - cur_ys[-1] > _LABEL_LINE_GAP:
            blocks.append((sum(cur_ys) / len(cur_ys), " ".join(reversed(cur_txts))))
            cur_ys, cur_txts = [], []
        cur_ys.append(y)
        cur_txts.append(t)
    if cur_ys:
        blocks.append((sum(cur_ys) / len(cur_ys), " ".join(reversed(cur_txts))))
    return blocks


def _code_header(clusters_in_band: list[list[dict]]) -> list[tuple[str, float]]:
    """[(code, y_center), ...] from the rotated code-header cluster, if any."""
    best: list[tuple[str, float]] = []
    for cl in clusters_in_band:
        schars = sorted(cl, key=lambda c: c["top"])
        n = len(schars)
        rtext = "".join(c["text"] for c in schars)[::-1]
        found: list[tuple[str, float]] = []
        for m in UNICODE_RE.finditer(rtext):
            tops = [schars[n - 1 - i]["top"] for i in range(m.start(), m.end())]
            found.append((m.group(), sum(tops) / len(tops)))
        if len({c for c, _ in found}) >= _MIN_CODES_FOR_HEADER and len(found) > len(best):
            best = found
    best.sort(key=lambda cy: cy[1])
    return best


def _nearest_one_to_one(
    targets: list[float], items: list[tuple[float, object]], tol: float
) -> list[object | None]:
    """Assign each item (y, payload) to the nearest target y within tol; 1:1."""
    result: list[object | None] = [None] * len(targets)
    for y, payload in sorted(items, key=lambda it: it[0]):
        best_j, best_d = None, tol
        for j, ty in enumerate(targets):
            d = abs(ty - y)
            if d <= best_d and result[j] is None:
                best_j, best_d = j, d
        if best_j is not None:
            result[best_j] = payload
    return result


# ── per-grid assembly ────────────────────────────────────────────────────────

def _build_grid(
    page_number: int,
    grid_index: int,
    grid_rows: list[_Row],
    labels: list[tuple[float, str]],
    codes: list[tuple[str, float]],
) -> PageGrid:
    warnings: list[str] = []

    # Column template: rows with the modal value count define column y-centers.
    counts = sorted(len(r.values) for r in grid_rows)
    modal = max(set(counts), key=counts.count)
    template = [r for r in grid_rows if len(r.values) == modal]
    centers = [
        median(r.values[j][1] for r in template) for j in range(modal)
    ]
    pitch = median(
        centers[j + 1] - centers[j] for j in range(len(centers) - 1)
    ) if len(centers) > 1 else 25.0
    tol = pitch * 0.45

    # Assign every row's values to columns by nearest center (handles blanks).
    rows_aligned: dict[str, list[str | None]] = {}
    for r in grid_rows:
        assigned = _nearest_one_to_one(
            centers, [(y, v) for v, y in r.values], tol
        )
        dropped = len(r.values) - sum(1 for a in assigned if a is not None)
        if dropped:
            warnings.append(f"{r.district}: {dropped} value(s) did not align to a column")
        if r.district in rows_aligned:
            warnings.append(f"duplicate district row {r.district}")
        rows_aligned[r.district] = assigned

    missing = [d for d in DISTRICTS_ORDER if d not in rows_aligned]
    if missing:
        warnings.append(f"missing districts: {', '.join(missing)}")

    # Labels and codes matched to columns by the same nearest-y rule.
    label_for = _nearest_one_to_one(centers, [(y, t) for y, t in labels], tol)
    code_for = _nearest_one_to_one(centers, [(y, c) for c, y in codes], tol)

    if labels and sum(1 for l in label_for if l) < modal:
        warnings.append(
            f"only {sum(1 for l in label_for if l)}/{modal} columns got a name label"
        )
    if codes and sum(1 for c in code_for if c) < modal:
        warnings.append(
            f"only {sum(1 for c in code_for if c)}/{modal} columns got a code"
        )

    columns: list[GridColumn] = []
    for j in range(modal):
        label = label_for[j]
        code = code_for[j]
        raw = code if label is None else str(label)
        markers = "".join(sorted(set(_MARKER_RE.findall(raw or "")))) or None
        columns.append(
            GridColumn(
                column_key=f"p{page_number}.g{grid_index}.c{j:02d}",
                page_number=page_number,
                grid_index=grid_index,
                column_index=j,
                y_center=centers[j],
                raw_label=raw,
                code=str(code) if code else None,
                markers=markers,
            )
        )
    if not labels and not codes:
        warnings.append("no labels and no code header found for this grid")

    return PageGrid(
        page_number=page_number,
        grid_index=grid_index,
        columns=columns,
        rows=rows_aligned,
        warnings=warnings,
    )


# ── public API ───────────────────────────────────────────────────────────────

def extract_grid(pdf_path: str, pages: list[int] | None = None) -> GridExtraction:
    """Extract the raw cutoff grid. `pages` are 1-based; None = auto-detect."""
    grids: list[PageGrid] = []
    top_warnings: list[str] = []
    pages_processed: list[int] = []

    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        if pages is None:
            page_nums = [pn + 1 for pn in range(total) if is_cutoff_page(pdf.pages[pn])]
        else:
            page_nums = [p for p in pages if 1 <= p <= total]
            skipped = sorted(set(pages) - set(page_nums))
            if skipped:
                top_warnings.append(f"pages out of range skipped: {skipped}")

        for pn in page_nums:
            page = pdf.pages[pn - 1]
            rows = _district_rows(page)
            row_groups = _split_grids(rows)
            if not row_groups:
                top_warnings.append(f"p{pn}: no district rows found")
                continue
            pages_processed.append(pn)

            lines = _upright_lines(page)
            rotated_clusters = cluster_by_x(get_rotated_chars(page))

            # grid x-bands for assigning labels / code clusters to grids
            bands = [
                (min(r.x for r in g), max(r.x for r in g)) for g in row_groups
            ]

            def band_dist(x: float, band: tuple[float, float]) -> float:
                lo, hi = band
                return lo - x if x < lo else (x - hi if x > hi else 0.0)

            def label_band_index(x1: float) -> int:
                """Label lines are right-aligned toward their grid's row band
                (verified on p190: grid labels end just left of the band's low
                edge). Pick the band whose low edge sits nearest at/after the
                line's right edge; long labels can't leak to the wrong grid the
                way an x-center rule allows."""
                best, best_gap = 0, float("inf")
                for i, (lo, _hi) in enumerate(bands):
                    gap = lo - x1
                    score = gap if gap >= 0 else -gap * 10  # penalise overshoot
                    if score < best_gap:
                        best, best_gap = i, score
                return best

            for gi, grid_rows in enumerate(row_groups, start=1):
                grid_labels = []
                for y, x0, x1, t in lines:
                    if label_band_index(x1) == gi - 1:
                        grid_labels.append((y, x0, x1, t))
                labels = [
                    (y, t) for y, t in _label_blocks(grid_labels)
                    if len(t) > 4 and not t.upper().startswith(("DISTRICT", "COURSE"))
                ]

                grid_clusters = []
                for cl in rotated_clusters:
                    xc = sum(c["matrix"][4] for c in cl) / len(cl)
                    dists = [band_dist(xc, b) for b in bands]
                    if dists.index(min(dists)) == gi - 1:
                        grid_clusters.append(cl)
                codes = _code_header(grid_clusters)

                grids.append(_build_grid(pn, gi, grid_rows, labels, codes))

    return GridExtraction(
        pages_processed=pages_processed, grids=grids, warnings=top_warnings
    )
