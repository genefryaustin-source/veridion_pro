"""
core/runtime/sovereignty_decision_engine.py

Sovereignty Decision Engine.

Purpose:
- sovereign operational reasoning
- decision fusion across policy, routing, relay, mesh, and governance signals
- confidence-scored sovereign decisions
- operational impact/blast-radius estimation
- decision memory for future learning

Architecture Rules:
- no Streamlit/session_state dependency
- no persistent SQLite connection
- no hidden global mutation
- service-owned decision state only
- recommendations before destructive enforcement
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


DECISION_OBSERVE = "OBSERVE"
DECISION_REDUCE_AUTONOMY = "REDUCE_AUTONOMY"
DECISION_REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
DECISION_RESTRICT_RELAYS = "RESTRICT_RELAYS"
DECISION_RESTRICT_FEDERATED_ROUTING = "RESTRICT_FEDERATED_ROUTING"
DECISION_TRIGGER_MESH_OPTIMIZATION = "TRIGGER_MESH_OPTIMIZATION"
DECISION_TRIGGER_BALANCER = "TRIGGER_BALANCER"
DECISION_TRIGGER_POLICY_ASSESSMENT = "TRIGGER_POLICY_ASSESSMENT"
DECISION_TRIGGER_RECOVERY = "TRIGGER_RECOVERY"
DECISION_QUARANTINE_DOMAIN = "QUARANTINE_DOMAIN"
DECISION_QUARANTINE_CLUSTER = "QUARANTINE_CLUSTER"
DECISION_LOCKDOWN = "LOCKDOWN"

RISK_LOW = "LOW"
RISK_MEDIUM = "MEDIUM"
RISK_HIGH = "HIGH"
RISK_CRITICAL = "CRITICAL"

IMPACT_LOW = "LOW"
IMPACT_MEDIUM = "MEDIUM"
IMPACT_HIGH = "HIGH"
IMPACT_CRITICAL = "CRITICAL"

STATUS_PROPOSED = "PROPOSED"
STATUS_DRY_RUN = "DRY_RUN"
STATUS_EXECUTED = "EXECUTED"
STATUS_FAILED = "FAILED"
STATUS_SKIPPED = "SKIPPED"

DEFAULT_TENANT = "default"


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class SovereigntySignal:
    signal_id: str
    signal_type: str
    severity: str
    message: str
    source: str
    tenant_id: str = DEFAULT_TENANT
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SovereigntyDecision:
    decision_id: str
    tenant_id: str
    decision_type: str
    risk_level: str
    confidence: float
    reason: str
    status: str = STATUS_PROPOSED
    blast_radius: str = IMPACT_LOW
    governance_impact: str = IMPACT_LOW
    sovereign_impact: str = IMPACT_LOW
    operational_impact: str = IMPACT_LOW
    target: Optional[str] = None
    recommended_actions: List[Dict[str, Any]] = field(default_factory=list)
    supporting_signals: List[Dict[str, Any]] = field(default_factory=list)
    telemetry: Dict[str, Any] = field(default_factory=dict)
    result: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)
    executed_at_ms: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SovereigntyDecisionAssessment:
    assessment_id: str
    tenant_id: str
    risk_level: str
    confidence: float
    summary: str
    signals: List[SovereigntySignal] = field(default_factory=list)
    decisions: List[SovereigntyDecision] = field(default_factory=list)
    telemetry: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["signals"] = [
            s.to_dict() if hasattr(s, "to_dict") else s
            for s in self.signals
        ]
        data["decisions"] = [
            d.to_dict() if hasattr(d, "to_dict") else d
            for d in self.decisions
        ]
        return data


class SovereigntyDecisionEngine:
    def __init__(
        self,
        *,
        policy_engine: Any = None,
        autonomy_governor: Any = None,
        mesh_optimizer: Any = None,
        cluster_balancer: Any = None,
        execution_relay: Any = None,
        sovereign_controller: Any = None,
        federated_router: Any = None,
        domain_manager: Any = None,
        cluster_manager: Any = None,
        federation_manager: Any = None,
        recovery_manager: Any = None,
        backpressure_controller: Any = None,
        storage: Any = None,
        event_bus: Any = None,
    ) -> None:
        self.storage = storage
        self.policy_engine = policy_engine or getattr(storage, "adaptive_sovereign_policy_engine", None)
        self.autonomy_governor = autonomy_governor or getattr(storage, "autonomy_governor_v2", None)
        self.mesh_optimizer = mesh_optimizer or getattr(storage, "sovereign_mesh_optimizer", None)
        self.cluster_balancer = cluster_balancer or getattr(storage, "autonomous_cluster_balancer", None)
        self.execution_relay = execution_relay or getattr(storage, "cross_runtime_execution_relay", None)
        self.sovereign_controller = sovereign_controller or getattr(storage, "sovereign_execution_controller", None)
        self.federated_router = federated_router or getattr(storage, "federated_execution_router", None)
        self.domain_manager = domain_manager or getattr(storage, "execution_domain_manager", None)
        self.cluster_manager = cluster_manager or getattr(storage, "distributed_runtime_cluster_manager", None)
        self.federation_manager = federation_manager or getattr(storage, "runtime_federation_manager", None)
        self.recovery_manager = recovery_manager or getattr(storage, "runtime_recovery_manager", None)
        self.backpressure_controller = backpressure_controller or getattr(storage, "backpressure_controller", None)
        self.event_bus = event_bus or getattr(storage, "event_bus", None)

        self._assessments: List[SovereigntyDecisionAssessment] = []
        self._signals: List[SovereigntySignal] = []
        self._decisions: List[SovereigntyDecision] = []

    # ========================================================
    # MAIN REASONING
    # ========================================================

    def assess(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        workload: Optional[Dict[str, Any]] = None,
    ) -> SovereigntyDecisionAssessment:
        workload = dict(workload or {})

        telemetry = self._collect_telemetry(
            tenant_id=tenant_id,
            workload=workload,
        )

        signals = self._derive_signals(
            tenant_id=tenant_id,
            telemetry=telemetry,
            workload=workload,
        )

        risk_score = self._score_signals(signals)
        risk_level = self._risk_level(risk_score)
        confidence = self._confidence(signals, telemetry)

        decisions = self._fuse_decisions(
            tenant_id=tenant_id,
            risk_level=risk_level,
            risk_score=risk_score,
            confidence=confidence,
            signals=signals,
            telemetry=telemetry,
        )

        summary = self._summary(
            risk_level=risk_level,
            confidence=confidence,
            signals=signals,
            decisions=decisions,
        )

        assessment = SovereigntyDecisionAssessment(
            assessment_id=f"SOV-DEC-ASSESS-{uuid.uuid4().hex[:12].upper()}",
            tenant_id=tenant_id,
            risk_level=risk_level,
            confidence=confidence,
            summary=summary,
            signals=signals,
            decisions=decisions,
            telemetry=telemetry,
        )

        self._assessments.append(assessment)
        self._assessments = self._assessments[-500:]

        self._signals.extend(signals)
        self._signals = self._signals[-1000:]

        self._decisions.extend(decisions)
        self._decisions = self._decisions[-1000:]

        self._emit(
            "SOVEREIGNTY_DECISION_ASSESSED",
            assessment.to_dict(),
        )

        return assessment

    # ========================================================
    # EXECUTION
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

        executed: List[Dict[str, Any]] = []

        for decision in assessment.decisions:
            if dry_run:
                decision.status = STATUS_DRY_RUN
                decision.result = {
                    "dry_run": True,
                    "message": "Decision not executed.",
                }
            else:
                self._execute_decision(decision)

            executed.append(decision.to_dict())

        payload = {
            "ok": True,
            "dry_run": dry_run,
            "assessment": assessment.to_dict(),
            "executed": executed,
        }

        self._emit(
            "SOVEREIGNTY_DECISION_ENFORCED",
            payload,
        )

        return payload

    def _execute_decision(
        self,
        decision: SovereigntyDecision,
    ) -> None:
        try:
            if decision.decision_type == DECISION_TRIGGER_POLICY_ASSESSMENT:
                decision.result = self._trigger_policy(decision)

            elif decision.decision_type == DECISION_TRIGGER_MESH_OPTIMIZATION:
                decision.result = self._trigger_mesh(decision)

            elif decision.decision_type == DECISION_TRIGGER_BALANCER:
                decision.result = self._trigger_balancer(decision)

            elif decision.decision_type == DECISION_REDUCE_AUTONOMY:
                decision.result = self._reduce_autonomy(decision)

            elif decision.decision_type == DECISION_TRIGGER_RECOVERY:
                decision.result = self._trigger_recovery(decision)

            elif decision.decision_type == DECISION_QUARANTINE_DOMAIN:
                decision.result = self._quarantine_domain(decision)

            elif decision.decision_type == DECISION_QUARANTINE_CLUSTER:
                decision.result = self._quarantine_cluster(decision)

            elif decision.decision_type in {
                DECISION_REQUIRE_APPROVAL,
                DECISION_RESTRICT_RELAYS,
                DECISION_RESTRICT_FEDERATED_ROUTING,
                DECISION_LOCKDOWN,
                DECISION_OBSERVE,
            }:
                decision.result = {
                    "status": "RECOMMENDED",
                    "manual_or_policy_update_required": True,
                    "decision_type": decision.decision_type,
                }

            else:
                decision.result = {
                    "status": STATUS_SKIPPED,
                    "reason": "unknown_decision_type",
                }

            decision.status = STATUS_EXECUTED
            decision.executed_at_ms = _now_ms()

        except Exception as exc:
            decision.status = STATUS_FAILED
            decision.result = {
                "error": str(exc),
            }
            decision.executed_at_ms = _now_ms()

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

        def capture(key: str, fn) -> None:
            try:
                telemetry[key] = fn()
            except Exception as exc:
                telemetry[f"{key}_error"] = str(exc)

        if self.policy_engine is not None:
            capture(
                "policy_engine_status",
                lambda: self.policy_engine.policy_engine_status(
                    tenant_id=tenant_id,
                ),
            )
            capture(
                "policy_assessments",
                lambda: self.policy_engine.list_assessments(limit=50),
            )

        if self.autonomy_governor is not None:
            capture(
                "governor_status",
                lambda: self.autonomy_governor.governor_status(
                    tenant_id=tenant_id,
                ),
            )

        if self.mesh_optimizer is not None:
            capture(
                "mesh_status",
                lambda: self.mesh_optimizer.optimizer_status(),
            )

        if self.cluster_balancer is not None:
            capture(
                "balancer_status",
                lambda: self.cluster_balancer.balancer_status(),
            )

        if self.execution_relay is not None:
            capture(
                "relay_status",
                lambda: self.execution_relay.relay_status(),
            )

        if self.sovereign_controller is not None:
            capture(
                "sovereignty_status",
                lambda: self.sovereign_controller.sovereignty_status(),
            )
            capture(
                "sovereign_decisions",
                lambda: self.sovereign_controller.list_decisions(limit=100),
            )

        if self.federated_router is not None:
            capture(
                "routing_status",
                lambda: self.federated_router.routing_status(),
            )

        if self.domain_manager is not None:
            capture(
                "domain_health",
                lambda: self.domain_manager.domain_health(),
            )

        if self.cluster_manager is not None:
            capture(
                "cluster_health",
                lambda: self.cluster_manager.cluster_health(),
            )

        if self.federation_manager is not None:
            capture(
                "federation_health",
                lambda: self.federation_manager.federation_health(),
            )

        return telemetry

    # ========================================================
    # SIGNAL DERIVATION
    # ========================================================

    def _derive_signals(
        self,
        *,
        tenant_id: str,
        telemetry: Dict[str, Any],
        workload: Dict[str, Any],
    ) -> List[SovereigntySignal]:
        signals: List[SovereigntySignal] = []

        self._add_status_signal(
            signals,
            tenant_id,
            telemetry.get("policy_engine_status", {}),
            status_key="tenant_posture",
            risky_values={"HARDENED", "LOCKDOWN"},
            signal_type="POLICY_POSTURE_PRESSURE",
            source="adaptive_sovereign_policy_engine",
        )

        sovereignty = telemetry.get("sovereignty_status", {}) or {}
        if int(sovereignty.get("blocked", 0) or 0) > 0:
            signals.append(
                self._signal(
                    "SOVEREIGN_BLOCKS_ACTIVE",
                    RISK_HIGH,
                    "Sovereign blocks are active.",
                    "sovereign_execution_controller",
                    tenant_id,
                    weight=1.4,
                    metadata=sovereignty,
                )
            )

        if int(sovereignty.get("requires_approval", 0) or 0) >= 5:
            signals.append(
                self._signal(
                    "APPROVAL_PRESSURE_ACTIVE",
                    RISK_MEDIUM,
                    "Sovereign approval pressure is elevated.",
                    "sovereign_execution_controller",
                    tenant_id,
                    weight=1.0,
                    metadata=sovereignty,
                )
            )

        routing = telemetry.get("routing_status", {}) or {}
        if int(routing.get("blocked", 0) or 0) > 0:
            signals.append(
                self._signal(
                    "ROUTE_BLOCKS_ACTIVE",
                    RISK_HIGH,
                    "Federated route blocks are active.",
                    "federated_execution_router",
                    tenant_id,
                    weight=1.3,
                    metadata=routing,
                )
            )

        if int(routing.get("federated_routes", 0) or 0) >= 10:
            signals.append(
                self._signal(
                    "CROSS_RUNTIME_ROUTE_PRESSURE",
                    RISK_MEDIUM,
                    "Cross-runtime routing pressure is elevated.",
                    "federated_execution_router",
                    tenant_id,
                    weight=0.9,
                    metadata=routing,
                )
            )

        relay = telemetry.get("relay_status", {}) or {}
        if int(relay.get("failed", 0) or 0) > 0:
            signals.append(
                self._signal(
                    "RELAY_FAILURES_ACTIVE",
                    RISK_HIGH,
                    "Execution relay failures are active.",
                    "cross_runtime_execution_relay",
                    tenant_id,
                    weight=1.3,
                    metadata=relay,
                )
            )

        if int(relay.get("blocked", 0) or 0) > 0:
            signals.append(
                self._signal(
                    "RELAY_BLOCKS_ACTIVE",
                    RISK_MEDIUM,
                    "Execution relay blocks are active.",
                    "cross_runtime_execution_relay",
                    tenant_id,
                    weight=1.0,
                    metadata=relay,
                )
            )

        for key, signal_type, source in [
            ("domain_health", "DOMAIN_HEALTH_RISK", "execution_domain_manager"),
            ("cluster_health", "CLUSTER_HEALTH_RISK", "distributed_runtime_cluster_manager"),
            ("federation_health", "FEDERATION_HEALTH_RISK", "runtime_federation_manager"),
        ]:
            health = telemetry.get(key, {}) or {}
            risk = health.get("risk")
            if risk in {RISK_HIGH, RISK_CRITICAL}:
                signals.append(
                    self._signal(
                        signal_type,
                        risk,
                        f"{source} reports elevated risk.",
                        source,
                        tenant_id,
                        weight=1.2,
                        metadata=health,
                    )
                )

        for key, signal_type, source in [
            ("mesh_status", "MESH_OPTIMIZATION_PRESSURE", "sovereign_mesh_optimizer"),
            ("balancer_status", "BALANCER_PRESSURE", "autonomous_cluster_balancer"),
            ("governor_status", "AUTONOMY_GOVERNANCE_PRESSURE", "autonomy_governor_v2"),
        ]:
            latest = (telemetry.get(key, {}) or {}).get("latest_assessment") or {}
            risk = latest.get("risk_level") or latest.get("status")
            if risk in {RISK_HIGH, RISK_CRITICAL, "DEGRADED", "PRESSURE", "CRITICAL"}:
                signals.append(
                    self._signal(
                        signal_type,
                        RISK_HIGH if risk != RISK_CRITICAL else RISK_CRITICAL,
                        f"{source} reports pressure.",
                        source,
                        tenant_id,
                        weight=1.1,
                        metadata=latest,
                    )
                )

        categories = {
            str(c).upper()
            for c in workload.get("categories", [])
        }

        if categories.intersection({"CLASSIFIED", "EXPORT_CONTROLLED", "ITAR", "CUI"}):
            signals.append(
                self._signal(
                    "HIGH_SENSITIVITY_DECISION_CONTEXT",
                    RISK_HIGH,
                    "High-sensitivity workload affects sovereign decision posture.",
                    "workload_context",
                    tenant_id,
                    weight=1.1,
                    metadata={"categories": sorted(categories)},
                )
            )

        return signals

    def _add_status_signal(
        self,
        signals: List[SovereigntySignal],
        tenant_id: str,
        status: Dict[str, Any],
        *,
        status_key: str,
        risky_values: set,
        signal_type: str,
        source: str,
    ) -> None:
        value = str(status.get(status_key) or "").upper()
        if value in risky_values:
            signals.append(
                self._signal(
                    signal_type,
                    RISK_MEDIUM if value != "LOCKDOWN" else RISK_CRITICAL,
                    f"{source} status indicates {value}.",
                    source,
                    tenant_id,
                    weight=1.0,
                    metadata=status,
                )
            )

    def _signal(
        self,
        signal_type: str,
        severity: str,
        message: str,
        source: str,
        tenant_id: str,
        *,
        weight: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SovereigntySignal:
        return SovereigntySignal(
            signal_id=f"SOV-SIGNAL-{uuid.uuid4().hex[:12].upper()}",
            signal_type=signal_type,
            severity=severity,
            message=message,
            source=source,
            tenant_id=tenant_id,
            weight=weight,
            metadata=metadata or {},
        )

    # ========================================================
    # DECISION FUSION
    # ========================================================

    def _fuse_decisions(
        self,
        *,
        tenant_id: str,
        risk_level: str,
        risk_score: float,
        confidence: float,
        signals: List[SovereigntySignal],
        telemetry: Dict[str, Any],
    ) -> List[SovereigntyDecision]:
        decisions: List[SovereigntyDecision] = []
        signal_types = {s.signal_type for s in signals}

        def add(decision_type: str, reason: str, *, target: Optional[str] = None) -> None:
            decisions.append(
                self._decision(
                    tenant_id=tenant_id,
                    decision_type=decision_type,
                    risk_level=risk_level,
                    confidence=confidence,
                    reason=reason,
                    target=target,
                    signals=signals,
                    telemetry=telemetry,
                )
            )

        if not signals:
            add(
                DECISION_OBSERVE,
                "No elevated sovereign operational pressure detected.",
            )
            return decisions

        if risk_level == RISK_CRITICAL:
            add(
                DECISION_LOCKDOWN,
                "Critical sovereign operational risk detected.",
            )
            add(
                DECISION_REDUCE_AUTONOMY,
                "Reduce autonomy under critical sovereign risk.",
            )

        if signal_types.intersection({
            "SOVEREIGN_BLOCKS_ACTIVE",
            "HIGH_SENSITIVITY_DECISION_CONTEXT",
            "DOMAIN_HEALTH_RISK",
        }):
            add(
                DECISION_REQUIRE_APPROVAL,
                "Require approval due to sovereign/domain sensitivity.",
            )

        if signal_types.intersection({
            "RELAY_FAILURES_ACTIVE",
            "RELAY_BLOCKS_ACTIVE",
        }):
            add(
                DECISION_RESTRICT_RELAYS,
                "Restrict cross-runtime relays due to relay pressure.",
            )

        if signal_types.intersection({
            "ROUTE_BLOCKS_ACTIVE",
            "CROSS_RUNTIME_ROUTE_PRESSURE",
        }):
            add(
                DECISION_RESTRICT_FEDERATED_ROUTING,
                "Restrict or optimize federated routing due to route pressure.",
            )

        if signal_types.intersection({
            "MESH_OPTIMIZATION_PRESSURE",
            "FEDERATION_HEALTH_RISK",
            "ROUTE_BLOCKS_ACTIVE",
        }):
            add(
                DECISION_TRIGGER_MESH_OPTIMIZATION,
                "Trigger mesh optimization due to topology/routing pressure.",
            )

        if signal_types.intersection({
            "BALANCER_PRESSURE",
            "CLUSTER_HEALTH_RISK",
        }):
            add(
                DECISION_TRIGGER_BALANCER,
                "Trigger cluster balancer due to fabric pressure.",
            )

        if signal_types.intersection({
            "POLICY_POSTURE_PRESSURE",
            "SOVEREIGN_BLOCKS_ACTIVE",
            "APPROVAL_PRESSURE_ACTIVE",
        }):
            add(
                DECISION_TRIGGER_POLICY_ASSESSMENT,
                "Trigger adaptive policy assessment due to governance pressure.",
            )

        if signal_types.intersection({
            "CLUSTER_HEALTH_RISK",
            "FEDERATION_HEALTH_RISK",
        }):
            add(
                DECISION_TRIGGER_RECOVERY,
                "Trigger recovery due to infrastructure health risk.",
            )

        if signal_types.intersection({"DOMAIN_HEALTH_RISK"}):
            add(
                DECISION_QUARANTINE_DOMAIN,
                "Quarantine or review high-risk sovereign execution domain.",
            )

        if signal_types.intersection({"CLUSTER_HEALTH_RISK"}):
            add(
                DECISION_QUARANTINE_CLUSTER,
                "Quarantine or review high-risk runtime cluster.",
            )

        if risk_level in {RISK_HIGH, RISK_CRITICAL}:
            add(
                DECISION_REDUCE_AUTONOMY,
                "Reduce autonomy under elevated sovereign operational risk.",
            )

        return self._dedupe_decisions(decisions)

    def _decision(
        self,
        *,
        tenant_id: str,
        decision_type: str,
        risk_level: str,
        confidence: float,
        reason: str,
        target: Optional[str],
        signals: List[SovereigntySignal],
        telemetry: Dict[str, Any],
    ) -> SovereigntyDecision:
        impact = self._impact_for(decision_type, risk_level)

        return SovereigntyDecision(
            decision_id=f"SOV-DEC-{uuid.uuid4().hex[:12].upper()}",
            tenant_id=tenant_id,
            decision_type=decision_type,
            risk_level=risk_level,
            confidence=confidence,
            reason=reason,
            blast_radius=impact.get("blast_radius", IMPACT_LOW),
            governance_impact=impact.get("governance_impact", IMPACT_LOW),
            sovereign_impact=impact.get("sovereign_impact", IMPACT_LOW),
            operational_impact=impact.get("operational_impact", IMPACT_LOW),
            target=target,
            recommended_actions=self._recommended_actions_for(decision_type),
            supporting_signals=[s.to_dict() for s in signals],
            telemetry={
                "signal_count": len(signals),
                "telemetry_keys": sorted(telemetry.keys()),
            },
        )

    def _dedupe_decisions(
        self,
        decisions: List[SovereigntyDecision],
    ) -> List[SovereigntyDecision]:
        seen = set()
        output = []

        priority = {
            DECISION_LOCKDOWN: 100,
            DECISION_QUARANTINE_DOMAIN: 90,
            DECISION_QUARANTINE_CLUSTER: 90,
            DECISION_REDUCE_AUTONOMY: 80,
            DECISION_REQUIRE_APPROVAL: 70,
            DECISION_RESTRICT_RELAYS: 65,
            DECISION_RESTRICT_FEDERATED_ROUTING: 65,
            DECISION_TRIGGER_RECOVERY: 60,
            DECISION_TRIGGER_MESH_OPTIMIZATION: 50,
            DECISION_TRIGGER_BALANCER: 45,
            DECISION_TRIGGER_POLICY_ASSESSMENT: 40,
            DECISION_OBSERVE: 10,
        }

        for d in sorted(
            decisions,
            key=lambda x: priority.get(x.decision_type, 0),
            reverse=True,
        ):
            key = (d.decision_type, d.target)
            if key in seen:
                continue
            seen.add(key)
            output.append(d)

        return output

    # ========================================================
    # SCORING
    # ========================================================

    def _score_signals(
        self,
        signals: List[SovereigntySignal],
    ) -> float:
        severity = {
            RISK_LOW: 5.0,
            RISK_MEDIUM: 15.0,
            RISK_HIGH: 30.0,
            RISK_CRITICAL: 50.0,
        }

        score = 0.0

        for signal in signals:
            score += severity.get(str(signal.severity).upper(), 10.0) * float(signal.weight or 1.0)

        return max(0.0, min(score, 100.0))

    def _risk_level(
        self,
        score: float,
    ) -> str:
        if score >= 80:
            return RISK_CRITICAL
        if score >= 55:
            return RISK_HIGH
        if score >= 25:
            return RISK_MEDIUM
        return RISK_LOW

    def _confidence(
        self,
        signals: List[SovereigntySignal],
        telemetry: Dict[str, Any],
    ) -> float:
        signal_component = min(len(signals) * 0.08, 0.50)
        telemetry_component = min(len([k for k in telemetry.keys() if not k.endswith("_error")]) * 0.04, 0.40)
        error_penalty = min(len([k for k in telemetry.keys() if k.endswith("_error")]) * 0.05, 0.30)

        confidence = 0.35 + signal_component + telemetry_component - error_penalty

        return round(max(0.05, min(confidence, 0.98)), 3)

    def _impact_for(
        self,
        decision_type: str,
        risk_level: str,
    ) -> Dict[str, str]:
        if decision_type == DECISION_LOCKDOWN:
            return {
                "blast_radius": IMPACT_CRITICAL,
                "governance_impact": IMPACT_CRITICAL,
                "sovereign_impact": IMPACT_CRITICAL,
                "operational_impact": IMPACT_CRITICAL,
            }

        if decision_type in {
            DECISION_QUARANTINE_DOMAIN,
            DECISION_QUARANTINE_CLUSTER,
            DECISION_RESTRICT_RELAYS,
            DECISION_RESTRICT_FEDERATED_ROUTING,
        }:
            return {
                "blast_radius": IMPACT_HIGH,
                "governance_impact": IMPACT_HIGH,
                "sovereign_impact": IMPACT_HIGH,
                "operational_impact": IMPACT_MEDIUM,
            }

        if decision_type in {
            DECISION_REDUCE_AUTONOMY,
            DECISION_REQUIRE_APPROVAL,
            DECISION_TRIGGER_RECOVERY,
        }:
            return {
                "blast_radius": IMPACT_MEDIUM,
                "governance_impact": IMPACT_HIGH,
                "sovereign_impact": IMPACT_MEDIUM,
                "operational_impact": IMPACT_MEDIUM,
            }

        return {
            "blast_radius": IMPACT_LOW,
            "governance_impact": IMPACT_LOW,
            "sovereign_impact": IMPACT_LOW,
            "operational_impact": IMPACT_LOW,
        }

    def _recommended_actions_for(
        self,
        decision_type: str,
    ) -> List[Dict[str, Any]]:
        return [
            {
                "action": decision_type,
                "requires_approval": decision_type in {
                    DECISION_LOCKDOWN,
                    DECISION_QUARANTINE_DOMAIN,
                    DECISION_QUARANTINE_CLUSTER,
                    DECISION_RESTRICT_RELAYS,
                    DECISION_RESTRICT_FEDERATED_ROUTING,
                },
            }
        ]

    def _summary(
        self,
        *,
        risk_level: str,
        confidence: float,
        signals: List[SovereigntySignal],
        decisions: List[SovereigntyDecision],
    ) -> str:
        if not signals:
            return "Sovereign operations appear stable; observation recommended."

        return (
            f"{len(signals)} sovereign signals produced "
            f"{len(decisions)} fused decisions. "
            f"Risk={risk_level}, confidence={confidence}."
        )

    # ========================================================
    # EXECUTION HELPERS
    # ========================================================

    def _trigger_policy(
        self,
        decision: SovereigntyDecision,
    ) -> Dict[str, Any]:
        if self.policy_engine is None:
            return {"status": STATUS_SKIPPED, "reason": "policy_engine_unavailable"}

        result = self.policy_engine.enforce(
            tenant_id=decision.tenant_id,
            workload={
                "action": "SOVEREIGNTY_DECISION_POLICY_TRIGGER",
                "decision_id": decision.decision_id,
            },
            dry_run=True,
        )

        return {"status": STATUS_EXECUTED, "result": result}

    def _trigger_mesh(
        self,
        decision: SovereigntyDecision,
    ) -> Dict[str, Any]:
        if self.mesh_optimizer is None:
            return {"status": STATUS_SKIPPED, "reason": "mesh_optimizer_unavailable"}

        result = self.mesh_optimizer.enforce(
            tenant_id=decision.tenant_id,
            dry_run=True,
        )

        return {"status": STATUS_EXECUTED, "result": result}

    def _trigger_balancer(
        self,
        decision: SovereigntyDecision,
    ) -> Dict[str, Any]:
        if self.cluster_balancer is None:
            return {"status": STATUS_SKIPPED, "reason": "cluster_balancer_unavailable"}

        result = self.cluster_balancer.enforce(
            tenant_id=decision.tenant_id,
            dry_run=True,
        )

        return {"status": STATUS_EXECUTED, "result": result}

    def _reduce_autonomy(
        self,
        decision: SovereigntyDecision,
    ) -> Dict[str, Any]:
        if self.autonomy_governor is None:
            return {"status": STATUS_SKIPPED, "reason": "autonomy_governor_unavailable"}

        result = self.autonomy_governor.set_autonomy_mode(
            tenant_id=decision.tenant_id,
            mode="ASSISTED",
            reason=decision.reason,
        )

        return {"status": STATUS_EXECUTED, "result": result}

    def _trigger_recovery(
        self,
        decision: SovereigntyDecision,
    ) -> Dict[str, Any]:
        if self.recovery_manager is None:
            return {"status": STATUS_SKIPPED, "reason": "recovery_manager_unavailable"}

        result = self.recovery_manager.auto_recover(
            tenant_id=decision.tenant_id,
            actor="sovereignty_decision_engine",
            force=False,
        )

        return {
            "status": STATUS_EXECUTED,
            "result": result.to_dict() if hasattr(result, "to_dict") else {},
        }

    def _quarantine_domain(
        self,
        decision: SovereigntyDecision,
    ) -> Dict[str, Any]:
        if self.domain_manager is None:
            return {"status": STATUS_SKIPPED, "reason": "domain_manager_unavailable"}

        return {
            "status": "RECOMMENDED",
            "reason": "Domain quarantine requires explicit target selection.",
        }

    def _quarantine_cluster(
        self,
        decision: SovereigntyDecision,
    ) -> Dict[str, Any]:
        if self.cluster_manager is None:
            return {"status": STATUS_SKIPPED, "reason": "cluster_manager_unavailable"}

        return {
            "status": "RECOMMENDED",
            "reason": "Cluster quarantine requires explicit target selection.",
        }

    # ========================================================
    # READS
    # ========================================================

    def list_assessments(
        self,
        *,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        rows = sorted(
            self._assessments,
            key=lambda a: a.created_at_ms,
            reverse=True,
        )
        return [r.to_dict() for r in rows[:limit]]

    def list_signals(
        self,
        *,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        rows = sorted(
            self._signals,
            key=lambda s: s.created_at_ms,
            reverse=True,
        )
        return [r.to_dict() for r in rows[:limit]]

    def list_decisions(
        self,
        *,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        rows = sorted(
            self._decisions,
            key=lambda d: d.created_at_ms,
            reverse=True,
        )
        return [r.to_dict() for r in rows[:limit]]

    def decision_engine_status(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
    ) -> Dict[str, Any]:
        latest = self._assessments[-1].to_dict() if self._assessments else None

        return {
            "tenant_id": tenant_id,
            "assessment_count": len(self._assessments),
            "signal_count": len(self._signals),
            "decision_count": len(self._decisions),
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
                source="sovereignty_decision_engine",
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


_DEFAULT_SOVEREIGNTY_DECISION_ENGINE: Optional[
    SovereigntyDecisionEngine
] = None


def get_sovereignty_decision_engine(
    *,
    policy_engine: Any = None,
    autonomy_governor: Any = None,
    mesh_optimizer: Any = None,
    cluster_balancer: Any = None,
    execution_relay: Any = None,
    sovereign_controller: Any = None,
    federated_router: Any = None,
    domain_manager: Any = None,
    cluster_manager: Any = None,
    federation_manager: Any = None,
    recovery_manager: Any = None,
    backpressure_controller: Any = None,
    storage: Any = None,
    event_bus: Any = None,
    reset: bool = False,
) -> SovereigntyDecisionEngine:
    global _DEFAULT_SOVEREIGNTY_DECISION_ENGINE

    if reset or _DEFAULT_SOVEREIGNTY_DECISION_ENGINE is None:
        _DEFAULT_SOVEREIGNTY_DECISION_ENGINE = SovereigntyDecisionEngine(
            policy_engine=policy_engine,
            autonomy_governor=autonomy_governor,
            mesh_optimizer=mesh_optimizer,
            cluster_balancer=cluster_balancer,
            execution_relay=execution_relay,
            sovereign_controller=sovereign_controller,
            federated_router=federated_router,
            domain_manager=domain_manager,
            cluster_manager=cluster_manager,
            federation_manager=federation_manager,
            recovery_manager=recovery_manager,
            backpressure_controller=backpressure_controller,
            storage=storage,
            event_bus=event_bus,
        )

    return _DEFAULT_SOVEREIGNTY_DECISION_ENGINE