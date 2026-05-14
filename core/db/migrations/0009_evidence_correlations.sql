CREATE TABLE IF NOT EXISTS evidence_correlations (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    run_id TEXT,

    source_evidence_id TEXT NOT NULL,

    target_evidence_id TEXT NOT NULL,

    correlation_type TEXT NOT NULL,

    correlation_value TEXT,

    confidence TEXT DEFAULT 'HIGH',

    created_at_ms INTEGER,

    metadata_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_corr_source
ON evidence_correlations(source_evidence_id);

CREATE INDEX IF NOT EXISTS idx_corr_target
ON evidence_correlations(target_evidence_id);

CREATE INDEX IF NOT EXISTS idx_corr_type
ON evidence_correlations(correlation_type);

CREATE INDEX IF NOT EXISTS idx_corr_value
ON evidence_correlations(correlation_value);