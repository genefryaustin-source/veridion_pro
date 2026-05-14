"""
core/runtime/execution_control_plane.py

Execution Control Plane.

Single runtime coordinator for:
- distributed queue
- worker orchestrator
- lease watchdog
- autonomy governor
- connector execution fabric
- execution sandbox
- case orchestrator
- graph engine
- action execution router

This is the brainstem of distributed autonomous execution.
"""

from __future__ import annotations

import time
import uuid
import traceback
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List


try:
    from core.events.event_subscribers import dispatch_event
except Exception:
    def dispatch_event(*args, **kwargs):
        return None


try:
    from core.runtime.distributed_execution_queue import (
        DistributedExecutionQueue,
        JOB_TYPE_ACTION,
        JOB_TYPE_GRAPH,
        JOB_TYPE_ROLLBACK,
    )
except Exception:
    DistributedExecutionQueue = None
    JOB_TYPE_ACTION = "ACTION"
    JOB_TYPE_GRAPH = "GRAPH"
    JOB_TYPE_ROLLBACK = "ROLLBACK"


try:
    from core.runtime.worker_orchestrator import (
        get_worker_orchestrator,
        WORKER_STATUS_ONLINE,
        WORKER_STATUS_BUSY,
        WORKER_STATUS_IDLE,
    )
except Exception:
    get_worker_orchestrator = None
    WORKER_STATUS_ONLINE = "ONLINE"
    WORKER_STATUS_BUSY = "BUSY"
    WORKER_STATUS_IDLE = "IDLE"


try:
    from core.runtime.lease_watchdog import (
        LeaseWatchdog,
        LeaseWatchdogConfig,
    )
except Exception:
    LeaseWatchdog = None
    LeaseWatchdogConfig = None


try:
    from core.governance.autonomy_governor import (
        get_autonomy_governor,
        MODE_ASSISTED,
        DECISION_CONTINUE,
        DECISION_THROTTLE,
        DECISION_REQUIRE_APPROVAL,
        DECISION_FREEZE,
        DECISION_LOCKDOWN,
    )
except Exception:
    get_autonomy_governor = None
    MODE_ASSISTED = "ASSISTED"
    DECISION_CONTINUE = "CONTINUE"
    DECISION_THROTTLE = "THROTTLE"
    DECISION_REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    DECISION_FREEZE = "FREEZE"
    DECISION_LOCKDOWN = "LOCKDOWN"


try:
    from core.runtime.tenant_execution_context import (
        build_tenant_context,
        serialize_tenant_context,
        TenantExecutionPolicy,
    )
except Exception:
    build_tenant_context = None
    serialize_tenant_context = None
    TenantExecutionPolicy = None


try:
    from core.agents.action_execution_router import ActionExecutionRouter
except Exception:
    ActionExecutionRouter = None


try:
    from core.agents.execution_graph_engine import ExecutionGraphEngine
except Exception:
    ExecutionGraphEngine = None


@dataclass
class ControlPlaneConfig:
    queue_db_path: str = "data/distributed_execution_queue.db"
    dry_run: bool = True

    autonomy_mode: str = MODE_ASSISTED

    watchdog_enabled: bool = True
    governor_enabled: bool = True
    worker_orchestration_enabled: bool = True

    default_tenant_id: str = "default"

    worker_poll_interval_seconds: int = 5
    lease_ms: int = 120_000

    allow_destructive: bool = False


@dataclass
class ControlPlaneSubmission:
    submission_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    job_id: Optional[str] = None
    job_type: str = JOB_TYPE_ACTION
    tenant_id: str = "default"
    accepted: bool = False
    blocked: bool = False
    reason: str = ""
    governor_decision: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ControlPlaneRunResult:
    success: bool
    worker_id: Optional[str] = None
    job_id: Optional[str] = None
    status: str = "UNKNOWN"
    message: str = ""
    result: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


