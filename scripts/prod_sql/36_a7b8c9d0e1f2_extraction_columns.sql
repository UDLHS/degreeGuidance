BEGIN;

-- Running upgrade f4a5b6c7d8e9 -> a7b8c9d0e1f2

CREATE TABLE extraction_columns (
    column_id BIGSERIAL NOT NULL, 
    run_id UUID NOT NULL, 
    column_key VARCHAR(30) NOT NULL, 
    page_number INTEGER NOT NULL, 
    raw_label TEXT NOT NULL, 
    markers VARCHAR(10), 
    suggested_course_code VARCHAR(15), 
    suggestion_confidence NUMERIC(4, 3), 
    mapped_course_code VARCHAR(15), 
    status VARCHAR(20) DEFAULT 'pending' NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (column_id), 
    CONSTRAINT ck_extraction_columns_status CHECK (status IN ('pending', 'confirmed', 'ignored')), 
    CONSTRAINT uq_extraction_columns_run_key UNIQUE (run_id, column_key), 
    FOREIGN KEY(run_id) REFERENCES ingestion_runs (run_id) ON DELETE CASCADE, 
    FOREIGN KEY(mapped_course_code) REFERENCES courses (course_code) ON DELETE RESTRICT
);

COMMENT ON COLUMN extraction_columns.column_key IS 'stable id within the run, e.g. ''p190.g1.c05''';

COMMENT ON COLUMN extraction_columns.markers IS 'printed flags seen in the label: ''#'' aptitude, ''*'' all-island';

COMMENT ON COLUMN extraction_columns.status IS 'pending | confirmed | ignored';

CREATE INDEX idx_extraction_columns_run ON extraction_columns (run_id, status);

ALTER TABLE ingestion_runs ADD COLUMN cutoff_pages TEXT;

ALTER TABLE ingestion_runs DROP CONSTRAINT chk_run_status;

ALTER TABLE ingestion_runs ADD CONSTRAINT chk_run_status CHECK (status IN ('running', 'success', 'failed', 'partial', 'needs_pages', 'needs_mapping'));

UPDATE alembic_version SET version_num='a7b8c9d0e1f2' WHERE alembic_version.version_num = 'f4a5b6c7d8e9';

COMMIT;

