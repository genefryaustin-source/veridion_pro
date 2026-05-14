# core/db/schema_validator.py

import json
import sqlite3
import time
from typing import Dict, List


def _now_ms() -> int:
    return int(time.time() * 1000)


REQUIRED_TABLES: Dict[str, List[str]] = {
    "schema_migrations": [
        "version",
        "filename",
        "checksum",
        "applied_at_ms",
    ],
    "schema_validation_log": [
        "id",
        "created_at_ms",
        "level",
        "message",
        "details_json",
    ],
    "oauth_tokens": [],
    "scan_queue": [],
    "processing_queue": [],
    "runs": [],
    "evidence_records": [],
    "evidence_events": [],
    "custody_events": [],
    "alerts": [],
    "cases": [],
    "case_timeline": [],
    "case_evidence_map": [],
    "worker_events": [],
}


SAFE_COLUMN_PATCHES = {
    ("alerts", "status"): "ALTER TABLE alerts ADD COLUMN status TEXT DEFAULT 'OPEN'",
    ("alerts", "resolved"): "ALTER TABLE alerts ADD COLUMN resolved INTEGER DEFAULT 0",
    ("alerts", "category"): "ALTER TABLE alerts ADD COLUMN category TEXT",
    ("alerts", "location"): "ALTER TABLE alerts ADD COLUMN location TEXT",
    ("alerts", "notes"): "ALTER TABLE alerts ADD COLUMN notes TEXT",
    ("alerts", "source_name"): "ALTER TABLE alerts ADD COLUMN source_name TEXT",
    ("alerts", "detection_json"): "ALTER TABLE alerts ADD COLUMN detection_json TEXT",

    ("scan_queue", "progress_current"): "ALTER TABLE scan_queue ADD COLUMN progress_current INTEGER DEFAULT 0",
    ("scan_queue", "progress_total"): "ALTER TABLE scan_queue ADD COLUMN progress_total INTEGER DEFAULT 0",
    ("scan_queue", "started_at_ms"): "ALTER TABLE scan_queue ADD COLUMN started_at_ms INTEGER",
    ("scan_queue", "completed_at_ms"): "ALTER TABLE scan_queue ADD COLUMN completed_at_ms INTEGER",
    ("scan_queue", "duration_ms"): "ALTER TABLE scan_queue ADD COLUMN duration_ms INTEGER",

    ("processing_queue", "progress_current"): "ALTER TABLE processing_queue ADD COLUMN progress_current INTEGER DEFAULT 0",
    ("processing_queue", "progress_total"): "ALTER TABLE processing_queue ADD COLUMN progress_total INTEGER DEFAULT 0",
    ("processing_queue", "started_at_ms"): "ALTER TABLE processing_queue ADD COLUMN started_at_ms INTEGER",
    ("processing_queue", "completed_at_ms"): "ALTER TABLE processing_queue ADD COLUMN completed_at_ms INTEGER",
    ("processing_queue", "duration_ms"): "ALTER TABLE processing_queue ADD COLUMN duration_ms INTEGER",
}


IMMUTABLE_TRIGGERS = [
    "trg_events_no_delete",
    "trg_events_no_update",
    "trg_evidence_no_delete",
    "trg_evidence_no_update",
    "trg_runs_no_delete",
    "trg_runs_no_update",
]


def _table_exists(con, table: str) -> bool:
    row = con.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name=?
    """, (table,)).fetchone()

    return row is not None


def _trigger_exists(con, trigger: str) -> bool:
    row = con.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='trigger'
        AND name=?
    """, (trigger,)).fetchone()

    return row is not None


def _columns(con, table: str) -> List[str]:
    rows = con.execute(f'PRAGMA table_info("{table}")').fetchall()
    return [r[1] for r in rows]


def _log(con, level: str, message: str, details=None):
    try:
        con.execute("""
            INSERT INTO schema_validation_log (
                created_at_ms,
                level,
                message,
                details_json
            )
            VALUES (?, ?, ?, ?)
        """, (
            _now_ms(),
            level,
            message,
            json.dumps(details or {}, default=str),
        ))
    except Exception:
        pass


def validate_schema(db_path: str, auto_patch: bool = True) -> dict:
    report = {
        "missing_tables": [],
        "missing_columns": [],
        "patched_columns": [],
        "missing_triggers": [],
        "warnings": [],
    }

    with sqlite3.connect(db_path) as con:
        con.execute("PRAGMA foreign_keys = ON;")

        for table, required_columns in REQUIRED_TABLES.items():
            if not _table_exists(con, table):
                report["missing_tables"].append(table)
                _log(con, "ERROR", f"Missing required table: {table}")
                continue

            existing_columns = _columns(con, table)

            for col in required_columns:
                if col not in existing_columns:
                    report["missing_columns"].append({
                        "table": table,
                        "column": col,
                    })

        for (table, column), sql in SAFE_COLUMN_PATCHES.items():
            if not _table_exists(con, table):
                continue

            existing_columns = _columns(con, table)

            if column not in existing_columns:
                if auto_patch:
                    print(f"🩹 Patching missing column: {table}.{column}")
                    con.execute(sql)
                    report["patched_columns"].append({
                        "table": table,
                        "column": column,
                    })
                    _log(con, "WARN", f"Auto patched missing column {table}.{column}")
                else:
                    report["missing_columns"].append({
                        "table": table,
                        "column": column,
                    })

        for trigger in IMMUTABLE_TRIGGERS:
            if not _trigger_exists(con, trigger):
                report["missing_triggers"].append(trigger)
                _log(con, "CRITICAL", f"Missing immutable trigger: {trigger}")

        con.commit()

    return report