class ExecutionControlPlane:
    """
    Central runtime coordination layer.
    """

    def __init__(
        self,
        storage: Optional[Any] = None,
        config: Optional[ControlPlaneConfig] = None,
        app_config: Optional[Dict[str, Any]] = None,
    ):
        self.storage = storage
        self.config = config or ControlPlaneConfig()
        self.app_config = app_config or {"dry_run": self.config.dry_run}

        self.control_plane_id = f"control-plane-{uuid.uuid4()}"

        self.queue = (
            DistributedExecutionQueue(db_path=self.config.queue_db_path)
            if DistributedExecutionQueue is not None
            else None
        )

        self.worker_orchestrator = (
            get_worker_orchestrator(
                db_path=self.config.queue_db_path,
                queue=self.queue,
            )
            if get_worker_orchestrator
            else None
        )

        self.watchdog = (
            LeaseWatchdog(
                queue=self.queue,
                config=LeaseWatchdogConfig(
                    queue_db_path=self.config.queue_db_path,
                ) if LeaseWatchdogConfig else None,
                storage=storage,
            )
            if LeaseWatchdog and self.config.watchdog_enabled
            else None
        )

        self.governor = (
            get_autonomy_governor(
                queue_db_path=self.config.queue_db_path,
                queue=self.queue,
            )
            if get_autonomy_governor and self.config.governor_enabled
            else None
        )

    # ========================================================
    # EVENTING
    # ========================================================

    def emit_event(self, event_type: str, payload: Optional[Dict[str, Any]] = None) -> None:
        dispatch_event(
            event_type=event_type,
            payload=payload or {},
            source="execution_control_plane",
        )

    # ========================================================
    # GOVERNOR
    # ========================================================

    def evaluate_governor(
        self,
        tenant_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Any:
        if self.governor is None:
            return None

        return self.governor.evaluate(
            autonomy_mode=self.config.autonomy_mode,
            tenant_id=tenant_id,
            context=context or {},
            persist=True,
        )

    def _governor_blocks_submission(self, decision: Any) -> bool:
        if decision is None:
            return False

        decision_type = getattr(decision, "decision", None)

        return decision_type in {
            DECISION_REQUIRE_APPROVAL,
            DECISION_FREEZE,
            DECISION_LOCKDOWN,
        }

    # ========================================================
    # TENANT CONTEXT
    # ========================================================

    def build_tenant_context_json(
        self,
        tenant_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        context = context or {}

        if not build_tenant_context or not serialize_tenant_context:
            return None

        policy = None

        if TenantExecutionPolicy:
            policy = TenantExecutionPolicy(
                allow_autonomous_execution=True,
                allow_destructive_actions=bool(context.get("allow_destructive", False)),
                allow_identity_actions=True,
                allow_endpoint_actions=True,
                default_autonomy_mode=self.config.autonomy_mode,
            )

        tenant_ctx = build_tenant_context(
            tenant_id=tenant_id,
            actor=context.get("actor", "execution_control_plane"),
            autonomy_mode=context.get("autonomy_mode") or self.config.autonomy_mode,
            case_id=context.get("case_id"),
            graph_id=context.get("graph_id"),
            evidence_ids=context.get("evidence_ids") or [],
            policy=policy,
            metadata={
                "control_plane_id": self.control_plane_id,
                **context.get("metadata", {}),
            },
        )

        return serialize_tenant_context(tenant_ctx)

    # ========================================================
    # SUBMISSIONS
    # ========================================================

    def submit_action(
        self,
        agent_name: str,
        action: str,
        context: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[str] = None,
        priority: int = 100,
        allow_destructive: Optional[bool] = None,
    ) -> ControlPlaneSubmission:
        context = context or {}
        tenant_id = tenant_id or context.get("tenant_id") or self.config.default_tenant_id

        governor_decision = self.evaluate_governor(
            tenant_id=tenant_id,
            context=context,
        )

        if self._governor_blocks_submission(governor_decision):
            submission = ControlPlaneSubmission(
                job_type=JOB_TYPE_ACTION,
                tenant_id=tenant_id,
                accepted=False,
                blocked=True,
                reason=getattr(governor_decision, "reason", "governor_blocked"),
                governor_decision=getattr(governor_decision, "decision", None),
                metadata={
                    "agent_name": agent_name,
                    "action": action,
                    "context": self._safe_context(context),
                },
            )

            self.emit_event(
                "CONTROL_PLANE_ACTION_SUBMISSION_BLOCKED",
                submission.__dict__,
            )

            return submission

        if self.queue is None:
            return ControlPlaneSubmission(
                job_type=JOB_TYPE_ACTION,
                tenant_id=tenant_id,
                accepted=False,
                blocked=True,
                reason="queue_unavailable",
            )

        job_context = {
            **context,
            "tenant_id": tenant_id,
            "allow_destructive": (
                self.config.allow_destructive
                if allow_destructive is None
                else allow_destructive
            ),
        }

        tenant_context_json = self.build_tenant_context_json(
            tenant_id=tenant_id,
            context=job_context,
        )

        job_id = self.queue.enqueue_action(
            agent_name=agent_name,
            action=action,
            context=job_context,
            tenant_id=tenant_id,
            tenant_context_json=tenant_context_json,
            priority=priority,
        )

        submission = ControlPlaneSubmission(
            job_id=job_id,
            job_type=JOB_TYPE_ACTION,
            tenant_id=tenant_id,
            accepted=True,
            blocked=False,
            reason="accepted",
            governor_decision=getattr(governor_decision, "decision", None),
            metadata={
                "agent_name": agent_name,
                "action": action,
            },
        )

        self.emit_event(
            "CONTROL_PLANE_ACTION_SUBMITTED",
            submission.__dict__,
        )

        return submission

    def submit_graph(
        self,
        graph_context: Dict[str, Any],
        tenant_id: Optional[str] = None,
        priority: int = 50,
    ) -> ControlPlaneSubmission:
        tenant_id = tenant_id or graph_context.get("tenant_id") or self.config.default_tenant_id

        governor_decision = self.evaluate_governor(
            tenant_id=tenant_id,
            context=graph_context,
        )

        if self._governor_blocks_submission(governor_decision):
            submission = ControlPlaneSubmission(
                job_type=JOB_TYPE_GRAPH,
                tenant_id=tenant_id,
                accepted=False,
                blocked=True,
                reason=getattr(governor_decision, "reason", "governor_blocked"),
                governor_decision=getattr(governor_decision, "decision", None),
                metadata={
                    "graph_context": self._safe_context(graph_context),
                },
            )

            self.emit_event(
                "CONTROL_PLANE_GRAPH_SUBMISSION_BLOCKED",
                submission.__dict__,
            )

            return submission

        if self.queue is None:
            return ControlPlaneSubmission(
                job_type=JOB_TYPE_GRAPH,
                tenant_id=tenant_id,
                accepted=False,
                blocked=True,
                reason="queue_unavailable",
            )

        tenant_context_json = self.build_tenant_context_json(
            tenant_id=tenant_id,
            context=graph_context,
        )

        job_id = self.queue.enqueue_graph(
            graph_context={
                **graph_context,
                "tenant_id": tenant_id,
            },
            tenant_id=tenant_id,
            tenant_context_json=tenant_context_json,
            priority=priority,
        )

        submission = ControlPlaneSubmission(
            job_id=job_id,
            job_type=JOB_TYPE_GRAPH,
            tenant_id=tenant_id,
            accepted=True,
            blocked=False,
            reason="accepted",
            governor_decision=getattr(governor_decision, "decision", None),
            metadata={
                "graph_context": self._safe_context(graph_context),
            },
        )

        self.emit_event(
            "CONTROL_PLANE_GRAPH_SUBMITTED",
            submission.__dict__,
        )

        return submission

    def submit_rollback(
        self,
        rollback_payload: Dict[str, Any],
        tenant_id: Optional[str] = None,
        priority: int = 1,
    ) -> ControlPlaneSubmission:
        tenant_id = tenant_id or rollback_payload.get("tenant_id") or self.config.default_tenant_id

        if self.queue is None:
            return ControlPlaneSubmission(
                job_type=JOB_TYPE_ROLLBACK,
                tenant_id=tenant_id,
                accepted=False,
                blocked=True,
                reason="queue_unavailable",
            )

        tenant_context_json = self.build_tenant_context_json(
            tenant_id=tenant_id,
            context=rollback_payload,
        )

        job_id = self.queue.enqueue_rollback(
            rollback_payload={
                **rollback_payload,
                "tenant_id": tenant_id,
            },
            tenant_id=tenant_id,
            tenant_context_json=tenant_context_json,
            priority=priority,
        )

        submission = ControlPlaneSubmission(
            job_id=job_id,
            job_type=JOB_TYPE_ROLLBACK,
            tenant_id=tenant_id,
            accepted=True,
            blocked=False,
            reason="accepted",
        )

        self.emit_event(
            "CONTROL_PLANE_ROLLBACK_SUBMITTED",
            submission.__dict__,
        )

        return submission

    # ========================================================
    # WORKERS
    # ========================================================

    def register_worker(
        self,
        worker_id: Optional[str] = None,
        hostname: str = "unknown",
        tenant_affinity: Optional[List[str]] = None,
        capabilities: Optional[List[str]] = None,
        max_concurrent_jobs: int = 1,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        if self.worker_orchestrator is None:
            return None

        return self.worker_orchestrator.register_worker(
            worker_id=worker_id,
            hostname=hostname,
            tenant_affinity=tenant_affinity,
            capabilities=capabilities,
            max_concurrent_jobs=max_concurrent_jobs,
            metadata={
                "control_plane_id": self.control_plane_id,
                **(metadata or {}),
            },
        )

    def worker_heartbeat(
        self,
        worker_id: str,
        status: str = WORKER_STATUS_ONLINE,
        active_jobs: Optional[int] = None,
        last_error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        if self.worker_orchestrator is None:
            return False

        return self.worker_orchestrator.heartbeat(
            worker_id=worker_id,
            status=status,
            active_jobs=active_jobs,
            last_error=last_error,
            metadata=metadata,
        )

    def run_worker_once(
        self,
        worker_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> ControlPlaneRunResult:
        worker_id = worker_id or f"worker-{uuid.uuid4()}"

        if self.queue is None:
            return ControlPlaneRunResult(
                success=False,
                worker_id=worker_id,
                status="QUEUE_UNAVAILABLE",
                error="queue_unavailable",
            )

        if self.watchdog is not None:
            self.watchdog.run_once()

        try:
            job = self.queue.lease_next(
                worker_id=worker_id,
                tenant_id=tenant_id,
                lease_ms=self.config.lease_ms,
            )

            if job is None:
                return ControlPlaneRunResult(
                    success=True,
                    worker_id=worker_id,
                    status="NO_JOB",
                    message="No job available.",
                )

            if self.worker_orchestrator is not None:
                self.worker_orchestrator.heartbeat(
                    worker_id,
                    status=WORKER_STATUS_BUSY,
                    active_jobs=1,
                )

            result = self.queue.execute_job(
                job,
                worker_id=worker_id,
                storage=self.storage,
                config=self.app_config,
            )

            if result.get("success"):
                self.queue.complete(
                    getattr(job, "job_id", None),
                    worker_id,
                    result,
                )
            else:
                self.queue.fail(
                    getattr(job, "job_id", None),
                    worker_id,
                    result.get("error") or str(result),
                )

            if self.worker_orchestrator is not None:
                self.worker_orchestrator.heartbeat(
                    worker_id,
                    status=WORKER_STATUS_IDLE,
                    active_jobs=0,
                )

            run_result = ControlPlaneRunResult(
                success=bool(result.get("success")),
                worker_id=worker_id,
                job_id=getattr(job, "job_id", None),
                status=result.get("status") or "COMPLETED",
                result=result,
                error=result.get("error"),
            )

            self.emit_event(
                "CONTROL_PLANE_WORKER_RUN_COMPLETED",
                run_result.__dict__,
            )

            return run_result

        except Exception:
            error = traceback.format_exc()

            self.emit_event(
                "CONTROL_PLANE_WORKER_RUN_FAILED",
                {
                    "worker_id": worker_id,
                    "tenant_id": tenant_id,
                    "error": error,
                },
            )

            if self.worker_orchestrator is not None:
                self.worker_orchestrator.heartbeat(
                    worker_id,
                    status=WORKER_STATUS_IDLE,
                    active_jobs=0,
                    last_error=error,
                )

            return ControlPlaneRunResult(
                success=False,
                worker_id=worker_id,
                status="FAILED",
                error=error,
            )

    # ========================================================
    # SUPERVISION
    # ========================================================

    def run_supervision_once(self) -> Dict[str, Any]:
        watchdog_result = None
        governor_result = None
        worker_result = None

        if self.watchdog is not None:
            watchdog_result = self.watchdog.run_once()

        if self.governor is not None:
            governor_result = self.governor.evaluate(
                autonomy_mode=self.config.autonomy_mode,
                persist=True,
            )

        if self.worker_orchestrator is not None:
            worker_result = self.worker_orchestrator.rebalance_workloads()

        result = {
            "control_plane_id": self.control_plane_id,
            "watchdog": watchdog_result,
            "governor": governor_result.__dict__ if governor_result else None,
            "worker_rebalance": worker_result,
            "created_at_ms": self._now_ms(),
        }

        self.emit_event(
            "CONTROL_PLANE_SUPERVISION_COMPLETED",
            result,
        )

        return result

    # ========================================================
    # STATUS
    # ========================================================

    def status(self) -> Dict[str, Any]:
        queue_stats = self.queue.get_stats() if self.queue else {}
        worker_stats = (
            self.worker_orchestrator.worker_stats()
            if self.worker_orchestrator
            else {}
        )

        governor_decision = (
            self.governor.evaluate(
                autonomy_mode=self.config.autonomy_mode,
                persist=False,
            )
            if self.governor
            else None
        )

        return {
            "control_plane_id": self.control_plane_id,
            "queue": queue_stats,
            "workers": worker_stats,
            "governor": governor_decision.__dict__ if governor_decision else None,
            "watchdog_enabled": self.watchdog is not None,
            "dry_run": self.config.dry_run,
            "autonomy_mode": self.config.autonomy_mode,
        }

    # ========================================================
    # HELPERS
    # ========================================================

    def _safe_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        sensitive = {
            "password",
            "token",
            "access_token",
            "refresh_token",
            "secret",
            "client_secret",
            "api_key",
        }

        clean = {}

        for key, value in context.items():
            if key.lower() in sensitive:
                clean[key] = "***REDACTED***"
            else:
                clean[key] = value

        return clean

    def _now_ms(self) -> int:
        return int(time.time() * 1000)


_DEFAULT_CONTROL_PLANE: Optional[ExecutionControlPlane] = None


def get_execution_control_plane(
    storage: Optional[Any] = None,
    config: Optional[ControlPlaneConfig] = None,
    app_config: Optional[Dict[str, Any]] = None,
) -> ExecutionControlPlane:
    global _DEFAULT_CONTROL_PLANE

    if _DEFAULT_CONTROL_PLANE is None:
        _DEFAULT_CONTROL_PLANE = ExecutionControlPlane(
            storage=storage,
            config=config,
            app_config=app_config,
        )

    return _DEFAULT_CONTROL_PLANE