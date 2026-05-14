"""
core/runtime/runtime_recovery_manager.py

Runtime Recovery Manager.

Purpose:
- autonomous runtime stabilization
- dependency-aware recovery
- service restart orchestration
- quarantine handling
- backpressure integration
- safe recovery planning
- recovery audit trail

Architecture Rules:
- no shared sqlite connection
- no UI state dependency
- no hidden runtime mutation
- all service access through registry/lifecycle/storage boundaries
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


RECOVERY_PENDING = "PENDING"
RECOVERY_PLANNED = "PLANNED"
RECOVERY_RUNNING = "RUNNING"
RECOVERY_COMPLETED = "COMPLETED"
RECOVERY_FAILED = "FAILED"
RECOVERY_BLOCKED = "BLOCKED"

ACTION_RESTART_SERVICE = "RESTART_SERVICE"
ACTION_QUARANTINE_SERVICE = "QUARANTINE_SERVICE"
ACTION_CLEAR_QUARANTINE = "CLEAR_QUARANTINE"
ACTION_ENABLE_BACKPRESSURE = "ENABLE_BACKPRESSURE"
ACTION_RUN_WATCHDOG = "RUN_WATCHDOG"
ACTION_RECOVER_LEASES = "RECOVER_LEASES"
ACTION_MARK_DEGRADED = "MARK_DEGRADED"
ACTION_AUDIT_POLICY = "AUDIT_POLICY"

MODE_PERMISSIVE = "PERMISSIVE"
MODE_CONSERVATIVE = "CONSERVATIVE"
MODE_GOVCLOUD = "GOVCLOUD"
MODE_MANUAL_APPROVAL = "MANUAL_APPROVAL"

DEFAULT_TENANT = "default"


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class RuntimeRecoveryAction:
    action_id: str
    action_type: str
    service_name: Optional[str] = None
    tenant_id: str = DEFAULT_TENANT
    reason: str = ""
    requires_approval: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: str = RECOVERY_PENDING
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RuntimeRecoveryPlan:
    plan_id: str
    tenant_id: str = DEFAULT_TENANT
    status: str = RECOVERY_PLANNED
    risk: str = "LOW"
    reason: str = ""
    actions: List[RuntimeRecoveryAction] = field(default_factory=list)
    findings: List[Dict[str, Any]] = field(default_factory=list)
    created_by: str = "runtime_recovery_manager"
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["actions"] = [
            a.to_dict()
            if hasattr(a, "to_dict")
            else a
            for a in self.actions
        ]
        return data


@dataclass
class RuntimeRecoveryResult:
    plan_id: str
    ok: bool
    status: str
    message: str
    executed_actions: List[Dict[str, Any]] = field(default_factory=list)
    failed_actions: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    completed_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RuntimeRecoveryManager:
    def __init__(
        self,
        *,
        registry: Any,
        lifecycle: Any = None,
        health_manager: Any = None,
        dependency_graph: Any = None,
        policy_manager: Any = None,
        storage: Any = None,
        event_bus: Any = None,
        recovery_mode: str = MODE_CONSERVATIVE,
    ) -> None:
        self.registry = registry
        self.lifecycle = lifecycle
        self.health_manager = health_manager
        self.dependency_graph = dependency_graph
        self.policy_manager = policy_manager
        self.storage = storage
        self.event_bus = event_bus or getattr(storage, "event_bus", None)
        self.recovery_mode = recovery_mode

        self._plans: Dict[str, RuntimeRecoveryPlan] = {}
        self._results: List[RuntimeRecoveryResult] = []

    # ========================================================
    # PLAN CREATION
    # ========================================================

    def create_recovery_plan(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        reason: str = "runtime_health_degradation",
        created_by: str = "runtime_recovery_manager",
    ) -> RuntimeRecoveryPlan:
        plan_id = f"RECOVERY-{uuid.uuid4().hex[:12].upper()}"

        findings: List[Dict[str, Any]] = []
        actions: List[RuntimeRecoveryAction] = []

        snapshot = None

        if self.health_manager is not None:
            try:
                snapshot = self.health_manager.evaluate()
                findings.extend(getattr(snapshot, "findings", []) or [])
            except Exception as exc:
                findings.append({
                    "type": "HEALTH_EVALUATION_FAILED",
                    "error": str(exc),
                })

        # ----------------------------------------------------
        # Translate health findings into recovery actions
        # ----------------------------------------------------

        for finding in findings:
            ftype = str(finding.get("type") or "")

            service = (
                finding.get("service")
                or finding.get("service_name")
            )

            if ftype in {
                "SERVICE_UNAVAILABLE",
                "SERVICE_DEGRADED",
            } and service:
                actions.append(
                    self._action(
                        ACTION_RESTART_SERVICE,
                        service_name=service,
                        tenant_id=tenant_id,
                        reason=f"{ftype}: restart recommended",
                    )
                )

            if ftype == "SERVICE_QUARANTINED" and service:
                actions.append(
                    self._action(
                        ACTION_MARK_DEGRADED,
                        service_name=service,
                        tenant_id=tenant_id,
                        reason="Service quarantined; mark dependent runtime degraded.",
                    )
                )

            if ftype in {
                "QUEUE_DEPTH_HIGH",
                "RETRY_STORM",
                "DEAD_LETTER_SPIKE",
            }:
                actions.append(
                    self._action(
                        ACTION_ENABLE_BACKPRESSURE,
                        tenant_id=tenant_id,
                        reason=f"{ftype}: enable/runtime throttle.",
                    )
                )

            if ftype in {
                "RETRY_STORM",
                "DEAD_LETTER_SPIKE",
            }:
                actions.append(
                    self._action(
                        ACTION_RUN_WATCHDOG,
                        tenant_id=tenant_id,
                        reason=f"{ftype}: watchdog recovery recommended.",
                    )
                )

            if ftype == "RUNTIME_POLICY_VIOLATIONS":
                actions.append(
                    self._action(
                        ACTION_AUDIT_POLICY,
                        tenant_id=tenant_id,
                        reason="Runtime policy violations detected.",
                    )
                )

            if ftype == "WORKER_POOL_DEGRADED":
                actions.append(
                    self._action(
                        ACTION_RUN_WATCHDOG,
                        tenant_id=tenant_id,
                        reason="Worker pool degraded.",
                    )
                )

        # ----------------------------------------------------
        # Dependency-aware expansion
        # ----------------------------------------------------

        actions = self._expand_actions_with_dependency_context(
            actions
        )

        # ----------------------------------------------------
        # Recovery mode safety controls
        # ----------------------------------------------------

        risk = self._derive_plan_risk(actions, findings)

        if self.recovery_mode in {
            MODE_GOVCLOUD,
            MODE_MANUAL_APPROVAL,
        }:
            for action in actions:
                if action.action_type in {
                    ACTION_RESTART_SERVICE,
                    ACTION_CLEAR_QUARANTINE,
                    ACTION_QUARANTINE_SERVICE,
                }:
                    action.requires_approval = True

        if self.recovery_mode == MODE_CONSERVATIVE:
            for action in actions:
                if action.action_type == ACTION_CLEAR_QUARANTINE:
                    action.requires_approval = True

        plan = RuntimeRecoveryPlan(
            plan_id=plan_id,
            tenant_id=tenant_id,
            status=RECOVERY_PLANNED,
            risk=risk,
            reason=reason,
            actions=actions,
            findings=findings,
            created_by=created_by,
        )

        self._plans[plan_id] = plan

        self._emit(
            "RUNTIME_RECOVERY_PLAN_CREATED",
            plan.to_dict(),
        )

        return plan

    # ========================================================
    # EXECUTION
    # ========================================================

    def execute_plan(
        self,
        plan_id: str,
        *,
        actor: str = "runtime_recovery_manager",
        force: bool = False,
    ) -> RuntimeRecoveryResult:
        plan = self._plans.get(plan_id)

        if plan is None:
            return RuntimeRecoveryResult(
                plan_id=plan_id,
                ok=False,
                status=RECOVERY_FAILED,
                message="Recovery plan not found.",
            )

        if any(a.requires_approval for a in plan.actions) and not force:
            result = RuntimeRecoveryResult(
                plan_id=plan_id,
                ok=False,
                status=RECOVERY_BLOCKED,
                message="Recovery plan requires approval.",
                metadata={
                    "requires_approval": True,
                    "actions": [
                        a.to_dict()
                        for a in plan.actions
                        if a.requires_approval
                    ],
                },
            )
            self._results.append(result)
            return result

        plan.status = RECOVERY_RUNNING

        executed: List[Dict[str, Any]] = []
        failed: List[Dict[str, Any]] = []

        self._emit(
            "RUNTIME_RECOVERY_STARTED",
            {
                "plan_id": plan_id,
                "actor": actor,
                "force": force,
            },
        )

        for action in plan.actions:
            try:
                ok, message, metadata = self._execute_action(
                    action,
                    actor=actor,
                    force=force,
                )

                action.status = (
                    RECOVERY_COMPLETED
                    if ok
                    else RECOVERY_FAILED
                )

                action_result = {
                    **action.to_dict(),
                    "ok": ok,
                    "message": message,
                    "metadata": metadata,
                }

                if ok:
                    executed.append(action_result)
                else:
                    failed.append(action_result)

            except Exception as exc:
                action.status = RECOVERY_FAILED
                failed.append({
                    **action.to_dict(),
                    "ok": False,
                    "message": str(exc),
                })

        ok = len(failed) == 0

        plan.status = (
            RECOVERY_COMPLETED
            if ok
            else RECOVERY_FAILED
        )

        result = RuntimeRecoveryResult(
            plan_id=plan_id,
            ok=ok,
            status=plan.status,
            message=(
                "Recovery plan completed."
                if ok
                else "Recovery plan completed with failures."
            ),
            executed_actions=executed,
            failed_actions=failed,
        )

        self._results.append(result)

        self._emit(
            "RUNTIME_RECOVERY_COMPLETED",
            result.to_dict(),
        )

        return result

    def auto_recover(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        actor: str = "runtime_recovery_manager",
        force: bool = False,
    ) -> RuntimeRecoveryResult:
        plan = self.create_recovery_plan(
            tenant_id=tenant_id,
            reason="auto_recover_requested",
            created_by=actor,
        )

        if not plan.actions:
            result = RuntimeRecoveryResult(
                plan_id=plan.plan_id,
                ok=True,
                status=RECOVERY_COMPLETED,
                message="No recovery actions required.",
            )
            self._results.append(result)
            return result

        return self.execute_plan(
            plan.plan_id,
            actor=actor,
            force=force,
        )

    # ========================================================
    # ACTION EXECUTION
    # ========================================================

    def _execute_action(
        self,
        action: RuntimeRecoveryAction,
        *,
        actor: str,
        force: bool,
    ) -> tuple[bool, str, Dict[str, Any]]:
        if action.action_type == ACTION_RESTART_SERVICE:
            return self._restart_service(action, actor=actor, force=force)

        if action.action_type == ACTION_QUARANTINE_SERVICE:
            return self._quarantine_service(action)

        if action.action_type == ACTION_CLEAR_QUARANTINE:
            return self._clear_quarantine(action)

        if action.action_type == ACTION_ENABLE_BACKPRESSURE:
            return self._enable_backpressure(action)

        if action.action_type == ACTION_RUN_WATCHDOG:
            return self._run_watchdog(action)

        if action.action_type == ACTION_RECOVER_LEASES:
            return self._recover_leases(action)

        if action.action_type == ACTION_MARK_DEGRADED:
            return self._mark_degraded(action)

        if action.action_type == ACTION_AUDIT_POLICY:
            return self._audit_policy(action)

        return (
            False,
            f"Unknown recovery action: {action.action_type}",
            {},
        )

    def _restart_service(
        self,
        action: RuntimeRecoveryAction,
        *,
        actor: str,
        force: bool,
    ) -> tuple[bool, str, Dict[str, Any]]:
        if self.lifecycle is None:
            return False, "Lifecycle manager unavailable.", {}

        if not action.service_name:
            return False, "Missing service_name.", {}

        impact = self._safe_restart_impact(
            action.service_name
        )

        if (
            not force
            and impact.get("risk") in {"HIGH", "CRITICAL"}
        ):
            return (
                False,
                "Restart blocked due to high dependency impact.",
                {"impact": impact},
            )

        result = self.lifecycle.restart_service(
            action.service_name,
            restarted_by=actor,
            force=force,
        )

        return (
            bool(result.ok),
            result.message,
            {
                "impact": impact,
                "result": (
                    result.to_dict()
                    if hasattr(result, "to_dict")
                    else {}
                ),
            },
        )

    def _quarantine_service(
        self,
        action: RuntimeRecoveryAction,
    ) -> tuple[bool, str, Dict[str, Any]]:
        if self.policy_manager is not None:
            result = self.policy_manager.quarantine_service(
                action.service_name,
                reason=action.reason,
            )
            return bool(result.get("ok")), "Service quarantined.", result

        if self.registry is not None:
            ok = self.registry.quarantine(
                action.service_name,
                reason=action.reason,
            )
            return bool(ok), "Service quarantined.", {}

        return False, "No quarantine mechanism available.", {}

    def _clear_quarantine(
        self,
        action: RuntimeRecoveryAction,
    ) -> tuple[bool, str, Dict[str, Any]]:
        if self.policy_manager is not None:
            result = self.policy_manager.clear_quarantine(
                action.service_name
            )
            return bool(result.get("ok")), "Quarantine cleared.", result

        if self.registry is not None:
            ok = self.registry.clear_quarantine(
                action.service_name
            )
            return bool(ok), "Quarantine cleared.", {}

        return False, "No restore mechanism available.", {}

    def _enable_backpressure(
        self,
        action: RuntimeRecoveryAction,
    ) -> tuple[bool, str, Dict[str, Any]]:
        controller = getattr(
            self.storage,
            "backpressure_controller",
            None,
        )

        if controller is None:
            return False, "Backpressure controller unavailable.", {}

        try:
            decision = controller.evaluate(
                tenant_id=action.tenant_id,
                context={
                    "source": "runtime_recovery_manager",
                    "reason": action.reason,
                },
            )

            if getattr(decision, "freeze_tenant", False):
                controller.enforce_freeze_if_needed(decision)

            return (
                True,
                "Backpressure evaluated/enforced.",
                {
                    "decision": (
                        decision.to_dict()
                        if hasattr(decision, "to_dict")
                        else {}
                    )
                },
            )

        except Exception as exc:
            return False, str(exc), {}

    def _run_watchdog(
        self,
        action: RuntimeRecoveryAction,
    ) -> tuple[bool, str, Dict[str, Any]]:
        watchdog = getattr(
            self.storage,
            "lease_watchdog",
            None,
        )

        if watchdog is None:
            return False, "Lease watchdog unavailable.", {}

        result = watchdog.run_cycle()

        return True, "Watchdog recovery cycle completed.", result

    def _recover_leases(
        self,
        action: RuntimeRecoveryAction,
    ) -> tuple[bool, str, Dict[str, Any]]:
        queue = getattr(
            self.storage,
            "execution_queue",
            None,
        )

        if queue is None:
            return False, "Execution queue unavailable.", {}

        recovered = queue.requeue_expired_leases()

        return (
            True,
            f"Recovered {recovered} expired leases.",
            {"recovered": recovered},
        )

    def _mark_degraded(
        self,
        action: RuntimeRecoveryAction,
    ) -> tuple[bool, str, Dict[str, Any]]:
        if self.lifecycle is None:
            return False, "Lifecycle manager unavailable.", {}

        if not action.service_name:
            return False, "Missing service_name.", {}

        ok = self.lifecycle.mark_degraded(
            action.service_name,
            reason=action.reason,
        )

        return bool(ok), "Service marked degraded.", {}

    def _audit_policy(
        self,
        action: RuntimeRecoveryAction,
    ) -> tuple[bool, str, Dict[str, Any]]:
        if self.policy_manager is None:
            return False, "Policy manager unavailable.", {}

        audit = self.policy_manager.audit_runtime()

        return True, "Runtime policy audit completed.", audit

    # ========================================================
    # DEPENDENCY CONTEXT
    # ========================================================

    def _expand_actions_with_dependency_context(
        self,
        actions: List[RuntimeRecoveryAction],
    ) -> List[RuntimeRecoveryAction]:
        if self.dependency_graph is None:
            return actions

        expanded: List[RuntimeRecoveryAction] = []

        seen = set()

        for action in actions:
            key = (
                action.action_type,
                action.service_name,
                action.reason,
            )

            if key not in seen:
                expanded.append(action)
                seen.add(key)

            if (
                action.action_type
                == ACTION_RESTART_SERVICE
                and action.service_name
            ):
                impact = self._safe_restart_impact(
                    action.service_name
                )

                if impact.get("risk") in {"HIGH", "CRITICAL"}:
                    degraded_action = self._action(
                        ACTION_MARK_DEGRADED,
                        service_name=action.service_name,
                        tenant_id=action.tenant_id,
                        reason=(
                            "High restart impact detected; "
                            "marking service degraded before recovery."
                        ),
                    )
                    k2 = (
                        degraded_action.action_type,
                        degraded_action.service_name,
                        degraded_action.reason,
                    )
                    if k2 not in seen:
                        expanded.insert(
                            max(len(expanded) - 1, 0),
                            degraded_action,
                        )
                        seen.add(k2)

        return expanded

    def _safe_restart_impact(
        self,
        service_name: str,
    ) -> Dict[str, Any]:
        if self.dependency_graph is None:
            return {
                "risk": "UNKNOWN",
                "service_name": service_name,
            }

        try:
            return self.dependency_graph.restart_impact(
                service_name
            )
        except Exception as exc:
            return {
                "risk": "UNKNOWN",
                "service_name": service_name,
                "error": str(exc),
            }

    def _derive_plan_risk(
        self,
        actions: List[RuntimeRecoveryAction],
        findings: List[Dict[str, Any]],
    ) -> str:
        score = 0

        for action in actions:
            if action.action_type == ACTION_RESTART_SERVICE:
                score += 20
            elif action.action_type == ACTION_QUARANTINE_SERVICE:
                score += 25
            elif action.action_type == ACTION_ENABLE_BACKPRESSURE:
                score += 10
            elif action.action_type == ACTION_RUN_WATCHDOG:
                score += 10

        for finding in findings:
            ftype = finding.get("type")
            if ftype in {
                "SERVICE_QUARANTINED",
                "WORKER_POOL_DEGRADED",
            }:
                score += 20
            elif ftype in {
                "RETRY_STORM",
                "DEAD_LETTER_SPIKE",
            }:
                score += 15
            elif ftype in {
                "RUNTIME_POLICY_VIOLATIONS",
            }:
                score += 15

        if score >= 75:
            return "CRITICAL"
        if score >= 50:
            return "HIGH"
        if score >= 25:
            return "MEDIUM"
        return "LOW"

    def _action(
        self,
        action_type: str,
        *,
        service_name: Optional[str] = None,
        tenant_id: str = DEFAULT_TENANT,
        reason: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RuntimeRecoveryAction:
        return RuntimeRecoveryAction(
            action_id=f"RA-{uuid.uuid4().hex[:12].upper()}",
            action_type=action_type,
            service_name=service_name,
            tenant_id=tenant_id,
            reason=reason,
            metadata=metadata or {},
        )

    # ========================================================
    # READS
    # ========================================================

    def get_plan(
        self,
        plan_id: str,
    ) -> Optional[Dict[str, Any]]:
        plan = self._plans.get(plan_id)
        return plan.to_dict() if plan else None

    def list_plans(
        self,
        *,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        plans = sorted(
            self._plans.values(),
            key=lambda p: p.created_at_ms,
            reverse=True,
        )

        return [
            p.to_dict()
            for p in plans[:limit]
        ]

    def list_results(
        self,
        *,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        results = sorted(
            self._results,
            key=lambda r: r.completed_at_ms,
            reverse=True,
        )

        return [
            r.to_dict()
            for r in results[:limit]
        ]

    # ========================================================
    # EVENTS
    # ========================================================

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
                source="runtime_recovery_manager",
                severity=payload.get("risk") or "INFO",
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


_DEFAULT_RUNTIME_RECOVERY_MANAGER: Optional[
    RuntimeRecoveryManager
] = None


def get_runtime_recovery_manager(
    *,
    registry: Any,
    lifecycle: Any = None,
    health_manager: Any = None,
    dependency_graph: Any = None,
    policy_manager: Any = None,
    storage: Any = None,
    event_bus: Any = None,
    recovery_mode: str = MODE_CONSERVATIVE,
    reset: bool = False,
) -> RuntimeRecoveryManager:
    global _DEFAULT_RUNTIME_RECOVERY_MANAGER

    if reset or _DEFAULT_RUNTIME_RECOVERY_MANAGER is None:
        _DEFAULT_RUNTIME_RECOVERY_MANAGER = RuntimeRecoveryManager(
            registry=registry,
            lifecycle=lifecycle,
            health_manager=health_manager,
            dependency_graph=dependency_graph,
            policy_manager=policy_manager,
            storage=storage,
            event_bus=event_bus,
            recovery_mode=recovery_mode,
        )

    return _DEFAULT_RUNTIME_RECOVERY_MANAGER