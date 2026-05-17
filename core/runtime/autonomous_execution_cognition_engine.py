"""
core/runtime/autonomous_execution_cognition_engine.py

Autonomous Execution Cognition Engine.

Purpose:
- runtime cognition fusion
- unified operational cognition across sovereignty, learning, prediction,
  routing, relay, balancing, mesh optimization, and governance engines
- cascading failure cognition
- execution chain / continuity cognition
- cognitive recommendations before enforcement

Architecture Rules:
- no Streamlit/session_state dependency
- no persistent SQLite connection
- no hidden global mutation
- service-owned cognition memory only
- recommendations before destructive action
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


COGNITION_STABLE = "STABLE"
COGNITION_WATCH = "WATCH"
COGNITION_DEGRADED = "DEGRADED"
COGNITION_UNSTABLE = "UNSTABLE"
COGNITION_CRITICAL = "CRITICAL"

COGNITION_LOW = "LOW"
COGNITION_MEDIUM = "MEDIUM"
COGNITION_HIGH = "HIGH"
COGNITION_CRITICAL_RISK = "CRITICAL"

ACTION_OBSERVE = "OBSERVE"
ACTION_REDUCE_AUTONOMY = "REDUCE_AUTONOMY"
ACTION_REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
ACTION_RESTRICT_RELAYS = "RESTRICT_RELAYS"
ACTION_RESTRICT_FEDERATED_ROUTING = "RESTRICT_FEDERATED_ROUTING"
ACTION_TRIGGER_POLICY_ENGINE = "TRIGGER_POLICY_ENGINE"
ACTION_TRIGGER_DECISION_ENGINE = "TRIGGER_DECISION_ENGINE"
ACTION_TRIGGER_PREDICTIVE_ENGINE = "TRIGGER_PREDICTIVE_ENGINE"
ACTION_TRIGGER_MESH_OPTIMIZER = "TRIGGER_MESH_OPTIMIZER"
ACTION_TRIGGER_CLUSTER_BALANCER = "TRIGGER_CLUSTER_BALANCER"
ACTION_TRIGGER_LEARNING_INGEST = "TRIGGER_LEARNING_INGEST"
ACTION_TRIGGER_RECOVERY = "TRIGGER_RECOVERY"
ACTION_PRESERVE_CONTINUITY = "PRESERVE_CONTINUITY"
ACTION_ESCALATE_GOVERNANCE = "ESCALATE_GOVERNANCE"

DEFAULT_TENANT = "default"


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class ExecutionCognitionSignal:
    signal_id: str
    signal_type: str
    severity: str
    source: str
    message: str
    tenant_id: str = DEFAULT_TENANT
    target: Optional[str] = None
    confidence: float = 0.5
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ExecutionCognitionRecommendation:
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
class ExecutionCognitionAssessment:
    assessment_id: str
    tenant_id: str
    cognition_state: str
    risk_level: str
    cognition_score: float
    confidence: float
    survivability_score: float
    continuity_score: float
    summary: str
    signals: List[ExecutionCognitionSignal] = field(default_factory=list)
    recommendations: List[ExecutionCognitionRecommendation] = field(default_factory=list)
    cascade_model: Dict[str, Any] = field(default_factory=dict)
    execution_chain_model: Dict[str, Any] = field(default_factory=dict)
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


class AutonomousExecutionCognitionEngine:
    def __init__(
        self,
        *,
        sovereignty_decision_engine: Any = None,
        predictive_engine: Any = None,
        learning_engine: Any = None,
        adaptive_policy_engine: Any = None,
        mesh_optimizer: Any = None,
        cluster_balancer: Any = None,
        execution_relay: Any = None,
        federated_router: Any = None,
        sovereign_controller: Any = None,
        cluster_manager: Any = None,
        domain_manager: Any = None,
        federation_manager: Any = None,
        recovery_manager: Any = None,
        autonomy_governor: Any = None,
        storage: Any = None,
        event_bus: Any = None,
    ) -> None:
        self.storage = storage

        self.sovereignty_decision_engine = (
            sovereignty_decision_engine
            or getattr(storage, "sovereignty_decision_engine", None)
        )
        self.predictive_engine = (
            predictive_engine
            or getattr(storage, "predictive_runtime_stability_engine", None)
        )
        self.learning_engine = (
            learning_engine
            or getattr(storage, "runtime_fabric_learning_engine", None)
        )
        self.adaptive_policy_engine = (
            adaptive_policy_engine
            or getattr(storage, "adaptive_sovereign_policy_engine", None)
        )
        self.mesh_optimizer = (
            mesh_optimizer
            or getattr(storage, "sovereign_mesh_optimizer", None)
        )
        self.cluster_balancer = (
            cluster_balancer
            or getattr(storage, "autonomous_cluster_balancer", None)
        )
        self.execution_relay = (
            execution_relay
            or getattr(storage, "cross_runtime_execution_relay", None)
        )
        self.federated_router = (
            federated_router
            or getattr(storage, "federated_execution_router", None)
        )
        self.sovereign_controller = (
            sovereign_controller
            or getattr(storage, "sovereign_execution_controller", None)
        )
        self.cluster_manager = (
            cluster_manager
            or getattr(storage, "distributed_runtime_cluster_manager", None)
        )
        self.domain_manager = (
            domain_manager
            or getattr(storage, "execution_domain_manager", None)
        )
        self.federation_manager = (
            federation_manager
            or getattr(storage, "runtime_federation_manager", None)
        )
        self.recovery_manager = (
            recovery_manager
            or getattr(storage, "runtime_recovery_manager", None)
        )
        self.autonomy_governor = (
            autonomy_governor
            or getattr(storage, "autonomy_governor_v2", None)
        )
        self.event_bus = event_bus or getattr(storage, "event_bus", None)

        self._assessments: List[ExecutionCognitionAssessment] = []
        self._signals: List[ExecutionCognitionSignal] = []
        self._recommendations: List[ExecutionCognitionRecommendation] = []

    # ========================================================
    # MAIN COGNITION
    # ========================================================

    def assess(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        workload: Optional[Dict[str, Any]] = None,
    ) -> ExecutionCognitionAssessment:
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

        cascade_model = self._build_cascade_model(
            signals=signals,
            telemetry=telemetry,
        )

        execution_chain_model = self._build_execution_chain_model(
            tenant_id=tenant_id,
            workload=workload,
            telemetry=telemetry,
            signals=signals,
        )

        cognition_score = self._cognition_score(
            signals=signals,
            cascade_model=cascade_model,
        )

        risk_level = self._risk_level(cognition_score)

        cognition_state = self._cognition_state(
            score=cognition_score,
            signals=signals,
        )

        confidence = self._confidence(
            signals=signals,
            telemetry=telemetry,
        )

        survivability_score = self._survivability_score(
            telemetry=telemetry,
            signals=signals,
            execution_chain_model=execution_chain_model,
        )

        continuity_score = self._continuity_score(
            telemetry=telemetry,
            signals=signals,
            execution_chain_model=execution_chain_model,
        )

        recommendations = self._recommendations_for(
            tenant_id=tenant_id,
            risk_level=risk_level,
            cognition_state=cognition_state,
            survivability_score=survivability_score,
            continuity_score=continuity_score,
            signals=signals,
            cascade_model=cascade_model,
            execution_chain_model=execution_chain_model,
        )

        summary = self._summary(
            cognition_state=cognition_state,
            risk_level=risk_level,
            confidence=confidence,
            signal_count=len(signals),
            recommendation_count=len(recommendations),
            survivability_score=survivability_score,
            continuity_score=continuity_score,
        )

        assessment = ExecutionCognitionAssessment(
            assessment_id=f"EXEC-COG-{uuid.uuid4().hex[:12].upper()}",
            tenant_id=tenant_id,
            cognition_state=cognition_state,
            risk_level=risk_level,
            cognition_score=cognition_score,
            confidence=confidence,
            survivability_score=survivability_score,
            continuity_score=continuity_score,
            summary=summary,
            signals=signals,
            recommendations=recommendations,
            cascade_model=cascade_model,
            execution_chain_model=execution_chain_model,
            telemetry=telemetry,
        )

        self._assessments.append(assessment)
        self._assessments = self._assessments[-500:]

        self._signals.extend(signals)
        self._signals = self._signals[-1500:]

        self._recommendations.extend(recommendations)
        self._recommendations = self._recommendations[-1500:]

        self._emit(
            "AUTONOMOUS_EXECUTION_COGNITION_ASSESSED",
            assessment.to_dict(),
        )

        return assessment

    # ========================================================
    # ENFORCEMENT / ORCHESTRATION
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

        actions = []

        for rec in assessment.recommendations:
            if dry_run:
                actions.append({
                    "recommendation_id": rec.recommendation_id,
                    "action": rec.action,
                    "status": "DRY_RUN",
                    "reason": rec.reason,
                    "target": rec.target,
                })
            else:
                actions.append(
                    self._execute_recommendation(rec)
                )

        payload = {
            "ok": True,
            "dry_run": dry_run,
            "assessment": assessment.to_dict(),
            "actions": actions,
        }

        self._emit(
            "AUTONOMOUS_EXECUTION_COGNITION_ENFORCED",
            payload,
        )

        return payload

    def _execute_recommendation(
        self,
        rec: ExecutionCognitionRecommendation,
    ) -> Dict[str, Any]:
        try:
            if rec.action == ACTION_TRIGGER_LEARNING_INGEST:
                return self._trigger_learning_ingest(rec)

            if rec.action == ACTION_TRIGGER_PREDICTIVE_ENGINE:
                return self._trigger_predictive_engine(rec)

            if rec.action == ACTION_TRIGGER_DECISION_ENGINE:
                return self._trigger_decision_engine(rec)

            if rec.action == ACTION_TRIGGER_POLICY_ENGINE:
                return self._trigger_policy_engine(rec)

            if rec.action == ACTION_TRIGGER_MESH_OPTIMIZER:
                return self._trigger_mesh_optimizer(rec)

            if rec.action == ACTION_TRIGGER_CLUSTER_BALANCER:
                return self._trigger_cluster_balancer(rec)

            if rec.action == ACTION_TRIGGER_RECOVERY:
                return self._trigger_recovery(rec)

            if rec.action == ACTION_REDUCE_AUTONOMY:
                return self._reduce_autonomy(rec)

            if rec.action in {
                ACTION_REQUIRE_APPROVAL,
                ACTION_RESTRICT_RELAYS,
                ACTION_RESTRICT_FEDERATED_ROUTING,
                ACTION_PRESERVE_CONTINUITY,
                ACTION_ESCALATE_GOVERNANCE,
                ACTION_OBSERVE,
            }:
                return {
                    "recommendation_id": rec.recommendation_id,
                    "action": rec.action,
                    "status": "RECOMMENDED",
                    "manual_or_policy_update_required": True,
                    "reason": rec.reason,
                }

            return {
                "recommendation_id": rec.recommendation_id,
                "action": rec.action,
                "status": "SKIPPED",
                "reason": "unknown_recommendation_action",
            }

        except Exception as exc:
            return {
                "recommendation_id": rec.recommendation_id,
                "action": rec.action,
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

        def capture(key: str, fn) -> None:
            try:
                telemetry[key] = fn()
            except Exception as exc:
                telemetry[f"{key}_error"] = str(exc)

        if self.sovereignty_decision_engine is not None:
            capture(
                "sovereignty_decision_status",
                lambda: self.sovereignty_decision_engine.decision_engine_status(
                    tenant_id=tenant_id,
                ),
            )
            capture(
                "sovereignty_decisions",
                lambda: self.sovereignty_decision_engine.list_decisions(limit=100),
            )

        if self.predictive_engine is not None:
            capture(
                "predictive_status",
                lambda: self.predictive_engine.predictive_status(
                    tenant_id=tenant_id,
                ),
            )
            capture(
                "predictions",
                lambda: self.predictive_engine.list_predictions(limit=100),
            )

        if self.learning_engine is not None:
            capture(
                "learning_status",
                lambda: self.learning_engine.learning_status(
                    tenant_id=tenant_id,
                ),
            )
            capture(
                "learning_patterns",
                lambda: self.learning_engine.list_patterns(limit=100),
            )
            capture(
                "target_scores",
                lambda: self.learning_engine.target_scores(),
            )

        if self.adaptive_policy_engine is not None:
            capture(
                "policy_status",
                lambda: self.adaptive_policy_engine.policy_engine_status(
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

        if self.federated_router is not None:
            capture(
                "routing_status",
                lambda: self.federated_router.routing_status(),
            )

        if self.sovereign_controller is not None:
            capture(
                "sovereignty_status",
                lambda: self.sovereign_controller.sovereignty_status(),
            )

        if self.cluster_manager is not None:
            capture(
                "cluster_health",
                lambda: self.cluster_manager.cluster_health(),
            )
            capture(
                "clusters",
                lambda: self.cluster_manager.list_clusters(
                    tenant_id=tenant_id,
                ),
            )

        if self.domain_manager is not None:
            capture(
                "domain_health",
                lambda: self.domain_manager.domain_health(),
            )
            capture(
                "domains",
                lambda: self.domain_manager.list_domains(
                    tenant_id=tenant_id,
                ),
            )

        if self.federation_manager is not None:
            capture(
                "federation_health",
                lambda: self.federation_manager.federation_health(),
            )

        return telemetry

    # ========================================================
    # SIGNAL FUSION
    # ========================================================

    def _derive_signals(
        self,
        *,
        tenant_id: str,
        telemetry: Dict[str, Any],
        workload: Dict[str, Any],
    ) -> List[ExecutionCognitionSignal]:
        signals: List[ExecutionCognitionSignal] = []

        signals.extend(
            self._signals_from_status_blocks(
                tenant_id=tenant_id,
                telemetry=telemetry,
            )
        )

        signals.extend(
            self._signals_from_predictions(
                tenant_id=tenant_id,
                telemetry=telemetry,
            )
        )

        signals.extend(
            self._signals_from_learning(
                tenant_id=tenant_id,
                telemetry=telemetry,
            )
        )

        signals.extend(
            self._signals_from_workload(
                tenant_id=tenant_id,
                workload=workload,
            )
        )

        return signals

    def _signals_from_status_blocks(
        self,
        *,
        tenant_id: str,
        telemetry: Dict[str, Any],
    ) -> List[ExecutionCognitionSignal]:
        signals: List[ExecutionCognitionSignal] = []

        checks = [
            ("sovereignty_status", "SOVEREIGN_BLOCK_PRESSURE", "sovereign_execution_controller", "blocked"),
            ("routing_status", "ROUTING_BLOCK_PRESSURE", "federated_execution_router", "blocked"),
            ("relay_status", "RELAY_FAILURE_PRESSURE", "cross_runtime_execution_relay", "failed"),
            ("relay_status", "RELAY_BLOCK_PRESSURE", "cross_runtime_execution_relay", "blocked"),
        ]

        for key, signal_type, source, field_name in checks:
            data = telemetry.get(key, {}) or {}
            value = int(data.get(field_name, 0) or 0)

            if value > 0:
                signals.append(
                    self._signal(
                        signal_type=signal_type,
                        severity=COGNITION_HIGH,
                        source=source,
                        message=f"{source} reports {field_name}={value}.",
                        tenant_id=tenant_id,
                        confidence=0.75,
                        weight=1.2,
                        metadata=data,
                    )
                )

        for key, signal_type, source in [
            ("cluster_health", "CLUSTER_HEALTH_PRESSURE", "distributed_runtime_cluster_manager"),
            ("domain_health", "DOMAIN_HEALTH_PRESSURE", "execution_domain_manager"),
            ("federation_health", "FEDERATION_HEALTH_PRESSURE", "runtime_federation_manager"),
        ]:
            data = telemetry.get(key, {}) or {}
            risk = str(data.get("risk") or "").upper()

            if risk in {"HIGH", "CRITICAL"}:
                signals.append(
                    self._signal(
                        signal_type=signal_type,
                        severity=risk,
                        source=source,
                        message=f"{source} reports risk={risk}.",
                        tenant_id=tenant_id,
                        confidence=0.72,
                        weight=1.25,
                        metadata=data,
                    )
                )

        return signals

    def _signals_from_predictions(
        self,
        *,
        tenant_id: str,
        telemetry: Dict[str, Any],
    ) -> List[ExecutionCognitionSignal]:
        signals = []

        for pred in telemetry.get("predictions", []) or []:
            severity = str(pred.get("severity") or COGNITION_MEDIUM).upper()
            probability = float(pred.get("probability", 0.0) or 0.0)

            if probability < 0.35:
                continue

            signals.append(
                self._signal(
                    signal_type=f"PREDICTED_{pred.get('prediction_type')}",
                    severity=severity,
                    source="predictive_runtime_stability_engine",
                    message=pred.get("message", "Predictive runtime signal detected."),
                    tenant_id=tenant_id,
                    target=pred.get("target"),
                    confidence=float(pred.get("confidence", 0.5) or 0.5),
                    weight=max(0.8, probability),
                    metadata=pred,
                )
            )

        predictive_latest = (
            telemetry.get("predictive_status", {})
            .get("latest_assessment")
            or {}
        )

        state = str(predictive_latest.get("predictive_state") or "").upper()

        if state in {"DEGRADING", "UNSTABLE", "CRITICAL"}:
            signals.append(
                self._signal(
                    signal_type="PREDICTIVE_STATE_PRESSURE",
                    severity=COGNITION_HIGH if state != "CRITICAL" else COGNITION_CRITICAL_RISK,
                    source="predictive_runtime_stability_engine",
                    message=f"Predictive runtime state is {state}.",
                    tenant_id=tenant_id,
                    confidence=float(predictive_latest.get("confidence", 0.6) or 0.6),
                    weight=1.3,
                    metadata=predictive_latest,
                )
            )

        return signals

    def _signals_from_learning(
        self,
        *,
        tenant_id: str,
        telemetry: Dict[str, Any],
    ) -> List[ExecutionCognitionSignal]:
        signals = []

        learning_latest = (
            telemetry.get("learning_status", {})
            .get("latest_assessment")
            or {}
        )

        state = str(learning_latest.get("learning_state") or "").upper()

        if state in {"DEGRADING", "UNSTABLE", "RECURRING"}:
            signals.append(
                self._signal(
                    signal_type="LEARNED_FABRIC_INSTABILITY",
                    severity=COGNITION_HIGH,
                    source="runtime_fabric_learning_engine",
                    message=f"Learning engine reports runtime fabric state={state}.",
                    tenant_id=tenant_id,
                    confidence=float(learning_latest.get("confidence", 0.6) or 0.6),
                    weight=1.2,
                    metadata=learning_latest,
                )
            )

        for pattern in telemetry.get("learning_patterns", []) or []:
            severity = str(pattern.get("severity") or COGNITION_MEDIUM).upper()

            if severity not in {"HIGH", "CRITICAL"}:
                continue

            signals.append(
                self._signal(
                    signal_type=f"LEARNED_{pattern.get('pattern_type')}",
                    severity=severity,
                    source="runtime_fabric_learning_engine",
                    message=pattern.get("message", "Runtime learning pattern detected."),
                    tenant_id=tenant_id,
                    target=pattern.get("target"),
                    confidence=float(pattern.get("confidence", 0.5) or 0.5),
                    weight=1.15,
                    metadata=pattern,
                )
            )

        return signals

    def _signals_from_workload(
        self,
        *,
        tenant_id: str,
        workload: Dict[str, Any],
    ) -> List[ExecutionCognitionSignal]:
        categories = {
            str(c).upper()
            for c in workload.get("categories", [])
        }

        if not categories.intersection({"CUI", "ITAR", "EXPORT_CONTROLLED", "CLASSIFIED"}):
            return []

        return [
            self._signal(
                signal_type="HIGH_SENSITIVITY_EXECUTION_CONTEXT",
                severity=COGNITION_HIGH,
                source="workload_context",
                message="High-sensitivity workload increases sovereign cognition requirements.",
                tenant_id=tenant_id,
                confidence=0.8,
                weight=1.1,
                metadata={"categories": sorted(categories)},
            )
        ]

    def _signal(
        self,
        *,
        signal_type: str,
        severity: str,
        source: str,
        message: str,
        tenant_id: str,
        target: Optional[str] = None,
        confidence: float = 0.5,
        weight: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ExecutionCognitionSignal:
        return ExecutionCognitionSignal(
            signal_id=f"EXEC-COG-SIGNAL-{uuid.uuid4().hex[:12].upper()}",
            signal_type=signal_type,
            severity=severity,
            source=source,
            message=message,
            tenant_id=tenant_id,
            target=target,
            confidence=round(max(0.0, min(confidence, 1.0)), 3),
            weight=float(weight or 1.0),
            metadata=metadata or {},
        )

    # ========================================================
    # COGNITIVE MODELS
    # ========================================================

    def _build_cascade_model(
        self,
        *,
        signals: List[ExecutionCognitionSignal],
        telemetry: Dict[str, Any],
    ) -> Dict[str, Any]:
        signal_types = {s.signal_type for s in signals}

        cascades = []

        if any("RELAY" in s for s in signal_types) and any(
            "ROUTING" in s or "FEDERATION" in s
            for s in signal_types
        ):
            cascades.append({
                "cascade": "relay_to_routing_fragmentation",
                "likelihood": "HIGH",
                "description": "Relay pressure may increase federated routing fragmentation.",
            })

        if any("CLUSTER" in s for s in signal_types) and any(
            "ROUTING" in s or "PREDICTED" in s
            for s in signal_types
        ):
            cascades.append({
                "cascade": "cluster_pressure_to_execution_congestion",
                "likelihood": "HIGH",
                "description": "Cluster pressure may propagate into execution routing congestion.",
            })

        if any("DOMAIN" in s or "SOVEREIGN" in s for s in signal_types) and any(
            "POLICY" in s or "HIGH_SENSITIVITY" in s
            for s in signal_types
        ):
            cascades.append({
                "cascade": "domain_pressure_to_governance_escalation",
                "likelihood": "MEDIUM",
                "description": "Domain pressure may trigger governance escalation and approval bottlenecks.",
            })

        if any("LEARNED" in s for s in signal_types) and any(
            "PREDICTED" in s for s in signal_types
        ):
            cascades.append({
                "cascade": "learned_pattern_to_predicted_instability",
                "likelihood": "HIGH",
                "description": "Historical instability patterns align with predictive warnings.",
            })

        return {
            "cascade_count": len(cascades),
            "cascades": cascades,
            "signal_count": len(signals),
            "created_at_ms": _now_ms(),
        }

    def _build_execution_chain_model(
        self,
        *,
        tenant_id: str,
        workload: Dict[str, Any],
        telemetry: Dict[str, Any],
        signals: List[ExecutionCognitionSignal],
    ) -> Dict[str, Any]:
        relay_status = telemetry.get("relay_status", {}) or {}
        routing_status = telemetry.get("routing_status", {}) or {}
        cluster_health = telemetry.get("cluster_health", {}) or {}
        domain_health = telemetry.get("domain_health", {}) or {}

        blocked = (
            int(relay_status.get("blocked", 0) or 0)
            + int(routing_status.get("blocked", 0) or 0)
        )

        failed = int(relay_status.get("failed", 0) or 0)

        chain_state = "VIABLE"

        if failed > 0 or blocked > 0:
            chain_state = "DEGRADED"

        if cluster_health.get("risk") == "CRITICAL" or domain_health.get("risk") == "CRITICAL":
            chain_state = "AT_RISK"

        if any(s.severity == COGNITION_CRITICAL_RISK for s in signals):
            chain_state = "CRITICAL"

        return {
            "tenant_id": tenant_id,
            "workload_action": workload.get("action"),
            "chain_state": chain_state,
            "relay_health": relay_status,
            "routing_health": routing_status,
            "cluster_health": cluster_health,
            "domain_health": domain_health,
            "blocked_paths": blocked,
            "failed_relays": failed,
            "high_sensitivity": bool(
                {
                    str(c).upper()
                    for c in workload.get("categories", [])
                }.intersection({"CUI", "ITAR", "EXPORT_CONTROLLED", "CLASSIFIED"})
            ),
            "created_at_ms": _now_ms(),
        }

    # ========================================================
    # SCORING
    # ========================================================

    def _cognition_score(
        self,
        *,
        signals: List[ExecutionCognitionSignal],
        cascade_model: Dict[str, Any],
    ) -> float:
        score = 0.0

        severity_score = {
            COGNITION_LOW: 5.0,
            COGNITION_MEDIUM: 15.0,
            COGNITION_HIGH: 30.0,
            COGNITION_CRITICAL_RISK: 50.0,
        }

        for signal in signals:
            score += (
                severity_score.get(str(signal.severity).upper(), 10.0)
                * float(signal.weight or 1.0)
                * max(float(signal.confidence or 0.5), 0.25)
            )

        score += int(cascade_model.get("cascade_count", 0) or 0) * 8.0

        return round(max(0.0, min(score, 100.0)), 2)

    def _risk_level(
        self,
        score: float,
    ) -> str:
        if score >= 80:
            return COGNITION_CRITICAL_RISK
        if score >= 55:
            return COGNITION_HIGH
        if score >= 25:
            return COGNITION_MEDIUM
        return COGNITION_LOW

    def _cognition_state(
        self,
        *,
        score: float,
        signals: List[ExecutionCognitionSignal],
    ) -> str:
        if any(s.severity == COGNITION_CRITICAL_RISK for s in signals):
            return COGNITION_CRITICAL
        if score >= 80:
            return COGNITION_UNSTABLE
        if score >= 55:
            return COGNITION_DEGRADED
        if score >= 25:
            return COGNITION_WATCH
        return COGNITION_STABLE

    def _confidence(
        self,
        *,
        signals: List[ExecutionCognitionSignal],
        telemetry: Dict[str, Any],
    ) -> float:
        if not signals:
            return 0.55

        signal_conf = (
            sum(float(s.confidence or 0.5) for s in signals)
            / max(len(signals), 1)
        )

        telemetry_quality = min(
            len([k for k in telemetry.keys() if not k.endswith("_error")]) * 0.025,
            0.25,
        )

        error_penalty = min(
            len([k for k in telemetry.keys() if k.endswith("_error")]) * 0.04,
            0.25,
        )

        return round(
            max(0.05, min(signal_conf + telemetry_quality - error_penalty, 0.98)),
            3,
        )

    def _survivability_score(
        self,
        *,
        telemetry: Dict[str, Any],
        signals: List[ExecutionCognitionSignal],
        execution_chain_model: Dict[str, Any],
    ) -> float:
        score = 100.0

        chain_state = execution_chain_model.get("chain_state")

        if chain_state == "DEGRADED":
            score -= 25.0
        elif chain_state == "AT_RISK":
            score -= 45.0
        elif chain_state == "CRITICAL":
            score -= 65.0

        score -= len([
            s for s in signals
            if s.severity in {COGNITION_HIGH, COGNITION_CRITICAL_RISK}
        ]) * 5.0

        return round(max(0.0, min(score, 100.0)), 2)

    def _continuity_score(
        self,
        *,
        telemetry: Dict[str, Any],
        signals: List[ExecutionCognitionSignal],
        execution_chain_model: Dict[str, Any],
    ) -> float:
        score = 100.0

        relay = telemetry.get("relay_status", {}) or {}
        routing = telemetry.get("routing_status", {}) or {}

        score -= int(relay.get("failed", 0) or 0) * 10.0
        score -= int(relay.get("blocked", 0) or 0) * 8.0
        score -= int(routing.get("blocked", 0) or 0) * 8.0

        if execution_chain_model.get("high_sensitivity"):
            score -= 5.0

        return round(max(0.0, min(score, 100.0)), 2)

    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    def _recommendations_for(
        self,
        *,
        tenant_id: str,
        risk_level: str,
        cognition_state: str,
        survivability_score: float,
        continuity_score: float,
        signals: List[ExecutionCognitionSignal],
        cascade_model: Dict[str, Any],
        execution_chain_model: Dict[str, Any],
    ) -> List[ExecutionCognitionRecommendation]:
        recs: List[ExecutionCognitionRecommendation] = []
        seen = set()
        signal_types = {s.signal_type for s in signals}

        def add(
            action: str,
            priority: str,
            reason: str,
            target: Optional[str] = None,
            requires_approval: bool = True,
        ) -> None:
            key = (action, target, reason)
            if key in seen:
                return
            seen.add(key)
            recs.append(
                ExecutionCognitionRecommendation(
                    recommendation_id=f"EXEC-COG-REC-{uuid.uuid4().hex[:12].upper()}",
                    action=action,
                    priority=priority,
                    reason=reason,
                    tenant_id=tenant_id,
                    target=target,
                    requires_approval=requires_approval,
                    metadata={
                        "cognition_state": cognition_state,
                        "survivability_score": survivability_score,
                        "continuity_score": continuity_score,
                    },
                )
            )

        if not signals:
            add(
                ACTION_OBSERVE,
                COGNITION_LOW,
                "No elevated execution cognition pressure detected.",
                requires_approval=False,
            )
            return recs

        if risk_level in {COGNITION_HIGH, COGNITION_CRITICAL_RISK}:
            add(
                ACTION_REDUCE_AUTONOMY,
                risk_level,
                "Reduce autonomy under elevated fused execution cognition risk.",
            )
            add(
                ACTION_ESCALATE_GOVERNANCE,
                risk_level,
                "Escalate governance due to fused operational cognition risk.",
            )

        if any("RELAY" in s for s in signal_types):
            add(
                ACTION_RESTRICT_RELAYS,
                COGNITION_HIGH,
                "Restrict relays due to continuity or relay instability pressure.",
            )
            add(
                ACTION_PRESERVE_CONTINUITY,
                COGNITION_HIGH,
                "Preserve mission continuity due to relay pressure.",
            )

        if any("ROUTING" in s or "FEDERATION" in s for s in signal_types):
            add(
                ACTION_RESTRICT_FEDERATED_ROUTING,
                COGNITION_HIGH,
                "Restrict or optimize federated routing due to routing/federation pressure.",
            )
            add(
                ACTION_TRIGGER_MESH_OPTIMIZER,
                COGNITION_MEDIUM,
                "Trigger mesh optimizer due to routing or topology pressure.",
                requires_approval=False,
            )

        if any("CLUSTER" in s for s in signal_types):
            add(
                ACTION_TRIGGER_CLUSTER_BALANCER,
                COGNITION_MEDIUM,
                "Trigger cluster balancer due to cluster pressure.",
                requires_approval=False,
            )

        if any("PREDICTED" in s for s in signal_types):
            add(
                ACTION_TRIGGER_PREDICTIVE_ENGINE,
                COGNITION_MEDIUM,
                "Refresh predictive runtime cognition due to active forecasts.",
                requires_approval=False,
            )

        if any("LEARNED" in s for s in signal_types):
            add(
                ACTION_TRIGGER_LEARNING_INGEST,
                COGNITION_MEDIUM,
                "Refresh learning memory due to learned instability pattern.",
                requires_approval=False,
            )

        if any("SOVEREIGN" in s or "DOMAIN" in s or "HIGH_SENSITIVITY" in s for s in signal_types):
            add(
                ACTION_REQUIRE_APPROVAL,
                COGNITION_HIGH,
                "Require approval due to sovereignty/domain/high-sensitivity cognition.",
            )
            add(
                ACTION_TRIGGER_POLICY_ENGINE,
                COGNITION_MEDIUM,
                "Trigger adaptive sovereign policy cognition.",
                requires_approval=False,
            )
            add(
                ACTION_TRIGGER_DECISION_ENGINE,
                COGNITION_MEDIUM,
                "Trigger sovereignty decision engine for fused reasoning.",
                requires_approval=False,
            )

        if survivability_score < 60 or continuity_score < 60:
            add(
                ACTION_TRIGGER_RECOVERY,
                COGNITION_HIGH,
                "Trigger recovery because survivability or continuity score is degraded.",
            )

        if int(cascade_model.get("cascade_count", 0) or 0) > 0:
            add(
                ACTION_ESCALATE_GOVERNANCE,
                COGNITION_HIGH,
                "Escalate governance due to cascading failure cognition.",
            )

        return recs

    # ========================================================
    # ACTION HELPERS
    # ========================================================

    def _trigger_learning_ingest(
        self,
        rec: ExecutionCognitionRecommendation,
    ) -> Dict[str, Any]:
        if self.learning_engine is None:
            return {"status": "SKIPPED", "reason": "learning_engine_unavailable"}

        result = self.learning_engine.ingest_current_state(
            tenant_id=rec.tenant_id,
        )

        return {"status": "EXECUTED", "result": result}

    def _trigger_predictive_engine(
        self,
        rec: ExecutionCognitionRecommendation,
    ) -> Dict[str, Any]:
        if self.predictive_engine is None:
            return {"status": "SKIPPED", "reason": "predictive_engine_unavailable"}

        assessment = self.predictive_engine.assess(
            tenant_id=rec.tenant_id,
        )

        return {
            "status": "EXECUTED",
            "assessment": assessment.to_dict() if hasattr(assessment, "to_dict") else {},
        }

    def _trigger_decision_engine(
        self,
        rec: ExecutionCognitionRecommendation,
    ) -> Dict[str, Any]:
        if self.sovereignty_decision_engine is None:
            return {"status": "SKIPPED", "reason": "sovereignty_decision_engine_unavailable"}

        assessment = self.sovereignty_decision_engine.assess(
            tenant_id=rec.tenant_id,
            workload={
                "action": "AUTONOMOUS_EXECUTION_COGNITION_TRIGGER",
                "source": "autonomous_execution_cognition_engine",
            },
        )

        return {
            "status": "EXECUTED",
            "assessment": assessment.to_dict() if hasattr(assessment, "to_dict") else {},
        }

    def _trigger_policy_engine(
        self,
        rec: ExecutionCognitionRecommendation,
    ) -> Dict[str, Any]:
        if self.adaptive_policy_engine is None:
            return {"status": "SKIPPED", "reason": "adaptive_policy_engine_unavailable"}

        assessment = self.adaptive_policy_engine.assess(
            tenant_id=rec.tenant_id,
            workload={
                "action": "AUTONOMOUS_EXECUTION_COGNITION_POLICY_TRIGGER",
                "source": "autonomous_execution_cognition_engine",
            },
        )

        return {
            "status": "EXECUTED",
            "assessment": assessment.to_dict() if hasattr(assessment, "to_dict") else {},
        }

    def _trigger_mesh_optimizer(
        self,
        rec: ExecutionCognitionRecommendation,
    ) -> Dict[str, Any]:
        if self.mesh_optimizer is None:
            return {"status": "SKIPPED", "reason": "mesh_optimizer_unavailable"}

        result = self.mesh_optimizer.enforce(
            tenant_id=rec.tenant_id,
            dry_run=True,
        )

        return {"status": "EXECUTED", "result": result}

    def _trigger_cluster_balancer(
        self,
        rec: ExecutionCognitionRecommendation,
    ) -> Dict[str, Any]:
        if self.cluster_balancer is None:
            return {"status": "SKIPPED", "reason": "cluster_balancer_unavailable"}

        result = self.cluster_balancer.enforce(
            tenant_id=rec.tenant_id,
            dry_run=True,
        )

        return {"status": "EXECUTED", "result": result}

    def _trigger_recovery(
        self,
        rec: ExecutionCognitionRecommendation,
    ) -> Dict[str, Any]:
        if self.recovery_manager is None:
            return {"status": "SKIPPED", "reason": "recovery_manager_unavailable"}

        result = self.recovery_manager.auto_recover(
            tenant_id=rec.tenant_id,
            actor="autonomous_execution_cognition_engine",
            force=False,
        )

        return {
            "status": "EXECUTED",
            "result": result.to_dict() if hasattr(result, "to_dict") else {},
        }

    def _reduce_autonomy(
        self,
        rec: ExecutionCognitionRecommendation,
    ) -> Dict[str, Any]:
        if self.autonomy_governor is None:
            return {"status": "SKIPPED", "reason": "autonomy_governor_unavailable"}

        result = self.autonomy_governor.set_autonomy_mode(
            tenant_id=rec.tenant_id,
            mode="ASSISTED",
            reason=rec.reason,
        )

        return {"status": "EXECUTED", "result": result}

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

    def list_recommendations(
        self,
        *,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        rows = sorted(
            self._recommendations,
            key=lambda r: r.created_at_ms,
            reverse=True,
        )

        return [r.to_dict() for r in rows[:limit]]

    def cognition_status(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
    ) -> Dict[str, Any]:
        latest = self._assessments[-1].to_dict() if self._assessments else None

        return {
            "tenant_id": tenant_id,
            "assessment_count": len(self._assessments),
            "signal_count": len(self._signals),
            "recommendation_count": len(self._recommendations),
            "latest_assessment": latest,
        }

    # ========================================================
    # SUMMARY
    # ========================================================

    def _summary(
        self,
        *,
        cognition_state: str,
        risk_level: str,
        confidence: float,
        signal_count: int,
        recommendation_count: int,
        survivability_score: float,
        continuity_score: float,
    ) -> str:
        return (
            f"Execution cognition state={cognition_state}, "
            f"risk={risk_level}, confidence={confidence}. "
            f"Signals={signal_count}, recommendations={recommendation_count}, "
            f"survivability={survivability_score}, continuity={continuity_score}."
        )

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
                source="autonomous_execution_cognition_engine",
                severity=payload.get("risk_level") or payload.get("cognition_state") or "INFO",
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


_DEFAULT_AUTONOMOUS_EXECUTION_COGNITION_ENGINE: Optional[
    AutonomousExecutionCognitionEngine
] = None


def get_autonomous_execution_cognition_engine(
    *,
    sovereignty_decision_engine: Any = None,
    predictive_engine: Any = None,
    learning_engine: Any = None,
    adaptive_policy_engine: Any = None,
    mesh_optimizer: Any = None,
    cluster_balancer: Any = None,
    execution_relay: Any = None,
    federated_router: Any = None,
    sovereign_controller: Any = None,
    cluster_manager: Any = None,
    domain_manager: Any = None,
    federation_manager: Any = None,
    recovery_manager: Any = None,
    autonomy_governor: Any = None,
    storage: Any = None,
    event_bus: Any = None,
    reset: bool = False,
) -> AutonomousExecutionCognitionEngine:
    global _DEFAULT_AUTONOMOUS_EXECUTION_COGNITION_ENGINE

    if reset or _DEFAULT_AUTONOMOUS_EXECUTION_COGNITION_ENGINE is None:
        _DEFAULT_AUTONOMOUS_EXECUTION_COGNITION_ENGINE = (
            AutonomousExecutionCognitionEngine(
                sovereignty_decision_engine=sovereignty_decision_engine,
                predictive_engine=predictive_engine,
                learning_engine=learning_engine,
                adaptive_policy_engine=adaptive_policy_engine,
                mesh_optimizer=mesh_optimizer,
                cluster_balancer=cluster_balancer,
                execution_relay=execution_relay,
                federated_router=federated_router,
                sovereign_controller=sovereign_controller,
                cluster_manager=cluster_manager,
                domain_manager=domain_manager,
                federation_manager=federation_manager,
                recovery_manager=recovery_manager,
                autonomy_governor=autonomy_governor,
                storage=storage,
                event_bus=event_bus,
            )
        )

    return _DEFAULT_AUTONOMOUS_EXECUTION_COGNITION_ENGINE