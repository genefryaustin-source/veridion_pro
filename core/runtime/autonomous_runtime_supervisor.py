"""
core/runtime/autonomous_runtime_supervisor.py

Autonomous Runtime Supervisor.

Purpose:
- continuous runtime oversight
- autonomous health monitoring
- recovery trigger orchestration
- backpressure activation
- policy-aware runtime supervision
- recovery storm prevention
- runtime mode management

Architecture Rules:
- no Streamlit/session_state dependency
- no shared SQLite connection
- no hidden runtime mutation
- service access through explicit injected dependencies/storage boundaries
"""

from __future__ import annotations

import threading
import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


MODE_NORMAL = "NORMAL"
MODE_DEGRADED = "DEGRADED"
MODE_CONTAINMENT = "CONTAINMENT"
MODE_LOCKDOWN = "LOCKDOWN"
MODE_RECOVERY = "RECOVERY"
MODE_MAINTENANCE = "MAINTENANCE"

SUPERVISOR_STOPPED = "STOPPED"
SUPERVISOR_RUNNING = "RUNNING"
SUPERVISOR_PAUSED = "PAUSED"
SUPERVISOR_ERROR = "ERROR"

RISK_LOW = "LOW"
RISK_MEDIUM = "MEDIUM"
RISK_HIGH = "HIGH"
RISK_CRITICAL = "CRITICAL"

