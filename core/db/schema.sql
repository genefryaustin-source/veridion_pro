-- ====================================
-- VERIDION PRO CANONICAL SCHEMA
-- AUTO-GENERATED FROM LIVE DATABASE
-- ====================================

-- TABLE: alert_evidence
CREATE TABLE alert_evidence (
    alert_id INTEGER,
    evidence_id TEXT,
    PRIMARY KEY (alert_id, evidence_id)
);

-- TABLE: alert_settings
CREATE TABLE alert_settings (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    slack_enabled INTEGER DEFAULT 0,
                    slack_webhook_url TEXT,
                    email_enabled INTEGER DEFAULT 0,
                    email_to TEXT,
                    min_severity TEXT DEFAULT 'CRITICAL',
                    updated_at_ms INTEGER
                );

-- TABLE: alerts
CREATE TABLE alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    evidence_id TEXT,
                    severity TEXT,
                    message TEXT,
                    created_at_ms INTEGER,
                    resolved INTEGER DEFAULT 0
                , status TEXT DEFAULT 'OPEN', priority TEXT DEFAULT 'MEDIUM', case_id TEXT, risk_score REAL DEFAULT 0, category TEXT, details_json TEXT, location TEXT, notes TEXT, source_name TEXT, detection_json TEXT);

-- TABLE: attachments
CREATE TABLE attachments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT,
                    filename TEXT,
                    mime_type TEXT,
                    size_bytes INTEGER,
                    storage_path TEXT,
                    extracted_text TEXT,
                    created_at TEXT
                );

-- TABLE: case_alert_map
CREATE TABLE case_alert_map (
    case_id INTEGER,
    alert_id INTEGER
);

-- TABLE: case_alerts
CREATE TABLE case_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT,
    alert_id INTEGER
);

-- TABLE: case_audit_log
CREATE TABLE case_audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id INTEGER,
                    action TEXT,
                    performed_by TEXT,
                    details TEXT,
                    created_at_ms INTEGER
                );

-- TABLE: case_events
CREATE TABLE case_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT,
    event_type TEXT,
    message TEXT,
    created_at_ms INTEGER
, actor TEXT, details_json TEXT);

-- TABLE: case_evidence
CREATE TABLE case_evidence (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id TEXT,
                    evidence_id TEXT
                , linked_at_ms INTEGER);

-- TABLE: case_evidence_map
CREATE TABLE case_evidence_map (
    case_id TEXT,
    evidence_id TEXT,
    UNIQUE(case_id, evidence_id)
);

-- TABLE: case_notes
CREATE TABLE case_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id TEXT,
                    note TEXT,
                    created_at_ms INTEGER
                );

-- TABLE: case_risk_history
CREATE TABLE case_risk_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT,
    risk_score INTEGER,
    alert_count INTEGER,
    critical_count INTEGER,
    created_at_ms INTEGER
);

-- TABLE: case_timeline
CREATE TABLE case_timeline (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id INTEGER,
    event_type TEXT,
    message TEXT,
    created_at_ms INTEGER
, ts INTEGER, label TEXT, actor TEXT, details TEXT);

-- TABLE: cases
CREATE TABLE cases (
                    case_id TEXT PRIMARY KEY,
                    title TEXT,
                    description TEXT,
                    status TEXT,
                    created_at_ms INTEGER
                , job_id INTEGER, assigned_to TEXT, priority TEXT, sla_due_ms INTEGER, assigned_at_ms INTEGER, assigned_by TEXT, escalated_at_ms INTEGER, updated_at_ms INTEGER, category TEXT, source TEXT, sender TEXT, subject TEXT, attachment_sha TEXT);

-- TABLE: custody_events
CREATE TABLE custody_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL REFERENCES runs(run_id),
                    evidence_id TEXT NOT NULL REFERENCES evidence_records(evidence_id),
                    event_type TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    timestamp_ms INTEGER NOT NULL,
                    details_json TEXT
                );

-- TABLE: emails
CREATE TABLE emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT UNIQUE,
                    thread_id TEXT,
                    mailbox TEXT,
                    subject TEXT,
                    sender TEXT,
                    received_at TEXT,
                    snippet TEXT,
                    body_text TEXT,
                    body_html TEXT,
                    raw_headers TEXT,
                    has_attachments INTEGER,
                    created_at TEXT
                );

