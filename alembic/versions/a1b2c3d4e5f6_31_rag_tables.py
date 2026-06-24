"""31 RAG tables — document_sources and chunks with pgvector

Week 4 RAG pipeline. Stores factsheet content as searchable chunks with
Google gemini-embedding-001 embeddings truncated to 768 dims via Matryoshka
(output_dimensionality=768) for hybrid BM25+pgvector retrieval.

Revision ID: a1b2c3d4e5f6
Revises: 5b7bc34e2628
Create Date: 2026-06-24
"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


revision = 'a1b2c3d4e5f6'
down_revision = '5b7bc34e2628'
branch_labels = None
depends_on = None

EMBEDDING_DIM = 768  # Matryoshka truncation of gemini-embedding-001 (full=3072)


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "document_sources",
        sa.Column("source_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("source_type", sa.String(30), nullable=False),
        sa.Column("course_number", sa.String(10), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("file_path", sa.String(512), nullable=True),
        sa.Column("content_hash", sa.String(64), nullable=False, unique=True),
        sa.Column(
            "indexed_at", sa.DateTime(timezone=True),
            nullable=False, server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "chunks",
        sa.Column("chunk_id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "source_id", sa.Integer,
            sa.ForeignKey("document_sources.source_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("chunk_index", sa.Integer, nullable=False),
        sa.Column("heading", sa.String(255), nullable=True),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("token_count", sa.Integer, nullable=True),
        sa.Column("embedding", Vector(EMBEDDING_DIM), nullable=True),
        sa.UniqueConstraint("source_id", "chunk_index", name="uq_chunk_source_index"),
    )

    op.execute(
        "CREATE INDEX idx_chunks_embedding "
        "ON chunks USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64)"
    )
    op.execute(
        "ALTER TABLE chunks ADD COLUMN fts_vector tsvector "
        "GENERATED ALWAYS AS (to_tsvector('english', content)) STORED"
    )
    op.execute("CREATE INDEX idx_chunks_fts ON chunks USING gin (fts_vector)")
    op.execute("CREATE INDEX idx_chunks_source ON chunks (source_id)")


def downgrade() -> None:
    op.drop_table("chunks")
    op.drop_table("document_sources")
