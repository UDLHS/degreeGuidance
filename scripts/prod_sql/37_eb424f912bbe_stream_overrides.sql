BEGIN;

-- Running upgrade a7b8c9d0e1f2 -> eb424f912bbe

CREATE TABLE course_stream_cutoff_overrides (
    override_id BIGSERIAL NOT NULL, 
    year INTEGER NOT NULL, 
    course_code VARCHAR(15) NOT NULL, 
    district_id INTEGER NOT NULL, 
    stream_id INTEGER NOT NULL, 
    z_score NUMERIC(6, 4), 
    notes TEXT, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (override_id), 
    CONSTRAINT uq_stream_override_year_course_district_stream UNIQUE (year, course_code, district_id, stream_id), 
    FOREIGN KEY(course_code) REFERENCES courses (course_code) ON DELETE RESTRICT, 
    FOREIGN KEY(district_id) REFERENCES districts (district_id) ON DELETE RESTRICT, 
    FOREIGN KEY(stream_id) REFERENCES streams (stream_id) ON DELETE RESTRICT
);

CREATE INDEX idx_stream_override_course_year ON course_stream_cutoff_overrides (course_code, year);

ALTER TABLE extraction_columns ADD COLUMN override_streams VARCHAR(200);

COMMENT ON COLUMN extraction_columns.override_streams IS 'comma-separated stream codes this confirmed column represents, when it shares its mapped code with another confirmed column (disjoint stream split, e.g. ''COMMERCE'' / ''BIO_SCIENCE,PHYSICAL_SCIENCE'')';

UPDATE alembic_version SET version_num='eb424f912bbe' WHERE alembic_version.version_num = 'a7b8c9d0e1f2';

COMMIT;

