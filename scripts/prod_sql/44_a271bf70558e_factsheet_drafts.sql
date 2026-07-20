BEGIN;

-- Running upgrade c5d8e2f91a47 -> a271bf70558e

CREATE TABLE factsheet_drafts (
    course_number VARCHAR(10) NOT NULL, 
    status VARCHAR(20) DEFAULT 'queued' NOT NULL, 
    content TEXT, 
    error TEXT, 
    provenance JSONB, 
    requested_by UUID, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (course_number), 
    CONSTRAINT ck_factsheet_drafts_status CHECK (status IN ('queued', 'ready', 'failed', 'rejected')), 
    FOREIGN KEY(requested_by) REFERENCES users (user_id) ON DELETE SET NULL
);

UPDATE alembic_version SET version_num='a271bf70558e' WHERE alembic_version.version_num = 'c5d8e2f91a47';

COMMIT;

