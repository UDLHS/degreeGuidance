"""ORM models for RAG knowledge base — factsheets (source of truth,
migration 41), document_sources and chunks (the embedded index)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db import Base

EMBEDDING_DIM = 768  # gemini-embedding-001 with output_dimensionality=768


class Factsheet(Base):
    """Editable factsheet markdown — the SOURCE the index job reads (migration
    41; decision D3). One row per 3-digit course number. content_hash vs the
    indexed document_sources.content_hash is the staleness signal."""

    __tablename__ = "factsheets"

    course_number: Mapped[str] = mapped_column(String(10), primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class DocumentSource(Base):
    __tablename__ = "document_sources"

    source_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_type: Mapped[str] = mapped_column(String(30), nullable=False)
    course_number: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    indexed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    chunks: Mapped[list[Chunk]] = relationship(
        "Chunk", back_populates="source", cascade="all, delete-orphan"
    )


class Chunk(Base):
    __tablename__ = "chunks"
    __table_args__ = (
        UniqueConstraint("source_id", "chunk_index", name="uq_chunk_source_index"),
    )

    chunk_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("document_sources.source_id", ondelete="CASCADE"), nullable=False
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    heading: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    embedding: Mapped[Optional[list[float]]] = mapped_column(Vector(EMBEDDING_DIM), nullable=True)

    source: Mapped[DocumentSource] = relationship("DocumentSource", back_populates="chunks")
