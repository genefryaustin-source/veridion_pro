"""
core/runtime/distributed_execution_router.py

Intelligent Distributed Execution Router.

Responsibilities:
- choose best worker for queued jobs
- tenant-aware routing
- capability-aware routing
- worker affinity
- connector-aware dispatching
- rollback-safe routing
- graph/orchestration routing
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


JOB_TYPE_ACTION = "ACTION"
JOB_TYPE_GRAPH = "GRAPH"
JOB_TYPE_ROLLBACK = "ROLLBACK"

ROUTE_ACCEPTED = "ACCEPTED"
ROUTE_SKIPPED = "SKIPPED"
ROUTE_BLOCKED = "BLOCKED"
ROUTE_FAILED = "FAILED"

WORKER_STATUS_ONLINE = "ONLINE"
WORKER_STATUS_IDLE = "IDLE"
WORKER_STATUS_BUSY = "BUSY"
WORKER_STATUS_DEGRADED = "DEGRADED"
WORKER_STATUS_OFFLINE = "OFFLINE"
WORKER_STATUS_QUARANTINED = "QUARANTINED"

CAPABILITY_GOVERNANCE = "governance"
CAPABILITY_ORCHESTRATION = "orchestration"
CAPABILITY_ROLLBACK = "rollback"
CAPABILITY_CONNECTOR = "connector"
CAPABILITY_ENDPOINT = "endpoint"
CAPABILITY_IDENTITY = "identity"
CAPABILITY_MAILBOX = "mailbox"
CAPABILITY_GRAPH = "graph"


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class RouteDecision:
    decision_id: str
    accepted: bool
    status: str
    reason: str
    job_id: Optional[str] = None
    worker_id: Optional[str] = None
    tenant_id: Optional[str] = None
    job_type: Optional[str] = None
    required_capability: Optional[str] = None
    score: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DistributedExecutionRouter:
    def __init__(
        self,
        *,
        queue: Any = None,
        worker_orchestrator: Any = None,
        storage: Any = None,
        event_bus: Any = None,
    ) -> None:
        self.queue = queue or getattr(storage, "execution_queue", None)
        self.worker_orchestrator = (
            worker_orchestrator
            or getattr(storage, "worker_orchestrator", None)
        )
        self.storage = storage
        self.event_bus = event_bus or getattr(storage, "event_bus", None)
        self.backpressure_controller = getattr(
            storage,
            "backpressure_controller",
            None,
        )
    # ========================================================
    # MAIN ROUTING
    # ========================================================

    def route_next(
        self,
        *,
        tenant_id: Optional[str] = None,
        lease_ms: int = 120_000,
    ) -> RouteDecision:
        if self.queue is None:
            return self._decision(
                accepted=False,
                status=ROUTE_FAILED,
                reason="Execution queue unavailable.",
                tenant_id=tenant_id,
            )

        if self.worker_orchestrator is None:
            return self._decision(
                accepted=False,
                status=ROUTE_FAILED,
                reason="Worker orchestrator unavailable.",
                tenant_id=tenant_id,
            )
        if self.backpressure_controller is not None:
            decision = self.backpressure_controller.should_route(
                tenant_id=tenant_id or "default",
                context={
                    "source": "distributed_execution_router",
                },
            )

            if decision.freeze_tenant:
                self.backpressure_controller.enforce_freeze_if_needed(decision)

            if not decision.allowed:
                return self._decision(
                    accepted=False,
                    status=ROUTE_BLOCKED,
                    reason=decision.reason,
                    tenant_id=tenant_id,
                    metadata={
                        "backpressure_decision": decision.to_dict(),
                    },
                )
        candidates = self._candidate_jobs(
            tenant_id=tenant_id,
            limit=50,
        )

        if not candidates:
            return self._decision(
                accepted=False,
                status=ROUTE_SKIPPED,
                reason="No routable jobs available.",
                tenant_id=tenant_id,
            )

        workers = self._available_workers()

        if not workers:
            return self._decision(
                accepted=False,
                status=ROUTE_SKIPPED,
                reason="No available workers.",
                tenant_id=tenant_id,
            )

        best = self._choose_best_route(
            jobs=candidates,
            workers=workers,
        )

        if best is None:
            return self._decision(
                accepted=False,
                status=ROUTE_SKIPPED,
                reason="No compatible worker/job route found.",
                tenant_id=tenant_id,
            )

        job = best["job"]
        worker = best["worker"]
        required_capability = best.get("required_capability")

        leased = self.queue.lease_next(
            worker_id=worker.worker_id,
            tenant_id=job.get("tenant_id"),
            lease_ms=lease_ms,
        )

        if leased is None:
            return self._decision(
                accepted=False,
                status=ROUTE_SKIPPED,
                reason="Job was not leased. It may have been claimed by another worker.",
                tenant_id=job.get("tenant_id"),
                job_id=job.get("job_id"),
                worker_id=worker.worker_id,
                job_type=job.get("job_type"),
                required_capability=required_capability,
            )

        try:
            self.worker_orchestrator.heartbeat(
                worker.worker_id,
                status=WORKER_STATUS_BUSY,
                active_jobs=int(getattr(worker, "active_jobs", 0) or 0) + 1,
            )
        except Exception:
            pass

        decision = self._decision(
            accepted=True,
            status=ROUTE_ACCEPTED,
            reason="Job routed and leased.",
            tenant_id=job.get("tenant_id"),
            job_id=getattr(leased, "job_id", job.get("job_id")),
            worker_id=worker.worker_id,
            job_type=job.get("job_type"),
            required_capability=required_capability,
            score=best.get("score", 0),
            metadata={
                "lease_expires_ms": getattr(leased, "lease_expires_ms", None),
                "priority": job.get("priority"),
            },
        )

        self._emit(
            "DISTRIBUTED_JOB_ROUTED",
            decision.to_dict(),
        )

        return decision

    def route_batch(
            self,
            *,
            tenant_id: Optional[str] = None,
            max_routes: int = 10,
            lease_ms: int = 120_000,
    ) -> List[RouteDecision]:

        if self.backpressure_controller is not None:
            pressure = self.backpressure_controller.should_route(
                tenant_id=tenant_id or "default",
                context={
                    "source": "distributed_execution_router_batch",
                },
            )

            if pressure.freeze_tenant:
                self.backpressure_controller.enforce_freeze_if_needed(pressure)

            if not pressure.allowed:
                return [
                    self._decision(
                        accepted=False,
                        status=ROUTE_BLOCKED,
                        reason=pressure.reason,
                        tenant_id=tenant_id,
                        metadata={
                            "backpressure_decision": pressure.to_dict(),
                        },
                    )
                ]

            max_routes = min(
                max_routes,
                pressure.max_routes,
            )

        decisions = []

        for _ in range(max_routes):
            decision = self.route_next(
                tenant_id=tenant_id,
                lease_ms=lease_ms,
            )

            decisions.append(decision)

            if not decision.accepted:
                break

        return decisions

    # ========================================================
    # JOB / WORKER SELECTION
    # ========================================================

    def _candidate_jobs(
        self,
        *,
        tenant_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        if self.queue is None:
            return []

        try:
            jobs = self.queue.list_jobs(
                tenant_id=tenant_id,
                limit=limit,
            )
        except TypeError:
            jobs = self.queue.list_jobs(
                limit=limit,
            )

        routable = []

        for job in jobs:
            status = job.get("status")

            if status not in {"PENDING", "RETRY"}:
                continue

            routable.append(job)

        routable.sort(
            key=lambda j: (
                int(j.get("priority") or 100),
                int(j.get("created_at_ms") or 0),
            )
        )

        return routable

    def _available_workers(self) -> List[Any]:
        try:
            workers = self.worker_orchestrator.list_workers()
        except Exception:
            return []

        available = []

        for worker in workers:
            status = getattr(worker, "status", None)

            if status in {
                WORKER_STATUS_OFFLINE,
                WORKER_STATUS_QUARANTINED,
                WORKER_STATUS_DEGRADED,
            }:
                continue

            active_jobs = int(getattr(worker, "active_jobs", 0) or 0)
            max_jobs = int(getattr(worker, "max_concurrent_jobs", 1) or 1)

            if active_jobs >= max_jobs:
                continue

            available.append(worker)

        return available

    def _choose_best_route(
        self,
        *,
        jobs: List[Dict[str, Any]],
        workers: List[Any],
    ) -> Optional[Dict[str, Any]]:
        best = None

        for job in jobs:
            required_capability = self._required_capability(job)

            for worker in workers:
                score = self._score_worker_for_job(
                    worker=worker,
                    job=job,
                    required_capability=required_capability,
                )

                if score < 0:
                    continue

                route = {
                    "job": job,
                    "worker": worker,
                    "required_capability": required_capability,
                    "score": score,
                }

                if best is None or score > best["score"]:
                    best = route

        return best

    def _required_capability(
        self,
        job: Dict[str, Any],
    ) -> Optional[str]:
        job_type = job.get("job_type")
        action = str(job.get("action") or "").upper()
        payload = job.get("payload") or {}

        if job_type == JOB_TYPE_ROLLBACK:
            return CAPABILITY_ROLLBACK

        if job_type == JOB_TYPE_GRAPH:
            return CAPABILITY_ORCHESTRATION

        if action in {
            "ISOLATE_ENDPOINT",
            "UNISOLATE_ENDPOINT",
            "KILL_PROCESS",
            "COLLECT_ENDPOINT_TELEMETRY",
        }:
            return CAPABILITY_ENDPOINT

        if action in {
            "DISABLE_USER",
            "ENABLE_USER",
            "REVOKE_SESSIONS",
            "RESET_PASSWORD",
        }:
            return CAPABILITY_IDENTITY

        if action in {
            "QUARANTINE_EMAIL",
            "DELETE_EMAIL",
            "RESTORE_EMAIL",
            "SEARCH_MAILBOX",
        }:
            return CAPABILITY_MAILBOX

        connector_id = (
            job.get("connector_id")
            or payload.get("connector_id")
            if isinstance(payload, dict)
            else None
        )

        if connector_id:
            return CAPABILITY_CONNECTOR

        return CAPABILITY_ORCHESTRATION

    def _score_worker_for_job(
        self,
        *,
        worker: Any,
        job: Dict[str, Any],
        required_capability: Optional[str],
    ) -> int:
        score = 100

        capabilities = set(getattr(worker, "capabilities", []) or [])
        tenant_affinity = set(getattr(worker, "tenant_affinity", []) or [])

        tenant_id = job.get("tenant_id") or "default"

        if required_capability and capabilities:
            if required_capability not in capabilities:
                return -1
            score += 50

        if tenant_affinity:
            if tenant_id not in tenant_affinity:
                return -1
            score += 30

        active_jobs = int(getattr(worker, "active_jobs", 0) or 0)
        max_jobs = int(getattr(worker, "max_concurrent_jobs", 1) or 1)

        score += max(0, (max_jobs - active_jobs) * 10)

        priority = int(job.get("priority") or 100)
        score += max(0, 100 - priority)

        status = getattr(worker, "status", None)

        if status == WORKER_STATUS_IDLE:
            score += 20
        elif status == WORKER_STATUS_ONLINE:
            score += 10
        elif status == WORKER_STATUS_BUSY:
            score -= 10

        return score

    # ========================================================
    # HELPERS
    # ========================================================

    def _decision(
        self,
        *,
        accepted: bool,
        status: str,
        reason: str,
        job_id: Optional[str] = None,
        worker_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        job_type: Optional[str] = None,
        required_capability: Optional[str] = None,
        score: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RouteDecision:
        return RouteDecision(
            decision_id=f"ROUTE-{uuid.uuid4().hex[:12].upper()}",
            accepted=accepted,
            status=status,
            reason=reason,
            job_id=job_id,
            worker_id=worker_id,
            tenant_id=tenant_id,
            job_type=job_type,
            required_capability=required_capability,
            score=score,
            metadata=metadata or {},
        )

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
                source="distributed_execution_router",
                severity="INFO",
                payload=payload,
            )
        except TypeError:
            try:
                self.event_bus.publish(
                    event_type=event_type,
                    payload=payload,
                    tenant_id=payload.get("tenant_id") or "default",
                    source="distributed_execution_router",
                )
            except Exception:
                pass
        except Exception:
            pass


_DEFAULT_ROUTER: Optional[DistributedExecutionRouter] = None


def get_distributed_execution_router(
    *,
    queue: Any = None,
    worker_orchestrator: Any = None,
    storage: Any = None,
    event_bus: Any = None,
    reset: bool = False,
) -> DistributedExecutionRouter:
    global _DEFAULT_ROUTER

    if reset or _DEFAULT_ROUTER is None:
        _DEFAULT_ROUTER = DistributedExecutionRouter(
            queue=queue,
            worker_orchestrator=worker_orchestrator,
            storage=storage,
            event_bus=event_bus,
        )

    return _DEFAULT_ROUTER