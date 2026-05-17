"""
core/runtime/adaptive_sovereign_policy_engine.py

Adaptive Sovereign Policy Engine.

Purpose:
- sovereign policy cognition
- adaptive governance recommendations
- policy pressure modeling
- sovereign drift detection
- approval bottleneck intelligence
- relay/routing/mesh outcome learning
- policy posture recommendations

Architecture Rules:
- no Streamlit/session_state dependency
- no persistent SQLite connection
- no hidden global mutation
- service-owned state only
- recommendations before enforcement
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


POLICY_POSTURE_RELAXED = "RELAXED"
POLICY_POSTURE_BALANCED = "BALANCED"
POLICY_POSTURE_HARDENED = "HARDENED"
POLICY_POSTURE_LOCKDOWN = "LOCKDOWN"

POLICY_RISK_LOW = "LOW"
POLICY_RISK_MEDIUM = "MEDIUM"
POLICY_RISK_HIGH = "HIGH"
POLICY_RISK_CRITICAL = "CRITICAL"

ACTION_NONE = "NONE"
ACTION_TIGHTEN_SOVEREIGN_POLICY = "TIGHTEN_SOVEREIGN_POLICY"
ACTION_REQUIRE_HUMAN_APPROVAL = "REQUIRE_HUMAN_APPROVAL"
ACTION_REDUCE_AUTONOMY = "REDUCE_AUTONOMY"
ACTION_RESTRICT_RELAYS = "RESTRICT_RELAYS"
ACTION_RESTRICT_FEDERATED_ROUTING = "RESTRICT_FEDERATED_ROUTING"
ACTION_FREEZE_HIGH_RISK_DOMAINS = "FREEZE_HIGH_RISK_DOMAINS"
ACTION_RELAX_POLICY_CAUTIOUSLY = "RELAX_POLICY_CAUTIOUSLY"
ACTION_TRIGGER_GOVERNOR = "TRIGGER_GOVERNOR"
ACTION_TRIGGER_MESH_OPTIMIZER = "TRIGGER_MESH_OPTIMIZER"

DEFAULT_TENANT = "default"


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class SovereignPolicySignal:
    signal_id: str
    signal_type: str
    severity: str
    message: str
    tenant_id: str = DEFAULT_TENANT
    source: str = "adaptive_sovereign_policy_engine"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SovereignPolicyRecommendation:
    recommendation_id: str
    action: str
    priority: str
    reason: str
    tenant_id: str = DEFAULT_TENANT
    target: Optional[str] = None
    requires_approval: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SovereignPolicyAssessment:
    assessment_id: str
    tenant_id: str
    posture: str
    recommended_posture: str
    risk_level: str
    risk_score: float
    policy_pressure_score: float
    signals: List[SovereignPolicySignal] = field(default_factory=list)
    recommendations: List[SovereignPolicyRecommendation] = field(default_factory=list)
    telemetry: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["signals"] = [
            s.to_dict() if hasattr(s, "to_dict") else s
            for s in self.signals
        ]
        data["recommendations"] = [
            r.to_dict() if hasattr(r, "to_dict") else r
            for r in self.recommendations
        ]
        return data


class AdaptiveSovereignPolicyEngine:
    def __init__(
        self,
        *,
        policy_manager: Any = None,
        sovereign_controller: Any = None,
        autonomy_governor: Any = None,
        mesh_optimizer: Any = None,
        cluster_balancer: Any = None,
        execution_relay: Any = None,
        federated_router: Any = None,
        domain_manager: Any = None,
        cluster_manager: Any = None,
        recovery_manager: Any = None,
        storage: Any = None,
        event_bus: Any = None,
        default_posture: str = POLICY_POSTURE_BALANCED,
    ) -> None:
        self.storage = storage
        self.policy_manager = policy_manager or getattr(storage, "runtime_policy_manager", None)
        self.sovereign_controller = sovereign_controller or getattr(storage, "sovereign_execution_controller", None)
        self.autonomy_governor = autonomy_governor or getattr(storage, "autonomy_governor_v2", None)
        self.mesh_optimizer = mesh_optimizer or getattr(storage, "sovereign_mesh_optimizer", None)
        self.cluster_balancer = cluster_balancer or getattr(storage, "autonomous_cluster_balancer", None)
        self.execution_relay = execution_relay or getattr(storage, "cross_runtime_execution_relay", None)
        self.federated_router = federated_router or getattr(storage, "federated_execution_router", None)
        self.domain_manager = domain_manager or getattr(storage, "execution_domain_manager", None)
        self.cluster_manager = cluster_manager or getattr(storage, "distributed_runtime_cluster_manager", None)
        self.recovery_manager = recovery_manager or getattr(storage, "runtime_recovery_manager", None)
        self.event_bus = event_bus or getattr(storage, "event_bus", None)

        self.default_posture = default_posture
        self._tenant_postures: Dict[str, str] = {
            DEFAULT_TENANT: default_posture,
        }

        self._assessments: List[SovereignPolicyAssessment] = []
        self._signals: List[SovereignPolicySignal] = []
        self._recommendations: List[SovereignPolicyRecommendation] = []

    # ========================================================
    # POSTURE
    # ========================================================

    def set_policy_posture(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        posture: str,
        reason: str = "manual_update",
    ) -> Dict[str, Any]:
        self._tenant_postures[tenant_id] = posture

        payload = {
            "ok": True,
            "tenant_id": tenant_id,
            "posture": posture,
            "reason": reason,
        }

        self._emit(
            "ADAPTIVE_SOVEREIGN_POLICY_POSTURE_CHANGED",
            payload,
        )

        return payload

    def get_policy_posture(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
    ) -> str:
        return self._tenant_postures.get(
            tenant_id,
            self.default_posture,
        )

    # ========================================================
    # ASSESSMENT
    # ========================================================

    def assess(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        workload: Optional[Dict[str, Any]] = None,
    ) -> SovereignPolicyAssessment:
        workload = dict(workload or {})

        current_posture = self.get_policy_posture(
            tenant_id=tenant_id,
        )

        telemetry = self._collect_telemetry(
            tenant_id=tenant_id,
            workload=workload,
        )

        signals = self._derive_signals(
            tenant_id=tenant_id,
            telemetry=telemetry,
            workload=workload,
        )

        risk_score = self._score_policy_risk(
            signals=signals,
            telemetry=telemetry,
            workload=workload,
        )

        pressure_score = self._score_policy_pressure(
            signals=signals,
            telemetry=telemetry,
        )

        risk_level = self._risk_level(risk_score)

        recommended_posture = self._recommended_posture(
            current_posture=current_posture,
            risk_level=risk_level,
            risk_score=risk_score,
            pressure_score=pressure_score,
            signals=signals,
        )

        recommendations = self._recommendations_for(
            tenant_id=tenant_id,
            current_posture=current_posture,
            recommended_posture=recommended_posture,
            risk_level=risk_level,
            risk_score=risk_score,
            pressure_score=pressure_score,
            signals=signals,
            telemetry=telemetry,
        )

        assessment = SovereignPolicyAssessment(
            assessment_id=f"SOV-POLICY-{uuid.uuid4().hex[:12].upper()}",
            tenant_id=tenant_id,
            posture=current_posture,
            recommended_posture=recommended_posture,
            risk_level=risk_level,
            risk_score=risk_score,
            policy_pressure_score=pressure_score,
            signals=signals,
            recommendations=recommendations,
            telemetry=telemetry,
        )

        self._assessments.append(assessment)
        self._assessments = self._assessments[-500:]

        self._signals.extend(signals)
        self._signals = self._signals[-1000:]

        self._recommendations.extend(recommendations)
        self._recommendations = self._recommendations[-1000:]

        self._emit(
            "ADAPTIVE_SOVEREIGN_POLICY_ASSESSED",
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
        workload: Optional[Dict[str, Any]] = None,
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        assessment = self.assess(
            tenant_id=tenant_id,
            workload=workload or {},
        )

        actions: List[Dict[str, Any]] = []

        if not dry_run:
            if assessment.recommended_posture != assessment.posture:
                self.set_policy_posture(
                    tenant_id=tenant_id,
                    posture=assessment.recommended_posture,
                    reason="adaptive_sovereign_policy_engine_enforcement",
                )

        for rec in assessment.recommendations:
            result = {
                "recommendation_id": rec.recommendation_id,
                "action": rec.action,
                "dry_run": dry_run,
                "status": "DRY_RUN" if dry_run else "RECOMMENDED",
                "reason": rec.reason,
                "target": rec.target,
            }

            if not dry_run:
                result.update(
                    self._execute_recommendation(rec)
                )

            actions.append(result)

        payload = {
            "ok": True,
            "dry_run": dry_run,
            "assessment": assessment.to_dict(),
            "actions": actions,
        }

        self._emit(
            "ADAPTIVE_SOVEREIGN_POLICY_ENFORCED",
            payload,
        )

        return payload

    def _execute_recommendation(
        self,
        rec: SovereignPolicyRecommendation,
    ) -> Dict[str, Any]:
        try:
            if rec.action == ACTION_TRIGGER_GOVERNOR:
                return self._trigger_governor(rec)

            if rec.action == ACTION_TRIGGER_MESH_OPTIMIZER:
                return self._trigger_mesh_optimizer(rec)

            if rec.action == ACTION_FREEZE_HIGH_RISK_DOMAINS:
                return self._freeze_high_risk_domains(rec)

            if rec.action == ACTION_REDUCE_AUTONOMY:
                return self._reduce_autonomy(rec)

            if rec.action in {
                ACTION_TIGHTEN_SOVEREIGN_POLICY,
                ACTION_REQUIRE_HUMAN_APPROVAL,
                ACTION_RESTRICT_RELAYS,
                ACTION_RESTRICT_FEDERATED_ROUTING,
                ACTION_RELAX_POLICY_CAUTIOUSLY,
            }:
                return {
                    "status": "RECOMMENDED",
                    "manual_or_policy_manager_update_required": True,
                    "reason": rec.reason,
                }

            return {
                "status": "SKIPPED",
                "reason": "unknown_recommendation_action",
            }

        except Exception as exc:
            return {
                "status": "FAILED",
                "error": str(exc),
            }

    # ========================================================
    # TELEMETRY
    # ========================================================

    def _collect_telemetry(
        self,
        *,
        tenant_id: str,
        workload: Dict[str, Any],
    ) -> Dict[str, Any]:
        telemetry: Dict[str, Any] = {
            "tenant_id": tenant_id,
            "workload": workload,
            "collected_at_ms": _now_ms(),
        }

        try:
            if self.policy_manager is not None:
                telemetry["policy_status"] = self.policy_manager.policy_status()
        except Exception as exc:
            telemetry["policy_error"] = str(exc)

        try:
            if self.sovereign_controller is not None:
                telemetry["sovereignty_status"] = self.sovereign_controller.sovereignty_status()
                telemetry["sovereign_decisions"] = self.sovereign_controller.list_decisions(
                    limit=100,
                )
        except Exception as exc:
            telemetry["sovereignty_error"] = str(exc)

        try:
            if self.autonomy_governor is not None:
                telemetry["governor_status"] = self.autonomy_governor.governor_status(
                    tenant_id=tenant_id,
                )
                telemetry["governor_assessments"] = self.autonomy_governor.list_assessments(
                    limit=50,
                )
        except Exception as exc:
            telemetry["governor_error"] = str(exc)

        try:
            if self.mesh_optimizer is not None:
                telemetry["mesh_status"] = self.mesh_optimizer.optimizer_status()
                telemetry["mesh_assessments"] = self.mesh_optimizer.list_assessments(
                    limit=50,
                )
        except Exception as exc:
            telemetry["mesh_error"] = str(exc)

        try:
            if self.cluster_balancer is not None:
                telemetry["balancer_status"] = self.cluster_balancer.balancer_status()
                telemetry["balancer_assessments"] = self.cluster_balancer.list_assessments(
                    limit=50,
                )
        except Exception as exc:
            telemetry["balancer_error"] = str(exc)

        try:
            if self.execution_relay is not None:
                telemetry["relay_status"] = self.execution_relay.relay_status()
                telemetry["relays"] = self.execution_relay.list_relays(
                    limit=50,
                )
                telemetry["relay_results"] = self.execution_relay.list_results(
                    limit=50,
                )
        except Exception as exc:
            telemetry["relay_error"] = str(exc)

        try:
            if self.federated_router is not None:
                telemetry["routing_status"] = self.federated_router.routing_status()
                telemetry["route_decisions"] = self.federated_router.list_decisions(
                    limit=100,
                )
        except Exception as exc:
            telemetry["routing_error"] = str(exc)

        try:
            if self.domain_manager is not None:
                telemetry["domain_health"] = self.domain_manager.domain_health()
                telemetry["domains"] = self.domain_manager.list_domains(
                    tenant_id=tenant_id,
                )
        except Exception as exc:
            telemetry["domain_error"] = str(exc)

        try:
            if self.cluster_manager is not None:
                telemetry["cluster_health"] = self.cluster_manager.cluster_health()
                telemetry["clusters"] = self.cluster_manager.list_clusters(
                    tenant_id=tenant_id,
                )
        except Exception as exc:
            telemetry["cluster_error"] = str(exc)

        return telemetry

    # ========================================================
    # SIGNALS
    # ========================================================

    def _derive_signals(
        self,
        *,
        tenant_id: str,
        telemetry: Dict[str, Any],
        workload: Dict[str, Any],
    ) -> List[SovereignPolicySignal]:
        signals: List[SovereignPolicySignal] = []

        policy_status = telemetry.get("policy_status", {}) or {}
        violations = int(policy_status.get("violation_count", 0) or 0)

        if violations:
            signals.append(
                self._signal(
                    "POLICY_VIOLATION_PRESSURE",
                    "HIGH",
                    "Runtime policy violations detected.",
                    tenant_id=tenant_id,
                    source="runtime_policy_manager",
                    metadata=policy_status,
                )
            )

        sovereignty = telemetry.get("sovereignty_status", {}) or {}
        sovereign_blocks = int(sovereignty.get("blocked", 0) or 0)
        approvals = int(sovereignty.get("requires_approval", 0) or 0)

        if sovereign_blocks:
            signals.append(
                self._signal(
                    "SOVEREIGN_BLOCK_PRESSURE",
                    "HIGH",
                    "Sovereign execution blocks detected.",
                    tenant_id=tenant_id,
                    source="sovereign_execution_controller",
                    metadata=sovereignty,
                )
            )

        if approvals >= 5:
            signals.append(
                self._signal(
                    "SOVEREIGN_APPROVAL_BOTTLENECK",
                    "MEDIUM",
                    "Sovereign approval pressure detected.",
                    tenant_id=tenant_id,
                    source="sovereign_execution_controller",
                    metadata=sovereignty,
                )
            )

        relay_status = telemetry.get("relay_status", {}) or {}
        relay_failed = int(relay_status.get("failed", 0) or 0)
        relay_blocked = int(relay_status.get("blocked", 0) or 0)

        if relay_failed:
            signals.append(
                self._signal(
                    "RELAY_FAILURE_PRESSURE",
                    "HIGH",
                    "Cross-runtime relay failures detected.",
                    tenant_id=tenant_id,
                    source="cross_runtime_execution_relay",
                    metadata=relay_status,
                )
            )

        if relay_blocked:
            signals.append(
                self._signal(
                    "RELAY_BLOCK_PRESSURE",
                    "MEDIUM",
                    "Cross-runtime relay blocks detected.",
                    tenant_id=tenant_id,
                    source="cross_runtime_execution_relay",
                    metadata=relay_status,
                )
            )

        routing = telemetry.get("routing_status", {}) or {}
        route_blocked = int(routing.get("blocked", 0) or 0)
        federated_routes = int(routing.get("federated_routes", 0) or 0)

        if route_blocked:
            signals.append(
                self._signal(
                    "ROUTE_BLOCK_PRESSURE",
                    "HIGH",
                    "Federated route blocks detected.",
                    tenant_id=tenant_id,
                    source="federated_execution_router",
                    metadata=routing,
                )
            )

        if federated_routes >= 10:
            signals.append(
                self._signal(
                    "CROSS_RUNTIME_ROUTING_PRESSURE",
                    "MEDIUM",
                    "Cross-runtime routing volume is elevated.",
                    tenant_id=tenant_id,
                    source="federated_execution_router",
                    metadata=routing,
                )
            )

        domain_health = telemetry.get("domain_health", {}) or {}
        if domain_health.get("risk") in {"HIGH", "CRITICAL"}:
            signals.append(
                self._signal(
                    "DOMAIN_POLICY_RISK",
                    domain_health.get("risk"),
                    "Execution domain risk is elevated.",
                    tenant_id=tenant_id,
                    source="execution_domain_manager",
                    metadata=domain_health,
                )
            )

        cluster_health = telemetry.get("cluster_health", {}) or {}
        if cluster_health.get("risk") in {"HIGH", "CRITICAL"}:
            signals.append(
                self._signal(
                    "CLUSTER_POLICY_RISK",
                    cluster_health.get("risk"),
                    "Cluster risk may require sovereign policy adaptation.",
                    tenant_id=tenant_id,
                    source="distributed_runtime_cluster_manager",
                    metadata=cluster_health,
                )
            )

        categories = {
            str(c).upper()
            for c in workload.get("categories", [])
        }

        if categories.intersection(
            {
                "CLASSIFIED",
                "EXPORT_CONTROLLED",
                "EXPORT_CONTROL",
                "ITAR",
                "CUI",
            }
        ):
            signals.append(
                self._signal(
                    "HIGH_SENSITIVITY_WORKLOAD_POLICY_SIGNAL",
                    "HIGH",
                    "High-sensitivity workload requires tighter sovereign policy posture.",
                    tenant_id=tenant_id,
                    source="workload_classifier",
                    metadata={
                        "categories": sorted(categories),
                    },
                )
            )

        return signals

    def _signal(
        self,
        signal_type: str,
        severity: str,
        message: str,
        *,
        tenant_id: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SovereignPolicySignal:
        return SovereignPolicySignal(
            signal_id=f"SOV-SIGNAL-{uuid.uuid4().hex[:12].upper()}",
            signal_type=signal_type,
            severity=severity,
            message=message,
            tenant_id=tenant_id,
            source=source,
            metadata=metadata or {},
        )

    # ========================================================
    # RISK / PRESSURE
    # ========================================================

    def _score_policy_risk(
        self,
        *,
        signals: List[SovereignPolicySignal],
        telemetry: Dict[str, Any],
        workload: Dict[str, Any],
    ) -> float:
        score = 0.0

        weights = {
            "POLICY_VIOLATION_PRESSURE": 25.0,
            "SOVEREIGN_BLOCK_PRESSURE": 25.0,
            "SOVEREIGN_APPROVAL_BOTTLENECK": 10.0,
            "RELAY_FAILURE_PRESSURE": 20.0,
            "RELAY_BLOCK_PRESSURE": 12.0,
            "ROUTE_BLOCK_PRESSURE": 18.0,
            "CROSS_RUNTIME_ROUTING_PRESSURE": 10.0,
            "DOMAIN_POLICY_RISK": 22.0,
            "CLUSTER_POLICY_RISK": 16.0,
            "HIGH_SENSITIVITY_WORKLOAD_POLICY_SIGNAL": 20.0,
        }

        severity_boost = {
            "LOW": 0.0,
            "MEDIUM": 5.0,
            "HIGH": 10.0,
            "CRITICAL": 20.0,
        }

        for signal in signals:
            score += weights.get(signal.signal_type, 5.0)
            score += severity_boost.get(
                str(signal.severity).upper(),
                0.0,
            )

        return max(0.0, min(score, 100.0))

    def _score_policy_pressure(
        self,
        *,
        signals: List[SovereignPolicySignal],
        telemetry: Dict[str, Any],
    ) -> float:
        pressure = 0.0

        sovereignty = telemetry.get("sovereignty_status", {}) or {}
        relay = telemetry.get("relay_status", {}) or {}
        routing = telemetry.get("routing_status", {}) or {}

        pressure += min(float(sovereignty.get("blocked", 0) or 0) * 8.0, 30.0)
        pressure += min(float(sovereignty.get("requires_approval", 0) or 0) * 3.0, 20.0)
        pressure += min(float(relay.get("failed", 0) or 0) * 8.0, 20.0)
        pressure += min(float(routing.get("blocked", 0) or 0) * 6.0, 20.0)

        pressure += min(len(signals) * 4.0, 30.0)

        return max(0.0, min(pressure, 100.0))

    def _risk_level(
        self,
        score: float,
    ) -> str:
        if score >= 80:
            return POLICY_RISK_CRITICAL
        if score >= 55:
            return POLICY_RISK_HIGH
        if score >= 25:
            return POLICY_RISK_MEDIUM
        return POLICY_RISK_LOW

    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    def _recommended_posture(
        self,
        *,
        current_posture: str,
        risk_level: str,
        risk_score: float,
        pressure_score: float,
        signals: List[SovereignPolicySignal],
    ) -> str:
        signal_types = {s.signal_type for s in signals}

        if risk_level == POLICY_RISK_CRITICAL:
            return POLICY_POSTURE_LOCKDOWN

        if risk_level == POLICY_RISK_HIGH:
            return POLICY_POSTURE_HARDENED

        if pressure_score >= 50:
            return POLICY_POSTURE_HARDENED

        if risk_level == POLICY_RISK_LOW and pressure_score < 10:
            if current_posture == POLICY_POSTURE_HARDENED:
                return POLICY_POSTURE_BALANCED

        if "HIGH_SENSITIVITY_WORKLOAD_POLICY_SIGNAL" in signal_types:
            return POLICY_POSTURE_HARDENED

        return current_posture

    def _recommendations_for(
        self,
        *,
        tenant_id: str,
        current_posture: str,
        recommended_posture: str,
        risk_level: str,
        risk_score: float,
        pressure_score: float,
        signals: List[SovereignPolicySignal],
        telemetry: Dict[str, Any],
    ) -> List[SovereignPolicyRecommendation]:
        recs: List[SovereignPolicyRecommendation] = []
        seen = set()

        signal_types = {s.signal_type for s in signals}

        if recommended_posture != current_posture:
            action = (
                ACTION_RELAX_POLICY_CAUTIOUSLY
                if recommended_posture == POLICY_POSTURE_BALANCED
                else ACTION_TIGHTEN_SOVEREIGN_POLICY
            )

            self._append_rec(
                recs,
                seen,
                action=action,
                priority=risk_level,
                tenant_id=tenant_id,
                reason=(
                    f"Policy posture should shift from "
                    f"{current_posture} to {recommended_posture}."
                ),
                metadata={
                    "current_posture": current_posture,
                    "recommended_posture": recommended_posture,
                    "risk_score": risk_score,
                    "pressure_score": pressure_score,
                },
            )

        if signal_types.intersection(
            {
                "SOVEREIGN_BLOCK_PRESSURE",
                "HIGH_SENSITIVITY_WORKLOAD_POLICY_SIGNAL",
                "DOMAIN_POLICY_RISK",
            }
        ):
            self._append_rec(
                recs,
                seen,
                action=ACTION_REQUIRE_HUMAN_APPROVAL,
                priority="HIGH",
                tenant_id=tenant_id,
                reason="Require human approval for high-risk sovereign execution.",
            )

        if signal_types.intersection(
            {
                "RELAY_FAILURE_PRESSURE",
                "RELAY_BLOCK_PRESSURE",
            }
        ):
            self._append_rec(
                recs,
                seen,
                action=ACTION_RESTRICT_RELAYS,
                priority="HIGH",
                tenant_id=tenant_id,
                reason="Restrict cross-runtime relays until relay reliability improves.",
            )

        if signal_types.intersection(
            {
                "CROSS_RUNTIME_ROUTING_PRESSURE",
                "ROUTE_BLOCK_PRESSURE",
            }
        ):
            self._append_rec(
                recs,
                seen,
                action=ACTION_RESTRICT_FEDERATED_ROUTING,
                priority="MEDIUM",
                tenant_id=tenant_id,
                reason="Restrict or optimize federated routing due to route pressure.",
            )

        if signal_types.intersection(
            {
                "DOMAIN_POLICY_RISK",
            }
        ):
            self._append_rec(
                recs,
                seen,
                action=ACTION_FREEZE_HIGH_RISK_DOMAINS,
                priority="HIGH",
                tenant_id=tenant_id,
                reason="High-risk domains should be frozen or reviewed.",
            )

        if risk_level in {
            POLICY_RISK_HIGH,
            POLICY_RISK_CRITICAL,
        }:
            self._append_rec(
                recs,
                seen,
                action=ACTION_REDUCE_AUTONOMY,
                priority=risk_level,
                tenant_id=tenant_id,
                reason="Reduce autonomy under elevated sovereign policy risk.",
            )

            self._append_rec(
                recs,
                seen,
                action=ACTION_TRIGGER_GOVERNOR,
                priority=risk_level,
                tenant_id=tenant_id,
                reason="Trigger autonomy governor reassessment.",
            )

        if signal_types.intersection(
            {
                "CLUSTER_POLICY_RISK",
                "ROUTE_BLOCK_PRESSURE",
                "CROSS_RUNTIME_ROUTING_PRESSURE",
            }
        ):
            self._append_rec(
                recs,
                seen,
                action=ACTION_TRIGGER_MESH_OPTIMIZER,
                priority="MEDIUM",
                tenant_id=tenant_id,
                reason="Trigger mesh optimizer to reduce policy pressure.",
            )

        return recs

    def _append_rec(
        self,
        recs: List[SovereignPolicyRecommendation],
        seen: set,
        *,
        action: str,
        priority: str,
        tenant_id: str,
        reason: str,
        target: Optional[str] = None,
        requires_approval: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        key = (action, target, reason)

        if key in seen:
            return

        seen.add(key)

        recs.append(
            SovereignPolicyRecommendation(
                recommendation_id=f"SOV-REC-{uuid.uuid4().hex[:12].upper()}",
                action=action,
                priority=priority,
                reason=reason,
                tenant_id=tenant_id,
                target=target,
                requires_approval=requires_approval,
                metadata=metadata or {},
            )
        )

    # ========================================================
    # EXECUTION HELPERS
    # ========================================================

    def _trigger_governor(
        self,
        rec: SovereignPolicyRecommendation,
    ) -> Dict[str, Any]:
        if self.autonomy_governor is None:
            return {
                "status": "SKIPPED",
                "reason": "autonomy_governor_unavailable",
            }

        assessment = self.autonomy_governor.assess(
            tenant_id=rec.tenant_id,
            workload={
                "action": "ADAPTIVE_POLICY_ENGINE_GOVERNOR_ASSESSMENT",
                "source": "adaptive_sovereign_policy_engine",
            },
        )

        return {
            "status": "COMPLETED",
            "assessment": (
                assessment.to_dict()
                if hasattr(assessment, "to_dict")
                else {}
            ),
        }

    def _trigger_mesh_optimizer(
        self,
        rec: SovereignPolicyRecommendation,
    ) -> Dict[str, Any]:
        if self.mesh_optimizer is None:
            return {
                "status": "SKIPPED",
                "reason": "sovereign_mesh_optimizer_unavailable",
            }

        assessment = self.mesh_optimizer.assess(
            tenant_id=rec.tenant_id,
            capability="execution_queue",
        )

        return {
            "status": "COMPLETED",
            "assessment": (
                assessment.to_dict()
                if hasattr(assessment, "to_dict")
                else {}
            ),
        }

    def _freeze_high_risk_domains(
        self,
        rec: SovereignPolicyRecommendation,
    ) -> Dict[str, Any]:
        if self.domain_manager is None:
            return {
                "status": "SKIPPED",
                "reason": "domain_manager_unavailable",
            }

        domains = self.domain_manager.list_domains(
            tenant_id=rec.tenant_id,
        )

        risky = [
            d for d in domains
            if d.get("status") in {"DEGRADED", "QUARANTINED"}
            or d.get("domain_type") in {"CLASSIFIED", "EXPORT_CONTROLLED"}
        ]

        frozen = []

        for domain in risky:
            domain_id = domain.get("domain_id")
            if not domain_id:
                continue

            ok = self.domain_manager.freeze_domain(
                domain_id,
                reason=rec.reason,
            )

            frozen.append({
                "domain_id": domain_id,
                "ok": ok,
            })

        return {
            "status": "COMPLETED",
            "frozen": frozen,
        }

    def _reduce_autonomy(
        self,
        rec: SovereignPolicyRecommendation,
    ) -> Dict[str, Any]:
        if self.autonomy_governor is None:
            return {
                "status": "SKIPPED",
                "reason": "autonomy_governor_unavailable",
            }

        result = self.autonomy_governor.set_autonomy_mode(
            tenant_id=rec.tenant_id,
            mode="ASSISTED",
            reason=rec.reason,
        )

        return {
            "status": "COMPLETED",
            "result": result,
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

    def list_signals(
        self,
        *,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        signals = sorted(
            self._signals,
            key=lambda s: s.created_at_ms,
            reverse=True,
        )

        return [
            s.to_dict()
            for s in signals[:limit]
        ]

    def list_recommendations(
        self,
        *,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        recs = sorted(
            self._recommendations,
            key=lambda r: r.created_at_ms,
            reverse=True,
        )

        return [
            r.to_dict()
            for r in recs[:limit]
        ]

    def policy_engine_status(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
    ) -> Dict[str, Any]:
        latest = self._assessments[-1].to_dict() if self._assessments else None

        return {
            "default_posture": self.default_posture,
            "tenant_posture": self.get_policy_posture(tenant_id=tenant_id),
            "assessment_count": len(self._assessments),
            "signal_count": len(self._signals),
            "recommendation_count": len(self._recommendations),
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
                source="adaptive_sovereign_policy_engine",
                severity=payload.get("risk_level") or "INFO",
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


_DEFAULT_ADAPTIVE_SOVEREIGN_POLICY_ENGINE: Optional[
    AdaptiveSovereignPolicyEngine
] = None


def get_adaptive_sovereign_policy_engine(
    *,
    policy_manager: Any = None,
    sovereign_controller: Any = None,
    autonomy_governor: Any = None,
    mesh_optimizer: Any = None,
    cluster_balancer: Any = None,
    execution_relay: Any = None,
    federated_router: Any = None,
    domain_manager: Any = None,
    cluster_manager: Any = None,
    recovery_manager: Any = None,
    storage: Any = None,
    event_bus: Any = None,
    default_posture: str = POLICY_POSTURE_BALANCED,
    reset: bool = False,
) -> AdaptiveSovereignPolicyEngine:
    global _DEFAULT_ADAPTIVE_SOVEREIGN_POLICY_ENGINE

    if reset or _DEFAULT_ADAPTIVE_SOVEREIGN_POLICY_ENGINE is None:
        _DEFAULT_ADAPTIVE_SOVEREIGN_POLICY_ENGINE = AdaptiveSovereignPolicyEngine(
            policy_manager=policy_manager,
            sovereign_controller=sovereign_controller,
            autonomy_governor=autonomy_governor,
            mesh_optimizer=mesh_optimizer,
            cluster_balancer=cluster_balancer,
            execution_relay=execution_relay,
            federated_router=federated_router,
            domain_manager=domain_manager,
            cluster_manager=cluster_manager,
            recovery_manager=recovery_manager,
            storage=storage,
            event_bus=event_bus,
            default_posture=default_posture,
        )

    return _DEFAULT_ADAPTIVE_SOVEREIGN_POLICY_ENGINE