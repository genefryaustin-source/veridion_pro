"""
core/runtime/execution_verifier.py

Execution Verifier for Veridion Pro / CUI GovCloud App.

Purpose:
- Post-execution validation fabric
- Verify connector actions actually succeeded
- Retry transient/eventual-consistency checks
- Mark verification state
- Trigger rollback/escalation events when verification fails
- Emit realtime SOC/governance telemetry

Used by:
- autonomous_response_engine
- rollback_orchestrator
- governance workflows
- connectors
- live execution stream
"""

from __future__ import annotations

import json
import math
import sqlite3
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


# =============================================================================
# Verification States
# =============================================================================

VERIFY_PENDING = "PENDING"
VERIFY_RUNNING = "RUNNING"
VERIFY_VERIFIED = "VERIFIED"
VERIFY_FAILED = "FAILED"
VERIFY_DEGRADED = "DEGRADED"
VERIFY_TIMED_OUT = "TIMED_OUT"
VERIFY_ROLLBACK_REQUIRED = "ROLLBACK_REQUIRED"


# =============================================================================
# Event Types
# =============================================================================

EVENT_VERIFICATION_SCHEDULED = "VERIFICATION_SCHEDULED"
EVENT_VERIFICATION_STARTED = "VERIFICATION_STARTED"
EVENT_VERIFICATION_COMPLETED = "VERIFICATION_COMPLETED"
EVENT_VERIFICATION_FAILED = "VERIFICATION_FAILED"
EVENT_VERIFICATION_DEGRADED = "VERIFICATION_DEGRADED"
EVENT_VERIFICATION_TIMED_OUT = "VERIFICATION_TIMED_OUT"
EVENT_ROLLBACK_REQUIRED = "ROLLBACK_REQUIRED"


SEVERITY_INFO = "INFO"
SEVERITY_MEDIUM = "MEDIUM"
SEVERITY_HIGH = "HIGH"
SEVERITY_CRITICAL = "CRITICAL"


DEFAULT_MAX_ATTEMPTS = 5
DEFAULT_INITIAL_BACKOFF_MS = 2_000
DEFAULT_MAX_BACKOFF_MS = 60_000


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
    try:
        if value is None:
            return default
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


@dataclass
class VerificationRequest:
    verification_id: str
    tenant_id: str
    action: str
    connector_id: Optional[str] = None
    execution_id: Optional[str] = None
    rollback_id: Optional[str] = None
    case_id: Optional[Any] = None
    alert_id: Optional[Any] = None
    evidence_id: Optional[Any] = None

    status: str = VERIFY_PENDING
    attempts: int = 0
    max_attempts: int = DEFAULT_MAX_ATTEMPTS

    initial_backoff_ms: int = DEFAULT_INITIAL_BACKOFF_MS
    max_backoff_ms: int = DEFAULT_MAX_BACKOFF_MS
    next_attempt_ms: int = field(default_factory=_now_ms)

    payload: Dict[str, Any] = field(default_factory=dict)
    execution_result: Dict[str, Any] = field(default_factory=dict)

    created_by: str = "execution_verifier"
    created_at_ms: int = field(default_factory=_now_ms)
    updated_at_ms: int = field(default_factory=_now_ms)


@dataclass
class VerificationResult:
    ok: bool
    verification_id: str
    status: str
    message: str

    tenant_id: str = "default"
    action: Optional[str] = None
    connector_id: Optional[str] = None
    execution_id: Optional[str] = None
    rollback_required: bool = False
    attempts: int = 0

    raw: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)