DEFAULT_TENANT = "default"


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class RuntimeSupervisorEvent:
    event_id: str
    event_type: str
    severity: str
    message: str
    tenant_id: str = DEFAULT_TENANT
    runtime_mode: str = MODE_NORMAL
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RuntimeSupervisorCycleResult:
    cycle_id: str
    ok: bool
    status: str
    runtime_mode: str
    health_score: float = 100.0
    risk: str = RISK_LOW
    recovery_triggered: bool = False
    backpressure_triggered: bool = False
    watchdog_triggered: bool = False
    findings: List[Dict[str, Any]] = field(default_factory=list)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AutonomousRuntimeSupervisor:
    def __init__(
        self,
        *,
        registry: Any = None,
        lifecycle: Any = None,
        health_manager: Any = None,
        dependency_graph: Any = None,
        policy_manager: Any = None,
        recovery_manager: Any = None,
        backpressure_controller: Any = None,
        watchdog: Any = None,
        storage: Any = None,
        event_bus: Any = None,
        tenant_id: str = DEFAULT_TENANT,
        recovery_cooldown_ms: int = 300_000,
    ) -> None:
        self.storage = storage
        self.registry = registry or getattr(storage, "runtime_service_registry", None)
        self.lifecycle = lifecycle or getattr(storage, "runtime_lifecycle_manager", None)
        self.health_manager = health_manager or getattr(storage, "runtime_health_manager", None)
        self.dependency_graph = dependency_graph or getattr(storage, "runtime_dependency_graph", None)
        self.policy_manager = policy_manager or getattr(storage, "runtime_policy_manager", None)
        self.recovery_manager = recovery_manager or getattr(storage, "runtime_recovery_manager", None)
        self.backpressure_controller = (
            backpressure_controller
            or getattr(storage, "backpressure_controller", None)
        )
        self.watchdog = watchdog or getattr(storage, "lease_watchdog", None)
        self.event_bus = event_bus or getattr(storage, "event_bus", None)

        self.tenant_id = tenant_id
        self.recovery_cooldown_ms = recovery_cooldown_ms

        self._lock = threading.RLock()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

        self.status = SUPERVISOR_STOPPED
        self.runtime_mode = MODE_NORMAL
        self.last_cycle_ms: Optional[int] = None
        self.last_recovery_ms: Optional[int] = None
        self.cycle_count = 0
        self.recovery_count = 0
        self.error_count = 0

        self._events: List[RuntimeSupervisorEvent] = []
        self._cycles: List[RuntimeSupervisorCycleResult] = []

    # ========================================================
    # LOOP CONTROL
    # ========================================================

    def start(
        self,
        *,
        interval_seconds: float = 30.0,
        daemon: bool = True,
    ) -> bool:
        with self._lock:
            if self.status == SUPERVISOR_RUNNING:
                return True

            self._stop_event.clear()

            self._thread = threading.Thread(
                target=self.run_loop,
                kwargs={"interval_seconds": interval_seconds},
                daemon=daemon,
                name="AutonomousRuntimeSupervisor",
            )

            self.status = SUPERVISOR_RUNNING
            self._thread.start()

        self._record_event(
            event_type="AUTONOMOUS_RUNTIME_SUPERVISOR_STARTED",
            severity="INFO",
            message="Autonomous runtime supervisor started.",
        )

        return True

    def stop(self) -> bool:
        with self._lock:
            self._stop_event.set()
            self.status = SUPERVISOR_STOPPED

        self._record_event(
            event_type="AUTONOMOUS_RUNTIME_SUPERVISOR_STOPPED",
            severity="INFO",
            message="Autonomous runtime supervisor stopped.",
        )

        return True

    def pause(self) -> bool:
        with self._lock:
            self.status = SUPERVISOR_PAUSED

        self._record_event(
            event_type="AUTONOMOUS_RUNTIME_SUPERVISOR_PAUSED",
            severity="WARNING",
            message="Autonomous runtime supervisor paused.",
        )

        return True

    def resume(self) -> bool:
        with self._lock:
            self.status = SUPERVISOR_RUNNING

        self._record_event(
            event_type="AUTONOMOUS_RUNTIME_SUPERVISOR_RESUMED",
            severity="INFO",
            message="Autonomous runtime supervisor resumed.",
        )

        return True

    def run_loop(
        self,
        *,
        interval_seconds: float = 30.0,
    ) -> None:
        while not self._stop_event.is_set():
            if self.status == SUPERVISOR_RUNNING:
                try:
                    self.run_cycle()
                except Exception as exc:
                    self.error_count += 1
                    self.status = SUPERVISOR_ERROR
                    self._record_event(
                        event_type="AUTONOMOUS_RUNTIME_SUPERVISOR_ERROR",
                        severity="CRITICAL",
                        message=str(exc),
                        metadata={"error": str(exc)},
                    )

            time.sleep(interval_seconds)

    # ========================================================
    # MAIN SUPERVISION CYCLE
    # ========================================================

    def run_cycle(
        self,
        *,
        tenant_id: Optional[str] = None,
        force_recovery: bool = False,
    ) -> RuntimeSupervisorCycleResult:
        tenant_id = tenant_id or self.tenant_id
        cycle_id = f"SUP-CYCLE-{uuid.uuid4().hex[:12].upper()}"

        findings: List[Dict[str, Any]] = []
        actions: List[Dict[str, Any]] = []
        errors: List[str] = []

        recovery_triggered = False
        backpressure_triggered = False
        watchdog_triggered = False

        health_score = 100.0
        risk = RISK_LOW

        try:
            health_snapshot = self._evaluate_health()
            if health_snapshot:
                hdict = (
                    health_snapshot.to_dict()
                    if hasattr(health_snapshot, "to_dict")
                    else dict(health_snapshot)
                )

                health_score = float(hdict.get("score", 100.0) or 100.0)
                risk = str(hdict.get("risk", RISK_LOW) or RISK_LOW)

                findings.extend(hdict.get("findings", []) or [])

        except Exception as exc:
            errors.append(f"health_evaluation_failed: {exc}")

        try:
            policy_findings = self._audit_policy()
            findings.extend(policy_findings)
        except Exception as exc:
            errors.append(f"policy_audit_failed: {exc}")

        try:
            topology_findings = self._validate_topology()
            findings.extend(topology_findings)
        except Exception as exc:
            errors.append(f"dependency_validation_failed: {exc}")

        runtime_mode = self._derive_runtime_mode(
            risk=risk,
            health_score=health_score,
            findings=findings,
        )

        self.runtime_mode = runtime_mode

        # ----------------------------------------------------
        # Backpressure
        # ----------------------------------------------------

        if self._should_trigger_backpressure(
            risk=risk,
            findings=findings,
        ):
            ok, action = self._trigger_backpressure(
                tenant_id=tenant_id,
                reason="supervisor_pressure_detection",
            )
            backpressure_triggered = ok
            actions.append(action)

        # ----------------------------------------------------
        # Watchdog
        # ----------------------------------------------------

        if self._should_run_watchdog(findings):
            ok, action = self._run_watchdog()
            watchdog_triggered = ok
            actions.append(action)

        # ----------------------------------------------------
        # Recovery
        # ----------------------------------------------------

        if force_recovery or self._should_recover(
            risk=risk,
            health_score=health_score,
            findings=findings,
        ):
            if self._recovery_cooldown_clear() or force_recovery:
                ok, action = self._trigger_recovery(
                    tenant_id=tenant_id,
                    force=False,
                )
                recovery_triggered = ok
                actions.append(action)

                if ok:
                    self.last_recovery_ms = _now_ms()
                    self.recovery_count += 1
            else:
                actions.append({
                    "action": "RECOVERY_SKIPPED",
                    "reason": "recovery_cooldown_active",
                    "last_recovery_ms": self.last_recovery_ms,
                })

        ok = len(errors) == 0

        result = RuntimeSupervisorCycleResult(
            cycle_id=cycle_id,
            ok=ok,
            status=SUPERVISOR_RUNNING if ok else SUPERVISOR_ERROR,
            runtime_mode=runtime_mode,
            health_score=health_score,
            risk=risk,
            recovery_triggered=recovery_triggered,
            backpressure_triggered=backpressure_triggered,
            watchdog_triggered=watchdog_triggered,
            findings=findings,
            actions=actions,
            errors=errors,
        )

        with self._lock:
            self.cycle_count += 1
            self.last_cycle_ms = _now_ms()
            self._cycles.append(result)
            self._cycles = self._cycles[-250:]

        self._record_event(
            event_type="AUTONOMOUS_RUNTIME_SUPERVISOR_CYCLE_COMPLETED",
            severity=risk,
            message=f"Supervisor cycle completed in {runtime_mode} mode.",
            runtime_mode=runtime_mode,
            metadata=result.to_dict(),
        )

        return result

    # ========================================================
    # DECISION LOGIC
    # ========================================================

    def _derive_runtime_mode(
        self,
        *,
        risk: str,
        health_score: float,
        findings: List[Dict[str, Any]],
    ) -> str:
        finding_types = {f.get("type") for f in findings}

        if risk == RISK_CRITICAL or health_score < 35:
            return MODE_LOCKDOWN

        if "RUNTIME_POLICY_VIOLATIONS" in finding_types:
            return MODE_CONTAINMENT

        if risk == RISK_HIGH or health_score < 65:
            return MODE_RECOVERY

        if risk == RISK_MEDIUM or health_score < 85:
            return MODE_DEGRADED

        return MODE_NORMAL

    def _should_trigger_backpressure(
        self,
        *,
        risk: str,
        findings: List[Dict[str, Any]],
    ) -> bool:
        finding_types = {f.get("type") for f in findings}

        if risk in {RISK_HIGH, RISK_CRITICAL}:
            return True

        if finding_types.intersection({
            "QUEUE_DEPTH_HIGH",
            "RETRY_STORM",
            "DEAD_LETTER_SPIKE",
            "WORKER_POOL_DEGRADED",
        }):
            return True

        return False

    def _should_run_watchdog(
        self,
        findings: List[Dict[str, Any]],
    ) -> bool:
        finding_types = {f.get("type") for f in findings}

        return bool(
            finding_types.intersection({
                "RETRY_STORM",
                "DEAD_LETTER_SPIKE",
                "WORKER_POOL_DEGRADED",
                "QUEUE_DEPTH_HIGH",
            })
        )

    def _should_recover(
        self,
        *,
        risk: str,
        health_score: float,
        findings: List[Dict[str, Any]],
    ) -> bool:
        if risk in {RISK_HIGH, RISK_CRITICAL}:
            return True

        if health_score < 65:
            return True

        finding_types = {f.get("type") for f in findings}

        if finding_types.intersection({
            "SERVICE_UNAVAILABLE",
            "SERVICE_DEGRADED",
            "SERVICE_QUARANTINED",
            "RUNTIME_POLICY_VIOLATIONS",
        }):
            return True

        return False

    def _recovery_cooldown_clear(self) -> bool:
        if not self.last_recovery_ms:
            return True

        return (_now_ms() - self.last_recovery_ms) >= self.recovery_cooldown_ms

    # ========================================================
    # ACTIONS
    # ========================================================

    def _evaluate_health(self) -> Optional[Any]:
        if self.health_manager is None:
            return None

        if hasattr(self.health_manager, "evaluate"):
            return self.health_manager.evaluate()

        return None

    def _audit_policy(self) -> List[Dict[str, Any]]:
        if self.policy_manager is None:
            return []

        if not hasattr(self.policy_manager, "audit_runtime"):
            return []

        audit = self.policy_manager.audit_runtime()

        findings: List[Dict[str, Any]] = []

        if not audit.get("ok", True):
            findings.append({
                "type": "RUNTIME_POLICY_VIOLATIONS",
                "audit": audit,
            })

        return findings

    def _validate_topology(self) -> List[Dict[str, Any]]:
        if self.dependency_graph is None:
            return []

        if not hasattr(self.dependency_graph, "validate"):
            return []

        validation = self.dependency_graph.validate()

        findings: List[Dict[str, Any]] = []

        if validation.get("cycles"):
            findings.append({
                "type": "RUNTIME_DEPENDENCY_CYCLE",
                "cycles": validation.get("cycles"),
            })

        if validation.get("missing_dependencies"):
            findings.append({
                "type": "RUNTIME_MISSING_DEPENDENCIES",
                "missing_dependencies": validation.get("missing_dependencies"),
            })

        return findings

    def _trigger_backpressure(
        self,
        *,
        tenant_id: str,
        reason: str,
    ) -> tuple[bool, Dict[str, Any]]:
        if self.backpressure_controller is None:
            return False, {
                "action": "BACKPRESSURE_UNAVAILABLE",
                "ok": False,
            }

        try:
            decision = self.backpressure_controller.evaluate(
                tenant_id=tenant_id,
                context={
                    "source": "autonomous_runtime_supervisor",
                    "reason": reason,
                },
            )

            if getattr(decision, "freeze_tenant", False):
                self.backpressure_controller.enforce_freeze_if_needed(decision)

            return True, {
                "action": "BACKPRESSURE_EVALUATED",
                "ok": True,
                "decision": (
                    decision.to_dict()
                    if hasattr(decision, "to_dict")
                    else {}
                ),
            }

        except Exception as exc:
            return False, {
                "action": "BACKPRESSURE_FAILED",
                "ok": False,
                "error": str(exc),
            }

    def _run_watchdog(self) -> tuple[bool, Dict[str, Any]]:
        if self.watchdog is None:
            return False, {
                "action": "WATCHDOG_UNAVAILABLE",
                "ok": False,
            }

        try:
            result = self.watchdog.run_cycle()

            return True, {
                "action": "WATCHDOG_RUN",
                "ok": True,
                "result": result,
            }

        except Exception as exc:
            return False, {
                "action": "WATCHDOG_FAILED",
                "ok": False,
                "error": str(exc),
            }

    def _trigger_recovery(
        self,
        *,
        tenant_id: str,
        force: bool = False,
    ) -> tuple[bool, Dict[str, Any]]:
        if self.recovery_manager is None:
            return False, {
                "action": "RECOVERY_UNAVAILABLE",
                "ok": False,
            }

        try:
            result = self.recovery_manager.auto_recover(
                tenant_id=tenant_id,
                actor="autonomous_runtime_supervisor",
                force=force,
            )

            return bool(result.ok), {
                "action": "AUTO_RECOVERY",
                "ok": bool(result.ok),
                "result": (
                    result.to_dict()
                    if hasattr(result, "to_dict")
                    else {}
                ),
            }

        except Exception as exc:
            return False, {
                "action": "RECOVERY_FAILED",
                "ok": False,
                "error": str(exc),
            }

    # ========================================================
    # EVENTS / READS
    # ========================================================

    def _record_event(
        self,
        *,
        event_type: str,
        severity: str,
        message: str,
        tenant_id: str = DEFAULT_TENANT,
        runtime_mode: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RuntimeSupervisorEvent:
        event = RuntimeSupervisorEvent(
            event_id=f"ARSE-{uuid.uuid4().hex[:12].upper()}",
            event_type=event_type,
            severity=severity,
            message=message,
            tenant_id=tenant_id,
            runtime_mode=runtime_mode or self.runtime_mode,
            metadata=metadata or {},
        )

        with self._lock:
            self._events.append(event)
            self._events = self._events[-500:]

        self._emit(
            event_type,
            event.to_dict(),
        )

        return event

    def status_snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "status": self.status,
                "runtime_mode": self.runtime_mode,
                "tenant_id": self.tenant_id,
                "last_cycle_ms": self.last_cycle_ms,
                "last_recovery_ms": self.last_recovery_ms,
                "cycle_count": self.cycle_count,
                "recovery_count": self.recovery_count,
                "error_count": self.error_count,
                "recovery_cooldown_ms": self.recovery_cooldown_ms,
            }

    def list_events(
        self,
        *,
        limit: int = 250,
    ) -> List[Dict[str, Any]]:
        with self._lock:
            events = sorted(
                self._events,
                key=lambda e: e.created_at_ms,
                reverse=True,
            )

        return [
            e.to_dict()
            for e in events[:limit]
        ]

    def list_cycles(
        self,
        *,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        with self._lock:
            cycles = sorted(
                self._cycles,
                key=lambda c: c.created_at_ms,
                reverse=True,
            )

        return [
            c.to_dict()
            for c in cycles[:limit]
        ]

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
                source="autonomous_runtime_supervisor",
                severity=payload.get("severity") or "INFO",
                payload=payload,
            )
        except TypeError:
            try:
                self.event_bus.publish(
                    event_type=event_type,
                    payload=payload,
                )
            except Exception:
                pass
        except Exception:
            pass


