"""
core/runtime/sovereign_execution_controller.py

Sovereign Execution Controller.

Purpose:
- enforce execution-domain decisions before runtime execution
- combine domain policy + federation placement + runtime governance
- block illegal execution paths
- support GovCloud / export-controlled / classified / air-gapped routing
- provide sovereign execution audit decisions
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


DECISION_ALLOWED = "ALLOWED"
DECISION_BLOCKED = "BLOCKED"
DECISION_REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
DECISION_REROUTE = "REROUTE"
DECISION_QUARANTINE = "QUARANTINE"

SOVEREIGN_MODE_PERMISSIVE = "PERMISSIVE"
SOVEREIGN_MODE_ENFORCING = "ENFORCING"
SOVEREIGN_MODE_GOVCLOUD = "GOVCLOUD"
SOVEREIGN_MODE_LOCKDOWN = "LOCKDOWN"

DEFAULT_TENANT = "default"


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class SovereignExecutionDecision:
    decision_id: str
    tenant_id: str
    allowed: bool
    decision: str
    reason: str
    sensitivity: str = "INTERNAL"
    capability: Optional[str] = None
    selected_domain_id: Optional[str] = None
    selected_runtime_id: Optional[str] = None
    requires_approval: bool = False
    blocked_reasons: List[str] = field(default_factory=list)
    domain_decision: Dict[str, Any] = field(default_factory=dict)
    federation_decision: Dict[str, Any] = field(default_factory=dict)
    workload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SovereignExecutionController:
    def __init__(
        self,
        *,
        domain_manager: Any = None,
        federation_manager: Any = None,
        policy_manager: Any = None,
        supervisor: Any = None,
        registry: Any = None,
        storage: Any = None,
        event_bus: Any = None,
        sovereign_mode: str = SOVEREIGN_MODE_ENFORCING,
    ) -> None:
        self.storage = storage
        self.domain_manager = (
            domain_manager
            or getattr(storage, "execution_domain_manager", None)
        )
        self.federation_manager = (
            federation_manager
            or getattr(storage, "runtime_federation_manager", None)
        )
        self.policy_manager = (
            policy_manager
            or getattr(storage, "runtime_policy_manager", None)
        )
        self.supervisor = (
            supervisor
            or getattr(storage, "autonomous_runtime_supervisor", None)
        )
        self.registry = (
            registry
            or getattr(storage, "runtime_service_registry", None)
        )
        self.event_bus = event_bus or getattr(storage, "event_bus", None)
        self.sovereign_mode = sovereign_mode

        self._decisions: List[SovereignExecutionDecision] = []

    # ========================================================
    # MAIN ENFORCEMENT
    # ========================================================

    def authorize_execution(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        workload: Optional[Dict[str, Any]] = None,
        capability: Optional[str] = None,
        target_domain_id: Optional[str] = None,
        target_runtime_id: Optional[str] = None,
        require_govcloud: bool = False,
        require_high_trust: bool = False,
        allow_degraded_runtime: bool = False,
        actor: str = "sovereign_execution_controller",
    ) -> SovereignExecutionDecision:
        workload = workload or {}

        if self.sovereign_mode == SOVEREIGN_MODE_LOCKDOWN:
            return self._record_decision(
                SovereignExecutionDecision(
                    decision_id=self._new_decision_id(),
                    tenant_id=tenant_id,
                    allowed=False,
                    decision=DECISION_BLOCKED,
                    reason="Sovereign execution controller is in LOCKDOWN mode.",
                    capability=capability,
                    workload=workload,
                    metadata={"actor": actor, "mode": self.sovereign_mode},
                )
            )

        domain_decision = self._evaluate_domain(
            tenant_id=tenant_id,
            workload=workload,
            capability=capability,
            target_domain_id=target_domain_id,
            require_govcloud=require_govcloud,
        )

        if not domain_decision.get("allowed", False):
            if domain_decision.get("decision") == DECISION_REQUIRES_APPROVAL:
                return self._record_decision(
                    SovereignExecutionDecision(
                        decision_id=self._new_decision_id(),
                        tenant_id=tenant_id,
                        allowed=False,
                        decision=DECISION_REQUIRES_APPROVAL,
                        reason="Execution requires domain approval.",
                        sensitivity=domain_decision.get("sensitivity", "INTERNAL"),
                        capability=capability,
                        selected_domain_id=domain_decision.get("domain_id"),
                        requires_approval=True,
                        blocked_reasons=domain_decision.get("blocked_reasons", []),
                        domain_decision=domain_decision,
                        workload=workload,
                        metadata={"actor": actor, "mode": self.sovereign_mode},
                    )
                )

            return self._record_decision(
                SovereignExecutionDecision(
                    decision_id=self._new_decision_id(),
                    tenant_id=tenant_id,
                    allowed=False,
                    decision=DECISION_BLOCKED,
                    reason=domain_decision.get(
                        "reason",
                        "Execution domain policy blocked workload.",
                    ),
                    sensitivity=domain_decision.get("sensitivity", "INTERNAL"),
                    capability=capability,
                    selected_domain_id=domain_decision.get("domain_id"),
                    blocked_reasons=domain_decision.get("blocked_reasons", []),
                    domain_decision=domain_decision,
                    workload=workload,
                    metadata={"actor": actor, "mode": self.sovereign_mode},
                )
            )

        federation_decision = self._evaluate_federation(
            tenant_id=tenant_id,
            capability=capability,
            require_govcloud=require_govcloud,
            require_high_trust=require_high_trust,
            allow_degraded_runtime=allow_degraded_runtime,
            target_runtime_id=target_runtime_id,
        )

        if not federation_decision.get("allowed", True):
            return self._record_decision(
                SovereignExecutionDecision(
                    decision_id=self._new_decision_id(),
                    tenant_id=tenant_id,
                    allowed=False,
                    decision=DECISION_BLOCKED,
                    reason=federation_decision.get(
                        "reason",
                        "Federation placement blocked execution.",
                    ),
                    sensitivity=domain_decision.get("sensitivity", "INTERNAL"),
                    capability=capability,
                    selected_domain_id=domain_decision.get("domain_id"),
                    blocked_reasons=(
                        domain_decision.get("blocked_reasons", [])
                        + federation_decision.get("blocked_runtime_ids", [])
                    ),
                    domain_decision=domain_decision,
                    federation_decision=federation_decision,
                    workload=workload,
                    metadata={"actor": actor, "mode": self.sovereign_mode},
                )
            )

        selected_runtime_id = (
            target_runtime_id
            or federation_decision.get("selected_runtime_id")
        )

        decision = SovereignExecutionDecision(
            decision_id=self._new_decision_id(),
            tenant_id=tenant_id,
            allowed=True,
            decision=DECISION_ALLOWED,
            reason="Sovereign execution authorized.",
            sensitivity=domain_decision.get("sensitivity", "INTERNAL"),
            capability=capability,
            selected_domain_id=domain_decision.get("domain_id"),
            selected_runtime_id=selected_runtime_id,
            requires_approval=False,
            domain_decision=domain_decision,
            federation_decision=federation_decision,
            workload=workload,
            metadata={
                "actor": actor,
                "mode": self.sovereign_mode,
                "require_govcloud": require_govcloud,
                "require_high_trust": require_high_trust,
            },
        )

        return self._record_decision(decision)

    # ========================================================
    # ROUTING GUARD
    # ========================================================

    def guard_route(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        workload: Optional[Dict[str, Any]] = None,
        capability: Optional[str] = None,
        action: Optional[str] = None,
        agent_name: Optional[str] = None,
        target_domain_id: Optional[str] = None,
        target_runtime_id: Optional[str] = None,
    ) -> SovereignExecutionDecision:
        payload = dict(workload or {})

        if action:
            payload.setdefault("action", action)

        if agent_name:
            payload.setdefault("agent_name", agent_name)

        require_govcloud = bool(
            payload.get("requires_govcloud")
            or payload.get("govcloud_required")
        )

        require_high_trust = bool(
            payload.get("requires_high_trust")
            or payload.get("high_trust_required")
        )

        return self.authorize_execution(
            tenant_id=tenant_id,
            workload=payload,
            capability=capability or payload.get("capability"),
            target_domain_id=target_domain_id,
            target_runtime_id=target_runtime_id,
            require_govcloud=require_govcloud,
            require_high_trust=require_high_trust,
            actor="route_guard",
        )

    # ========================================================
    # DOMAIN + FEDERATION EVALUATION
    # ========================================================

    def _evaluate_domain(
        self,
        *,
        tenant_id: str,
        workload: Dict[str, Any],
        capability: Optional[str],
        target_domain_id: Optional[str],
        require_govcloud: bool,
    ) -> Dict[str, Any]:
        if self.domain_manager is None:
            if self.sovereign_mode in {
                SOVEREIGN_MODE_GOVCLOUD,
                SOVEREIGN_MODE_ENFORCING,
            }:
                return {
                    "allowed": False,
                    "decision": DECISION_BLOCKED,
                    "reason": "Execution domain manager unavailable.",
                    "sensitivity": "UNKNOWN",
                    "blocked_reasons": ["domain_manager_unavailable"],
                }

            return {
                "allowed": True,
                "decision": DECISION_ALLOWED,
                "reason": "Domain manager unavailable; permissive mode allowed.",
                "sensitivity": "UNKNOWN",
                "domain_id": None,
            }

        if require_govcloud:
            workload = {
                **workload,
                "requires_govcloud": True,
            }

        decision = self.domain_manager.validate_workload_execution(
            tenant_id=tenant_id,
            workload=workload,
            capability=capability,
            target_domain_id=target_domain_id,
        )

        return (
            decision.to_dict()
            if hasattr(decision, "to_dict")
            else dict(decision)
        )

    def _evaluate_federation(
        self,
        *,
        tenant_id: str,
        capability: Optional[str],
        require_govcloud: bool,
        require_high_trust: bool,
        allow_degraded_runtime: bool,
        target_runtime_id: Optional[str],
    ) -> Dict[str, Any]:
        if target_runtime_id:
            return {
                "allowed": True,
                "status": "TARGET_RUNTIME_REQUESTED",
                "reason": "Target runtime explicitly requested.",
                "selected_runtime_id": target_runtime_id,
            }

        if self.federation_manager is None:
            return {
                "allowed": True,
                "status": "LOCAL_RUNTIME",
                "reason": "Federation unavailable; local runtime assumed.",
                "selected_runtime_id": "local-runtime",
            }

        decision = self.federation_manager.choose_runtime(
            tenant_id=tenant_id,
            capability=capability,
            require_govcloud=require_govcloud,
            require_high_trust=require_high_trust,
            allow_degraded=allow_degraded_runtime,
        )

        return (
            decision.to_dict()
            if hasattr(decision, "to_dict")
            else dict(decision)
        )

    # ========================================================
    # DOMAIN CONTROL
    # ========================================================

    def freeze_domain(
        self,
        domain_id: str,
        *,
        reason: str,
    ) -> Dict[str, Any]:
        if self.domain_manager is None:
            return {"ok": False, "reason": "domain_manager_unavailable"}

        ok = self.domain_manager.freeze_domain(domain_id, reason=reason)

        self._emit(
            "SOVEREIGN_DOMAIN_FREEZE_REQUESTED",
            {
                "domain_id": domain_id,
                "reason": reason,
                "ok": ok,
            },
        )

        return {"ok": ok, "domain_id": domain_id, "reason": reason}

    def quarantine_domain(
        self,
        domain_id: str,
        *,
        reason: str,
    ) -> Dict[str, Any]:
        if self.domain_manager is None:
            return {"ok": False, "reason": "domain_manager_unavailable"}

        ok = self.domain_manager.quarantine_domain(domain_id, reason=reason)

        self._emit(
            "SOVEREIGN_DOMAIN_QUARANTINE_REQUESTED",
            {
                "domain_id": domain_id,
                "reason": reason,
                "ok": ok,
            },
        )

        return {"ok": ok, "domain_id": domain_id, "reason": reason}

    def restore_domain(
        self,
        domain_id: str,
    ) -> Dict[str, Any]:
        if self.domain_manager is None:
            return {"ok": False, "reason": "domain_manager_unavailable"}

        ok = self.domain_manager.restore_domain(domain_id)

        self._emit(
            "SOVEREIGN_DOMAIN_RESTORE_REQUESTED",
            {
                "domain_id": domain_id,
                "ok": ok,
            },
        )

        return {"ok": ok, "domain_id": domain_id}

    # ========================================================
    # READS
    # ========================================================

    def list_decisions(
        self,
        *,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        decisions = sorted(
            self._decisions,
            key=lambda d: d.created_at_ms,
            reverse=True,
        )

        return [
            d.to_dict()
            for d in decisions[:limit]
        ]

    def sovereignty_status(self) -> Dict[str, Any]:
        blocked = len([
            d for d in self._decisions
            if d.decision == DECISION_BLOCKED
        ])

        approvals = len([
            d for d in self._decisions
            if d.decision == DECISION_REQUIRES_APPROVAL
        ])

        allowed = len([
            d for d in self._decisions
            if d.allowed
        ])

        return {
            "sovereign_mode": self.sovereign_mode,
            "decision_count": len(self._decisions),
            "allowed": allowed,
            "blocked": blocked,
            "requires_approval": approvals,
        }

    # ========================================================
    # INTERNAL
    # ========================================================

    def _record_decision(
        self,
        decision: SovereignExecutionDecision,
    ) -> SovereignExecutionDecision:
        self._decisions.append(decision)
        self._decisions = self._decisions[-500:]

        self._emit(
            "SOVEREIGN_EXECUTION_DECISION",
            decision.to_dict(),
        )

        if (
            self.policy_manager is not None
            and not decision.allowed
            and hasattr(self.policy_manager, "_record")
        ):
            try:
                self.policy_manager._record(
                    event_type="SOVEREIGN_EXECUTION_BLOCKED",
                    severity="VIOLATION",
                    message=decision.reason,
                    source_service="sovereign_execution_controller",
                    tenant_id=decision.tenant_id,
                    metadata=decision.to_dict(),
                )
            except Exception:
                pass

        return decision

    def _new_decision_id(self) -> str:
        return f"SOVEREIGN-DECISION-{uuid.uuid4().hex[:12].upper()}"

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
                source="sovereign_execution_controller",
                severity=payload.get("decision") or "INFO",
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


_DEFAULT_SOVEREIGN_EXECUTION_CONTROLLER: Optional[
    SovereignExecutionController
] = None


def get_sovereign_execution_controller(
    *,
    domain_manager: Any = None,
    federation_manager: Any = None,
    policy_manager: Any = None,
    supervisor: Any = None,
    registry: Any = None,
    storage: Any = None,
    event_bus: Any = None,
    sovereign_mode: str = SOVEREIGN_MODE_ENFORCING,
    reset: bool = False,
) -> SovereignExecutionController:
    global _DEFAULT_SOVEREIGN_EXECUTION_CONTROLLER

    if reset or _DEFAULT_SOVEREIGN_EXECUTION_CONTROLLER is None:
        _DEFAULT_SOVEREIGN_EXECUTION_CONTROLLER = SovereignExecutionController(
            domain_manager=domain_manager,
            federation_manager=federation_manager,
            policy_manager=policy_manager,
            supervisor=supervisor,
            registry=registry,
            storage=storage,
            event_bus=event_bus,
            sovereign_mode=sovereign_mode,
        )

    return _DEFAULT_SOVEREIGN_EXECUTION_CONTROLLER