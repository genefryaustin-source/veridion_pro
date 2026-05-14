from __future__ import annotations

import json
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional


def _now_ms() -> int:
    return int(time.time() * 1000)


def _json_dumps(value: Any) -> str:
    try:
        return json.dumps(value or {}, ensure_ascii=False, sort_keys=True)
    except Exception:
        return "{}"


def _json_loads(value: Any) -> Any:
    if value is None:
        return {}
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except Exception:
        return {}


def _row_to_dict(row: sqlite3.Row | Dict[str, Any] | None) -> Optional[Dict[str, Any]]:
    if row is None:
        return None
    data = dict(row) if not isinstance(row, dict) else row

    for key in (
        "metadata_json",
        "details_json",
        "payload_json",
        "policy_context_json",
        "rollback_payload_json",
        "verification_json",
    ):
        if key in data:
            data[key.replace("_json", "")] = _json_loads(data.get(key))

    return data


class GovernanceRepository:
    """
    Thread-safe SQLite-backed governance repository.

    IMPORTANT:
    This class intentionally does NOT keep a shared sqlite connection.
    Every method opens a short-lived connection to avoid Streamlit/thread errors.
    """

    def __init__(self, db_path: str):
        self.db_path = str(db_path)

    def _connect(self) -> sqlite3.Connection:
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            timeout=30,
        )
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=30000")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    # ========================================================
    # SCHEMA
    # ========================================================

    def ensure_schema(self) -> None:
        with self._connect() as conn:
            cur = conn.cursor()

            cur.execute("""
            CREATE TABLE IF NOT EXISTS approval_requests (
                request_id TEXT PRIMARY KEY,
                tenant_id TEXT,
                case_id TEXT,
                evidence_id TEXT,
                decision_id TEXT,
                request_type TEXT,
                action TEXT NOT NULL,
                risk TEXT,
                severity TEXT,
                status TEXT NOT NULL DEFAULT 'PENDING',
                requested_by TEXT,
                assigned_reviewer TEXT,
                reviewed_by TEXT,
                review_comment TEXT,
                requires_legal INTEGER DEFAULT 0,
                requires_manager INTEGER DEFAULT 0,
                rollback_available INTEGER DEFAULT 0,
                execution_trace_id TEXT,
                metadata_json TEXT,
                created_at_ms INTEGER NOT NULL,
                updated_at_ms INTEGER,
                reviewed_at_ms INTEGER
            )
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS orchestration_decisions (
                decision_id TEXT PRIMARY KEY,
                run_id TEXT,
                tenant_id TEXT,
                case_id TEXT,
                evidence_id TEXT,
                actor TEXT,
                recommendation TEXT,
                final_action TEXT,
                confidence REAL DEFAULT 0,
                risk TEXT,
                severity TEXT,
                status TEXT NOT NULL DEFAULT 'DECIDED',
                outcome TEXT,
                requires_approval INTEGER DEFAULT 0,
                approval_request_id TEXT,
                analyst_override INTEGER DEFAULT 0,
                rollback_available INTEGER DEFAULT 0,
                rollback_triggered INTEGER DEFAULT 0,
                execution_trace_id TEXT,
                policy_context_json TEXT,
                details_json TEXT,
                created_at_ms INTEGER NOT NULL,
                updated_at_ms INTEGER
            )
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS analyst_overrides (
                override_id TEXT PRIMARY KEY,
                decision_id TEXT,
                tenant_id TEXT,
                case_id TEXT,
                evidence_id TEXT,
                analyst TEXT,
                original_action TEXT,
                override_action TEXT,
                reason TEXT,
                severity TEXT,
                details_json TEXT,
                created_at_ms INTEGER NOT NULL
            )
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS governance_events (
                event_id TEXT PRIMARY KEY,
                tenant_id TEXT,
                case_id TEXT,
                evidence_id TEXT,
                decision_id TEXT,
                approval_request_id TEXT,
                rollback_id TEXT,
                event_type TEXT NOT NULL,
                severity TEXT,
                status TEXT,
                actor TEXT,
                action TEXT,
                target_type TEXT,
                target_id TEXT,
                requires_approval INTEGER DEFAULT 0,
                approved_by TEXT,
                rollback_available INTEGER DEFAULT 0,
                execution_trace_id TEXT,
                details_json TEXT,
                created_at_ms INTEGER NOT NULL
            )
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS rollback_events (
                rollback_id TEXT PRIMARY KEY,
                tenant_id TEXT,
                case_id TEXT,
                evidence_id TEXT,
                decision_id TEXT,
                approval_request_id TEXT,
                rollback_action TEXT NOT NULL,
                rollback_reason TEXT,
                status TEXT NOT NULL DEFAULT 'ROLLBACK_REQUIRED',
                severity TEXT,
                actor TEXT,
                assigned_reviewer TEXT,
                requires_approval INTEGER DEFAULT 0,
                rollback_payload_json TEXT,
                verification_json TEXT,
                execution_trace_id TEXT,
                created_at_ms INTEGER NOT NULL,
                updated_at_ms INTEGER,
                completed_at_ms INTEGER
            )
            """)

            cur.execute("""
            CREATE TABLE IF NOT EXISTS execution_traces (
                trace_id TEXT PRIMARY KEY,
                tenant_id TEXT,
                case_id TEXT,
                evidence_id TEXT,
                decision_id TEXT,
                stage TEXT NOT NULL,
                status TEXT NOT NULL,
                actor TEXT,
                action TEXT,
                message TEXT,
                payload_json TEXT,
                created_at_ms INTEGER NOT NULL
            )
            """)

            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_approval_status ON approval_requests(status)",
                "CREATE INDEX IF NOT EXISTS idx_approval_case ON approval_requests(case_id)",
                "CREATE INDEX IF NOT EXISTS idx_approval_decision ON approval_requests(decision_id)",
                "CREATE INDEX IF NOT EXISTS idx_decisions_case ON orchestration_decisions(case_id)",
                "CREATE INDEX IF NOT EXISTS idx_decisions_tenant ON orchestration_decisions(tenant_id)",
                "CREATE INDEX IF NOT EXISTS idx_decisions_created ON orchestration_decisions(created_at_ms)",
                "CREATE INDEX IF NOT EXISTS idx_overrides_case ON analyst_overrides(case_id)",
                "CREATE INDEX IF NOT EXISTS idx_overrides_decision ON analyst_overrides(decision_id)",
                "CREATE INDEX IF NOT EXISTS idx_gov_events_case ON governance_events(case_id)",
                "CREATE INDEX IF NOT EXISTS idx_gov_events_decision ON governance_events(decision_id)",
                "CREATE INDEX IF NOT EXISTS idx_gov_events_created ON governance_events(created_at_ms)",
                "CREATE INDEX IF NOT EXISTS idx_rollbacks_case ON rollback_events(case_id)",
                "CREATE INDEX IF NOT EXISTS idx_rollbacks_decision ON rollback_events(decision_id)",
                "CREATE INDEX IF NOT EXISTS idx_traces_decision ON execution_traces(decision_id)",
                "CREATE INDEX IF NOT EXISTS idx_traces_case ON execution_traces(case_id)",
                "CREATE INDEX IF NOT EXISTS idx_traces_created ON execution_traces(created_at_ms)",
            ]

            for sql in indexes:
                try:
                    cur.execute(sql)
                except Exception as e:
                    print("\n⚠️ GOVERNANCE INDEX FAILURE")
                    print("--------------------------------")
                    print("SQL:", sql)
                    print("ERROR:", str(e))
                    print("--------------------------------\n")

            conn.commit()

    # ========================================================
    # APPROVALS
    # ========================================================

    def create_approval_request(
        self,
        action: str,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        evidence_id: Optional[str] = None,
        decision_id: Optional[str] = None,
        request_type: str = "ACTION_APPROVAL",
        risk: Optional[str] = None,
        severity: Optional[str] = None,
        requested_by: str = "system",
        assigned_reviewer: Optional[str] = None,
        requires_legal: bool = False,
        requires_manager: bool = False,
        rollback_available: bool = False,
        execution_trace_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        self.ensure_schema()

        request_id = f"apr_{uuid.uuid4().hex}"
        now = _now_ms()

        with self._connect() as conn:
            conn.execute("""
                INSERT INTO approval_requests (
                    request_id, tenant_id, case_id, evidence_id, decision_id,
                    request_type, action, risk, severity, status,
                    requested_by, assigned_reviewer,
                    requires_legal, requires_manager, rollback_available,
                    execution_trace_id, metadata_json,
                    created_at_ms, updated_at_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING', ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                request_id,
                tenant_id,
                case_id,
                evidence_id,
                decision_id,
                request_type,
                action,
                risk,
                severity,
                requested_by,
                assigned_reviewer,
                int(requires_legal),
                int(requires_manager),
                int(rollback_available),
                execution_trace_id,
                _json_dumps(metadata),
                now,
                now,
            ))
            conn.commit()

        self.record_governance_event(
            event_type="APPROVAL_REQUEST_CREATED",
            action=action,
            tenant_id=tenant_id,
            case_id=case_id,
            evidence_id=evidence_id,
            decision_id=decision_id,
            approval_request_id=request_id,
            severity=severity,
            status="PENDING",
            actor=requested_by,
            requires_approval=True,
            rollback_available=rollback_available,
            execution_trace_id=execution_trace_id,
            details={
                "request_type": request_type,
                "assigned_reviewer": assigned_reviewer,
                "requires_legal": requires_legal,
                "requires_manager": requires_manager,
            },
        )

        return request_id

    def update_approval_status(
        self,
        request_id: str,
        status: str,
        reviewed_by: str = "system",
        review_comment: Optional[str] = None,
    ) -> bool:
        self.ensure_schema()

        now = _now_ms()
        status = status.upper()

        with self._connect() as conn:
            cur = conn.execute("""
                UPDATE approval_requests
                SET status = ?,
                    reviewed_by = ?,
                    review_comment = ?,
                    reviewed_at_ms = ?,
                    updated_at_ms = ?
                WHERE request_id = ?
            """, (
                status,
                reviewed_by,
                review_comment,
                now,
                now,
                request_id,
            ))
            conn.commit()
            changed = cur.rowcount > 0

        approval = self.get_approval_request(request_id)

        if approval:
            self.record_governance_event(
                event_type=f"APPROVAL_{status}",
                action=approval.get("action"),
                tenant_id=approval.get("tenant_id"),
                case_id=approval.get("case_id"),
                evidence_id=approval.get("evidence_id"),
                decision_id=approval.get("decision_id"),
                approval_request_id=request_id,
                severity=approval.get("severity"),
                status=status,
                actor=reviewed_by,
                details={
                    "review_comment": review_comment,
                    "request_type": approval.get("request_type"),
                },
            )

        return changed

    def get_approval_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        self.ensure_schema()

        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM approval_requests WHERE request_id = ?",
                (request_id,),
            ).fetchone()

        return _row_to_dict(row)

    def get_pending_approvals(
        self,
        tenant_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        self.ensure_schema()

        with self._connect() as conn:
            if tenant_id:
                rows = conn.execute("""
                    SELECT * FROM approval_requests
                    WHERE status = 'PENDING' AND tenant_id = ?
                    ORDER BY created_at_ms DESC
                    LIMIT ?
                """, (tenant_id, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM approval_requests
                    WHERE status = 'PENDING'
                    ORDER BY created_at_ms DESC
                    LIMIT ?
                """, (limit,)).fetchall()

        return [_row_to_dict(r) for r in rows if r is not None]

    def get_approval_history(
        self,
        case_id: Optional[str] = None,
        decision_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        limit: int = 250,
    ) -> List[Dict[str, Any]]:
        self.ensure_schema()

        with self._connect() as conn:
            if case_id:
                rows = conn.execute("""
                    SELECT * FROM approval_requests
                    WHERE case_id = ?
                    ORDER BY created_at_ms DESC
                    LIMIT ?
                """, (case_id, limit)).fetchall()
            elif decision_id:
                rows = conn.execute("""
                    SELECT * FROM approval_requests
                    WHERE decision_id = ?
                    ORDER BY created_at_ms DESC
                    LIMIT ?
                """, (decision_id, limit)).fetchall()
            elif tenant_id:
                rows = conn.execute("""
                    SELECT * FROM approval_requests
                    WHERE tenant_id = ?
                    ORDER BY created_at_ms DESC
                    LIMIT ?
                """, (tenant_id, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM approval_requests
                    ORDER BY created_at_ms DESC
                    LIMIT ?
                """, (limit,)).fetchall()

        return [_row_to_dict(r) for r in rows if r is not None]

    # ========================================================
    # ORCHESTRATION DECISIONS
    # ========================================================

    def record_orchestration_decision(
        self,
        recommendation: str,
        final_action: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        evidence_id: Optional[str] = None,
        run_id: Optional[str] = None,
        actor: str = "ai_orchestrator",
        confidence: float = 0.0,
        risk: Optional[str] = None,
        severity: Optional[str] = None,
        status: str = "DECIDED",
        outcome: Optional[str] = None,
        requires_approval: bool = False,
        approval_request_id: Optional[str] = None,
        analyst_override: bool = False,
        rollback_available: bool = False,
        rollback_triggered: bool = False,
        execution_trace_id: Optional[str] = None,
        policy_context: Optional[Dict[str, Any]] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> str:
        self.ensure_schema()

        decision_id = f"dec_{uuid.uuid4().hex}"
        now = _now_ms()

        with self._connect() as conn:
            conn.execute("""
                INSERT INTO orchestration_decisions (
                    decision_id, run_id, tenant_id, case_id, evidence_id, actor,
                    recommendation, final_action, confidence, risk, severity,
                    status, outcome, requires_approval, approval_request_id,
                    analyst_override, rollback_available, rollback_triggered,
                    execution_trace_id, policy_context_json, details_json,
                    created_at_ms, updated_at_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                decision_id,
                run_id,
                tenant_id,
                case_id,
                evidence_id,
                actor,
                recommendation,
                final_action,
                float(confidence or 0.0),
                risk,
                severity,
                status,
                outcome,
                int(requires_approval),
                approval_request_id,
                int(analyst_override),
                int(rollback_available),
                int(rollback_triggered),
                execution_trace_id,
                _json_dumps(policy_context),
                _json_dumps(details),
                now,
                now,
            ))
            conn.commit()

        self.record_governance_event(
            event_type="ORCHESTRATION_DECISION_RECORDED",
            action=final_action or recommendation,
            tenant_id=tenant_id,
            case_id=case_id,
            evidence_id=evidence_id,
            decision_id=decision_id,
            approval_request_id=approval_request_id,
            severity=severity,
            status=status,
            actor=actor,
            requires_approval=requires_approval,
            rollback_available=rollback_available,
            execution_trace_id=execution_trace_id,
            details={
                "confidence": confidence,
                "risk": risk,
                "outcome": outcome,
                "recommendation": recommendation,
            },
        )

        return decision_id

    def get_decision(self, decision_id: str) -> Optional[Dict[str, Any]]:
        self.ensure_schema()

        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM orchestration_decisions WHERE decision_id = ?",
                (decision_id,),
            ).fetchone()

        return _row_to_dict(row)

    def get_recent_decisions(
        self,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        self.ensure_schema()

        with self._connect() as conn:
            if case_id:
                rows = conn.execute("""
                    SELECT * FROM orchestration_decisions
                    WHERE case_id = ?
                    ORDER BY created_at_ms DESC
                    LIMIT ?
                """, (case_id, limit)).fetchall()
            elif tenant_id:
                rows = conn.execute("""
                    SELECT * FROM orchestration_decisions
                    WHERE tenant_id = ?
                    ORDER BY created_at_ms DESC
                    LIMIT ?
                """, (tenant_id, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM orchestration_decisions
                    ORDER BY created_at_ms DESC
                    LIMIT ?
                """, (limit,)).fetchall()

        return [_row_to_dict(r) for r in rows if r is not None]

    # ========================================================
    # OVERRIDES
    # ========================================================

    def record_analyst_override(
        self,
        decision_id: str,
        analyst: str,
        original_action: str,
        override_action: str,
        reason: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        evidence_id: Optional[str] = None,
        severity: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> str:
        self.ensure_schema()

        override_id = f"ovr_{uuid.uuid4().hex}"
        now = _now_ms()

        with self._connect() as conn:
            conn.execute("""
                INSERT INTO analyst_overrides (
                    override_id, decision_id, tenant_id, case_id, evidence_id,
                    analyst, original_action, override_action, reason,
                    severity, details_json, created_at_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                override_id,
                decision_id,
                tenant_id,
                case_id,
                evidence_id,
                analyst,
                original_action,
                override_action,
                reason,
                severity,
                _json_dumps(details),
                now,
            ))

            conn.execute("""
                UPDATE orchestration_decisions
                SET analyst_override = 1,
                    updated_at_ms = ?
                WHERE decision_id = ?
            """, (now, decision_id))

            conn.commit()

        self.record_governance_event(
            event_type="ANALYST_OVERRIDE_RECORDED",
            action=f"{original_action} -> {override_action}",
            tenant_id=tenant_id,
            case_id=case_id,
            evidence_id=evidence_id,
            decision_id=decision_id,
            severity=severity,
            status="OVERRIDDEN",
            actor=analyst,
            details={
                "override_id": override_id,
                "reason": reason,
                "original_action": original_action,
                "override_action": override_action,
            },
        )

        return override_id

    def get_case_overrides(
        self,
        case_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        self.ensure_schema()

        with self._connect() as conn:
            if case_id:
                rows = conn.execute("""
                    SELECT * FROM analyst_overrides
                    WHERE case_id = ?
                    ORDER BY created_at_ms DESC
                    LIMIT ?
                """, (case_id, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM analyst_overrides
                    ORDER BY created_at_ms DESC
                    LIMIT ?
                """, (limit,)).fetchall()

        return [_row_to_dict(r) for r in rows if r is not None]

    def get_decision_overrides(
        self,
        decision_id: str,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        self.ensure_schema()

        with self._connect() as conn:
            rows = conn.execute("""
                SELECT * FROM analyst_overrides
                WHERE decision_id = ?
                ORDER BY created_at_ms DESC
                LIMIT ?
            """, (decision_id, limit)).fetchall()

        return [_row_to_dict(r) for r in rows if r is not None]

    # ========================================================
    # GOVERNANCE EVENTS
    # ========================================================

    def record_governance_event(
        self,
        event_type: str,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        evidence_id: Optional[str] = None,
        decision_id: Optional[str] = None,
        approval_request_id: Optional[str] = None,
        rollback_id: Optional[str] = None,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        actor: str = "system",
        action: Optional[str] = None,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        requires_approval: bool = False,
        approved_by: Optional[str] = None,
        rollback_available: bool = False,
        execution_trace_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> str:
        self.ensure_schema()

        event_id = f"gov_{uuid.uuid4().hex}"
        now = _now_ms()

        with self._connect() as conn:
            conn.execute("""
                INSERT INTO governance_events (
                    event_id, tenant_id, case_id, evidence_id, decision_id,
                    approval_request_id, rollback_id, event_type, severity,
                    status, actor, action, target_type, target_id,
                    requires_approval, approved_by, rollback_available,
                    execution_trace_id, details_json, created_at_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event_id,
                tenant_id,
                case_id,
                evidence_id,
                decision_id,
                approval_request_id,
                rollback_id,
                event_type,
                severity,
                status,
                actor,
                action,
                target_type,
                target_id,
                int(requires_approval),
                approved_by,
                int(rollback_available),
                execution_trace_id,
                _json_dumps(details),
                now,
            ))
            conn.commit()

        return event_id

    def get_governance_events(
        self,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        decision_id: Optional[str] = None,
        limit: int = 250,
    ) -> List[Dict[str, Any]]:
        self.ensure_schema()

        with self._connect() as conn:
            if decision_id:
                rows = conn.execute("""
                    SELECT * FROM governance_events
                    WHERE decision_id = ?
                    ORDER BY created_at_ms DESC
                    LIMIT ?
                """, (decision_id, limit)).fetchall()
            elif case_id:
                rows = conn.execute("""
                    SELECT * FROM governance_events
                    WHERE case_id = ?
                    ORDER BY created_at_ms DESC
                    LIMIT ?
                """, (case_id, limit)).fetchall()
            elif tenant_id:
                rows = conn.execute("""
                    SELECT * FROM governance_events
                    WHERE tenant_id = ?
                    ORDER BY created_at_ms DESC
                    LIMIT ?
                """, (tenant_id, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM governance_events
                    ORDER BY created_at_ms DESC
                    LIMIT ?
                """, (limit,)).fetchall()

        return [_row_to_dict(r) for r in rows if r is not None]

    # ========================================================
    # ROLLBACKS
    # ========================================================

    def record_rollback_event(
        self,
        rollback_action: str,
        rollback_reason: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        evidence_id: Optional[str] = None,
        decision_id: Optional[str] = None,
        approval_request_id: Optional[str] = None,
        status: str = "ROLLBACK_REQUIRED",
        severity: Optional[str] = "HIGH",
        actor: str = "system",
        assigned_reviewer: Optional[str] = None,
        requires_approval: bool = False,
        rollback_payload: Optional[Dict[str, Any]] = None,
        verification: Optional[Dict[str, Any]] = None,
        execution_trace_id: Optional[str] = None,
    ) -> str:
        self.ensure_schema()

        rollback_id = f"rbk_{uuid.uuid4().hex}"
        now = _now_ms()

        with self._connect() as conn:
            conn.execute("""
                INSERT INTO rollback_events (
                    rollback_id, tenant_id, case_id, evidence_id, decision_id,
                    approval_request_id, rollback_action, rollback_reason,
                    status, severity, actor, assigned_reviewer,
                    requires_approval, rollback_payload_json,
                    verification_json, execution_trace_id,
                    created_at_ms, updated_at_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rollback_id,
                tenant_id,
                case_id,
                evidence_id,
                decision_id,
                approval_request_id,
                rollback_action,
                rollback_reason,
                status,
                severity,
                actor,
                assigned_reviewer,
                int(requires_approval),
                _json_dumps(rollback_payload),
                _json_dumps(verification),
                execution_trace_id,
                now,
                now,
            ))

            if decision_id:
                conn.execute("""
                    UPDATE orchestration_decisions
                    SET rollback_triggered = 1,
                        updated_at_ms = ?
                    WHERE decision_id = ?
                """, (now, decision_id))

            conn.commit()

        self.record_governance_event(
            event_type="ROLLBACK_EVENT_RECORDED",
            action=rollback_action,
            tenant_id=tenant_id,
            case_id=case_id,
            evidence_id=evidence_id,
            decision_id=decision_id,
            approval_request_id=approval_request_id,
            rollback_id=rollback_id,
            severity=severity,
            status=status,
            actor=actor,
            requires_approval=requires_approval,
            rollback_available=True,
            execution_trace_id=execution_trace_id,
            details={
                "rollback_reason": rollback_reason,
                "assigned_reviewer": assigned_reviewer,
            },
        )

        return rollback_id

    def update_rollback_status(
        self,
        rollback_id: str,
        status: str,
        actor: str = "system",
        verification: Optional[Dict[str, Any]] = None,
    ) -> bool:
        self.ensure_schema()

        now = _now_ms()
        status = status.upper()
        completed_at_ms = now if status in {"COMPLETED", "FAILED", "CANCELLED", "ROLLBACK_COMPLETED", "ROLLBACK_FAILED"} else None

        with self._connect() as conn:
            cur = conn.execute("""
                UPDATE rollback_events
                SET status = ?,
                    verification_json = ?,
                    updated_at_ms = ?,
                    completed_at_ms = COALESCE(?, completed_at_ms)
                WHERE rollback_id = ?
            """, (
                status,
                _json_dumps(verification),
                now,
                completed_at_ms,
                rollback_id,
            ))
            conn.commit()
            changed = cur.rowcount > 0

        rollback = self.get_rollback(rollback_id)

        if rollback:
            self.record_governance_event(
                event_type=f"ROLLBACK_{status}",
                action=rollback.get("rollback_action"),
                tenant_id=rollback.get("tenant_id"),
                case_id=rollback.get("case_id"),
                evidence_id=rollback.get("evidence_id"),
                decision_id=rollback.get("decision_id"),
                approval_request_id=rollback.get("approval_request_id"),
                rollback_id=rollback_id,
                severity=rollback.get("severity"),
                status=status,
                actor=actor,
                rollback_available=True,
                details={"verification": verification or {}},
            )

        return changed

    def get_rollback(self, rollback_id: str) -> Optional[Dict[str, Any]]:
        self.ensure_schema()

        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM rollback_events WHERE rollback_id = ?",
                (rollback_id,),
            ).fetchone()

        return _row_to_dict(row)

    def get_rollback_history(
        self,
        case_id: Optional[str] = None,
        decision_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        limit: int = 250,
    ) -> List[Dict[str, Any]]:
        self.ensure_schema()

        with self._connect() as conn:
            if case_id:
                rows = conn.execute("""
                    SELECT * FROM rollback_events
                    WHERE case_id = ?
                    ORDER BY created_at_ms DESC
                    LIMIT ?
                """, (case_id, limit)).fetchall()
            elif decision_id:
                rows = conn.execute("""
                    SELECT * FROM rollback_events
                    WHERE decision_id = ?
                    ORDER BY created_at_ms DESC
                    LIMIT ?
                """, (decision_id, limit)).fetchall()
            elif tenant_id:
                rows = conn.execute("""
                    SELECT * FROM rollback_events
                    WHERE tenant_id = ?
                    ORDER BY created_at_ms DESC
                    LIMIT ?
                """, (tenant_id, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM rollback_events
                    ORDER BY created_at_ms DESC
                    LIMIT ?
                """, (limit,)).fetchall()

        return [_row_to_dict(r) for r in rows if r is not None]

    # ========================================================
    # EXECUTION TRACES
    # ========================================================

    def record_execution_trace(
        self,
        stage: str,
        status: str,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        evidence_id: Optional[str] = None,
        decision_id: Optional[str] = None,
        actor: str = "system",
        action: Optional[str] = None,
        message: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> str:
        self.ensure_schema()

        trace_id = f"trc_{uuid.uuid4().hex}"
        now = _now_ms()

        with self._connect() as conn:
            conn.execute("""
                INSERT INTO execution_traces (
                    trace_id, tenant_id, case_id, evidence_id, decision_id,
                    stage, status, actor, action, message, payload_json,
                    created_at_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trace_id,
                tenant_id,
                case_id,
                evidence_id,
                decision_id,
                stage,
                status,
                actor,
                action,
                message,
                _json_dumps(payload),
                now,
            ))
            conn.commit()

        self.record_governance_event(
            event_type="EXECUTION_TRACE_RECORDED",
            action=action,
            tenant_id=tenant_id,
            case_id=case_id,
            evidence_id=evidence_id,
            decision_id=decision_id,
            status=status,
            actor=actor,
            execution_trace_id=trace_id,
            details={
                "stage": stage,
                "message": message,
                "payload": payload or {},
            },
        )

        return trace_id

    def get_execution_traces(
        self,
        case_id: Optional[str] = None,
        decision_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        limit: int = 250,
    ) -> List[Dict[str, Any]]:
        self.ensure_schema()

        with self._connect() as conn:
            if decision_id:
                rows = conn.execute("""
                    SELECT * FROM execution_traces
                    WHERE decision_id = ?
                    ORDER BY created_at_ms ASC
                    LIMIT ?
                """, (decision_id, limit)).fetchall()
            elif case_id:
                rows = conn.execute("""
                    SELECT * FROM execution_traces
                    WHERE case_id = ?
                    ORDER BY created_at_ms ASC
                    LIMIT ?
                """, (case_id, limit)).fetchall()
            elif tenant_id:
                rows = conn.execute("""
                    SELECT * FROM execution_traces
                    WHERE tenant_id = ?
                    ORDER BY created_at_ms DESC
                    LIMIT ?
                """, (tenant_id, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM execution_traces
                    ORDER BY created_at_ms DESC
                    LIMIT ?
                """, (limit,)).fetchall()

        return [_row_to_dict(r) for r in rows if r is not None]

    # ========================================================
    # FORENSIC REPLAY
    # ========================================================

    def get_forensic_replay(
        self,
        case_id: Optional[str] = None,
        decision_id: Optional[str] = None,
        evidence_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        limit: int = 500,
    ) -> List[Dict[str, Any]]:
        self.ensure_schema()

        events: List[Dict[str, Any]] = []

        def add_event(source: str, timestamp: Any, event: str, data: Dict[str, Any]) -> None:
            events.append({
                "source": source,
                "timestamp": timestamp,
                "event": event,
                "status": data.get("status") or data.get("outcome"),
                "actor": data.get("actor") or data.get("requested_by") or data.get("analyst"),
                "case_id": data.get("case_id"),
                "tenant_id": data.get("tenant_id"),
                "evidence_id": data.get("evidence_id"),
                "decision_id": data.get("decision_id"),
                "details": data,
            })

        filters = []
        params: List[Any] = []

        if case_id:
            filters.append("case_id = ?")
            params.append(case_id)
        if decision_id:
            filters.append("decision_id = ?")
            params.append(decision_id)
        if evidence_id:
            filters.append("evidence_id = ?")
            params.append(evidence_id)
        if tenant_id:
            filters.append("tenant_id = ?")
            params.append(tenant_id)

        where = f"WHERE {' AND '.join(filters)}" if filters else ""

        table_specs = [
            ("orchestration_decisions", "created_at_ms", "AI Decision", "recommendation"),
            ("approval_requests", "created_at_ms", "Approval Request", "action"),
            ("analyst_overrides", "created_at_ms", "Analyst Override", "override_action"),
            ("governance_events", "created_at_ms", "Governance Event", "event_type"),
            ("rollback_events", "created_at_ms", "Rollback Event", "rollback_action"),
            ("execution_traces", "created_at_ms", "Execution Trace", "stage"),
        ]

        with self._connect() as conn:
            for table, ts_col, source, event_col in table_specs:
                query = f"""
                    SELECT * FROM {table}
                    {where}
                    ORDER BY {ts_col} DESC
                    LIMIT ?
                """
                try:
                    rows = conn.execute(query, (*params, limit)).fetchall()
                except Exception:
                    rows = []

                for row in rows:
                    data = _row_to_dict(row) or {}
                    add_event(
                        source=source,
                        timestamp=data.get(ts_col),
                        event=str(data.get(event_col) or source),
                        data=data,
                    )

        events.sort(key=lambda x: x.get("timestamp") or 0)
        return events[-limit:]