class ExecutionVerifier:
    def __init__(
        self,
        storage: Any = None,
        *,
        event_bus: Any = None,
        connector_registry: Any = None,
    ) -> None:
        self.storage = storage
        self.ledger = _get_ledger(storage)
        self.conn = _get_connection(storage)
        self.event_bus = event_bus or getattr(storage, "event_bus", None)

        if connector_registry is None:
            try:
                from core.connectors.connector_registry import get_connector_registry
                connector_registry = get_connector_registry(
                    storage=storage,
                    event_bus=self.event_bus,
                )
            except Exception:
                connector_registry = None

        self.connector_registry = connector_registry
        self.ensure_schema()

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    def ensure_schema(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS execution_verifications (
                verification_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                action TEXT NOT NULL,
                connector_id TEXT,
                execution_id TEXT,
                rollback_id TEXT,
                case_id TEXT,
                alert_id TEXT,
                evidence_id TEXT,

                status TEXT NOT NULL,
                attempts INTEGER DEFAULT 0,
                max_attempts INTEGER DEFAULT 5,

                initial_backoff_ms INTEGER DEFAULT 2000,
                max_backoff_ms INTEGER DEFAULT 60000,
                next_attempt_ms INTEGER,

                payload_json TEXT,
                execution_result_json TEXT,
                last_result_json TEXT,
                last_error TEXT,

                created_by TEXT,
                created_at_ms INTEGER NOT NULL,
                updated_at_ms INTEGER NOT NULL,
                completed_at_ms INTEGER
            )
            """
        )

        self.conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_execution_verifications_status
            ON execution_verifications(status)
            """
        )

        self.conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_execution_verifications_next_attempt
            ON execution_verifications(next_attempt_ms)
            """
        )

        self.conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_execution_verifications_execution
            ON execution_verifications(execution_id)
            """
        )

        self.conn.commit()

    # ------------------------------------------------------------------
    # Scheduling
    # ------------------------------------------------------------------

    def schedule_verification(
        self,
        *,
        tenant_id: str,
        action: str,
        connector_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        rollback_id: Optional[str] = None,
        case_id: Optional[Any] = None,
        alert_id: Optional[Any] = None,
        evidence_id: Optional[Any] = None,
        payload: Optional[Dict[str, Any]] = None,
        execution_result: Optional[Dict[str, Any]] = None,
        created_by: str = "execution_verifier",
        delay_ms: int = 0,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        initial_backoff_ms: int = DEFAULT_INITIAL_BACKOFF_MS,
        max_backoff_ms: int = DEFAULT_MAX_BACKOFF_MS,
    ) -> VerificationRequest:
        verification_id = f"VER-{uuid.uuid4().hex[:12].upper()}"
        now = _now_ms()

        request = VerificationRequest(
            verification_id=verification_id,
            tenant_id=tenant_id or "default",
            action=_safe_str(action).upper(),
            connector_id=connector_id,
            execution_id=execution_id,
            rollback_id=rollback_id,
            case_id=case_id,
            alert_id=alert_id,
            evidence_id=evidence_id,
            status=VERIFY_PENDING,
            attempts=0,
            max_attempts=max_attempts,
            initial_backoff_ms=initial_backoff_ms,
            max_backoff_ms=max_backoff_ms,
            next_attempt_ms=now + max(0, int(delay_ms)),
            payload=payload or {},
            execution_result=execution_result or {},
            created_by=created_by,
            created_at_ms=now,
            updated_at_ms=now,
        )

        self.conn.execute(
            """
            INSERT INTO execution_verifications (
                verification_id,
                tenant_id,
                action,
                connector_id,
                execution_id,
                rollback_id,
                case_id,
                alert_id,
                evidence_id,
                status,
                attempts,
                max_attempts,
                initial_backoff_ms,
                max_backoff_ms,
                next_attempt_ms,
                payload_json,
                execution_result_json,
                created_by,
                created_at_ms,
                updated_at_ms
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request.verification_id,
                request.tenant_id,
                request.action,
                request.connector_id,
                request.execution_id,
                request.rollback_id,
                str(request.case_id) if request.case_id is not None else None,
                str(request.alert_id) if request.alert_id is not None else None,
                str(request.evidence_id) if request.evidence_id is not None else None,
                request.status,
                request.attempts,
                request.max_attempts,
                request.initial_backoff_ms,
                request.max_backoff_ms,
                request.next_attempt_ms,
                _json_dumps(request.payload),
                _json_dumps(request.execution_result),
                request.created_by,
                request.created_at_ms,
                request.updated_at_ms,
            ),
        )
        self.conn.commit()

        self._emit(
            EVENT_VERIFICATION_SCHEDULED,
            tenant_id=request.tenant_id,
            severity=SEVERITY_INFO,
            payload={
                "verification_id": verification_id,
                "execution_id": execution_id,
                "rollback_id": rollback_id,
                "connector_id": connector_id,
                "action": request.action,
                "case_id": case_id,
                "alert_id": alert_id,
                "evidence_id": evidence_id,
                "next_attempt_ms": request.next_attempt_ms,
            },
        )

        self._record_case_event(
            case_id=case_id,
            event_type=EVENT_VERIFICATION_SCHEDULED,
            actor=created_by,
            details={
                "verification_id": verification_id,
                "action": request.action,
                "connector_id": connector_id,
                "execution_id": execution_id,
            },
        )

        return request

    # ------------------------------------------------------------------
    # Verification Execution
    # ------------------------------------------------------------------

    def run_due_verifications(self, *, limit: int = 50, actor: str = "execution_verifier") -> List[VerificationResult]:
        now = _now_ms()

        rows = self.conn.execute(
            """
            SELECT *
            FROM execution_verifications
            WHERE status IN (?, ?, ?)
              AND next_attempt_ms <= ?
            ORDER BY next_attempt_ms ASC
            LIMIT ?
            """,
            (
                VERIFY_PENDING,
                VERIFY_RUNNING,
                VERIFY_DEGRADED,
                now,
                limit,
            ),
        ).fetchall()

        results: List[VerificationResult] = []

        for row in rows:
            req = self._row_to_dict(row)
            results.append(
                self.verify_now(
                    verification_id=req["verification_id"],
                    actor=actor,
                )
            )

        return results

    def verify_now(self, *, verification_id: str, actor: str = "execution_verifier") -> VerificationResult:
        request = self.get_verification(verification_id)

        if not request:
            return VerificationResult(
                ok=False,
                verification_id=verification_id,
                status=VERIFY_FAILED,
                message="Verification request not found.",
            )

        if request["status"] in {VERIFY_VERIFIED, VERIFY_FAILED, VERIFY_TIMED_OUT, VERIFY_ROLLBACK_REQUIRED}:
            return VerificationResult(
                ok=request["status"] == VERIFY_VERIFIED,
                verification_id=verification_id,
                status=request["status"],
                message=f"Verification already terminal: {request['status']}",
                tenant_id=request.get("tenant_id") or "default",
                action=request.get("action"),
                connector_id=request.get("connector_id"),
                execution_id=request.get("execution_id"),
                attempts=_safe_int(request.get("attempts")),
            )

        attempts = _safe_int(request.get("attempts"), 0) + 1

        self._update(
            verification_id,
            {
                "status": VERIFY_RUNNING,
                "attempts": attempts,
                "updated_at_ms": _now_ms(),
            },
        )

        self._emit(
            EVENT_VERIFICATION_STARTED,
            tenant_id=request.get("tenant_id") or "default",
            severity=SEVERITY_INFO,
            payload={
                "verification_id": verification_id,
                "execution_id": request.get("execution_id"),
                "connector_id": request.get("connector_id"),
                "action": request.get("action"),
                "attempts": attempts,
                "case_id": request.get("case_id"),
            },
        )

        try:
            result = self._perform_connector_verification(
                request=request,
                actor=actor,
            )

            if result.ok:
                self._mark_verified(verification_id, result)
                return result

            max_attempts = _safe_int(request.get("max_attempts"), DEFAULT_MAX_ATTEMPTS)

            if attempts >= max_attempts:
                terminal = self._mark_failed_or_rollback_required(
                    verification_id=verification_id,
                    request=request,
                    result=result,
                    actor=actor,
                )
                return terminal

            backoff = self._calculate_backoff_ms(
                attempts=attempts,
                initial_backoff_ms=_safe_int(request.get("initial_backoff_ms"), DEFAULT_INITIAL_BACKOFF_MS),
                max_backoff_ms=_safe_int(request.get("max_backoff_ms"), DEFAULT_MAX_BACKOFF_MS),
            )

            next_attempt_ms = _now_ms() + backoff

            self._update(
                verification_id,
                {
                    "status": VERIFY_DEGRADED,
                    "next_attempt_ms": next_attempt_ms,
                    "last_result_json": _json_dumps(result.raw),
                    "last_error": result.message,
                    "updated_at_ms": _now_ms(),
                },
            )

            self._emit(
                EVENT_VERIFICATION_DEGRADED,
                tenant_id=request.get("tenant_id") or "default",
                severity=SEVERITY_MEDIUM,
                payload={
                    "verification_id": verification_id,
                    "execution_id": request.get("execution_id"),
                    "connector_id": request.get("connector_id"),
                    "action": request.get("action"),
                    "attempts": attempts,
                    "next_attempt_ms": next_attempt_ms,
                    "message": result.message,
                    "case_id": request.get("case_id"),
                },
            )

            return VerificationResult(
                ok=False,
                verification_id=verification_id,
                status=VERIFY_DEGRADED,
                message=f"Verification degraded; retry scheduled in {backoff}ms.",
                tenant_id=request.get("tenant_id") or "default",
                action=request.get("action"),
                connector_id=request.get("connector_id"),
                execution_id=request.get("execution_id"),
                attempts=attempts,
                raw={"last_result": result.raw, "next_attempt_ms": next_attempt_ms},
            )

        except Exception as exc:
            result = VerificationResult(
                ok=False,
                verification_id=verification_id,
                status=VERIFY_FAILED,
                message=str(exc),
                tenant_id=request.get("tenant_id") or "default",
                action=request.get("action"),
                connector_id=request.get("connector_id"),
                execution_id=request.get("execution_id"),
                attempts=attempts,
                raw={"error": str(exc)},
            )

            if attempts >= _safe_int(request.get("max_attempts"), DEFAULT_MAX_ATTEMPTS):
                return self._mark_failed_or_rollback_required(
                    verification_id=verification_id,
                    request=request,
                    result=result,
                    actor=actor,
                )

            backoff = self._calculate_backoff_ms(
                attempts=attempts,
                initial_backoff_ms=_safe_int(request.get("initial_backoff_ms"), DEFAULT_INITIAL_BACKOFF_MS),
                max_backoff_ms=_safe_int(request.get("max_backoff_ms"), DEFAULT_MAX_BACKOFF_MS),
            )

            self._update(
                verification_id,
                {
                    "status": VERIFY_DEGRADED,
                    "next_attempt_ms": _now_ms() + backoff,
                    "last_error": str(exc),
                    "last_result_json": _json_dumps(result.raw),
                    "updated_at_ms": _now_ms(),
                },
            )

            return result

    def _perform_connector_verification(
        self,
        *,
        request: Dict[str, Any],
        actor: str,
    ) -> VerificationResult:
        tenant_id = request.get("tenant_id") or "default"
        connector_id = request.get("connector_id")
        action = request.get("action")
        payload = _json_loads(request.get("payload_json"))
        execution_result_json = _json_loads(request.get("execution_result_json"))

        if not self.connector_registry:
            return VerificationResult(
                ok=False,
                verification_id=request["verification_id"],
                status=VERIFY_FAILED,
                message="Connector registry unavailable.",
                tenant_id=tenant_id,
                action=action,
                connector_id=connector_id,
                execution_id=request.get("execution_id"),
            )

        connector = None

        if connector_id:
            connector = self.connector_registry.get_connector(
                connector_id,
                tenant_id=tenant_id,
            )

        if connector is None:
            resolution = self.connector_registry.resolve(
                action=action,
                tenant_id=tenant_id,
            )
            connector = resolution.connector if resolution.ok else None
            connector_id = resolution.connector_id if resolution.ok else connector_id

        if connector is None:
            return VerificationResult(
                ok=False,
                verification_id=request["verification_id"],
                status=VERIFY_FAILED,
                message=f"No connector available to verify action {action}.",
                tenant_id=tenant_id,
                action=action,
                connector_id=connector_id,
                execution_id=request.get("execution_id"),
            )

        execution_result_obj = self._build_execution_result_stub(
            connector=connector,
            action=action,
            execution_id=request.get("execution_id"),
            execution_result_json=execution_result_json,
        )

        verify_result = connector.verify(
            action=action,
            payload=payload,
            execution_result=execution_result_obj,
            actor=actor,
        )

        ok = bool(getattr(verify_result, "ok", False))

        return VerificationResult(
            ok=ok,
            verification_id=request["verification_id"],
            status=VERIFY_VERIFIED if ok else VERIFY_FAILED,
            message=getattr(verify_result, "message", "Verification completed."),
            tenant_id=tenant_id,
            action=action,
            connector_id=connector_id,
            execution_id=request.get("execution_id"),
            rollback_required=not ok,
            attempts=_safe_int(request.get("attempts"), 0),
            raw=verify_result.to_dict() if hasattr(verify_result, "to_dict") else dict(getattr(verify_result, "__dict__", {})),
        )

    def _build_execution_result_stub(
        self,
        *,
        connector: Any,
        action: str,
        execution_id: Optional[str],
        execution_result_json: Dict[str, Any],
    ) -> Any:
        try:
            from core.connectors.base_connector import ConnectorExecutionResult, STATUS_COMPLETED

            return ConnectorExecutionResult(
                ok=bool(execution_result_json.get("ok", True)),
                connector_id=connector.connector_id,
                action=action,
                status=execution_result_json.get("status") or STATUS_COMPLETED,
                message=execution_result_json.get("message") or "Execution result for verification.",
                execution_id=execution_id or execution_result_json.get("execution_id"),
                tenant_id=getattr(connector, "tenant_id", "default"),
                target_id=execution_result_json.get("target_id"),
                simulated=bool(execution_result_json.get("simulated", getattr(connector, "simulation_mode", True))),
                verification_ok=execution_result_json.get("verification_ok"),
                rollback_available=bool(execution_result_json.get("rollback_available")),
                rollback_payload=execution_result_json.get("rollback_payload") or {},
                raw=execution_result_json.get("raw") or execution_result_json,
            )
        except Exception:
            class _Stub:
                pass

            stub = _Stub()
            stub.ok = bool(execution_result_json.get("ok", True))
            stub.connector_id = getattr(connector, "connector_id", None)
            stub.action = action
            stub.status = execution_result_json.get("status")
            stub.message = execution_result_json.get("message")
            stub.execution_id = execution_id
            stub.tenant_id = getattr(connector, "tenant_id", "default")
            stub.target_id = execution_result_json.get("target_id")
            stub.simulated = bool(execution_result_json.get("simulated", True))
            stub.rollback_payload = execution_result_json.get("rollback_payload") or {}
            return stub

    # ------------------------------------------------------------------
    # Terminal State Updates
    # ------------------------------------------------------------------

    def _mark_verified(self, verification_id: str, result: VerificationResult) -> None:
        self._update(
            verification_id,
            {
                "status": VERIFY_VERIFIED,
                "last_result_json": _json_dumps(result.raw),
                "last_error": None,
                "updated_at_ms": _now_ms(),
                "completed_at_ms": _now_ms(),
            },
        )

        self._emit(
            EVENT_VERIFICATION_COMPLETED,
            tenant_id=result.tenant_id,
            severity=SEVERITY_INFO,
            payload={
                "verification_id": verification_id,
                "execution_id": result.execution_id,
                "connector_id": result.connector_id,
                "action": result.action,
                "message": result.message,
                "status": VERIFY_VERIFIED,
            },
        )

        self._record_case_event(
            case_id=self._get_case_id(verification_id),
            event_type=EVENT_VERIFICATION_COMPLETED,
            actor="execution_verifier",
            details=asdict(result),
        )

    def _mark_failed_or_rollback_required(
        self,
        *,
        verification_id: str,
        request: Dict[str, Any],
        result: VerificationResult,
        actor: str,
    ) -> VerificationResult:
        rollback_payload = self._extract_rollback_payload(request, result)
        rollback_required = bool(rollback_payload)

        status = VERIFY_ROLLBACK_REQUIRED if rollback_required else VERIFY_FAILED

        self._update(
            verification_id,
            {
                "status": status,
                "last_result_json": _json_dumps(result.raw),
                "last_error": result.message,
                "updated_at_ms": _now_ms(),
                "completed_at_ms": _now_ms(),
            },
        )

        event_type = EVENT_ROLLBACK_REQUIRED if rollback_required else EVENT_VERIFICATION_FAILED
        severity = SEVERITY_CRITICAL if rollback_required else SEVERITY_HIGH

        payload = {
            "verification_id": verification_id,
            "execution_id": request.get("execution_id"),
            "rollback_id": request.get("rollback_id"),
            "connector_id": request.get("connector_id"),
            "action": request.get("action"),
            "case_id": request.get("case_id"),
            "alert_id": request.get("alert_id"),
            "evidence_id": request.get("evidence_id"),
            "message": result.message,
            "status": status,
            "rollback_required": rollback_required,
            "rollback_payload": rollback_payload,
        }

        self._emit(
            event_type,
            tenant_id=request.get("tenant_id") or "default",
            severity=severity,
            payload=payload,
        )

        self._record_case_event(
            case_id=request.get("case_id"),
            event_type=event_type,
            actor=actor,
            details=payload,
        )

        self._record_custody_event(
            event_type=event_type,
            actor=actor,
            tenant_id=request.get("tenant_id") or "default",
            evidence_id=request.get("evidence_id"),
            case_id=request.get("case_id"),
            alert_id=request.get("alert_id"),
            execution_id=request.get("execution_id"),
            rollback_id=request.get("rollback_id"),
            details=payload,
        )

        return VerificationResult(
            ok=False,
            verification_id=verification_id,
            status=status,
            message=result.message,
            tenant_id=request.get("tenant_id") or "default",
            action=request.get("action"),
            connector_id=request.get("connector_id"),
            execution_id=request.get("execution_id"),
            rollback_required=rollback_required,
            attempts=_safe_int(request.get("attempts"), 0),
            raw=payload,
        )

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def get_verification(self, verification_id: str) -> Optional[Dict[str, Any]]:
        row = self.conn.execute(
            """
            SELECT *
            FROM execution_verifications
            WHERE verification_id=?
            LIMIT 1
            """,
            (verification_id,),
        ).fetchone()

        if not row:
            return None

        return self._row_to_dict(row)

    def list_verifications(
        self,
        *,
        status: Optional[str] = None,
        tenant_id: Optional[str] = None,
        limit: int = 500,
    ) -> List[Dict[str, Any]]:
        clauses = []
        params: List[Any] = []

        if status:
            clauses.append("status=?")
            params.append(status)

        if tenant_id:
            clauses.append("tenant_id=?")
            params.append(tenant_id)

        where = "WHERE " + " AND ".join(clauses) if clauses else ""

        rows = self.conn.execute(
            f"""
            SELECT *
            FROM execution_verifications
            {where}
            ORDER BY updated_at_ms DESC
            LIMIT ?
            """,
            (*params, limit),
        ).fetchall()

        return [self._row_to_dict(row) for row in rows]

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def _calculate_backoff_ms(
        self,
        *,
        attempts: int,
        initial_backoff_ms: int,
        max_backoff_ms: int,
    ) -> int:
        value = int(initial_backoff_ms * math.pow(2, max(0, attempts - 1)))
        return min(value, max_backoff_ms)

    def _extract_rollback_payload(self, request: Dict[str, Any], result: VerificationResult) -> Dict[str, Any]:
        execution_result = _json_loads(request.get("execution_result_json"))
        rollback_payload = execution_result.get("rollback_payload") or {}

        if rollback_payload:
            return rollback_payload

        raw = result.raw or {}
        return raw.get("rollback_payload") or {}

    def _update(self, verification_id: str, updates: Dict[str, Any]) -> None:
        if not updates:
            return

        allowed = {
            "status",
            "attempts",
            "next_attempt_ms",
            "last_result_json",
            "last_error",
            "updated_at_ms",
            "completed_at_ms",
        }

        clean = {k: v for k, v in updates.items() if k in allowed}

        if not clean:
            return

        assignments = ", ".join([f"{k}=?" for k in clean.keys()])
        values = list(clean.values())

        self.conn.execute(
            f"""
            UPDATE execution_verifications
            SET {assignments}
            WHERE verification_id=?
            """,
            (*values, verification_id),
        )
        self.conn.commit()

    def _row_to_dict(self, row: Any) -> Dict[str, Any]:
        cols = [
            d[1]
            for d in self.conn.execute("PRAGMA table_info(execution_verifications)").fetchall()
        ]
        return dict(zip(cols, row))

    def _get_case_id(self, verification_id: str) -> Optional[Any]:
        request = self.get_verification(verification_id)
        if not request:
            return None
        return request.get("case_id")

    # ------------------------------------------------------------------
    # Audit / Events
    # ------------------------------------------------------------------

    def _emit(
        self,
        event_type: str,
        *,
        tenant_id: str,
        payload: Dict[str, Any],
        severity: str = SEVERITY_INFO,
    ) -> None:
        if self.event_bus is None:
            return

        try:
            self.event_bus.publish(
                event_type=event_type,
                tenant_id=tenant_id,
                source="execution_verifier",
                severity=severity,
                payload=payload,
            )
        except TypeError:
            try:
                self.event_bus.publish(
                    event_type=event_type,
                    payload=payload,
                    tenant_id=tenant_id,
                    source="execution_verifier",
                )
            except Exception:
                pass
        except Exception:
            pass

    def _record_case_event(
        self,
        *,
        case_id: Any,
        event_type: str,
        actor: str,
        details: Dict[str, Any],
    ) -> None:
        if self.ledger is None or not case_id:
            return

        for method_name in ("add_case_event", "record_case_event", "create_case_event"):
            fn = getattr(self.ledger, method_name, None)
            if not callable(fn):
                continue

            try:
                fn(
                    case_id=case_id,
                    event_type=event_type,
                    actor=actor,
                    details=details,
                )
                return
            except TypeError:
                try:
                    fn(case_id, event_type, actor, details)
                    return
                except Exception:
                    pass
            except Exception:
                pass

    def _record_custody_event(
        self,
        *,
        event_type: str,
        actor: str,
        tenant_id: str,
        evidence_id: Any = None,
        case_id: Any = None,
        alert_id: Any = None,
        execution_id: Any = None,
        rollback_id: Any = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.ledger is None:
            return

        fn = getattr(self.ledger, "record_custody_event", None)
        if not callable(fn):
            return

        payload = {
            "tenant_id": tenant_id,
            "case_id": case_id,
            "alert_id": alert_id,
            "execution_id": execution_id,
            "rollback_id": rollback_id,
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
                fn(None, evidence_id, event_type, actor, _now_ms(), payload)
            except Exception:
                pass
        except Exception:
            pass


# =============================================================================
# Global / Convenience
# =============================================================================

_DEFAULT_VERIFIER: Optional[ExecutionVerifier] = None


def get_execution_verifier(
    storage: Any = None,
    *,
    reset: bool = False,
    event_bus: Any = None,
    connector_registry: Any = None,
) -> ExecutionVerifier:
    global _DEFAULT_VERIFIER

    if reset or _DEFAULT_VERIFIER is None:
        _DEFAULT_VERIFIER = ExecutionVerifier(
            storage=storage,
            event_bus=event_bus,
            connector_registry=connector_registry,
        )

    return _DEFAULT_VERIFIER


def schedule_verification(
    storage: Any,
    *,
    tenant_id: str,
    action: str,
    connector_id: Optional[str] = None,
    execution_id: Optional[str] = None,
    rollback_id: Optional[str] = None,
    case_id: Optional[Any] = None,
    alert_id: Optional[Any] = None,
    evidence_id: Optional[Any] = None,
    payload: Optional[Dict[str, Any]] = None,
    execution_result: Optional[Dict[str, Any]] = None,
    created_by: str = "execution_verifier",
) -> VerificationRequest:
    verifier = get_execution_verifier(storage)
    return verifier.schedule_verification(
        tenant_id=tenant_id,
        action=action,
        connector_id=connector_id,
        execution_id=execution_id,
        rollback_id=rollback_id,
        case_id=case_id,
        alert_id=alert_id,
        evidence_id=evidence_id,
        payload=payload,
        execution_result=execution_result,
        created_by=created_by,
    )


def run_due_verifications(
    storage: Any,
    *,
    limit: int = 50,
    actor: str = "execution_verifier",
) -> List[VerificationResult]:
    verifier = get_execution_verifier(storage)
    return verifier.run_due_verifications(limit=limit, actor=actor)