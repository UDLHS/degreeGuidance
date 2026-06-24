"""Hybrid retrieval: pgvector (semantic) + PostgreSQL FTS (keyword) + RRF fusion.

Usage:
    from core.rag.retrieval import retrieve
    results = await retrieve(session, client, query="what z-score for engineering?", top_k=5)
"""

from __future__ import annotations

from dataclasses import dataclass

from google import genai
from google.genai.types import EmbedContentConfig
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings

RRF_K = 60          # Reciprocal Rank Fusion constant
CANDIDATE_N = 20    # candidates pulled from each retriever before fusion


@dataclass
class RetrievedChunk:
    chunk_id: int
    source_id: int
    course_number: str | None
    title: str
    heading: str | None
    content: str
    rrf_score: float


def _embed_query(client: genai.Client, query: str) -> list[float]:
    result = client.models.embed_content(
        model=settings.gemini_embedding_model,
        contents=query,
        config=EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=settings.gemini_embedding_dim,
        ),
    )
    return result.embeddings[0].values


async def _vector_search(
    session: AsyncSession,
    embedding: list[float],
    n: int,
) -> list[tuple[int, float]]:
    """Return (chunk_id, cosine_distance) for top-n semantic results."""
    sql = text(
        "SELECT chunk_id, embedding <=> :vec AS dist "
        "FROM chunks WHERE embedding IS NOT NULL "
        "ORDER BY dist LIMIT :n"
    )
    rows = (await session.execute(sql, {"vec": str(embedding), "n": n})).fetchall()
    return [(r.chunk_id, r.dist) for r in rows]


async def _fts_search(
    session: AsyncSession,
    query: str,
    n: int,
) -> list[tuple[int, float]]:
    """Return (chunk_id, ts_rank) for top-n full-text results."""
    sql = text(
        "SELECT chunk_id, ts_rank(fts_vector, plainto_tsquery('english', :q)) AS rank "
        "FROM chunks "
        "WHERE fts_vector @@ plainto_tsquery('english', :q) "
        "ORDER BY rank DESC LIMIT :n"
    )
    rows = (await session.execute(sql, {"q": query, "n": n})).fetchall()
    return [(r.chunk_id, r.rank) for r in rows]


def _rrf(
    vector_hits: list[tuple[int, float]],
    fts_hits: list[tuple[int, float]],
    k: int = RRF_K,
) -> list[tuple[int, float]]:
    """Reciprocal Rank Fusion — merge two ranked lists by chunk_id."""
    scores: dict[int, float] = {}

    for rank, (chunk_id, _) in enumerate(vector_hits, 1):
        scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank)

    for rank, (chunk_id, _) in enumerate(fts_hits, 1):
        scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank)

    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


async def _fetch_chunks(
    session: AsyncSession,
    chunk_ids: list[int],
    rrf_scores: dict[int, float],
) -> list[RetrievedChunk]:
    if not chunk_ids:
        return []
    sql = text(
        "SELECT c.chunk_id, c.source_id, c.heading, c.content, "
        "       d.course_number, d.title "
        "FROM chunks c "
        "JOIN document_sources d ON d.source_id = c.source_id "
        "WHERE c.chunk_id = ANY(:ids)"
    )
    rows = (await session.execute(sql, {"ids": chunk_ids})).fetchall()
    result = [
        RetrievedChunk(
            chunk_id=r.chunk_id,
            source_id=r.source_id,
            course_number=r.course_number,
            title=r.title,
            heading=r.heading,
            content=r.content,
            rrf_score=rrf_scores.get(r.chunk_id, 0.0),
        )
        for r in rows
    ]
    result.sort(key=lambda x: x.rrf_score, reverse=True)
    return result


async def retrieve(
    session: AsyncSession,
    client: genai.Client,
    query: str,
    top_k: int = 5,
) -> list[RetrievedChunk]:
    """Hybrid retrieval: embed query → vector search + FTS → RRF → top_k chunks."""
    embedding = _embed_query(client, query)

    vector_hits, fts_hits = await _vector_search(
        session, embedding, CANDIDATE_N
    ), await _fts_search(session, query, CANDIDATE_N)

    # Merge all unique chunk_ids, preserving RRF ordering
    fused = _rrf(vector_hits, fts_hits)
    top_ids = [cid for cid, _ in fused[:top_k]]
    rrf_scores = {cid: score for cid, score in fused}

    return await _fetch_chunks(session, top_ids, rrf_scores)
