"""
core/runtime/runtime_federation_manager.py

Runtime Federation Manager.

Purpose:
- track multiple runtime domains/clusters
- coordinate distributed runtime health
- support tenant-aware runtime placement
- prepare for GovCloud / isolated execution domains
- enable future cross-runtime routing and failover

Architecture Rules:
- no Streamlit/session_state dependency
- no persistent shared SQLite connection
- no hidden runtime mutation
- service-owned state only
- explicit tenant/runtime boundaries
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


RUNTIME_STATUS_ONLINE = "ONLINE"
RUNTIME_STATUS_DEGRADED = "DEGRADED"
RUNTIME_STATUS_OFFLINE = "OFFLINE"
RUNTIME_STATUS_QUARANTINED = "QUARANTINED"
RUNTIME_STATUS_MAINTENANCE = "MAINTENANCE"

DOMAIN_LOCAL = "LOCAL"
DOMAIN_STANDALONE = "STANDALONE"
DOMAIN_DISTRIBUTED = "DISTRIBUTED"
DOMAIN_GOVCLOUD = "GOVCLOUD"
DOMAIN_AIRGAPPED = "AIRGAPPED"
DOMAIN_CUSTOMER_ISOLATED = "CUSTOMER_ISOLATED"

TRUST_HIGH = "HIGH"
TRUST_MEDIUM = "MEDIUM"
TRUST_LOW = "LOW"
TRUST_RESTRICTED = "RESTRICTED"

PLACEMENT_ALLOWED = "ALLOWED"
PLACEMENT_BLOCKED = "BLOCKED"
PLACEMENT_DEGRADED = "DEGRADED"

DEFAULT_TENANT = "default"


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class FederatedRuntimeNode:
    runtime_id: str
    name: str
    domain_type: str = DOMAIN_LOCAL
    region: str = "local"
    status: str = RUNTIME_STATUS_ONLINE
    trust_level: str = TRUST_HIGH
    tenant_affinity: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    capacity_units: int = 100
    active_units: int = 0
    health_score: float = 100.0
    risk_level: str = "LOW"
    metadata: Dict[str, Any] = field(default_factory=dict)
    registered_at_ms: int = field(default_factory=_now_ms)
    last_heartbeat_ms: int = field(default_factory=_now_ms)
    last_error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FederationPlacementDecision:
    decision_id: str
    tenant_id: str
    capability: Optional[str]
    allowed: bool
    status: str
    reason: str
    selected_runtime_id: Optional[str] = None
    candidate_runtime_ids: List[str] = field(default_factory=list)
    blocked_runtime_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RuntimeFederationManager:
    def __init__(
        self,
        *,
        registry: Any = None,
        lifecycle: Any = None,
        health_manager: Any = None,
        supervisor: Any = None,
        storage: Any = None,
        event_bus: Any = None,
        local_runtime_id: str = "local-runtime",
    ) -> None:
        self.storage = storage
        self.registry = registry or getattr(storage, "runtime_service_registry", None)
        self.lifecycle = lifecycle or getattr(storage, "runtime_lifecycle_manager", None)
        self.health_manager = health_manager or getattr(storage, "runtime_health_manager", None)
        self.supervisor = supervisor or getattr(storage, "autonomous_runtime_supervisor", None)
        self.event_bus = event_bus or getattr(storage, "event_bus", None)

        self.local_runtime_id = local_runtime_id
        self._nodes: Dict[str, FederatedRuntimeNode] = {}
        self._decisions: List[FederationPlacementDecision] = []

        self.register_local_runtime()

    # ========================================================
    # REGISTRATION
    # ========================================================

    def register_local_runtime(self) -> FederatedRuntimeNode:
        health_score = 100.0
        risk_level = "LOW"

        if self.health_manager is not None:
            try:
                snapshot = self.health_manager.evaluate()
                if hasattr(snapshot, "score"):
                    health_score = float(snapshot.score)
                if hasattr(snapshot, "risk"):
                    risk_level = str(snapshot.risk)
            except Exception:
                pass

        node = FederatedRuntimeNode(
            runtime_id=self.local_runtime_id,
            name="Local Runtime",
            domain_type=DOMAIN_LOCAL,
            region="local",
            status=RUNTIME_STATUS_ONLINE,
            trust_level=TRUST_HIGH,
            tenant_affinity=[DEFAULT_TENANT],
            capabilities=[
                "execution_queue",
                "worker_orchestration",
                "runtime_governance",
                "runtime_recovery",
                "autonomous_supervision",
            ],
            health_score=health_score,
            risk_level=risk_level,
            metadata={
                "source": "runtime_federation_manager",
                "local": True,
            },
        )

        self._nodes[self.local_runtime_id] = node

        self._emit(
            "FEDERATED_RUNTIME_REGISTERED",
            {
                "runtime_id": node.runtime_id,
                "domain_type": node.domain_type,
                "region": node.region,
            },
        )

        return node

    def register_runtime(
        self,
        *,
        runtime_id: Optional[str] = None,
        name: str,
        domain_type: str = DOMAIN_DISTRIBUTED,
        region: str = "unknown",
        trust_level: str = TRUST_MEDIUM,
        tenant_affinity: Optional[List[str]] = None,
        capabilities: Optional[List[str]] = None,
        capacity_units: int = 100,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> FederatedRuntimeNode:
        runtime_id = runtime_id or f"runtime-{uuid.uuid4().hex[:12].upper()}"

        node = FederatedRuntimeNode(
            runtime_id=runtime_id,
            name=name,
            domain_type=domain_type,
            region=region,
            trust_level=trust_level,
            tenant_affinity=tenant_affinity or [],
            capabilities=capabilities or [],
            capacity_units=int(capacity_units),
            metadata=metadata or {},
        )

        self._nodes[runtime_id] = node

        self._emit(
            "FEDERATED_RUNTIME_REGISTERED",
            node.to_dict(),
        )

        return node

    def heartbeat_runtime(
        self,
        runtime_id: str,
        *,
        status: Optional[str] = None,
        health_score: Optional[float] = None,
        risk_level: Optional[str] = None,
        active_units: Optional[int] = None,
        last_error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        node = self._nodes.get(runtime_id)

        if not node:
            return False

        node.last_heartbeat_ms = _now_ms()

        if status is not None:
            node.status = status

        if health_score is not None:
            node.health_score = float(health_score)

        if risk_level is not None:
            node.risk_level = risk_level

        if active_units is not None:
            node.active_units = int(active_units)

        if last_error is not None:
            node.last_error = last_error

        if metadata:
            node.metadata.update(metadata)

        self._emit(
            "FEDERATED_RUNTIME_HEARTBEAT",
            {
                "runtime_id": runtime_id,
                "status": node.status,
                "health_score": node.health_score,
                "risk_level": node.risk_level,
            },
        )

        return True

    # ========================================================
    # FEDERATED PLACEMENT
    # ========================================================

    def choose_runtime(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        capability: Optional[str] = None,
        require_govcloud: bool = False,
        require_high_trust: bool = False,
        allow_degraded: bool = False,
    ) -> FederationPlacementDecision:
        candidates: List[FederatedRuntimeNode] = []
        blocked: List[str] = []

        for node in self._nodes.values():
            ok, reason = self._runtime_eligible(
                node,
                tenant_id=tenant_id,
                capability=capability,
                require_govcloud=require_govcloud,
                require_high_trust=require_high_trust,
                allow_degraded=allow_degraded,
            )

            if ok:
                candidates.append(node)
            else:
                blocked.append(f"{node.runtime_id}: {reason}")

        if not candidates:
            decision = FederationPlacementDecision(
                decision_id=self._new_decision_id(),
                tenant_id=tenant_id,
                capability=capability,
                allowed=False,
                status=PLACEMENT_BLOCKED,
                reason="No eligible federated runtime available.",
                candidate_runtime_ids=[],
                blocked_runtime_ids=blocked,
            )
            self._record_decision(decision)
            return decision

        candidates.sort(
            key=lambda n: (
                -float(n.health_score or 0.0),
                self._load_ratio(n),
                -int(n.capacity_units or 0),
            )
        )

        selected = candidates[0]

        status = (
            PLACEMENT_DEGRADED
            if selected.status == RUNTIME_STATUS_DEGRADED
            else PLACEMENT_ALLOWED
        )

        decision = FederationPlacementDecision(
            decision_id=self._new_decision_id(),
            tenant_id=tenant_id,
            capability=capability,
            allowed=True,
            status=status,
            reason="Runtime placement selected.",
            selected_runtime_id=selected.runtime_id,
            candidate_runtime_ids=[n.runtime_id for n in candidates],
            blocked_runtime_ids=blocked,
            metadata={
                "selected_health_score": selected.health_score,
                "selected_region": selected.region,
                "selected_domain_type": selected.domain_type,
                "selected_trust_level": selected.trust_level,
            },
        )

        self._record_decision(decision)
        return decision

    def _runtime_eligible(
        self,
        node: FederatedRuntimeNode,
        *,
        tenant_id: str,
        capability: Optional[str],
        require_govcloud: bool,
        require_high_trust: bool,
        allow_degraded: bool,
    ) -> tuple[bool, str]:
        if node.status in {
            RUNTIME_STATUS_OFFLINE,
            RUNTIME_STATUS_QUARANTINED,
            RUNTIME_STATUS_MAINTENANCE,
        }:
            return False, f"status={node.status}"

        if node.status == RUNTIME_STATUS_DEGRADED and not allow_degraded:
            return False, "runtime_degraded"

        if node.tenant_affinity and tenant_id not in node.tenant_affinity:
            return False, "tenant_affinity_mismatch"

        if capability and node.capabilities and capability not in node.capabilities:
            return False, "missing_capability"

        if require_govcloud and node.domain_type != DOMAIN_GOVCLOUD:
            return False, "govcloud_required"

        if require_high_trust and node.trust_level != TRUST_HIGH:
            return False, "high_trust_required"

        if self._load_ratio(node) >= 1.0:
            return False, "capacity_exhausted"

        return True, "eligible"

    def _load_ratio(self, node: FederatedRuntimeNode) -> float:
        return float(node.active_units or 0) / max(float(node.capacity_units or 1), 1.0)

    # ========================================================
    # FAILOVER / QUARANTINE
    # ========================================================

    def quarantine_runtime(
        self,
        runtime_id: str,
        *,
        reason: str,
    ) -> bool:
        node = self._nodes.get(runtime_id)

        if not node:
            return False

        node.status = RUNTIME_STATUS_QUARANTINED
        node.last_error = reason
        node.last_heartbeat_ms = _now_ms()

        self._emit(
            "FEDERATED_RUNTIME_QUARANTINED",
            {
                "runtime_id": runtime_id,
                "reason": reason,
            },
        )

        return True

    def restore_runtime(
        self,
        runtime_id: str,
    ) -> bool:
        node = self._nodes.get(runtime_id)

        if not node:
            return False

        node.status = RUNTIME_STATUS_ONLINE
        node.last_error = None
        node.last_heartbeat_ms = _now_ms()

        self._emit(
            "FEDERATED_RUNTIME_RESTORED",
            {
                "runtime_id": runtime_id,
            },
        )

        return True

    def failover_plan(
        self,
        *,
        failed_runtime_id: str,
        tenant_id: str = DEFAULT_TENANT,
        capability: Optional[str] = None,
    ) -> Dict[str, Any]:
        failed = self._nodes.get(failed_runtime_id)

        decision = self.choose_runtime(
            tenant_id=tenant_id,
            capability=capability,
            allow_degraded=False,
        )

        return {
            "failed_runtime_id": failed_runtime_id,
            "failed_runtime": failed.to_dict() if failed else None,
            "placement_decision": decision.to_dict(),
            "can_failover": decision.allowed,
            "recommended_runtime_id": decision.selected_runtime_id,
        }

    # ========================================================
    # FEDERATION HEALTH
    # ========================================================

    def federation_health(self) -> Dict[str, Any]:
        nodes = list(self._nodes.values())

        total = len(nodes)
        online = len([n for n in nodes if n.status == RUNTIME_STATUS_ONLINE])
        degraded = len([n for n in nodes if n.status == RUNTIME_STATUS_DEGRADED])
        offline = len([n for n in nodes if n.status == RUNTIME_STATUS_OFFLINE])
        quarantined = len([n for n in nodes if n.status == RUNTIME_STATUS_QUARANTINED])

        if not nodes:
            avg_health = 0.0
        else:
            avg_health = sum(float(n.health_score or 0.0) for n in nodes) / len(nodes)

        risk = "LOW"
        if quarantined or offline:
            risk = "MEDIUM"
        if degraded >= max(total // 2, 1):
            risk = "HIGH"
        if online == 0 and total > 0:
            risk = "CRITICAL"

        return {
            "total_runtimes": total,
            "online": online,
            "degraded": degraded,
            "offline": offline,
            "quarantined": quarantined,
            "avg_health": round(avg_health, 2),
            "risk": risk,
        }

    # ========================================================
    # READS
    # ========================================================

    def list_runtimes(
        self,
        *,
        status: Optional[str] = None,
        domain_type: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        nodes = list(self._nodes.values())

        if status:
            nodes = [n for n in nodes if n.status == status]

        if domain_type:
            nodes = [n for n in nodes if n.domain_type == domain_type]

        if tenant_id:
            nodes = [
                n for n in nodes
                if not n.tenant_affinity or tenant_id in n.tenant_affinity
            ]

        return [n.to_dict() for n in nodes]

    def get_runtime(
        self,
        runtime_id: str,
    ) -> Optional[Dict[str, Any]]:
        node = self._nodes.get(runtime_id)
        return node.to_dict() if node else None

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
        return [d.to_dict() for d in decisions[:limit]]

    def federation_topology(self) -> Dict[str, Any]:
        nodes = []
        edges = []

        for node in self._nodes.values():
            nodes.append({
                "id": node.runtime_id,
                "label": node.name,
                "domain_type": node.domain_type,
                "region": node.region,
                "status": node.status,
                "health_score": node.health_score,
                "risk_level": node.risk_level,
                "trust_level": node.trust_level,
                "capabilities": node.capabilities,
                "tenant_affinity": node.tenant_affinity,
            })

            if node.runtime_id != self.local_runtime_id:
                edges.append({
                    "source": self.local_runtime_id,
                    "target": node.runtime_id,
                    "type": "FEDERATION_LINK",
                })

        return {
            "nodes": nodes,
            "edges": edges,
            "health": self.federation_health(),
            "created_at_ms": _now_ms(),
        }

    # ========================================================
    # INTERNAL
    # ========================================================

    def _record_decision(
        self,
        decision: FederationPlacementDecision,
    ) -> None:
        self._decisions.append(decision)
        self._decisions = self._decisions[-500:]

        self._emit(
            "FEDERATION_PLACEMENT_DECISION",
            decision.to_dict(),
        )

    def _new_decision_id(self) -> str:
        return f"FED-DECISION-{uuid.uuid4().hex[:12].upper()}"

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
                source="runtime_federation_manager",
                severity=payload.get("risk") or payload.get("risk_level") or "INFO",
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


_DEFAULT_RUNTIME_FEDERATION_MANAGER: Optional[
    RuntimeFederationManager
] = None


def get_runtime_federation_manager(
    *,
    registry: Any = None,
    lifecycle: Any = None,
    health_manager: Any = None,
    supervisor: Any = None,
    storage: Any = None,
    event_bus: Any = None,
    local_runtime_id: str = "local-runtime",
    reset: bool = False,
) -> RuntimeFederationManager:
    global _DEFAULT_RUNTIME_FEDERATION_MANAGER

    if reset or _DEFAULT_RUNTIME_FEDERATION_MANAGER is None:
        _DEFAULT_RUNTIME_FEDERATION_MANAGER = RuntimeFederationManager(
            registry=registry,
            lifecycle=lifecycle,
            health_manager=health_manager,
            supervisor=supervisor,
            storage=storage,
            event_bus=event_bus,
            local_runtime_id=local_runtime_id,
        )

    return _DEFAULT_RUNTIME_FEDERATION_MANAGER