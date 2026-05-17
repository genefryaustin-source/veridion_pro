"""
core/runtime/sovereign_autonomous_orchestration_engine.py

Sovereign Autonomous Orchestration Engine

Unified sovereign autonomous operational orchestration layer.

Orchestrates:
- executive strategic directives
- strategic synthesis outputs
- global risk forecasts
- global command posture
- sovereignty assurance posture
- continuity recovery flows
- resilience recovery flows
- escalation containment flows
- replayable orchestration lineage/evidence

IMPORTANT:
This subsystem DOES NOT:
- execute destructive operations
- bypass governance
- mutate infrastructure directly
- perform offensive actions

It ONLY:
- synthesize orchestration sequencing
- coordinate defensive recovery phases
- prioritize sovereign stabilization flows
- produce replayable orchestration rationale
"""

from __future__ import annotations

import statistics
import time
import uuid

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


DEFAULT_ENGINE_NAME = "sovereign_autonomous_orchestration_engine"
DEFAULT_ORCHESTRATION_DEPTH = 10


ORCHESTRATION_STATE_STABLE = "STABLE"
ORCHESTRATION_STATE_MONITORING = "MONITORING"
ORCHESTRATION_STATE_COORDINATING = "COORDINATING"
ORCHESTRATION_STATE_RECOVERY = "RECOVERY"
ORCHESTRATION_STATE_CONTINUITY_RESTORATION = "CONTINUITY_RESTORATION"
ORCHESTRATION_STATE_SOVEREIGNTY_STABILIZATION = "SOVEREIGNTY_STABILIZATION"
ORCHESTRATION_STATE_ESCALATION_CONTAINMENT = "ESCALATION_CONTAINMENT"
ORCHESTRATION_STATE_GLOBAL_STABILIZATION = "GLOBAL_STABILIZATION"
ORCHESTRATION_STATE_CRITICAL = "CRITICAL"


PHASE_MONITOR = "MONITOR"
PHASE_COMMAND_HARDENING = "COMMAND_HARDENING"
PHASE_ESCALATION_CONTAINMENT = "ESCALATION_CONTAINMENT"
PHASE_CONTINUITY_RESTORATION = "CONTINUITY_RESTORATION"
PHASE_SOVEREIGNTY_STABILIZATION = "SOVEREIGNTY_STABILIZATION"
PHASE_RESILIENCE_SURGE = "RESILIENCE_SURGE"
PHASE_STRATEGIC_RECOVERY = "STRATEGIC_RECOVERY"
PHASE_GLOBAL_STABILIZATION = "GLOBAL_STABILIZATION"


class OrchestrationSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class OrchestrationSignal:
    signal_id: str
    source_engine: str
    severity: str
    confidence: float
    summary: str

    tenant_id: Optional[str] = None
    mission_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    executive_priority_score: float = 0.0
    strategic_risk_score: float = 0.0
    continuity_risk_score: float = 0.0
    sovereignty_risk_score: float = 0.0
    escalation_risk_score: float = 0.0
    resilience_exhaustion_score: float = 0.0

    survivability_score: float = 100.0
    recovery_capacity_score: float = 100.0
    orchestration_complexity_score: float = 0.0
    uncertainty_score: float = 0.0

    requested_phase: Optional[str] = None

    payload: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(
        default_factory=lambda: int(time.time() * 1000)
    )


