"""
core/runtime/sovereign_global_risk_forecasting_engine.py

Sovereign Global Risk Forecasting Engine

Planetary-scale sovereign predictive cognition engine.

Forecasts:
- global operational instability
- escalation trajectories
- continuity degradation futures
- sovereignty destabilization futures
- infrastructure destabilization futures
- resilience stabilization futures
- strategic recovery futures

IMPORTANT:
This subsystem DOES NOT:
- execute operational changes
- bypass governance
- mutate infrastructure
- perform offensive actions
- make autonomous destructive decisions

It ONLY:
- forecast sovereign global risk
- model future-state trajectories
- project escalation and recovery paths
- provide replayable forecasting lineage/evidence
"""

from __future__ import annotations

import statistics
import time
import uuid

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


DEFAULT_ENGINE_NAME = "sovereign_global_risk_forecasting_engine"
DEFAULT_FORECAST_DEPTH = 16


FORECAST_STATE_STABLE = "STABLE"
FORECAST_STATE_WATCH = "WATCH"
FORECAST_STATE_ELEVATED = "ELEVATED"
FORECAST_STATE_ESCALATING = "ESCALATING"
FORECAST_STATE_CONTINUITY_DEGRADING = "CONTINUITY_DEGRADING"
FORECAST_STATE_SOVEREIGNTY_DEGRADING = "SOVEREIGNTY_DEGRADING"
FORECAST_STATE_SYSTEMIC_RISK = "SYSTEMIC_RISK"
FORECAST_STATE_GLOBAL_CRITICAL = "GLOBAL_CRITICAL"

TRAJECTORY_STABILIZING = "STABILIZING"
TRAJECTORY_MONITORING = "MONITORING"
TRAJECTORY_ESCALATING = "ESCALATING"
TRAJECTORY_FRAGMENTING = "FRAGMENTING"
TRAJECTORY_SYSTEMIC_DEGRADATION = "SYSTEMIC_DEGRADATION"
TRAJECTORY_RECOVERY = "RECOVERY"

ACTION_MONITOR = "MONITOR"
ACTION_FORECAST_REVIEW = "FORECAST_REVIEW"
ACTION_ESCALATION_CONTAINMENT = "ESCALATION_CONTAINMENT"
ACTION_CONTINUITY_RESTORATION = "CONTINUITY_RESTORATION"
ACTION_SOVEREIGNTY_STABILIZATION = "SOVEREIGNTY_STABILIZATION"
ACTION_GLOBAL_RESILIENCE_SURGE = "GLOBAL_RESILIENCE_SURGE"
ACTION_STRATEGIC_RECOVERY = "STRATEGIC_RECOVERY"


class GlobalForecastSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class GlobalRiskForecastSignal:
    signal_id: str

    source_engine: str
    severity: str
    confidence: float
    summary: str

    tenant_id: Optional[str] = None
    mission_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    global_instability_score: float = 0.0
    escalation_probability_score: float = 0.0
    continuity_degradation_score: float = 0.0
    sovereignty_degradation_score: float = 0.0
    infrastructure_destabilization_score: float = 0.0
    ecosystem_fragility_score: float = 0.0
    geopolitical_pressure_score: float = 0.0
    resilience_exhaustion_score: float = 0.0
    recovery_capacity_score: float = 100.0
    survivability_score: float = 100.0
    uncertainty_score: float = 0.0

    payload: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(
        default_factory=lambda: int(time.time() * 1000)
    )


@dataclass(frozen=True)
class GlobalRiskForecastStep:
    step_id: str
    step_index: int

    forecast_state: str
    trajectory: str

    global_instability_score: float
    escalation_probability_score: float
    continuity_degradation_score: float
    sovereignty_degradation_score: float
    infrastructure_destabilization_score: float
    ecosystem_fragility_score: float
    resilience_exhaustion_score: float
    recovery_capacity_score: float
    survivability_score: float

    global_risk_score: float
    recovery_probability: float
    systemic_risk_probability: float

    rationale: str

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GlobalRiskProjection:
    projection_id: str

    projected_state: str
    trajectory: str

    global_risk_projection_score: float
    escalation_projection_score: float
    continuity_projection_score: float
    sovereignty_projection_score: float
    recovery_projection_score: float
    survivability_projection_score: float

    rationale: str

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GlobalRiskForecastDirective:
    directive_id: str

    directive_name: str
    action_type: str
    priority: str

    expected_risk_reduction: float
    expected_recovery_gain: float
    expected_sovereignty_gain: float
    expected_continuity_gain: float

    rationale: str

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SovereignGlobalRiskForecastAssessment:
    assessment_id: str

    forecast_state: str
    trajectory: str
    recommended_action: str

    global_instability_score: float
    escalation_probability_score: float
    continuity_degradation_score: float
    sovereignty_degradation_score: float
    infrastructure_destabilization_score: float
    ecosystem_fragility_score: float
    geopolitical_pressure_score: float
    resilience_exhaustion_score: float
    recovery_capacity_score: float
    survivability_score: float
    uncertainty_score: float

    global_risk_score: float
    recovery_probability: float
    systemic_risk_probability: float

    confidence: float
    explainability_score: float

    signal_count: int
    engine_count: int

    severity: str

    tenant_id: Optional[str]
    mission_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    strategic_projection: GlobalRiskProjection

    forecast_steps: List[GlobalRiskForecastStep]
    directives: List[GlobalRiskForecastDirective]

    telemetry_fusion: Dict[str, Any]

    rationale: str

    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(
        default_factory=lambda: int(time.time() * 1000)
    )


