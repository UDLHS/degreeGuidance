-- 42: ingestion_artifacts — cross-instance artifact store (W2 follow-through)
-- Generated from alembic revision 7fa2c4d81b3e and hand-reviewed.
-- Guarded: the version UPDATE only fires from the exact expected predecessor,
-- and the whole file is one transaction.

BEGIN;

CREATE TABLE ingestion_artifacts (
    artifact_id BIGSERIAL NOT NULL,
    run_id UUID NOT NULL,
    kind VARCHAR(40) NOT NULL,
    content BYTEA NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    PRIMARY KEY (artifact_id),
    CONSTRAINT uq_artifact_run_kind UNIQUE (run_id, kind),
    FOREIGN KEY (run_id) REFERENCES ingestion_runs (run_id) ON DELETE CASCADE
);

CREATE INDEX idx_artifacts_run ON ingestion_artifacts (run_id);

UPDATE alembic_version SET version_num = '7fa2c4d81b3e'
WHERE version_num = 'e75434db887c';

COMMIT;