-- TABLE: evidence_events
CREATE TABLE evidence_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    evidence_id TEXT NOT NULL,
    run_id TEXT,

    event_type TEXT NOT NULL,

    created_at_ms INTEGER NOT NULL,

    data_json TEXT,

    FOREIGN KEY (evidence_id) REFERENCES evidence_records(evidence_id),
    FOREIGN KEY (run_id) REFERENCES runs(run_id)
);

-- TABLE: evidence_records
CREATE TABLE evidence_records (
                    evidence_id TEXT PRIMARY KEY,
                    sha256 TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    content_type TEXT NOT NULL,
                    storage_uri TEXT NOT NULL,
                    suggested_name TEXT NOT NULL,
                    created_at_ms INTEGER NOT NULL,
                    metadata_json TEXT NOT NULL
                , run_id TEXT);

-- TABLE: forensic_anchors
CREATE TABLE forensic_anchors (
                    anchor_id TEXT PRIMARY KEY,
                    anchor_type TEXT NOT NULL,      -- SNAPSHOT | EVIDENCE | RUN
                    target_id TEXT NOT NULL,        -- snapshot path / evidence_id / run_id
                    hash_sha256 TEXT NOT NULL,
                    metadata_json TEXT,
                    created_at_ms INTEGER NOT NULL
                );

-- TABLE: heartbeats
CREATE TABLE "heartbeats" (
    worker_id TEXT PRIMARY KEY,
    status TEXT,
    ts_ms INTEGER,
    details_json TEXT
);

-- TABLE: manifests
CREATE TABLE manifests (
                    run_id TEXT PRIMARY KEY REFERENCES runs(run_id),
                    manifest_json TEXT NOT NULL,
                    manifest_sha256 TEXT NOT NULL,
                    created_at_ms INTEGER NOT NULL
                );

-- TABLE: metrics
CREATE TABLE metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    ts_ms INTEGER NOT NULL,
                    tags_json TEXT
                );

-- TABLE: oauth_tokens
CREATE TABLE oauth_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider TEXT NOT NULL,
    mailbox TEXT NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    token_uri TEXT,
    client_id TEXT,
    client_secret TEXT,
    scopes TEXT,
    expiry_ts INTEGER,
    created_at_ms INTEGER,
    updated_at_ms INTEGER,
    UNIQUE(provider, mailbox)
);

-- TABLE: processed_messages
CREATE TABLE processed_messages (
    provider TEXT,
    uid TEXT,
    PRIMARY KEY (provider, uid)
);

-- TABLE: processing_queue
CREATE TABLE processing_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider TEXT,
    mailbox TEXT,
    lookback_hours INTEGER,
    attachments_only INTEGER,
    max_messages INTEGER,
    payload_json TEXT,
    status TEXT,
    worker_id TEXT,
    created_at_ms INTEGER,
    started_at_ms INTEGER,
    completed_at_ms INTEGER,
    error TEXT
, attempts INTEGER DEFAULT 0, next_attempt_ms INTEGER DEFAULT 0, last_error TEXT, updated_at_ms INTEGER, run_id TEXT, progress_current INTEGER DEFAULT 0, progress_total INTEGER DEFAULT 1, duration_ms INTEGER);

-- TABLE: response_actions
CREATE TABLE response_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT,
    action_type TEXT,
    status TEXT,
    actor TEXT,
    details_json TEXT,
    created_at_ms INTEGER
);

-- TABLE: response_approvals
CREATE TABLE response_approvals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id TEXT NOT NULL,
    action_type TEXT NOT NULL,
    requested_by TEXT NOT NULL,
    approved_by TEXT,
    status TEXT NOT NULL,
    details_json TEXT,
    created_at_ms INTEGER,
    updated_at_ms INTEGER
);

-- TABLE: response_playbooks
CREATE TABLE response_playbooks (
    playbook_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    steps_json TEXT NOT NULL,
    created_at_ms INTEGER
);

-- TABLE: retry_policy
CREATE TABLE retry_policy (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    max_attempts INTEGER NOT NULL DEFAULT 5,
                    base_delay_seconds INTEGER NOT NULL DEFAULT 30,
                    max_delay_seconds INTEGER NOT NULL DEFAULT 21600,
                    jitter_seconds INTEGER NOT NULL DEFAULT 10,
                    updated_at_ms INTEGER NOT NULL
                );

