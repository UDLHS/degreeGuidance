"""Memory-bounded page iteration for whole-document PDF sweeps.

pdfminer (under pdfplumber) accumulates document-level state for every page
touched within one open handle — font maps, the resource manager's caches,
the lazily-built page list. `page.flush_cache()` drops pdfplumber's per-page
cached properties but NOT this document-level growth, and glibc's
`malloc_trim` can't reclaim it while the handle is open. On a 200+ page
handbook that accumulation reaches ~500 MB and OOM-kills a memory-constrained
worker (measured: 1.25 GB peak on Render's free tier → crash-loop).

The one thing that reliably releases it is closing the PDF. So any sweep that
must visit the whole book does it in CHUNKS, closing and reopening the handle
between them — bounding peak memory to roughly one chunk's worth regardless of
book length. Measured on the 2024 handbook: the whole-book text sweep drops
from ~695 MB to ~305 MB peak, flat across chunks.

Reopening a 6-15 MB PDF costs ~0.1 s and there are only ~5 chunks, so the time
cost is negligible next to the extraction itself.
"""

from __future__ import annotations

import ctypes
import ctypes.util
import gc
from collections.abc import Iterator
from typing import Any

import pdfplumber

# Pages per open handle. 40 keeps the 2024/2025 books comfortably under a
# 512 MB worker while staying well above the ~10-page cutoff cluster and the
# ~7-page Uni-Code section (so a single keeper run rarely needs a second open).
PAGE_CHUNK = 40


def _load_libc_malloc_trim():
    """glibc's malloc_trim(0), or None where unavailable (musl, macOS, Windows).

    Returning freed pages to the OS is a glibc-specific extension; everywhere
    else this is simply skipped — chunked close/reopen is what does the real
    work, malloc_trim only tidies the arena between chunks on glibc hosts
    (Render runs Debian/glibc)."""
    name = ctypes.util.find_library("c")
    if not name:
        return None
    try:
        libc = ctypes.CDLL(name)
        fn = libc.malloc_trim  # AttributeError on musl/macOS
        fn.argtypes = [ctypes.c_size_t]
        return fn
    except (OSError, AttributeError):
        return None


_MALLOC_TRIM = _load_libc_malloc_trim()


def reclaim() -> None:
    """Collect Python cycles and hand freed heap pages back to the OS.
    Called between chunks; a no-op beyond gc.collect() off glibc."""
    gc.collect()
    if _MALLOC_TRIM is not None:
        try:
            _MALLOC_TRIM(0)
        except Exception:  # noqa: BLE001 - never let cleanup break a sweep
            pass


def count_pages(pdf_path: str) -> int:
    with pdfplumber.open(pdf_path) as pdf:
        return len(pdf.pages)


def iter_pages_chunked(
    pdf_path: str, chunk_size: int = PAGE_CHUNK
) -> Iterator[tuple[int, Any]]:
    """Yield (page_number_1based, page) across the whole document, reopening
    the PDF every `chunk_size` pages so pdfminer's per-page accumulation is
    released on each close.

    The caller MUST finish using each yielded page before the next iteration
    (its cache is flushed on resume, and its handle is closed at the chunk
    boundary). Do not retain page objects across iterations.
    """
    total = count_pages(pdf_path)
    for start in range(0, total, chunk_size):
        with pdfplumber.open(pdf_path) as pdf:
            for pn in range(start, min(start + chunk_size, total)):
                page = pdf.pages[pn]
                yield pn + 1, page
                page.flush_cache()
        reclaim()
