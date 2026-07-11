BEGIN;

-- Running upgrade 093c47d4fb58 -> e75434db887c
-- DDL + version only. The 129 factsheet seed rows are inserted by
-- scripts/apply_prod_migrations.py with parameterized statements (the
-- generated literal INSERTs tripped a quoting edge in the markdown content).

CREATE TABLE factsheets (
    course_number VARCHAR(10) NOT NULL,
    content TEXT NOT NULL,
    version INTEGER DEFAULT 1 NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    updated_by UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    PRIMARY KEY (course_number),
    FOREIGN KEY(updated_by) REFERENCES users (user_id) ON DELETE SET NULL
);

UPDATE alembic_version SET version_num='e75434db887c' WHERE alembic_version.version_num = '093c47d4fb58';

COMMIT;
