-- 43: articles — admin-authored knowledge beyond courses (Phase 8.6)
-- Generated from alembic revision c5d8e2f91a47 and hand-reviewed.
-- Guarded: the version UPDATE only fires from the exact expected predecessor,
-- and the whole file is one transaction. No seed — articles start empty.

BEGIN;

CREATE TABLE articles (
    article_id SERIAL NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    version INTEGER DEFAULT 1 NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    PRIMARY KEY (article_id),
    FOREIGN KEY (updated_by) REFERENCES users (user_id) ON DELETE SET NULL
);

UPDATE alembic_version SET version_num = 'c5d8e2f91a47'
WHERE version_num = '7fa2c4d81b3e';

COMMIT;
