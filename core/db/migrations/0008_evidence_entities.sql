CREATE TABLE IF NOT EXISTS evidence_entities (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    run_id TEXT,

    evidence_id TEXT NOT NULL,

    entity_type TEXT NOT NULL,

    entity_value TEXT NOT NULL,

    normalized_value TEXT,

    confidence TEXT DEFAULT 'HIGH',

    source TEXT DEFAULT 'extracted',

    created_at_ms INTEGER,

    metadata_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_entities_evidence
ON evidence_entities(evidence_id);

CREATE INDEX IF NOT EXISTS idx_entities_type
ON evidence_entities(entity_type);

CREATE INDEX IF NOT EXISTS idx_entities_value
ON evidence_entities(entity_value);

CREATE INDEX IF NOT EXISTS idx_entities_normalized
ON evidence_entities(normalized_value);