@dataclass(frozen=True)
class OrchestrationPhase:
    phase_id: str
    phase_name: str
    sequencing_order: int
    priority: str

    expected_risk_reduction: float
    expected_recovery_gain: float
    expected_sovereignty_gain: float
    expected_continuity_gain: float

    requires_governance_review: bool
    requires_human_approval: bool

    rationale: str

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class OrchestrationDirective:
    directive_id: str
    directive_name: str
    phase_name: str
    priority: str
    sequencing_order: int

    safe_mode: bool
    governance_required: bool

    rationale: str

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class OrchestrationProjection:
    projection_id: str
    projected_state: str
    primary_phase: str

    survivability_projection_score: float
    recovery_projection_score: float
    sovereignty_projection_score: float
    continuity_projection_score: float
    orchestration_risk_projection_score: float

    rationale: str

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class OrchestrationForecastStep:
    step_id: str
    step_index: int

    orchestration_state: str
    active_phase: str

    orchestration_risk_score: float
    survivability_score: float
    recovery_capacity_score: float
    sovereignty_risk_score: float
    continuity_risk_score: float
    escalation_risk_score: float

    rationale: str

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class SovereignAutonomousOrchestrationAssessment:
    assessment_id: str

    orchestration_state: str
    primary_phase: str
    primary_directive: str

    executive_priority_score: float
    strategic_risk_score: float
    continuity_risk_score: float
    sovereignty_risk_score: float
    escalation_risk_score: float
    resilience_exhaustion_score: float

    survivability_score: float
    recovery_capacity_score: float
    orchestration_complexity_score: float
    uncertainty_score: float

    orchestration_risk_score: float
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

    strategic_projection: OrchestrationProjection

    phases: List[OrchestrationPhase]
    directives: List[OrchestrationDirective]
    forecast_steps: List[OrchestrationForecastStep]

    telemetry_fusion: Dict[str, Any]

    rationale: str

    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(
        default_factory=lambda: int(time.time() * 1000)
    )