class SovereignGlobalRiskForecastingEngine:
    """
    Planetary-scale sovereign predictive risk cognition.
    """

    def __init__(
        self,
        *,
        engine_name: str = DEFAULT_ENGINE_NAME,
        event_bus: Optional[Any] = None,
        global_command_integrator: Optional[Any] = None,
        geopolitical_resilience_engine: Optional[Any] = None,
        ecosystem_resilience_engine: Optional[Any] = None,
        mesh_autonomy_engine: Optional[Any] = None,
        sovereignty_assurance_engine: Optional[Any] = None,
        operational_memory_engine: Optional[Any] = None,
        lineage_engine: Optional[Any] = None,
        fedramp_evidence_lineage_engine: Optional[Any] = None,
    ) -> None:
        self.engine_name = engine_name
        self.event_bus = event_bus
        self.global_command_integrator = global_command_integrator
        self.geopolitical_resilience_engine = geopolitical_resilience_engine
        self.ecosystem_resilience_engine = ecosystem_resilience_engine
        self.mesh_autonomy_engine = mesh_autonomy_engine
        self.sovereignty_assurance_engine = sovereignty_assurance_engine
        self.operational_memory_engine = operational_memory_engine
        self.lineage_engine = lineage_engine
        self.fedramp_evidence_lineage_engine = fedramp_evidence_lineage_engine

        self._assessments: List[SovereignGlobalRiskForecastAssessment] = []

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def evaluate(
        self,
        signals: Sequence[GlobalRiskForecastSignal | Dict[str, Any]],
        *,
        forecast_depth: int = DEFAULT_FORECAST_DEPTH,
        tenant_id: Optional[str] = None,
        mission_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> SovereignGlobalRiskForecastAssessment:
        normalized = [
            self._normalize_signal(
                item,
                tenant_id=tenant_id,
                mission_id=mission_id,
                case_id=case_id,
                correlation_id=correlation_id,
            )
            for item in signals
        ]

        if not normalized:
            assessment = self._empty_assessment(
                tenant_id=tenant_id,
                mission_id=mission_id,
                case_id=case_id,
                correlation_id=correlation_id,
            )
            self._record_assessment(assessment, context=context)
            return assessment

        selected = self._select_primary_signal(normalized)

        global_instability = self._avg_score(
            [s.global_instability_score for s in normalized]
        )
        escalation_probability = self._avg_score(
            [s.escalation_probability_score for s in normalized]
        )
        continuity_degradation = self._avg_score(
            [s.continuity_degradation_score for s in normalized]
        )
        sovereignty_degradation = self._avg_score(
            [s.sovereignty_degradation_score for s in normalized]
        )
        infrastructure_destabilization = self._avg_score(
            [s.infrastructure_destabilization_score for s in normalized]
        )
        ecosystem_fragility = self._avg_score(
            [s.ecosystem_fragility_score for s in normalized]
        )
        geopolitical_pressure = self._avg_score(
            [s.geopolitical_pressure_score for s in normalized]
        )
        resilience_exhaustion = self._avg_score(
            [s.resilience_exhaustion_score for s in normalized]
        )
        recovery_capacity = self._avg_score(
            [s.recovery_capacity_score for s in normalized],
            default=100.0,
        )
        survivability = self._avg_score(
            [s.survivability_score for s in normalized],
            default=100.0,
        )
        uncertainty = self._avg_score(
            [s.uncertainty_score for s in normalized]
        )

        recovery_probability = self._recovery_probability(
            recovery_capacity_score=recovery_capacity,
            survivability_score=survivability,
            continuity_degradation_score=continuity_degradation,
            sovereignty_degradation_score=sovereignty_degradation,
            resilience_exhaustion_score=resilience_exhaustion,
        )

        systemic_risk_probability = self._systemic_risk_probability(
            global_instability_score=global_instability,
            escalation_probability_score=escalation_probability,
            continuity_degradation_score=continuity_degradation,
            sovereignty_degradation_score=sovereignty_degradation,
            infrastructure_destabilization_score=infrastructure_destabilization,
            ecosystem_fragility_score=ecosystem_fragility,
            geopolitical_pressure_score=geopolitical_pressure,
            uncertainty_score=uncertainty,
        )

        global_risk = self._global_risk_score(
            global_instability_score=global_instability,
            escalation_probability_score=escalation_probability,
            continuity_degradation_score=continuity_degradation,
            sovereignty_degradation_score=sovereignty_degradation,
            infrastructure_destabilization_score=infrastructure_destabilization,
            ecosystem_fragility_score=ecosystem_fragility,
            geopolitical_pressure_score=geopolitical_pressure,
            resilience_exhaustion_score=resilience_exhaustion,
            uncertainty_score=uncertainty,
            recovery_probability=recovery_probability,
            systemic_risk_probability=systemic_risk_probability,
            survivability_score=survivability,
        )

        forecast_state = self._forecast_state(
            global_risk_score=global_risk,
            escalation_probability_score=escalation_probability,
            continuity_degradation_score=continuity_degradation,
            sovereignty_degradation_score=sovereignty_degradation,
            systemic_risk_probability=systemic_risk_probability,
            survivability_score=survivability,
        )

        trajectory = self._trajectory(
            forecast_state=forecast_state,
            recovery_probability=recovery_probability,
            systemic_risk_probability=systemic_risk_probability,
            escalation_probability_score=escalation_probability,
        )

        recommended_action = self._recommended_action(
            forecast_state=forecast_state,
            trajectory=trajectory,
            recovery_probability=recovery_probability,
        )

        projection = self._projection(
            forecast_state=forecast_state,
            trajectory=trajectory,
            global_risk_score=global_risk,
            escalation_probability_score=escalation_probability,
            continuity_degradation_score=continuity_degradation,
            sovereignty_degradation_score=sovereignty_degradation,
            recovery_capacity_score=recovery_capacity,
            survivability_score=survivability,
        )

        steps = self._forecast_steps(
            forecast_state=forecast_state,
            trajectory=trajectory,
            global_instability_score=global_instability,
            escalation_probability_score=escalation_probability,
            continuity_degradation_score=continuity_degradation,
            sovereignty_degradation_score=sovereignty_degradation,
            infrastructure_destabilization_score=infrastructure_destabilization,
            ecosystem_fragility_score=ecosystem_fragility,
            resilience_exhaustion_score=resilience_exhaustion,
            recovery_capacity_score=recovery_capacity,
            survivability_score=survivability,
            depth=forecast_depth,
        )

        directives = self._directives(
            recommended_action=recommended_action,
            global_risk_score=global_risk,
            recovery_capacity_score=recovery_capacity,
            sovereignty_degradation_score=sovereignty_degradation,
            continuity_degradation_score=continuity_degradation,
        )

        assessment = SovereignGlobalRiskForecastAssessment(
            assessment_id=str(uuid.uuid4()),
            forecast_state=forecast_state,
            trajectory=trajectory,
            recommended_action=recommended_action,
            global_instability_score=global_instability,
            escalation_probability_score=escalation_probability,
            continuity_degradation_score=continuity_degradation,
            sovereignty_degradation_score=sovereignty_degradation,
            infrastructure_destabilization_score=infrastructure_destabilization,
            ecosystem_fragility_score=ecosystem_fragility,
            geopolitical_pressure_score=geopolitical_pressure,
            resilience_exhaustion_score=resilience_exhaustion,
            recovery_capacity_score=recovery_capacity,
            survivability_score=survivability,
            uncertainty_score=uncertainty,
            global_risk_score=global_risk,
            recovery_probability=recovery_probability,
            systemic_risk_probability=systemic_risk_probability,
            confidence=self._confidence(normalized),
            explainability_score=self._explainability_score(normalized),
            signal_count=len(normalized),
            engine_count=len({s.source_engine for s in normalized}),
            severity=selected.severity,
            tenant_id=tenant_id or selected.tenant_id,
            mission_id=mission_id or selected.mission_id,
            case_id=case_id or selected.case_id,
            correlation_id=correlation_id or selected.correlation_id,
            strategic_projection=projection,
            forecast_steps=steps,
            directives=directives,
            telemetry_fusion=self._telemetry_fusion(normalized),
            rationale=self._rationale(
                forecast_state=forecast_state,
                trajectory=trajectory,
                recommended_action=recommended_action,
                global_risk_score=global_risk,
                recovery_probability=recovery_probability,
                systemic_risk_probability=systemic_risk_probability,
            ),
            metadata={
                "source_engines": sorted({s.source_engine for s in normalized}),
            },
        )

        self._record_assessment(assessment, context=context)
        return assessment

    def submit(
        self,
        signals: Sequence[GlobalRiskForecastSignal | Dict[str, Any]],
        **kwargs: Any,
    ) -> SovereignGlobalRiskForecastAssessment:
        return self.evaluate(signals, **kwargs)

    def get_recent_assessments(
        self,
        *,
        limit: int = 25,
    ) -> List[SovereignGlobalRiskForecastAssessment]:
        limit = max(1, int(limit))
        return list(reversed(self._assessments[-limit:]))

    # ==========================================================
    # PROBABILITY / RISK
    # ==========================================================

    def _recovery_probability(
        self,
        *,
        recovery_capacity_score: float,
        survivability_score: float,
        continuity_degradation_score: float,
        sovereignty_degradation_score: float,
        resilience_exhaustion_score: float,
    ) -> float:
        score = (
            recovery_capacity_score
            + survivability_score
            + (100.0 - continuity_degradation_score)
            + (100.0 - sovereignty_degradation_score)
            + (100.0 - resilience_exhaustion_score)
        ) / 500.0

        return self._clamp_probability(score)

    def _systemic_risk_probability(
        self,
        *,
        global_instability_score: float,
        escalation_probability_score: float,
        continuity_degradation_score: float,
        sovereignty_degradation_score: float,
        infrastructure_destabilization_score: float,
        ecosystem_fragility_score: float,
        geopolitical_pressure_score: float,
        uncertainty_score: float,
    ) -> float:
        score = (
            global_instability_score
            + escalation_probability_score
            + continuity_degradation_score
            + sovereignty_degradation_score
            + infrastructure_destabilization_score
            + ecosystem_fragility_score
            + geopolitical_pressure_score
            + uncertainty_score
        ) / 800.0

        return self._clamp_probability(score)

    def _global_risk_score(
        self,
        *,
        global_instability_score: float,
        escalation_probability_score: float,
        continuity_degradation_score: float,
        sovereignty_degradation_score: float,
        infrastructure_destabilization_score: float,
        ecosystem_fragility_score: float,
        geopolitical_pressure_score: float,
        resilience_exhaustion_score: float,
        uncertainty_score: float,
        recovery_probability: float,
        systemic_risk_probability: float,
        survivability_score: float,
    ) -> float:
        risk = (
            global_instability_score
            + escalation_probability_score
            + continuity_degradation_score
            + sovereignty_degradation_score
            + infrastructure_destabilization_score
            + ecosystem_fragility_score
            + geopolitical_pressure_score
            + resilience_exhaustion_score
            + uncertainty_score
            + ((1.0 - recovery_probability) * 100.0)
            + (systemic_risk_probability * 100.0)
            + (100.0 - survivability_score)
        ) / 12.0

        return self._clamp_score(risk)

    # ==========================================================
    # STATE / TRAJECTORY
    # ==========================================================

    @staticmethod
    def _forecast_state(
        *,
        global_risk_score: float,
        escalation_probability_score: float,
        continuity_degradation_score: float,
        sovereignty_degradation_score: float,
        systemic_risk_probability: float,
        survivability_score: float,
    ) -> str:
        if global_risk_score >= 85 or survivability_score <= 30:
            return FORECAST_STATE_GLOBAL_CRITICAL

        if systemic_risk_probability >= 0.75:
            return FORECAST_STATE_SYSTEMIC_RISK

        if sovereignty_degradation_score >= 70:
            return FORECAST_STATE_SOVEREIGNTY_DEGRADING

        if continuity_degradation_score >= 70:
            return FORECAST_STATE_CONTINUITY_DEGRADING

        if escalation_probability_score >= 65:
            return FORECAST_STATE_ESCALATING

        if global_risk_score >= 50:
            return FORECAST_STATE_ELEVATED

        if global_risk_score >= 25:
            return FORECAST_STATE_WATCH

        return FORECAST_STATE_STABLE

    @staticmethod
    def _trajectory(
        *,
        forecast_state: str,
        recovery_probability: float,
        systemic_risk_probability: float,
        escalation_probability_score: float,
    ) -> str:
        if forecast_state == FORECAST_STATE_GLOBAL_CRITICAL:
            return TRAJECTORY_SYSTEMIC_DEGRADATION

        if systemic_risk_probability >= 0.70:
            return TRAJECTORY_FRAGMENTING

        if escalation_probability_score >= 65:
            return TRAJECTORY_ESCALATING

        if recovery_probability >= 0.75:
            return TRAJECTORY_RECOVERY

        if recovery_probability >= 0.55:
            return TRAJECTORY_STABILIZING

        return TRAJECTORY_MONITORING

    @staticmethod
    def _recommended_action(
        *,
        forecast_state: str,
        trajectory: str,
        recovery_probability: float,
    ) -> str:
        if forecast_state == FORECAST_STATE_GLOBAL_CRITICAL:
            return ACTION_GLOBAL_RESILIENCE_SURGE

        if trajectory == TRAJECTORY_SYSTEMIC_DEGRADATION:
            return ACTION_GLOBAL_RESILIENCE_SURGE

        if trajectory == TRAJECTORY_ESCALATING:
            return ACTION_ESCALATION_CONTAINMENT

        if forecast_state == FORECAST_STATE_CONTINUITY_DEGRADING:
            return ACTION_CONTINUITY_RESTORATION

        if forecast_state == FORECAST_STATE_SOVEREIGNTY_DEGRADING:
            return ACTION_SOVEREIGNTY_STABILIZATION

        if trajectory == TRAJECTORY_RECOVERY:
            return ACTION_STRATEGIC_RECOVERY

        if recovery_probability <= 0.45:
            return ACTION_FORECAST_REVIEW

        return ACTION_MONITOR

    # ==========================================================
    # PROJECTION / STEPS / DIRECTIVES
    # ==========================================================

    def _projection(
        self,
        *,
        forecast_state: str,
        trajectory: str,
        global_risk_score: float,
        escalation_probability_score: float,
        continuity_degradation_score: float,
        sovereignty_degradation_score: float,
        recovery_capacity_score: float,
        survivability_score: float,
    ) -> GlobalRiskProjection:
        return GlobalRiskProjection(
            projection_id=str(uuid.uuid4()),
            projected_state=forecast_state,
            trajectory=trajectory,
            global_risk_projection_score=global_risk_score,
            escalation_projection_score=escalation_probability_score,
            continuity_projection_score=continuity_degradation_score,
            sovereignty_projection_score=sovereignty_degradation_score,
            recovery_projection_score=recovery_capacity_score,
            survivability_projection_score=survivability_score,
            rationale=(
                f"Global risk forecast projects {forecast_state} "
                f"with trajectory {trajectory}."
            ),
        )

    def _forecast_steps(
        self,
        *,
        forecast_state: str,
        trajectory: str,
        global_instability_score: float,
        escalation_probability_score: float,
        continuity_degradation_score: float,
        sovereignty_degradation_score: float,
        infrastructure_destabilization_score: float,
        ecosystem_fragility_score: float,
        resilience_exhaustion_score: float,
        recovery_capacity_score: float,
        survivability_score: float,
        depth: int,
    ) -> List[GlobalRiskForecastStep]:
        steps: List[GlobalRiskForecastStep] = []

        for idx in range(max(1, int(depth))):
            recovery_probability = self._recovery_probability(
                recovery_capacity_score=recovery_capacity_score,
                survivability_score=survivability_score,
                continuity_degradation_score=continuity_degradation_score,
                sovereignty_degradation_score=sovereignty_degradation_score,
                resilience_exhaustion_score=resilience_exhaustion_score,
            )

            systemic_risk_probability = self._systemic_risk_probability(
                global_instability_score=global_instability_score,
                escalation_probability_score=escalation_probability_score,
                continuity_degradation_score=continuity_degradation_score,
                sovereignty_degradation_score=sovereignty_degradation_score,
                infrastructure_destabilization_score=infrastructure_destabilization_score,
                ecosystem_fragility_score=ecosystem_fragility_score,
                geopolitical_pressure_score=global_instability_score,
                uncertainty_score=0.0,
            )

            global_risk = self._global_risk_score(
                global_instability_score=global_instability_score,
                escalation_probability_score=escalation_probability_score,
                continuity_degradation_score=continuity_degradation_score,
                sovereignty_degradation_score=sovereignty_degradation_score,
                infrastructure_destabilization_score=infrastructure_destabilization_score,
                ecosystem_fragility_score=ecosystem_fragility_score,
                geopolitical_pressure_score=global_instability_score,
                resilience_exhaustion_score=resilience_exhaustion_score,
                uncertainty_score=0.0,
                recovery_probability=recovery_probability,
                systemic_risk_probability=systemic_risk_probability,
                survivability_score=survivability_score,
            )

            steps.append(
                GlobalRiskForecastStep(
                    step_id=str(uuid.uuid4()),
                    step_index=idx,
                    forecast_state=forecast_state,
                    trajectory=trajectory,
                    global_instability_score=global_instability_score,
                    escalation_probability_score=escalation_probability_score,
                    continuity_degradation_score=continuity_degradation_score,
                    sovereignty_degradation_score=sovereignty_degradation_score,
                    infrastructure_destabilization_score=infrastructure_destabilization_score,
                    ecosystem_fragility_score=ecosystem_fragility_score,
                    resilience_exhaustion_score=resilience_exhaustion_score,
                    recovery_capacity_score=recovery_capacity_score,
                    survivability_score=survivability_score,
                    global_risk_score=global_risk,
                    recovery_probability=recovery_probability,
                    systemic_risk_probability=systemic_risk_probability,
                    rationale=(
                        f"Global forecast step {idx} projects "
                        f"{forecast_state} / {trajectory}."
                    ),
                )
            )

            if trajectory in {TRAJECTORY_RECOVERY, TRAJECTORY_STABILIZING}:
                global_instability_score = self._clamp_score(global_instability_score - 1.0)
                escalation_probability_score = self._clamp_score(escalation_probability_score - 1.0)
                continuity_degradation_score = self._clamp_score(continuity_degradation_score - 1.0)
                sovereignty_degradation_score = self._clamp_score(sovereignty_degradation_score - 0.8)
                infrastructure_destabilization_score = self._clamp_score(
                    infrastructure_destabilization_score - 0.8
                )
                ecosystem_fragility_score = self._clamp_score(ecosystem_fragility_score - 0.8)
                resilience_exhaustion_score = self._clamp_score(resilience_exhaustion_score - 0.8)
                recovery_capacity_score = self._clamp_score(recovery_capacity_score + 1.0)
                survivability_score = self._clamp_score(survivability_score + 0.8)
            else:
                global_instability_score = self._clamp_score(global_instability_score + 1.0)
                escalation_probability_score = self._clamp_score(escalation_probability_score + 1.0)
                continuity_degradation_score = self._clamp_score(continuity_degradation_score + 0.8)
                sovereignty_degradation_score = self._clamp_score(sovereignty_degradation_score + 0.8)
                infrastructure_destabilization_score = self._clamp_score(
                    infrastructure_destabilization_score + 0.8
                )
                ecosystem_fragility_score = self._clamp_score(ecosystem_fragility_score + 0.8)
                resilience_exhaustion_score = self._clamp_score(resilience_exhaustion_score + 0.8)
                recovery_capacity_score = self._clamp_score(recovery_capacity_score - 0.6)
                survivability_score = self._clamp_score(survivability_score - 0.6)

        return steps

    def _directives(
        self,
        *,
        recommended_action: str,
        global_risk_score: float,
        recovery_capacity_score: float,
        sovereignty_degradation_score: float,
        continuity_degradation_score: float,
    ) -> List[GlobalRiskForecastDirective]:
        priority = "LOW"

        if recommended_action in {
            ACTION_GLOBAL_RESILIENCE_SURGE,
            ACTION_ESCALATION_CONTAINMENT,
        }:
            priority = "CRITICAL"
        elif recommended_action != ACTION_MONITOR:
            priority = "HIGH"

        return [
            GlobalRiskForecastDirective(
                directive_id=str(uuid.uuid4()),
                directive_name=recommended_action.lower(),
                action_type=recommended_action,
                priority=priority,
                expected_risk_reduction=global_risk_score * 0.20,
                expected_recovery_gain=max(0.0, 100.0 - recovery_capacity_score) * 0.20,
                expected_sovereignty_gain=sovereignty_degradation_score * 0.20,
                expected_continuity_gain=continuity_degradation_score * 0.20,
                rationale=f"Recommended forecast action {recommended_action}.",
            )
        ]

    # ==========================================================
    # RECORDING
    # ==========================================================

    def _record_assessment(
        self,
        assessment: SovereignGlobalRiskForecastAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._assessments.append(assessment)

        self._write_to_memory(assessment, context=context)
        self._write_to_lineage(assessment, context=context)
        self._write_to_evidence(assessment, context=context)
        self._emit_event(assessment, context=context)

    def _write_to_memory(
        self,
        assessment: SovereignGlobalRiskForecastAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.operational_memory_engine is None:
            return

        payload = {
            "type": "SOVEREIGN_GLOBAL_RISK_FORECAST",
            "assessment": asdict(assessment),
            "context": context or {},
        }

        try:
            if hasattr(self.operational_memory_engine, "append_memory"):
                self.operational_memory_engine.append_memory(payload)
        except Exception as exc:
            print(f"⚠️ Global risk forecast memory write failed: {exc}")

    def _write_to_lineage(
        self,
        assessment: SovereignGlobalRiskForecastAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.lineage_engine is None:
            return

        payload = {
            "lineage_type": "SOVEREIGN_GLOBAL_RISK_FORECAST",
            "source_engine": self.engine_name,
            "summary": assessment.rationale,
            "severity": assessment.severity,
            "confidence": assessment.confidence,
            "tenant_id": assessment.tenant_id,
            "case_id": assessment.case_id,
            "correlation_id": assessment.correlation_id,
            "context": {
                "assessment": asdict(assessment),
                "context": context or {},
            },
        }

        try:
            if hasattr(self.lineage_engine, "record_lineage"):
                self.lineage_engine.record_lineage(payload)
        except Exception as exc:
            print(f"⚠️ Global risk forecast lineage write failed: {exc}")

    def _write_to_evidence(
        self,
        assessment: SovereignGlobalRiskForecastAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.fedramp_evidence_lineage_engine is None:
            return

        payload = {
            "evidence_type": "SOVEREIGN_GLOBAL_RISK_FORECAST",
            "source_engine": self.engine_name,
            "summary": assessment.rationale,
            "severity": assessment.severity,
            "confidence": assessment.confidence,
            "tenant_id": assessment.tenant_id,
            "case_id": assessment.case_id,
            "correlation_id": assessment.correlation_id,
            "evidence_payload": {
                "assessment": asdict(assessment),
                "context": context or {},
            },
        }

        try:
            if hasattr(self.fedramp_evidence_lineage_engine, "record_evidence"):
                self.fedramp_evidence_lineage_engine.record_evidence(payload)
        except Exception as exc:
            print(f"⚠️ Global risk forecast evidence write failed: {exc}")

    def _emit_event(
        self,
        assessment: SovereignGlobalRiskForecastAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self.event_bus is None:
            return

        payload = {
            "event_type": "SOVEREIGN_GLOBAL_RISK_FORECAST",
            "engine_name": self.engine_name,
            "assessment": asdict(assessment),
            "context": context or {},
        }

        try:
            if hasattr(self.event_bus, "emit"):
                self.event_bus.emit(
                    "SOVEREIGN_GLOBAL_RISK_FORECAST",
                    payload,
                )
        except Exception as exc:
            print(f"⚠️ Global risk forecast event emit failed: {exc}")

    # ==========================================================
    # NORMALIZATION / HELPERS
    # ==========================================================

    def _normalize_signal(
        self,
        item: GlobalRiskForecastSignal | Dict[str, Any],
        *,
        tenant_id: Optional[str],
        mission_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> GlobalRiskForecastSignal:
        if isinstance(item, GlobalRiskForecastSignal):
            return item

        return GlobalRiskForecastSignal(
            signal_id=str(item.get("signal_id") or uuid.uuid4()),
            source_engine=str(item.get("source_engine") or "unknown_engine"),
            severity=self._safe_severity(item.get("severity")),
            confidence=self._clamp_probability(item.get("confidence", 0.0)),
            summary=str(item.get("summary") or ""),
            tenant_id=tenant_id or item.get("tenant_id"),
            mission_id=mission_id or item.get("mission_id"),
            case_id=case_id or item.get("case_id"),
            correlation_id=correlation_id or item.get("correlation_id"),
            global_instability_score=self._clamp_score(
                item.get("global_instability_score", 0.0)
            ),
            escalation_probability_score=self._clamp_score(
                item.get("escalation_probability_score", 0.0)
            ),
            continuity_degradation_score=self._clamp_score(
                item.get("continuity_degradation_score", 0.0)
            ),
            sovereignty_degradation_score=self._clamp_score(
                item.get("sovereignty_degradation_score", 0.0)
            ),
            infrastructure_destabilization_score=self._clamp_score(
                item.get("infrastructure_destabilization_score", 0.0)
            ),
            ecosystem_fragility_score=self._clamp_score(
                item.get("ecosystem_fragility_score", 0.0)
            ),
            geopolitical_pressure_score=self._clamp_score(
                item.get("geopolitical_pressure_score", 0.0)
            ),
            resilience_exhaustion_score=self._clamp_score(
                item.get("resilience_exhaustion_score", 0.0)
            ),
            recovery_capacity_score=self._clamp_score(
                item.get("recovery_capacity_score", 100.0)
            ),
            survivability_score=self._clamp_score(
                item.get("survivability_score", 100.0)
            ),
            uncertainty_score=self._clamp_score(item.get("uncertainty_score", 0.0)),
            payload=dict(item.get("payload", {}) or {}),
        )

    def _empty_assessment(
        self,
        *,
        tenant_id: Optional[str],
        mission_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> SovereignGlobalRiskForecastAssessment:
        projection = GlobalRiskProjection(
            projection_id=str(uuid.uuid4()),
            projected_state=FORECAST_STATE_STABLE,
            trajectory=TRAJECTORY_STABILIZING,
            global_risk_projection_score=0.0,
            escalation_projection_score=0.0,
            continuity_projection_score=0.0,
            sovereignty_projection_score=0.0,
            recovery_projection_score=100.0,
            survivability_projection_score=100.0,
            rationale="No global risk forecast signals submitted.",
        )

        return SovereignGlobalRiskForecastAssessment(
            assessment_id=str(uuid.uuid4()),
            forecast_state=FORECAST_STATE_STABLE,
            trajectory=TRAJECTORY_STABILIZING,
            recommended_action=ACTION_MONITOR,
            global_instability_score=0.0,
            escalation_probability_score=0.0,
            continuity_degradation_score=0.0,
            sovereignty_degradation_score=0.0,
            infrastructure_destabilization_score=0.0,
            ecosystem_fragility_score=0.0,
            geopolitical_pressure_score=0.0,
            resilience_exhaustion_score=0.0,
            recovery_capacity_score=100.0,
            survivability_score=100.0,
            uncertainty_score=0.0,
            global_risk_score=0.0,
            recovery_probability=1.0,
            systemic_risk_probability=0.0,
            confidence=1.0,
            explainability_score=100.0,
            signal_count=0,
            engine_count=0,
            severity=GlobalForecastSeverity.INFO.value,
            tenant_id=tenant_id,
            mission_id=mission_id,
            case_id=case_id,
            correlation_id=correlation_id,
            strategic_projection=projection,
            forecast_steps=[],
            directives=[],
            telemetry_fusion={},
            rationale="No global risk forecast signals submitted.",
            metadata={},
        )

    def _select_primary_signal(
        self,
        signals: Sequence[GlobalRiskForecastSignal],
    ) -> GlobalRiskForecastSignal:
        return sorted(
            signals,
            key=lambda item: (
                item.global_instability_score,
                item.escalation_probability_score,
                item.sovereignty_degradation_score,
                item.continuity_degradation_score,
                -item.created_at_ms,
            ),
            reverse=True,
        )[0]

    def _telemetry_fusion(
        self,
        signals: Sequence[GlobalRiskForecastSignal],
    ) -> Dict[str, Any]:
        return {
            "signal_count": len(signals),
            "source_engines": sorted({s.source_engine for s in signals}),
            "tenants": sorted({s.tenant_id for s in signals if s.tenant_id}),
            "missions": sorted({s.mission_id for s in signals if s.mission_id}),
        }

    def _confidence(
        self,
        signals: Sequence[GlobalRiskForecastSignal],
    ) -> float:
        if not signals:
            return 0.0

        return self._clamp_probability(
            statistics.mean([s.confidence for s in signals])
        )

    def _explainability_score(
        self,
        signals: Sequence[GlobalRiskForecastSignal],
    ) -> float:
        if not signals:
            return 0.0

        explained = 0

        for signal in signals:
            if signal.summary:
                explained += 1
            if signal.source_engine:
                explained += 1
            if signal.payload:
                explained += 1

        return self._clamp_score((explained / (len(signals) * 3)) * 100.0)

    @staticmethod
    def _rationale(
        *,
        forecast_state: str,
        trajectory: str,
        recommended_action: str,
        global_risk_score: float,
        recovery_probability: float,
        systemic_risk_probability: float,
    ) -> str:
        return (
            f"Sovereign global risk forecast completed. "
            f"Forecast state {forecast_state}; trajectory {trajectory}; "
            f"recommended action {recommended_action}; global risk score "
            f"{global_risk_score:.2f}; recovery probability "
            f"{recovery_probability:.2f}; systemic risk probability "
            f"{systemic_risk_probability:.2f}."
        )

    @staticmethod
    def _safe_severity(value: Any) -> str:
        value = str(value or GlobalForecastSeverity.INFO.value).upper()
        valid = {item.value for item in GlobalForecastSeverity}
        return value if value in valid else GlobalForecastSeverity.INFO.value

    @staticmethod
    def _clamp_score(value: Any) -> float:
        try:
            score = float(value)
        except Exception:
            score = 0.0

        return max(0.0, min(100.0, score))

    @staticmethod
    def _clamp_probability(value: Any) -> float:
        try:
            score = float(value)
        except Exception:
            score = 0.0

        return max(0.0, min(1.0, score))

    def _avg_score(
        self,
        values: Sequence[float],
        *,
        default: float = 0.0,
    ) -> float:
        if not values:
            return default

        return self._clamp_score(statistics.mean(values))


def build_sovereign_global_risk_forecasting_engine(
    *,
    event_bus: Optional[Any] = None,
    global_command_integrator: Optional[Any] = None,
    geopolitical_resilience_engine: Optional[Any] = None,
    ecosystem_resilience_engine: Optional[Any] = None,
    mesh_autonomy_engine: Optional[Any] = None,
    sovereignty_assurance_engine: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[Any] = None,
) -> SovereignGlobalRiskForecastingEngine:
    return SovereignGlobalRiskForecastingEngine(
        event_bus=event_bus,
        global_command_integrator=global_command_integrator,
        geopolitical_resilience_engine=geopolitical_resilience_engine,
        ecosystem_resilience_engine=ecosystem_resilience_engine,
        mesh_autonomy_engine=mesh_autonomy_engine,
        sovereignty_assurance_engine=sovereignty_assurance_engine,
        operational_memory_engine=operational_memory_engine,
        lineage_engine=lineage_engine,
        fedramp_evidence_lineage_engine=fedramp_evidence_lineage_engine,
    )