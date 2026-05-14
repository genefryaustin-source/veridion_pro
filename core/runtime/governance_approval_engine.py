"""
core/runtime/governance_approval_engine.py

Governance Approval Engine for Veridion Pro / CUI GovCloud App.

Purpose:
- Create approval requests
- Approve/reject governed actions
- Support legal review
- Support dual approval
- Track approval expiration/SLA pressure
- Support emergency override
- Preserve audit chain
- Bridge autonomous execution to human governance

Safe defaults:
- Approval requests are explicit and auditable
- Legal and dual approvals are tracked separately
- Expired approvals cannot be executed
- Emergency override is recorded as high-severity governance event
"""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


APPROVAL_STATUS_PENDING = "PENDING"
APPROVAL_STATUS_APPROVED = "APPROVED"
APPROVAL_STATUS_REJECTED = "REJECTED"
APPROVAL_STATUS_EXPIRED = "EXPIRED"
APPROVAL_STATUS_CANCELLED = "CANCELLED"
APPROVAL_STATUS_ESCALATED = "ESCALATED"
APPROVAL_STATUS_OVERRIDE_APPROVED = "OVERRIDE_APPROVED"

REVIEW_TYPE_STANDARD = "STANDARD"
REVIEW_TYPE_LEGAL = "LEGAL"
REVIEW_TYPE_DUAL = "DUAL"
REVIEW_TYPE_EMERGENCY = "EMERGENCY"

SEVERITY_LOW = "LOW"
SEVERITY_MEDIUM = "MEDIUM"
SEVERITY_HIGH = "HIGH"
SEVERITY_CRITICAL = "CRITICAL"

DEFAULT_APPROVAL_TTL_MS = 24 * 60 * 60 * 1000
CRITICAL_APPROVAL_TTL_MS = 4 * 60 * 60 * 1000
LEGAL_APPROVAL_TTL_MS = 72 * 60 * 60 * 1000


def _now_ms() -> int:
    return int(time.time() * 1000)


def _json_dumps(value: Any) -> str:
    try:
        return json.dumps(value or {}, default=str)
    except Exception:
        return "{}"


