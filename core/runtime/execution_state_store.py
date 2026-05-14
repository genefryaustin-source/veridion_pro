"""
core/runtime/execution_state_store.py

Thread-safe execution and rollback state store.
"""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from typing import Any, Dict, List, Optional


STATUS_PENDING = "PENDING"
STATUS_RUNNING = "RUNNING"
STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED = "FAILED"


def _now_ms() -> int:
    return int(time.time() * 1000)


def _json_dumps(value: Any) -> str:
    try:
        return json.dumps(value or {}, default=str)
    except Exception:
        return "{}"


def _json_loads(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return value
    try:
        parsed = json.loads(value or "{}")
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def _get_ledger(storage_or_ledger: Any) -> Any:
    if storage_or_ledger is None:
        return None
    return getattr(storage_or_ledger, "ledger", storage_or_ledger)


class ExecutionStateStore:
    def __init__(self, storage: Any = None) -> None:
        self.storage = storage
        self.ledger = _get_ledger(storage)
        self.db_path = self._resolve_db_path()
        self.ensure_schema()

    def _resolve_db_path(self) -> str:
        ledger = self.ledger

        if ledger is not None:
            for attr in ("db_path", "database_path", "path", "_db_path"):
                path = getattr(ledger, attr, None)
                if path:
                    return path

        if isinstance(self.storage, str):
            return self.storage

        return "data/ledger.db"

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            timeout=30,
        )

        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
            conn.execute("PRAGMA foreign_keys=ON;")
        except Exception:
            pass

        return conn

    def ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS execution_states (
                    execution_id TEXT PRIMARY KEY,
                    tenant_id TEXT DEFAULT 'default',
                    status TEXT,
                    action TEXT,
                    connector_id TEXT,
                    case_id TEXT,
                    alert_id TEXT,
                    evidence_id TEXT,
                    payload_json TEXT,
                    result_json TEXT,
                    details_json TEXT,
                    last_error TEXT,
                    created_at_ms INTEGER NOT NULL,
                    updated_at_ms INTEGER NOT NULL,
                    completed_at_ms INTEGER
                )
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS rollback_chains (
                    rollback_id TEXT PRIMARY KEY,
                    execution_id TEXT,
                    tenant_id TEXT DEFAULT 'default',
                    status TEXT,
                    attempts INTEGER DEFAULT 0,
                    payload_json TEXT,
                    details_json TEXT,
                    last_error TEXT,
                    escalation_reason TEXT,
                    created_at_ms INTEGER NOT NULL,
                    updated_at_ms INTEGER NOT NULL,
                    completed_at_ms INTEGER
                )
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_execution_states_status
                ON execution_states(status)
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_rollback_chains_status
                ON rollback_chains(status)
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_rollback_chains_execution
                ON rollback_chains(execution_id)
                """
            )

            conn.commit()

    # ---------------------------------------------------------
    # EXECUTION STATE
    # ---------------------------------------------------------

    def create_execution(
        self,
        *,
        execution_id: Optional[str] = None,
        tenant_id: str = "default",
        action: Optional[str] = None,
        connector_id: Optional[str] = None,
        case_id: Optional[Any] = None,
        alert_id: Optional[Any] = None,
        evidence_id: Optional[Any] = None,
        payload: Optional[Dict[str, Any]] = None,
        status: str = STATUS_PENDING,
    ) -> str:
        execution_id = execution_id or f"EXE-{uuid.uuid4().hex[:12].upper()}"
        now = _now_ms()

        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO execution_states (
                    execution_id,
                    tenant_id,
                    status,
                    action,
                    connector_id,
                    case_id,
                    alert_id,
                    evidence_id,
                    payload_json,
                    result_json,
                    details_json,
                    last_error,
                    created_at_ms,
                    updated_at_ms,
                    completed_at_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    execution_id,
                    tenant_id or "default",
                    status,
                    action,
                    connector_id,
                    str(case_id) if case_id is not None else None,
                    str(alert_id) if alert_id is not None else None,
                    str(evidence_id) if evidence_id is not None else None,
                    _json_dumps(payload),
                    "{}",
                    "{}",
                    None,
                    now,
                    now,
                    None,
                ),
            )
            conn.commit()

        return execution_id

    def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM execution_states
                WHERE execution_id=?
                LIMIT 1
                """,
                (execution_id,),
            ).fetchone()

            if not row:
                return None

            cols = self._table_cols(conn, "execution_states")

        return dict(zip(cols, row))

    def update_execution(
        self,
        *,
        execution_id: str,
        status: Optional[str] = None,
        result: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None,
        last_error: Optional[str] = None,
        completed_at_ms: Optional[int] = None,
    ) -> bool:
        current = self.get_execution(execution_id)
        if not current:
            return False

        new_status = status or current.get("status")
        now = _now_ms()

        with self._connect() as conn:
            conn.execute(
                """
                UPDATE execution_states
                SET status=?,
                    result_json=?,
                    details_json=?,
                    last_error=?,
                    updated_at_ms=?,
                    completed_at_ms=?
                WHERE execution_id=?
                """,
                (
                    new_status,
                    _json_dumps(result) if result is not None else current.get("result_json") or "{}",
                    _json_dumps(details) if details is not None else current.get("details_json") or "{}",
                    last_error if last_error is not None else current.get("last_error"),
                    now,
                    completed_at_ms,
                    execution_id,
                ),
            )
            conn.commit()

        return True

    # ---------------------------------------------------------
    # ROLLBACK CHAINS
    # ---------------------------------------------------------

    def create_rollback_chain(
        self,
        *,
        rollback_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        tenant_id: str = "default",
        payload: Optional[Dict[str, Any]] = None,
        status: str = "READY",
        attempts: int = 0,
        details: Optional[Dict[str, Any]] = None,
    ) -> str:
        rollback_id = rollback_id or f"RB-{uuid.uuid4().hex[:12].upper()}"
        now = _now_ms()

        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO rollback_chains (
                    rollback_id,
                    execution_id,
                    tenant_id,
                    status,
                    attempts,
                    payload_json,
                    details_json,
                    last_error,
                    escalation_reason,
                    created_at_ms,
                    updated_at_ms,
                    completed_at_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    rollback_id,
                    execution_id,
                    tenant_id or "default",
                    status,
                    int(attempts),
                    _json_dumps(payload),
                    _json_dumps(details),
                    None,
                    None,
                    now,
                    now,
                    None,
                ),
            )
            conn.commit()

        return rollback_id

    def get_rollback_chain(self, rollback_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM rollback_chains
                WHERE rollback_id=?
                LIMIT 1
                """,
                (rollback_id,),
            ).fetchone()

            if not row:
                return None

            cols = self._table_cols(conn, "rollback_chains")

        return dict(zip(cols, row))

    def update_rollback_chain(
        self,
        *,
        rollback_id: str,
        status: Optional[str] = None,
        attempts: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        last_error: Optional[str] = None,
        escalation_reason: Optional[str] = None,
        completed_at_ms: Optional[int] = None,
    ) -> bool:
        current = self.get_rollback_chain(rollback_id)
        if not current:
            return False

        with self._connect() as conn:
            conn.execute(
                """
                UPDATE rollback_chains
                SET status=?,
                    attempts=?,
                    details_json=?,
                    last_error=?,
                    escalation_reason=?,
                    updated_at_ms=?,
                    completed_at_ms=?
                WHERE rollback_id=?
                """,
                (
                    status or current.get("status"),
                    int(attempts if attempts is not None else current.get("attempts") or 0),
                    _json_dumps(details) if details is not None else current.get("details_json") or "{}",
                    last_error if last_error is not None else current.get("last_error"),
                    escalation_reason if escalation_reason is not None else current.get("escalation_reason"),
                    _now_ms(),
                    completed_at_ms if completed_at_ms is not None else current.get("completed_at_ms"),
                    rollback_id,
                ),
            )
            conn.commit()

        return True

    def list_failed_rollbacks(
        self,
        *,
        max_attempts: int = 3,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM rollback_chains
                WHERE status=?
                  AND attempts < ?
                ORDER BY updated_at_ms ASC
                LIMIT ?
                """,
                (
                    STATUS_FAILED,
                    int(max_attempts),
                    int(limit),
                ),
            ).fetchall()

            cols = self._table_cols(conn, "rollback_chains")

        return [dict(zip(cols, row)) for row in rows]

    def list_rollback_chains(
        self,
        *,
        status: Optional[str] = None,
        limit: int = 250,
    ) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            if status:
                rows = conn.execute(
                    """
                    SELECT *
                    FROM rollback_chains
                    WHERE status=?
                    ORDER BY updated_at_ms DESC
                    LIMIT ?
                    """,
                    (status, int(limit)),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT *
                    FROM rollback_chains
                    ORDER BY updated_at_ms DESC
                    LIMIT ?
                    """,
                    (int(limit),),
                ).fetchall()

            cols = self._table_cols(conn, "rollback_chains")

        return [dict(zip(cols, row)) for row in rows]

    def _table_cols(
        self,
        conn: sqlite3.Connection,
        table_name: str,
    ) -> List[str]:
        return [
            d[1]
            for d in conn.execute(
                f"PRAGMA table_info({table_name})"
            ).fetchall()
        ]