class SovereignAutonomousOrchestrationEngine:
    """
    Sovereign autonomous orchestration cognition.
    """

    def __init__(
        self,
        *,
        engine_name: str = DEFAULT_ENGINE_NAME,
        event_bus: Optional[Any] = None,
        executive_decision_engine: Optional[Any] = None,
        strategic_synthesis_engine: Optional[Any] = None,
        global_risk_forecasting_engine: Optional[Any] = None,
        global_command_integrator: Optional[Any] = None,
        sovereignty_assurance_engine: Optional[Any] = None,
        operational_governor: Optional[Any] = None,
        operational_memory_engine: Optional[Any] = None,
        lineage_engine: Optional[Any] = None,
        fedramp_evidence_lineage_engine: Optional[Any] = None,
    ) -> None:
        self.engine_name = engine_name
        self.event_bus = event_bus
        self.executive_decision_engine = executive_decision_engine
        self.strategic_synthesis_engine = strategic_synthesis_engine
        self.global_risk_forecasting_engine = global_risk_forecasting_engine
        self.global_command_integrator = global_command_integrator
        self.sovereignty_assurance_engine = sovereignty_assurance_engine
        self.operational_governor = operational_governor
        self.operational_memory_engine = operational_memory_engine
        self.lineage_engine = lineage_engine
        self.fedramp_evidence_lineage_engine = fedramp_evidence_lineage_engine

        self._assessments: List[SovereignAutonomousOrchestrationAssessment] = []

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def evaluate(
        self,
        signals: Sequence[OrchestrationSignal | Dict[str, Any]],
        *,
        orchestration_depth: int = DEFAULT_ORCHESTRATION_DEPTH,
        tenant_id: Optional[str] = None,
        mission_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> SovereignAutonomousOrchestrationAssessment:
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

        executive_priority = self._avg_score(
            [s.executive_priority_score for s in normalized]
        )
        strategic_risk = self._avg_score(
            [s.strategic_risk_score for s in normalized]
        )
        continuity_risk = self._avg_score(
            [s.continuity_risk_score for s in normalized]
        )
        sovereignty_risk = self._avg_score(
            [s.sovereignty_risk_score for s in normalized]
        )
        escalation_risk = self._avg_score(
            [s.escalation_risk_score for s in normalized]
        )
        resilience_exhaustion = self._avg_score(
            [s.resilience_exhaustion_score for s in normalized]
        )
        survivability = self._avg_score(
            [s.survivability_score for s in normalized],
            default=100.0,
        )
        recovery_capacity = self._avg_score(
            [s.recovery_capacity_score for s in normalized],
            default=100.0,
        )
        orchestration_complexity = self._avg_score(
            [s.orchestration_complexity_score for s in normalized]
        )
        uncertainty = self._avg_score(
            [s.uncertainty_score for s in normalized]
        )

        recovery_probability = self._recovery_probability(
            survivability_score=survivability,
            recovery_capacity_score=recovery_capacity,
            continuity_risk_score=continuity_risk,
            sovereignty_risk_score=sovereignty_risk,
            resilience_exhaustion_score=resilience_exhaustion,
        )

        systemic_risk_probability = self._systemic_risk_probability(
            strategic_risk_score=strategic_risk,
            continuity_risk_score=continuity_risk,
            sovereignty_risk_score=sovereignty_risk,
            escalation_risk_score=escalation_risk,
            orchestration_complexity_score=orchestration_complexity,
            uncertainty_score=uncertainty,
        )

        orchestration_risk = self._orchestration_risk_score(
            executive_priority_score=executive_priority,
            strategic_risk_score=strategic_risk,
            continuity_risk_score=continuity_risk,
            sovereignty_risk_score=sovereignty_risk,
            escalation_risk_score=escalation_risk,
            resilience_exhaustion_score=resilience_exhaustion,
            orchestration_complexity_score=orchestration_complexity,
            uncertainty_score=uncertainty,
            recovery_probability=recovery_probability,
            systemic_risk_probability=systemic_risk_probability,
            survivability_score=survivability,
        )

        orchestration_state = self._orchestration_state(
            orchestration_risk_score=orchestration_risk,
            continuity_risk_score=continuity_risk,
            sovereignty_risk_score=sovereignty_risk,
            escalation_risk_score=escalation_risk,
            survivability_score=survivability,
            systemic_risk_probability=systemic_risk_probability,
        )

        primary_phase = self._primary_phase(
            orchestration_state=orchestration_state,
            requested_phase=selected.requested_phase,
            continuity_risk_score=continuity_risk,
            sovereignty_risk_score=sovereignty_risk,
            escalation_risk_score=escalation_risk,
            recovery_probability=recovery_probability,
        )

        primary_directive = self._primary_directive(
            orchestration_state=orchestration_state,
            primary_phase=primary_phase,
        )

        phases = self._phases(
            primary_phase=primary_phase,
            orchestration_state=orchestration_state,
            orchestration_risk_score=orchestration_risk,
            survivability_score=survivability,
            recovery_capacity_score=recovery_capacity,
            sovereignty_risk_score=sovereignty_risk,
            continuity_risk_score=continuity_risk,
            escalation_risk_score=escalation_risk,
        )

        directives = self._directives(
            primary_directive=primary_directive,
            phases=phases,
            orchestration_state=orchestration_state,
        )

        projection = self._projection(
            orchestration_state=orchestration_state,
            primary_phase=primary_phase,
            survivability_score=survivability,
            recovery_capacity_score=recovery_capacity,
            sovereignty_risk_score=sovereignty_risk,
            continuity_risk_score=continuity_risk,
            orchestration_risk_score=orchestration_risk,
        )

        forecast_steps = self._forecast_steps(
            orchestration_state=orchestration_state,
            primary_phase=primary_phase,
            orchestration_risk_score=orchestration_risk,
            survivability_score=survivability,
            recovery_capacity_score=recovery_capacity,
            sovereignty_risk_score=sovereignty_risk,
            continuity_risk_score=continuity_risk,
            escalation_risk_score=escalation_risk,
            depth=orchestration_depth,
        )

        assessment = SovereignAutonomousOrchestrationAssessment(
            assessment_id=str(uuid.uuid4()),
            orchestration_state=orchestration_state,
            primary_phase=primary_phase,
            primary_directive=primary_directive,
            executive_priority_score=executive_priority,
            strategic_risk_score=strategic_risk,
            continuity_risk_score=continuity_risk,
            sovereignty_risk_score=sovereignty_risk,
            escalation_risk_score=escalation_risk,
            resilience_exhaustion_score=resilience_exhaustion,
            survivability_score=survivability,
            recovery_capacity_score=recovery_capacity,
            orchestration_complexity_score=orchestration_complexity,
            uncertainty_score=uncertainty,
            orchestration_risk_score=orchestration_risk,
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
            phases=phases,
            directives=directives,
            forecast_steps=forecast_steps,
            telemetry_fusion=self._telemetry_fusion(normalized),
            rationale=self._rationale(
                orchestration_state=orchestration_state,
                primary_phase=primary_phase,
                primary_directive=primary_directive,
                orchestration_risk_score=orchestration_risk,
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
        signals: Sequence[OrchestrationSignal | Dict[str, Any]],
        **kwargs: Any,
    ) -> SovereignAutonomousOrchestrationAssessment:
        return self.evaluate(signals, **kwargs)

    def get_recent_assessments(
        self,
        *,
        limit: int = 25,
    ) -> List[SovereignAutonomousOrchestrationAssessment]:
        limit = max(1, int(limit))
        return list(reversed(self._assessments[-limit:]))

    # ==========================================================
    # RISK / PROBABILITY
    # ==========================================================

    def _recovery_probability(
        self,
        *,
        survivability_score: float,
        recovery_capacity_score: float,
        continuity_risk_score: float,
        sovereignty_risk_score: float,
        resilience_exhaustion_score: float,
    ) -> float:
        value = (
            survivability_score
            + recovery_capacity_score
            + (100.0 - continuity_risk_score)
            + (100.0 - sovereignty_risk_score)
            + (100.0 - resilience_exhaustion_score)
        ) / 500.0

        return self._clamp_probability(value)

    def _systemic_risk_probability(
        self,
        *,
        strategic_risk_score: float,
        continuity_risk_score: float,
        sovereignty_risk_score: float,
        escalation_risk_score: float,
        orchestration_complexity_score: float,
        uncertainty_score: float,
    ) -> float:
        value = (
            strategic_risk_score
            + continuity_risk_score
            + sovereignty_risk_score
            + escalation_risk_score
            + orchestration_complexity_score
            + uncertainty_score
        ) / 600.0

        return self._clamp_probability(value)

    def _orchestration_risk_score(
        self,
        *,
        executive_priority_score: float,
        strategic_risk_score: float,
        continuity_risk_score: float,
        sovereignty_risk_score: float,
        escalation_risk_score: float,
        resilience_exhaustion_score: float,
        orchestration_complexity_score: float,
        uncertainty_score: float,
        recovery_probability: float,
        systemic_risk_probability: float,
        survivability_score: float,
    ) -> float:
        risk = (
            executive_priority_score
            + strategic_risk_score
            + continuity_risk_score
            + sovereignty_risk_score
            + escalation_risk_score
            + resilience_exhaustion_score
            + orchestration_complexity_score
            + uncertainty_score
            + ((1.0 - recovery_probability) * 100.0)
            + (systemic_risk_probability * 100.0)
            + (100.0 - survivability_score)
        ) / 11.0

        return self._clamp_score(risk)

    # ==========================================================
    # STATE / PHASES
    # ==========================================================

    @staticmethod
    def _orchestration_state(
        *,
        orchestration_risk_score: float,
        continuity_risk_score: float,
        sovereignty_risk_score: float,
        escalation_risk_score: float,
        survivability_score: float,
        systemic_risk_probability: float,
    ) -> str:
        if orchestration_risk_score >= 85 or survivability_score <= 30:
            return ORCHESTRATION_STATE_CRITICAL

        if systemic_risk_probability >= 0.75:
            return ORCHESTRATION_STATE_GLOBAL_STABILIZATION

        if sovereignty_risk_score >= 70:
            return ORCHESTRATION_STATE_SOVEREIGNTY_STABILIZATION

        if continuity_risk_score >= 70:
            return ORCHESTRATION_STATE_CONTINUITY_RESTORATION

        if escalation_risk_score >= 65:
            return ORCHESTRATION_STATE_ESCALATION_CONTAINMENT

        if orchestration_risk_score >= 50:
            return ORCHESTRATION_STATE_RECOVERY

        if orchestration_risk_score >= 25:
            return ORCHESTRATION_STATE_COORDINATING

        if orchestration_risk_score >= 10:
            return ORCHESTRATION_STATE_MONITORING

        return ORCHESTRATION_STATE_STABLE

    @staticmethod
    def _primary_phase(
        *,
        orchestration_state: str,
        requested_phase: Optional[str],
        continuity_risk_score: float,
        sovereignty_risk_score: float,
        escalation_risk_score: float,
        recovery_probability: float,
    ) -> str:
        if requested_phase:
            return requested_phase

        if orchestration_state == ORCHESTRATION_STATE_CRITICAL:
            return PHASE_GLOBAL_STABILIZATION

        if sovereignty_risk_score >= 70:
            return PHASE_SOVEREIGNTY_STABILIZATION

        if continuity_risk_score >= 70:
            return PHASE_CONTINUITY_RESTORATION

        if escalation_risk_score >= 65:
            return PHASE_ESCALATION_CONTAINMENT

        if recovery_probability >= 0.75:
            return PHASE_STRATEGIC_RECOVERY

        if orchestration_state in {
            ORCHESTRATION_STATE_RECOVERY,
            ORCHESTRATION_STATE_COORDINATING,
        }:
            return PHASE_COMMAND_HARDENING

        return PHASE_MONITOR

    @staticmethod
    def _primary_directive(
        *,
        orchestration_state: str,
        primary_phase: str,
    ) -> str:
        if orchestration_state == ORCHESTRATION_STATE_CRITICAL:
            return PHASE_GLOBAL_STABILIZATION

        return primary_phase

    # ==========================================================
    # PHASE / DIRECTIVE OBJECTS
    # ==========================================================

    def _phases(
        self,
        *,
        primary_phase: str,
        orchestration_state: str,
        orchestration_risk_score: float,
        survivability_score: float,
        recovery_capacity_score: float,
        sovereignty_risk_score: float,
        continuity_risk_score: float,
        escalation_risk_score: float,
    ) -> List[OrchestrationPhase]:
        phase_order = self._phase_sequence(primary_phase)

        phases: List[OrchestrationPhase] = []

        for idx, phase_name in enumerate(phase_order, start=1):
            priority = "LOW"

            if phase_name in {
                PHASE_GLOBAL_STABILIZATION,
                PHASE_ESCALATION_CONTAINMENT,
            }:
                priority = "CRITICAL"
            elif phase_name != PHASE_MONITOR:
                priority = "HIGH"

            phases.append(
                OrchestrationPhase(
                    phase_id=str(uuid.uuid4()),
                    phase_name=phase_name,
                    sequencing_order=idx,
                    priority=priority,
                    expected_risk_reduction=orchestration_risk_score * 0.10,
                    expected_recovery_gain=max(0.0, 100.0 - recovery_capacity_score) * 0.15,
                    expected_sovereignty_gain=sovereignty_risk_score * 0.15,
                    expected_continuity_gain=continuity_risk_score * 0.15,
                    requires_governance_review=phase_name != PHASE_MONITOR,
                    requires_human_approval=phase_name
                    in {
                        PHASE_GLOBAL_STABILIZATION,
                        PHASE_ESCALATION_CONTAINMENT,
                        PHASE_SOVEREIGNTY_STABILIZATION,
                    },
                    rationale=(
                        f"Phase {phase_name} sequenced from orchestration state "
                        f"{orchestration_state}."
                    ),
                    metadata={
                        "survivability_gap": max(0.0, 100.0 - survivability_score),
                        "escalation_risk_score": escalation_risk_score,
                    },
                )
            )

        return phases

    @staticmethod
    def _phase_sequence(primary_phase: str) -> List[str]:
        if primary_phase == PHASE_GLOBAL_STABILIZATION:
            return [
                PHASE_ESCALATION_CONTAINMENT,
                PHASE_SOVEREIGNTY_STABILIZATION,
                PHASE_CONTINUITY_RESTORATION,
                PHASE_RESILIENCE_SURGE,
                PHASE_STRATEGIC_RECOVERY,
            ]

        if primary_phase == PHASE_SOVEREIGNTY_STABILIZATION:
            return [
                PHASE_SOVEREIGNTY_STABILIZATION,
                PHASE_CONTINUITY_RESTORATION,
                PHASE_STRATEGIC_RECOVERY,
            ]

        if primary_phase == PHASE_CONTINUITY_RESTORATION:
            return [
                PHASE_CONTINUITY_RESTORATION,
                PHASE_RESILIENCE_SURGE,
                PHASE_STRATEGIC_RECOVERY,
            ]

        if primary_phase == PHASE_ESCALATION_CONTAINMENT:
            return [
                PHASE_ESCALATION_CONTAINMENT,
                PHASE_COMMAND_HARDENING,
                PHASE_STRATEGIC_RECOVERY,
            ]

        if primary_phase == PHASE_STRATEGIC_RECOVERY:
            return [
                PHASE_STRATEGIC_RECOVERY,
                PHASE_COMMAND_HARDENING,
            ]

        if primary_phase == PHASE_COMMAND_HARDENING:
            return [
                PHASE_COMMAND_HARDENING,
                PHASE_STRATEGIC_RECOVERY,
            ]

        return [PHASE_MONITOR]

    def _directives(
        self,
        *,
        primary_directive: str,
        phases: Sequence[OrchestrationPhase],
        orchestration_state: str,
    ) -> List[OrchestrationDirective]:
        directives: List[OrchestrationDirective] = []

        for phase in phases:
            directives.append(
                OrchestrationDirective(
                    directive_id=str(uuid.uuid4()),
                    directive_name=(
                        primary_directive
                        if phase.sequencing_order == 1
                        else phase.phase_name
                    ),
                    phase_name=phase.phase_name,
                    priority=phase.priority,
                    sequencing_order=phase.sequencing_order,
                    safe_mode=True,
                    governance_required=phase.requires_governance_review,
                    rationale=(
                        f"Directive for phase {phase.phase_name} under "
                        f"orchestration state {orchestration_state}."
                    ),
                )
            )

        return directives

    # ==========================================================
    # PROJECTION / FORECAST
    # ==========================================================

    def _projection(
        self,
        *,
        orchestration_state: str,
        primary_phase: str,
        survivability_score: float,
        recovery_capacity_score: float,
        sovereignty_risk_score: float,
        continuity_risk_score: float,
        orchestration_risk_score: float,
    ) -> OrchestrationProjection:
        return OrchestrationProjection(
            projection_id=str(uuid.uuid4()),
            projected_state=orchestration_state,
            primary_phase=primary_phase,
            survivability_projection_score=survivability_score,
            recovery_projection_score=recovery_capacity_score,
            sovereignty_projection_score=100.0 - sovereignty_risk_score,
            continuity_projection_score=100.0 - continuity_risk_score,
            orchestration_risk_projection_score=orchestration_risk_score,
            rationale=(
                f"Orchestration projection selected {primary_phase} under "
                f"state {orchestration_state}."
            ),
        )

    def _forecast_steps(
        self,
        *,
        orchestration_state: str,
        primary_phase: str,
        orchestration_risk_score: float,
        survivability_score: float,
        recovery_capacity_score: float,
        sovereignty_risk_score: float,
        continuity_risk_score: float,
        escalation_risk_score: float,
        depth: int,
    ) -> List[OrchestrationForecastStep]:
        steps: List[OrchestrationForecastStep] = []

        for idx in range(max(1, int(depth))):
            steps.append(
                OrchestrationForecastStep(
                    step_id=str(uuid.uuid4()),
                    step_index=idx,
                    orchestration_state=orchestration_state,
                    active_phase=primary_phase,
                    orchestration_risk_score=orchestration_risk_score,
                    survivability_score=survivability_score,
                    recovery_capacity_score=recovery_capacity_score,
                    sovereignty_risk_score=sovereignty_risk_score,
                    continuity_risk_score=continuity_risk_score,
                    escalation_risk_score=escalation_risk_score,
                    rationale=f"Orchestration forecast step {idx}.",
                )
            )

            orchestration_risk_score = self._clamp_score(orchestration_risk_score - 0.9)
            survivability_score = self._clamp_score(survivability_score + 0.8)
            recovery_capacity_score = self._clamp_score(recovery_capacity_score + 0.8)
            sovereignty_risk_score = self._clamp_score(sovereignty_risk_score - 0.8)
            continuity_risk_score = self._clamp_score(continuity_risk_score - 0.8)
            escalation_risk_score = self._clamp_score(escalation_risk_score - 0.8)

        return steps

    # ==========================================================
    # RECORDING
    # ==========================================================

    def _record_assessment(
        self,
        assessment: SovereignAutonomousOrchestrationAssessment,
        *,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._assessments.append(assessment)

        payload = {
            "type": "SOVEREIGN_AUTONOMOUS_ORCHESTRATION",
            "assessment": asdict(assessment),
            "context": context or {},
        }

        self._write_memory(payload)
        self._write_lineage(payload)
        self._write_evidence(payload)
        self._emit_event(payload)

    def _write_memory(self, payload: Dict[str, Any]) -> None:
        try:
            if self.operational_memory_engine and hasattr(
                self.operational_memory_engine,
                "append_memory",
            ):
                self.operational_memory_engine.append_memory(payload)
        except Exception as exc:
            print(f"⚠️ Orchestration memory write failed: {exc}")

    def _write_lineage(self, payload: Dict[str, Any]) -> None:
        try:
            if self.lineage_engine and hasattr(self.lineage_engine, "record_lineage"):
                self.lineage_engine.record_lineage(payload)
        except Exception as exc:
            print(f"⚠️ Orchestration lineage write failed: {exc}")

    def _write_evidence(self, payload: Dict[str, Any]) -> None:
        try:
            if self.fedramp_evidence_lineage_engine and hasattr(
                self.fedramp_evidence_lineage_engine,
                "record_evidence",
            ):
                self.fedramp_evidence_lineage_engine.record_evidence(payload)
        except Exception as exc:
            print(f"⚠️ Orchestration evidence write failed: {exc}")

    def _emit_event(self, payload: Dict[str, Any]) -> None:
        try:
            if self.event_bus and hasattr(self.event_bus, "emit"):
                self.event_bus.emit(
                    "SOVEREIGN_AUTONOMOUS_ORCHESTRATION",
                    payload,
                )
        except Exception as exc:
            print(f"⚠️ Orchestration event emit failed: {exc}")

    # ==========================================================
    # HELPERS
    # ==========================================================

    def _normalize_signal(
        self,
        item: OrchestrationSignal | Dict[str, Any],
        *,
        tenant_id: Optional[str],
        mission_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> OrchestrationSignal:
        if isinstance(item, OrchestrationSignal):
            return item

        return OrchestrationSignal(
            signal_id=str(item.get("signal_id") or uuid.uuid4()),
            source_engine=str(item.get("source_engine") or "unknown_engine"),
            severity=self._safe_severity(item.get("severity")),
            confidence=self._clamp_probability(item.get("confidence", 0.0)),
            summary=str(item.get("summary") or ""),
            tenant_id=tenant_id or item.get("tenant_id"),
            mission_id=mission_id or item.get("mission_id"),
            case_id=case_id or item.get("case_id"),
            correlation_id=correlation_id or item.get("correlation_id"),
            executive_priority_score=self._clamp_score(
                item.get("executive_priority_score", 0.0)
            ),
            strategic_risk_score=self._clamp_score(
                item.get("strategic_risk_score", 0.0)
            ),
            continuity_risk_score=self._clamp_score(
                item.get("continuity_risk_score", 0.0)
            ),
            sovereignty_risk_score=self._clamp_score(
                item.get("sovereignty_risk_score", 0.0)
            ),
            escalation_risk_score=self._clamp_score(
                item.get("escalation_risk_score", 0.0)
            ),
            resilience_exhaustion_score=self._clamp_score(
                item.get("resilience_exhaustion_score", 0.0)
            ),
            survivability_score=self._clamp_score(
                item.get("survivability_score", 100.0)
            ),
            recovery_capacity_score=self._clamp_score(
                item.get("recovery_capacity_score", 100.0)
            ),
            orchestration_complexity_score=self._clamp_score(
                item.get("orchestration_complexity_score", 0.0)
            ),
            uncertainty_score=self._clamp_score(item.get("uncertainty_score", 0.0)),
            requested_phase=item.get("requested_phase"),
            payload=dict(item.get("payload", {}) or {}),
        )

    def _empty_assessment(
        self,
        *,
        tenant_id: Optional[str],
        mission_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> SovereignAutonomousOrchestrationAssessment:
        projection = OrchestrationProjection(
            projection_id=str(uuid.uuid4()),
            projected_state=ORCHESTRATION_STATE_STABLE,
            primary_phase=PHASE_MONITOR,
            survivability_projection_score=100.0,
            recovery_projection_score=100.0,
            sovereignty_projection_score=100.0,
            continuity_projection_score=100.0,
            orchestration_risk_projection_score=0.0,
            rationale="No orchestration signals submitted.",
        )

        return SovereignAutonomousOrchestrationAssessment(
            assessment_id=str(uuid.uuid4()),
            orchestration_state=ORCHESTRATION_STATE_STABLE,
            primary_phase=PHASE_MONITOR,
            primary_directive=PHASE_MONITOR,
            executive_priority_score=0.0,
            strategic_risk_score=0.0,
            continuity_risk_score=0.0,
            sovereignty_risk_score=0.0,
            escalation_risk_score=0.0,
            resilience_exhaustion_score=0.0,
            survivability_score=100.0,
            recovery_capacity_score=100.0,
            orchestration_complexity_score=0.0,
            uncertainty_score=0.0,
            orchestration_risk_score=0.0,
            recovery_probability=1.0,
            systemic_risk_probability=0.0,
            confidence=1.0,
            explainability_score=100.0,
            signal_count=0,
            engine_count=0,
            severity=OrchestrationSeverity.INFO.value,
            tenant_id=tenant_id,
            mission_id=mission_id,
            case_id=case_id,
            correlation_id=correlation_id,
            strategic_projection=projection,
            phases=[],
            directives=[],
            forecast_steps=[],
            telemetry_fusion={},
            rationale="No orchestration signals submitted.",
            metadata={},
        )

    def _select_primary_signal(
        self,
        signals: Sequence[OrchestrationSignal],
    ) -> OrchestrationSignal:
        return sorted(
            signals,
            key=lambda item: (
                item.executive_priority_score,
                item.strategic_risk_score,
                item.sovereignty_risk_score,
                item.continuity_risk_score,
                item.escalation_risk_score,
                -item.created_at_ms,
            ),
            reverse=True,
        )[0]

    def _telemetry_fusion(
        self,
        signals: Sequence[OrchestrationSignal],
    ) -> Dict[str, Any]:
        return {
            "signal_count": len(signals),
            "source_engines": sorted({s.source_engine for s in signals}),
            "tenants": sorted({s.tenant_id for s in signals if s.tenant_id}),
            "missions": sorted({s.mission_id for s in signals if s.mission_id}),
            "requested_phases": sorted(
                {s.requested_phase for s in signals if s.requested_phase}
            ),
        }

    def _confidence(self, signals: Sequence[OrchestrationSignal]) -> float:
        if not signals:
            return 0.0

        return self._clamp_probability(
            statistics.mean([s.confidence for s in signals])
        )

    def _explainability_score(self, signals: Sequence[OrchestrationSignal]) -> float:
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
        orchestration_state: str,
        primary_phase: str,
        primary_directive: str,
        orchestration_risk_score: float,
        recovery_probability: float,
        systemic_risk_probability: float,
    ) -> str:
        return (
            f"Sovereign autonomous orchestration completed. "
            f"State {orchestration_state}; primary phase {primary_phase}; "
            f"directive {primary_directive}; orchestration risk "
            f"{orchestration_risk_score:.2f}; recovery probability "
            f"{recovery_probability:.2f}; systemic risk probability "
            f"{systemic_risk_probability:.2f}."
        )

    @staticmethod
    def _safe_severity(value: Any) -> str:
        value = str(value or OrchestrationSeverity.INFO.value).upper()
        valid = {item.value for item in OrchestrationSeverity}
        return value if value in valid else OrchestrationSeverity.INFO.value

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


def build_sovereign_autonomous_orchestration_engine(
    *,
    event_bus: Optional[Any] = None,
    executive_decision_engine: Optional[Any] = None,
    strategic_synthesis_engine: Optional[Any] = None,
    global_risk_forecasting_engine: Optional[Any] = None,
    global_command_integrator: Optional[Any] = None,
    sovereignty_assurance_engine: Optional[Any] = None,
    operational_governor: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[Any] = None,
) -> SovereignAutonomousOrchestrationEngine:
    return SovereignAutonomousOrchestrationEngine(
        event_bus=event_bus,
        executive_decision_engine=executive_decision_engine,
        strategic_synthesis_engine=strategic_synthesis_engine,
        global_risk_forecasting_engine=global_risk_forecasting_engine,
        global_command_integrator=global_command_integrator,
        sovereignty_assurance_engine=sovereignty_assurance_engine,
        operational_governor=operational_governor,
        operational_memory_engine=operational_memory_engine,
        lineage_engine=lineage_engine,
        fedramp_evidence_lineage_engine=fedramp_evidence_lineage_engine,
    )