-- TABLE: runs
CREATE TABLE runs (
                    run_id TEXT PRIMARY KEY,
                    provider TEXT NOT NULL,
                    mailbox TEXT NOT NULL,
                    started_at_ms INTEGER NOT NULL,
                    completed_at_ms INTEGER,
                    messages_scanned INTEGER DEFAULT 0,
                    attachments_scanned INTEGER DEFAULT 0,
                    cui_flagged INTEGER DEFAULT 0
                );

-- TABLE: scan_queue
CREATE TABLE scan_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider TEXT NOT NULL,
                    mailbox TEXT NOT NULL,
                    lookback_hours INTEGER NOT NULL,
                    attachments_only INTEGER NOT NULL,
                    max_messages INTEGER NOT NULL,
                    payload_json TEXT,
                    status TEXT NOT NULL DEFAULT 'queued',
                    attempts INTEGER NOT NULL DEFAULT 0,
                    next_attempt_ms INTEGER NOT NULL DEFAULT 0,
                    last_error TEXT,
                    created_at_ms INTEGER NOT NULL,
                    updated_at_ms INTEGER NOT NULL,
                    run_id TEXT
                , started_at_ms INTEGER, completed_at_ms INTEGER, duration_ms INTEGER, progress_current INTEGER DEFAULT 0, progress_total INTEGER DEFAULT 1);

-- TABLE: schema_migrations
CREATE TABLE schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at_ms INTEGER NOT NULL
);

-- TABLE: supervisor_config
CREATE TABLE supervisor_config (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    enabled INTEGER NOT NULL DEFAULT 1,
                    interval_seconds INTEGER NOT NULL DEFAULT 60,
                    updated_at_ms INTEGER NOT NULL
                );

-- TABLE: supervisor_events
CREATE TABLE supervisor_events
                (
                    id
                    INTEGER
                    PRIMARY
                    KEY
                    AUTOINCREMENT,
                    event_type
                    TEXT
                    NOT
                    NULL, -- e.g. LEADER_STALE, LOCK_CLEARED
                    leader_id
                    TEXT,
                    details_json
                    TEXT,
                    created_at_ms
                    INTEGER
                    NOT
                    NULL
                );

-- TABLE: supervisor_heartbeat
CREATE TABLE supervisor_heartbeat (
                    worker_id TEXT PRIMARY KEY,
                    leader_id TEXT,
                    status TEXT NOT NULL DEFAULT 'idle',
                    last_seen_ms INTEGER NOT NULL,
                    details_json TEXT,
                    timestamp_ms INTEGER
                );

-- TABLE: supervisor_lock
CREATE TABLE supervisor_lock (
                    lock_name TEXT PRIMARY KEY,
                    leader_id TEXT NOT NULL,
                    acquired_at_ms INTEGER NOT NULL,
                    expires_at_ms INTEGER NOT NULL
                );

-- TABLE: supervisor_locks
CREATE TABLE supervisor_locks (
    lock_name TEXT PRIMARY KEY,
    leader_id TEXT,
    expires_at_ms INTEGER
);

-- TABLE: task_queue
CREATE TABLE task_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_type TEXT,
    payload_json TEXT,
    status TEXT DEFAULT 'QUEUED',
    created_at_ms INTEGER,
    started_at_ms INTEGER,
    completed_at_ms INTEGER
, priority INTEGER DEFAULT 5, attempts INTEGER DEFAULT 0, max_attempts INTEGER DEFAULT 3, last_error TEXT, available_at_ms INTEGER DEFAULT 0);

-- TABLE: ui_debug_log
CREATE TABLE ui_debug_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at_ms INTEGER,
                    message TEXT
                );

-- TABLE: worker_events
CREATE TABLE worker_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    worker_name TEXT,
                    event_type TEXT,
                    message TEXT,
                    task_id INTEGER,
                    job_id INTEGER,
                    created_at_ms INTEGER
                );

-- INDEX: idx_alert_unique
CREATE UNIQUE INDEX idx_alert_unique
ON alerts (evidence_id, severity);

-- INDEX: idx_alerts_time
CREATE INDEX idx_alerts_time
                ON alerts(created_at_ms);

-- INDEX: idx_custody_events_evidence_id
CREATE INDEX idx_custody_events_evidence_id ON custody_events(evidence_id);

-- INDEX: idx_custody_events_run_id
CREATE INDEX idx_custody_events_run_id ON custody_events(run_id);

