"""
core/runtime/execution_backpressure_controller.py

Execution Backpressure Controller.

Purpose:
- prevent autonomous execution storms
- throttle runtime throughput
- protect SaaS connector APIs
- detect retry/dead-letter floods
- reduce tenant concurrency
- pause risky autonomy
- preserve distributed execution stability
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


PRESSURE_NORMAL = "NORMAL"
PRESSURE_ELEVATED = "ELEVATED"
PRESSURE_HIGH = "HIGH"
PRESSURE_CRITICAL = "CRITICAL"

DECISION_ALLOW = "ALLOW"
DECISION_THROTTLE = "THROTTLE"
DECISION_PAUSE = "PAUSE"
DECISION_FREEZE = "FREEZE"

DEFAULT_TENANT = "default"


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class BackpressureDecision:
    decision_id: str
    tenant_id: str
    pressure_level: str
    decision: str
    allowed: bool
    reason: str
    throttle_seconds: int = 0
    max_routes: int = 10
    max_worker_iterations: int = 10
    reduce_autonomy: bool = False
    freeze_tenant: bool = False
    findings: List[Dict[str, Any]] = field(default_factory=list)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ExecutionBackpressureController:
    def __init__(
        self,
        *,
        queue: Any = None,
        worker_orchestrator: Any = None,
        watchdog: Any = None,
        storage: Any = None,
        event_bus: Any = None,
    ) -> None:
        self.storage = storage

        self.queue = queue or getattr(storage, "execution_queue", None)

        self.worker_orchestrator = (
            worker_orchestrator
            or getattr(storage, "worker_orchestrator", None)
        )

        self.watchdog = (
            watchdog
            or getattr(storage, "lease_watchdog", None)
        )

        self.event_bus = event_bus or getattr(storage, "event_bus", None)

    # ========================================================
    # MAIN EVALUATION
    # ========================================================

    def evaluate(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        context: Optional[Dict[str, Any]] = None,
    ) -> BackpressureDecision:
        context = context or {}

        findings: List[Dict[str, Any]] = []

        stats = self._queue_stats()

        worker_stats = self._worker_stats()

        pressure_score = 0

        pending = int(stats.get("pending", 0))
        retry = int(stats.get("retry", 0))
        leased = int(stats.get("leased", 0))
        running = int(stats.get("running", 0))
        dead_letter = int(stats.get("dead_letter", 0))
        failed = int(stats.get("failed", 0))

        active_jobs = int(worker_stats.get("active_jobs", 0))
        total_workers = int(worker_stats.get("total_workers", 0))
        offline = int(worker_stats.get("offline", 0))
        degraded = int(worker_stats.get("degraded", 0))
        quarantined = int(worker_stats.get("quarantined", 0))

        # ----------------------------------------------------
        # QUEUE DEPTH PRESSURE
        # ----------------------------------------------------

        if pending >= 500:
            pressure_score += 20
            findings.append({
                "type": "QUEUE_DEPTH_HIGH",
                "pending": pending,
            })

        if pending >= 2000:
            pressure_score += 35
            findings.append({
                "type": "QUEUE_DEPTH_CRITICAL",
                "pending": pending,
            })

        # ----------------------------------------------------
        # RETRY STORM
        # ----------------------------------------------------

        if retry >= 50:
            pressure_score += 25
            findings.append({
                "type": "RETRY_STORM",
                "retry": retry,
            })

        if retry >= 250:
            pressure_score += 40
            findings.append({
                "type": "RETRY_STORM_CRITICAL",
                "retry": retry,
            })

        # ----------------------------------------------------
        # DEAD LETTER SPIKE
        # ----------------------------------------------------

        if dead_letter >= 10:
            pressure_score += 20
            findings.append({
                "type": "DEAD_LETTER_SPIKE",
                "dead_letter": dead_letter,
            })

        if dead_letter >= 100:
            pressure_score += 40
            findings.append({
                "type": "DEAD_LETTER_CRITICAL",
                "dead_letter": dead_letter,
            })

        # ----------------------------------------------------
        # WORKER SATURATION
        # ----------------------------------------------------

        if total_workers > 0:
            unavailable = offline + degraded + quarantined
            unavailable_ratio = unavailable / max(total_workers, 1)

            if unavailable_ratio >= 0.25:
                pressure_score += 20
                findings.append({
                    "type": "WORKER_POOL_DEGRADED",
                    "unavailable_ratio": unavailable_ratio,
                    "offline": offline,
                    "degraded": degraded,
                    "quarantined": quarantined,
                })

            if unavailable_ratio >= 0.50:
                pressure_score += 40
                findings.append({
                    "type": "WORKER_POOL_CRITICAL",
                    "unavailable_ratio": unavailable_ratio,
                })

        if leased + running > max(total_workers * 10, 25):
            pressure_score += 15
            findings.append({
                "type": "EXECUTION_SATURATION",
                "leased": leased,
                "running": running,
                "workers": total_workers,
            })

        # ----------------------------------------------------
        # FAILURE PRESSURE
        # ----------------------------------------------------

        if failed >= 25:
            pressure_score += 15
            findings.append({
                "type": "FAILURE_RATE_ELEVATED",
                "failed": failed,
            })

        if failed >= 150:
            pressure_score += 35
            findings.append({
                "type": "FAILURE_RATE_CRITICAL",
                "failed": failed,
            })

        # ----------------------------------------------------
        # CONTEXT OVERRIDES
        # ----------------------------------------------------

        connector_rate_limited = bool(
            context.get("connector_rate_limited")
            or context.get("rate_limited")
        )

        if connector_rate_limited:
            pressure_score += 35
            findings.append({
                "type": "CONNECTOR_RATE_LIMITED",
                "connector": context.get("connector_id"),
            })

        connector_degraded = bool(
            context.get("connector_degraded")
        )

        if connector_degraded:
            pressure_score += 25
            findings.append({
                "type": "CONNECTOR_DEGRADED",
                "connector": context.get("connector_id"),
            })

        # ----------------------------------------------------
        # DECISION
        # ----------------------------------------------------

        if pressure_score >= 100:
            decision = BackpressureDecision(
                decision_id=self._new_id(),
                tenant_id=tenant_id,
                pressure_level=PRESSURE_CRITICAL,
                decision=DECISION_FREEZE,
                allowed=False,
                reason="Critical execution pressure detected. Tenant execution should be frozen.",
                throttle_seconds=300,
                max_routes=0,
                max_worker_iterations=0,
                reduce_autonomy=True,
                freeze_tenant=True,
                findings=findings,
            )

        elif pressure_score >= 70:
            decision = BackpressureDecision(
                decision_id=self._new_id(),
                tenant_id=tenant_id,
                pressure_level=PRESSURE_HIGH,
                decision=DECISION_PAUSE,
                allowed=False,
                reason="High execution pressure detected. Pause autonomous routing temporarily.",
                throttle_seconds=120,
                max_routes=1,
                max_worker_iterations=1,
                reduce_autonomy=True,
                freeze_tenant=False,
                findings=findings,
            )

        elif pressure_score >= 35:
            decision = BackpressureDecision(
                decision_id=self._new_id(),
                tenant_id=tenant_id,
                pressure_level=PRESSURE_ELEVATED,
                decision=DECISION_THROTTLE,
                allowed=True,
                reason="Elevated execution pressure detected. Throttle runtime throughput.",
                throttle_seconds=30,
                max_routes=3,
                max_worker_iterations=3,
                reduce_autonomy=False,
                freeze_tenant=False,
                findings=findings,
            )

        else:
            decision = BackpressureDecision(
                decision_id=self._new_id(),
                tenant_id=tenant_id,
                pressure_level=PRESSURE_NORMAL,
                decision=DECISION_ALLOW,
                allowed=True,
                reason="Execution pressure normal.",
                throttle_seconds=0,
                max_routes=10,
                max_worker_iterations=10,
                findings=findings,
            )

        self._emit(
            "EXECUTION_BACKPRESSURE_EVALUATED",
            decision.to_dict(),
        )

        return decision

    # ========================================================
    # ENFORCEMENT HELPERS
    # ========================================================

    def should_route(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        context: Optional[Dict[str, Any]] = None,
    ) -> BackpressureDecision:
        return self.evaluate(
            tenant_id=tenant_id,
            context=context,
        )

    def apply_delay(
        self,
        decision: BackpressureDecision,
    ) -> None:
        if decision.throttle_seconds > 0:
            time.sleep(decision.throttle_seconds)

    def route_budget(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        context: Optional[Dict[str, Any]] = None,
    ) -> int:
        decision = self.evaluate(
            tenant_id=tenant_id,
            context=context,
        )

        return int(decision.max_routes)

    def worker_iteration_budget(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        context: Optional[Dict[str, Any]] = None,
    ) -> int:
        decision = self.evaluate(
            tenant_id=tenant_id,
            context=context,
        )

        return int(decision.max_worker_iterations)

    # ========================================================
    # FREEZE / GOVERNANCE HOOKS
    # ========================================================

    def enforce_freeze_if_needed(
        self,
        decision: BackpressureDecision,
    ) -> bool:
        if not decision.freeze_tenant:
            return False

        try:
            guardrails = getattr(
                self.storage,
                "safety_guardrails",
                None,
            )

            if guardrails is not None and hasattr(
                guardrails,
                "enable_emergency_freeze",
            ):
                guardrails.enable_emergency_freeze(
                    tenant_id=decision.tenant_id,
                    actor="execution_backpressure_controller",
                    reason=decision.reason,
                )

                self._emit(
                    "BACKPRESSURE_TENANT_FREEZE_TRIGGERED",
                    decision.to_dict(),
                )

                return True

        except Exception:
            pass

        return False

    # ========================================================
    # STATS
    # ========================================================

    def _queue_stats(self) -> Dict[str, Any]:
        if self.queue is None:
            return {}

        try:
            return self.queue.stats()
        except Exception:
            return {}

    def _worker_stats(self) -> Dict[str, Any]:
        if self.worker_orchestrator is None:
            return {}

        try:
            return self.worker_orchestrator.worker_stats()
        except Exception:
            return {}

    # ========================================================
    # INTERNAL
    # ========================================================

    def _new_id(self) -> str:
        return f"BACKPRESSURE-{uuid.uuid4().hex[:12].upper()}"

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
                tenant_id=payload.get("tenant_id") or DEFAULT_TENANT,
                source="execution_backpressure_controller",
                severity=payload.get("pressure_level") or "INFO",
                payload=payload,
            )
        except TypeError:
            try:
                self.event_bus.publish(
                    event_type=event_type,
                    payload=payload,
                    tenant_id=payload.get("tenant_id") or DEFAULT_TENANT,
                    source="execution_backpressure_controller",
                )
            except Exception:
                pass
        except Exception:
            pass


_DEFAULT_BACKPRESSURE_CONTROLLER: Optional[
    ExecutionBackpressureController
] = None


def get_execution_backpressure_controller(
    *,
    queue: Any = None,
    worker_orchestrator: Any = None,
    watchdog: Any = None,
    storage: Any = None,
    event_bus: Any = None,
    reset: bool = False,
) -> ExecutionBackpressureController:
    global _DEFAULT_BACKPRESSURE_CONTROLLER

    if reset or _DEFAULT_BACKPRESSURE_CONTROLLER is None:
        _DEFAULT_BACKPRESSURE_CONTROLLER = ExecutionBackpressureController(
            queue=queue,
            worker_orchestrator=worker_orchestrator,
            watchdog=watchdog,
            storage=storage,
            event_bus=event_bus,
        )

    return _DEFAULT_BACKPRESSURE_CONTROLLER