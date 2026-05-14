"""
core/agents/agent_coordinator.py

Multi-Agent SOC Coordinator for Veridion Pro / CUI GovCloud App.
"""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, List, Optional


AGENT_GOVERNANCE = "governance_agent"
AGENT_CONTAINMENT = "containment_agent"
AGENT_VERIFICATION = "verification_agent"
AGENT_ROLLBACK = "rollback_agent"
AGENT_ESCALATION = "escalation_agent"
AGENT_EVIDENCE = "evidence_agent"
AGENT_HUNT = "hunt_agent"

STATUS_PENDING = "PENDING"
STATUS_RUNNING = "RUNNING"
STATUS_COMPLETED = "COMPLETED"
STATUS_FAILED = "FAILED"
STATUS_BLOCKED = "BLOCKED"
STATUS_ESCALATED = "ESCALATED"

EVENT_AGENT_TASK_CREATED = "AGENT_TASK_CREATED"
EVENT_AGENT_TASK_STARTED = "AGENT_TASK_STARTED"
EVENT_AGENT_TASK_COMPLETED = "AGENT_TASK_COMPLETED"
EVENT_AGENT_TASK_FAILED = "AGENT_TASK_FAILED"
EVENT_AGENT_COORDINATION_STARTED = "AGENT_COORDINATION_STARTED"

SEVERITY_INFO = "INFO"
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
        parsed = json.loads(value or "{}")
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}


def _get_ledger(storage_or_ledger: Any) -> Any:
    if storage_or_ledger is None:
        return None
    return getattr(storage_or_ledger, "ledger", storage_or_ledger)


