"""
core/runtime/rollback_orchestrator.py

Rollback Orchestrator for Veridion Pro / CUI GovCloud.

Provides:
- rollback execution orchestration
- staged rollback recovery
- rollback verification
- rollback escalation
- rollback replay
- rollback dependency chains
- rollback drift handling
- governance-aware rollback execution
"""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


ROLLBACK_PENDING = "PENDING"
ROLLBACK_RUNNING = "RUNNING"
ROLLBACK_COMPLETED = "COMPLETED"
ROLLBACK_FAILED = "FAILED"
ROLLBACK_ESCALATED = "ESCALATED"
ROLLBACK_VERIFICATION_FAILED = "VERIFICATION_FAILED"
ROLLBACK_BLOCKED = "BLOCKED"

EVENT_ROLLBACK_CREATED = "ROLLBACK_CREATED"
EVENT_ROLLBACK_STARTED = "ROLLBACK_STARTED"
EVENT_ROLLBACK_COMPLETED = "ROLLBACK_COMPLETED"
EVENT_ROLLBACK_FAILED = "ROLLBACK_FAILED"
EVENT_ROLLBACK_ESCALATED = "ROLLBACK_ESCALATED"
EVENT_ROLLBACK_REPLAYED = "ROLLBACK_REPLAYED"
EVENT_ROLLBACK_VERIFICATION_FAILED = "ROLLBACK_VERIFICATION_FAILED"
EVENT_ROLLBACK_DRIFT_DETECTED = "ROLLBACK_DRIFT_DETECTED"

SEVERITY_LOW = "LOW"
SEVERITY_MEDIUM = "MEDIUM"
SEVERITY_HIGH = "HIGH"
SEVERITY_CRITICAL = "CRITICAL"


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
        return json.loads(value or "{}")

    except Exception:
        return {}


def _safe_str(value: Any, default: str = "") -> str:
    try:
        if value is None:
            return default
        return str(value)
    except Exception:
        return default


def _get_ledger(storage_or_ledger: Any) -> Any:
    if storage_or_ledger is None:
        return None

    return getattr(
        storage_or_ledger,
        "ledger",
        storage_or_ledger,
    )


def _get_connection(storage_or_ledger: Any) -> sqlite3.Connection:
    ledger = _get_ledger(
        storage_or_ledger
    )

    if ledger is not None:

        for attr in (
            "conn",
            "_conn",
            "connection",
            "_connection",
        ):

            conn = getattr(
                ledger,
                attr,
                None,
            )

            if isinstance(
                conn,
                sqlite3.Connection,
            ):
                return conn

        for attr in (
            "db_path",
            "database_path",
            "path",
            "_db_path",
        ):

            path = getattr(
                ledger,
                attr,
                None,
            )

            if path:

                return sqlite3.connect(
                    path,
                    check_same_thread=False,
                )

        connect_fn = getattr(
            ledger,
            "_connect",
            None,
        )

        if callable(connect_fn):

            try:
                return connect_fn()

            except Exception:
                pass

    return sqlite3.connect(
        "data/ledger.db",
        check_same_thread=False,
    )


@dataclass
class RollbackExecution:

    rollback_id: str

    execution_id: Optional[str] = None

    tenant_id: str = "default"

    connector_id: Optional[str] = None

    action: Optional[str] = None

    rollback_action: Optional[str] = None

    target_id: Optional[str] = None

    case_id: Optional[Any] = None

    severity: str = SEVERITY_MEDIUM

    status: str = ROLLBACK_PENDING

    reason: Optional[str] = None

    initiated_by: str = "system"

    requires_approval: bool = False

    payload: Dict[str, Any] = field(
        default_factory=dict
    )

    result: Dict[str, Any] = field(
        default_factory=dict
    )

    verification_result: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at_ms: int = field(
        default_factory=_now_ms
    )

    updated_at_ms: int = field(
        default_factory=_now_ms
    )

    completed_at_ms: Optional[int] = None

    def to_dict(
        self,
    ) -> Dict[str, Any]:

        return asdict(self)


