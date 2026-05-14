"""
core/ai/orchestration/mission_execution_engine.py

Autonomous Mission Execution Engine for Veridion Pro / CUI GovCloud App.

Purpose:
- Execute mission_planner.py mission graphs
- Respect dependency order
- Gate on approval-required steps
- Block unsafe steps
- Delegate agent work to AgentCoordinator / DistributedAgentFabric
- Execute connector actions where appropriate
- Schedule verification
- Create rollback records
- Emit mission telemetry
"""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Set


MISSION_RUNNING = "RUNNING"
MISSION_COMPLETED = "COMPLETED"
MISSION_FAILED = "FAILED"
MISSION_BLOCKED = "BLOCKED"
MISSION_APPROVAL_REQUIRED = "APPROVAL_REQUIRED"

STEP_PENDING = "PENDING"
STEP_READY = "READY"
STEP_RUNNING = "RUNNING"
STEP_COMPLETED = "COMPLETED"
STEP_FAILED = "FAILED"
STEP_BLOCKED = "BLOCKED"
STEP_APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
STEP_SKIPPED = "SKIPPED"

EVENT_MISSION_EXECUTION_STARTED = "MISSION_EXECUTION_STARTED"
EVENT_MISSION_STEP_STARTED = "MISSION_STEP_STARTED"
EVENT_MISSION_STEP_COMPLETED = "MISSION_STEP_COMPLETED"
EVENT_MISSION_STEP_FAILED = "MISSION_STEP_FAILED"
EVENT_MISSION_STEP_BLOCKED = "MISSION_STEP_BLOCKED"
EVENT_MISSION_STEP_APPROVAL_REQUIRED = "MISSION_STEP_APPROVAL_REQUIRED"
EVENT_MISSION_EXECUTION_COMPLETED = "MISSION_EXECUTION_COMPLETED"
EVENT_MISSION_EXECUTION_FAILED = "MISSION_EXECUTION_FAILED"

AGENT_STEP_TYPES = {
    "evidence",
    "governance",
    "hunt",
    "verification",
}

CONNECTOR_STEP_TYPES = {
    "containment",
    "identity",
    "mailbox",
    "drive",
    "endpoint",
}

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


def _json_loads(value: Any) -> Any:
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value or "{}")
    except Exception:
        return {}


def _upper(value: Any, default: str = "") -> str:
    try:
        return str(value or default).upper()
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
            path = getattr(ledger, attr, None)
            if path:
                return sqlite3.connect(path, check_same_thread=False)

        connect_fn = getattr(ledger, "_connect", None)
        if callable(connect_fn):
            try:
                return connect_fn()
            except Exception:
                pass

    return sqlite3.connect("data/ledger.db", check_same_thread=False)