-- INDEX: idx_custody_evidence
CREATE INDEX idx_custody_evidence
                    ON custody_events(evidence_id);

-- INDEX: idx_custody_run
CREATE INDEX idx_custody_run
                    ON custody_events(run_id);

-- INDEX: idx_forensic_anchors_target
CREATE INDEX idx_forensic_anchors_target
                    ON forensic_anchors(target_id);

-- INDEX: idx_forensic_anchors_type_time
CREATE INDEX idx_forensic_anchors_type_time
                    ON forensic_anchors(anchor_type, created_at_ms);

-- INDEX: idx_metrics_name_ts
CREATE INDEX idx_metrics_name_ts
                    ON metrics(name, ts_ms);

-- INDEX: idx_scan_queue_status
CREATE INDEX idx_scan_queue_status
ON scan_queue(status);

-- INDEX: idx_scan_queue_status_next
CREATE INDEX idx_scan_queue_status_next
                    ON scan_queue(status, next_attempt_ms);

-- INDEX: idx_supervisor_heartbeat_last_seen
CREATE INDEX idx_supervisor_heartbeat_last_seen
                ON supervisor_heartbeat(last_seen_ms);

-- INDEX: idx_supervisor_heartbeat_ts
CREATE INDEX idx_supervisor_heartbeat_ts
                    ON supervisor_heartbeat(last_seen_ms);

-- TRIGGER: trg_events_no_delete
CREATE TRIGGER trg_events_no_delete
                    BEFORE DELETE ON custody_events
                    BEGIN
                        SELECT RAISE(ABORT, 'IMMUTABLE_LEDGER: custody_events are append-only');
                    END;

-- TRIGGER: trg_events_no_update
CREATE TRIGGER trg_events_no_update
                    BEFORE UPDATE ON custody_events
                    BEGIN
                        SELECT RAISE(ABORT, 'IMMUTABLE_LEDGER: custody_events are append-only');
                    END;

-- TRIGGER: trg_evidence_no_delete
CREATE TRIGGER trg_evidence_no_delete
                    BEFORE DELETE ON evidence_records
                    BEGIN
                        SELECT RAISE(ABORT, 'IMMUTABLE_LEDGER: evidence_records are append-only');
                    END;

-- TRIGGER: trg_evidence_no_update
CREATE TRIGGER trg_evidence_no_update
                    BEFORE UPDATE ON evidence_records
                    BEGIN
                        SELECT RAISE(ABORT, 'IMMUTABLE_LEDGER: evidence_records are append-only');
                    END;

-- TRIGGER: trg_manifests_no_delete
CREATE TRIGGER trg_manifests_no_delete
                    BEFORE DELETE ON manifests
                    BEGIN
                        SELECT RAISE(ABORT, 'IMMUTABLE_LEDGER: manifests are write-once');
                    END;

-- TRIGGER: trg_manifests_no_update
CREATE TRIGGER trg_manifests_no_update
                    BEFORE UPDATE ON manifests
                    BEGIN
                        SELECT RAISE(ABORT, 'IMMUTABLE_LEDGER: manifests are write-once');
                    END;

-- TRIGGER: trg_no_delete_forensic_anchors
CREATE TRIGGER trg_no_delete_forensic_anchors
                    BEFORE DELETE ON forensic_anchors
                    BEGIN
                        SELECT RAISE(ABORT, 'IMMUTABLE_LEDGER: forensic_anchors are append-only');
                    END;

-- TRIGGER: trg_no_update_forensic_anchors
CREATE TRIGGER trg_no_update_forensic_anchors
                    BEFORE UPDATE ON forensic_anchors
                    BEGIN
                        SELECT RAISE(ABORT, 'IMMUTABLE_LEDGER: forensic_anchors are append-only');
                    END;

-- TRIGGER: trg_runs_no_delete
CREATE TRIGGER trg_runs_no_delete
                    BEFORE DELETE ON runs
                    BEGIN
                        SELECT RAISE(ABORT, 'IMMUTABLE_LEDGER: runs are append-only');
                    END;

-- TRIGGER: trg_runs_no_update
CREATE TRIGGER trg_runs_no_update
                    BEFORE UPDATE ON runs
                    BEGIN
                        SELECT RAISE(ABORT, 'IMMUTABLE_LEDGER: runs are append-only');
                    END;