def _json_loads(value: Any, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if default is None:
        default = {}
    if value is None:
        return default
    if isinstance(value, dict):
        return value
    try:
        return json.loads(value)
    except Exception:
        return default


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    try:
        return str(value)
    except Exception:
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except Exception:
        return default


def _get_ledger(storage_or_ledger: Any) -> Any:
    if storage_or_ledger is None:
        return None
    return getattr(storage_or_ledger, "ledger", storage_or_ledger)


def _get_connection(storage_or_ledger: Any) -> sqlite3.Connection:
    ledger = _get_ledger(storage_or_ledger)

    if ledger is not None:
        for attr in ("conn", "_conn", "connection", "_connection"):
            conn = getattr(ledger, attr, None)
            if isinstance(conn, sqlite3.Connection):
                return conn

        for attr in ("db_path", "database_path", "path", "_db_path"):
            db_path = getattr(ledger, attr, None)
            if db_path:
                return sqlite3.connect(db_path, check_same_thread=False)

        connect_fn = getattr(ledger, "_connect", None)
        if callable(connect_fn):
            try:
                return connect_fn()
            except Exception:
                pass

    if isinstance(storage_or_ledger, str):
        return sqlite3.connect(storage_or_ledger, check_same_thread=False)

    return sqlite3.connect("data/ledger.db", check_same_thread=False)


def _record_custody_event(
    storage: Any,
    *,
    event_type: str,
    actor: str,
    tenant_id: str,
    evidence_id: Optional[str] = None,
    case_id: Optional[Any] = None,
    alert_id: Optional[Any] = None,
    execution_id: Optional[str] = None,
    approval_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> None:
    ledger = _get_ledger(storage)
    if ledger is None:
        return

    fn = getattr(ledger, "record_custody_event", None)
    if not callable(fn):
        return

    payload = {
        "tenant_id": tenant_id,
        "case_id": case_id,
        "alert_id": alert_id,
        "execution_id": execution_id,
        "approval_id": approval_id,
        **(details or {}),
    }

    try:
        fn(
            run_id=None,
            evidence_id=evidence_id,
            event_type=event_type,
            actor=actor,
            timestamp_ms=_now_ms(),
            details_json=payload,
        )
    except TypeError:
        try:
            fn(
                None,
                evidence_id,
                event_type,
                actor,
                _now_ms(),
                payload,
            )
        except Exception:
            pass
    except Exception:
        pass


@dataclass
class ApprovalRequest:
    approval_id: str
    tenant_id: str
    action: str
    status: str = APPROVAL_STATUS_PENDING

    requested_by: str = "system"
    requested_at_ms: int = field(default_factory=_now_ms)
    expires_at_ms: int = 0

    execution_id: Optional[str] = None
    job_id: Optional[str] = None
    case_id: Optional[Any] = None
    alert_id: Optional[Any] = None
    evidence_id: Optional[Any] = None

    severity: str = SEVERITY_MEDIUM
    risk_score: int = 0
    review_type: str = REVIEW_TYPE_STANDARD

    requires_legal: bool = False
    requires_dual_approval: bool = False

    approved_by: Optional[str] = None
    approved_at_ms: Optional[int] = None

    second_approved_by: Optional[str] = None
    second_approved_at_ms: Optional[int] = None

    rejected_by: Optional[str] = None
    rejected_at_ms: Optional[int] = None

    legal_reviewer: Optional[str] = None
    legal_reviewed_at_ms: Optional[int] = None
    legal_approved: Optional[bool] = None

    reason: str = ""
    rejection_reason: Optional[str] = None
    override_reason: Optional[str] = None

    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ApprovalDecisionResult:
    ok: bool
    approval_id: str
    status: str
    message: str
    action: Optional[str] = None
    execution_id: Optional[str] = None
    case_id: Optional[Any] = None
    tenant_id: Optional[str] = None
    approved: bool = False
    rejected: bool = False
    executable: bool = False
    details: Dict[str, Any] = field(default_factory=dict)


class GovernanceApprovalEngine:
    def __init__(
        self,
        storage: Any = None,
        *,
        event_bus: Any = None,
        execution_release_callback: Any = None,
    ) -> None:
        self.storage = storage
        self.ledger = _get_ledger(storage)
        self.conn = _get_connection(storage)
        self.event_bus = event_bus
        self.execution_release_callback = execution_release_callback
        self.ensure_schema()

    def ensure_schema(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS governance_approval_requests (
                approval_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                action TEXT NOT NULL,
                status TEXT NOT NULL,

                requested_by TEXT,
                requested_at_ms INTEGER NOT NULL,
                expires_at_ms INTEGER,

                execution_id TEXT,
                job_id TEXT,
                case_id TEXT,
                alert_id TEXT,
                evidence_id TEXT,

                severity TEXT,
                risk_score INTEGER DEFAULT 0,
                review_type TEXT,

                requires_legal INTEGER DEFAULT 0,
                requires_dual_approval INTEGER DEFAULT 0,

                approved_by TEXT,
                approved_at_ms INTEGER,

                second_approved_by TEXT,
                second_approved_at_ms INTEGER,

                rejected_by TEXT,
                rejected_at_ms INTEGER,

                legal_reviewer TEXT,
                legal_reviewed_at_ms INTEGER,
                legal_approved INTEGER,

                reason TEXT,
                rejection_reason TEXT,
                override_reason TEXT,

                payload_json TEXT,
                metadata_json TEXT,

                created_at_ms INTEGER NOT NULL,
                updated_at_ms INTEGER NOT NULL
            )
            """
        )

        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS governance_approval_events (
                event_id TEXT PRIMARY KEY,
                approval_id TEXT NOT NULL,
                tenant_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                actor TEXT,
                message TEXT,
                details_json TEXT,
                created_at_ms INTEGER NOT NULL
            )
            """
        )

        self.conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_governance_approvals_status
            ON governance_approval_requests(status)
            """
        )

        self.conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_governance_approvals_tenant
            ON governance_approval_requests(tenant_id)
            """
        )

        self.conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_governance_approvals_execution
            ON governance_approval_requests(execution_id)
            """
        )

        self.conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_governance_approval_events_approval
            ON governance_approval_events(approval_id)
            """
        )

        self.conn.commit()

    def create_approval_request(
        self,
        *,
        tenant_id: str,
        action: str,
        requested_by: str,
        execution_id: Optional[str] = None,
        job_id: Optional[str] = None,
        case_id: Optional[Any] = None,
        alert_id: Optional[Any] = None,
        evidence_id: Optional[Any] = None,
        severity: str = SEVERITY_MEDIUM,
        risk_score: int = 0,
        requires_legal: bool = False,
        requires_dual_approval: bool = False,
        reason: str = "",
        payload: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ttl_ms: Optional[int] = None,
    ) -> ApprovalRequest:
        tenant_id = tenant_id or "default"
        action = _safe_str(action).upper()
        severity = _safe_str(severity, SEVERITY_MEDIUM).upper()

        review_type = REVIEW_TYPE_STANDARD
        if requires_legal:
            review_type = REVIEW_TYPE_LEGAL
        if requires_dual_approval:
            review_type = REVIEW_TYPE_DUAL
        if requires_legal and requires_dual_approval:
            review_type = f"{REVIEW_TYPE_LEGAL}+{REVIEW_TYPE_DUAL}"

        ttl = ttl_ms
        if ttl is None:
            if requires_legal:
                ttl = LEGAL_APPROVAL_TTL_MS
            elif severity == SEVERITY_CRITICAL:
                ttl = CRITICAL_APPROVAL_TTL_MS
            else:
                ttl = DEFAULT_APPROVAL_TTL_MS

        now = _now_ms()
        approval_id = f"APR-{uuid.uuid4().hex[:12].upper()}"

        request = ApprovalRequest(
            approval_id=approval_id,
            tenant_id=tenant_id,
            action=action,
            status=APPROVAL_STATUS_PENDING,
            requested_by=requested_by,
            requested_at_ms=now,
            expires_at_ms=now + int(ttl),
            execution_id=execution_id,
            job_id=job_id,
            case_id=case_id,
            alert_id=alert_id,
            evidence_id=evidence_id,
            severity=severity,
            risk_score=risk_score,
            review_type=review_type,
            requires_legal=requires_legal,
            requires_dual_approval=requires_dual_approval,
            reason=reason,
            payload=payload or {},
            metadata=metadata or {},
        )

        self.conn.execute(
            """
            INSERT INTO governance_approval_requests (
                approval_id,
                tenant_id,
                action,
                status,
                requested_by,
                requested_at_ms,
                expires_at_ms,
                execution_id,
                job_id,
                case_id,
                alert_id,
                evidence_id,
                severity,
                risk_score,
                review_type,
                requires_legal,
                requires_dual_approval,
                reason,
                payload_json,
                metadata_json,
                created_at_ms,
                updated_at_ms
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request.approval_id,
                request.tenant_id,
                request.action,
                request.status,
                request.requested_by,
                request.requested_at_ms,
                request.expires_at_ms,
                request.execution_id,
                request.job_id,
                str(request.case_id) if request.case_id is not None else None,
                str(request.alert_id) if request.alert_id is not None else None,
                str(request.evidence_id) if request.evidence_id is not None else None,
                request.severity,
                request.risk_score,
                request.review_type,
                int(request.requires_legal),
                int(request.requires_dual_approval),
                request.reason,
                _json_dumps(request.payload),
                _json_dumps(request.metadata),
                now,
                now,
            ),
        )
        self.conn.commit()

        self._record_approval_event(
            approval_id=approval_id,
            tenant_id=tenant_id,
            event_type="APPROVAL_REQUEST_CREATED",
            actor=requested_by,
            message="Governance approval request created.",
            details=asdict(request),
        )

        _record_custody_event(
            self.storage,
            event_type="GOVERNANCE_APPROVAL_REQUEST_CREATED",
            actor=requested_by,
            tenant_id=tenant_id,
            evidence_id=evidence_id,
            case_id=case_id,
            alert_id=alert_id,
            execution_id=execution_id,
            approval_id=approval_id,
            details={
                "action": action,
                "severity": severity,
                "risk_score": risk_score,
                "requires_legal": requires_legal,
                "requires_dual_approval": requires_dual_approval,
                "reason": reason,
            },
        )

        self._publish(
            event_type="APPROVAL_REQUEST_CREATED",
            tenant_id=tenant_id,
            payload={
                "approval_id": approval_id,
                "action": action,
                "execution_id": execution_id,
                "case_id": case_id,
                "severity": severity,
                "risk_score": risk_score,
                "requires_legal": requires_legal,
                "requires_dual_approval": requires_dual_approval,
            },
        )

        return request

    def approve(
        self,
        approval_id: str,
        *,
        actor: str,
        reason: str = "",
        legal_approval: bool = False,
        second_approval: bool = False,
        release_execution: bool = True,
    ) -> ApprovalDecisionResult:
        request = self.get_approval_request(approval_id)

        if not request:
            return ApprovalDecisionResult(
                ok=False,
                approval_id=approval_id,
                status="NOT_FOUND",
                message="Approval request not found.",
            )

        if request["status"] not in {APPROVAL_STATUS_PENDING, APPROVAL_STATUS_ESCALATED}:
            return ApprovalDecisionResult(
                ok=False,
                approval_id=approval_id,
                status=request["status"],
                message=f"Approval request is not pending: {request['status']}",
            )

        if self._is_expired(request):
            self.expire_approval(approval_id, actor="approval_engine")
            return ApprovalDecisionResult(
                ok=False,
                approval_id=approval_id,
                status=APPROVAL_STATUS_EXPIRED,
                message="Approval request has expired.",
            )

        now = _now_ms()

        updates: Dict[str, Any] = {}

        if legal_approval or request.get("requires_legal"):
            updates["legal_reviewer"] = actor
            updates["legal_reviewed_at_ms"] = now
            updates["legal_approved"] = 1

        if second_approval or request.get("approved_by"):
            if request.get("approved_by") and request.get("approved_by") != actor:
                updates["second_approved_by"] = actor
                updates["second_approved_at_ms"] = now
            elif not request.get("approved_by"):
                updates["approved_by"] = actor
                updates["approved_at_ms"] = now
        else:
            updates["approved_by"] = actor
            updates["approved_at_ms"] = now

        merged = {**request, **updates}

        final_ready = self._approval_is_complete(merged)

        status = APPROVAL_STATUS_APPROVED if final_ready else APPROVAL_STATUS_PENDING

        self._update_approval(
            approval_id,
            {
                **updates,
                "status": status,
                "metadata_json": self._merge_metadata(
                    request.get("metadata_json"),
                    {
                        "last_approval_reason": reason,
                        "last_approved_by": actor,
                    },
                ),
            },
        )

        self._record_approval_event(
            approval_id=approval_id,
            tenant_id=request["tenant_id"],
            event_type="APPROVAL_GRANTED" if final_ready else "PARTIAL_APPROVAL_GRANTED",
            actor=actor,
            message="Approval granted." if final_ready else "Partial approval granted.",
            details={
                "reason": reason,
                "legal_approval": legal_approval,
                "second_approval": second_approval,
                "final_ready": final_ready,
            },
        )

        _record_custody_event(
            self.storage,
            event_type="GOVERNANCE_APPROVAL_GRANTED" if final_ready else "GOVERNANCE_PARTIAL_APPROVAL_GRANTED",
            actor=actor,
            tenant_id=request["tenant_id"],
            evidence_id=request.get("evidence_id"),
            case_id=request.get("case_id"),
            alert_id=request.get("alert_id"),
            execution_id=request.get("execution_id"),
            approval_id=approval_id,
            details={
                "reason": reason,
                "final_ready": final_ready,
            },
        )

        executable = False

        if final_ready and release_execution:
            executable = self.release_execution(approval_id, actor=actor)

        return ApprovalDecisionResult(
            ok=True,
            approval_id=approval_id,
            status=status,
            message="Approval complete." if final_ready else "Partial approval recorded.",
            action=request.get("action"),
            execution_id=request.get("execution_id"),
            case_id=request.get("case_id"),
            tenant_id=request.get("tenant_id"),
            approved=final_ready,
            executable=executable,
            details={
                "final_ready": final_ready,
                "released": executable,
            },
        )

    def reject(
        self,
        approval_id: str,
        *,
        actor: str,
        reason: str,
    ) -> ApprovalDecisionResult:
        request = self.get_approval_request(approval_id)

        if not request:
            return ApprovalDecisionResult(
                ok=False,
                approval_id=approval_id,
                status="NOT_FOUND",
                message="Approval request not found.",
            )

        if request["status"] not in {APPROVAL_STATUS_PENDING, APPROVAL_STATUS_ESCALATED}:
            return ApprovalDecisionResult(
                ok=False,
                approval_id=approval_id,
                status=request["status"],
                message=f"Approval request is not pending: {request['status']}",
            )

        self._update_approval(
            approval_id,
            {
                "status": APPROVAL_STATUS_REJECTED,
                "rejected_by": actor,
                "rejected_at_ms": _now_ms(),
                "rejection_reason": reason,
            },
        )

        self._record_approval_event(
            approval_id=approval_id,
            tenant_id=request["tenant_id"],
            event_type="APPROVAL_REJECTED",
            actor=actor,
            message="Approval rejected.",
            details={"reason": reason},
        )

        _record_custody_event(
            self.storage,
            event_type="GOVERNANCE_APPROVAL_REJECTED",
            actor=actor,
            tenant_id=request["tenant_id"],
            evidence_id=request.get("evidence_id"),
            case_id=request.get("case_id"),
            alert_id=request.get("alert_id"),
            execution_id=request.get("execution_id"),
            approval_id=approval_id,
            details={"reason": reason},
        )

        self._publish(
            event_type="APPROVAL_REJECTED",
            tenant_id=request["tenant_id"],
            payload={
                "approval_id": approval_id,
                "execution_id": request.get("execution_id"),
                "case_id": request.get("case_id"),
                "reason": reason,
            },
        )

        return ApprovalDecisionResult(
            ok=True,
            approval_id=approval_id,
            status=APPROVAL_STATUS_REJECTED,
            message="Approval rejected.",
            action=request.get("action"),
            execution_id=request.get("execution_id"),
            case_id=request.get("case_id"),
            tenant_id=request.get("tenant_id"),
            rejected=True,
        )

    def emergency_override(
        self,
        approval_id: str,
        *,
        actor: str,
        reason: str,
        release_execution: bool = True,
    ) -> ApprovalDecisionResult:
        request = self.get_approval_request(approval_id)

        if not request:
            return ApprovalDecisionResult(
                ok=False,
                approval_id=approval_id,
                status="NOT_FOUND",
                message="Approval request not found.",
            )

        self._update_approval(
            approval_id,
            {
                "status": APPROVAL_STATUS_OVERRIDE_APPROVED,
                "approved_by": actor,
                "approved_at_ms": _now_ms(),
                "override_reason": reason,
            },
        )

        self._record_approval_event(
            approval_id=approval_id,
            tenant_id=request["tenant_id"],
            event_type="EMERGENCY_OVERRIDE_APPROVED",
            actor=actor,
            message="Emergency override approved.",
            details={"reason": reason},
        )

        _record_custody_event(
            self.storage,
            event_type="GOVERNANCE_EMERGENCY_OVERRIDE_APPROVED",
            actor=actor,
            tenant_id=request["tenant_id"],
            evidence_id=request.get("evidence_id"),
            case_id=request.get("case_id"),
            alert_id=request.get("alert_id"),
            execution_id=request.get("execution_id"),
            approval_id=approval_id,
            details={"reason": reason},
        )

        released = False
        if release_execution:
            released = self.release_execution(approval_id, actor=actor)

        return ApprovalDecisionResult(
            ok=True,
            approval_id=approval_id,
            status=APPROVAL_STATUS_OVERRIDE_APPROVED,
            message="Emergency override approved.",
            action=request.get("action"),
            execution_id=request.get("execution_id"),
            case_id=request.get("case_id"),
            tenant_id=request.get("tenant_id"),
            approved=True,
            executable=released,
            details={"override": True, "released": released},
        )

    def release_execution(self, approval_id: str, *, actor: str) -> bool:
        request = self.get_approval_request(approval_id)
        if not request:
            return False

        execution_id = request.get("execution_id")

        if not execution_id:
            self._record_approval_event(
                approval_id=approval_id,
                tenant_id=request["tenant_id"],
                event_type="APPROVAL_RELEASE_SKIPPED",
                actor=actor,
                message="No execution_id attached to approval.",
                details={},
            )
            return False

        if callable(self.execution_release_callback):
            try:
                self.execution_release_callback(
                    execution_id=execution_id,
                    approval_id=approval_id,
                    actor=actor,
                )
                self._record_approval_event(
                    approval_id=approval_id,
                    tenant_id=request["tenant_id"],
                    event_type="APPROVED_EXECUTION_RELEASED",
                    actor=actor,
                    message="Approved execution released through callback.",
                    details={"execution_id": execution_id},
                )
                return True
            except Exception as exc:
                self._record_approval_event(
                    approval_id=approval_id,
                    tenant_id=request["tenant_id"],
                    event_type="APPROVED_EXECUTION_RELEASE_FAILED",
                    actor=actor,
                    message=str(exc),
                    details={"execution_id": execution_id},
                )
                return False

        for method_name in [
            "release_approved_execution",
            "mark_execution_approved",
            "approve_execution",
        ]:
            fn = getattr(self.ledger, method_name, None)
            if callable(fn):
                try:
                    fn(execution_id=execution_id, approval_id=approval_id, actor=actor)
                    return True
                except TypeError:
                    try:
                        fn(execution_id, approval_id, actor)
                        return True
                    except Exception:
                        pass
                except Exception:
                    pass

        self._record_approval_event(
            approval_id=approval_id,
            tenant_id=request["tenant_id"],
            event_type="APPROVED_EXECUTION_RELEASE_RECORDED_ONLY",
            actor=actor,
            message="No release callback or ledger method configured.",
            details={"execution_id": execution_id},
        )
        return False

    def escalate_pending_approvals(
        self,
        *,
        tenant_id: Optional[str] = None,
        actor: str = "approval_engine",
        near_expiry_ms: int = 60 * 60 * 1000,
    ) -> List[Dict[str, Any]]:
        now = _now_ms()
        clauses = ["status = ?"]
        params: List[Any] = [APPROVAL_STATUS_PENDING]

        if tenant_id:
            clauses.append("tenant_id = ?")
            params.append(tenant_id)

        clauses.append("expires_at_ms <= ?")
        params.append(now + near_expiry_ms)

        rows = self.conn.execute(
            f"""
            SELECT *
            FROM governance_approval_requests
            WHERE {' AND '.join(clauses)}
            ORDER BY expires_at_ms ASC
            """,
            params,
        ).fetchall()

        escalated = []

        for row in rows:
            req = self._row_to_dict("governance_approval_requests", row)
            approval_id = req["approval_id"]

            self._update_approval(
                approval_id,
                {"status": APPROVAL_STATUS_ESCALATED},
            )

            self._record_approval_event(
                approval_id=approval_id,
                tenant_id=req["tenant_id"],
                event_type="APPROVAL_ESCALATED",
                actor=actor,
                message="Approval nearing expiry and escalated.",
                details={
                    "expires_at_ms": req.get("expires_at_ms"),
                    "near_expiry_ms": near_expiry_ms,
                },
            )

            escalated.append(req)

        return escalated

    def expire_stale_approvals(
        self,
        *,
        tenant_id: Optional[str] = None,
        actor: str = "approval_engine",
    ) -> List[Dict[str, Any]]:
        now = _now_ms()

        clauses = ["status IN (?, ?)"]
        params: List[Any] = [APPROVAL_STATUS_PENDING, APPROVAL_STATUS_ESCALATED]

        if tenant_id:
            clauses.append("tenant_id = ?")
            params.append(tenant_id)

        clauses.append("expires_at_ms <= ?")
        params.append(now)

        rows = self.conn.execute(
            f"""
            SELECT *
            FROM governance_approval_requests
            WHERE {' AND '.join(clauses)}
            """,
            params,
        ).fetchall()

        expired = []

        for row in rows:
            req = self._row_to_dict("governance_approval_requests", row)
            self.expire_approval(req["approval_id"], actor=actor)
            expired.append(req)

        return expired

    def expire_approval(self, approval_id: str, *, actor: str = "approval_engine") -> bool:
        request = self.get_approval_request(approval_id)

        if not request:
            return False

        if request["status"] not in {APPROVAL_STATUS_PENDING, APPROVAL_STATUS_ESCALATED}:
            return False

        self._update_approval(
            approval_id,
            {"status": APPROVAL_STATUS_EXPIRED},
        )

        self._record_approval_event(
            approval_id=approval_id,
            tenant_id=request["tenant_id"],
            event_type="APPROVAL_EXPIRED",
            actor=actor,
            message="Approval request expired.",
            details={},
        )

        return True

    def get_approval_request(self, approval_id: str) -> Optional[Dict[str, Any]]:
        row = self.conn.execute(
            """
            SELECT *
            FROM governance_approval_requests
            WHERE approval_id=?
            LIMIT 1
            """,
            (approval_id,),
        ).fetchone()

        if not row:
            return None

        return self._row_to_dict("governance_approval_requests", row)

    def list_pending_approvals(
        self,
        *,
        tenant_id: Optional[str] = None,
        review_type: Optional[str] = None,
        limit: int = 500,
    ) -> List[Dict[str, Any]]:
        clauses = ["status IN (?, ?)"]
        params: List[Any] = [APPROVAL_STATUS_PENDING, APPROVAL_STATUS_ESCALATED]

        if tenant_id:
            clauses.append("tenant_id = ?")
            params.append(tenant_id)

        if review_type:
            clauses.append("review_type = ?")
            params.append(review_type)

        rows = self.conn.execute(
            f"""
            SELECT *
            FROM governance_approval_requests
            WHERE {' AND '.join(clauses)}
            ORDER BY severity DESC, expires_at_ms ASC
            LIMIT ?
            """,
            (*params, limit),
        ).fetchall()

        return [
            self._row_to_dict("governance_approval_requests", row)
            for row in rows
        ]

    def list_approval_events(self, approval_id: str) -> List[Dict[str, Any]]:
        rows = self.conn.execute(
            """
            SELECT *
            FROM governance_approval_events
            WHERE approval_id=?
            ORDER BY created_at_ms ASC
            """,
            (approval_id,),
        ).fetchall()

        return [
            self._row_to_dict("governance_approval_events", row)
            for row in rows
        ]

    def _approval_is_complete(self, request: Dict[str, Any]) -> bool:
        if request.get("requires_legal") and not request.get("legal_approved"):
            return False

        if not request.get("approved_by"):
            return False

        if request.get("requires_dual_approval"):
            if not request.get("second_approved_by"):
                return False

            if request.get("second_approved_by") == request.get("approved_by"):
                return False

        return True

    def _is_expired(self, request: Dict[str, Any]) -> bool:
        expires_at = _safe_int(request.get("expires_at_ms"), 0)
        return bool(expires_at and expires_at <= _now_ms())

    def _update_approval(self, approval_id: str, updates: Dict[str, Any]) -> None:
        if not updates:
            return

        allowed = {
            "status",
            "approved_by",
            "approved_at_ms",
            "second_approved_by",
            "second_approved_at_ms",
            "rejected_by",
            "rejected_at_ms",
            "legal_reviewer",
            "legal_reviewed_at_ms",
            "legal_approved",
            "reason",
            "rejection_reason",
            "override_reason",
            "metadata_json",
        }

        clean = {k: v for k, v in updates.items() if k in allowed}
        clean["updated_at_ms"] = _now_ms()

        assignments = ", ".join([f"{k}=?" for k in clean.keys()])
        values = list(clean.values())

        self.conn.execute(
            f"""
            UPDATE governance_approval_requests
            SET {assignments}
            WHERE approval_id=?
            """,
            (*values, approval_id),
        )
        self.conn.commit()

    def _merge_metadata(self, existing_json: Any, patch: Dict[str, Any]) -> str:
        existing = _json_loads(existing_json)
        existing.update(patch or {})
        return _json_dumps(existing)

    def _record_approval_event(
        self,
        *,
        approval_id: str,
        tenant_id: str,
        event_type: str,
        actor: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        event_id = f"APREV-{uuid.uuid4().hex[:12].upper()}"

        self.conn.execute(
            """
            INSERT INTO governance_approval_events (
                event_id,
                approval_id,
                tenant_id,
                event_type,
                actor,
                message,
                details_json,
                created_at_ms
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                approval_id,
                tenant_id,
                event_type,
                actor,
                message,
                _json_dumps(details or {}),
                _now_ms(),
            ),
        )
        self.conn.commit()

        self._publish(
            event_type=event_type,
            tenant_id=tenant_id,
            payload={
                "approval_id": approval_id,
                "actor": actor,
                "message": message,
                "details": details or {},
            },
        )

    def _publish(
        self,
        *,
        event_type: str,
        tenant_id: str,
        payload: Dict[str, Any],
    ) -> None:
        if self.event_bus is None:
            return

        try:
            self.event_bus.publish(
                event_type=event_type,
                tenant_id=tenant_id,
                source="governance_approval_engine",
                payload=payload,
            )
        except TypeError:
            try:
                self.event_bus.publish(
                    event_type=event_type,
                    payload=payload,
                    tenant_id=tenant_id,
                    source="governance_approval_engine",
                )
            except Exception:
                pass
        except Exception:
            pass

    def _row_to_dict(self, table_name: str, row: Any) -> Dict[str, Any]:
        if row is None:
            return {}

        cols = [
            d[1]
            for d in self.conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        ]

        return dict(zip(cols, row))


def get_governance_approval_engine(
    storage: Any = None,
    *,
    event_bus: Any = None,
    execution_release_callback: Any = None,
) -> GovernanceApprovalEngine:
    return GovernanceApprovalEngine(
        storage=storage,
        event_bus=event_bus,
        execution_release_callback=execution_release_callback,
    )