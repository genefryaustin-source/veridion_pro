"""
core/runtime/worker_orchestrator.py

Distributed Worker Orchestrator.

Upgraded responsibilities:
- worker registration
- worker heartbeats
- capability registration
- tenant affinity
- queue-driven job execution
- lease renewal
- completion/failure reporting
- worker quarantine
- dead-worker visibility
- autonomous runtime telemetry
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
import traceback
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


try:
    from core.events.event_subscribers import dispatch_event
except Exception:
    def dispatch_event(*args, **kwargs):
        return None


try:
    from core.runtime.distributed_execution_queue import (
        DistributedExecutionQueue,
        STATUS_PENDING,
        STATUS_RETRY,
        STATUS_LEASED,
        STATUS_RUNNING,
        STATUS_COMPLETED,
        STATUS_FAILED,
        STATUS_DEAD_LETTER,
    )
except Exception:
    DistributedExecutionQueue = None
    STATUS_PENDING = "PENDING"
    STATUS_RETRY = "RETRY"
    STATUS_LEASED = "LEASED"
    STATUS_RUNNING = "RUNNING"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_FAILED = "FAILED"
    STATUS_DEAD_LETTER = "DEAD_LETTER"


WORKER_STATUS_ONLINE = "ONLINE"
WORKER_STATUS_IDLE = "IDLE"
WORKER_STATUS_BUSY = "BUSY"
WORKER_STATUS_DEGRADED = "DEGRADED"
WORKER_STATUS_OFFLINE = "OFFLINE"
WORKER_STATUS_QUARANTINED = "QUARANTINED"

DEFAULT_DB_PATH = "data/distributed_execution_queue.db"
DEFAULT_LEASE_MS = 120_000


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


@dataclass
class WorkerRegistration:
    worker_id: str
    hostname: str = "unknown"
    status: str = WORKER_STATUS_ONLINE
    tenant_affinity: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    max_concurrent_jobs: int = 1
    active_jobs: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    registered_at_ms: int = field(default_factory=_now_ms)
    last_seen_ms: int = field(default_factory=_now_ms)
    last_heartbeat_ms: int = field(default_factory=_now_ms)
    last_error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class WorkerRunResult:
    success: bool
    worker_id: str
    job_id: Optional[str] = None
    status: str = "UNKNOWN"
    message: str = ""
    result: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    lease_renewed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class WorkerOrchestrator:
    def __init__(
        self,
        db_path: str = DEFAULT_DB_PATH,
        queue: Optional[Any] = None,
        storage: Optional[Any] = None,
        event_bus: Optional[Any] = None,
    ) -> None:
        self.db_path = db_path
        self.storage = storage
        self.event_bus = event_bus or getattr(storage, "event_bus", None)

        self.queue = queue or (
            DistributedExecutionQueue(db_path=db_path)
            if DistributedExecutionQueue is not None
            else None
        )

        self._lock = threading.RLock()

        self.ensure_schema()

        self.backpressure_controller = getattr(
            storage,
            "backpressure_controller",
            None,
        )

    # ========================================================
    # DB
    # ========================================================

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(
            self.db_path,
            timeout=30,
            check_same_thread=False,
        )
        conn.row_factory = sqlite3.Row

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
                CREATE TABLE IF NOT EXISTS worker_heartbeats (
                    worker_id TEXT PRIMARY KEY,
                    hostname TEXT,
                    status TEXT,
                    tenant_affinity_json TEXT,
                    capabilities_json TEXT,
                    max_concurrent_jobs INTEGER DEFAULT 1,
                    active_jobs INTEGER DEFAULT 0,
                    metadata_json TEXT,
                    registered_at_ms INTEGER,
                    last_seen_ms INTEGER,
                    last_heartbeat_ms INTEGER,
                    last_error TEXT
                )
                """
            )

            existing_cols = {
                row[1]
                for row in conn.execute(
                    "PRAGMA table_info(worker_heartbeats)"
                ).fetchall()
            }

            required_columns = {
                "last_heartbeat_ms":
                    "ALTER TABLE worker_heartbeats ADD COLUMN last_heartbeat_ms INTEGER",
                "last_error":
                    "ALTER TABLE worker_heartbeats ADD COLUMN last_error TEXT",
                "metadata_json":
                    "ALTER TABLE worker_heartbeats ADD COLUMN metadata_json TEXT",
                "active_jobs":
                    "ALTER TABLE worker_heartbeats ADD COLUMN active_jobs INTEGER DEFAULT 0",
                "max_concurrent_jobs":
                    "ALTER TABLE worker_heartbeats ADD COLUMN max_concurrent_jobs INTEGER DEFAULT 1",
            }

            for col, sql in required_columns.items():
                if col not in existing_cols:
                    try:
                        conn.execute(sql)
                    except Exception:
                        pass

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS worker_events (
                    event_id TEXT PRIMARY KEY,
                    worker_id TEXT,
                    event_type TEXT,
                    payload_json TEXT,
                    created_at_ms INTEGER
                )
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_worker_status
                ON worker_heartbeats(status)
                """
            )

            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_worker_seen
                ON worker_heartbeats(last_seen_ms)
                """
            )

            conn.commit()

    # ========================================================
    # EVENTING
    # ========================================================

    def emit_event(
        self,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        payload = payload or {}

        if self.event_bus is not None:
            try:
                self.event_bus.publish(
                    event_type=event_type,
                    tenant_id=payload.get("tenant_id") or "default",
                    source="worker_orchestrator",
                    severity=payload.get("severity") or "INFO",
                    payload=payload,
                )
                return
            except TypeError:
                try:
                    self.event_bus.publish(
                        event_type=event_type,
                        payload=payload,
                        tenant_id=payload.get("tenant_id") or "default",
                        source="worker_orchestrator",
                    )
                    return
                except Exception:
                    pass
            except Exception:
                pass

        dispatch_event(
            event_type=event_type,
            payload=payload,
            source="worker_orchestrator",
        )

    def record_worker_event(
        self,
        worker_id: str,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO worker_events (
                    event_id,
                    worker_id,
                    event_type,
                    payload_json,
                    created_at_ms
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    worker_id,
                    event_type,
                    _json_dumps(payload or {}),
                    _now_ms(),
                ),
            )
            conn.commit()

    # ========================================================
    # REGISTRATION / HEARTBEAT
    # ========================================================

    def register_worker(
        self,
        worker_id: Optional[str] = None,
        hostname: str = "unknown",
        tenant_affinity: Optional[List[str]] = None,
        capabilities: Optional[List[str]] = None,
        max_concurrent_jobs: int = 1,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        worker_id = worker_id or f"worker-{uuid.uuid4()}"
        now = _now_ms()

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO worker_heartbeats (
                    worker_id,
                    hostname,
                    status,
                    tenant_affinity_json,
                    capabilities_json,
                    max_concurrent_jobs,
                    active_jobs,
                    metadata_json,
                    registered_at_ms,
                    last_seen_ms,
                    last_heartbeat_ms,
                    last_error
                )
                VALUES (?, ?, ?, ?, ?, ?, 0, ?, ?, ?, ?, NULL)
                ON CONFLICT(worker_id) DO UPDATE SET
                    hostname=excluded.hostname,
                    status=excluded.status,
                    tenant_affinity_json=excluded.tenant_affinity_json,
                    capabilities_json=excluded.capabilities_json,
                    max_concurrent_jobs=excluded.max_concurrent_jobs,
                    metadata_json=excluded.metadata_json,
                    last_seen_ms=excluded.last_seen_ms,
                    last_heartbeat_ms=excluded.last_heartbeat_ms,
                    last_error=NULL
                """,
                (
                    worker_id,
                    hostname,
                    WORKER_STATUS_ONLINE,
                    _json_dumps(tenant_affinity or []),
                    _json_dumps(capabilities or []),
                    int(max_concurrent_jobs),
                    _json_dumps(metadata or {}),
                    now,
                    now,
                    now,
                ),
            )
            conn.commit()

        payload = {
            "worker_id": worker_id,
            "hostname": hostname,
            "tenant_affinity": tenant_affinity or [],
            "capabilities": capabilities or [],
            "max_concurrent_jobs": max_concurrent_jobs,
        }

        self.record_worker_event(worker_id, "WORKER_REGISTERED", payload)
        self.emit_event("WORKER_REGISTERED", payload)

        return worker_id

    def heartbeat(
        self,
        worker_id: str,
        status: str = WORKER_STATUS_ONLINE,
        active_jobs: Optional[int] = None,
        last_error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        now = _now_ms()

        updates = {
            "last_seen_ms": now,
            "last_heartbeat_ms": now,
            "status": status,
            "last_error": last_error,
        }

        if active_jobs is not None:
            updates["active_jobs"] = int(active_jobs)

        if metadata is not None:
            updates["metadata_json"] = _json_dumps(metadata)

        set_sql = ", ".join([f"{k}=?" for k in updates.keys()])
        values = list(updates.values())

        with self._connect() as conn:
            cur = conn.execute(
                f"""
                UPDATE worker_heartbeats
                SET {set_sql}
                WHERE worker_id=?
                """,
                values + [worker_id],
            )
            conn.commit()

        ok = cur.rowcount > 0

        if ok:
            self.emit_event(
                "WORKER_HEARTBEAT",
                {
                    "worker_id": worker_id,
                    "status": status,
                    "active_jobs": active_jobs,
                    "last_error": last_error,
                },
            )

        return ok

    # ========================================================
    # STATUS / QUARANTINE
    # ========================================================

    def mark_worker_status(
        self,
        worker_id: str,
        status: str,
        reason: str = "",
    ) -> bool:
        now = _now_ms()

        with self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE worker_heartbeats
                SET status=?,
                    last_error=?,
                    last_seen_ms=?,
                    last_heartbeat_ms=?
                WHERE worker_id=?
                """,
                (
                    status,
                    reason,
                    now,
                    now,
                    worker_id,
                ),
            )
            conn.commit()

        ok = cur.rowcount > 0

        if ok:
            self.record_worker_event(
                worker_id,
                "WORKER_STATUS_CHANGED",
                {
                    "status": status,
                    "reason": reason,
                },
            )

            self.emit_event(
                "WORKER_STATUS_CHANGED",
                {
                    "worker_id": worker_id,
                    "status": status,
                    "reason": reason,
                },
            )

        return ok

    def quarantine_worker(
        self,
        worker_id: str,
        reason: str = "",
    ) -> bool:
        return self.mark_worker_status(
            worker_id,
            WORKER_STATUS_QUARANTINED,
            reason or "manual_or_watchdog_quarantine",
        )

    def release_worker_quarantine(
        self,
        worker_id: str,
    ) -> bool:
        return self.mark_worker_status(
            worker_id,
            WORKER_STATUS_ONLINE,
            "quarantine_released",
        )

    # ========================================================
    # WORKER SELECTION
    # ========================================================

    def select_worker_for_job(
        self,
        tenant_id: Optional[str] = None,
        required_capability: Optional[str] = None,
    ) -> Optional[WorkerRegistration]:
        workers = self.list_workers()

        eligible: List[WorkerRegistration] = []

        for worker in workers:
            if worker.status in {
                WORKER_STATUS_OFFLINE,
                WORKER_STATUS_QUARANTINED,
                WORKER_STATUS_DEGRADED,
            }:
                continue

            if worker.active_jobs >= worker.max_concurrent_jobs:
                continue

            if tenant_id and worker.tenant_affinity:
                if tenant_id not in worker.tenant_affinity:
                    continue

            if required_capability and worker.capabilities:
                if required_capability not in worker.capabilities:
                    continue

            eligible.append(worker)

        if not eligible:
            return None

        eligible.sort(
            key=lambda w: (
                w.active_jobs,
                len(w.tenant_affinity or []),
                -int(w.last_seen_ms or 0),
            )
        )

        return eligible[0]

    # ========================================================
    # QUEUE-DRIVEN EXECUTION
    # ========================================================

    def run_worker_once(
        self,
        *,
        worker_id: str,
        tenant_id: Optional[str] = None,
        lease_ms: int = DEFAULT_LEASE_MS,
        storage: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> WorkerRunResult:
        if self.queue is None:
            return WorkerRunResult(
                success=False,
                worker_id=worker_id,
                status="QUEUE_UNAVAILABLE",
                error="Execution queue unavailable.",
            )

        worker = self.get_worker(worker_id)

        if worker is None:
            return WorkerRunResult(
                success=False,
                worker_id=worker_id,
                status="WORKER_NOT_REGISTERED",
                error="Worker is not registered.",
            )

        if worker.status == WORKER_STATUS_QUARANTINED:
            return WorkerRunResult(
                success=False,
                worker_id=worker_id,
                status="WORKER_QUARANTINED",
                error="Worker is quarantined.",
            )

        if worker.status == WORKER_STATUS_OFFLINE:
            return WorkerRunResult(
                success=False,
                worker_id=worker_id,
                status="WORKER_OFFLINE",
                error="Worker is offline.",
            )

        # ====================================================
        # BACKPRESSURE CONTROL
        # ====================================================

        if self.backpressure_controller is not None:
            pressure = self.backpressure_controller.should_route(
                tenant_id=tenant_id or "default",
                context={
                    "source": "worker_orchestrator",
                    "worker_id": worker_id,
                },
            )

            if pressure.freeze_tenant:
                self.backpressure_controller.enforce_freeze_if_needed(
                    pressure
                )

            if not pressure.allowed:
                self.heartbeat(
                    worker_id,
                    status=WORKER_STATUS_IDLE,
                    active_jobs=0,
                    last_error=pressure.reason,
                )

                return WorkerRunResult(
                    success=False,
                    worker_id=worker_id,
                    status="BACKPRESSURE_BLOCKED",
                    error=pressure.reason,
                    result={
                        "backpressure_decision": pressure.to_dict(),
                    },
                )

        job = self.queue.lease_next(
            worker_id=worker_id,
            tenant_id=tenant_id,
            lease_ms=lease_ms,
        )

        if job is None:
            self.heartbeat(
                worker_id,
                status=WORKER_STATUS_IDLE,
                active_jobs=0,
            )

            return WorkerRunResult(
                success=True,
                worker_id=worker_id,
                status="NO_JOB",
                message="No job available.",
            )

        job_id = getattr(job, "job_id", None)

        self.heartbeat(
            worker_id,
            status=WORKER_STATUS_BUSY,
            active_jobs=int(worker.active_jobs or 0) + 1,
        )

        self.record_worker_event(
            worker_id,
            "JOB_LEASED",
            {
                "job_id": job_id,
                "tenant_id": getattr(job, "tenant_id", None),
                "job_type": getattr(job, "job_type", None),
                "action": getattr(job, "action", None),
            },
        )

        self.emit_event(
            "WORKER_JOB_LEASED",
            {
                "worker_id": worker_id,
                "job_id": job_id,
                "tenant_id": getattr(job, "tenant_id", None),
                "job_type": getattr(job, "job_type", None),
                "action": getattr(job, "action", None),
            },
        )

        lease_renewed = False

        try:
            self.queue.mark_running(
                job_id,
                worker_id,
            )

            lease_renewed = self.queue.renew_lease(
                job_id,
                worker_id,
                lease_ms=lease_ms,
            )

            result = self.queue.execute_job(
                job,
                worker_id=worker_id,
                storage=storage or self.storage,
                config=config or {},
            )

            if result.get("success"):
                self.queue.complete(
                    job_id,
                    worker_id,
                    result,
                )

                self.record_worker_event(
                    worker_id,
                    "JOB_COMPLETED",
                    {
                        "job_id": job_id,
                        "result": result,
                    },
                )

                self.emit_event(
                    "WORKER_JOB_COMPLETED",
                    {
                        "worker_id": worker_id,
                        "job_id": job_id,
                        "result": result,
                    },
                )

                self.heartbeat(
                    worker_id,
                    status=WORKER_STATUS_IDLE,
                    active_jobs=max(int(worker.active_jobs or 0) - 1, 0),
                )

                return WorkerRunResult(
                    success=True,
                    worker_id=worker_id,
                    job_id=job_id,
                    status=result.get("status") or STATUS_COMPLETED,
                    message=result.get("message") or "Job completed.",
                    result=result,
                    lease_renewed=lease_renewed,
                )

            error = result.get("error") or result.get("message") or str(result)

            self.queue.fail(
                job_id,
                worker_id,
                error,
            )

            self._maybe_trigger_failure_rollback(
                job=job,
                worker_id=worker_id,
                error=error,
                result=result,
            )

            self.record_worker_event(
                worker_id,
                "JOB_FAILED",
                {
                    "job_id": job_id,
                    "error": error,
                    "result": result,
                },
            )

            self.emit_event(
                "WORKER_JOB_FAILED",
                {
                    "worker_id": worker_id,
                    "job_id": job_id,
                    "error": error,
                    "result": result,
                },
            )

            self.heartbeat(
                worker_id,
                status=WORKER_STATUS_IDLE,
                active_jobs=max(int(worker.active_jobs or 0) - 1, 0),
                last_error=error,
            )

            return WorkerRunResult(
                success=False,
                worker_id=worker_id,
                job_id=job_id,
                status=result.get("status") or STATUS_FAILED,
                result=result,
                error=error,
                lease_renewed=lease_renewed,
            )

        except Exception as exc:
            err = str(exc)

            try:
                self.queue.fail(
                    job_id,
                    worker_id,
                    err,
                )
            except Exception:
                pass

            self.record_worker_event(
                worker_id,
                "JOB_EXECUTION_EXCEPTION",
                {
                    "job_id": job_id,
                    "error": err,
                    "traceback": traceback.format_exc(),
                },
            )

            self.emit_event(
                "WORKER_JOB_EXCEPTION",
                {
                    "worker_id": worker_id,
                    "job_id": job_id,
                    "error": err,
                    "traceback": traceback.format_exc(),
                },
            )

            self.heartbeat(
                worker_id,
                status=WORKER_STATUS_DEGRADED,
                active_jobs=max(int(worker.active_jobs or 0) - 1, 0),
                last_error=err,
            )

            return WorkerRunResult(
                success=False,
                worker_id=worker_id,
                job_id=job_id,
                status="EXCEPTION",
                error=err,
                result={
                    "traceback": traceback.format_exc(),
                },
                lease_renewed=lease_renewed,
            )

    def run_worker_loop(
        self,
        *,
        worker_id: str,
        tenant_id: Optional[str] = None,
        poll_interval_seconds: float = 2.0,
        stop_event: Optional[threading.Event] = None,
        lease_ms: int = DEFAULT_LEASE_MS,
        storage: Optional[Any] = None,
        config: Optional[Dict[str, Any]] = None,
        max_iterations: Optional[int] = None,
    ) -> List[WorkerRunResult]:
        results: List[WorkerRunResult] = []
        iterations = 0

        # ====================================================
        # BACKPRESSURE EXECUTION BUDGET
        # ====================================================

        budget = None

        if self.backpressure_controller is not None:
            pressure = self.backpressure_controller.should_route(
                tenant_id=tenant_id or "default",
                context={
                    "source": "worker_loop",
                    "worker_id": worker_id,
                },
            )

            if pressure.freeze_tenant:
                self.backpressure_controller.enforce_freeze_if_needed(
                    pressure
                )

            if not pressure.allowed:
                return [
                    WorkerRunResult(
                        success=False,
                        worker_id=worker_id,
                        status="BACKPRESSURE_BLOCKED",
                        error=pressure.reason,
                        result={
                            "backpressure_decision": pressure.to_dict(),
                        },
                    )
                ]

            budget = pressure.max_worker_iterations

        while True:
            if stop_event is not None and stop_event.is_set():
                break

            effective_max_iterations = max_iterations

            if budget is not None:
                effective_max_iterations = (
                    min(max_iterations, budget)
                    if max_iterations is not None
                    else budget
                )

            if (
                effective_max_iterations is not None
                and iterations >= effective_max_iterations
            ):
                break

            worker = self.get_worker(worker_id)

            if worker and worker.status == WORKER_STATUS_QUARANTINED:
                self.emit_event(
                    "WORKER_LOOP_PAUSED_QUARANTINED",
                    {
                        "worker_id": worker_id,
                    },
                )
                break

            result = self.run_worker_once(
                worker_id=worker_id,
                tenant_id=tenant_id,
                lease_ms=lease_ms,
                storage=storage or self.storage,
                config=config or {},
            )

            results.append(result)

            iterations += 1

            if result.status == "NO_JOB":
                time.sleep(poll_interval_seconds)

        return results

    def assign_next_job(
        self,
        tenant_id: Optional[str] = None,
        required_capability: Optional[str] = None,
        lease_ms: int = DEFAULT_LEASE_MS,
    ) -> Optional[Dict[str, Any]]:
        if self.queue is None:
            return None

        worker = self.select_worker_for_job(
            tenant_id=tenant_id,
            required_capability=required_capability,
        )

        if worker is None:
            self.emit_event(
                "WORKER_ASSIGNMENT_SKIPPED",
                {
                    "reason": "no_eligible_worker",
                    "tenant_id": tenant_id,
                    "required_capability": required_capability,
                },
            )
            return None

        job = self.queue.lease_next(
            worker_id=worker.worker_id,
            tenant_id=tenant_id,
            lease_ms=lease_ms,
        )

        if job is None:
            return None

        self.heartbeat(
            worker.worker_id,
            status=WORKER_STATUS_BUSY,
            active_jobs=worker.active_jobs + 1,
        )

        payload = {
            "worker_id": worker.worker_id,
            "job_id": getattr(job, "job_id", None),
            "tenant_id": getattr(job, "tenant_id", None),
            "job_type": getattr(job, "job_type", None),
        }

        self.record_worker_event(
            worker.worker_id,
            "JOB_ASSIGNED",
            payload,
        )

        self.emit_event(
            "WORKER_JOB_ASSIGNED",
            payload,
        )

        return {
            "worker": worker,
            "job": job,
        }

    def release_job_slot(
        self,
        worker_id: str,
    ) -> None:
        worker = self.get_worker(worker_id)

        if not worker:
            return

        active_jobs = max(int(worker.active_jobs or 0) - 1, 0)
        status = WORKER_STATUS_IDLE if active_jobs == 0 else WORKER_STATUS_BUSY

        self.heartbeat(
            worker_id,
            status=status,
            active_jobs=active_jobs,
        )

    # ========================================================
    # FAILURE / ROLLBACK
    # ========================================================

    def _maybe_trigger_failure_rollback(
        self,
        *,
        job: Any,
        worker_id: str,
        error: str,
        result: Dict[str, Any],
    ) -> None:
        if self.queue is None:
            return

        job_type = getattr(job, "job_type", None)

        if job_type == "ROLLBACK":
            return

        payload = getattr(job, "payload", {}) or {}

        rollback_payload = (
            result.get("rollback_payload")
            or payload.get("rollback_payload")
            or {}
        )

        if not rollback_payload:
            return

        try:
            rollback_payload = {
                **rollback_payload,
                "source_job_id": getattr(job, "job_id", None),
                "source_worker_id": worker_id,
                "failure_error": error,
            }

            rollback_id = self.queue.enqueue_rollback(
                rollback_payload=rollback_payload,
                tenant_id=getattr(job, "tenant_id", "default"),
                priority=1,
            )

            self.emit_event(
                "WORKER_ROLLBACK_ENQUEUED",
                {
                    "worker_id": worker_id,
                    "source_job_id": getattr(job, "job_id", None),
                    "rollback_job_id": rollback_id,
                },
            )

        except Exception:
            pass

    # ========================================================
    # DEAD WORKER / REBALANCING
    # ========================================================

    def detect_stale_workers(
        self,
        stale_after_ms: int = 5 * 60_000,
    ) -> List[WorkerRegistration]:
        now = _now_ms()
        stale: List[WorkerRegistration] = []

        for worker in self.list_workers():
            age_ms = now - int(worker.last_heartbeat_ms or worker.last_seen_ms or 0)

            if age_ms >= stale_after_ms and worker.status not in {
                WORKER_STATUS_OFFLINE,
                WORKER_STATUS_QUARANTINED,
            }:
                stale.append(worker)

        return stale

    def mark_stale_workers_offline(
        self,
        stale_after_ms: int = 5 * 60_000,
    ) -> List[str]:
        stale = self.detect_stale_workers(stale_after_ms)
        marked = []

        for worker in stale:
            if self.mark_worker_status(
                worker.worker_id,
                WORKER_STATUS_OFFLINE,
                f"stale_worker_no_heartbeat:{stale_after_ms}ms",
            ):
                marked.append(worker.worker_id)

        if marked:
            self.emit_event(
                "STALE_WORKERS_MARKED_OFFLINE",
                {
                    "worker_ids": marked,
                    "count": len(marked),
                },
            )

        return marked

    def rebalance_workloads(self) -> Dict[str, Any]:
        offline = self.mark_stale_workers_offline()

        summary = {
            "offline_workers": offline,
            "offline_count": len(offline),
        }

        self.emit_event(
            "WORKER_REBALANCE_COMPLETED",
            summary,
        )

        return summary

    # ========================================================
    # READS
    # ========================================================

    def get_worker(
        self,
        worker_id: str,
    ) -> Optional[WorkerRegistration]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT *
                FROM worker_heartbeats
                WHERE worker_id=?
                LIMIT 1
                """,
                (worker_id,),
            ).fetchone()

        if not row:
            return None

        return self._row_to_worker(dict(row))

    def list_workers(
        self,
        status: Optional[str] = None,
    ) -> List[WorkerRegistration]:
        params: List[Any] = []
        where = ""

        if status:
            where = "WHERE status=?"
            params.append(status)

        with self._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT *
                FROM worker_heartbeats
                {where}
                ORDER BY last_seen_ms DESC
                """,
                params,
            ).fetchall()

        return [
            self._row_to_worker(dict(r))
            for r in rows
        ]

    def worker_stats(self) -> Dict[str, Any]:
        workers = self.list_workers()

        by_status: Dict[str, int] = {}

        active_jobs = 0

        for worker in workers:
            by_status[worker.status] = by_status.get(worker.status, 0) + 1
            active_jobs += int(worker.active_jobs or 0)

        return {
            "total_workers": len(workers),
            "online": by_status.get(WORKER_STATUS_ONLINE, 0),
            "idle": by_status.get(WORKER_STATUS_IDLE, 0),
            "busy": by_status.get(WORKER_STATUS_BUSY, 0),
            "degraded": by_status.get(WORKER_STATUS_DEGRADED, 0),
            "offline": by_status.get(WORKER_STATUS_OFFLINE, 0),
            "quarantined": by_status.get(WORKER_STATUS_QUARANTINED, 0),
            "active_jobs": active_jobs,
            "by_status": by_status,
        }

    def list_worker_events(
        self,
        worker_id: Optional[str] = None,
        limit: int = 200,
    ) -> List[Dict[str, Any]]:
        params: List[Any] = []
        where = ""

        if worker_id:
            where = "WHERE worker_id=?"
            params.append(worker_id)

        params.append(limit)

        with self._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT *
                FROM worker_events
                {where}
                ORDER BY created_at_ms DESC
                LIMIT ?
                """,
                params,
            ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    # ========================================================
    # ROW HELPERS
    # ========================================================

    def _row_to_worker(
        self,
        row: Dict[str, Any],
    ) -> WorkerRegistration:
        tenant_affinity = _json_loads(row.get("tenant_affinity_json"))
        capabilities = _json_loads(row.get("capabilities_json"))
        metadata = _json_loads(row.get("metadata_json"))

        if not isinstance(tenant_affinity, list):
            tenant_affinity = []

        if not isinstance(capabilities, list):
            capabilities = []

        if not isinstance(metadata, dict):
            metadata = {}

        return WorkerRegistration(
            worker_id=row.get("worker_id"),
            hostname=row.get("hostname") or "unknown",
            status=row.get("status") or WORKER_STATUS_ONLINE,
            tenant_affinity=tenant_affinity,
            capabilities=capabilities,
            max_concurrent_jobs=int(row.get("max_concurrent_jobs") or 1),
            active_jobs=int(row.get("active_jobs") or 0),
            metadata=metadata,
            registered_at_ms=int(row.get("registered_at_ms") or _now_ms()),
            last_seen_ms=int(row.get("last_seen_ms") or _now_ms()),
            last_heartbeat_ms=int(
                row.get("last_heartbeat_ms")
                or row.get("last_seen_ms")
                or _now_ms()
            ),
            last_error=row.get("last_error"),
        )


_DEFAULT_WORKER_ORCHESTRATOR: Optional[WorkerOrchestrator] = None


def get_worker_orchestrator(
    db_path: str = DEFAULT_DB_PATH,
    *,
    queue: Optional[Any] = None,
    storage: Optional[Any] = None,
    event_bus: Optional[Any] = None,
    reset: bool = False,
) -> WorkerOrchestrator:
    global _DEFAULT_WORKER_ORCHESTRATOR

    if reset or _DEFAULT_WORKER_ORCHESTRATOR is None:
        _DEFAULT_WORKER_ORCHESTRATOR = WorkerOrchestrator(
            db_path=db_path,
            queue=queue,
            storage=storage,
            event_bus=event_bus,
        )

    return _DEFAULT_WORKER_ORCHESTRATOR