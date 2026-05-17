"""
core/runtime/sovereign_mesh_optimizer.py

Sovereign Mesh Optimizer.

Purpose:
- global sovereign execution mesh optimization
- routing topology intelligence
- cluster/runtime placement optimization
- sovereign pressure reduction
- governance-aware optimization recommendations
- predictive fabric stabilization foundation

Architecture Rules:
- no Streamlit/session_state dependency
- no persistent SQLite connection
- no hidden global mutation
- explicit service-owned state only
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


OPTIMIZATION_HEALTHY = "HEALTHY"
OPTIMIZATION_IMPROVABLE = "IMPROVABLE"
OPTIMIZATION_DEGRADED = "DEGRADED"
OPTIMIZATION_CRITICAL = "CRITICAL"

ACTION_NONE = "NONE"
ACTION_REBALANCE_CLUSTER = "REBALANCE_CLUSTER"
ACTION_PLAN_CLUSTER_FAILOVER = "PLAN_CLUSTER_FAILOVER"
ACTION_REDUCE_CROSS_RUNTIME_ROUTING = "REDUCE_CROSS_RUNTIME_ROUTING"
ACTION_TIGHTEN_SOVEREIGN_CONTROLS = "TIGHTEN_SOVEREIGN_CONTROLS"
ACTION_TRIGGER_BALANCER = "TRIGGER_BALANCER"
ACTION_TRIGGER_GOVERNOR_ASSESSMENT = "TRIGGER_GOVERNOR_ASSESSMENT"
ACTION_TRIGGER_BACKPRESSURE = "TRIGGER_BACKPRESSURE"

DEFAULT_TENANT = "default"


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class MeshOptimizationFinding:
    finding_id: str
    finding_type: str
    severity: str
    message: str
    tenant_id: str = DEFAULT_TENANT
    target: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MeshOptimizationAction:
    action_id: str
    action_type: str
    tenant_id: str = DEFAULT_TENANT
    target: Optional[str] = None
    reason: str = ""
    status: str = "PENDING"
    result: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)
    completed_at_ms: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MeshOptimizationAssessment:
    assessment_id: str
    tenant_id: str
    status: str
    optimization_score: float
    findings: List[MeshOptimizationFinding] = field(default_factory=list)
    recommended_actions: List[MeshOptimizationAction] = field(default_factory=list)
    telemetry: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["findings"] = [
            f.to_dict() if hasattr(f, "to_dict") else f
            for f in self.findings
        ]
        data["recommended_actions"] = [
            a.to_dict() if hasattr(a, "to_dict") else a
            for a in self.recommended_actions
        ]
        return data


class SovereignMeshOptimizer:
    def __init__(
        self,
        *,
        cluster_manager: Any = None,
        federation_manager: Any = None,
        federated_router: Any = None,
        sovereign_controller: Any = None,
        domain_manager: Any = None,
        autonomy_governor: Any = None,
        cluster_balancer: Any = None,
        backpressure_controller: Any = None,
        storage: Any = None,
        event_bus: Any = None,
        cross_runtime_threshold: int = 10,
        sovereign_block_threshold: int = 5,
    ) -> None:
        self.storage = storage
        self.cluster_manager = (
            cluster_manager
            or getattr(storage, "distributed_runtime_cluster_manager", None)
        )
        self.federation_manager = (
            federation_manager
            or getattr(storage, "runtime_federation_manager", None)
        )
        self.federated_router = (
            federated_router
            or getattr(storage, "federated_execution_router", None)
        )
        self.sovereign_controller = (
            sovereign_controller
            or getattr(storage, "sovereign_execution_controller", None)
        )
        self.domain_manager = (
            domain_manager
            or getattr(storage, "execution_domain_manager", None)
        )
        self.autonomy_governor = (
            autonomy_governor
            or getattr(storage, "autonomy_governor_v2", None)
        )
        self.cluster_balancer = (
            cluster_balancer
            or getattr(storage, "autonomous_cluster_balancer", None)
        )
        self.backpressure_controller = (
            backpressure_controller
            or getattr(storage, "backpressure_controller", None)
        )
        self.event_bus = event_bus or getattr(storage, "event_bus", None)

        self.cross_runtime_threshold = cross_runtime_threshold
        self.sovereign_block_threshold = sovereign_block_threshold

        self._assessments: List[MeshOptimizationAssessment] = []
        self._actions: List[MeshOptimizationAction] = []

    # ========================================================
    # ASSESSMENT
    # ========================================================

    def assess(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        capability: Optional[str] = "execution_queue",
    ) -> MeshOptimizationAssessment:
        telemetry = self._collect_telemetry(
            tenant_id=tenant_id,
            capability=capability,
        )

        findings = self._derive_findings(
            telemetry=telemetry,
            tenant_id=tenant_id,
        )

        score = self._optimization_score(findings)

        status = self._status_from_score(score)

        actions = self._recommend_actions(
            tenant_id=tenant_id,
            capability=capability,
            status=status,
            findings=findings,
        )

        assessment = MeshOptimizationAssessment(
            assessment_id=f"MESH-OPT-{uuid.uuid4().hex[:12].upper()}",
            tenant_id=tenant_id,
            status=status,
            optimization_score=score,
            findings=findings,
            recommended_actions=actions,
            telemetry=telemetry,
        )

        self._assessments.append(assessment)
        self._assessments = self._assessments[-500:]

        self._emit(
            "SOVEREIGN_MESH_OPTIMIZATION_ASSESSED",
            assessment.to_dict(),
        )

        return assessment

    # ========================================================
    # ENFORCEMENT
    # ========================================================

    def enforce(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        capability: Optional[str] = "execution_queue",
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        assessment = self.assess(
            tenant_id=tenant_id,
            capability=capability,
        )

        executed: List[Dict[str, Any]] = []

        for action in assessment.recommended_actions:
            if dry_run:
                action.status = "DRY_RUN"
            else:
                self._execute_action(action)

            self._actions.append(action)
            self._actions = self._actions[-500:]
            executed.append(action.to_dict())

        result = {
            "ok": True,
            "dry_run": dry_run,
            "assessment": assessment.to_dict(),
            "actions": executed,
        }

        self._emit(
            "SOVEREIGN_MESH_OPTIMIZATION_ENFORCED",
            result,
        )

        return result

    # ========================================================
    # TELEMETRY
    # ========================================================

    def _collect_telemetry(
        self,
        *,
        tenant_id: str,
        capability: Optional[str],
    ) -> Dict[str, Any]:
        telemetry: Dict[str, Any] = {
            "tenant_id": tenant_id,
            "capability": capability,
            "collected_at_ms": _now_ms(),
        }

        try:
            if self.cluster_manager is not None:
                telemetry["cluster_health"] = self.cluster_manager.cluster_health()
                telemetry["clusters"] = self.cluster_manager.list_clusters(
                    tenant_id=tenant_id,
                )
                telemetry["cluster_topology"] = self.cluster_manager.cluster_topology()
                telemetry["failover_plans"] = self.cluster_manager.list_failover_plans(
                    limit=50,
                )
        except Exception as exc:
            telemetry["cluster_error"] = str(exc)

        try:
            if self.federation_manager is not None:
                telemetry["federation_health"] = self.federation_manager.federation_health()
                telemetry["runtimes"] = self.federation_manager.list_runtimes(
                    tenant_id=tenant_id,
                )
                telemetry["federation_topology"] = self.federation_manager.federation_topology()
        except Exception as exc:
            telemetry["federation_error"] = str(exc)

        try:
            if self.federated_router is not None:
                telemetry["routing_status"] = self.federated_router.routing_status()
                telemetry["route_decisions"] = self.federated_router.list_decisions(
                    limit=100,
                )
        except Exception as exc:
            telemetry["routing_error"] = str(exc)

        try:
            if self.sovereign_controller is not None:
                telemetry["sovereignty_status"] = self.sovereign_controller.sovereignty_status()
                telemetry["sovereign_decisions"] = self.sovereign_controller.list_decisions(
                    limit=100,
                )
        except Exception as exc:
            telemetry["sovereignty_error"] = str(exc)

        try:
            if self.domain_manager is not None:
                telemetry["domain_health"] = self.domain_manager.domain_health()
                telemetry["domains"] = self.domain_manager.list_domains(
                    tenant_id=tenant_id,
                )
        except Exception as exc:
            telemetry["domain_error"] = str(exc)

        try:
            if self.autonomy_governor is not None:
                telemetry["governor_status"] = self.autonomy_governor.governor_status(
                    tenant_id=tenant_id,
                )
        except Exception as exc:
            telemetry["governor_error"] = str(exc)

        try:
            if self.cluster_balancer is not None:
                telemetry["balancer_status"] = self.cluster_balancer.balancer_status()
        except Exception as exc:
            telemetry["balancer_error"] = str(exc)

        return telemetry

    # ========================================================
    # FINDINGS
    # ========================================================

    def _derive_findings(
        self,
        *,
        telemetry: Dict[str, Any],
        tenant_id: str,
    ) -> List[MeshOptimizationFinding]:
        findings: List[MeshOptimizationFinding] = []

        clusters = telemetry.get("clusters", []) or []
        for cluster in clusters:
            cluster_id = cluster.get("cluster_id")
            status = str(cluster.get("status") or "").upper()
            risk = str(cluster.get("risk_level") or "").upper()
            health = float(cluster.get("health_score", 100.0) or 100.0)

            active = float(cluster.get("active_units", 0) or 0)
            capacity = float(cluster.get("capacity_units", 1) or 1)
            load_ratio = active / max(capacity, 1.0)

            if status in {"DEGRADED", "DRAINING"} or risk in {"HIGH", "CRITICAL"}:
                findings.append(
                    self._finding(
                        "CLUSTER_OPTIMIZATION_NEEDED",
                        "HIGH",
                        f"Cluster {cluster_id} needs optimization.",
                        tenant_id=tenant_id,
                        target=cluster_id,
                        metadata=cluster,
                    )
                )

            if health < 70:
                findings.append(
                    self._finding(
                        "LOW_CLUSTER_HEALTH",
                        "HIGH",
                        f"Cluster {cluster_id} health is below optimization threshold.",
                        tenant_id=tenant_id,
                        target=cluster_id,
                        metadata={
                            "health_score": health,
                            "cluster": cluster,
                        },
                    )
                )

            if load_ratio >= 0.75:
                findings.append(
                    self._finding(
                        "CLUSTER_LOAD_IMBALANCE",
                        "MEDIUM" if load_ratio < 0.90 else "HIGH",
                        f"Cluster {cluster_id} has elevated load ratio.",
                        tenant_id=tenant_id,
                        target=cluster_id,
                        metadata={
                            "load_ratio": load_ratio,
                            "cluster": cluster,
                        },
                    )
                )

        routing = telemetry.get("routing_status", {}) or {}
        federated_routes = int(routing.get("federated_routes", 0) or 0)
        local_routes = int(routing.get("local_routes", 0) or 0)
        blocked_routes = int(routing.get("blocked", 0) or 0)

        if federated_routes > self.cross_runtime_threshold:
            findings.append(
                self._finding(
                    "CROSS_RUNTIME_ROUTE_PRESSURE",
                    "MEDIUM",
                    "Cross-runtime routing exceeds optimization threshold.",
                    tenant_id=tenant_id,
                    metadata=routing,
                )
            )

        if blocked_routes > 0:
            findings.append(
                self._finding(
                    "ROUTE_BLOCK_OPTIMIZATION_PRESSURE",
                    "HIGH",
                    "Blocked routes indicate placement or sovereignty pressure.",
                    tenant_id=tenant_id,
                    metadata=routing,
                )
            )

        sovereignty = telemetry.get("sovereignty_status", {}) or {}
        sovereign_blocks = int(sovereignty.get("blocked", 0) or 0)
        approvals = int(sovereignty.get("requires_approval", 0) or 0)

        if sovereign_blocks >= self.sovereign_block_threshold:
            findings.append(
                self._finding(
                    "SOVEREIGN_BLOCK_PRESSURE",
                    "HIGH",
                    "Sovereign execution blocks exceed optimization threshold.",
                    tenant_id=tenant_id,
                    metadata=sovereignty,
                )
            )

        if approvals >= 10:
            findings.append(
                self._finding(
                    "SOVEREIGN_APPROVAL_BOTTLENECK",
                    "MEDIUM",
                    "Sovereign approval pressure may be slowing execution.",
                    tenant_id=tenant_id,
                    metadata=sovereignty,
                )
            )

        domain_health = telemetry.get("domain_health", {}) or {}
        if domain_health.get("risk") in {"HIGH", "CRITICAL"}:
            findings.append(
                self._finding(
                    "DOMAIN_TOPOLOGY_RISK",
                    domain_health.get("risk"),
                    "Execution domain topology has elevated risk.",
                    tenant_id=tenant_id,
                    metadata=domain_health,
                )
            )

        federation_health = telemetry.get("federation_health", {}) or {}
        if federation_health.get("risk") in {"HIGH", "CRITICAL"}:
            findings.append(
                self._finding(
                    "FEDERATION_TOPOLOGY_RISK",
                    federation_health.get("risk"),
                    "Federation topology has elevated risk.",
                    tenant_id=tenant_id,
                    metadata=federation_health,
                )
            )

        balancer_status = telemetry.get("balancer_status", {}) or {}
        latest_balance = balancer_status.get("latest_assessment") or {}
        if latest_balance.get("status") in {"PRESSURE", "CRITICAL"}:
            findings.append(
                self._finding(
                    "BALANCER_PRESSURE_SIGNAL",
                    latest_balance.get("status"),
                    "Cluster balancer reports active pressure.",
                    tenant_id=tenant_id,
                    metadata=latest_balance,
                )
            )

        return findings

    def _finding(
        self,
        finding_type: str,
        severity: str,
        message: str,
        *,
        tenant_id: str = DEFAULT_TENANT,
        target: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MeshOptimizationFinding:
        return MeshOptimizationFinding(
            finding_id=f"MESH-FINDING-{uuid.uuid4().hex[:12].upper()}",
            finding_type=finding_type,
            severity=severity,
            message=message,
            tenant_id=tenant_id,
            target=target,
            metadata=metadata or {},
        )

    # ========================================================
    # SCORE + RECOMMENDATIONS
    # ========================================================

    def _optimization_score(
        self,
        findings: List[MeshOptimizationFinding],
    ) -> float:
        score = 100.0

        penalties = {
            "CLUSTER_OPTIMIZATION_NEEDED": 18.0,
            "LOW_CLUSTER_HEALTH": 18.0,
            "CLUSTER_LOAD_IMBALANCE": 12.0,
            "CROSS_RUNTIME_ROUTE_PRESSURE": 10.0,
            "ROUTE_BLOCK_OPTIMIZATION_PRESSURE": 18.0,
            "SOVEREIGN_BLOCK_PRESSURE": 22.0,
            "SOVEREIGN_APPROVAL_BOTTLENECK": 10.0,
            "DOMAIN_TOPOLOGY_RISK": 18.0,
            "FEDERATION_TOPOLOGY_RISK": 18.0,
            "BALANCER_PRESSURE_SIGNAL": 16.0,
        }

        severity_penalty = {
            "LOW": 0.0,
            "MEDIUM": 4.0,
            "HIGH": 8.0,
            "CRITICAL": 16.0,
            "PRESSURE": 6.0,
        }

        for finding in findings:
            score -= penalties.get(finding.finding_type, 5.0)
            score -= severity_penalty.get(
                str(finding.severity).upper(),
                0.0,
            )

        return max(0.0, min(score, 100.0))

    def _status_from_score(
        self,
        score: float,
    ) -> str:
        if score >= 85:
            return OPTIMIZATION_HEALTHY
        if score >= 65:
            return OPTIMIZATION_IMPROVABLE
        if score >= 35:
            return OPTIMIZATION_DEGRADED
        return OPTIMIZATION_CRITICAL

    def _recommend_actions(
        self,
        *,
        tenant_id: str,
        capability: Optional[str],
        status: str,
        findings: List[MeshOptimizationFinding],
    ) -> List[MeshOptimizationAction]:
        actions: List[MeshOptimizationAction] = []
        seen = set()

        for finding in findings:
            ftype = finding.finding_type

            if ftype in {
                "CLUSTER_OPTIMIZATION_NEEDED",
                "LOW_CLUSTER_HEALTH",
                "CLUSTER_LOAD_IMBALANCE",
                "BALANCER_PRESSURE_SIGNAL",
            }:
                self._append_action(
                    actions,
                    seen,
                    ACTION_TRIGGER_BALANCER,
                    tenant_id=tenant_id,
                    target=finding.target,
                    reason=finding.message,
                    metadata={
                        "capability": capability,
                        "finding": finding.to_dict(),
                    },
                )

            if ftype in {
                "CLUSTER_OPTIMIZATION_NEEDED",
                "LOW_CLUSTER_HEALTH",
            }:
                self._append_action(
                    actions,
                    seen,
                    ACTION_PLAN_CLUSTER_FAILOVER,
                    tenant_id=tenant_id,
                    target=finding.target,
                    reason="Plan cluster failover for unhealthy optimization target.",
                    metadata={
                        "capability": capability,
                        "finding": finding.to_dict(),
                    },
                )

            if ftype == "CROSS_RUNTIME_ROUTE_PRESSURE":
                self._append_action(
                    actions,
                    seen,
                    ACTION_REDUCE_CROSS_RUNTIME_ROUTING,
                    tenant_id=tenant_id,
                    reason="Cross-runtime routing pressure detected.",
                    metadata={
                        "capability": capability,
                        "finding": finding.to_dict(),
                    },
                )

            if ftype in {
                "SOVEREIGN_BLOCK_PRESSURE",
                "DOMAIN_TOPOLOGY_RISK",
                "SOVEREIGN_APPROVAL_BOTTLENECK",
            }:
                self._append_action(
                    actions,
                    seen,
                    ACTION_TIGHTEN_SOVEREIGN_CONTROLS,
                    tenant_id=tenant_id,
                    reason=finding.message,
                    metadata={
                        "finding": finding.to_dict(),
                    },
                )

            if ftype in {
                "FEDERATION_TOPOLOGY_RISK",
                "ROUTE_BLOCK_OPTIMIZATION_PRESSURE",
            }:
                self._append_action(
                    actions,
                    seen,
                    ACTION_TRIGGER_GOVERNOR_ASSESSMENT,
                    tenant_id=tenant_id,
                    reason=finding.message,
                    metadata={
                        "capability": capability,
                        "finding": finding.to_dict(),
                    },
                )

        if status in {
            OPTIMIZATION_DEGRADED,
            OPTIMIZATION_CRITICAL,
        }:
            self._append_action(
                actions,
                seen,
                ACTION_TRIGGER_BACKPRESSURE,
                tenant_id=tenant_id,
                reason="Mesh optimization degradation detected.",
                metadata={"status": status},
            )

        return actions

    def _append_action(
        self,
        actions: List[MeshOptimizationAction],
        seen: set,
        action_type: str,
        *,
        tenant_id: str = DEFAULT_TENANT,
        target: Optional[str] = None,
        reason: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        key = (action_type, target, reason)

        if key in seen:
            return

        seen.add(key)

        actions.append(
            MeshOptimizationAction(
                action_id=f"MESH-ACTION-{uuid.uuid4().hex[:12].upper()}",
                action_type=action_type,
                tenant_id=tenant_id,
                target=target,
                reason=reason,
                metadata=metadata or {},
            )
        )

    # ========================================================
    # ACTION EXECUTION
    # ========================================================

    def _execute_action(
        self,
        action: MeshOptimizationAction,
    ) -> None:
        try:
            action.status = "RUNNING"

            if action.action_type == ACTION_TRIGGER_BALANCER:
                self._trigger_balancer(action)

            elif action.action_type == ACTION_PLAN_CLUSTER_FAILOVER:
                self._plan_cluster_failover(action)

            elif action.action_type == ACTION_TRIGGER_GOVERNOR_ASSESSMENT:
                self._trigger_governor(action)

            elif action.action_type == ACTION_TRIGGER_BACKPRESSURE:
                self._trigger_backpressure(action)

            elif action.action_type in {
                ACTION_REDUCE_CROSS_RUNTIME_ROUTING,
                ACTION_TIGHTEN_SOVEREIGN_CONTROLS,
            }:
                action.status = "RECOMMENDED"
                action.result = {
                    "manual_or_policy_engine_action_required": True,
                    "reason": action.reason,
                }

            else:
                action.status = "SKIPPED"
                action.result = {"reason": "unknown_action"}

        except Exception as exc:
            action.status = "FAILED"
            action.result = {"error": str(exc)}

        action.completed_at_ms = _now_ms()

    def _trigger_balancer(
        self,
        action: MeshOptimizationAction,
    ) -> None:
        if self.cluster_balancer is None:
            action.status = "SKIPPED"
            action.result = {"reason": "cluster_balancer_unavailable"}
            return

        capability = action.metadata.get("capability")

        result = self.cluster_balancer.enforce(
            tenant_id=action.tenant_id,
            capability=capability,
            dry_run=True,
        )

        action.status = "COMPLETED"
        action.result = result

    def _plan_cluster_failover(
        self,
        action: MeshOptimizationAction,
    ) -> None:
        if self.cluster_manager is None or not action.target:
            action.status = "SKIPPED"
            action.result = {"reason": "cluster_manager_or_target_unavailable"}
            return

        capability = action.metadata.get("capability")

        plan = self.cluster_manager.plan_cluster_failover(
            source_cluster_id=action.target,
            tenant_id=action.tenant_id,
            capability=capability,
        )

        action.status = "COMPLETED"
        action.result = {
            "failover_plan": (
                plan.to_dict()
                if hasattr(plan, "to_dict")
                else plan
            )
        }

    def _trigger_governor(
        self,
        action: MeshOptimizationAction,
    ) -> None:
        if self.autonomy_governor is None:
            action.status = "SKIPPED"
            action.result = {"reason": "autonomy_governor_unavailable"}
            return

        capability = action.metadata.get("capability")

        assessment = self.autonomy_governor.assess(
            tenant_id=action.tenant_id,
            workload={
                "action": "MESH_OPTIMIZER_GOVERNOR_ASSESSMENT",
                "capability": capability,
                "source": "sovereign_mesh_optimizer",
            },
        )

        action.status = "COMPLETED"
        action.result = {
            "governor_assessment": (
                assessment.to_dict()
                if hasattr(assessment, "to_dict")
                else {}
            )
        }

    def _trigger_backpressure(
        self,
        action: MeshOptimizationAction,
    ) -> None:
        if self.backpressure_controller is None:
            action.status = "SKIPPED"
            action.result = {"reason": "backpressure_controller_unavailable"}
            return

        decision = self.backpressure_controller.evaluate(
            tenant_id=action.tenant_id,
            context={
                "source": "sovereign_mesh_optimizer",
                "reason": action.reason,
            },
        )

        if getattr(decision, "freeze_tenant", False):
            self.backpressure_controller.enforce_freeze_if_needed(decision)

        action.status = "COMPLETED"
        action.result = {
            "backpressure_decision": (
                decision.to_dict()
                if hasattr(decision, "to_dict")
                else {}
            )
        }

    # ========================================================
    # READS
    # ========================================================

    def list_assessments(
        self,
        *,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        assessments = sorted(
            self._assessments,
            key=lambda a: a.created_at_ms,
            reverse=True,
        )

        return [
            a.to_dict()
            for a in assessments[:limit]
        ]

    def list_actions(
        self,
        *,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        actions = sorted(
            self._actions,
            key=lambda a: a.created_at_ms,
            reverse=True,
        )

        return [
            a.to_dict()
            for a in actions[:limit]
        ]

    def optimizer_status(self) -> Dict[str, Any]:
        latest = self._assessments[-1].to_dict() if self._assessments else None

        return {
            "assessment_count": len(self._assessments),
            "action_count": len(self._actions),
            "cross_runtime_threshold": self.cross_runtime_threshold,
            "sovereign_block_threshold": self.sovereign_block_threshold,
            "latest_assessment": latest,
        }

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
                source="sovereign_mesh_optimizer",
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


_DEFAULT_SOVEREIGN_MESH_OPTIMIZER: Optional[
    SovereignMeshOptimizer
] = None


def get_sovereign_mesh_optimizer(
    *,
    cluster_manager: Any = None,
    federation_manager: Any = None,
    federated_router: Any = None,
    sovereign_controller: Any = None,
    domain_manager: Any = None,
    autonomy_governor: Any = None,
    cluster_balancer: Any = None,
    backpressure_controller: Any = None,
    storage: Any = None,
    event_bus: Any = None,
    cross_runtime_threshold: int = 10,
    sovereign_block_threshold: int = 5,
    reset: bool = False,
) -> SovereignMeshOptimizer:
    global _DEFAULT_SOVEREIGN_MESH_OPTIMIZER

    if reset or _DEFAULT_SOVEREIGN_MESH_OPTIMIZER is None:
        _DEFAULT_SOVEREIGN_MESH_OPTIMIZER = SovereignMeshOptimizer(
            cluster_manager=cluster_manager,
            federation_manager=federation_manager,
            federated_router=federated_router,
            sovereign_controller=sovereign_controller,
            domain_manager=domain_manager,
            autonomy_governor=autonomy_governor,
            cluster_balancer=cluster_balancer,
            backpressure_controller=backpressure_controller,
            storage=storage,
            event_bus=event_bus,
            cross_runtime_threshold=cross_runtime_threshold,
            sovereign_block_threshold=sovereign_block_threshold,
        )

    return _DEFAULT_SOVEREIGN_MESH_OPTIMIZER