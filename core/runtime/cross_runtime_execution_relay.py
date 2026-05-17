"""
core/runtime/cross_runtime_execution_relay.py

Cross Runtime Execution Relay.

Purpose:
- sovereign execution continuity
- cross-runtime relay planning
- failover continuation support
- execution state transfer envelope
- sovereign relay validation
- execution lineage preservation

Architecture Rules:
- no Streamlit/session_state dependency
- no persistent SQLite connection
- no hidden global mutation
- explicit service-owned relay state
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


RELAY_PENDING = "PENDING"
RELAY_AUTHORIZED = "AUTHORIZED"
RELAY_BLOCKED = "BLOCKED"
RELAY_IN_PROGRESS = "IN_PROGRESS"
RELAY_COMPLETED = "COMPLETED"
RELAY_FAILED = "FAILED"
RELAY_REQUIRES_APPROVAL = "REQUIRES_APPROVAL"

RELAY_REASON_FAILOVER = "FAILOVER"
RELAY_REASON_OPTIMIZATION = "OPTIMIZATION"
RELAY_REASON_RECOVERY = "RECOVERY"
RELAY_REASON_MANUAL = "MANUAL"
RELAY_REASON_SOVEREIGN_REROUTE = "SOVEREIGN_REROUTE"

DEFAULT_TENANT = "default"


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class ExecutionRelayEnvelope:
    relay_id: str
    tenant_id: str
    source_runtime_id: str
    target_runtime_id: str
    status: str = RELAY_PENDING
    reason: str = RELAY_REASON_MANUAL
    workload: Dict[str, Any] = field(default_factory=dict)
    execution_state: Dict[str, Any] = field(default_factory=dict)
    lineage: Dict[str, Any] = field(default_factory=dict)
    sovereign_decision: Dict[str, Any] = field(default_factory=dict)
    route_decision: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)
    updated_at_ms: int = field(default_factory=_now_ms)
    completed_at_ms: Optional[int] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ExecutionRelayResult:
    relay_id: str
    ok: bool
    status: str
    message: str
    target_runtime_id: Optional[str] = None
    target_job_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    completed_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CrossRuntimeExecutionRelay:
    def __init__(
        self,
        *,
        federated_router: Any = None,
        sovereign_controller: Any = None,
        federation_manager: Any = None,
        cluster_manager: Any = None,
        mesh_optimizer: Any = None,
        queue: Any = None,
        graph_engine: Any = None,
        recovery_manager: Any = None,
        storage: Any = None,
        event_bus: Any = None,
        local_runtime_id: str = "local-runtime",
    ) -> None:
        self.storage = storage
        self.federated_router = (
            federated_router
            or getattr(storage, "federated_execution_router", None)
        )
        self.sovereign_controller = (
            sovereign_controller
            or getattr(storage, "sovereign_execution_controller", None)
        )
        self.federation_manager = (
            federation_manager
            or getattr(storage, "runtime_federation_manager", None)
        )
        self.cluster_manager = (
            cluster_manager
            or getattr(storage, "distributed_runtime_cluster_manager", None)
        )
        self.mesh_optimizer = (
            mesh_optimizer
            or getattr(storage, "sovereign_mesh_optimizer", None)
        )
        self.queue = queue or getattr(storage, "execution_queue", None)
        self.graph_engine = graph_engine or getattr(storage, "execution_graph_engine", None)
        self.recovery_manager = (
            recovery_manager
            or getattr(storage, "runtime_recovery_manager", None)
        )
        self.event_bus = event_bus or getattr(storage, "event_bus", None)
        self.local_runtime_id = local_runtime_id

        self._relays: Dict[str, ExecutionRelayEnvelope] = {}
        self._results: List[ExecutionRelayResult] = []

    # ========================================================
    # RELAY PLANNING
    # ========================================================

    def plan_relay(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        source_runtime_id: str = "local-runtime",
        target_runtime_id: Optional[str] = None,
        workload: Optional[Dict[str, Any]] = None,
        execution_state: Optional[Dict[str, Any]] = None,
        reason: str = RELAY_REASON_MANUAL,
        capability: Optional[str] = "execution_queue",
    ) -> ExecutionRelayEnvelope:
        workload = dict(workload or {})
        execution_state = dict(execution_state or {})

        if target_runtime_id is None:
            target_runtime_id = self._choose_target_runtime(
                tenant_id=tenant_id,
                workload=workload,
                capability=capability,
                source_runtime_id=source_runtime_id,
            )

        relay = ExecutionRelayEnvelope(
            relay_id=f"RELAY-{uuid.uuid4().hex[:12].upper()}",
            tenant_id=tenant_id,
            source_runtime_id=source_runtime_id,
            target_runtime_id=target_runtime_id or "",
            reason=reason,
            workload=workload,
            execution_state=execution_state,
            lineage=self._build_lineage(
                tenant_id=tenant_id,
                source_runtime_id=source_runtime_id,
                target_runtime_id=target_runtime_id,
                workload=workload,
                execution_state=execution_state,
            ),
            metadata={
                "capability": capability,
                "planned_by": "cross_runtime_execution_relay",
            },
        )

        validation = self._validate_relay(relay, capability=capability)

        relay.sovereign_decision = validation.get("sovereign_decision", {})
        relay.route_decision = validation.get("route_decision", {})

        if validation.get("requires_approval"):
            relay.status = RELAY_REQUIRES_APPROVAL
        elif validation.get("allowed"):
            relay.status = RELAY_AUTHORIZED
        else:
            relay.status = RELAY_BLOCKED
            relay.error = validation.get("reason")

        relay.updated_at_ms = _now_ms()

        self._relays[relay.relay_id] = relay

        self._emit(
            "CROSS_RUNTIME_RELAY_PLANNED",
            relay.to_dict(),
        )

        return relay

    def _choose_target_runtime(
        self,
        *,
        tenant_id: str,
        workload: Dict[str, Any],
        capability: Optional[str],
        source_runtime_id: str,
    ) -> Optional[str]:
        if self.federated_router is not None:
            try:
                decision = self.federated_router.route_workload(
                    tenant_id=tenant_id,
                    workload={
                        **workload,
                        "source": "cross_runtime_execution_relay",
                    },
                    capability=capability,
                    dispatch_local=False,
                    prefer_local=False,
                )

                payload = (
                    decision.to_dict()
                    if hasattr(decision, "to_dict")
                    else dict(decision)
                )

                target = payload.get("selected_runtime_id")
                if target and target != source_runtime_id:
                    return target
            except Exception:
                pass

        if self.federation_manager is not None:
            try:
                decision = self.federation_manager.choose_runtime(
                    tenant_id=tenant_id,
                    capability=capability,
                    allow_degraded=False,
                )

                payload = (
                    decision.to_dict()
                    if hasattr(decision, "to_dict")
                    else dict(decision)
                )

                target = payload.get("selected_runtime_id")
                if target:
                    return target
            except Exception:
                pass

        return self.local_runtime_id

    # ========================================================
    # RELAY EXECUTION
    # ========================================================

    def execute_relay(
        self,
        relay_id: str,
        *,
        force: bool = False,
    ) -> ExecutionRelayResult:
        relay = self._relays.get(relay_id)

        if relay is None:
            return ExecutionRelayResult(
                relay_id=relay_id,
                ok=False,
                status=RELAY_FAILED,
                message="Relay not found.",
            )

        if relay.status == RELAY_REQUIRES_APPROVAL and not force:
            result = ExecutionRelayResult(
                relay_id=relay_id,
                ok=False,
                status=RELAY_REQUIRES_APPROVAL,
                message="Relay requires approval.",
                target_runtime_id=relay.target_runtime_id,
                metadata=relay.to_dict(),
            )
            self._record_result(result)
            return result

        if relay.status == RELAY_BLOCKED and not force:
            result = ExecutionRelayResult(
                relay_id=relay_id,
                ok=False,
                status=RELAY_BLOCKED,
                message=relay.error or "Relay blocked by sovereign validation.",
                target_runtime_id=relay.target_runtime_id,
                metadata=relay.to_dict(),
            )
            self._record_result(result)
            return result

        relay.status = RELAY_IN_PROGRESS
        relay.updated_at_ms = _now_ms()

        self._emit(
            "CROSS_RUNTIME_RELAY_STARTED",
            relay.to_dict(),
        )

        try:
            target_job_id = self._dispatch_relay(relay)

            relay.status = RELAY_COMPLETED
            relay.completed_at_ms = _now_ms()
            relay.updated_at_ms = _now_ms()

            result = ExecutionRelayResult(
                relay_id=relay.relay_id,
                ok=True,
                status=RELAY_COMPLETED,
                message="Execution relay completed.",
                target_runtime_id=relay.target_runtime_id,
                target_job_id=target_job_id,
                metadata=relay.to_dict(),
            )

        except Exception as exc:
            relay.status = RELAY_FAILED
            relay.error = str(exc)
            relay.updated_at_ms = _now_ms()

            result = ExecutionRelayResult(
                relay_id=relay.relay_id,
                ok=False,
                status=RELAY_FAILED,
                message=str(exc),
                target_runtime_id=relay.target_runtime_id,
                metadata=relay.to_dict(),
            )

        self._record_result(result)

        self._emit(
            "CROSS_RUNTIME_RELAY_COMPLETED",
            result.to_dict(),
        )

        return result

    def relay_execution(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        source_runtime_id: str = "local-runtime",
        target_runtime_id: Optional[str] = None,
        workload: Optional[Dict[str, Any]] = None,
        execution_state: Optional[Dict[str, Any]] = None,
        reason: str = RELAY_REASON_MANUAL,
        capability: Optional[str] = "execution_queue",
        force: bool = False,
    ) -> ExecutionRelayResult:
        relay = self.plan_relay(
            tenant_id=tenant_id,
            source_runtime_id=source_runtime_id,
            target_runtime_id=target_runtime_id,
            workload=workload,
            execution_state=execution_state,
            reason=reason,
            capability=capability,
        )

        return self.execute_relay(
            relay.relay_id,
            force=force,
        )

    # ========================================================
    # FAILOVER CONTINUITY
    # ========================================================

    def relay_failed_runtime(
        self,
        *,
        failed_runtime_id: str,
        tenant_id: str = DEFAULT_TENANT,
        workload: Optional[Dict[str, Any]] = None,
        execution_state: Optional[Dict[str, Any]] = None,
        capability: Optional[str] = "execution_queue",
    ) -> ExecutionRelayResult:
        target_runtime_id = None

        if self.federation_manager is not None:
            try:
                plan = self.federation_manager.failover_plan(
                    failed_runtime_id=failed_runtime_id,
                    tenant_id=tenant_id,
                    capability=capability,
                )
                if plan.get("can_failover"):
                    target_runtime_id = plan.get("recommended_runtime_id")
            except Exception:
                pass

        return self.relay_execution(
            tenant_id=tenant_id,
            source_runtime_id=failed_runtime_id,
            target_runtime_id=target_runtime_id,
            workload=workload or {
                "action": "RUNTIME_FAILOVER_RELAY",
                "failed_runtime_id": failed_runtime_id,
            },
            execution_state=execution_state or {},
            reason=RELAY_REASON_FAILOVER,
            capability=capability,
        )

    # ========================================================
    # VALIDATION / DISPATCH
    # ========================================================

    def _validate_relay(
        self,
        relay: ExecutionRelayEnvelope,
        *,
        capability: Optional[str],
    ) -> Dict[str, Any]:
        if not relay.target_runtime_id:
            return {
                "allowed": False,
                "reason": "No target runtime selected.",
            }

        sovereign_payload: Dict[str, Any] = {}
        route_payload: Dict[str, Any] = {}

        if self.sovereign_controller is not None:
            try:
                decision = self.sovereign_controller.authorize_execution(
                    tenant_id=relay.tenant_id,
                    workload={
                        **relay.workload,
                        "relay_id": relay.relay_id,
                        "source_runtime_id": relay.source_runtime_id,
                        "target_runtime_id": relay.target_runtime_id,
                        "execution_lineage": relay.lineage,
                    },
                    capability=capability,
                    target_runtime_id=relay.target_runtime_id,
                    actor="cross_runtime_execution_relay",
                )

                sovereign_payload = (
                    decision.to_dict()
                    if hasattr(decision, "to_dict")
                    else dict(decision)
                )

                if sovereign_payload.get("decision") == "REQUIRES_APPROVAL":
                    return {
                        "allowed": False,
                        "requires_approval": True,
                        "reason": sovereign_payload.get("reason"),
                        "sovereign_decision": sovereign_payload,
                    }

                if not sovereign_payload.get("allowed", False):
                    return {
                        "allowed": False,
                        "reason": sovereign_payload.get("reason"),
                        "sovereign_decision": sovereign_payload,
                    }

            except Exception as exc:
                return {
                    "allowed": False,
                    "reason": f"Sovereign validation failed: {exc}",
                }

        if self.federated_router is not None:
            try:
                decision = self.federated_router.route_workload(
                    tenant_id=relay.tenant_id,
                    workload=relay.workload,
                    capability=capability,
                    dispatch_local=False,
                    target_runtime_id=relay.target_runtime_id
                    if hasattr(self.federated_router, "route_workload")
                    else None,
                )

                route_payload = (
                    decision.to_dict()
                    if hasattr(decision, "to_dict")
                    else dict(decision)
                )

            except TypeError:
                route_payload = {
                    "allowed": True,
                    "reason": "Federated router does not support target runtime parameter.",
                    "selected_runtime_id": relay.target_runtime_id,
                }
            except Exception as exc:
                return {
                    "allowed": False,
                    "reason": f"Federated route validation failed: {exc}",
                    "sovereign_decision": sovereign_payload,
                }

        return {
            "allowed": True,
            "reason": "Relay validation authorized.",
            "sovereign_decision": sovereign_payload,
            "route_decision": route_payload,
        }

    def _dispatch_relay(
        self,
        relay: ExecutionRelayEnvelope,
    ) -> Optional[str]:
        payload = {
            "action": "CROSS_RUNTIME_RELAY_CONTINUATION",
            "relay_id": relay.relay_id,
            "source_runtime_id": relay.source_runtime_id,
            "target_runtime_id": relay.target_runtime_id,
            "tenant_id": relay.tenant_id,
            "workload": relay.workload,
            "execution_state": relay.execution_state,
            "lineage": relay.lineage,
            "sovereign_decision": relay.sovereign_decision,
            "route_decision": relay.route_decision,
        }

        if relay.target_runtime_id == self.local_runtime_id:
            return self._enqueue_local(payload, relay.tenant_id)

        # Future remote transport hook.
        # For now, preserve the relay envelope and mark as locally staged.
        return self._enqueue_local(
            {
                **payload,
                "remote_relay_staged": True,
                "remote_transport_pending": True,
            },
            relay.tenant_id,
        )

    def _enqueue_local(
        self,
        payload: Dict[str, Any],
        tenant_id: str,
    ) -> Optional[str]:
        if self.queue is None:
            return None

        if hasattr(self.queue, "enqueue_action"):
            return self.queue.enqueue_action(
                agent_name="cross_runtime_execution_relay",
                action=payload.get("action", "CROSS_RUNTIME_RELAY_CONTINUATION"),
                context=payload,
                tenant_id=tenant_id,
                priority=25,
            )

        if hasattr(self.queue, "enqueue"):
            return self.queue.enqueue(payload)

        return None

    # ========================================================
    # LINEAGE
    # ========================================================

    def _build_lineage(
        self,
        *,
        tenant_id: str,
        source_runtime_id: str,
        target_runtime_id: Optional[str],
        workload: Dict[str, Any],
        execution_state: Dict[str, Any],
    ) -> Dict[str, Any]:
        return {
            "lineage_id": f"RELAY-LINEAGE-{uuid.uuid4().hex[:12].upper()}",
            "tenant_id": tenant_id,
            "source_runtime_id": source_runtime_id,
            "target_runtime_id": target_runtime_id,
            "source_execution_id": (
                execution_state.get("execution_id")
                or workload.get("execution_id")
            ),
            "source_graph_id": (
                execution_state.get("graph_id")
                or workload.get("graph_id")
            ),
            "source_job_id": (
                execution_state.get("job_id")
                or workload.get("job_id")
            ),
            "created_at_ms": _now_ms(),
            "continuity_type": "cross_runtime_relay",
        }

    # ========================================================
    # READS
    # ========================================================

    def get_relay(
        self,
        relay_id: str,
    ) -> Optional[Dict[str, Any]]:
        relay = self._relays.get(relay_id)
        return relay.to_dict() if relay else None

    def list_relays(
        self,
        *,
        status: Optional[str] = None,
        tenant_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        relays = list(self._relays.values())

        if status:
            relays = [r for r in relays if r.status == status]

        if tenant_id:
            relays = [r for r in relays if r.tenant_id == tenant_id]

        relays = sorted(
            relays,
            key=lambda r: r.created_at_ms,
            reverse=True,
        )

        return [
            r.to_dict()
            for r in relays[:limit]
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

    def relay_status(self) -> Dict[str, Any]:
        relays = list(self._relays.values())

        return {
            "relay_count": len(relays),
            "authorized": len([r for r in relays if r.status == RELAY_AUTHORIZED]),
            "blocked": len([r for r in relays if r.status == RELAY_BLOCKED]),
            "requires_approval": len([r for r in relays if r.status == RELAY_REQUIRES_APPROVAL]),
            "in_progress": len([r for r in relays if r.status == RELAY_IN_PROGRESS]),
            "completed": len([r for r in relays if r.status == RELAY_COMPLETED]),
            "failed": len([r for r in relays if r.status == RELAY_FAILED]),
            "result_count": len(self._results),
        }

    # ========================================================
    # INTERNAL
    # ========================================================

    def _record_result(
        self,
        result: ExecutionRelayResult,
    ) -> None:
        self._results.append(result)
        self._results = self._results[-500:]

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
                source="cross_runtime_execution_relay",
                severity=payload.get("status") or "INFO",
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


_DEFAULT_CROSS_RUNTIME_EXECUTION_RELAY: Optional[
    CrossRuntimeExecutionRelay
] = None


def get_cross_runtime_execution_relay(
    *,
    federated_router: Any = None,
    sovereign_controller: Any = None,
    federation_manager: Any = None,
    cluster_manager: Any = None,
    mesh_optimizer: Any = None,
    queue: Any = None,
    graph_engine: Any = None,
    recovery_manager: Any = None,
    storage: Any = None,
    event_bus: Any = None,
    local_runtime_id: str = "local-runtime",
    reset: bool = False,
) -> CrossRuntimeExecutionRelay:
    global _DEFAULT_CROSS_RUNTIME_EXECUTION_RELAY

    if reset or _DEFAULT_CROSS_RUNTIME_EXECUTION_RELAY is None:
        _DEFAULT_CROSS_RUNTIME_EXECUTION_RELAY = CrossRuntimeExecutionRelay(
            federated_router=federated_router,
            sovereign_controller=sovereign_controller,
            federation_manager=federation_manager,
            cluster_manager=cluster_manager,
            mesh_optimizer=mesh_optimizer,
            queue=queue,
            graph_engine=graph_engine,
            recovery_manager=recovery_manager,
            storage=storage,
            event_bus=event_bus,
            local_runtime_id=local_runtime_id,
        )

    return _DEFAULT_CROSS_RUNTIME_EXECUTION_RELAY