BEGIN;

-- Running upgrade 2cd4dc5ac4d2 -> 985e13967bd9

ALTER TABLE conversations ADD COLUMN flagged BOOLEAN DEFAULT false NOT NULL;

COMMENT ON COLUMN conversations.flagged IS 'admin marked this conversation for review';

UPDATE alembic_version SET version_num='985e13967bd9' WHERE alembic_version.version_num = '2cd4dc5ac4d2';

COMMIT;

