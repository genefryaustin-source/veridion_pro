"""
core/runtime/autonomous_cluster_balancer.py

Autonomous Cluster Balancer.

Purpose:
- adaptive runtime fabric balancing
- sovereign-aware cluster pressure analysis
- cluster failover/rebalance recommendations
- preemptive stabilization
- autonomous fabric healing support

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


BALANCE_OK = "OK"
BALANCE_DEGRADED = "DEGRADED"
BALANCE_PRESSURE = "PRESSURE"
BALANCE_CRITICAL = "CRITICAL"

ACTION_NONE = "NONE"
ACTION_PLAN_FAILOVER = "PLAN_FAILOVER"
ACTION_DRAIN_CLUSTER = "DRAIN_CLUSTER"
ACTION_QUARANTINE_CLUSTER = "QUARANTINE_CLUSTER"
ACTION_TRIGGER_BACKPRESSURE = "TRIGGER_BACKPRESSURE"
ACTION_REDUCE_AUTONOMY = "REDUCE_AUTONOMY"
ACTION_ROUTE_TEST = "ROUTE_TEST"

DEFAULT_TENANT = "default"


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class ClusterBalanceFinding:
    finding_id: str
    finding_type: str
    severity: str
    message: str
    cluster_id: Optional[str] = None
    tenant_id: str = DEFAULT_TENANT
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ClusterBalanceAction:
    action_id: str
    action_type: str
    cluster_id: Optional[str] = None
    tenant_id: str = DEFAULT_TENANT
    reason: str = ""
    status: str = "PENDING"
    result: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)
    completed_at_ms: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ClusterBalanceAssessment:
    assessment_id: str
    tenant_id: str
    status: str
    risk_score: float
    findings: List[ClusterBalanceFinding] = field(default_factory=list)
    recommended_actions: List[ClusterBalanceAction] = field(default_factory=list)
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


class AutonomousClusterBalancer:
    def __init__(
        self,
        *,
        cluster_manager: Any = None,
        federation_manager: Any = None,
        federated_router: Any = None,
        sovereign_controller: Any = None,
        autonomy_governor: Any = None,
        backpressure_controller: Any = None,
        recovery_manager: Any = None,
        storage: Any = None,
        event_bus: Any = None,
        pressure_threshold: float = 0.75,
        critical_threshold: float = 0.90,
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
        self.autonomy_governor = (
            autonomy_governor
            or getattr(storage, "autonomy_governor_v2", None)
        )
        self.backpressure_controller = (
            backpressure_controller
            or getattr(storage, "backpressure_controller", None)
        )
        self.recovery_manager = (
            recovery_manager
            or getattr(storage, "runtime_recovery_manager", None)
        )
        self.event_bus = event_bus or getattr(storage, "event_bus", None)

        self.pressure_threshold = pressure_threshold
        self.critical_threshold = critical_threshold

        self._assessments: List[ClusterBalanceAssessment] = []
        self._actions: List[ClusterBalanceAction] = []

    # ========================================================
    # ASSESSMENT
    # ========================================================

    def assess(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        capability: Optional[str] = "execution_queue",
    ) -> ClusterBalanceAssessment:
        telemetry = self._collect_telemetry(
            tenant_id=tenant_id,
            capability=capability,
        )

        findings = self._derive_findings(
            telemetry=telemetry,
            tenant_id=tenant_id,
        )

        risk_score = self._score_risk(findings)

        status = self._status_from_score(risk_score)

        actions = self._recommend_actions(
            findings=findings,
            tenant_id=tenant_id,
            capability=capability,
            status=status,
        )

        assessment = ClusterBalanceAssessment(
            assessment_id=f"BALANCE-{uuid.uuid4().hex[:12].upper()}",
            tenant_id=tenant_id,
            status=status,
            risk_score=risk_score,
            findings=findings,
            recommended_actions=actions,
            telemetry=telemetry,
        )

        self._assessments.append(assessment)
        self._assessments = self._assessments[-500:]

        self._emit(
            "AUTONOMOUS_CLUSTER_BALANCE_ASSESSED",
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
            "AUTONOMOUS_CLUSTER_BALANCE_ENFORCED",
            result,
        )

        return result

    def _execute_action(
        self,
        action: ClusterBalanceAction,
    ) -> None:
        try:
            action.status = "RUNNING"

            if action.action_type == ACTION_PLAN_FAILOVER:
                self._plan_failover(action)

            elif action.action_type == ACTION_DRAIN_CLUSTER:
                self._drain_cluster(action)

            elif action.action_type == ACTION_QUARANTINE_CLUSTER:
                self._quarantine_cluster(action)

            elif action.action_type == ACTION_TRIGGER_BACKPRESSURE:
                self._trigger_backpressure(action)

            elif action.action_type == ACTION_REDUCE_AUTONOMY:
                self._reduce_autonomy(action)

            elif action.action_type == ACTION_ROUTE_TEST:
                self._route_test(action)

            else:
                action.status = "SKIPPED"
                action.result = {"reason": "unknown_or_noop_action"}

        except Exception as exc:
            action.status = "FAILED"
            action.result = {"error": str(exc)}

        action.completed_at_ms = _now_ms()

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
        except Exception as exc:
            telemetry["cluster_error"] = str(exc)

        try:
            if self.federation_manager is not None:
                telemetry["federation_health"] = self.federation_manager.federation_health()
                telemetry["runtimes"] = self.federation_manager.list_runtimes(
                    tenant_id=tenant_id,
                )
        except Exception as exc:
            telemetry["federation_error"] = str(exc)

        try:
            if self.federated_router is not None:
                telemetry["routing_status"] = self.federated_router.routing_status()
        except Exception as exc:
            telemetry["routing_error"] = str(exc)

        try:
            if self.autonomy_governor is not None:
                telemetry["governor_status"] = self.autonomy_governor.governor_status(
                    tenant_id=tenant_id,
                )
        except Exception as exc:
            telemetry["governor_error"] = str(exc)

        return telemetry

    # ========================================================
    # FINDINGS
    # ========================================================

    def _derive_findings(
        self,
        *,
        telemetry: Dict[str, Any],
        tenant_id: str,
    ) -> List[ClusterBalanceFinding]:
        findings: List[ClusterBalanceFinding] = []

        clusters = telemetry.get("clusters", []) or []

        for cluster in clusters:
            cluster_id = cluster.get("cluster_id")
            status = str(cluster.get("status") or "").upper()
            risk = str(cluster.get("risk_level") or "").upper()
            health = float(cluster.get("health_score", 100.0) or 100.0)

            active = float(cluster.get("active_units", 0) or 0)
            capacity = float(cluster.get("capacity_units", 1) or 1)
            load_ratio = active / max(capacity, 1.0)

            if status in {"QUARANTINED", "OFFLINE"}:
                findings.append(
                    self._finding(
                        "CLUSTER_UNAVAILABLE",
                        "CRITICAL",
                        f"Cluster {cluster_id} is unavailable.",
                        cluster_id=cluster_id,
                        tenant_id=tenant_id,
                        metadata=cluster,
                    )
                )

            elif status in {"DEGRADED", "DRAINING"} or risk in {"HIGH", "CRITICAL"}:
                findings.append(
                    self._finding(
                        "CLUSTER_DEGRADED",
                        "HIGH",
                        f"Cluster {cluster_id} is degraded.",
                        cluster_id=cluster_id,
                        tenant_id=tenant_id,
                        metadata=cluster,
                    )
                )

            if health < 65:
                findings.append(
                    self._finding(
                        "CLUSTER_HEALTH_LOW",
                        "HIGH",
                        f"Cluster {cluster_id} health is low.",
                        cluster_id=cluster_id,
                        tenant_id=tenant_id,
                        metadata={
                            "health_score": health,
                            "cluster": cluster,
                        },
                    )
                )

            if load_ratio >= self.critical_threshold:
                findings.append(
                    self._finding(
                        "CLUSTER_CAPACITY_CRITICAL",
                        "CRITICAL",
                        f"Cluster {cluster_id} is critically saturated.",
                        cluster_id=cluster_id,
                        tenant_id=tenant_id,
                        metadata={
                            "load_ratio": load_ratio,
                            "active_units": active,
                            "capacity_units": capacity,
                        },
                    )
                )

            elif load_ratio >= self.pressure_threshold:
                findings.append(
                    self._finding(
                        "CLUSTER_CAPACITY_PRESSURE",
                        "MEDIUM",
                        f"Cluster {cluster_id} is under load pressure.",
                        cluster_id=cluster_id,
                        tenant_id=tenant_id,
                        metadata={
                            "load_ratio": load_ratio,
                            "active_units": active,
                            "capacity_units": capacity,
                        },
                    )
                )

        routing = telemetry.get("routing_status", {}) or {}
        blocked = int(routing.get("blocked", 0) or 0)

        if blocked > 0:
            findings.append(
                self._finding(
                    "ROUTING_BLOCK_PRESSURE",
                    "HIGH",
                    "Federated routing has blocked decisions.",
                    tenant_id=tenant_id,
                    metadata=routing,
                )
            )

        cluster_health = telemetry.get("cluster_health", {}) or {}
        if cluster_health.get("risk") in {"HIGH", "CRITICAL"}:
            findings.append(
                self._finding(
                    "FABRIC_CLUSTER_RISK",
                    cluster_health.get("risk"),
                    "Overall cluster fabric risk is elevated.",
                    tenant_id=tenant_id,
                    metadata=cluster_health,
                )
            )

        return findings

    def _finding(
        self,
        finding_type: str,
        severity: str,
        message: str,
        *,
        cluster_id: Optional[str] = None,
        tenant_id: str = DEFAULT_TENANT,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ClusterBalanceFinding:
        return ClusterBalanceFinding(
            finding_id=f"CBF-{uuid.uuid4().hex[:12].upper()}",
            finding_type=finding_type,
            severity=severity,
            message=message,
            cluster_id=cluster_id,
            tenant_id=tenant_id,
            metadata=metadata or {},
        )

    # ========================================================
    # RISK + RECOMMENDATIONS
    # ========================================================

    def _score_risk(
        self,
        findings: List[ClusterBalanceFinding],
    ) -> float:
        score = 0.0

        weights = {
            "CLUSTER_UNAVAILABLE": 35.0,
            "CLUSTER_DEGRADED": 25.0,
            "CLUSTER_HEALTH_LOW": 20.0,
            "CLUSTER_CAPACITY_CRITICAL": 30.0,
            "CLUSTER_CAPACITY_PRESSURE": 10.0,
            "ROUTING_BLOCK_PRESSURE": 20.0,
            "FABRIC_CLUSTER_RISK": 25.0,
        }

        severity_boost = {
            "LOW": 0.0,
            "MEDIUM": 5.0,
            "HIGH": 10.0,
            "CRITICAL": 20.0,
        }

        for finding in findings:
            score += weights.get(finding.finding_type, 5.0)
            score += severity_boost.get(
                str(finding.severity).upper(),
                0.0,
            )

        return max(0.0, min(score, 100.0))

    def _status_from_score(
        self,
        risk_score: float,
    ) -> str:
        if risk_score >= 80:
            return BALANCE_CRITICAL
        if risk_score >= 55:
            return BALANCE_PRESSURE
        if risk_score >= 25:
            return BALANCE_DEGRADED
        return BALANCE_OK

    def _recommend_actions(
        self,
        *,
        findings: List[ClusterBalanceFinding],
        tenant_id: str,
        capability: Optional[str],
        status: str,
    ) -> List[ClusterBalanceAction]:
        actions: List[ClusterBalanceAction] = []
        seen = set()

        for finding in findings:
            ftype = finding.finding_type
            cluster_id = finding.cluster_id

            if ftype in {
                "CLUSTER_UNAVAILABLE",
                "CLUSTER_DEGRADED",
                "CLUSTER_HEALTH_LOW",
            }:
                self._append_action(
                    actions,
                    seen,
                    ACTION_PLAN_FAILOVER,
                    cluster_id=cluster_id,
                    tenant_id=tenant_id,
                    reason=finding.message,
                    metadata={
                        "capability": capability,
                        "finding": finding.to_dict(),
                    },
                )

            if ftype == "CLUSTER_CAPACITY_CRITICAL":
                self._append_action(
                    actions,
                    seen,
                    ACTION_TRIGGER_BACKPRESSURE,
                    cluster_id=cluster_id,
                    tenant_id=tenant_id,
                    reason="Critical cluster saturation detected.",
                    metadata={"finding": finding.to_dict()},
                )

                self._append_action(
                    actions,
                    seen,
                    ACTION_PLAN_FAILOVER,
                    cluster_id=cluster_id,
                    tenant_id=tenant_id,
                    reason="Plan failover for critically saturated cluster.",
                    metadata={
                        "capability": capability,
                        "finding": finding.to_dict(),
                    },
                )

            if ftype == "CLUSTER_CAPACITY_PRESSURE":
                self._append_action(
                    actions,
                    seen,
                    ACTION_ROUTE_TEST,
                    cluster_id=cluster_id,
                    tenant_id=tenant_id,
                    reason="Test alternate sovereign route due to load pressure.",
                    metadata={
                        "capability": capability,
                        "finding": finding.to_dict(),
                    },
                )

            if ftype == "ROUTING_BLOCK_PRESSURE":
                self._append_action(
                    actions,
                    seen,
                    ACTION_REDUCE_AUTONOMY,
                    tenant_id=tenant_id,
                    reason="Routing block pressure detected.",
                    metadata={"finding": finding.to_dict()},
                )

            if ftype == "FABRIC_CLUSTER_RISK":
                self._append_action(
                    actions,
                    seen,
                    ACTION_TRIGGER_BACKPRESSURE,
                    tenant_id=tenant_id,
                    reason="Elevated fabric cluster risk.",
                    metadata={"finding": finding.to_dict()},
                )

        if status == BALANCE_CRITICAL:
            self._append_action(
                actions,
                seen,
                ACTION_REDUCE_AUTONOMY,
                tenant_id=tenant_id,
                reason="Critical cluster balancing risk.",
            )

        return actions

    def _append_action(
        self,
        actions: List[ClusterBalanceAction],
        seen: set,
        action_type: str,
        *,
        cluster_id: Optional[str] = None,
        tenant_id: str = DEFAULT_TENANT,
        reason: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        key = (action_type, cluster_id, reason)

        if key in seen:
            return

        seen.add(key)

        actions.append(
            ClusterBalanceAction(
                action_id=f"CBA-{uuid.uuid4().hex[:12].upper()}",
                action_type=action_type,
                cluster_id=cluster_id,
                tenant_id=tenant_id,
                reason=reason,
                metadata=metadata or {},
            )
        )

    # ========================================================
    # ACTION EXECUTION
    # ========================================================

    def _plan_failover(
        self,
        action: ClusterBalanceAction,
    ) -> None:
        if self.cluster_manager is None or not action.cluster_id:
            action.status = "SKIPPED"
            action.result = {
                "reason": "cluster_manager_or_cluster_missing",
            }
            return

        capability = action.metadata.get("capability")

        plan = self.cluster_manager.plan_cluster_failover(
            source_cluster_id=action.cluster_id,
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

    def _drain_cluster(
        self,
        action: ClusterBalanceAction,
    ) -> None:
        if self.cluster_manager is None or not action.cluster_id:
            action.status = "SKIPPED"
            action.result = {
                "reason": "cluster_manager_or_cluster_missing",
            }
            return

        ok = self.cluster_manager.drain_cluster(
            action.cluster_id,
            reason=action.reason,
        )

        action.status = "COMPLETED" if ok else "FAILED"
        action.result = {"ok": ok}

    def _quarantine_cluster(
        self,
        action: ClusterBalanceAction,
    ) -> None:
        if self.cluster_manager is None or not action.cluster_id:
            action.status = "SKIPPED"
            action.result = {
                "reason": "cluster_manager_or_cluster_missing",
            }
            return

        ok = self.cluster_manager.quarantine_cluster(
            action.cluster_id,
            reason=action.reason,
        )

        action.status = "COMPLETED" if ok else "FAILED"
        action.result = {"ok": ok}

    def _trigger_backpressure(
        self,
        action: ClusterBalanceAction,
    ) -> None:
        if self.backpressure_controller is None:
            action.status = "SKIPPED"
            action.result = {
                "reason": "backpressure_controller_unavailable",
            }
            return

        decision = self.backpressure_controller.evaluate(
            tenant_id=action.tenant_id,
            context={
                "source": "autonomous_cluster_balancer",
                "reason": action.reason,
                "cluster_id": action.cluster_id,
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

    def _reduce_autonomy(
        self,
        action: ClusterBalanceAction,
    ) -> None:
        if self.autonomy_governor is None:
            action.status = "SKIPPED"
            action.result = {
                "reason": "autonomy_governor_unavailable",
            }
            return

        result = self.autonomy_governor.set_autonomy_mode(
            tenant_id=action.tenant_id,
            mode="ASSISTED",
            reason=action.reason,
        )

        action.status = "COMPLETED"
        action.result = result

    def _route_test(
        self,
        action: ClusterBalanceAction,
    ) -> None:
        if self.federated_router is None:
            action.status = "SKIPPED"
            action.result = {
                "reason": "federated_router_unavailable",
            }
            return

        capability = action.metadata.get("capability")

        decision = self.federated_router.route_workload(
            tenant_id=action.tenant_id,
            workload={
                "action": "BALANCER_ROUTE_TEST",
                "source": "autonomous_cluster_balancer",
                "cluster_id": action.cluster_id,
                "capability": capability,
            },
            capability=capability,
            dispatch_local=False,
        )

        action.status = "COMPLETED"
        action.result = {
            "route_decision": (
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

    def balancer_status(self) -> Dict[str, Any]:
        latest = self._assessments[-1].to_dict() if self._assessments else None

        return {
            "assessment_count": len(self._assessments),
            "action_count": len(self._actions),
            "pressure_threshold": self.pressure_threshold,
            "critical_threshold": self.critical_threshold,
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
                source="autonomous_cluster_balancer",
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


_DEFAULT_AUTONOMOUS_CLUSTER_BALANCER: Optional[
    AutonomousClusterBalancer
] = None


def get_autonomous_cluster_balancer(
    *,
    cluster_manager: Any = None,
    federation_manager: Any = None,
    federated_router: Any = None,
    sovereign_controller: Any = None,
    autonomy_governor: Any = None,
    backpressure_controller: Any = None,
    recovery_manager: Any = None,
    storage: Any = None,
    event_bus: Any = None,
    pressure_threshold: float = 0.75,
    critical_threshold: float = 0.90,
    reset: bool = False,
) -> AutonomousClusterBalancer:
    global _DEFAULT_AUTONOMOUS_CLUSTER_BALANCER

    if reset or _DEFAULT_AUTONOMOUS_CLUSTER_BALANCER is None:
        _DEFAULT_AUTONOMOUS_CLUSTER_BALANCER = AutonomousClusterBalancer(
            cluster_manager=cluster_manager,
            federation_manager=federation_manager,
            federated_router=federated_router,
            sovereign_controller=sovereign_controller,
            autonomy_governor=autonomy_governor,
            backpressure_controller=backpressure_controller,
            recovery_manager=recovery_manager,
            storage=storage,
            event_bus=event_bus,
            pressure_threshold=pressure_threshold,
            critical_threshold=critical_threshold,
        )

    return _DEFAULT_AUTONOMOUS_CLUSTER_BALANCER