@dataclass
class MissionExecutionResult:
    ok: bool
    mission_id: str
    status: str
    message: str
    execution_id: str
    completed_steps: int = 0
    failed_steps: int = 0
    blocked_steps: int = 0
    approval_required_steps: int = 0
    results: List[Dict[str, Any]] = field(default_factory=list)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MissionExecutionEngine:
    def __init__(self, storage: Any = None, *, event_bus: Any = None) -> None:
        self.storage = storage
        self.ledger = _get_ledger(storage)
        self.db_path = self._resolve_db_path()
        self.event_bus = event_bus or getattr(storage, "event_bus", None)
        self.ensure_schema()

    def _resolve_db_path(self) -> str:

        ledger = self.ledger

        if ledger is not None:

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

            conn.execute(
                "PRAGMA journal_mode=WAL;"
            )

            conn.execute(
                "PRAGMA synchronous=NORMAL;"
            )

            conn.execute(
                "PRAGMA foreign_keys=ON;"
            )

        except Exception:
            pass

        return conn
    def ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS mission_executions (
                    execution_id TEXT PRIMARY KEY,
                    mission_id TEXT NOT NULL,
                    tenant_id TEXT DEFAULT 'default',
                    status TEXT,
                    result_json TEXT,
                    created_by TEXT,
                    created_at_ms INTEGER NOT NULL,
                    updated_at_ms INTEGER NOT NULL,
                    completed_at_ms INTEGER
                )
                """
            )

        with self._connect() as conn:
            conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mission_step_executions (
                step_execution_id TEXT PRIMARY KEY,
                execution_id TEXT NOT NULL,
                mission_id TEXT NOT NULL,
                step_id TEXT NOT NULL,
                sequence INTEGER,
                step_type TEXT,
                action TEXT,
                status TEXT,
                result_json TEXT,
                started_at_ms INTEGER,
                completed_at_ms INTEGER,
                updated_at_ms INTEGER NOT NULL,
                last_error TEXT
            )
            """
        )

        with self._connect() as conn:
            conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_mission_exec_mission
            ON mission_executions(mission_id)
            """
        )

        with self._connect() as conn:
            conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_mission_step_exec_execution
            ON mission_step_executions(execution_id)
            """
        )

        conn.commit()

    # ------------------------------------------------------------------
    # Main execution
    # ------------------------------------------------------------------

    def execute_mission(
        self,
        mission_id: str,
        *,
        actor: str = "mission_execution_engine",
        dry_run: bool = False,
        max_steps: int = 100,
    ) -> MissionExecutionResult:
        mission = self._get_mission(mission_id)

        if not mission:
            return MissionExecutionResult(
                ok=False,
                mission_id=mission_id,
                status=MISSION_FAILED,
                message="Mission not found.",
                execution_id=f"MEX-{uuid.uuid4().hex[:12].upper()}",
            )

        execution_id = f"MEX-{uuid.uuid4().hex[:12].upper()}"
        tenant_id = mission.get("tenant_id") or "default"
        severity = mission.get("severity") or SEVERITY_MEDIUM

        self._create_execution(
            execution_id=execution_id,
            mission_id=mission_id,
            tenant_id=tenant_id,
            actor=actor,
        )

        self._set_mission_status(mission_id, MISSION_RUNNING)

        self._emit(
            EVENT_MISSION_EXECUTION_STARTED,
            tenant_id=tenant_id,
            severity=severity,
            payload={
                "execution_id": execution_id,
                "mission_id": mission_id,
                "actor": actor,
                "dry_run": dry_run,
            },
        )

        steps = self._get_steps(mission_id)
        completed: Set[str] = set()
        failed_steps = 0
        blocked_steps = 0
        approval_steps = 0
        results: List[Dict[str, Any]] = []

        for _ in range(max_steps):
            ready = self._find_ready_steps(steps, completed)

            if not ready:
                break

            progressed = False

            for step in ready:
                result = self._execute_step(
                    execution_id=execution_id,
                    mission=mission,
                    step=step,
                    actor=actor,
                    dry_run=dry_run,
                )

                results.append(result)

                if result.get("status") == STEP_COMPLETED:
                    completed.add(step["step_id"])
                    progressed = True

                elif result.get("status") == STEP_APPROVAL_REQUIRED:
                    approval_steps += 1
                    progressed = True

                elif result.get("status") == STEP_BLOCKED:
                    blocked_steps += 1
                    progressed = True

                elif result.get("status") == STEP_FAILED:
                    failed_steps += 1
                    progressed = True

            if not progressed:
                break

        total_steps = len(steps)
        completed_count = len(completed)

        if blocked_steps:
            final_status = MISSION_BLOCKED
            ok = False
            message = "Mission blocked by one or more steps."
            event_type = EVENT_MISSION_EXECUTION_FAILED
        elif failed_steps:
            final_status = MISSION_FAILED
            ok = False
            message = "Mission failed due to one or more failed steps."
            event_type = EVENT_MISSION_EXECUTION_FAILED
        elif approval_steps:
            final_status = MISSION_APPROVAL_REQUIRED
            ok = False
            message = "Mission paused because one or more steps require approval."
            event_type = EVENT_MISSION_STEP_APPROVAL_REQUIRED
        elif completed_count >= total_steps:
            final_status = MISSION_COMPLETED
            ok = True
            message = "Mission execution completed."
            event_type = EVENT_MISSION_EXECUTION_COMPLETED
        else:
            final_status = MISSION_RUNNING
            ok = True
            message = "Mission execution partially progressed."
            event_type = EVENT_MISSION_EXECUTION_STARTED

        final = MissionExecutionResult(
            ok=ok,
            mission_id=mission_id,
            status=final_status,
            message=message,
            execution_id=execution_id,
            completed_steps=completed_count,
            failed_steps=failed_steps,
            blocked_steps=blocked_steps,
            approval_required_steps=approval_steps,
            results=results,
        )

        self._complete_execution(execution_id, final.to_dict(), final_status)
        self._set_mission_status(mission_id, final_status)

        self._emit(
            event_type,
            tenant_id=tenant_id,
            severity=severity,
            payload=final.to_dict(),
        )

        return final

    # ------------------------------------------------------------------
    # Step execution
    # ------------------------------------------------------------------

    def _execute_step(
        self,
        *,
        execution_id: str,
        mission: Dict[str, Any],
        step: Dict[str, Any],
        actor: str,
        dry_run: bool,
    ) -> Dict[str, Any]:
        step_execution_id = f"MSTEP-{uuid.uuid4().hex[:12].upper()}"
        tenant_id = mission.get("tenant_id") or "default"
        severity = mission.get("severity") or SEVERITY_MEDIUM
        mission_id = mission["mission_id"]

        status = step.get("status") or STEP_PENDING
        action = _upper(step.get("action"))
        step_type = str(step.get("step_type") or "").lower()

        if status == STEP_BLOCKED:
            result = {
                "ok": False,
                "status": STEP_BLOCKED,
                "message": "Step is blocked.",
                "step_id": step["step_id"],
            }
            self._record_step_execution(step_execution_id, execution_id, mission_id, step, result)
            self._emit_step(EVENT_MISSION_STEP_BLOCKED, tenant_id, severity, execution_id, step, result)
            return result

        if status == STEP_APPROVAL_REQUIRED or bool(step.get("requires_approval")):
            result = {
                "ok": False,
                "status": STEP_APPROVAL_REQUIRED,
                "message": "Step requires approval before execution.",
                "step_id": step["step_id"],
            }
            self._record_step_execution(step_execution_id, execution_id, mission_id, step, result)
            self._emit_step(EVENT_MISSION_STEP_APPROVAL_REQUIRED, tenant_id, severity, execution_id, step, result)
            return result

        self._record_step_start(step_execution_id, execution_id, mission_id, step)

        self._emit_step(
            EVENT_MISSION_STEP_STARTED,
            tenant_id,
            severity,
            execution_id,
            step,
            {"status": STEP_RUNNING},
        )

        try:
            if dry_run:
                result = {
                    "ok": True,
                    "status": STEP_COMPLETED,
                    "dry_run": True,
                    "message": "Dry-run step completed.",
                    "step_id": step["step_id"],
                }

            elif step_type in AGENT_STEP_TYPES or step.get("agent_name"):
                result = self._execute_agent_step(
                    mission=mission,
                    step=step,
                    actor=actor,
                    execution_id=execution_id,
                )

            elif step_type in CONNECTOR_STEP_TYPES:
                result = self._execute_connector_step(
                    mission=mission,
                    step=step,
                    actor=actor,
                    execution_id=execution_id,
                )

            else:
                result = {
                    "ok": True,
                    "status": STEP_SKIPPED,
                    "message": f"No executor for step type: {step_type}",
                    "step_id": step["step_id"],
                }

            status = STEP_COMPLETED if result.get("ok") else result.get("status", STEP_FAILED)

            if status == STEP_SKIPPED:
                status = STEP_COMPLETED

            result["status"] = status

            self._complete_step_execution(step_execution_id, result, status)

            self._emit_step(
                EVENT_MISSION_STEP_COMPLETED if status == STEP_COMPLETED else EVENT_MISSION_STEP_FAILED,
                tenant_id,
                severity,
                execution_id,
                step,
                result,
            )

            return result

        except Exception as exc:
            result = {
                "ok": False,
                "status": STEP_FAILED,
                "message": str(exc),
                "step_id": step["step_id"],
            }

            self._complete_step_execution(step_execution_id, result, STEP_FAILED, error=str(exc))

            self._emit_step(
                EVENT_MISSION_STEP_FAILED,
                tenant_id,
                severity,
                execution_id,
                step,
                result,
            )

            return result

    def _execute_agent_step(
        self,
        *,
        mission: Dict[str, Any],
        step: Dict[str, Any],
        actor: str,
        execution_id: str,
    ) -> Dict[str, Any]:
        coordinator = getattr(self.storage, "agent_coordinator", None)

        if coordinator is None:
            return {
                "ok": False,
                "status": STEP_FAILED,
                "message": "Agent coordinator unavailable.",
            }

        task = coordinator.create_task(
            agent_name=step.get("agent_name") or "governance_agent",
            task_type=step.get("action") or "MISSION_STEP",
            tenant_id=mission.get("tenant_id") or "default",
            case_id=mission.get("case_id"),
            alert_id=mission.get("alert_id"),
            evidence_id=mission.get("evidence_id"),
            execution_id=execution_id,
            priority=mission.get("severity") or SEVERITY_MEDIUM,
            payload={
                "mission_id": mission.get("mission_id"),
                "step_id": step.get("step_id"),
                "step": step,
                "mission": mission,
            },
            created_by=actor,
        )

        fabric = getattr(self.storage, "distributed_agent_fabric", None)

        return {
            "ok": True,
            "status": STEP_COMPLETED,
            "message": "Agent task created.",
            "task_id": getattr(task, "task_id", None),
            "distributed_fabric_available": fabric is not None,
        }

    def _execute_connector_step(
        self,
        *,
        mission: Dict[str, Any],
        step: Dict[str, Any],
        actor: str,
        execution_id: str,
    ) -> Dict[str, Any]:
        registry = getattr(self.storage, "connector_registry", None)

        if registry is None:
            return {
                "ok": False,
                "status": STEP_FAILED,
                "message": "Connector registry unavailable.",
            }

        action = _upper(step.get("action"))
        tenant_id = mission.get("tenant_id") or "default"
        payload = _json_loads(step.get("payload_json") or step.get("payload") or {})

        connector = None

        connector_id = step.get("connector_id")
        if connector_id and hasattr(registry, "get_connector"):
            try:
                connector = registry.get_connector(connector_id, tenant_id=tenant_id)
            except TypeError:
                connector = registry.get_connector(connector_id)

        if connector is None and hasattr(registry, "resolve"):
            resolved = registry.resolve(action=action, tenant_id=tenant_id)
            connector = getattr(resolved, "connector", None) if getattr(resolved, "ok", False) else None

        if connector is None:
            return {
                "ok": False,
                "status": STEP_FAILED,
                "message": f"No connector available for action {action}.",
            }

        if not hasattr(connector, "execute"):
            return {
                "ok": False,
                "status": STEP_FAILED,
                "message": "Connector missing execute().",
            }

        result = connector.execute(
            action=action,
            payload=payload,
            actor=actor,
            execution_id=execution_id,
        )

        raw = result.to_dict() if hasattr(result, "to_dict") else dict(getattr(result, "__dict__", {}))

        self._maybe_create_rollback(
            mission=mission,
            step=step,
            connector=getattr(connector, "connector_id", connector_id),
            result=raw,
        )

        return {
            "ok": bool(getattr(result, "ok", False)),
            "status": STEP_COMPLETED if bool(getattr(result, "ok", False)) else STEP_FAILED,
            "message": getattr(result, "message", "Connector execution completed."),
            "connector_result": raw,
        }

    def _maybe_create_rollback(
        self,
        *,
        mission: Dict[str, Any],
        step: Dict[str, Any],
        connector: str,
        result: Dict[str, Any],
    ) -> None:
        rollback_payload = result.get("rollback_payload") or {}
        if not rollback_payload:
            return

        try:
            from core.runtime.rollback_orchestrator import get_rollback_orchestrator

            orchestrator = get_rollback_orchestrator(
                self.storage,
                event_bus=self.event_bus,
            )

            orchestrator.create_rollback(
                execution_id=result.get("execution_id"),
                tenant_id=mission.get("tenant_id") or "default",
                connector_id=connector,
                action=step.get("action"),
                rollback_action=rollback_payload.get("action"),
                target_id=result.get("target_id"),
                case_id=mission.get("case_id"),
                severity=mission.get("severity") or SEVERITY_MEDIUM,
                reason="Rollback payload captured during mission execution.",
                initiated_by="mission_execution_engine",
                requires_approval=False,
                payload=rollback_payload,
            )

        except Exception:
            pass

    # ------------------------------------------------------------------
    # Dependency resolution
    # ------------------------------------------------------------------

    def _find_ready_steps(
        self,
        steps: List[Dict[str, Any]],
        completed: Set[str],
    ) -> List[Dict[str, Any]]:
        ready = []

        already_terminal = self._terminal_step_ids(steps)

        for step in steps:
            step_id = step["step_id"]

            if step_id in completed or step_id in already_terminal:
                continue

            status = step.get("status") or STEP_PENDING

            if status in {STEP_BLOCKED, STEP_APPROVAL_REQUIRED}:
                ready.append(step)
                continue

            deps = _json_loads(step.get("depends_on_json") or "[]")
            if not isinstance(deps, list):
                deps = []

            if all(dep in completed for dep in deps):
                ready.append(step)

        return ready

    def _terminal_step_ids(
            self,
            steps: List[Dict[str, Any]],
    ) -> Set[str]:

        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT step_id
                FROM mission_step_executions
                WHERE status IN (?, ?, ?, ?)
                """,
                (
                    STEP_COMPLETED,
                    STEP_FAILED,
                    STEP_BLOCKED,
                    STEP_APPROVAL_REQUIRED,
                ),
            ).fetchall()

        return {
            r[0]
            for r in rows
        }

    # ------------------------------------------------------------------
    # DB helpers
    # ------------------------------------------------------------------

    def _get_mission(
            self,
            mission_id: str,
    ) -> Optional[Dict[str, Any]]:

        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM mission_plans
                WHERE mission_id=?
                LIMIT 1
                """,
                (mission_id,),
            ).fetchone()

            if not row:
                return None

            cols = [

                d[1]

                for d in conn.execute(
                    "PRAGMA table_info(mission_plans)"
                ).fetchall()
            ]

        return dict(
            zip(cols, row)
        )

    def _get_steps(
            self,
            mission_id: str,
    ) -> List[Dict[str, Any]]:

        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM mission_steps
                WHERE mission_id=?
                ORDER BY sequence ASC
                """,
                (mission_id,),
            ).fetchall()

            cols = [

                d[1]

                for d in conn.execute(
                    "PRAGMA table_info(mission_steps)"
                ).fetchall()
            ]

        return [
            dict(zip(cols, row))
            for row in rows
        ]

    def _create_execution(self, *, execution_id: str, mission_id: str, tenant_id: str, actor: str) -> None:
        now = _now_ms()
        with self._connect() as conn:
            conn.execute(
            """
            INSERT INTO mission_executions (
                execution_id, mission_id, tenant_id, status,
                result_json, created_by, created_at_ms, updated_at_ms
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                execution_id,
                mission_id,
                tenant_id,
                MISSION_RUNNING,
                "{}",
                actor,
                now,
                now,
            ),
        )
        conn.commit()

    def _record_step_start(
        self,
        step_execution_id: str,
        execution_id: str,
        mission_id: str,
        step: Dict[str, Any],
    ) -> None:
        now = _now_ms()
        with self._connect() as conn:
            conn.execute(
            """
            INSERT INTO mission_step_executions (
                step_execution_id, execution_id, mission_id, step_id,
                sequence, step_type, action, status, result_json,
                started_at_ms, updated_at_ms
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                step_execution_id,
                execution_id,
                mission_id,
                step["step_id"],
                step.get("sequence"),
                step.get("step_type"),
                step.get("action"),
                STEP_RUNNING,
                "{}",
                now,
                now,
            ),
        )
        conn.commit()

    def _record_step_execution(
        self,
        step_execution_id: str,
        execution_id: str,
        mission_id: str,
        step: Dict[str, Any],
        result: Dict[str, Any],
    ) -> None:
        now = _now_ms()
        with self._connect() as conn:
            conn.execute(
            """
            INSERT INTO mission_step_executions (
                step_execution_id, execution_id, mission_id, step_id,
                sequence, step_type, action, status, result_json,
                started_at_ms, completed_at_ms, updated_at_ms, last_error
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                step_execution_id,
                execution_id,
                mission_id,
                step["step_id"],
                step.get("sequence"),
                step.get("step_type"),
                step.get("action"),
                result.get("status"),
                _json_dumps(result),
                now,
                now,
                now,
                result.get("message") if not result.get("ok") else None,
            ),
        )
        conn.commit()

    def _complete_step_execution(
        self,
        step_execution_id: str,
        result: Dict[str, Any],
        status: str,
        *,
        error: Optional[str] = None,
    ) -> None:
        now = _now_ms()
        with self._connect() as conn:
            conn.execute(
            """
            UPDATE mission_step_executions
            SET status=?,
                result_json=?,
                completed_at_ms=?,
                updated_at_ms=?,
                last_error=?
            WHERE step_execution_id=?
            """,
            (
                status,
                _json_dumps(result),
                now,
                now,
                error,
                step_execution_id,
            ),
        )
        conn.commit()

    def _complete_execution(self, execution_id: str, result: Dict[str, Any], status: str) -> None:
        now = _now_ms()
        with self._connect() as conn:
            conn.execute(
            """
            UPDATE mission_executions
            SET status=?,
                result_json=?,
                updated_at_ms=?,
                completed_at_ms=?
            WHERE execution_id=?
            """,
            (
                status,
                _json_dumps(result),
                now,
                now if status in {MISSION_COMPLETED, MISSION_FAILED, MISSION_BLOCKED, MISSION_APPROVAL_REQUIRED} else None,
                execution_id,
            ),
        )
        conn.commit()

    def _set_mission_status(self, mission_id: str, status: str) -> None:
        with self._connect() as conn:
            conn.execute(
            """
            UPDATE mission_plans
            SET status=?
            WHERE mission_id=?
            """,
            (status, mission_id),
        )
        conn.commit()

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def _emit_step(
        self,
        event_type: str,
        tenant_id: str,
        severity: str,
        execution_id: str,
        step: Dict[str, Any],
        result: Dict[str, Any],
    ) -> None:
        self._emit(
            event_type,
            tenant_id=tenant_id,
            severity=severity,
            payload={
                "execution_id": execution_id,
                "mission_id": step.get("mission_id"),
                "step_id": step.get("step_id"),
                "action": step.get("action"),
                "step_type": step.get("step_type"),
                "result": result,
            },
        )

    def _emit(self, event_type: str, *, tenant_id: str, severity: str, payload: Dict[str, Any]) -> None:
        if self.event_bus is None:
            return

        try:
            self.event_bus.publish(
                event_type=event_type,
                tenant_id=tenant_id,
                source="mission_execution_engine",
                severity=severity,
                payload=payload,
            )
        except TypeError:
            try:
                self.event_bus.publish(
                    event_type=event_type,
                    payload=payload,
                    tenant_id=tenant_id,
                    source="mission_execution_engine",
                )
            except Exception:
                pass
        except Exception:
            pass


_DEFAULT_MISSION_EXECUTION_ENGINE: Optional[MissionExecutionEngine] = None


def get_mission_execution_engine(
    storage: Any = None,
    *,
    reset: bool = False,
    event_bus: Any = None,
) -> MissionExecutionEngine:
    global _DEFAULT_MISSION_EXECUTION_ENGINE

    if reset or _DEFAULT_MISSION_EXECUTION_ENGINE is None:
        _DEFAULT_MISSION_EXECUTION_ENGINE = MissionExecutionEngine(
            storage=storage,
            event_bus=event_bus,
        )

    return _DEFAULT_MISSION_EXECUTION_ENGINE