_DEFAULT_AUTONOMOUS_RUNTIME_SUPERVISOR: Optional[
    AutonomousRuntimeSupervisor
] = None


def get_autonomous_runtime_supervisor(
    *,
    registry: Any = None,
    lifecycle: Any = None,
    health_manager: Any = None,
    dependency_graph: Any = None,
    policy_manager: Any = None,
    recovery_manager: Any = None,
    backpressure_controller: Any = None,
    watchdog: Any = None,
    storage: Any = None,
    event_bus: Any = None,
    tenant_id: str = DEFAULT_TENANT,
    recovery_cooldown_ms: int = 300_000,
    reset: bool = False,
) -> AutonomousRuntimeSupervisor:
    global _DEFAULT_AUTONOMOUS_RUNTIME_SUPERVISOR

    if reset or _DEFAULT_AUTONOMOUS_RUNTIME_SUPERVISOR is None:
        _DEFAULT_AUTONOMOUS_RUNTIME_SUPERVISOR = AutonomousRuntimeSupervisor(
            registry=registry,
            lifecycle=lifecycle,
            health_manager=health_manager,
            dependency_graph=dependency_graph,
            policy_manager=policy_manager,
            recovery_manager=recovery_manager,
            backpressure_controller=backpressure_controller,
            watchdog=watchdog,
            storage=storage,
            event_bus=event_bus,
            tenant_id=tenant_id,
            recovery_cooldown_ms=recovery_cooldown_ms,
        )

    return _DEFAULT_AUTONOMOUS_RUNTIME_SUPERVISOR