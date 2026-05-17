"""
core/runtime/adaptive_operational_strategy_engine.py

Adaptive Operational Strategy Engine.

Purpose:
- adaptive strategic operational evolution
- strategy performance learning
- mission-aware strategy adaptation
- autonomy/governance/continuity tradeoff evolution
- strategic drift detection
- adaptive strategy generation

Architecture Rules:
- no Streamlit/session_state dependency
- no persistent SQLite connection
- no hidden global mutation
- service-owned strategy memory only
- recommendations before destructive action
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


STRATEGY_STATE_STABLE = "STABLE"
STRATEGY_STATE_WATCH = "WATCH"
STRATEGY_STATE_DRIFTING = "DRIFTING"
STRATEGY_STATE_DEGRADED = "DEGRADED"
STRATEGY_STATE_CRITICAL = "CRITICAL"

PRIORITY_LOW = "LOW"
PRIORITY_MEDIUM = "MEDIUM"
PRIORITY_HIGH = "HIGH"
PRIORITY_CRITICAL = "CRITICAL"

OUTCOME_SUCCESS = "SUCCESS"
OUTCOME_PARTIAL = "PARTIAL"
OUTCOME_FAILED = "FAILED"
OUTCOME_BLOCKED = "BLOCKED"
OUTCOME_UNKNOWN = "UNKNOWN"

ADAPT_OBSERVE = "OBSERVE"
ADAPT_REDUCE_AUTONOMY = "REDUCE_AUTONOMY"
ADAPT_REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
ADAPT_RESTRICT_RELAYS = "RESTRICT_RELAYS"
ADAPT_RESTRICT_FEDERATION = "RESTRICT_FEDERATION"
ADAPT_PROTECT_SOVEREIGN_PATHS = "PROTECT_SOVEREIGN_PATHS"
ADAPT_PRESERVE_CONTINUITY = "PRESERVE_CONTINUITY"
ADAPT_TRIGGER_OPERATIONAL_REASONING = "TRIGGER_OPERATIONAL_REASONING"
ADAPT_TRIGGER_EXECUTION_COGNITION = "TRIGGER_EXECUTION_COGNITION"
ADAPT_TRIGGER_POLICY_REVIEW = "TRIGGER_POLICY_REVIEW"
ADAPT_TRIGGER_MESH_OPTIMIZATION = "TRIGGER_MESH_OPTIMIZATION"
ADAPT_TRIGGER_PREDICTIVE_ASSESSMENT = "TRIGGER_PREDICTIVE_ASSESSMENT"
ADAPT_TRIGGER_RECOVERY = "TRIGGER_RECOVERY"
ADAPT_ESCALATE_GOVERNANCE = "ESCALATE_GOVERNANCE"
ADAPT_RELAX_CONTROLS_CAUTIOUSLY = "RELAX_CONTROLS_CAUTIOUSLY"

DEFAULT_TENANT = "default"


def _now_ms() -> int:
    return int(time.time() * 1000)


@dataclass
class StrategyOutcomeRecord:
    record_id: str
    strategy_type: str
    tenant_id: str = DEFAULT_TENANT
    outcome: str = OUTCOME_UNKNOWN
    effectiveness_score: float = 0.0
    mission_survivability_delta: float = 0.0
    continuity_delta: float = 0.0
    sovereignty_delta: float = 0.0
    governance_delta: float = 0.0
    source: str = "adaptive_operational_strategy_engine"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StrategyDriftSignal:
    signal_id: str
    signal_type: str
    severity: str
    message: str
    tenant_id: str = DEFAULT_TENANT
    target_strategy: Optional[str] = None
    confidence: float = 0.5
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AdaptiveStrategyRecommendation:
    recommendation_id: str
    strategy_type: str
    priority: str
    reason: str
    tenant_id: str = DEFAULT_TENANT
    requires_approval: bool = True
    expected_effect: str = ""
    confidence: float = 0.5
    tradeoffs: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AdaptiveStrategyAssessment:
    assessment_id: str
    tenant_id: str
    strategy_state: str
    adaptation_score: float
    confidence: float
    strategy_health_score: float
    mission_adaptation_score: float
    drift_signals: List[StrategyDriftSignal] = field(default_factory=list)
    recommendations: List[AdaptiveStrategyRecommendation] = field(default_factory=list)
    strategy_profiles: Dict[str, Any] = field(default_factory=dict)
    telemetry: Dict[str, Any] = field(default_factory=dict)
    summary: str = ""
    created_at_ms: int = field(default_factory=_now_ms)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["drift_signals"] = [
            s.to_dict() if hasattr(s, "to_dict") else s
            for s in self.drift_signals
        ]
        data["recommendations"] = [
            r.to_dict() if hasattr(r, "to_dict") else r
            for r in self.recommendations
        ]
        return data


class AdaptiveOperationalStrategyEngine:
    def __init__(
        self,
        *,
        operational_reasoning_engine: Any = None,
        execution_cognition_engine: Any = None,
        predictive_engine: Any = None,
        learning_engine: Any = None,
        adaptive_policy_engine: Any = None,
        mesh_optimizer: Any = None,
        execution_relay: Any = None,
        autonomy_governor: Any = None,
        recovery_manager: Any = None,
        storage: Any = None,
        event_bus: Any = None,
    ) -> None:
        self.storage = storage
        self.operational_reasoning_engine = (
            operational_reasoning_engine
            or getattr(storage, "sovereign_operational_reasoning_engine", None)
        )
        self.execution_cognition_engine = (
            execution_cognition_engine
            or getattr(storage, "autonomous_execution_cognition_engine", None)
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
        self.execution_relay = (
            execution_relay
            or getattr(storage, "cross_runtime_execution_relay", None)
        )
        self.autonomy_governor = (
            autonomy_governor
            or getattr(storage, "autonomy_governor_v2", None)
        )
        self.recovery_manager = (
            recovery_manager
            or getattr(storage, "runtime_recovery_manager", None)
        )
        self.event_bus = event_bus or getattr(storage, "event_bus", None)

        self._outcomes: List[StrategyOutcomeRecord] = []
        self._drift_signals: List[StrategyDriftSignal] = []
        self._recommendations: List[AdaptiveStrategyRecommendation] = []
        self._assessments: List[AdaptiveStrategyAssessment] = []
        self._strategy_profiles: Dict[str, Dict[str, Any]] = {}

    # ========================================================
    # OUTCOME LEARNING
    # ========================================================

    def record_strategy_outcome(
        self,
        *,
        strategy_type: str,
        tenant_id: str = DEFAULT_TENANT,
        outcome: str = OUTCOME_UNKNOWN,
        effectiveness_score: float = 0.0,
        mission_survivability_delta: float = 0.0,
        continuity_delta: float = 0.0,
        sovereignty_delta: float = 0.0,
        governance_delta: float = 0.0,
        source: str = "external",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StrategyOutcomeRecord:
        record = StrategyOutcomeRecord(
            record_id=f"STRAT-OUTCOME-{uuid.uuid4().hex[:12].upper()}",
            strategy_type=strategy_type,
            tenant_id=tenant_id,
            outcome=outcome,
            effectiveness_score=float(effectiveness_score or 0.0),
            mission_survivability_delta=float(mission_survivability_delta or 0.0),
            continuity_delta=float(continuity_delta or 0.0),
            sovereignty_delta=float(sovereignty_delta or 0.0),
            governance_delta=float(governance_delta or 0.0),
            source=source,
            metadata=metadata or {},
        )

        self._outcomes.append(record)
        self._outcomes = self._outcomes[-5000:]

        self._update_strategy_profile(record)

        self._emit(
            "ADAPTIVE_OPERATIONAL_STRATEGY_OUTCOME_RECORDED",
            record.to_dict(),
        )

        return record

    def ingest_current_state(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
    ) -> Dict[str, Any]:
        telemetry = self._collect_telemetry(
            tenant_id=tenant_id,
            objective="ingest_current_strategy_state",
            workload={},
        )

        created: List[StrategyOutcomeRecord] = []

        reasoning = telemetry.get("operational_reasoning_status", {}) or {}
        latest_reasoning = reasoning.get("latest_assessment") or {}

        for strategy in latest_reasoning.get("strategies", []) or []:
            created.append(
                self.record_strategy_outcome(
                    strategy_type=strategy.get("strategy_type", "UNKNOWN_STRATEGY"),
                    tenant_id=tenant_id,
                    outcome=OUTCOME_SUCCESS
                    if latest_reasoning.get("reasoning_state") in {"STABLE", "WATCH"}
                    else OUTCOME_PARTIAL,
                    effectiveness_score=max(
                        0.0,
                        100.0 - float(latest_reasoning.get("strategic_score", 0.0) or 0.0),
                    ),
                    mission_survivability_delta=float(
                        latest_reasoning.get("mission_survivability", 0.0) or 0.0
                    ) - 50.0,
                    continuity_delta=float(
                        latest_reasoning.get("continuity_viability", 0.0) or 0.0
                    ) - 50.0,
                    sovereignty_delta=float(
                        latest_reasoning.get("sovereignty_integrity", 0.0) or 0.0
                    ) - 50.0,
                    source="sovereign_operational_reasoning_engine",
                    metadata=strategy,
                )
            )

        payload = {
            "ok": True,
            "tenant_id": tenant_id,
            "created_outcomes": len(created),
            "record_ids": [r.record_id for r in created],
        }

        self._emit(
            "ADAPTIVE_OPERATIONAL_STRATEGY_STATE_INGESTED",
            payload,
        )

        return payload

    # ========================================================
    # ASSESSMENT
    # ========================================================

    def assess(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        objective: str = "adapt_sovereign_operational_strategy",
        workload: Optional[Dict[str, Any]] = None,
    ) -> AdaptiveStrategyAssessment:
        workload = dict(workload or {})

        telemetry = self._collect_telemetry(
            tenant_id=tenant_id,
            objective=objective,
            workload=workload,
        )

        profiles = self._build_strategy_profiles(
            tenant_id=tenant_id,
        )

        drift = self._detect_strategy_drift(
            tenant_id=tenant_id,
            telemetry=telemetry,
            profiles=profiles,
            workload=workload,
        )

        strategy_health = self._strategy_health_score(
            profiles=profiles,
            drift_signals=drift,
        )

        mission_adaptation = self._mission_adaptation_score(
            telemetry=telemetry,
            drift_signals=drift,
        )

        adaptation_score = self._adaptation_pressure_score(
            strategy_health=strategy_health,
            mission_adaptation=mission_adaptation,
            drift_signals=drift,
            telemetry=telemetry,
        )

        strategy_state = self._strategy_state(
            adaptation_score=adaptation_score,
            drift_signals=drift,
        )

        confidence = self._confidence(
            telemetry=telemetry,
            drift_signals=drift,
            profiles=profiles,
        )

        recommendations = self._recommendations_for(
            tenant_id=tenant_id,
            strategy_state=strategy_state,
            adaptation_score=adaptation_score,
            strategy_health=strategy_health,
            mission_adaptation=mission_adaptation,
            drift_signals=drift,
            telemetry=telemetry,
            workload=workload,
        )

        assessment = AdaptiveStrategyAssessment(
            assessment_id=f"ADAPT-STRATEGY-{uuid.uuid4().hex[:12].upper()}",
            tenant_id=tenant_id,
            strategy_state=strategy_state,
            adaptation_score=adaptation_score,
            confidence=confidence,
            strategy_health_score=strategy_health,
            mission_adaptation_score=mission_adaptation,
            drift_signals=drift,
            recommendations=recommendations,
            strategy_profiles=profiles,
            telemetry=telemetry,
            summary=self._summary(
                strategy_state=strategy_state,
                adaptation_score=adaptation_score,
                confidence=confidence,
                strategy_health=strategy_health,
                mission_adaptation=mission_adaptation,
                drift_count=len(drift),
                recommendation_count=len(recommendations),
            ),
        )

        self._assessments.append(assessment)
        self._assessments = self._assessments[-500:]

        self._drift_signals.extend(drift)
        self._drift_signals = self._drift_signals[-1500:]

        self._recommendations.extend(recommendations)
        self._recommendations = self._recommendations[-1500:]

        self._emit(
            "ADAPTIVE_OPERATIONAL_STRATEGY_ASSESSED",
            assessment.to_dict(),
        )

        return assessment

    def enforce(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
        objective: str = "adapt_sovereign_operational_strategy",
        workload: Optional[Dict[str, Any]] = None,
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        assessment = self.assess(
            tenant_id=tenant_id,
            objective=objective,
            workload=workload or {},
        )

        actions = []

        for rec in assessment.recommendations:
            if dry_run:
                actions.append({
                    "recommendation_id": rec.recommendation_id,
                    "strategy": rec.strategy_type,
                    "status": "DRY_RUN",
                    "reason": rec.reason,
                })
            else:
                actions.append(self._execute_recommendation(rec))

        payload = {
            "ok": True,
            "dry_run": dry_run,
            "assessment": assessment.to_dict(),
            "actions": actions,
        }

        self._emit(
            "ADAPTIVE_OPERATIONAL_STRATEGY_ENFORCED",
            payload,
        )

        return payload

    # ========================================================
    # TELEMETRY
    # ========================================================

    def _collect_telemetry(
        self,
        *,
        tenant_id: str,
        objective: str,
        workload: Dict[str, Any],
    ) -> Dict[str, Any]:
        telemetry: Dict[str, Any] = {
            "tenant_id": tenant_id,
            "objective": objective,
            "workload": workload,
            "collected_at_ms": _now_ms(),
            "strategy_profile_count": len(self._strategy_profiles),
            "outcome_count": len(self._outcomes),
        }

        def capture(key: str, fn) -> None:
            try:
                telemetry[key] = fn()
            except Exception as exc:
                telemetry[f"{key}_error"] = str(exc)

        if self.operational_reasoning_engine is not None:
            capture(
                "operational_reasoning_status",
                lambda: self.operational_reasoning_engine.reasoning_status(
                    tenant_id=tenant_id,
                ),
            )

        if self.execution_cognition_engine is not None:
            capture(
                "execution_cognition_status",
                lambda: self.execution_cognition_engine.cognition_status(
                    tenant_id=tenant_id,
                ),
            )

        if self.predictive_engine is not None:
            capture(
                "predictive_status",
                lambda: self.predictive_engine.predictive_status(
                    tenant_id=tenant_id,
                ),
            )

        if self.learning_engine is not None:
            capture(
                "learning_status",
                lambda: self.learning_engine.learning_status(
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

        if self.execution_relay is not None:
            capture(
                "relay_status",
                lambda: self.execution_relay.relay_status(),
            )

        if self.autonomy_governor is not None:
            capture(
                "governor_status",
                lambda: self.autonomy_governor.governor_status(
                    tenant_id=tenant_id,
                ),
            )

        return telemetry

    # ========================================================
    # STRATEGY PROFILES
    # ========================================================

    def _update_strategy_profile(
        self,
        record: StrategyOutcomeRecord,
    ) -> None:
        profile = self._strategy_profiles.setdefault(
            record.strategy_type,
            {
                "strategy_type": record.strategy_type,
                "events": 0,
                "success": 0,
                "partial": 0,
                "failed": 0,
                "blocked": 0,
                "avg_effectiveness": 0.0,
                "avg_mission_delta": 0.0,
                "avg_continuity_delta": 0.0,
                "avg_sovereignty_delta": 0.0,
                "avg_governance_delta": 0.0,
                "trust_score": 50.0,
                "updated_at_ms": _now_ms(),
            },
        )

        count = int(profile.get("events", 0)) + 1
        old_count = count - 1

        profile["events"] = count

        if record.outcome == OUTCOME_SUCCESS:
            profile["success"] += 1
        elif record.outcome == OUTCOME_PARTIAL:
            profile["partial"] += 1
        elif record.outcome == OUTCOME_FAILED:
            profile["failed"] += 1
        elif record.outcome == OUTCOME_BLOCKED:
            profile["blocked"] += 1

        for field_name, value in [
            ("avg_effectiveness", record.effectiveness_score),
            ("avg_mission_delta", record.mission_survivability_delta),
            ("avg_continuity_delta", record.continuity_delta),
            ("avg_sovereignty_delta", record.sovereignty_delta),
            ("avg_governance_delta", record.governance_delta),
        ]:
            prev = float(profile.get(field_name, 0.0) or 0.0)
            profile[field_name] = round(
                ((prev * old_count) + float(value or 0.0)) / max(count, 1),
                2,
            )

        failure_penalty = profile["failed"] * 8.0 + profile["blocked"] * 6.0
        success_bonus = profile["success"] * 2.0 + profile["partial"] * 0.75

        profile["trust_score"] = round(
            max(
                0.0,
                min(
                    100.0,
                    float(profile["avg_effectiveness"] or 0.0)
                    + success_bonus
                    - failure_penalty,
                ),
            ),
            2,
        )

        profile["updated_at_ms"] = _now_ms()

    def _build_strategy_profiles(
        self,
        *,
        tenant_id: str,
    ) -> Dict[str, Any]:
        return {
            key: dict(value)
            for key, value in self._strategy_profiles.items()
        }

    # ========================================================
    # DRIFT DETECTION
    # ========================================================

    def _detect_strategy_drift(
        self,
        *,
        tenant_id: str,
        telemetry: Dict[str, Any],
        profiles: Dict[str, Any],
        workload: Dict[str, Any],
    ) -> List[StrategyDriftSignal]:
        signals: List[StrategyDriftSignal] = []

        for strategy_type, profile in profiles.items():
            trust = float(profile.get("trust_score", 50.0) or 50.0)
            failed = int(profile.get("failed", 0) or 0)
            blocked = int(profile.get("blocked", 0) or 0)
            events = int(profile.get("events", 0) or 0)

            if events >= 3 and trust < 45:
                signals.append(
                    self._drift(
                        signal_type="LOW_STRATEGY_TRUST",
                        severity=PRIORITY_HIGH,
                        message=f"Strategy {strategy_type} has low trust score.",
                        tenant_id=tenant_id,
                        target_strategy=strategy_type,
                        confidence=0.75,
                        evidence=[profile],
                    )
                )

            if failed + blocked >= 3:
                signals.append(
                    self._drift(
                        signal_type="RECURRING_STRATEGY_FAILURE",
                        severity=PRIORITY_HIGH,
                        message=f"Strategy {strategy_type} shows recurring failure/block patterns.",
                        tenant_id=tenant_id,
                        target_strategy=strategy_type,
                        confidence=0.8,
                        evidence=[profile],
                    )
                )

        reasoning = (
            telemetry.get("operational_reasoning_status", {})
            .get("latest_assessment")
            or {}
        )

        if str(reasoning.get("reasoning_state") or "").upper() in {
            "DEGRADED",
            "CRITICAL",
        }:
            signals.append(
                self._drift(
                    signal_type="STRATEGIC_REASONING_DEGRADATION",
                    severity=PRIORITY_HIGH,
                    message="Operational reasoning state indicates strategic degradation.",
                    tenant_id=tenant_id,
                    confidence=float(reasoning.get("confidence", 0.7) or 0.7),
                    evidence=[reasoning],
                )
            )

        predictive = (
            telemetry.get("predictive_status", {})
            .get("latest_assessment")
            or {}
        )

        if str(predictive.get("predictive_state") or "").upper() in {
            "DEGRADING",
            "UNSTABLE",
            "CRITICAL",
        }:
            signals.append(
                self._drift(
                    signal_type="PREDICTIVE_STRATEGY_PRESSURE",
                    severity=PRIORITY_HIGH,
                    message="Predictive engine indicates strategy should adapt before instability.",
                    tenant_id=tenant_id,
                    confidence=float(predictive.get("confidence", 0.65) or 0.65),
                    evidence=[predictive],
                )
            )

        relay = telemetry.get("relay_status", {}) or {}
        if int(relay.get("failed", 0) or 0) > 0 or int(relay.get("blocked", 0) or 0) > 0:
            signals.append(
                self._drift(
                    signal_type="CONTINUITY_STRATEGY_DRIFT",
                    severity=PRIORITY_HIGH,
                    message="Relay failures or blocks indicate continuity strategy drift.",
                    tenant_id=tenant_id,
                    confidence=0.72,
                    evidence=[relay],
                )
            )

        categories = {str(c).upper() for c in workload.get("categories", [])}
        if categories.intersection({"CUI", "ITAR", "EXPORT_CONTROLLED", "CLASSIFIED", "FEDRAMP_HIGH"}):
            signals.append(
                self._drift(
                    signal_type="HIGH_SENSITIVITY_STRATEGY_CONTEXT",
                    severity=PRIORITY_HIGH,
                    message="High-sensitivity workload requires hardened strategy posture.",
                    tenant_id=tenant_id,
                    confidence=0.85,
                    evidence=[{"categories": sorted(categories)}],
                )
            )

        return signals

    def _drift(
        self,
        *,
        signal_type: str,
        severity: str,
        message: str,
        tenant_id: str,
        target_strategy: Optional[str] = None,
        confidence: float = 0.5,
        evidence: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> StrategyDriftSignal:
        return StrategyDriftSignal(
            signal_id=f"STRAT-DRIFT-{uuid.uuid4().hex[:12].upper()}",
            signal_type=signal_type,
            severity=severity,
            message=message,
            tenant_id=tenant_id,
            target_strategy=target_strategy,
            confidence=round(max(0.0, min(confidence, 1.0)), 3),
            evidence=evidence or [],
            metadata=metadata or {},
        )

    # ========================================================
    # SCORING
    # ========================================================

    def _strategy_health_score(
        self,
        *,
        profiles: Dict[str, Any],
        drift_signals: List[StrategyDriftSignal],
    ) -> float:
        if not profiles:
            baseline = 70.0
        else:
            baseline = sum(
                float(p.get("trust_score", 50.0) or 50.0)
                for p in profiles.values()
            ) / max(len(profiles), 1)

        baseline -= len(drift_signals) * 4.0

        return round(max(0.0, min(baseline, 100.0)), 2)

    def _mission_adaptation_score(
        self,
        *,
        telemetry: Dict[str, Any],
        drift_signals: List[StrategyDriftSignal],
    ) -> float:
        reasoning = (
            telemetry.get("operational_reasoning_status", {})
            .get("latest_assessment")
            or {}
        )

        mission = float(reasoning.get("mission_survivability", 75.0) or 75.0)
        continuity = float(reasoning.get("continuity_viability", 75.0) or 75.0)
        sovereignty = float(reasoning.get("sovereignty_integrity", 75.0) or 75.0)

        score = (mission + continuity + sovereignty) / 3.0
        score -= len(drift_signals) * 3.0

        return round(max(0.0, min(score, 100.0)), 2)

    def _adaptation_pressure_score(
        self,
        *,
        strategy_health: float,
        mission_adaptation: float,
        drift_signals: List[StrategyDriftSignal],
        telemetry: Dict[str, Any],
    ) -> float:
        pressure = 0.0

        pressure += max(0.0, 100.0 - strategy_health) * 0.45
        pressure += max(0.0, 100.0 - mission_adaptation) * 0.45

        severity_weight = {
            PRIORITY_LOW: 2.0,
            PRIORITY_MEDIUM: 8.0,
            PRIORITY_HIGH: 16.0,
            PRIORITY_CRITICAL: 30.0,
        }

        for signal in drift_signals:
            pressure += severity_weight.get(signal.severity, 8.0) * float(
                signal.confidence or 0.5
            )

        return round(max(0.0, min(pressure, 100.0)), 2)

    def _strategy_state(
        self,
        *,
        adaptation_score: float,
        drift_signals: List[StrategyDriftSignal],
    ) -> str:
        if any(s.severity == PRIORITY_CRITICAL for s in drift_signals):
            return STRATEGY_STATE_CRITICAL
        if adaptation_score >= 80:
            return STRATEGY_STATE_CRITICAL
        if adaptation_score >= 60:
            return STRATEGY_STATE_DEGRADED
        if adaptation_score >= 40:
            return STRATEGY_STATE_DRIFTING
        if adaptation_score >= 20:
            return STRATEGY_STATE_WATCH
        return STRATEGY_STATE_STABLE

    def _confidence(
        self,
        *,
        telemetry: Dict[str, Any],
        drift_signals: List[StrategyDriftSignal],
        profiles: Dict[str, Any],
    ) -> float:
        drift_conf = (
            sum(float(s.confidence or 0.5) for s in drift_signals)
            / max(len(drift_signals), 1)
            if drift_signals
            else 0.55
        )

        profile_component = min(len(profiles) * 0.04, 0.20)
        telemetry_component = min(
            len([k for k in telemetry.keys() if not k.endswith("_error")]) * 0.025,
            0.25,
        )
        error_penalty = min(
            len([k for k in telemetry.keys() if k.endswith("_error")]) * 0.04,
            0.25,
        )

        return round(max(0.05, min(drift_conf + profile_component + telemetry_component - error_penalty, 0.98)), 3)

    # ========================================================
    # RECOMMENDATIONS
    # ========================================================

    def _recommendations_for(
        self,
        *,
        tenant_id: str,
        strategy_state: str,
        adaptation_score: float,
        strategy_health: float,
        mission_adaptation: float,
        drift_signals: List[StrategyDriftSignal],
        telemetry: Dict[str, Any],
        workload: Dict[str, Any],
    ) -> List[AdaptiveStrategyRecommendation]:
        recs: List[AdaptiveStrategyRecommendation] = []
        seen = set()
        drift_types = {s.signal_type for s in drift_signals}

        def add(
            strategy_type: str,
            priority: str,
            reason: str,
            *,
            expected_effect: str,
            confidence: float = 0.6,
            tradeoffs: Optional[List[str]] = None,
            requires_approval: bool = True,
            metadata: Optional[Dict[str, Any]] = None,
        ) -> None:
            key = (strategy_type, reason)
            if key in seen:
                return
            seen.add(key)
            recs.append(
                AdaptiveStrategyRecommendation(
                    recommendation_id=f"ADAPT-REC-{uuid.uuid4().hex[:12].upper()}",
                    strategy_type=strategy_type,
                    priority=priority,
                    reason=reason,
                    tenant_id=tenant_id,
                    requires_approval=requires_approval,
                    expected_effect=expected_effect,
                    confidence=round(max(0.0, min(confidence, 1.0)), 3),
                    tradeoffs=tradeoffs or [],
                    metadata=metadata or {},
                )
            )

        if not drift_signals:
            add(
                ADAPT_OBSERVE,
                PRIORITY_LOW,
                "No strategic drift detected.",
                expected_effect="Maintain current operational strategy.",
                requires_approval=False,
            )
            return recs

        if strategy_state in {STRATEGY_STATE_DEGRADED, STRATEGY_STATE_CRITICAL}:
            add(
                ADAPT_ESCALATE_GOVERNANCE,
                PRIORITY_HIGH if strategy_state == STRATEGY_STATE_DEGRADED else PRIORITY_CRITICAL,
                "Escalate governance due to degraded adaptive strategy state.",
                expected_effect="Increase command oversight and reduce unsafe drift.",
            )
            add(
                ADAPT_TRIGGER_OPERATIONAL_REASONING,
                PRIORITY_HIGH,
                "Refresh sovereign operational reasoning under strategy degradation.",
                expected_effect="Generate updated mission-aware strategy.",
                requires_approval=False,
            )

        if "CONTINUITY_STRATEGY_DRIFT" in drift_types:
            add(
                ADAPT_PRESERVE_CONTINUITY,
                PRIORITY_HIGH,
                "Adapt continuity strategy due to relay failures or blocked continuity paths.",
                expected_effect="Improve mission continuity survivability.",
                tradeoffs=["may restrict routing", "may increase governance approvals"],
            )
            add(
                ADAPT_RESTRICT_RELAYS,
                PRIORITY_HIGH,
                "Restrict relays until continuity strategy stabilizes.",
                expected_effect="Reduce relay-induced propagation risk.",
            )

        if "HIGH_SENSITIVITY_STRATEGY_CONTEXT" in drift_types:
            add(
                ADAPT_PROTECT_SOVEREIGN_PATHS,
                PRIORITY_HIGH,
                "Protect sovereign execution paths for high-sensitivity workload context.",
                expected_effect="Improve sovereignty preservation.",
                tradeoffs=["may reduce throughput", "may require approvals"],
            )
            add(
                ADAPT_REQUIRE_APPROVAL,
                PRIORITY_HIGH,
                "Require approval for high-sensitivity adaptive strategy execution.",
                expected_effect="Improve audit defensibility and governance control.",
            )

        if "PREDICTIVE_STRATEGY_PRESSURE" in drift_types:
            add(
                ADAPT_TRIGGER_PREDICTIVE_ASSESSMENT,
                PRIORITY_MEDIUM,
                "Refresh predictive assessment before strategy drift worsens.",
                expected_effect="Improve anticipatory strategy quality.",
                requires_approval=False,
            )
            add(
                ADAPT_TRIGGER_MESH_OPTIMIZATION,
                PRIORITY_MEDIUM,
                "Optimize mesh topology to reduce predicted strategy pressure.",
                expected_effect="Reduce future topology instability.",
                requires_approval=False,
            )

        if "STRATEGIC_REASONING_DEGRADATION" in drift_types:
            add(
                ADAPT_REDUCE_AUTONOMY,
                PRIORITY_HIGH,
                "Reduce autonomy due to strategic reasoning degradation.",
                expected_effect="Improve controlled governance posture.",
            )
            add(
                ADAPT_TRIGGER_POLICY_REVIEW,
                PRIORITY_HIGH,
                "Review adaptive policy due to strategic reasoning degradation.",
                expected_effect="Reduce governance drift.",
                requires_approval=False,
            )

        if "LOW_STRATEGY_TRUST" in drift_types or "RECURRING_STRATEGY_FAILURE" in drift_types:
            add(
                ADAPT_TRIGGER_RECOVERY,
                PRIORITY_HIGH,
                "Trigger recovery because strategy outcome history indicates degraded effectiveness.",
                expected_effect="Restore reliable operational pathways.",
                requires_approval=False,
            )

        if strategy_health > 85 and mission_adaptation > 85 and strategy_state == STRATEGY_STATE_STABLE:
            add(
                ADAPT_RELAX_CONTROLS_CAUTIOUSLY,
                PRIORITY_LOW,
                "Strategy health is strong; cautious relaxation may improve throughput.",
                expected_effect="Improve operational efficiency while preserving guardrails.",
            )

        return recs

    # ========================================================
    # EXECUTION HELPERS
    # ========================================================

    def _execute_recommendation(
        self,
        rec: AdaptiveStrategyRecommendation,
    ) -> Dict[str, Any]:
        try:
            if rec.strategy_type == ADAPT_TRIGGER_OPERATIONAL_REASONING:
                return self._trigger_operational_reasoning(rec)

            if rec.strategy_type == ADAPT_TRIGGER_EXECUTION_COGNITION:
                return self._trigger_execution_cognition(rec)

            if rec.strategy_type == ADAPT_TRIGGER_POLICY_REVIEW:
                return self._trigger_policy(rec)

            if rec.strategy_type == ADAPT_TRIGGER_MESH_OPTIMIZATION:
                return self._trigger_mesh(rec)

            if rec.strategy_type == ADAPT_TRIGGER_PREDICTIVE_ASSESSMENT:
                return self._trigger_predictive(rec)

            if rec.strategy_type == ADAPT_TRIGGER_RECOVERY:
                return self._trigger_recovery(rec)

            if rec.strategy_type == ADAPT_REDUCE_AUTONOMY:
                return self._reduce_autonomy(rec)

            return {
                "recommendation_id": rec.recommendation_id,
                "strategy": rec.strategy_type,
                "status": "RECOMMENDED",
                "manual_or_policy_update_required": True,
                "reason": rec.reason,
            }

        except Exception as exc:
            return {
                "recommendation_id": rec.recommendation_id,
                "strategy": rec.strategy_type,
                "status": "FAILED",
                "error": str(exc),
            }

    def _trigger_operational_reasoning(
        self,
        rec: AdaptiveStrategyRecommendation,
    ) -> Dict[str, Any]:
        if self.operational_reasoning_engine is None:
            return {"status": "SKIPPED", "reason": "operational_reasoning_engine_unavailable"}

        assessment = self.operational_reasoning_engine.assess(
            tenant_id=rec.tenant_id,
            objective="adaptive_strategy_refresh",
            workload={
                "action": "ADAPTIVE_STRATEGY_REASONING_REFRESH",
                "source": "adaptive_operational_strategy_engine",
            },
        )

        return {"status": "EXECUTED", "assessment": assessment.to_dict()}

    def _trigger_execution_cognition(
        self,
        rec: AdaptiveStrategyRecommendation,
    ) -> Dict[str, Any]:
        if self.execution_cognition_engine is None:
            return {"status": "SKIPPED", "reason": "execution_cognition_engine_unavailable"}

        assessment = self.execution_cognition_engine.assess(
            tenant_id=rec.tenant_id,
            workload={
                "action": "ADAPTIVE_STRATEGY_EXECUTION_COGNITION_REFRESH",
                "source": "adaptive_operational_strategy_engine",
            },
        )

        return {"status": "EXECUTED", "assessment": assessment.to_dict()}

    def _trigger_policy(
        self,
        rec: AdaptiveStrategyRecommendation,
    ) -> Dict[str, Any]:
        if self.adaptive_policy_engine is None:
            return {"status": "SKIPPED", "reason": "adaptive_policy_engine_unavailable"}

        assessment = self.adaptive_policy_engine.assess(
            tenant_id=rec.tenant_id,
            workload={
                "action": "ADAPTIVE_STRATEGY_POLICY_REVIEW",
                "source": "adaptive_operational_strategy_engine",
            },
        )

        return {"status": "EXECUTED", "assessment": assessment.to_dict()}

    def _trigger_mesh(
        self,
        rec: AdaptiveStrategyRecommendation,
    ) -> Dict[str, Any]:
        if self.mesh_optimizer is None:
            return {"status": "SKIPPED", "reason": "mesh_optimizer_unavailable"}

        result = self.mesh_optimizer.enforce(
            tenant_id=rec.tenant_id,
            dry_run=True,
        )

        return {"status": "EXECUTED", "result": result}

    def _trigger_predictive(
        self,
        rec: AdaptiveStrategyRecommendation,
    ) -> Dict[str, Any]:
        if self.predictive_engine is None:
            return {"status": "SKIPPED", "reason": "predictive_engine_unavailable"}

        assessment = self.predictive_engine.assess(
            tenant_id=rec.tenant_id,
        )

        return {"status": "EXECUTED", "assessment": assessment.to_dict()}

    def _trigger_recovery(
        self,
        rec: AdaptiveStrategyRecommendation,
    ) -> Dict[str, Any]:
        if self.recovery_manager is None:
            return {"status": "SKIPPED", "reason": "recovery_manager_unavailable"}

        result = self.recovery_manager.auto_recover(
            tenant_id=rec.tenant_id,
            actor="adaptive_operational_strategy_engine",
            force=False,
        )

        return {
            "status": "EXECUTED",
            "result": result.to_dict() if hasattr(result, "to_dict") else {},
        }

    def _reduce_autonomy(
        self,
        rec: AdaptiveStrategyRecommendation,
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

    def list_outcomes(
        self,
        *,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        rows = sorted(
            self._outcomes,
            key=lambda r: r.created_at_ms,
            reverse=True,
        )
        return [r.to_dict() for r in rows[:limit]]

    def list_drift_signals(
        self,
        *,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        rows = sorted(
            self._drift_signals,
            key=lambda r: r.created_at_ms,
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

    def list_assessments(
        self,
        *,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        rows = sorted(
            self._assessments,
            key=lambda r: r.created_at_ms,
            reverse=True,
        )
        return [r.to_dict() for r in rows[:limit]]

    def strategy_profiles(
        self,
    ) -> Dict[str, Any]:
        return {
            key: dict(value)
            for key, value in self._strategy_profiles.items()
        }

    def strategy_status(
        self,
        *,
        tenant_id: str = DEFAULT_TENANT,
    ) -> Dict[str, Any]:
        latest = self._assessments[-1].to_dict() if self._assessments else None

        return {
            "tenant_id": tenant_id,
            "outcome_count": len(self._outcomes),
            "drift_signal_count": len(self._drift_signals),
            "recommendation_count": len(self._recommendations),
            "assessment_count": len(self._assessments),
            "strategy_profile_count": len(self._strategy_profiles),
            "latest_assessment": latest,
        }

    # ========================================================
    # SUMMARY / EVENTS
    # ========================================================

    def _summary(
        self,
        *,
        strategy_state: str,
        adaptation_score: float,
        confidence: float,
        strategy_health: float,
        mission_adaptation: float,
        drift_count: int,
        recommendation_count: int,
    ) -> str:
        return (
            f"Adaptive strategy state={strategy_state}, "
            f"adaptation_pressure={adaptation_score}, confidence={confidence}. "
            f"Strategy health={strategy_health}, mission adaptation={mission_adaptation}. "
            f"Drift signals={drift_count}, recommendations={recommendation_count}."
        )

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
                source="adaptive_operational_strategy_engine",
                severity=payload.get("strategy_state") or "INFO",
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


_DEFAULT_ADAPTIVE_OPERATIONAL_STRATEGY_ENGINE: Optional[
    AdaptiveOperationalStrategyEngine
] = None


def get_adaptive_operational_strategy_engine(
    *,
    operational_reasoning_engine: Any = None,
    execution_cognition_engine: Any = None,
    predictive_engine: Any = None,
    learning_engine: Any = None,
    adaptive_policy_engine: Any = None,
    mesh_optimizer: Any = None,
    execution_relay: Any = None,
    autonomy_governor: Any = None,
    recovery_manager: Any = None,
    storage: Any = None,
    event_bus: Any = None,
    reset: bool = False,
) -> AdaptiveOperationalStrategyEngine:
    global _DEFAULT_ADAPTIVE_OPERATIONAL_STRATEGY_ENGINE

    if reset or _DEFAULT_ADAPTIVE_OPERATIONAL_STRATEGY_ENGINE is None:
        _DEFAULT_ADAPTIVE_OPERATIONAL_STRATEGY_ENGINE = (
            AdaptiveOperationalStrategyEngine(
                operational_reasoning_engine=operational_reasoning_engine,
                execution_cognition_engine=execution_cognition_engine,
                predictive_engine=predictive_engine,
                learning_engine=learning_engine,
                adaptive_policy_engine=adaptive_policy_engine,
                mesh_optimizer=mesh_optimizer,
                execution_relay=execution_relay,
                autonomy_governor=autonomy_governor,
                recovery_manager=recovery_manager,
                storage=storage,
                event_bus=event_bus,
            )
        )

    return _DEFAULT_ADAPTIVE_OPERATIONAL_STRATEGY_ENGINE