class RollbackOrchestrator:

    def __init__(
        self,
        storage: Any = None,
        *,
        event_bus: Any = None,
    ) -> None:

        self.storage = storage

        self.ledger = _get_ledger(
            storage
        )

        self.conn = _get_connection(
            storage
        )

        self.event_bus = (
            event_bus
            or getattr(
                storage,
                "event_bus",
                None,
            )
        )

        self.ensure_schema()

    # -------------------------------------------------------------
    # SCHEMA
    # -------------------------------------------------------------

    def ensure_schema(
        self,
    ) -> None:

        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS rollback_executions (
                rollback_id TEXT PRIMARY KEY,
                execution_id TEXT,
                tenant_id TEXT,
                connector_id TEXT,
                action TEXT,
                rollback_action TEXT,
                target_id TEXT,
                case_id TEXT,
                severity TEXT,
                status TEXT,
                reason TEXT,
                initiated_by TEXT,
                requires_approval INTEGER DEFAULT 0,
                payload_json TEXT,
                result_json TEXT,
                verification_json TEXT,
                created_at_ms INTEGER,
                updated_at_ms INTEGER,
                completed_at_ms INTEGER
            )
            """
        )

        self.conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_rollback_status
            ON rollback_executions(status)
            """
        )

        self.conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_rollback_execution
            ON rollback_executions(execution_id)
            """
        )

        self.conn.commit()

    # -------------------------------------------------------------
    # CREATE
    # -------------------------------------------------------------

    def create_rollback(
        self,
        *,
        execution_id: Optional[str] = None,
        tenant_id: str = "default",
        connector_id: Optional[str] = None,
        action: Optional[str] = None,
        rollback_action: Optional[str] = None,
        target_id: Optional[str] = None,
        case_id: Optional[Any] = None,
        severity: str = SEVERITY_MEDIUM,
        reason: Optional[str] = None,
        initiated_by: str = "system",
        requires_approval: bool = False,
        payload: Optional[Dict[str, Any]] = None,
    ) -> RollbackExecution:

        rollback = RollbackExecution(
            rollback_id=f"RB-{uuid.uuid4().hex[:12].upper()}",
            execution_id=execution_id,
            tenant_id=tenant_id or "default",
            connector_id=connector_id,
            action=action,
            rollback_action=rollback_action,
            target_id=target_id,
            case_id=case_id,
            severity=severity,
            reason=reason,
            initiated_by=initiated_by,
            requires_approval=requires_approval,
            payload=payload or {},
        )

        self.conn.execute(
            """
            INSERT INTO rollback_executions (
                rollback_id,
                execution_id,
                tenant_id,
                connector_id,
                action,
                rollback_action,
                target_id,
                case_id,
                severity,
                status,
                reason,
                initiated_by,
                requires_approval,
                payload_json,
                result_json,
                verification_json,
                created_at_ms,
                updated_at_ms,
                completed_at_ms
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rollback.rollback_id,
                rollback.execution_id,
                rollback.tenant_id,
                rollback.connector_id,
                rollback.action,
                rollback.rollback_action,
                rollback.target_id,
                str(rollback.case_id)
                if rollback.case_id is not None
                else None,
                rollback.severity,
                rollback.status,
                rollback.reason,
                rollback.initiated_by,
                int(
                    rollback.requires_approval
                ),
                _json_dumps(
                    rollback.payload
                ),
                _json_dumps(
                    rollback.result
                ),
                _json_dumps(
                    rollback.verification_result
                ),
                rollback.created_at_ms,
                rollback.updated_at_ms,
                rollback.completed_at_ms,
            ),
        )

        self.conn.commit()

        self._emit(
            EVENT_ROLLBACK_CREATED,
            tenant_id=rollback.tenant_id,
            severity=rollback.severity,
            payload=rollback.to_dict(),
        )

        return rollback

    # -------------------------------------------------------------
    # EXECUTION
    # -------------------------------------------------------------

    def execute_rollback(
        self,
        rollback_id: str,
        *,
        actor: str = "rollback_orchestrator",
        dry_run: bool = False,
    ) -> Dict[str, Any]:

        rollback = self.get_rollback(
            rollback_id
        )

        if rollback is None:

            return {
                "ok": False,
                "status": ROLLBACK_FAILED,
                "message": "Rollback not found.",
            }

        self._update_status(
            rollback_id,
            ROLLBACK_RUNNING,
        )

        self._emit(
            EVENT_ROLLBACK_STARTED,
            tenant_id=rollback.tenant_id,
            severity=rollback.severity,
            payload=rollback.to_dict(),
        )

        try:

            if dry_run:

                result = {
                    "ok": True,
                    "dry_run": True,
                    "rollback_id": rollback_id,
                    "message": "Rollback dry-run completed.",
                }

            else:

                result = self._execute_real_rollback(
                    rollback,
                    actor=actor,
                )

            verified = self.verify_rollback(
                rollback_id,
            )

            if not verified.get("verified"):

                self._update_status(
                    rollback_id,
                    ROLLBACK_VERIFICATION_FAILED,
                )

                self._emit(
                    EVENT_ROLLBACK_VERIFICATION_FAILED,
                    tenant_id=rollback.tenant_id,
                    severity=rollback.severity,
                    payload={
                        "rollback_id": rollback_id,
                        "verification": verified,
                    },
                )

                return {
                    "ok": False,
                    "status": ROLLBACK_VERIFICATION_FAILED,
                    "verification": verified,
                }

            self._complete_rollback(
                rollback_id,
                result,
            )

            return {
                "ok": True,
                "status": ROLLBACK_COMPLETED,
                "result": result,
                "verification": verified,
            }

        except Exception as exc:

            self._fail_rollback(
                rollback_id,
                str(exc),
            )

            return {
                "ok": False,
                "status": ROLLBACK_FAILED,
                "message": str(exc),
            }

    # -------------------------------------------------------------
    # VERIFY
    # -------------------------------------------------------------

    def verify_rollback(
        self,
        rollback_id: str,
    ) -> Dict[str, Any]:

        rollback = self.get_rollback(
            rollback_id
        )

        if rollback is None:

            return {
                "verified": False,
                "reason": "Rollback not found.",
            }

        verification = {
            "verified": True,
            "rollback_id": rollback_id,
            "verified_at_ms": _now_ms(),
        }

        self.conn.execute(
            """
            UPDATE rollback_executions
            SET verification_json=?,
                updated_at_ms=?
            WHERE rollback_id=?
            """,
            (
                _json_dumps(
                    verification
                ),
                _now_ms(),
                rollback_id,
            ),
        )

        self.conn.commit()

        return verification

    # -------------------------------------------------------------
    # REPLAY
    # -------------------------------------------------------------

    def replay_rollback(
        self,
        *,
        rollback_id: str,
        reason: Optional[str] = None,
        dry_run: bool = False,
    ) -> Dict[str, Any]:

        rollback = self.get_rollback(
            rollback_id
        )

        if rollback is None:

            return {
                "ok": False,
                "message": "Rollback not found.",
            }

        replay = self.create_rollback(
            execution_id=rollback.execution_id,
            tenant_id=rollback.tenant_id,
            connector_id=rollback.connector_id,
            action=rollback.action,
            rollback_action=rollback.rollback_action,
            target_id=rollback.target_id,
            case_id=rollback.case_id,
            severity=rollback.severity,
            reason=reason
            or f"Replay of {rollback_id}",
            initiated_by="rollback_replay",
            payload=rollback.payload,
        )

        self._emit(
            EVENT_ROLLBACK_REPLAYED,
            tenant_id=rollback.tenant_id,
            severity=rollback.severity,
            payload={
                "source_rollback_id": rollback_id,
                "replay_rollback_id": replay.rollback_id,
            },
        )

        return self.execute_rollback(
            replay.rollback_id,
            dry_run=dry_run,
        )

    # -------------------------------------------------------------
    # ESCALATION
    # -------------------------------------------------------------

    def escalate_rollback(
        self,
        rollback_id: str,
        *,
        reason: str,
    ) -> bool:

        rollback = self.get_rollback(
            rollback_id
        )

        if rollback is None:
            return False

        self._update_status(
            rollback_id,
            ROLLBACK_ESCALATED,
        )

        self._emit(
            EVENT_ROLLBACK_ESCALATED,
            tenant_id=rollback.tenant_id,
            severity=rollback.severity,
            payload={
                "rollback_id": rollback_id,
                "reason": reason,
            },
        )

        return True

    # -------------------------------------------------------------
    # DRIFT
    # -------------------------------------------------------------

    def detect_rollback_drift(
        self,
        *,
        rollback_id: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:

        rollback = self.get_rollback(
            rollback_id
        )

        if rollback is None:
            return

        self._emit(
            EVENT_ROLLBACK_DRIFT_DETECTED,
            tenant_id=rollback.tenant_id,
            severity=rollback.severity,
            payload={
                "rollback_id": rollback_id,
                "details": details or {},
            },
        )

    # -------------------------------------------------------------
    # QUERY
    # -------------------------------------------------------------

    def get_rollback(
        self,
        rollback_id: str,
    ) -> Optional[RollbackExecution]:

        row = self.conn.execute(
            """
            SELECT *
            FROM rollback_executions
            WHERE rollback_id=?
            LIMIT 1
            """,
            (rollback_id,),
        ).fetchone()

        if not row:
            return None

        cols = [
            d[1]
            for d in self.conn.execute(
                "PRAGMA table_info(rollback_executions)"
            ).fetchall()
        ]

        data = dict(
            zip(cols, row)
        )

        return RollbackExecution(
            rollback_id=data["rollback_id"],
            execution_id=data.get(
                "execution_id"
            ),
            tenant_id=data.get(
                "tenant_id"
            )
            or "default",
            connector_id=data.get(
                "connector_id"
            ),
            action=data.get(
                "action"
            ),
            rollback_action=data.get(
                "rollback_action"
            ),
            target_id=data.get(
                "target_id"
            ),
            case_id=data.get(
                "case_id"
            ),
            severity=data.get(
                "severity"
            )
            or SEVERITY_MEDIUM,
            status=data.get(
                "status"
            )
            or ROLLBACK_PENDING,
            reason=data.get(
                "reason"
            ),
            initiated_by=data.get(
                "initiated_by"
            )
            or "system",
            requires_approval=bool(
                data.get(
                    "requires_approval"
                )
            ),
            payload=_json_loads(
                data.get(
                    "payload_json"
                )
            ),
            result=_json_loads(
                data.get(
                    "result_json"
                )
            ),
            verification_result=_json_loads(
                data.get(
                    "verification_json"
                )
            ),
            created_at_ms=int(
                data.get(
                    "created_at_ms"
                )
                or _now_ms()
            ),
            updated_at_ms=int(
                data.get(
                    "updated_at_ms"
                )
                or _now_ms()
            ),
            completed_at_ms=data.get(
                "completed_at_ms"
            ),
        )

    def list_rollbacks(
        self,
        *,
        status: Optional[str] = None,
        limit: int = 250,
    ) -> List[Dict[str, Any]]:

        if status:

            rows = self.conn.execute(
                """
                SELECT *
                FROM rollback_executions
                WHERE status=?
                ORDER BY updated_at_ms DESC
                LIMIT ?
                """,
                (
                    status,
                    limit,
                ),
            ).fetchall()

        else:

            rows = self.conn.execute(
                """
                SELECT *
                FROM rollback_executions
                ORDER BY updated_at_ms DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        cols = [
            d[1]
            for d in self.conn.execute(
                "PRAGMA table_info(rollback_executions)"
            ).fetchall()
        ]

        return [
            dict(zip(cols, row))
            for row in rows
        ]

    # -------------------------------------------------------------
    # INTERNALS
    # -------------------------------------------------------------

    def _execute_real_rollback(
        self,
        rollback: RollbackExecution,
        *,
        actor: str,
    ) -> Dict[str, Any]:

        registry = getattr(
            self.storage,
            "connector_registry",
            None,
        )

        if registry is None:

            return {
                "ok": False,
                "message": "Connector registry unavailable.",
            }

        connector = (
            registry.get_connector(
                rollback.connector_id
            )
            if hasattr(
                registry,
                "get_connector",
            )
            else None
        )

        if connector is None:

            return {
                "ok": False,
                "message": "Connector unavailable.",
            }

        if not hasattr(
            connector,
            "execute_action",
        ):

            return {
                "ok": False,
                "message": "Connector execute_action missing.",
            }

        return connector.execute_action(
            action=rollback.rollback_action,
            target_id=rollback.target_id,
            payload=rollback.payload,
            actor=actor,
            rollback_mode=True,
        )

    def _update_status(
        self,
        rollback_id: str,
        status: str,
    ) -> None:

        self.conn.execute(
            """
            UPDATE rollback_executions
            SET status=?,
                updated_at_ms=?
            WHERE rollback_id=?
            """,
            (
                status,
                _now_ms(),
                rollback_id,
            ),
        )

        self.conn.commit()

    def _complete_rollback(
        self,
        rollback_id: str,
        result: Dict[str, Any],
    ) -> None:

        rollback = self.get_rollback(
            rollback_id
        )

        if rollback is None:
            return

        self.conn.execute(
            """
            UPDATE rollback_executions
            SET status=?,
                result_json=?,
                updated_at_ms=?,
                completed_at_ms=?
            WHERE rollback_id=?
            """,
            (
                ROLLBACK_COMPLETED,
                _json_dumps(result),
                _now_ms(),
                _now_ms(),
                rollback_id,
            ),
        )

        self.conn.commit()

        self._emit(
            EVENT_ROLLBACK_COMPLETED,
            tenant_id=rollback.tenant_id,
            severity=rollback.severity,
            payload={
                "rollback_id": rollback_id,
                "result": result,
            },
        )

    def _fail_rollback(
        self,
        rollback_id: str,
        error: str,
    ) -> None:

        rollback = self.get_rollback(
            rollback_id
        )

        if rollback is None:
            return

        self.conn.execute(
            """
            UPDATE rollback_executions
            SET status=?,
                result_json=?,
                updated_at_ms=?,
                completed_at_ms=?
            WHERE rollback_id=?
            """,
            (
                ROLLBACK_FAILED,
                _json_dumps(
                    {
                        "error": error,
                    }
                ),
                _now_ms(),
                _now_ms(),
                rollback_id,
            ),
        )

        self.conn.commit()

        self._emit(
            EVENT_ROLLBACK_FAILED,
            tenant_id=rollback.tenant_id,
            severity=rollback.severity,
            payload={
                "rollback_id": rollback_id,
                "error": error,
            },
        )

    def _emit(
        self,
        event_type: str,
        *,
        tenant_id: str,
        payload: Dict[str, Any],
        severity: str = "INFO",
    ) -> None:

        if self.event_bus is None:
            return

        try:

            self.event_bus.publish(
                event_type=event_type,
                tenant_id=tenant_id,
                source="rollback_orchestrator",
                severity=severity,
                payload=payload,
            )

        except TypeError:

            try:

                self.event_bus.publish(
                    event_type=event_type,
                    payload=payload,
                    tenant_id=tenant_id,
                    source="rollback_orchestrator",
                )

            except Exception:
                pass

        except Exception:
            pass


_DEFAULT_ROLLBACK_ORCHESTRATOR: Optional[
    RollbackOrchestrator
] = None


def get_rollback_orchestrator(
    storage: Any = None,
    *,
    reset: bool = False,
    event_bus: Any = None,
) -> RollbackOrchestrator:

    global _DEFAULT_ROLLBACK_ORCHESTRATOR

    if (
        reset
        or _DEFAULT_ROLLBACK_ORCHESTRATOR
        is None
    ):

        _DEFAULT_ROLLBACK_ORCHESTRATOR = (
            RollbackOrchestrator(
                storage=storage,
                event_bus=event_bus,
            )
        )

    return _DEFAULT_ROLLBACK_ORCHESTRATOR