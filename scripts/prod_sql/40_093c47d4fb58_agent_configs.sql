BEGIN;

-- Running upgrade 985e13967bd9 -> 093c47d4fb58

CREATE TABLE agent_configs (
    config_id SERIAL NOT NULL, 
    name VARCHAR(100) NOT NULL, 
    system_prompt_template TEXT NOT NULL, 
    model_name VARCHAR(100) NOT NULL, 
    web_search_default BOOLEAN DEFAULT true NOT NULL, 
    max_tool_turns INTEGER DEFAULT 6 NOT NULL, 
    notes TEXT, 
    is_active BOOLEAN DEFAULT false NOT NULL, 
    created_by UUID, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (config_id), 
    CONSTRAINT ck_agent_configs_turns CHECK (max_tool_turns BETWEEN 1 AND 12), 
    FOREIGN KEY(created_by) REFERENCES users (user_id) ON DELETE SET NULL
);

CREATE UNIQUE INDEX uq_agent_configs_one_active ON agent_configs (is_active) WHERE is_active;

UPDATE alembic_version SET version_num='093c47d4fb58' WHERE alembic_version.version_num = '985e13967bd9';

COMMIT;

