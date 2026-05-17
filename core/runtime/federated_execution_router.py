"""
core/runtime/federated_execution_router.py

Federated Execution Router.

Purpose:
- cross-runtime sovereign routing
- federation-aware placement
- sovereign execution authorization
- local/federated dispatch decisions
- failover planning
- runtime mesh routing foundation

Architecture Rules:
- no Streamlit/session_state dependency
- no persistent SQLite connection
- no hidden globals for state mutation
- explicit service-owned routing state
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


ROUTE_ALLOWED = "ALLOWED"
ROUTE_BLOCKED = "BLOCKED"
ROUTE_LOCAL = "LOCAL"
ROUTE_FEDERATED = "FEDERATED"
ROUTE_REQUIRES_APPROVAL = "REQUIRES_APPROVAL"
ROUTE_FAILOVER = "FAILOVER"
ROUTE_NO_RUNTIME = "NO_RUNTIME"

DEFAULT_TENANT = "default"


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class FederatedRouteDecision:
    decision_id: str
    tenant_id: str
    allowed: bool
    route_type: str
    reason: str
    capability: Optional[str] = None
    selected_runtime_id: Optional[str] = None
    selected_domain_id: Optional[str] = None
    local_dispatch: bool = False
    requires_approval: bool = False
    sovereign_decision: Dict[str, Any] = field(default_factory=dict)
    federation_decision: Dict[str, Any] = field(default_factory=dict)
    dispatch_result: Dict[str, Any] = field(default_factory=dict)
    workload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class FederatedExecutionRouter:
    def __init__(
        self,
        *,
        local_router: Any = None,
        federation_manager: Any = None,
        sovereign_controller: Any = None,
        domain_manager: Any = None,
        queue: Any = None,
        storage: Any = None,
        event_bus: Any = None,
        local_runtime_id: str = "local-runtime",
    ) -> None:
        self.storage = storage
        self.local_router = local_router or getattr(storage, "execution_router", None)
        self.federation_manager = federation_manager or getattr(storage, "runtime_federation_manager", None)
        self.sovereign_controller = sovereign_controller or getattr(storage, "sovereign_execution_controller", None)
        self.domain_manager = domain_manager or getattr(storage, "execution_domain_manager", None)
        self.queue = queue or getattr(storage, "execution_queue", None)
        self.event_bus = event_bus or getattr(storage, "event_bus", None)
        self.local_runtime_id = local_runtime_id

        self._decisions: List[FederatedRouteDecision] = []

    # ========================================================
    # MAIN ROUTING
    # ========================================================

    def route_workload(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        workload: Optional[Dict[str, Any]] = None,
        capability: Optional[str] = None,
        action: Optional[str] = None,
        agent_name: Optional[str] = None,
        require_govcloud: bool = False,
        require_high_trust: bool = False,
        allow_degraded_runtime: bool = False,
        prefer_local: bool = True,
        dispatch_local: bool = False,
    ) -> FederatedRouteDecision:
        workload = dict(workload or {})

        if action:
            workload.setdefault("action", action)

        if agent_name:
            workload.setdefault("agent_name", agent_name)

        capability = capability or workload.get("capability")

        sovereign = self._authorize(
            tenant_id=tenant_id,
            workload=workload,
            capability=capability,
            action=action,
            agent_name=agent_name,
            require_govcloud=require_govcloud,
            require_high_trust=require_high_trust,
            allow_degraded_runtime=allow_degraded_runtime,
        )

        if not sovereign.get("allowed", False):
            decision_type = ROUTE_BLOCKED

            if sovereign.get("decision") == "REQUIRES_APPROVAL":
                decision_type = ROUTE_REQUIRES_APPROVAL

            return self._record_decision(
                FederatedRouteDecision(
                    decision_id=self._new_decision_id(),
                    tenant_id=tenant_id,
                    allowed=False,
                    route_type=decision_type,
                    reason=sovereign.get("reason", "Sovereign authorization blocked route."),
                    capability=capability,
                    selected_domain_id=sovereign.get("selected_domain_id"),
                    requires_approval=bool(sovereign.get("requires_approval")),
                    sovereign_decision=sovereign,
                    workload=workload,
                )
            )

        selected_runtime_id = sovereign.get("selected_runtime_id")

        federation = self._choose_runtime(
            tenant_id=tenant_id,
            capability=capability,
            require_govcloud=require_govcloud,
            require_high_trust=require_high_trust,
            allow_degraded_runtime=allow_degraded_runtime,
        )

        if federation and not federation.get("allowed", True):
            return self._record_decision(
                FederatedRouteDecision(
                    decision_id=self._new_decision_id(),
                    tenant_id=tenant_id,
                    allowed=False,
                    route_type=ROUTE_NO_RUNTIME,
                    reason=federation.get("reason", "No eligible federated runtime."),
                    capability=capability,
                    selected_domain_id=sovereign.get("selected_domain_id"),
                    sovereign_decision=sovereign,
                    federation_decision=federation,
                    workload=workload,
                )
            )

        if not selected_runtime_id:
            selected_runtime_id = (
                federation.get("selected_runtime_id")
                if federation
                else self.local_runtime_id
            )

        local_dispatch = bool(selected_runtime_id == self.local_runtime_id)

        if prefer_local and self._can_use_local(sovereign, federation):
            selected_runtime_id = self.local_runtime_id
            local_dispatch = True

        route_type = ROUTE_LOCAL if local_dispatch else ROUTE_FEDERATED

        dispatch_result: Dict[str, Any] = {}

        if local_dispatch and dispatch_local:
            dispatch_result = self._dispatch_local(
                tenant_id=tenant_id,
                workload=workload,
                capability=capability,
                action=action,
                agent_name=agent_name,
            )

            if not dispatch_result.get("ok", True):
                return self._record_decision(
                    FederatedRouteDecision(
                        decision_id=self._new_decision_id(),
                        tenant_id=tenant_id,
                        allowed=False,
                        route_type=ROUTE_BLOCKED,
                        reason=dispatch_result.get("reason", "Local dispatch failed."),
                        capability=capability,
                        selected_runtime_id=selected_runtime_id,
                        selected_domain_id=sovereign.get("selected_domain_id"),
                        local_dispatch=True,
                        sovereign_decision=sovereign,
                        federation_decision=federation or {},
                        dispatch_result=dispatch_result,
                        workload=workload,
                    )
                )

        decision = FederatedRouteDecision(
            decision_id=self._new_decision_id(),
            tenant_id=tenant_id,
            allowed=True,
            route_type=route_type,
            reason="Federated sovereign route authorized.",
            capability=capability,
            selected_runtime_id=selected_runtime_id,
            selected_domain_id=sovereign.get("selected_domain_id"),
            local_dispatch=local_dispatch,
            requires_approval=False,
            sovereign_decision=sovereign,
            federation_decision=federation or {},
            dispatch_result=dispatch_result,
            workload=workload,
            metadata={
                "prefer_local": prefer_local,
                "dispatch_local": dispatch_local,
            },
        )

        return self._record_decision(decision)

    # ========================================================
    # QUEUE / ACTION HELPERS
    # ========================================================

    def route_action(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        agent_name: str,
        action: str,
        context: Optional[Dict[str, Any]] = None,
        capability: Optional[str] = None,
        priority: int = 100,
        dispatch_local: bool = True,
    ) -> FederatedRouteDecision:
        workload = dict(context or {})
        workload.setdefault("agent_name", agent_name)
        workload.setdefault("action", action)
        workload.setdefault("priority", priority)

        decision = self.route_workload(
            tenant_id=tenant_id,
            workload=workload,
            capability=capability,
            action=action,
            agent_name=agent_name,
            dispatch_local=False,
        )

        if not decision.allowed:
            return decision

        if decision.local_dispatch and dispatch_local:
            job_id = self._enqueue_local_action(
                tenant_id=tenant_id,
                agent_name=agent_name,
                action=action,
                context=workload,
                priority=priority,
            )

            decision.dispatch_result = {
                "ok": True,
                "dispatch": "LOCAL_QUEUE",
                "job_id": job_id,
            }

            self._emit(
                "FEDERATED_ROUTE_LOCAL_ENQUEUED",
                decision.to_dict(),
            )

        return decision

    def _enqueue_local_action(
        self,
        *,
        tenant_id: str,
        agent_name: str,
        action: str,
        context: Dict[str, Any],
        priority: int,
    ) -> Optional[str]:
        if self.queue is None:
            return None

        if hasattr(self.queue, "enqueue_action"):
            return self.queue.enqueue_action(
                agent_name=agent_name,
                action=action,
                context=context,
                tenant_id=tenant_id,
                priority=priority,
            )

        return None

    # ========================================================
    # FAILOVER
    # ========================================================

    def plan_failover(
        self,
        *,
        failed_runtime_id: str,
        tenant_id: str = DEFAULT_TENANT,
        capability: Optional[str] = None,
        workload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        workload = dict(workload or {})

        if self.federation_manager is None:
            return {
                "ok": False,
                "reason": "federation_manager_unavailable",
                "failed_runtime_id": failed_runtime_id,
            }

        plan = self.federation_manager.failover_plan(
            failed_runtime_id=failed_runtime_id,
            tenant_id=tenant_id,
            capability=capability,
        )

        if not plan.get("can_failover"):
            return {
                "ok": False,
                "reason": "No legal failover runtime available.",
                "plan": plan,
            }

        selected_runtime = plan.get("recommended_runtime_id")

        sovereign = self._authorize(
            tenant_id=tenant_id,
            workload=workload,
            capability=capability,
            target_runtime_id=selected_runtime,
            action=workload.get("action"),
            agent_name=workload.get("agent_name"),
        )

        if not sovereign.get("allowed", False):
            return {
                "ok": False,
                "reason": "Sovereign enforcement blocked failover.",
                "plan": plan,
                "sovereign_decision": sovereign,
            }

        return {
            "ok": True,
            "reason": "Failover route authorized.",
            "failed_runtime_id": failed_runtime_id,
            "target_runtime_id": selected_runtime,
            "plan": plan,
            "sovereign_decision": sovereign,
        }

    # ========================================================
    # INTERNAL DECISION HELPERS
    # ========================================================

    def _authorize(
        self,
        *,
        tenant_id: str,
        workload: Dict[str, Any],
        capability: Optional[str],
        action: Optional[str] = None,
        agent_name: Optional[str] = None,
        target_runtime_id: Optional[str] = None,
        require_govcloud: bool = False,
        require_high_trust: bool = False,
        allow_degraded_runtime: bool = False,
    ) -> Dict[str, Any]:
        if self.sovereign_controller is None:
            return {
                "allowed": True,
                "decision": "ALLOWED",
                "reason": "Sovereign controller unavailable; permissive local route.",
                "selected_runtime_id": self.local_runtime_id,
            }

        decision = self.sovereign_controller.authorize_execution(
            tenant_id=tenant_id,
            workload=workload,
            capability=capability,
            target_runtime_id=target_runtime_id,
            require_govcloud=require_govcloud,
            require_high_trust=require_high_trust,
            allow_degraded_runtime=allow_degraded_runtime,
            actor="federated_execution_router",
        )

        return (
            decision.to_dict()
            if hasattr(decision, "to_dict")
            else dict(decision)
        )

    def _choose_runtime(
        self,
        *,
        tenant_id: str,
        capability: Optional[str],
        require_govcloud: bool,
        require_high_trust: bool,
        allow_degraded_runtime: bool,
    ) -> Dict[str, Any]:
        if self.federation_manager is None:
            return {
                "allowed": True,
                "status": "LOCAL_ONLY",
                "reason": "Federation unavailable; local runtime selected.",
                "selected_runtime_id": self.local_runtime_id,
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

    def _can_use_local(
        self,
        sovereign: Dict[str, Any],
        federation: Optional[Dict[str, Any]],
    ) -> bool:
        if not sovereign.get("allowed", False):
            return False

        selected = sovereign.get("selected_runtime_id")

        if selected and selected != self.local_runtime_id:
            return False

        if federation:
            selected_fed = federation.get("selected_runtime_id")
            if selected_fed and selected_fed != self.local_runtime_id:
                return False

        return True

    def _dispatch_local(
        self,
        *,
        tenant_id: str,
        workload: Dict[str, Any],
        capability: Optional[str],
        action: Optional[str],
        agent_name: Optional[str],
    ) -> Dict[str, Any]:
        if self.local_router is None:
            return {
                "ok": False,
                "reason": "local_router_unavailable",
            }

        if hasattr(self.local_router, "route_next"):
            try:
                result = self.local_router.route_next(
                    tenant_id=tenant_id,
                    required_capability=capability,
                )

                return {
                    "ok": True,
                    "dispatch": "LOCAL_ROUTER",
                    "result": (
                        result.to_dict()
                        if hasattr(result, "to_dict")
                        else result
                    ),
                }

            except TypeError:
                try:
                    result = self.local_router.route_next()
                    return {
                        "ok": True,
                        "dispatch": "LOCAL_ROUTER",
                        "result": (
                            result.to_dict()
                            if hasattr(result, "to_dict")
                            else result
                        ),
                    }
                except Exception as exc:
                    return {
                        "ok": False,
                        "reason": str(exc),
                    }

            except Exception as exc:
                return {
                    "ok": False,
                    "reason": str(exc),
                }

        return {
            "ok": False,
            "reason": "local_router_has_no_route_next",
        }

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

    def routing_status(self) -> Dict[str, Any]:
        allowed = len([d for d in self._decisions if d.allowed])
        blocked = len([d for d in self._decisions if not d.allowed])

        local = len([d for d in self._decisions if d.route_type == ROUTE_LOCAL])
        federated = len([d for d in self._decisions if d.route_type == ROUTE_FEDERATED])

        return {
            "decision_count": len(self._decisions),
            "allowed": allowed,
            "blocked": blocked,
            "local_routes": local,
            "federated_routes": federated,
            "local_runtime_id": self.local_runtime_id,
            "federation_available": self.federation_manager is not None,
            "sovereignty_available": self.sovereign_controller is not None,
        }

    # ========================================================
    # INTERNAL
    # ========================================================

    def _record_decision(
        self,
        decision: FederatedRouteDecision,
    ) -> FederatedRouteDecision:
        self._decisions.append(decision)
        self._decisions = self._decisions[-500:]

        self._emit(
            "FEDERATED_EXECUTION_ROUTE_DECISION",
            decision.to_dict(),
        )

        return decision

    def _new_decision_id(self) -> str:
        return f"FED-ROUTE-{uuid.uuid4().hex[:12].upper()}"

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
                source="federated_execution_router",
                severity=payload.get("route_type") or "INFO",
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


_DEFAULT_FEDERATED_EXECUTION_ROUTER: Optional[
    FederatedExecutionRouter
] = None


def get_federated_execution_router(
    *,
    local_router: Any = None,
    federation_manager: Any = None,
    sovereign_controller: Any = None,
    domain_manager: Any = None,
    queue: Any = None,
    storage: Any = None,
    event_bus: Any = None,
    local_runtime_id: str = "local-runtime",
    reset: bool = False,
) -> FederatedExecutionRouter:
    global _DEFAULT_FEDERATED_EXECUTION_ROUTER

    if reset or _DEFAULT_FEDERATED_EXECUTION_ROUTER is None:
        _DEFAULT_FEDERATED_EXECUTION_ROUTER = FederatedExecutionRouter(
            local_router=local_router,
            federation_manager=federation_manager,
            sovereign_controller=sovereign_controller,
            domain_manager=domain_manager,
            queue=queue,
            storage=storage,
            event_bus=event_bus,
            local_runtime_id=local_runtime_id,
        )

    return _DEFAULT_FEDERATED_EXECUTION_ROUTER