@dataclass
class AgentTask:
    task_id: str
    agent_name: str
    task_type: str
    tenant_id: str = "default"
    case_id: Optional[Any] = None
    alert_id: Optional[Any] = None
    evidence_id: Optional[Any] = None
    execution_id: Optional[str] = None
    priority: str = SEVERITY_MEDIUM
    status: str = STATUS_PENDING
    payload: Dict[str, Any] = field(default_factory=dict)
    result: Dict[str, Any] = field(default_factory=dict)
    created_by: str = "agent_coordinator"
    created_at_ms: int = field(default_factory=_now_ms)
    updated_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AgentCoordinator:
    def __init__(self, storage: Any = None, *, event_bus: Any = None) -> None:
        self.storage = storage
        self.ledger = _get_ledger(storage)
        self.event_bus = event_bus or getattr(storage, "event_bus", None)
        self.db_path = self._resolve_db_path()

        self.handlers: Dict[str, Callable[[AgentTask], Dict[str, Any]]] = {}

        self.ensure_schema()
        self._register_default_handlers()

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
                CREATE TABLE IF NOT EXISTS agent_tasks (
                    task_id TEXT PRIMARY KEY,
                    agent_name TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    tenant_id TEXT DEFAULT 'default',
                    case_id TEXT,
                    alert_id TEXT,
                    evidence_id TEXT,
                    execution_id TEXT,
                    priority TEXT,
                    status TEXT,
                    payload_json TEXT,
                    result_json TEXT,
                    created_by TEXT,
                    created_at_ms INTEGER NOT NULL,
                    updated_at_ms INTEGER NOT NULL,
                    completed_at_ms INTEGER,
                    last_error TEXT
                )
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_agent_tasks_status
                ON agent_tasks(status)
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_agent_tasks_agent
                ON agent_tasks(agent_name)
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_agent_tasks_case
                ON agent_tasks(case_id)
                """
            )

            conn.commit()

    def _register_default_handlers(self) -> None:
        self.register_handler(AGENT_GOVERNANCE, self._handle_governance_task)
        self.register_handler(AGENT_CONTAINMENT, self._handle_containment_task)
        self.register_handler(AGENT_VERIFICATION, self._handle_verification_task)
        self.register_handler(AGENT_ROLLBACK, self._handle_rollback_task)
        self.register_handler(AGENT_ESCALATION, self._handle_escalation_task)
        self.register_handler(AGENT_EVIDENCE, self._handle_evidence_task)
        self.register_handler(AGENT_HUNT, self._handle_hunt_task)

    def register_handler(
        self,
        agent_name: str,
        handler: Callable[[AgentTask], Dict[str, Any]],
    ) -> None:
        self.handlers[agent_name] = handler

    def create_task(
        self,
        *,
        agent_name: str,
        task_type: str,
        payload: Optional[Dict[str, Any]] = None,
        tenant_id: str = "default",
        case_id: Optional[Any] = None,
        alert_id: Optional[Any] = None,
        evidence_id: Optional[Any] = None,
        execution_id: Optional[str] = None,
        priority: str = SEVERITY_MEDIUM,
        created_by: str = "agent_coordinator",
    ) -> AgentTask:
        task = AgentTask(
            task_id=f"AGT-{uuid.uuid4().hex[:12].upper()}",
            agent_name=agent_name,
            task_type=task_type,
            tenant_id=tenant_id or "default",
            case_id=case_id,
            alert_id=alert_id,
            evidence_id=evidence_id,
            execution_id=execution_id,
            priority=priority,
            payload=payload or {},
            created_by=created_by,
        )

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO agent_tasks (
                    task_id, agent_name, task_type, tenant_id,
                    case_id, alert_id, evidence_id, execution_id,
                    priority, status, payload_json, result_json,
                    created_by, created_at_ms, updated_at_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task.task_id,
                    task.agent_name,
                    task.task_type,
                    task.tenant_id,
                    str(task.case_id) if task.case_id is not None else None,
                    str(task.alert_id) if task.alert_id is not None else None,
                    str(task.evidence_id) if task.evidence_id is not None else None,
                    task.execution_id,
                    task.priority,
                    task.status,
                    _json_dumps(task.payload),
                    _json_dumps(task.result),
                    task.created_by,
                    task.created_at_ms,
                    task.updated_at_ms,
                ),
            )
            conn.commit()

        self._emit(
            EVENT_AGENT_TASK_CREATED,
            tenant_id=task.tenant_id,
            severity=task.priority,
            payload=task.to_dict(),
        )

        return task

    def coordinate_incident(
        self,
        *,
        tenant_id: str = "default",
        case_id: Optional[Any] = None,
        alert_id: Optional[Any] = None,
        evidence_id: Optional[Any] = None,
        detection: Optional[Dict[str, Any]] = None,
        severity: str = SEVERITY_MEDIUM,
        actor: str = "agent_coordinator",
    ) -> List[AgentTask]:
        detection = detection or {}

        self._emit(
            EVENT_AGENT_COORDINATION_STARTED,
            tenant_id=tenant_id,
            severity=severity,
            payload={
                "case_id": case_id,
                "alert_id": alert_id,
                "evidence_id": evidence_id,
                "detection": detection,
                "actor": actor,
            },
        )

        tasks = [
            self.create_task(
                agent_name=AGENT_GOVERNANCE,
                task_type="evaluate_governance",
                tenant_id=tenant_id,
                case_id=case_id,
                alert_id=alert_id,
                evidence_id=evidence_id,
                priority=severity,
                payload={"detection": detection},
                created_by=actor,
            ),
            self.create_task(
                agent_name=AGENT_EVIDENCE,
                task_type="preserve_and_enrich_evidence",
                tenant_id=tenant_id,
                case_id=case_id,
                alert_id=alert_id,
                evidence_id=evidence_id,
                priority=severity,
                payload={"detection": detection},
                created_by=actor,
            ),
            self.create_task(
                agent_name=AGENT_HUNT,
                task_type="hunt_related_activity",
                tenant_id=tenant_id,
                case_id=case_id,
                alert_id=alert_id,
                evidence_id=evidence_id,
                priority=severity,
                payload={"detection": detection},
                created_by=actor,
            ),
        ]

        if severity in {SEVERITY_HIGH, SEVERITY_CRITICAL}:
            tasks.append(
                self.create_task(
                    agent_name=AGENT_CONTAINMENT,
                    task_type="evaluate_containment",
                    tenant_id=tenant_id,
                    case_id=case_id,
                    alert_id=alert_id,
                    evidence_id=evidence_id,
                    priority=severity,
                    payload={"detection": detection},
                    created_by=actor,
                )
            )

        if severity == SEVERITY_CRITICAL:
            tasks.append(
                self.create_task(
                    agent_name=AGENT_ESCALATION,
                    task_type="escalate_critical_incident",
                    tenant_id=tenant_id,
                    case_id=case_id,
                    alert_id=alert_id,
                    evidence_id=evidence_id,
                    priority=severity,
                    payload={"detection": detection},
                    created_by=actor,
                )
            )

        return tasks

    def run_pending_tasks(
        self,
        *,
        limit: int = 25,
        agent_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        clauses = ["status=?"]
        params: List[Any] = [STATUS_PENDING]

        if agent_name:
            clauses.append("agent_name=?")
            params.append(agent_name)

        with self._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT *
                FROM agent_tasks
                WHERE {' AND '.join(clauses)}
                ORDER BY
                    CASE priority
                        WHEN 'CRITICAL' THEN 1
                        WHEN 'HIGH' THEN 2
                        WHEN 'MEDIUM' THEN 3
                        WHEN 'LOW' THEN 4
                        ELSE 5
                    END,
                    created_at_ms ASC
                LIMIT ?
                """,
                (*params, limit),
            ).fetchall()

            cols = self._table_cols(conn, "agent_tasks")

        results = []

        for row in rows:
            task = self._row_to_task(row, cols)
            results.append(self.run_task(task.task_id))

        return results

    def run_task(self, task_id: str) -> Dict[str, Any]:
        task = self.get_task(task_id)

        if task is None:
            return {
                "ok": False,
                "status": STATUS_FAILED,
                "message": "Task not found.",
                "task_id": task_id,
            }

        handler = self.handlers.get(task.agent_name)

        if handler is None:
            result = {
                "ok": False,
                "status": STATUS_FAILED,
                "message": f"No handler registered for {task.agent_name}.",
            }
            self._complete_task(task, result, status=STATUS_FAILED)
            return result

        self._update_task_status(task.task_id, STATUS_RUNNING)

        self._emit(
            EVENT_AGENT_TASK_STARTED,
            tenant_id=task.tenant_id,
            severity=task.priority,
            payload=task.to_dict(),
        )

        try:
            result = handler(task)
            status = STATUS_COMPLETED if result.get("ok", True) else STATUS_FAILED
            self._complete_task(task, result, status=status)
            return result

        except Exception as exc:
            result = {
                "ok": False,
                "status": STATUS_FAILED,
                "message": str(exc),
                "task_id": task.task_id,
            }
            self._complete_task(task, result, status=STATUS_FAILED, error=str(exc))
            return result

    def get_task(self, task_id: str) -> Optional[AgentTask]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM agent_tasks
                WHERE task_id=?
                LIMIT 1
                """,
                (task_id,),
            ).fetchone()

            if not row:
                return None

            cols = self._table_cols(conn, "agent_tasks")

        return self._row_to_task(row, cols)

    def list_tasks(
        self,
        *,
        status: Optional[str] = None,
        agent_name: Optional[str] = None,
        case_id: Optional[Any] = None,
        limit: int = 250,
    ) -> List[Dict[str, Any]]:
        clauses = []
        params: List[Any] = []

        if status:
            clauses.append("status=?")
            params.append(status)

        if agent_name:
            clauses.append("agent_name=?")
            params.append(agent_name)

        if case_id is not None:
            clauses.append("case_id=?")
            params.append(str(case_id))

        where = "WHERE " + " AND ".join(clauses) if clauses else ""

        with self._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT *
                FROM agent_tasks
                {where}
                ORDER BY updated_at_ms DESC
                LIMIT ?
                """,
                (*params, limit),
            ).fetchall()

            cols = self._table_cols(conn, "agent_tasks")

        return [
            self._task_to_dict(self._row_to_task(row, cols))
            for row in rows
        ]

    def _handle_governance_task(self, task: AgentTask) -> Dict[str, Any]:
        return {
            "ok": True,
            "agent": task.agent_name,
            "task_type": task.task_type,
            "message": "Governance task evaluated.",
            "recommendation": "Apply tenant policy, blast radius, and approval gates.",
        }

    def _handle_containment_task(self, task: AgentTask) -> Dict[str, Any]:
        detection = task.payload.get("detection") or {}
        actions = []

        if detection.get("endpoint_id") or detection.get("host_id"):
            actions.append("ISOLATE_ENDPOINT")

        if detection.get("user_id") or detection.get("principal"):
            actions.append("REVOKE_SESSIONS")

        return {
            "ok": True,
            "agent": task.agent_name,
            "task_type": task.task_type,
            "message": "Containment options evaluated.",
            "recommended_actions": actions,
        }

    def _handle_verification_task(self, task: AgentTask) -> Dict[str, Any]:
        try:
            from core.runtime.execution_verifier import get_execution_verifier

            verifier = get_execution_verifier(self.storage)
            due = verifier.run_due_verifications(limit=10, actor=AGENT_VERIFICATION)

            return {
                "ok": True,
                "agent": task.agent_name,
                "message": "Verification cycle completed.",
                "results": [
                    asdict(item) if hasattr(item, "__dataclass_fields__") else item
                    for item in due
                ],
            }
        except Exception as exc:
            return {
                "ok": False,
                "agent": task.agent_name,
                "message": str(exc),
            }

    def _handle_rollback_task(self, task: AgentTask) -> Dict[str, Any]:
        return {
            "ok": True,
            "agent": task.agent_name,
            "task_type": task.task_type,
            "message": "Rollback task evaluated.",
            "recommendation": "Trigger rollback orchestrator if rollback payload is present.",
        }

    def _handle_escalation_task(self, task: AgentTask) -> Dict[str, Any]:
        self._record_case_event(
            case_id=task.case_id,
            event_type="AGENT_ESCALATION_RECOMMENDED",
            actor=task.agent_name,
            details=task.to_dict(),
        )

        return {
            "ok": True,
            "agent": task.agent_name,
            "task_type": task.task_type,
            "message": "Escalation recommended.",
        }

    def _handle_evidence_task(self, task: AgentTask) -> Dict[str, Any]:
        self._record_case_event(
            case_id=task.case_id,
            event_type="AGENT_EVIDENCE_REVIEWED",
            actor=task.agent_name,
            details=task.to_dict(),
        )

        return {
            "ok": True,
            "agent": task.agent_name,
            "task_type": task.task_type,
            "message": "Evidence enrichment task completed.",
        }

    def _handle_hunt_task(self, task: AgentTask) -> Dict[str, Any]:
        return {
            "ok": True,
            "agent": task.agent_name,
            "task_type": task.task_type,
            "message": "Related activity hunt queued/evaluated.",
        }

    def _update_task_status(self, task_id: str, status: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE agent_tasks
                SET status=?, updated_at_ms=?
                WHERE task_id=?
                """,
                (status, _now_ms(), task_id),
            )
            conn.commit()

    def _complete_task(
        self,
        task: AgentTask,
        result: Dict[str, Any],
        *,
        status: str,
        error: Optional[str] = None,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE agent_tasks
                SET status=?,
                    result_json=?,
                    updated_at_ms=?,
                    completed_at_ms=?,
                    last_error=?
                WHERE task_id=?
                """,
                (
                    status,
                    _json_dumps(result),
                    _now_ms(),
                    _now_ms(),
                    error,
                    task.task_id,
                ),
            )
            conn.commit()

        event_type = (
            EVENT_AGENT_TASK_COMPLETED
            if status == STATUS_COMPLETED
            else EVENT_AGENT_TASK_FAILED
        )

        self._emit(
            event_type,
            tenant_id=task.tenant_id,
            severity=task.priority,
            payload={
                "task": task.to_dict(),
                "result": result,
                "status": status,
            },
        )

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

    def _row_to_task(
        self,
        row: Any,
        cols: List[str],
    ) -> AgentTask:
        data = dict(zip(cols, row))

        return AgentTask(
            task_id=data["task_id"],
            agent_name=data["agent_name"],
            task_type=data["task_type"],
            tenant_id=data.get("tenant_id") or "default",
            case_id=data.get("case_id"),
            alert_id=data.get("alert_id"),
            evidence_id=data.get("evidence_id"),
            execution_id=data.get("execution_id"),
            priority=data.get("priority") or SEVERITY_MEDIUM,
            status=data.get("status") or STATUS_PENDING,
            payload=_json_loads(data.get("payload_json")),
            result=_json_loads(data.get("result_json")),
            created_by=data.get("created_by") or "agent_coordinator",
            created_at_ms=int(data.get("created_at_ms") or _now_ms()),
            updated_at_ms=int(data.get("updated_at_ms") or _now_ms()),
        )

    def _task_to_dict(self, task: AgentTask) -> Dict[str, Any]:
        return task.to_dict()

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
                source="agent_coordinator",
                severity=severity,
                payload=payload,
            )
        except TypeError:
            try:
                self.event_bus.publish(
                    event_type=event_type,
                    payload=payload,
                    tenant_id=tenant_id,
                    source="agent_coordinator",
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


_DEFAULT_COORDINATOR: Optional[AgentCoordinator] = None


def get_agent_coordinator(
    storage: Any = None,
    *,
    reset: bool = False,
    event_bus: Any = None,
) -> AgentCoordinator:
    global _DEFAULT_COORDINATOR

    if reset or _DEFAULT_COORDINATOR is None:
        _DEFAULT_COORDINATOR = AgentCoordinator(
            storage=storage,
            event_bus=event_bus,
        )

    return _DEFAULT_COORDINATOR


def coordinate_incident(
    storage: Any,
    *,
    tenant_id: str = "default",
    case_id: Optional[Any] = None,
    alert_id: Optional[Any] = None,
    evidence_id: Optional[Any] = None,
    detection: Optional[Dict[str, Any]] = None,
    severity: str = SEVERITY_MEDIUM,
    actor: str = "agent_coordinator",
) -> List[AgentTask]:
    coordinator = get_agent_coordinator(storage)

    return coordinator.coordinate_incident(
        tenant_id=tenant_id,
        case_id=case_id,
        alert_id=alert_id,
        evidence_id=evidence_id,
        detection=detection,
        severity=severity,
        actor=actor,
    )