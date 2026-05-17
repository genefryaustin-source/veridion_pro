"""
core/runtime/distributed_runtime_cluster_manager.py

Distributed Runtime Cluster Manager.

Purpose:
- runtime cluster orchestration
- cluster health aggregation
- sovereign cluster grouping
- failover planning
- cluster evacuation
- runtime balancing foundation
- GovCloud / air-gapped / customer-isolated cluster support

Architecture Rules:
- no Streamlit/session_state dependency
- no persistent SQLite connection
- no hidden runtime mutation
- explicit service-owned state
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


CLUSTER_ACTIVE = "ACTIVE"
CLUSTER_DEGRADED = "DEGRADED"
CLUSTER_QUARANTINED = "QUARANTINED"
CLUSTER_DRAINING = "DRAINING"
CLUSTER_MAINTENANCE = "MAINTENANCE"
CLUSTER_OFFLINE = "OFFLINE"

CLUSTER_DOMAIN_LOCAL = "LOCAL"
CLUSTER_DOMAIN_COMMERCIAL = "COMMERCIAL"
CLUSTER_DOMAIN_GOVCLOUD = "GOVCLOUD"
CLUSTER_DOMAIN_AIRGAPPED = "AIRGAPPED"
CLUSTER_DOMAIN_CLASSIFIED = "CLASSIFIED"
CLUSTER_DOMAIN_CUSTOMER_ISOLATED = "CUSTOMER_ISOLATED"
CLUSTER_DOMAIN_EXPORT_CONTROLLED = "EXPORT_CONTROLLED"

FAILOVER_READY = "READY"
FAILOVER_DEGRADED = "DEGRADED"
FAILOVER_BLOCKED = "BLOCKED"

DEFAULT_TENANT = "default"


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class RuntimeCluster:
    cluster_id: str
    name: str
    domain_type: str = CLUSTER_DOMAIN_LOCAL
    region: str = "local"
    status: str = CLUSTER_ACTIVE
    runtime_ids: List[str] = field(default_factory=list)
    tenant_affinity: List[str] = field(default_factory=list)
    allowed_capabilities: List[str] = field(default_factory=list)
    sovereign_tags: List[str] = field(default_factory=list)
    capacity_units: int = 1000
    active_units: int = 0
    health_score: float = 100.0
    risk_level: str = "LOW"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)
    updated_at_ms: int = field(default_factory=_now_ms)
    last_error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ClusterFailoverPlan:
    plan_id: str
    source_cluster_id: str
    tenant_id: str
    capability: Optional[str]
    status: str
    reason: str
    target_cluster_id: Optional[str] = None
    candidate_clusters: List[str] = field(default_factory=list)
    blocked_clusters: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ClusterOperation:
    operation_id: str
    operation_type: str
    cluster_id: str
    status: str
    reason: str
    tenant_id: str = DEFAULT_TENANT
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DistributedRuntimeClusterManager:
    def __init__(
        self,
        *,
        federation_manager: Any = None,
        domain_manager: Any = None,
        sovereign_controller: Any = None,
        registry: Any = None,
        storage: Any = None,
        event_bus: Any = None,
    ) -> None:
        self.storage = storage
        self.federation_manager = (
            federation_manager
            or getattr(storage, "runtime_federation_manager", None)
        )
        self.domain_manager = (
            domain_manager
            or getattr(storage, "execution_domain_manager", None)
        )
        self.sovereign_controller = (
            sovereign_controller
            or getattr(storage, "sovereign_execution_controller", None)
        )
        self.registry = registry or getattr(storage, "runtime_service_registry", None)
        self.event_bus = event_bus or getattr(storage, "event_bus", None)

        self._clusters: Dict[str, RuntimeCluster] = {}
        self._operations: List[ClusterOperation] = []
        self._failover_plans: List[ClusterFailoverPlan] = []

        self._register_default_cluster()

    # ========================================================
    # DEFAULT CLUSTER
    # ========================================================

    def _register_default_cluster(self) -> None:
        local_runtime_id = "local-runtime"

        try:
            if self.federation_manager is not None:
                runtimes = self.federation_manager.list_runtimes()
                if runtimes:
                    local_runtime_id = runtimes[0].get("runtime_id") or local_runtime_id
        except Exception:
            pass

        self.register_cluster(
            cluster_id="cluster-local",
            name="Local Runtime Cluster",
            domain_type=CLUSTER_DOMAIN_LOCAL,
            region="local",
            runtime_ids=[local_runtime_id],
            tenant_affinity=[DEFAULT_TENANT],
            allowed_capabilities=[
                "execution_queue",
                "worker_orchestration",
                "runtime_governance",
                "runtime_recovery",
                "autonomous_supervision",
            ],
            sovereign_tags=["LOCAL", "DEV"],
            metadata={
                "default": True,
                "local": True,
            },
        )

    # ========================================================
    # CLUSTER REGISTRATION
    # ========================================================

    def register_cluster(
        self,
        *,
        cluster_id: Optional[str] = None,
        name: str,
        domain_type: str = CLUSTER_DOMAIN_LOCAL,
        region: str = "local",
        runtime_ids: Optional[List[str]] = None,
        tenant_affinity: Optional[List[str]] = None,
        allowed_capabilities: Optional[List[str]] = None,
        sovereign_tags: Optional[List[str]] = None,
        capacity_units: int = 1000,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RuntimeCluster:
        cluster_id = cluster_id or f"cluster-{uuid.uuid4().hex[:12].upper()}"

        cluster = RuntimeCluster(
            cluster_id=cluster_id,
            name=name,
            domain_type=domain_type,
            region=region,
            runtime_ids=runtime_ids or [],
            tenant_affinity=tenant_affinity or [],
            allowed_capabilities=allowed_capabilities or [],
            sovereign_tags=sovereign_tags or [],
            capacity_units=int(capacity_units),
            metadata=metadata or {},
        )

        self._clusters[cluster_id] = cluster

        self.refresh_cluster_health(cluster_id)

        self._emit(
            "RUNTIME_CLUSTER_REGISTERED",
            cluster.to_dict(),
        )

        return cluster

    def add_runtime_to_cluster(
        self,
        *,
        cluster_id: str,
        runtime_id: str,
    ) -> bool:
        cluster = self._clusters.get(cluster_id)

        if not cluster:
            return False

        if runtime_id not in cluster.runtime_ids:
            cluster.runtime_ids.append(runtime_id)

        cluster.updated_at_ms = _now_ms()

        self.refresh_cluster_health(cluster_id)

        self._record_operation(
            "ADD_RUNTIME_TO_CLUSTER",
            cluster_id=cluster_id,
            status="COMPLETED",
            reason=f"Runtime {runtime_id} added.",
            metadata={"runtime_id": runtime_id},
        )

        return True

    def remove_runtime_from_cluster(
        self,
        *,
        cluster_id: str,
        runtime_id: str,
    ) -> bool:
        cluster = self._clusters.get(cluster_id)

        if not cluster:
            return False

        if runtime_id in cluster.runtime_ids:
            cluster.runtime_ids.remove(runtime_id)

        cluster.updated_at_ms = _now_ms()

        self.refresh_cluster_health(cluster_id)

        self._record_operation(
            "REMOVE_RUNTIME_FROM_CLUSTER",
            cluster_id=cluster_id,
            status="COMPLETED",
            reason=f"Runtime {runtime_id} removed.",
            metadata={"runtime_id": runtime_id},
        )

        return True

    # ========================================================
    # HEALTH
    # ========================================================

    def refresh_cluster_health(
        self,
        cluster_id: str,
    ) -> Dict[str, Any]:
        cluster = self._clusters.get(cluster_id)

        if not cluster:
            return {
                "ok": False,
                "reason": "cluster_not_found",
            }

        runtimes = self._get_cluster_runtimes(cluster)

        if not runtimes:
            cluster.health_score = 0.0
            cluster.risk_level = "CRITICAL"
            cluster.status = CLUSTER_OFFLINE
            cluster.updated_at_ms = _now_ms()
            return cluster.to_dict()

        total_health = 0.0
        active_units = 0
        capacity_units = 0

        online = 0
        degraded = 0
        offline = 0
        quarantined = 0

        for rt in runtimes:
            status = str(rt.get("status") or "").upper()
            total_health += float(rt.get("health_score", 0.0) or 0.0)
            active_units += int(rt.get("active_units", 0) or 0)
            capacity_units += int(rt.get("capacity_units", 0) or 0)

            if status == "ONLINE":
                online += 1
            elif status == "DEGRADED":
                degraded += 1
            elif status == "QUARANTINED":
                quarantined += 1
            else:
                offline += 1

        avg_health = total_health / max(len(runtimes), 1)

        cluster.health_score = round(avg_health, 2)
        cluster.active_units = active_units
        cluster.capacity_units = max(capacity_units, cluster.capacity_units)
        cluster.updated_at_ms = _now_ms()

        if quarantined:
            cluster.status = CLUSTER_DEGRADED
            cluster.risk_level = "HIGH"
        elif offline >= max(len(runtimes) // 2, 1):
            cluster.status = CLUSTER_DEGRADED
            cluster.risk_level = "HIGH"
        elif degraded:
            cluster.status = CLUSTER_DEGRADED
            cluster.risk_level = "MEDIUM"
        elif online > 0:
            cluster.status = CLUSTER_ACTIVE
            cluster.risk_level = "LOW"
        else:
            cluster.status = CLUSTER_OFFLINE
            cluster.risk_level = "CRITICAL"

        return cluster.to_dict()

    def cluster_health(self) -> Dict[str, Any]:
        for cluster_id in list(self._clusters.keys()):
            self.refresh_cluster_health(cluster_id)

        clusters = list(self._clusters.values())

        total = len(clusters)
        active = len([c for c in clusters if c.status == CLUSTER_ACTIVE])
        degraded = len([c for c in clusters if c.status == CLUSTER_DEGRADED])
        quarantined = len([c for c in clusters if c.status == CLUSTER_QUARANTINED])
        draining = len([c for c in clusters if c.status == CLUSTER_DRAINING])
        offline = len([c for c in clusters if c.status == CLUSTER_OFFLINE])

        avg_health = (
            sum(c.health_score for c in clusters) / max(len(clusters), 1)
            if clusters
            else 0.0
        )

        risk = "LOW"
        if degraded or draining:
            risk = "MEDIUM"
        if quarantined:
            risk = "HIGH"
        if active == 0 and total > 0:
            risk = "CRITICAL"

        return {
            "total_clusters": total,
            "active": active,
            "degraded": degraded,
            "quarantined": quarantined,
            "draining": draining,
            "offline": offline,
            "avg_health": round(avg_health, 2),
            "risk": risk,
        }

    # ========================================================
    # CLUSTER SELECTION
    # ========================================================

    def choose_cluster(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        capability: Optional[str] = None,
        domain_type: Optional[str] = None,
        require_sovereign_tag: Optional[str] = None,
        allow_degraded: bool = False,
    ) -> Dict[str, Any]:
        candidates: List[RuntimeCluster] = []
        blocked: List[str] = []

        for cluster in self._clusters.values():
            ok, reason = self._cluster_eligible(
                cluster,
                tenant_id=tenant_id,
                capability=capability,
                domain_type=domain_type,
                require_sovereign_tag=require_sovereign_tag,
                allow_degraded=allow_degraded,
            )

            if ok:
                candidates.append(cluster)
            else:
                blocked.append(f"{cluster.cluster_id}: {reason}")

        if not candidates:
            return {
                "allowed": False,
                "status": "NO_CLUSTER",
                "reason": "No eligible runtime cluster available.",
                "candidate_clusters": [],
                "blocked_clusters": blocked,
            }

        candidates.sort(
            key=lambda c: (
                -float(c.health_score or 0.0),
                self._load_ratio(c),
                -int(c.capacity_units or 0),
            )
        )

        selected = candidates[0]

        return {
            "allowed": True,
            "status": "CLUSTER_SELECTED",
            "reason": "Runtime cluster selected.",
            "selected_cluster_id": selected.cluster_id,
            "candidate_clusters": [c.cluster_id for c in candidates],
            "blocked_clusters": blocked,
            "metadata": {
                "region": selected.region,
                "domain_type": selected.domain_type,
                "health_score": selected.health_score,
                "risk_level": selected.risk_level,
                "runtime_ids": selected.runtime_ids,
            },
        }

    def _cluster_eligible(
        self,
        cluster: RuntimeCluster,
        *,
        tenant_id: str,
        capability: Optional[str],
        domain_type: Optional[str],
        require_sovereign_tag: Optional[str],
        allow_degraded: bool,
    ) -> tuple[bool, str]:
        if cluster.status in {
            CLUSTER_QUARANTINED,
            CLUSTER_DRAINING,
            CLUSTER_MAINTENANCE,
            CLUSTER_OFFLINE,
        }:
            return False, f"cluster_status={cluster.status}"

        if cluster.status == CLUSTER_DEGRADED and not allow_degraded:
            return False, "cluster_degraded"

        if cluster.tenant_affinity and tenant_id not in cluster.tenant_affinity:
            return False, "tenant_affinity_mismatch"

        if capability and cluster.allowed_capabilities:
            if capability not in cluster.allowed_capabilities:
                return False, "capability_not_allowed"

        if domain_type and cluster.domain_type != domain_type:
            return False, "domain_type_mismatch"

        if require_sovereign_tag:
            if require_sovereign_tag not in cluster.sovereign_tags:
                return False, "missing_sovereign_tag"

        if self._load_ratio(cluster) >= 1.0:
            return False, "cluster_capacity_exhausted"

        return True, "eligible"

    def _load_ratio(self, cluster: RuntimeCluster) -> float:
        return float(cluster.active_units or 0) / max(float(cluster.capacity_units or 1), 1.0)

    # ========================================================
    # FAILOVER / EVACUATION
    # ========================================================

    def plan_cluster_failover(
        self,
        *,
        source_cluster_id: str,
        tenant_id: str = DEFAULT_TENANT,
        capability: Optional[str] = None,
        domain_type: Optional[str] = None,
    ) -> ClusterFailoverPlan:
        source = self._clusters.get(source_cluster_id)

        if not source:
            plan = ClusterFailoverPlan(
                plan_id=self._new_plan_id(),
                source_cluster_id=source_cluster_id,
                tenant_id=tenant_id,
                capability=capability,
                status=FAILOVER_BLOCKED,
                reason="Source cluster not found.",
            )
            self._record_failover_plan(plan)
            return plan

        candidates = []
        blocked = []

        for cluster in self._clusters.values():
            if cluster.cluster_id == source_cluster_id:
                continue

            ok, reason = self._cluster_eligible(
                cluster,
                tenant_id=tenant_id,
                capability=capability,
                domain_type=domain_type or source.domain_type,
                require_sovereign_tag=None,
                allow_degraded=False,
            )

            if ok:
                candidates.append(cluster)
            else:
                blocked.append(f"{cluster.cluster_id}: {reason}")

        if not candidates:
            plan = ClusterFailoverPlan(
                plan_id=self._new_plan_id(),
                source_cluster_id=source_cluster_id,
                tenant_id=tenant_id,
                capability=capability,
                status=FAILOVER_BLOCKED,
                reason="No eligible failover cluster available.",
                candidate_clusters=[],
                blocked_clusters=blocked,
            )
            self._record_failover_plan(plan)
            return plan

        candidates.sort(
            key=lambda c: (
                -c.health_score,
                self._load_ratio(c),
            )
        )

        selected = candidates[0]

        plan = ClusterFailoverPlan(
            plan_id=self._new_plan_id(),
            source_cluster_id=source_cluster_id,
            tenant_id=tenant_id,
            capability=capability,
            status=FAILOVER_READY,
            reason="Cluster failover target selected.",
            target_cluster_id=selected.cluster_id,
            candidate_clusters=[c.cluster_id for c in candidates],
            blocked_clusters=blocked,
            metadata={
                "target_region": selected.region,
                "target_domain_type": selected.domain_type,
                "target_runtime_ids": selected.runtime_ids,
            },
        )

        self._record_failover_plan(plan)
        return plan

    def drain_cluster(
        self,
        cluster_id: str,
        *,
        reason: str,
    ) -> bool:
        return self._set_cluster_status(
            cluster_id,
            CLUSTER_DRAINING,
            reason=reason,
            operation_type="DRAIN_CLUSTER",
        )

    def quarantine_cluster(
        self,
        cluster_id: str,
        *,
        reason: str,
    ) -> bool:
        return self._set_cluster_status(
            cluster_id,
            CLUSTER_QUARANTINED,
            reason=reason,
            operation_type="QUARANTINE_CLUSTER",
        )

    def restore_cluster(
        self,
        cluster_id: str,
    ) -> bool:
        return self._set_cluster_status(
            cluster_id,
            CLUSTER_ACTIVE,
            reason="cluster_restored",
            operation_type="RESTORE_CLUSTER",
        )

    def _set_cluster_status(
        self,
        cluster_id: str,
        status: str,
        *,
        reason: str,
        operation_type: str,
    ) -> bool:
        cluster = self._clusters.get(cluster_id)

        if not cluster:
            return False

        cluster.status = status
        cluster.updated_at_ms = _now_ms()
        cluster.last_error = None if status == CLUSTER_ACTIVE else reason

        self._record_operation(
            operation_type,
            cluster_id=cluster_id,
            status="COMPLETED",
            reason=reason,
            metadata={
                "new_status": status,
            },
        )

        self._emit(
            "RUNTIME_CLUSTER_STATUS_CHANGED",
            cluster.to_dict(),
        )

        return True

    # ========================================================
    # TOPOLOGY
    # ========================================================

    def cluster_topology(self) -> Dict[str, Any]:
        nodes = []
        edges = []

        for cluster in self._clusters.values():
            nodes.append({
                "id": cluster.cluster_id,
                "label": cluster.name,
                "type": "CLUSTER",
                "domain_type": cluster.domain_type,
                "region": cluster.region,
                "status": cluster.status,
                "health_score": cluster.health_score,
                "risk_level": cluster.risk_level,
                "tenant_affinity": cluster.tenant_affinity,
                "runtime_count": len(cluster.runtime_ids),
            })

            for runtime_id in cluster.runtime_ids:
                nodes.append({
                    "id": runtime_id,
                    "label": runtime_id,
                    "type": "RUNTIME",
                    "cluster_id": cluster.cluster_id,
                })

                edges.append({
                    "source": cluster.cluster_id,
                    "target": runtime_id,
                    "type": "CONTAINS_RUNTIME",
                })

        return {
            "nodes": nodes,
            "edges": edges,
            "health": self.cluster_health(),
            "created_at_ms": _now_ms(),
        }

    # ========================================================
    # READS
    # ========================================================

    def list_clusters(
        self,
        *,
        status: Optional[str] = None,
        domain_type: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        for cluster_id in list(self._clusters.keys()):
            self.refresh_cluster_health(cluster_id)

        clusters = list(self._clusters.values())

        if status:
            clusters = [c for c in clusters if c.status == status]

        if domain_type:
            clusters = [c for c in clusters if c.domain_type == domain_type]

        if tenant_id:
            clusters = [
                c for c in clusters
                if not c.tenant_affinity or tenant_id in c.tenant_affinity
            ]

        return [c.to_dict() for c in clusters]

    def get_cluster(
        self,
        cluster_id: str,
    ) -> Optional[Dict[str, Any]]:
        if cluster_id not in self._clusters:
            return None

        self.refresh_cluster_health(cluster_id)
        return self._clusters[cluster_id].to_dict()

    def list_operations(
        self,
        *,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        ops = sorted(
            self._operations,
            key=lambda o: o.created_at_ms,
            reverse=True,
        )

        return [o.to_dict() for o in ops[:limit]]

    def list_failover_plans(
        self,
        *,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        plans = sorted(
            self._failover_plans,
            key=lambda p: p.created_at_ms,
            reverse=True,
        )

        return [p.to_dict() for p in plans[:limit]]

    # ========================================================
    # INTERNAL
    # ========================================================

    def _get_cluster_runtimes(
        self,
        cluster: RuntimeCluster,
    ) -> List[Dict[str, Any]]:
        if self.federation_manager is None:
            return [
                {
                    "runtime_id": rid,
                    "status": "ONLINE",
                    "health_score": 100.0,
                    "active_units": 0,
                    "capacity_units": 100,
                }
                for rid in cluster.runtime_ids
            ]

        runtimes = []

        for runtime_id in cluster.runtime_ids:
            rt = self.federation_manager.get_runtime(runtime_id)
            if rt:
                runtimes.append(rt)

        return runtimes

    def _record_operation(
        self,
        operation_type: str,
        *,
        cluster_id: str,
        status: str,
        reason: str,
        tenant_id: str = DEFAULT_TENANT,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ClusterOperation:
        operation = ClusterOperation(
            operation_id=f"CLUSTER-OP-{uuid.uuid4().hex[:12].upper()}",
            operation_type=operation_type,
            cluster_id=cluster_id,
            status=status,
            reason=reason,
            tenant_id=tenant_id,
            metadata=metadata or {},
        )

        self._operations.append(operation)
        self._operations = self._operations[-500:]

        self._emit(
            "RUNTIME_CLUSTER_OPERATION",
            operation.to_dict(),
        )

        return operation

    def _record_failover_plan(
        self,
        plan: ClusterFailoverPlan,
    ) -> None:
        self._failover_plans.append(plan)
        self._failover_plans = self._failover_plans[-500:]

        self._emit(
            "RUNTIME_CLUSTER_FAILOVER_PLAN",
            plan.to_dict(),
        )

    def _new_plan_id(self) -> str:
        return f"CLUSTER-FAILOVER-{uuid.uuid4().hex[:12].upper()}"

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
                source="distributed_runtime_cluster_manager",
                severity=payload.get("risk_level") or payload.get("status") or "INFO",
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


_DEFAULT_DISTRIBUTED_RUNTIME_CLUSTER_MANAGER: Optional[
    DistributedRuntimeClusterManager
] = None


def get_distributed_runtime_cluster_manager(
    *,
    federation_manager: Any = None,
    domain_manager: Any = None,
    sovereign_controller: Any = None,
    registry: Any = None,
    storage: Any = None,
    event_bus: Any = None,
    reset: bool = False,
) -> DistributedRuntimeClusterManager:
    global _DEFAULT_DISTRIBUTED_RUNTIME_CLUSTER_MANAGER

    if reset or _DEFAULT_DISTRIBUTED_RUNTIME_CLUSTER_MANAGER is None:
        _DEFAULT_DISTRIBUTED_RUNTIME_CLUSTER_MANAGER = (
            DistributedRuntimeClusterManager(
                federation_manager=federation_manager,
                domain_manager=domain_manager,
                sovereign_controller=sovereign_controller,
                registry=registry,
                storage=storage,
                event_bus=event_bus,
            )
        )

    return _DEFAULT_DISTRIBUTED_RUNTIME_CLUSTER_MANAGER