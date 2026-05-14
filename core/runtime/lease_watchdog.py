"""
core/runtime/lease_watchdog.py

Distributed Lease Watchdog.

Responsibilities:
- expired lease recovery
- stuck job recovery
- dead worker detection
- retry escalation
- dead-letter promotion
- rollback triggering
- worker quarantine
- autonomous execution stability
"""

from __future__ import annotations

import time
import traceback
import uuid
from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List, Optional


STATUS_OK = "OK"
STATUS_WARNING = "WARNING"
STATUS_CRITICAL = "CRITICAL"

ACTION_REQUEUED = "REQUEUED"
ACTION_DEAD_LETTERED = "DEAD_LETTERED"
ACTION_QUARANTINED = "QUARANTINED"
ACTION_TRIGGERED_ROLLBACK = "TRIGGERED_ROLLBACK"
ACTION_ESCALATED = "ESCALATED"

DEFAULT_WORKER_TIMEOUT_MS = 180_000
DEFAULT_STUCK_JOB_TIMEOUT_MS = 300_000
DEFAULT_MAX_FAILURES = 5


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class LeaseWatchdogEvent:
    event_id: str
    status: str
    action: str
    reason: str
    worker_id: Optional[str] = None
    job_id: Optional[str] = None
    tenant_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LeaseWatchdog:
    def __init__(
        self,
        *,
        queue: Any = None,
        worker_orchestrator: Any = None,
        router: Any = None,
        storage: Any = None,
        event_bus: Any = None,
    ) -> None:
        self.queue = queue or getattr(storage, "execution_queue", None)

        self.worker_orchestrator = (
            worker_orchestrator
            or getattr(storage, "worker_orchestrator", None)
        )

        self.router = (
            router
            or getattr(storage, "execution_router", None)
        )

        self.storage = storage

        self.event_bus = (
            event_bus
            or getattr(storage, "event_bus", None)
        )

    # ========================================================
    # MAIN CYCLE
    # ========================================================

    def run_cycle(
        self,
        *,
        worker_timeout_ms: int = DEFAULT_WORKER_TIMEOUT_MS,
        stuck_job_timeout_ms: int = DEFAULT_STUCK_JOB_TIMEOUT_MS,
        auto_requeue: bool = True,
        auto_quarantine: bool = True,
        auto_rollback: bool = True,
    ) -> Dict[str, Any]:

        results = {
            "expired_leases": [],
            "dead_workers": [],
            "stuck_jobs": [],
            "requeued": 0,
            "dead_lettered": 0,
            "quarantined": 0,
            "rollback_triggers": 0,
            "errors": [],
        }

        # ----------------------------------------------------
        # EXPIRED LEASES
        # ----------------------------------------------------

        try:

            recovered = self.queue.requeue_expired_leases()

            results["requeued"] += int(recovered or 0)

            if recovered:

                self._emit(
                    "LEASES_RECOVERED",
                    {
                        "recovered": recovered,
                    },
                )

        except Exception as exc:

            results["errors"].append(
                f"expired_lease_recovery_failed: {exc}"
            )

        # ----------------------------------------------------
        # DEAD WORKERS
        # ----------------------------------------------------

        try:

            dead_workers = self._detect_dead_workers(
                worker_timeout_ms=worker_timeout_ms,
            )

            results["dead_workers"] = dead_workers

            for worker in dead_workers:

                worker_id = worker.get("worker_id")

                if auto_quarantine:

                    self._quarantine_worker(
                        worker_id,
                        reason="heartbeat_timeout",
                    )

                    results["quarantined"] += 1

                self._emit_event(
                    status=STATUS_CRITICAL,
                    action=ACTION_QUARANTINED,
                    reason="Worker heartbeat expired.",
                    worker_id=worker_id,
                    metadata=worker,
                )

        except Exception as exc:

            results["errors"].append(
                f"dead_worker_detection_failed: {exc}"
            )

        # ----------------------------------------------------
        # STUCK JOBS
        # ----------------------------------------------------

        try:

            stuck_jobs = self._detect_stuck_jobs(
                stuck_job_timeout_ms=stuck_job_timeout_ms,
            )

            results["stuck_jobs"] = stuck_jobs

            for job in stuck_jobs:

                job_id = job.get("job_id")
                tenant_id = job.get("tenant_id")

                if auto_requeue:

                    ok = self.queue.fail(
                        job_id=job_id,
                        error="Stuck execution detected.",
                    )

                    if ok:
                        results["requeued"] += 1

                if auto_rollback:

                    self._trigger_rollback(job)

                    results["rollback_triggers"] += 1

                self._emit_event(
                    status=STATUS_WARNING,
                    action=ACTION_TRIGGERED_ROLLBACK,
                    reason="Stuck job detected.",
                    job_id=job_id,
                    tenant_id=tenant_id,
                    metadata=job,
                )

        except Exception as exc:

            results["errors"].append(
                f"stuck_job_detection_failed: {exc}"
            )

        return results

    # ========================================================
    # DEAD WORKERS
    # ========================================================

    def _detect_dead_workers(
        self,
        *,
        worker_timeout_ms: int,
    ) -> List[Dict[str, Any]]:

        if self.worker_orchestrator is None:
            return []

        workers = self.worker_orchestrator.list_workers()

        now = _now_ms()

        dead = []

        for worker in workers:

            status = getattr(worker, "status", None)

            if status in {
                "OFFLINE",
                "QUARANTINED",
            }:
                continue

            last_heartbeat = int(
                getattr(
                    worker,
                    "last_heartbeat_ms",
                    0,
                ) or 0
            )

            if last_heartbeat <= 0:
                continue

            age = now - last_heartbeat

            if age >= worker_timeout_ms:

                dead.append({

                    "worker_id":
                        getattr(
                            worker,
                            "worker_id",
                            None,
                        ),

                    "status":
                        status,

                    "heartbeat_age_ms":
                        age,

                    "active_jobs":
                        getattr(
                            worker,
                            "active_jobs",
                            0,
                        ),

                    "capabilities":
                        getattr(
                            worker,
                            "capabilities",
                            [],
                        ),
                })

        return dead

    def _quarantine_worker(
        self,
        worker_id: str,
        *,
        reason: str,
    ) -> bool:

        if self.worker_orchestrator is None:
            return False

        try:

            self.worker_orchestrator.quarantine_worker(
                worker_id,
                reason=reason,
            )

            self._emit(
                "WORKER_QUARANTINED",
                {
                    "worker_id": worker_id,
                    "reason": reason,
                },
            )

            return True

        except Exception:
            return False

    # ========================================================
    # STUCK JOBS
    # ========================================================

    def _detect_stuck_jobs(
        self,
        *,
        stuck_job_timeout_ms: int,
    ) -> List[Dict[str, Any]]:

        jobs = self.queue.list_jobs(
            limit=1000,
        )

        now = _now_ms()

        stuck = []

        for job in jobs:

            status = job.get("status")

            if status not in {
                "LEASED",
                "RUNNING",
            }:
                continue

            updated_at_ms = int(
                job.get("updated_at_ms") or 0
            )

            if updated_at_ms <= 0:
                continue

            age = now - updated_at_ms

            if age >= stuck_job_timeout_ms:

                stuck.append({

                    "job_id":
                        job.get("job_id"),

                    "tenant_id":
                        job.get("tenant_id"),

                    "worker_id":
                        job.get("worker_id"),

                    "status":
                        status,

                    "age_ms":
                        age,

                    "attempts":
                        job.get("attempts"),

                    "max_attempts":
                        job.get("max_attempts"),

                    "job_type":
                        job.get("job_type"),

                    "action":
                        job.get("action"),
                })

        return stuck

    # ========================================================
    # ROLLBACK TRIGGERS
    # ========================================================

    def _trigger_rollback(
        self,
        job: Dict[str, Any],
    ) -> bool:

        try:

            rollback_payload = {

                "execution_id":
                    job.get("job_id"),

                "source":
                    "lease_watchdog",

                "reason":
                    "stuck_execution",

                "job":
                    job,
            }

            rollback_id = self.queue.enqueue_rollback(
                rollback_payload=rollback_payload,
                tenant_id=job.get("tenant_id") or "default",
                priority=1,
            )

            self._emit(
                "ROLLBACK_TRIGGERED",
                {
                    "rollback_id": rollback_id,
                    "job_id": job.get("job_id"),
                },
            )

            return True

        except Exception:
            return False

    # ========================================================
    # HELPERS
    # ========================================================

    def _emit_event(
        self,
        *,
        status: str,
        action: str,
        reason: str,
        worker_id: Optional[str] = None,
        job_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> LeaseWatchdogEvent:

        event = LeaseWatchdogEvent(
            event_id=f"WATCHDOG-{uuid.uuid4().hex[:12].upper()}",
            status=status,
            action=action,
            reason=reason,
            worker_id=worker_id,
            job_id=job_id,
            tenant_id=tenant_id,
            metadata=metadata or {},
        )

        self._emit(
            "LEASE_WATCHDOG_EVENT",
            event.to_dict(),
        )

        return event

    def _emit(
        self,
        event_type: str,
        payload: Dict[str, Any],
    ) -> None:

        if self.event_bus is None:
            return

        try:

            self.event_bus.publish(
                event_type=event_type,
                tenant_id=payload.get("tenant_id") or "default",
                source="lease_watchdog",
                severity="INFO",
                payload=payload,
            )

        except TypeError:

            try:

                self.event_bus.publish(
                    event_type=event_type,
                    payload=payload,
                    tenant_id=payload.get("tenant_id") or "default",
                    source="lease_watchdog",
                )

            except Exception:
                pass

        except Exception:
            pass


_DEFAULT_WATCHDOG: Optional[LeaseWatchdog] = None


def get_lease_watchdog(
    *,
    queue: Any = None,
    worker_orchestrator: Any = None,
    router: Any = None,
    storage: Any = None,
    event_bus: Any = None,
    reset: bool = False,
) -> LeaseWatchdog:

    global _DEFAULT_WATCHDOG

    if reset or _DEFAULT_WATCHDOG is None:

        _DEFAULT_WATCHDOG = LeaseWatchdog(
            queue=queue,
            worker_orchestrator=worker_orchestrator,
            router=router,
            storage=storage,
            event_bus=event_bus,
        )

    return _DEFAULT_WATCHDOG