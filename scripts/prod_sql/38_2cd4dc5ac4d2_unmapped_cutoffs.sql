BEGIN;

-- Running upgrade eb424f912bbe -> 2cd4dc5ac4d2

CREATE TABLE unmapped_cutoffs (
    unmapped_id BIGSERIAL NOT NULL, 
    run_id UUID, 
    year INTEGER NOT NULL, 
    raw_label TEXT NOT NULL, 
    course_name TEXT, 
    university TEXT, 
    district_id INTEGER NOT NULL, 
    z_score NUMERIC(6, 4), 
    notes TEXT, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (unmapped_id), 
    CONSTRAINT uq_unmapped_year_label_district UNIQUE (year, raw_label, district_id), 
    FOREIGN KEY(run_id) REFERENCES ingestion_runs (run_id) ON DELETE SET NULL, 
    FOREIGN KEY(district_id) REFERENCES districts (district_id) ON DELETE RESTRICT
);

COMMENT ON COLUMN unmapped_cutoffs.run_id IS 'provenance; SET NULL so the cutoff persists past a run delete, like z_score_cutoffs';

COMMENT ON COLUMN unmapped_cutoffs.raw_label IS 'the printed cutoff-column label, verbatim (identity when there is no code)';

CREATE INDEX idx_unmapped_year ON unmapped_cutoffs (year);

ALTER TABLE extraction_columns DROP CONSTRAINT ck_extraction_columns_status;

ALTER TABLE extraction_columns ADD CONSTRAINT ck_extraction_columns_status CHECK (status IN ('pending', 'confirmed', 'ignored', 'unmapped_kept'));

UPDATE alembic_version SET version_num='2cd4dc5ac4d2' WHERE alembic_version.version_num = 'eb424f912bbe';

COMMIT;

