"""
core/runtime/predictive_runtime_stability_engine.py

Predictive Runtime Stability Engine.

Purpose:
- predictive sovereign runtime cognition
- early-warning instability forecasting
- topology degradation prediction
- relay/routing/cluster/domain risk projection
- governance overload prediction
- predictive confidence and impact scoring

Architecture Rules:
- no Streamlit/session_state dependency
- no persistent SQLite connection
- no hidden global mutation
- service-owned prediction memory only
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


PREDICTION_LOW = "LOW"
PREDICTION_MEDIUM = "MEDIUM"
PREDICTION_HIGH = "HIGH"
PREDICTION_CRITICAL = "CRITICAL"

PREDICTIVE_STATE_STABLE = "STABLE"
PREDICTIVE_STATE_WATCH = "WATCH"
PREDICTIVE_STATE_DEGRADING = "DEGRADING"
PREDICTIVE_STATE_UNSTABLE = "UNSTABLE"
PREDICTIVE_STATE_CRITICAL = "CRITICAL"

PREDICTION_PENDING = "PENDING"
PREDICTION_CONFIRMED = "CONFIRMED"
PREDICTION_FALSE_POSITIVE = "FALSE_POSITIVE"
PREDICTION_EXPIRED = "EXPIRED"

DEFAULT_TENANT = "default"


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class RuntimeStabilityPrediction:
    prediction_id: str
    prediction_type: str
    tenant_id: str
    severity: str
    probability: float
    confidence: float
    message: str
    projected_timeline_minutes: int = 30
    blast_radius: str = PREDICTION_LOW
    sovereign_impact: str = PREDICTION_LOW
    governance_impact: str = PREDICTION_LOW
    operational_impact: str = PREDICTION_LOW
    target: Optional[str] = None
    status: str = PREDICTION_PENDING
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    recommended_actions: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)
    expires_at_ms: Optional[int] = None
    resolved_at_ms: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RuntimeStabilityAssessment:
    assessment_id: str
    tenant_id: str
    predictive_state: str
    stability_score: float
    confidence: float
    predictions: List[RuntimeStabilityPrediction] = field(default_factory=list)
    early_warnings: List[Dict[str, Any]] = field(default_factory=list)
    telemetry: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["predictions"] = [
            p.to_dict() if hasattr(p, "to_dict") else p
            for p in self.predictions
        ]
        return data


class PredictiveRuntimeStabilityEngine:
    def __init__(
        self,
        *,
        learning_engine: Any = None,
        sovereignty_decision_engine: Any = None,
        adaptive_policy_engine: Any = None,
        mesh_optimizer: Any = None,
        cluster_balancer: Any = None,
        execution_relay: Any = None,
        federated_router: Any = None,
        cluster_manager: Any = None,
        domain_manager: Any = None,
        federation_manager: Any = None,
        storage: Any = None,
        event_bus: Any = None,
    ) -> None:
        self.storage = storage
        self.learning_engine = (
            learning_engine
            or getattr(storage, "runtime_fabric_learning_engine", None)
        )
        self.sovereignty_decision_engine = (
            sovereignty_decision_engine
            or getattr(storage, "sovereignty_decision_engine", None)
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
        self.event_bus = event_bus or getattr(storage, "event_bus", None)

        self._assessments: List[RuntimeStabilityAssessment] = []
        self._predictions: List[RuntimeStabilityPrediction] = []
        self._prediction_outcomes: List[Dict[str, Any]] = []

    # ========================================================
    # MAIN ASSESSMENT
    # ========================================================

    def assess(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
    ) -> RuntimeStabilityAssessment:
        telemetry = self._collect_telemetry(
            tenant_id=tenant_id,
        )

        predictions = self._generate_predictions(
            tenant_id=tenant_id,
            telemetry=telemetry,
        )

        stability_score = self._stability_score(
            predictions=predictions,
            telemetry=telemetry,
        )

        predictive_state = self._predictive_state(
            stability_score=stability_score,
            predictions=predictions,
        )

        confidence = self._confidence(
            predictions=predictions,
            telemetry=telemetry,
        )

        early_warnings = self._early_warnings(
            predictions=predictions,
            predictive_state=predictive_state,
        )

        assessment = RuntimeStabilityAssessment(
            assessment_id=f"PRED-STABILITY-{uuid.uuid4().hex[:12].upper()}",
            tenant_id=tenant_id,
            predictive_state=predictive_state,
            stability_score=stability_score,
            confidence=confidence,
            predictions=predictions,
            early_warnings=early_warnings,
            telemetry=telemetry,
        )

        self._assessments.append(assessment)
        self._assessments = self._assessments[-500:]

        self._predictions.extend(predictions)
        self._predictions = self._predictions[-1000:]

        self._emit(
            "PREDICTIVE_RUNTIME_STABILITY_ASSESSED",
            assessment.to_dict(),
        )

        return assessment

    # ========================================================
    # TELEMETRY
    # ========================================================

    def _collect_telemetry(
        self,
        *,
        tenant_id: str,
    ) -> Dict[str, Any]:
        telemetry: Dict[str, Any] = {
            "tenant_id": tenant_id,
            "collected_at_ms": _now_ms(),
        }

        def capture(key: str, fn) -> None:
            try:
                telemetry[key] = fn()
            except Exception as exc:
                telemetry[f"{key}_error"] = str(exc)

        if self.learning_engine is not None:
            capture(
                "learning_status",
                lambda: self.learning_engine.learning_status(
                    tenant_id=tenant_id,
                ),
            )
            capture(
                "learning_assessments",
                lambda: self.learning_engine.list_assessments(limit=50),
            )
            capture(
                "learning_patterns",
                lambda: self.learning_engine.list_patterns(limit=100),
            )
            capture(
                "target_scores",
                lambda: self.learning_engine.target_scores(),
            )

        if self.sovereignty_decision_engine is not None:
            capture(
                "decision_status",
                lambda: self.sovereignty_decision_engine.decision_engine_status(
                    tenant_id=tenant_id,
                ),
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

        if self.federation_manager is not None:
            capture(
                "federation_health",
                lambda: self.federation_manager.federation_health(),
            )

        return telemetry

    # ========================================================
    # PREDICTIONS
    # ========================================================

    def _generate_predictions(
        self,
        *,
        tenant_id: str,
        telemetry: Dict[str, Any],
    ) -> List[RuntimeStabilityPrediction]:
        predictions: List[RuntimeStabilityPrediction] = []

        predictions.extend(
            self._predict_from_learning(
                tenant_id=tenant_id,
                telemetry=telemetry,
            )
        )

        predictions.extend(
            self._predict_cluster_saturation(
                tenant_id=tenant_id,
                telemetry=telemetry,
            )
        )

        predictions.extend(
            self._predict_relay_instability(
                tenant_id=tenant_id,
                telemetry=telemetry,
            )
        )

        predictions.extend(
            self._predict_routing_congestion(
                tenant_id=tenant_id,
                telemetry=telemetry,
            )
        )

        predictions.extend(
            self._predict_sovereign_governance_pressure(
                tenant_id=tenant_id,
                telemetry=telemetry,
            )
        )

        predictions.extend(
            self._predict_domain_or_federation_degradation(
                tenant_id=tenant_id,
                telemetry=telemetry,
            )
        )

        return self._dedupe_predictions(predictions)

    def _predict_from_learning(
        self,
        *,
        tenant_id: str,
        telemetry: Dict[str, Any],
    ) -> List[RuntimeStabilityPrediction]:
        predictions = []

        latest = (
            telemetry.get("learning_status", {})
            .get("latest_assessment")
            or {}
        )

        state = latest.get("learning_state")
        stability = float(latest.get("stability_score", 100.0) or 100.0)
        patterns = latest.get("patterns", []) or []

        if state in {"DEGRADING", "UNSTABLE", "RECURRING"} or stability < 70:
            predictions.append(
                self._prediction(
                    prediction_type="RUNTIME_FABRIC_DEGRADATION_FORECAST",
                    tenant_id=tenant_id,
                    severity=PREDICTION_HIGH if stability < 50 else PREDICTION_MEDIUM,
                    probability=min(0.95, (100.0 - stability) / 100.0 + 0.25),
                    confidence=float(latest.get("confidence", 0.5) or 0.5),
                    message="Learning engine indicates future runtime fabric degradation risk.",
                    projected_timeline_minutes=30,
                    evidence=patterns[:10],
                    metadata=latest,
                )
            )

        for pattern in telemetry.get("learning_patterns", []) or []:
            if pattern.get("pattern_type") in {
                "TARGET_INSTABILITY_PATTERN",
                "RECURRING_FAILURE_PATTERN",
            }:
                predictions.append(
                    self._prediction(
                        prediction_type="RECURRING_INSTABILITY_FORECAST",
                        tenant_id=tenant_id,
                        severity=pattern.get("severity", PREDICTION_HIGH),
                        probability=min(
                            0.95,
                            0.45 + float(pattern.get("confidence", 0.4) or 0.4),
                        ),
                        confidence=float(pattern.get("confidence", 0.5) or 0.5),
                        message=pattern.get(
                            "message",
                            "Recurring instability pattern may continue.",
                        ),
                        target=pattern.get("target"),
                        projected_timeline_minutes=45,
                        evidence=[pattern],
                        metadata=pattern,
                    )
                )

        return predictions

    def _predict_cluster_saturation(
        self,
        *,
        tenant_id: str,
        telemetry: Dict[str, Any],
    ) -> List[RuntimeStabilityPrediction]:
        predictions = []

        for cluster in telemetry.get("clusters", []) or []:
            active = float(cluster.get("active_units", 0) or 0)
            capacity = float(cluster.get("capacity_units", 1) or 1)
            load_ratio = active / max(capacity, 1.0)
            health = float(cluster.get("health_score", 100.0) or 100.0)

            if load_ratio >= 0.75 or health < 70:
                severity = PREDICTION_CRITICAL if load_ratio >= 0.95 else PREDICTION_HIGH

                predictions.append(
                    self._prediction(
                        prediction_type="CLUSTER_SATURATION_FORECAST",
                        tenant_id=tenant_id,
                        severity=severity,
                        probability=min(0.98, load_ratio + ((100.0 - health) / 300.0)),
                        confidence=0.72,
                        message="Cluster saturation or health decline forecasted.",
                        target=cluster.get("cluster_id"),
                        projected_timeline_minutes=20,
                        blast_radius=PREDICTION_HIGH,
                        operational_impact=PREDICTION_HIGH,
                        evidence=[cluster],
                        metadata={
                            "load_ratio": load_ratio,
                            "health_score": health,
                            "cluster": cluster,
                        },
                    )
                )

        return predictions

    def _predict_relay_instability(
        self,
        *,
        tenant_id: str,
        telemetry: Dict[str, Any],
    ) -> List[RuntimeStabilityPrediction]:
        relay = telemetry.get("relay_status", {}) or {}

        failed = int(relay.get("failed", 0) or 0)
        blocked = int(relay.get("blocked", 0) or 0)
        approvals = int(relay.get("requires_approval", 0) or 0)

        pressure = failed * 0.2 + blocked * 0.15 + approvals * 0.05

        if pressure <= 0:
            return []

        return [
            self._prediction(
                prediction_type="RELAY_INSTABILITY_FORECAST",
                tenant_id=tenant_id,
                severity=PREDICTION_HIGH if pressure >= 0.4 else PREDICTION_MEDIUM,
                probability=min(0.95, 0.35 + pressure),
                confidence=0.68,
                message="Cross-runtime relay instability risk is increasing.",
                projected_timeline_minutes=30,
                sovereign_impact=PREDICTION_HIGH,
                operational_impact=PREDICTION_MEDIUM,
                evidence=[relay],
                metadata=relay,
            )
        ]

    def _predict_routing_congestion(
        self,
        *,
        tenant_id: str,
        telemetry: Dict[str, Any],
    ) -> List[RuntimeStabilityPrediction]:
        routing = telemetry.get("routing_status", {}) or {}

        blocked = int(routing.get("blocked", 0) or 0)
        federated = int(routing.get("federated_routes", 0) or 0)

        if blocked <= 0 and federated < 10:
            return []

        probability = min(0.95, 0.25 + blocked * 0.15 + federated * 0.025)

        return [
            self._prediction(
                prediction_type="ROUTING_CONGESTION_FORECAST",
                tenant_id=tenant_id,
                severity=PREDICTION_HIGH if probability >= 0.65 else PREDICTION_MEDIUM,
                probability=probability,
                confidence=0.7,
                message="Federated routing congestion or block pressure forecasted.",
                projected_timeline_minutes=25,
                governance_impact=PREDICTION_MEDIUM,
                operational_impact=PREDICTION_HIGH,
                evidence=[routing],
                metadata=routing,
            )
        ]

    def _predict_sovereign_governance_pressure(
        self,
        *,
        tenant_id: str,
        telemetry: Dict[str, Any],
    ) -> List[RuntimeStabilityPrediction]:
        policy_latest = (
            telemetry.get("policy_status", {})
            .get("latest_assessment")
            or {}
        )

        decision_latest = (
            telemetry.get("decision_status", {})
            .get("latest_assessment")
            or {}
        )

        risk_score = max(
            float(policy_latest.get("risk_score", 0.0) or 0.0),
            self._risk_to_score(decision_latest.get("risk_level")),
        )

        if risk_score < 40:
            return []

        return [
            self._prediction(
                prediction_type="GOVERNANCE_OVERLOAD_FORECAST",
                tenant_id=tenant_id,
                severity=PREDICTION_CRITICAL if risk_score >= 80 else PREDICTION_HIGH,
                probability=min(0.95, 0.35 + risk_score / 120.0),
                confidence=float(decision_latest.get("confidence", 0.65) or 0.65),
                message="Governance overload or sovereign escalation pressure forecasted.",
                projected_timeline_minutes=35,
                sovereign_impact=PREDICTION_HIGH,
                governance_impact=PREDICTION_HIGH,
                evidence=[
                    policy_latest,
                    decision_latest,
                ],
                metadata={
                    "policy_latest": policy_latest,
                    "decision_latest": decision_latest,
                },
            )
        ]

    def _predict_domain_or_federation_degradation(
        self,
        *,
        tenant_id: str,
        telemetry: Dict[str, Any],
    ) -> List[RuntimeStabilityPrediction]:
        predictions = []

        for key, label in [
            ("domain_health", "DOMAIN_INSTABILITY_FORECAST"),
            ("federation_health", "FEDERATION_FRAGMENTATION_FORECAST"),
        ]:
            health = telemetry.get(key, {}) or {}
            risk = health.get("risk")

            if risk in {PREDICTION_HIGH, PREDICTION_CRITICAL}:
                predictions.append(
                    self._prediction(
                        prediction_type=label,
                        tenant_id=tenant_id,
                        severity=risk,
                        probability=0.75 if risk == PREDICTION_HIGH else 0.9,
                        confidence=0.7,
                        message=f"{label} detected from runtime health signals.",
                        projected_timeline_minutes=30,
                        sovereign_impact=PREDICTION_HIGH,
                        governance_impact=PREDICTION_HIGH,
                        operational_impact=PREDICTION_MEDIUM,
                        evidence=[health],
                        metadata=health,
                    )
                )

        return predictions

    # ========================================================
    # HELPERS
    # ========================================================

    def _prediction(
        self,
        *,
        prediction_type: str,
        tenant_id: str,
        severity: str,
        probability: float,
        confidence: float,
        message: str,
        projected_timeline_minutes: int,
        target: Optional[str] = None,
        blast_radius: str = PREDICTION_MEDIUM,
        sovereign_impact: str = PREDICTION_MEDIUM,
        governance_impact: str = PREDICTION_MEDIUM,
        operational_impact: str = PREDICTION_MEDIUM,
        evidence: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RuntimeStabilityPrediction:
        expires_at_ms = _now_ms() + projected_timeline_minutes * 60_000

        return RuntimeStabilityPrediction(
            prediction_id=f"PRED-{uuid.uuid4().hex[:12].upper()}",
            prediction_type=prediction_type,
            tenant_id=tenant_id,
            severity=severity,
            probability=round(max(0.0, min(probability, 1.0)), 3),
            confidence=round(max(0.0, min(confidence, 1.0)), 3),
            message=message,
            projected_timeline_minutes=projected_timeline_minutes,
            blast_radius=blast_radius,
            sovereign_impact=sovereign_impact,
            governance_impact=governance_impact,
            operational_impact=operational_impact,
            target=target,
            evidence=evidence or [],
            recommended_actions=self._recommended_actions_for(
                prediction_type,
                severity,
            ),
            metadata=metadata or {},
            expires_at_ms=expires_at_ms,
        )

    def _recommended_actions_for(
        self,
        prediction_type: str,
        severity: str,
    ) -> List[Dict[str, Any]]:
        actions = []

        if prediction_type in {
            "CLUSTER_SATURATION_FORECAST",
            "RUNTIME_FABRIC_DEGRADATION_FORECAST",
        }:
            actions.append({"action": "TRIGGER_CLUSTER_BALANCER"})
            actions.append({"action": "TRIGGER_MESH_OPTIMIZER"})

        if prediction_type in {
            "ROUTING_CONGESTION_FORECAST",
            "FEDERATION_FRAGMENTATION_FORECAST",
        }:
            actions.append({"action": "RESTRICT_FEDERATED_ROUTING"})
            actions.append({"action": "TRIGGER_MESH_OPTIMIZER"})

        if prediction_type in {
            "RELAY_INSTABILITY_FORECAST",
        }:
            actions.append({"action": "RESTRICT_RELAYS"})
            actions.append({"action": "REVIEW_RELAY_CONTINUITY"})

        if prediction_type in {
            "GOVERNANCE_OVERLOAD_FORECAST",
            "DOMAIN_INSTABILITY_FORECAST",
        }:
            actions.append({"action": "TRIGGER_SOVEREIGNTY_DECISION_ENGINE"})
            actions.append({"action": "TRIGGER_ADAPTIVE_POLICY_ENGINE"})

        if severity in {PREDICTION_HIGH, PREDICTION_CRITICAL}:
            actions.append({"action": "REDUCE_AUTONOMY"})

        return actions

    def _dedupe_predictions(
        self,
        predictions: List[RuntimeStabilityPrediction],
    ) -> List[RuntimeStabilityPrediction]:
        seen = set()
        output = []

        for pred in sorted(
            predictions,
            key=lambda p: (
                self._risk_to_score(p.severity),
                p.probability,
                p.confidence,
            ),
            reverse=True,
        ):
            key = (pred.prediction_type, pred.target)
            if key in seen:
                continue
            seen.add(key)
            output.append(pred)

        return output

    def _risk_to_score(
        self,
        risk: Any,
    ) -> float:
        return {
            PREDICTION_LOW: 10.0,
            PREDICTION_MEDIUM: 35.0,
            PREDICTION_HIGH: 65.0,
            PREDICTION_CRITICAL: 90.0,
        }.get(str(risk or "").upper(), 0.0)

    def _stability_score(
        self,
        *,
        predictions: List[RuntimeStabilityPrediction],
        telemetry: Dict[str, Any],
    ) -> float:
        score = 100.0

        for pred in predictions:
            score -= self._risk_to_score(pred.severity) * pred.probability * 0.35
            score -= pred.confidence * 5.0

        return round(max(0.0, min(score, 100.0)), 2)

    def _predictive_state(
        self,
        *,
        stability_score: float,
        predictions: List[RuntimeStabilityPrediction],
    ) -> str:
        if any(p.severity == PREDICTION_CRITICAL for p in predictions):
            return PREDICTIVE_STATE_CRITICAL
        if stability_score < 35:
            return PREDICTIVE_STATE_UNSTABLE
        if stability_score < 60:
            return PREDICTIVE_STATE_DEGRADING
        if stability_score < 80:
            return PREDICTIVE_STATE_WATCH
        return PREDICTIVE_STATE_STABLE

    def _confidence(
        self,
        *,
        predictions: List[RuntimeStabilityPrediction],
        telemetry: Dict[str, Any],
    ) -> float:
        if not predictions:
            return 0.5

        avg = sum(p.confidence for p in predictions) / max(len(predictions), 1)
        telemetry_quality = min(
            len([k for k in telemetry.keys() if not k.endswith("_error")]) * 0.025,
            0.25,
        )
        error_penalty = min(
            len([k for k in telemetry.keys() if k.endswith("_error")]) * 0.04,
            0.25,
        )

        return round(max(0.05, min(avg + telemetry_quality - error_penalty, 0.98)), 3)

    def _early_warnings(
        self,
        *,
        predictions: List[RuntimeStabilityPrediction],
        predictive_state: str,
    ) -> List[Dict[str, Any]]:
        warnings = []

        for pred in predictions:
            if pred.severity in {PREDICTION_HIGH, PREDICTION_CRITICAL}:
                warnings.append(
                    {
                        "warning_type": pred.prediction_type,
                        "severity": pred.severity,
                        "probability": pred.probability,
                        "confidence": pred.confidence,
                        "target": pred.target,
                        "message": pred.message,
                        "timeline_minutes": pred.projected_timeline_minutes,
                    }
                )

        if predictive_state in {
            PREDICTIVE_STATE_DEGRADING,
            PREDICTIVE_STATE_UNSTABLE,
            PREDICTIVE_STATE_CRITICAL,
        }:
            warnings.append(
                {
                    "warning_type": "PREDICTIVE_RUNTIME_STATE",
                    "severity": (
                        PREDICTION_CRITICAL
                        if predictive_state == PREDICTIVE_STATE_CRITICAL
                        else PREDICTION_HIGH
                    ),
                    "message": f"Runtime predictive state is {predictive_state}.",
                }
            )

        return warnings

    # ========================================================
    # PREDICTION OUTCOMES
    # ========================================================

    def mark_prediction_outcome(
        self,
        *,
        prediction_id: str,
        status: str,
        notes: str = "",
    ) -> Dict[str, Any]:
        prediction = next(
            (
                p for p in self._predictions
                if p.prediction_id == prediction_id
            ),
            None,
        )

        if prediction is None:
            return {
                "ok": False,
                "reason": "prediction_not_found",
            }

        prediction.status = status
        prediction.resolved_at_ms = _now_ms()

        outcome = {
            "prediction_id": prediction_id,
            "status": status,
            "notes": notes,
            "resolved_at_ms": prediction.resolved_at_ms,
        }

        self._prediction_outcomes.append(outcome)
        self._prediction_outcomes = self._prediction_outcomes[-1000:]

        self._emit(
            "PREDICTIVE_RUNTIME_STABILITY_OUTCOME_MARKED",
            outcome,
        )

        return {
            "ok": True,
            "outcome": outcome,
        }

    # ========================================================
    # READS
    # ========================================================

    def list_predictions(
        self,
        *,
        limit: int = 100,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        rows = self._predictions

        if status:
            rows = [
                p for p in rows
                if p.status == status
            ]

        rows = sorted(
            rows,
            key=lambda p: p.created_at_ms,
            reverse=True,
        )

        return [
            p.to_dict()
            for p in rows[:limit]
        ]

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

        return [
            a.to_dict()
            for a in rows[:limit]
        ]

    def list_outcomes(
        self,
        *,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        return list(reversed(self._prediction_outcomes[-limit:]))

    def predictive_status(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
    ) -> Dict[str, Any]:
        latest = self._assessments[-1].to_dict() if self._assessments else None

        pending = len([
            p for p in self._predictions
            if p.status == PREDICTION_PENDING
        ])

        high = len([
            p for p in self._predictions
            if p.severity in {PREDICTION_HIGH, PREDICTION_CRITICAL}
        ])

        return {
            "tenant_id": tenant_id,
            "assessment_count": len(self._assessments),
            "prediction_count": len(self._predictions),
            "pending_predictions": pending,
            "high_risk_predictions": high,
            "outcome_count": len(self._prediction_outcomes),
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
                source="predictive_runtime_stability_engine",
                severity=payload.get("predictive_state") or payload.get("severity") or "INFO",
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


_DEFAULT_PREDICTIVE_RUNTIME_STABILITY_ENGINE: Optional[
    PredictiveRuntimeStabilityEngine
] = None


def get_predictive_runtime_stability_engine(
    *,
    learning_engine: Any = None,
    sovereignty_decision_engine: Any = None,
    adaptive_policy_engine: Any = None,
    mesh_optimizer: Any = None,
    cluster_balancer: Any = None,
    execution_relay: Any = None,
    federated_router: Any = None,
    cluster_manager: Any = None,
    domain_manager: Any = None,
    federation_manager: Any = None,
    storage: Any = None,
    event_bus: Any = None,
    reset: bool = False,
) -> PredictiveRuntimeStabilityEngine:
    global _DEFAULT_PREDICTIVE_RUNTIME_STABILITY_ENGINE

    if reset or _DEFAULT_PREDICTIVE_RUNTIME_STABILITY_ENGINE is None:
        _DEFAULT_PREDICTIVE_RUNTIME_STABILITY_ENGINE = (
            PredictiveRuntimeStabilityEngine(
                learning_engine=learning_engine,
                sovereignty_decision_engine=sovereignty_decision_engine,
                adaptive_policy_engine=adaptive_policy_engine,
                mesh_optimizer=mesh_optimizer,
                cluster_balancer=cluster_balancer,
                execution_relay=execution_relay,
                federated_router=federated_router,
                cluster_manager=cluster_manager,
                domain_manager=domain_manager,
                federation_manager=federation_manager,
                storage=storage,
                event_bus=event_bus,
            )
        )

    return _DEFAULT_PREDICTIVE_RUNTIME_STABILITY_ENGINE