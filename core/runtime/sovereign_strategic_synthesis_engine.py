"""
core/runtime/sovereign_strategic_synthesis_engine.py

Sovereign Strategic Synthesis Engine

Unified sovereign strategic intelligence synthesis layer.

Synthesizes:
- runtime cognition
- simulation cognition
- forecasting cognition
- resilience cognition
- geopolitical cognition
- ecosystem cognition
- global command cognition
- planetary predictive cognition

Produces:
- unified strategic operational intelligence
- strategic survivability synthesis
- sovereignty stabilization synthesis
- continuity restoration synthesis
- escalation containment synthesis
- strategic recovery synthesis
- replayable strategic lineage/evidence

IMPORTANT:
This subsystem DOES NOT:
- autonomously execute destructive operations
- bypass governance
- mutate infrastructure
- override sovereignty boundaries

It ONLY:
- synthesize strategic cognition
- correlate operational intelligence layers
- produce strategic reasoning outputs
- forecast strategic future states
- coordinate strategic recovery intelligence
"""

from __future__ import annotations

import statistics
import time
import uuid

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


DEFAULT_ENGINE_NAME = (
    "sovereign_strategic_synthesis_engine"
)

DEFAULT_SYNTHESIS_DEPTH = 12


STRATEGIC_STATE_STABLE = "STABLE"

STRATEGIC_STATE_MONITORING = (
    "MONITORING"
)

STRATEGIC_STATE_ELEVATED = (
    "ELEVATED"
)

STRATEGIC_STATE_CONTINUITY_PRESSURE = (
    "CONTINUITY_PRESSURE"
)

STRATEGIC_STATE_SOVEREIGNTY_PRESSURE = (
    "SOVEREIGNTY_PRESSURE"
)

STRATEGIC_STATE_ESCALATION_PRESSURE = (
    "ESCALATION_PRESSURE"
)

STRATEGIC_STATE_SYSTEMIC_RISK = (
    "SYSTEMIC_RISK"
)

STRATEGIC_STATE_GLOBAL_CRITICAL = (
    "GLOBAL_CRITICAL"
)

TRAJECTORY_STABILIZING = (
    "STABILIZING"
)

TRAJECTORY_MONITORING = (
    "MONITORING"
)

TRAJECTORY_ESCALATING = (
    "ESCALATING"
)

TRAJECTORY_FRAGMENTING = (
    "FRAGMENTING"
)

TRAJECTORY_RECOVERY = (
    "RECOVERY"
)

TRAJECTORY_SYSTEMIC_DEGRADATION = (
    "SYSTEMIC_DEGRADATION"
)

ACTION_MONITOR = "MONITOR"

ACTION_REVIEW_STRATEGY = (
    "REVIEW_STRATEGY"
)

ACTION_ESCALATION_CONTAINMENT = (
    "ESCALATION_CONTAINMENT"
)

ACTION_CONTINUITY_RESTORATION = (
    "CONTINUITY_RESTORATION"
)

ACTION_SOVEREIGNTY_STABILIZATION = (
    "SOVEREIGNTY_STABILIZATION"
)

ACTION_GLOBAL_RESILIENCE_SURGE = (
    "GLOBAL_RESILIENCE_SURGE"
)

ACTION_STRATEGIC_RECOVERY = (
    "STRATEGIC_RECOVERY"
)

ACTION_COMMAND_HARDENING = (
    "COMMAND_HARDENING"
)


class StrategicSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class StrategicSynthesisSignal:
    signal_id: str

    source_engine: str

    severity: str
    confidence: float

    summary: str

    tenant_id: Optional[str] = None
    mission_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    runtime_risk_score: float = 0.0
    continuity_risk_score: float = 0.0
    sovereignty_risk_score: float = 0.0
    escalation_risk_score: float = 0.0
    geopolitical_risk_score: float = 0.0
    ecosystem_risk_score: float = 0.0
    infrastructure_risk_score: float = 0.0
    resilience_exhaustion_score: float = 0.0
    recovery_capacity_score: float = 100.0
    survivability_score: float = 100.0
    uncertainty_score: float = 0.0

    payload: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


@dataclass(frozen=True)
class StrategicProjection:
    projection_id: str

    projected_state: str
    trajectory: str

    strategic_risk_projection_score: float
    continuity_projection_score: float
    sovereignty_projection_score: float
    recovery_projection_score: float
    survivability_projection_score: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class StrategicForecastStep:
    step_id: str

    step_index: int

    strategic_state: str
    trajectory: str

    runtime_risk_score: float
    continuity_risk_score: float
    sovereignty_risk_score: float
    escalation_risk_score: float
    geopolitical_risk_score: float
    ecosystem_risk_score: float
    infrastructure_risk_score: float
    resilience_exhaustion_score: float
    recovery_capacity_score: float
    survivability_score: float

    strategic_risk_score: float
    recovery_probability: float
    systemic_risk_probability: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class StrategicDirective:
    directive_id: str

    directive_name: str

    action_type: str
    priority: str

    expected_risk_reduction: float
    expected_recovery_gain: float
    expected_sovereignty_gain: float
    expected_continuity_gain: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class SovereignStrategicSynthesisAssessment:
    assessment_id: str

    strategic_state: str
    trajectory: str
    recommended_action: str

    runtime_risk_score: float
    continuity_risk_score: float
    sovereignty_risk_score: float
    escalation_risk_score: float
    geopolitical_risk_score: float
    ecosystem_risk_score: float
    infrastructure_risk_score: float
    resilience_exhaustion_score: float
    recovery_capacity_score: float
    survivability_score: float
    uncertainty_score: float

    strategic_risk_score: float
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

    strategic_projection: StrategicProjection

    forecast_steps: List[
        StrategicForecastStep
    ]

    directives: List[
        StrategicDirective
    ]

    telemetry_fusion: Dict[str, Any]

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


class SovereignStrategicSynthesisEngine:
    """
    Unified sovereign strategic cognition engine.
    """

    def __init__(
        self,
        *,
        engine_name: str = (
            DEFAULT_ENGINE_NAME
        ),
        event_bus: Optional[Any] = None,
        global_risk_forecasting_engine: Optional[
            Any
        ] = None,
        global_command_integrator: Optional[
            Any
        ] = None,
        geopolitical_resilience_engine: Optional[
            Any
        ] = None,
        ecosystem_resilience_engine: Optional[
            Any
        ] = None,
        mesh_autonomy_engine: Optional[
            Any
        ] = None,
        sovereignty_assurance_engine: Optional[
            Any
        ] = None,
        operational_memory_engine: Optional[
            Any
        ] = None,
        lineage_engine: Optional[Any] = None,
        fedramp_evidence_lineage_engine: Optional[
            Any
        ] = None,
    ) -> None:

        self.engine_name = engine_name

        self.event_bus = event_bus

        self.global_risk_forecasting_engine = (
            global_risk_forecasting_engine
        )

        self.global_command_integrator = (
            global_command_integrator
        )

        self.geopolitical_resilience_engine = (
            geopolitical_resilience_engine
        )

        self.ecosystem_resilience_engine = (
            ecosystem_resilience_engine
        )

        self.mesh_autonomy_engine = (
            mesh_autonomy_engine
        )

        self.sovereignty_assurance_engine = (
            sovereignty_assurance_engine
        )

        self.operational_memory_engine = (
            operational_memory_engine
        )

        self.lineage_engine = lineage_engine

        self.fedramp_evidence_lineage_engine = (
            fedramp_evidence_lineage_engine
        )

        self._assessments: List[
            SovereignStrategicSynthesisAssessment
        ] = []

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def evaluate(
        self,
        signals: Sequence[
            StrategicSynthesisSignal
            | Dict[str, Any]
        ],
        *,
        synthesis_depth: int = (
            DEFAULT_SYNTHESIS_DEPTH
        ),
        tenant_id: Optional[str] = None,
        mission_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> (
        SovereignStrategicSynthesisAssessment
    ):

        normalized = [
            self._normalize_signal(
                item,
                tenant_id=tenant_id,
                mission_id=mission_id,
                case_id=case_id,
                correlation_id=(
                    correlation_id
                ),
            )
            for item in signals
        ]

        if not normalized:

            assessment = (
                self._empty_assessment(
                    tenant_id=tenant_id,
                    mission_id=mission_id,
                    case_id=case_id,
                    correlation_id=(
                        correlation_id
                    ),
                )
            )

            self._record_assessment(
                assessment,
                context=context,
            )

            return assessment

        selected = self._select_primary_signal(
            normalized
        )

        runtime_risk = self._avg_score(
            [
                s.runtime_risk_score
                for s in normalized
            ]
        )

        continuity_risk = self._avg_score(
            [
                s.continuity_risk_score
                for s in normalized
            ]
        )

        sovereignty_risk = self._avg_score(
            [
                s.sovereignty_risk_score
                for s in normalized
            ]
        )

        escalation_risk = self._avg_score(
            [
                s.escalation_risk_score
                for s in normalized
            ]
        )

        geopolitical_risk = self._avg_score(
            [
                s.geopolitical_risk_score
                for s in normalized
            ]
        )

        ecosystem_risk = self._avg_score(
            [
                s.ecosystem_risk_score
                for s in normalized
            ]
        )

        infrastructure_risk = (
            self._avg_score(
                [
                    s.infrastructure_risk_score
                    for s in normalized
                ]
            )
        )

        resilience_exhaustion = (
            self._avg_score(
                [
                    s
                    .resilience_exhaustion_score
                    for s in normalized
                ]
            )
        )

        recovery_capacity = (
            self._avg_score(
                [
                    s.recovery_capacity_score
                    for s in normalized
                ],
                default=100.0,
            )
        )

        survivability = self._avg_score(
            [
                s.survivability_score
                for s in normalized
            ],
            default=100.0,
        )

        uncertainty = self._avg_score(
            [
                s.uncertainty_score
                for s in normalized
            ]
        )

        recovery_probability = (
            self._recovery_probability(
                recovery_capacity_score=(
                    recovery_capacity
                ),
                survivability_score=(
                    survivability
                ),
                continuity_risk_score=(
                    continuity_risk
                ),
                sovereignty_risk_score=(
                    sovereignty_risk
                ),
                resilience_exhaustion_score=(
                    resilience_exhaustion
                ),
            )
        )

        systemic_risk_probability = (
            self._systemic_risk_probability(
                runtime_risk_score=(
                    runtime_risk
                ),
                continuity_risk_score=(
                    continuity_risk
                ),
                sovereignty_risk_score=(
                    sovereignty_risk
                ),
                escalation_risk_score=(
                    escalation_risk
                ),
                geopolitical_risk_score=(
                    geopolitical_risk
                ),
                ecosystem_risk_score=(
                    ecosystem_risk
                ),
                infrastructure_risk_score=(
                    infrastructure_risk
                ),
                uncertainty_score=(
                    uncertainty
                ),
            )
        )

        strategic_risk = (
            self._strategic_risk_score(
                runtime_risk_score=(
                    runtime_risk
                ),
                continuity_risk_score=(
                    continuity_risk
                ),
                sovereignty_risk_score=(
                    sovereignty_risk
                ),
                escalation_risk_score=(
                    escalation_risk
                ),
                geopolitical_risk_score=(
                    geopolitical_risk
                ),
                ecosystem_risk_score=(
                    ecosystem_risk
                ),
                infrastructure_risk_score=(
                    infrastructure_risk
                ),
                resilience_exhaustion_score=(
                    resilience_exhaustion
                ),
                uncertainty_score=(
                    uncertainty
                ),
                recovery_probability=(
                    recovery_probability
                ),
                systemic_risk_probability=(
                    systemic_risk_probability
                ),
                survivability_score=(
                    survivability
                ),
            )
        )

        strategic_state = (
            self._strategic_state(
                strategic_risk_score=(
                    strategic_risk
                ),
                escalation_risk_score=(
                    escalation_risk
                ),
                continuity_risk_score=(
                    continuity_risk
                ),
                sovereignty_risk_score=(
                    sovereignty_risk
                ),
                systemic_risk_probability=(
                    systemic_risk_probability
                ),
                survivability_score=(
                    survivability
                ),
            )
        )

        trajectory = self._trajectory(
            strategic_state=(
                strategic_state
            ),
            recovery_probability=(
                recovery_probability
            ),
            systemic_risk_probability=(
                systemic_risk_probability
            ),
            escalation_risk_score=(
                escalation_risk
            ),
        )

        recommended_action = (
            self._recommended_action(
                strategic_state=(
                    strategic_state
                ),
                trajectory=trajectory,
                recovery_probability=(
                    recovery_probability
                ),
            )
        )

        projection = self._projection(
            strategic_state=(
                strategic_state
            ),
            trajectory=trajectory,
            strategic_risk_score=(
                strategic_risk
            ),
            continuity_risk_score=(
                continuity_risk
            ),
            sovereignty_risk_score=(
                sovereignty_risk
            ),
            recovery_capacity_score=(
                recovery_capacity
            ),
            survivability_score=(
                survivability
            ),
        )

        steps = self._forecast_steps(
            strategic_state=(
                strategic_state
            ),
            trajectory=trajectory,
            runtime_risk_score=(
                runtime_risk
            ),
            continuity_risk_score=(
                continuity_risk
            ),
            sovereignty_risk_score=(
                sovereignty_risk
            ),
            escalation_risk_score=(
                escalation_risk
            ),
            geopolitical_risk_score=(
                geopolitical_risk
            ),
            ecosystem_risk_score=(
                ecosystem_risk
            ),
            infrastructure_risk_score=(
                infrastructure_risk
            ),
            resilience_exhaustion_score=(
                resilience_exhaustion
            ),
            recovery_capacity_score=(
                recovery_capacity
            ),
            survivability_score=(
                survivability
            ),
            depth=synthesis_depth,
        )

        directives = self._directives(
            recommended_action=(
                recommended_action
            ),
            strategic_risk_score=(
                strategic_risk
            ),
            recovery_capacity_score=(
                recovery_capacity
            ),
            sovereignty_risk_score=(
                sovereignty_risk
            ),
            continuity_risk_score=(
                continuity_risk
            ),
        )

        assessment = (
            SovereignStrategicSynthesisAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                strategic_state=(
                    strategic_state
                ),
                trajectory=trajectory,
                recommended_action=(
                    recommended_action
                ),
                runtime_risk_score=(
                    runtime_risk
                ),
                continuity_risk_score=(
                    continuity_risk
                ),
                sovereignty_risk_score=(
                    sovereignty_risk
                ),
                escalation_risk_score=(
                    escalation_risk
                ),
                geopolitical_risk_score=(
                    geopolitical_risk
                ),
                ecosystem_risk_score=(
                    ecosystem_risk
                ),
                infrastructure_risk_score=(
                    infrastructure_risk
                ),
                resilience_exhaustion_score=(
                    resilience_exhaustion
                ),
                recovery_capacity_score=(
                    recovery_capacity
                ),
                survivability_score=(
                    survivability
                ),
                uncertainty_score=(
                    uncertainty
                ),
                strategic_risk_score=(
                    strategic_risk
                ),
                recovery_probability=(
                    recovery_probability
                ),
                systemic_risk_probability=(
                    systemic_risk_probability
                ),
                confidence=(
                    self._confidence(
                        normalized
                    )
                ),
                explainability_score=(
                    self
                    ._explainability_score(
                        normalized
                    )
                ),
                signal_count=len(
                    normalized
                ),
                engine_count=len(
                    {
                        s.source_engine
                        for s in normalized
                    }
                ),
                severity=(
                    selected.severity
                ),
                tenant_id=(
                    tenant_id
                    or selected
                    .tenant_id
                ),
                mission_id=(
                    mission_id
                    or selected
                    .mission_id
                ),
                case_id=(
                    case_id
                    or selected.case_id
                ),
                correlation_id=(
                    correlation_id
                    or selected
                    .correlation_id
                ),
                strategic_projection=(
                    projection
                ),
                forecast_steps=steps,
                directives=(
                    directives
                ),
                telemetry_fusion=(
                    self._telemetry_fusion(
                        normalized
                    )
                ),
                rationale=(
                    self._rationale(
                        strategic_state=(
                            strategic_state
                        ),
                        trajectory=trajectory,
                        recommended_action=(
                            recommended_action
                        ),
                        strategic_risk_score=(
                            strategic_risk
                        ),
                        recovery_probability=(
                            recovery_probability
                        ),
                        systemic_risk_probability=(
                            systemic_risk_probability
                        ),
                    )
                ),
                metadata={
                    "source_engines": sorted(
                        {
                            s.source_engine
                            for s in normalized
                        }
                    )
                },
            )
        )

        self._record_assessment(
            assessment,
            context=context,
        )

        return assessment

    # ==========================================================
    # RISK
    # ==========================================================

    def _recovery_probability(
        self,
        *,
        recovery_capacity_score: float,
        survivability_score: float,
        continuity_risk_score: float,
        sovereignty_risk_score: float,
        resilience_exhaustion_score: float,
    ) -> float:

        score = (
            recovery_capacity_score
            + survivability_score
            + (
                100.0
                - continuity_risk_score
            )
            + (
                100.0
                - sovereignty_risk_score
            )
            + (
                100.0
                - resilience_exhaustion_score
            )
        ) / 500.0

        return self._clamp_probability(
            score
        )

    def _systemic_risk_probability(
        self,
        *,
        runtime_risk_score: float,
        continuity_risk_score: float,
        sovereignty_risk_score: float,
        escalation_risk_score: float,
        geopolitical_risk_score: float,
        ecosystem_risk_score: float,
        infrastructure_risk_score: float,
        uncertainty_score: float,
    ) -> float:

        score = (
            runtime_risk_score
            + continuity_risk_score
            + sovereignty_risk_score
            + escalation_risk_score
            + geopolitical_risk_score
            + ecosystem_risk_score
            + infrastructure_risk_score
            + uncertainty_score
        ) / 800.0

        return self._clamp_probability(
            score
        )

    def _strategic_risk_score(
        self,
        *,
        runtime_risk_score: float,
        continuity_risk_score: float,
        sovereignty_risk_score: float,
        escalation_risk_score: float,
        geopolitical_risk_score: float,
        ecosystem_risk_score: float,
        infrastructure_risk_score: float,
        resilience_exhaustion_score: float,
        uncertainty_score: float,
        recovery_probability: float,
        systemic_risk_probability: float,
        survivability_score: float,
    ) -> float:

        risk = (
            runtime_risk_score
            + continuity_risk_score
            + sovereignty_risk_score
            + escalation_risk_score
            + geopolitical_risk_score
            + ecosystem_risk_score
            + infrastructure_risk_score
            + resilience_exhaustion_score
            + uncertainty_score
            + (
                (
                    1.0
                    - recovery_probability
                )
                * 100.0
            )
            + (
                systemic_risk_probability
                * 100.0
            )
            + (
                100.0
                - survivability_score
            )
        ) / 12.0

        return self._clamp_score(
            risk
        )

    # ==========================================================
    # STATE
    # ==========================================================

    @staticmethod
    def _strategic_state(
        *,
        strategic_risk_score: float,
        escalation_risk_score: float,
        continuity_risk_score: float,
        sovereignty_risk_score: float,
        systemic_risk_probability: float,
        survivability_score: float,
    ) -> str:

        if (
            strategic_risk_score >= 85
            or survivability_score <= 30
        ):
            return (
                STRATEGIC_STATE_GLOBAL_CRITICAL
            )

        if systemic_risk_probability >= 0.75:
            return (
                STRATEGIC_STATE_SYSTEMIC_RISK
            )

        if sovereignty_risk_score >= 70:
            return (
                STRATEGIC_STATE_SOVEREIGNTY_PRESSURE
            )

        if continuity_risk_score >= 70:
            return (
                STRATEGIC_STATE_CONTINUITY_PRESSURE
            )

        if escalation_risk_score >= 65:
            return (
                STRATEGIC_STATE_ESCALATION_PRESSURE
            )

        if strategic_risk_score >= 50:
            return (
                STRATEGIC_STATE_ELEVATED
            )

        if strategic_risk_score >= 25:
            return (
                STRATEGIC_STATE_MONITORING
            )

        return STRATEGIC_STATE_STABLE

    @staticmethod
    def _trajectory(
        *,
        strategic_state: str,
        recovery_probability: float,
        systemic_risk_probability: float,
        escalation_risk_score: float,
    ) -> str:

        if (
            strategic_state
            == STRATEGIC_STATE_GLOBAL_CRITICAL
        ):
            return (
                TRAJECTORY_SYSTEMIC_DEGRADATION
            )

        if systemic_risk_probability >= 0.70:
            return (
                TRAJECTORY_FRAGMENTING
            )

        if escalation_risk_score >= 65:
            return (
                TRAJECTORY_ESCALATING
            )

        if recovery_probability >= 0.75:
            return (
                TRAJECTORY_RECOVERY
            )

        if recovery_probability >= 0.55:
            return (
                TRAJECTORY_STABILIZING
            )

        return TRAJECTORY_MONITORING

    @staticmethod
    def _recommended_action(
        *,
        strategic_state: str,
        trajectory: str,
        recovery_probability: float,
    ) -> str:

        if (
            strategic_state
            == STRATEGIC_STATE_GLOBAL_CRITICAL
        ):
            return (
                ACTION_GLOBAL_RESILIENCE_SURGE
            )

        if (
            trajectory
            == TRAJECTORY_SYSTEMIC_DEGRADATION
        ):
            return (
                ACTION_GLOBAL_RESILIENCE_SURGE
            )

        if (
            trajectory
            == TRAJECTORY_ESCALATING
        ):
            return (
                ACTION_ESCALATION_CONTAINMENT
            )

        if (
            strategic_state
            == STRATEGIC_STATE_CONTINUITY_PRESSURE
        ):
            return (
                ACTION_CONTINUITY_RESTORATION
            )

        if (
            strategic_state
            == STRATEGIC_STATE_SOVEREIGNTY_PRESSURE
        ):
            return (
                ACTION_SOVEREIGNTY_STABILIZATION
            )

        if trajectory == TRAJECTORY_RECOVERY:
            return (
                ACTION_STRATEGIC_RECOVERY
            )

        if recovery_probability <= 0.45:
            return (
                ACTION_REVIEW_STRATEGY
            )

        return ACTION_MONITOR

    # ==========================================================
    # PROJECTION
    # ==========================================================

    def _projection(
        self,
        *,
        strategic_state: str,
        trajectory: str,
        strategic_risk_score: float,
        continuity_risk_score: float,
        sovereignty_risk_score: float,
        recovery_capacity_score: float,
        survivability_score: float,
    ) -> StrategicProjection:

        return StrategicProjection(
            projection_id=str(
                uuid.uuid4()
            ),
            projected_state=(
                strategic_state
            ),
            trajectory=trajectory,
            strategic_risk_projection_score=(
                strategic_risk_score
            ),
            continuity_projection_score=(
                continuity_risk_score
            ),
            sovereignty_projection_score=(
                sovereignty_risk_score
            ),
            recovery_projection_score=(
                recovery_capacity_score
            ),
            survivability_projection_score=(
                survivability_score
            ),
            rationale=(
                f"Strategic synthesis "
                f"projects "
                f"{strategic_state} "
                f"with trajectory "
                f"{trajectory}."
            ),
        )

    # ==========================================================
    # FORECASTING
    # ==========================================================

    def _forecast_steps(
        self,
        *,
        strategic_state: str,
        trajectory: str,
        runtime_risk_score: float,
        continuity_risk_score: float,
        sovereignty_risk_score: float,
        escalation_risk_score: float,
        geopolitical_risk_score: float,
        ecosystem_risk_score: float,
        infrastructure_risk_score: float,
        resilience_exhaustion_score: float,
        recovery_capacity_score: float,
        survivability_score: float,
        depth: int,
    ) -> List[
        StrategicForecastStep
    ]:

        steps = []

        for idx in range(
            max(1, int(depth))
        ):

            recovery_probability = (
                self._recovery_probability(
                    recovery_capacity_score=(
                        recovery_capacity_score
                    ),
                    survivability_score=(
                        survivability_score
                    ),
                    continuity_risk_score=(
                        continuity_risk_score
                    ),
                    sovereignty_risk_score=(
                        sovereignty_risk_score
                    ),
                    resilience_exhaustion_score=(
                        resilience_exhaustion_score
                    ),
                )
            )

            systemic_risk_probability = (
                self
                ._systemic_risk_probability(
                    runtime_risk_score=(
                        runtime_risk_score
                    ),
                    continuity_risk_score=(
                        continuity_risk_score
                    ),
                    sovereignty_risk_score=(
                        sovereignty_risk_score
                    ),
                    escalation_risk_score=(
                        escalation_risk_score
                    ),
                    geopolitical_risk_score=(
                        geopolitical_risk_score
                    ),
                    ecosystem_risk_score=(
                        ecosystem_risk_score
                    ),
                    infrastructure_risk_score=(
                        infrastructure_risk_score
                    ),
                    uncertainty_score=0.0,
                )
            )

            strategic_risk = (
                self._strategic_risk_score(
                    runtime_risk_score=(
                        runtime_risk_score
                    ),
                    continuity_risk_score=(
                        continuity_risk_score
                    ),
                    sovereignty_risk_score=(
                        sovereignty_risk_score
                    ),
                    escalation_risk_score=(
                        escalation_risk_score
                    ),
                    geopolitical_risk_score=(
                        geopolitical_risk_score
                    ),
                    ecosystem_risk_score=(
                        ecosystem_risk_score
                    ),
                    infrastructure_risk_score=(
                        infrastructure_risk_score
                    ),
                    resilience_exhaustion_score=(
                        resilience_exhaustion_score
                    ),
                    uncertainty_score=0.0,
                    recovery_probability=(
                        recovery_probability
                    ),
                    systemic_risk_probability=(
                        systemic_risk_probability
                    ),
                    survivability_score=(
                        survivability_score
                    ),
                )
            )

            steps.append(
                StrategicForecastStep(
                    step_id=str(
                        uuid.uuid4()
                    ),
                    step_index=idx,
                    strategic_state=(
                        strategic_state
                    ),
                    trajectory=trajectory,
                    runtime_risk_score=(
                        runtime_risk_score
                    ),
                    continuity_risk_score=(
                        continuity_risk_score
                    ),
                    sovereignty_risk_score=(
                        sovereignty_risk_score
                    ),
                    escalation_risk_score=(
                        escalation_risk_score
                    ),
                    geopolitical_risk_score=(
                        geopolitical_risk_score
                    ),
                    ecosystem_risk_score=(
                        ecosystem_risk_score
                    ),
                    infrastructure_risk_score=(
                        infrastructure_risk_score
                    ),
                    resilience_exhaustion_score=(
                        resilience_exhaustion_score
                    ),
                    recovery_capacity_score=(
                        recovery_capacity_score
                    ),
                    survivability_score=(
                        survivability_score
                    ),
                    strategic_risk_score=(
                        strategic_risk
                    ),
                    recovery_probability=(
                        recovery_probability
                    ),
                    systemic_risk_probability=(
                        systemic_risk_probability
                    ),
                    rationale=(
                        f"Strategic "
                        f"forecast step "
                        f"{idx} projects "
                        f"{strategic_state} "
                        f"/ {trajectory}."
                    ),
                )
            )

            if trajectory in {
                TRAJECTORY_RECOVERY,
                TRAJECTORY_STABILIZING,
            }:

                runtime_risk_score = (
                    self._clamp_score(
                        runtime_risk_score
                        - 1.0
                    )
                )

                continuity_risk_score = (
                    self._clamp_score(
                        continuity_risk_score
                        - 1.0
                    )
                )

                sovereignty_risk_score = (
                    self._clamp_score(
                        sovereignty_risk_score
                        - 0.8
                    )
                )

                escalation_risk_score = (
                    self._clamp_score(
                        escalation_risk_score
                        - 1.0
                    )
                )

                geopolitical_risk_score = (
                    self._clamp_score(
                        geopolitical_risk_score
                        - 0.8
                    )
                )

                ecosystem_risk_score = (
                    self._clamp_score(
                        ecosystem_risk_score
                        - 0.8
                    )
                )

                infrastructure_risk_score = (
                    self._clamp_score(
                        infrastructure_risk_score
                        - 0.8
                    )
                )

                resilience_exhaustion_score = (
                    self._clamp_score(
                        resilience_exhaustion_score
                        - 0.8
                    )
                )

                recovery_capacity_score = (
                    self._clamp_score(
                        recovery_capacity_score
                        + 1.0
                    )
                )

                survivability_score = (
                    self._clamp_score(
                        survivability_score
                        + 0.8
                    )
                )

            else:

                runtime_risk_score = (
                    self._clamp_score(
                        runtime_risk_score
                        + 1.0
                    )
                )

                continuity_risk_score = (
                    self._clamp_score(
                        continuity_risk_score
                        + 0.8
                    )
                )

                sovereignty_risk_score = (
                    self._clamp_score(
                        sovereignty_risk_score
                        + 0.8
                    )
                )

                escalation_risk_score = (
                    self._clamp_score(
                        escalation_risk_score
                        + 1.0
                    )
                )

                geopolitical_risk_score = (
                    self._clamp_score(
                        geopolitical_risk_score
                        + 0.8
                    )
                )

                ecosystem_risk_score = (
                    self._clamp_score(
                        ecosystem_risk_score
                        + 0.8
                    )
                )

                infrastructure_risk_score = (
                    self._clamp_score(
                        infrastructure_risk_score
                        + 0.8
                    )
                )

                resilience_exhaustion_score = (
                    self._clamp_score(
                        resilience_exhaustion_score
                        + 0.8
                    )
                )

                recovery_capacity_score = (
                    self._clamp_score(
                        recovery_capacity_score
                        - 0.6
                    )
                )

                survivability_score = (
                    self._clamp_score(
                        survivability_score
                        - 0.6
                    )
                )

        return steps

    # ==========================================================
    # DIRECTIVES
    # ==========================================================

    def _directives(
        self,
        *,
        recommended_action: str,
        strategic_risk_score: float,
        recovery_capacity_score: float,
        sovereignty_risk_score: float,
        continuity_risk_score: float,
    ) -> List[
        StrategicDirective
    ]:

        priority = "LOW"

        if recommended_action in {
            ACTION_GLOBAL_RESILIENCE_SURGE,
            ACTION_ESCALATION_CONTAINMENT,
        }:
            priority = "CRITICAL"

        elif (
            recommended_action
            != ACTION_MONITOR
        ):
            priority = "HIGH"

        return [
            StrategicDirective(
                directive_id=str(
                    uuid.uuid4()
                ),
                directive_name=(
                    recommended_action.lower()
                ),
                action_type=(
                    recommended_action
                ),
                priority=priority,
                expected_risk_reduction=(
                    strategic_risk_score
                    * 0.20
                ),
                expected_recovery_gain=(
                    max(
                        0.0,
                        100.0
                        - recovery_capacity_score,
                    )
                    * 0.20
                ),
                expected_sovereignty_gain=(
                    sovereignty_risk_score
                    * 0.20
                ),
                expected_continuity_gain=(
                    continuity_risk_score
                    * 0.20
                ),
                rationale=(
                    f"Recommended "
                    f"strategic action "
                    f"{recommended_action}."
                ),
            )
        ]

    # ==========================================================
    # RECORDING
    # ==========================================================

    def _record_assessment(
        self,
        assessment: (
            SovereignStrategicSynthesisAssessment
        ),
        *,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        self._assessments.append(
            assessment
        )

        payload = {
            "assessment": asdict(
                assessment
            ),
            "context": (
                context or {}
            ),
        }

        self._write_memory(payload)

        self._write_lineage(payload)

        self._write_evidence(payload)

        self._emit_event(payload)

    def _write_memory(
        self,
        payload: Dict[str, Any],
    ) -> None:

        try:

            if (
                self.operational_memory_engine
                and hasattr(
                    self
                    .operational_memory_engine,
                    "append_memory",
                )
            ):
                self.operational_memory_engine.append_memory(
                    payload
                )

        except Exception as exc:

            print(
                f"⚠️ Strategic "
                f"memory write failed: "
                f"{exc}"
            )

    def _write_lineage(
        self,
        payload: Dict[str, Any],
    ) -> None:

        try:

            if (
                self.lineage_engine
                and hasattr(
                    self.lineage_engine,
                    "record_lineage",
                )
            ):
                self.lineage_engine.record_lineage(
                    payload
                )

        except Exception as exc:

            print(
                f"⚠️ Strategic "
                f"lineage write failed: "
                f"{exc}"
            )

    def _write_evidence(
        self,
        payload: Dict[str, Any],
    ) -> None:

        try:

            if (
                self
                .fedramp_evidence_lineage_engine
                and hasattr(
                    self
                    .fedramp_evidence_lineage_engine,
                    "record_evidence",
                )
            ):
                self.fedramp_evidence_lineage_engine.record_evidence(
                    payload
                )

        except Exception as exc:

            print(
                f"⚠️ Strategic "
                f"evidence write failed: "
                f"{exc}"
            )

    def _emit_event(
        self,
        payload: Dict[str, Any],
    ) -> None:

        try:

            if (
                self.event_bus
                and hasattr(
                    self.event_bus,
                    "emit",
                )
            ):
                self.event_bus.emit(
                    "SOVEREIGN_STRATEGIC_SYNTHESIS",
                    payload,
                )

        except Exception as exc:

            print(
                f"⚠️ Strategic "
                f"event emit failed: "
                f"{exc}"
            )

    # ==========================================================
    # HELPERS
    # ==========================================================

    def _normalize_signal(
        self,
        item: (
            StrategicSynthesisSignal
            | Dict[str, Any]
        ),
        *,
        tenant_id: Optional[str],
        mission_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> StrategicSynthesisSignal:

        if isinstance(
            item,
            StrategicSynthesisSignal,
        ):
            return item

        return StrategicSynthesisSignal(
            signal_id=str(
                item.get(
                    "signal_id"
                )
                or uuid.uuid4()
            ),
            source_engine=str(
                item.get(
                    "source_engine",
                    "unknown_engine",
                )
            ),
            severity=self._safe_severity(
                item.get("severity")
            ),
            confidence=self._clamp_probability(
                item.get(
                    "confidence",
                    0.0,
                )
            ),
            summary=str(
                item.get(
                    "summary",
                    "",
                )
            ),
            tenant_id=(
                tenant_id
                or item.get(
                    "tenant_id"
                )
            ),
            mission_id=(
                mission_id
                or item.get(
                    "mission_id"
                )
            ),
            case_id=(
                case_id
                or item.get(
                    "case_id"
                )
            ),
            correlation_id=(
                correlation_id
                or item.get(
                    "correlation_id"
                )
            ),
            runtime_risk_score=self._clamp_score(
                item.get(
                    "runtime_risk_score",
                    0.0,
                )
            ),
            continuity_risk_score=self._clamp_score(
                item.get(
                    "continuity_risk_score",
                    0.0,
                )
            ),
            sovereignty_risk_score=self._clamp_score(
                item.get(
                    "sovereignty_risk_score",
                    0.0,
                )
            ),
            escalation_risk_score=self._clamp_score(
                item.get(
                    "escalation_risk_score",
                    0.0,
                )
            ),
            geopolitical_risk_score=self._clamp_score(
                item.get(
                    "geopolitical_risk_score",
                    0.0,
                )
            ),
            ecosystem_risk_score=self._clamp_score(
                item.get(
                    "ecosystem_risk_score",
                    0.0,
                )
            ),
            infrastructure_risk_score=self._clamp_score(
                item.get(
                    "infrastructure_risk_score",
                    0.0,
                )
            ),
            resilience_exhaustion_score=self._clamp_score(
                item.get(
                    "resilience_exhaustion_score",
                    0.0,
                )
            ),
            recovery_capacity_score=self._clamp_score(
                item.get(
                    "recovery_capacity_score",
                    100.0,
                )
            ),
            survivability_score=self._clamp_score(
                item.get(
                    "survivability_score",
                    100.0,
                )
            ),
            uncertainty_score=self._clamp_score(
                item.get(
                    "uncertainty_score",
                    0.0,
                )
            ),
            payload=dict(
                item.get(
                    "payload",
                    {},
                )
                or {}
            ),
        )

    def _empty_assessment(
        self,
        *,
        tenant_id: Optional[str],
        mission_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> (
        SovereignStrategicSynthesisAssessment
    ):

        projection = StrategicProjection(
            projection_id=str(
                uuid.uuid4()
            ),
            projected_state=(
                STRATEGIC_STATE_STABLE
            ),
            trajectory=(
                TRAJECTORY_STABILIZING
            ),
            strategic_risk_projection_score=0.0,
            continuity_projection_score=0.0,
            sovereignty_projection_score=0.0,
            recovery_projection_score=100.0,
            survivability_projection_score=100.0,
            rationale=(
                "No strategic "
                "signals submitted."
            ),
        )

        return (
            SovereignStrategicSynthesisAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                strategic_state=(
                    STRATEGIC_STATE_STABLE
                ),
                trajectory=(
                    TRAJECTORY_STABILIZING
                ),
                recommended_action=(
                    ACTION_MONITOR
                ),
                runtime_risk_score=0.0,
                continuity_risk_score=0.0,
                sovereignty_risk_score=0.0,
                escalation_risk_score=0.0,
                geopolitical_risk_score=0.0,
                ecosystem_risk_score=0.0,
                infrastructure_risk_score=0.0,
                resilience_exhaustion_score=0.0,
                recovery_capacity_score=100.0,
                survivability_score=100.0,
                uncertainty_score=0.0,
                strategic_risk_score=0.0,
                recovery_probability=1.0,
                systemic_risk_probability=0.0,
                confidence=1.0,
                explainability_score=100.0,
                signal_count=0,
                engine_count=0,
                severity=(
                    StrategicSeverity.INFO.value
                ),
                tenant_id=tenant_id,
                mission_id=mission_id,
                case_id=case_id,
                correlation_id=(
                    correlation_id
                ),
                strategic_projection=(
                    projection
                ),
                forecast_steps=[],
                directives=[],
                telemetry_fusion={},
                rationale=(
                    "No strategic "
                    "signals submitted."
                ),
                metadata={},
            )
        )

    def _select_primary_signal(
        self,
        signals: Sequence[
            StrategicSynthesisSignal
        ],
    ) -> StrategicSynthesisSignal:

        return sorted(
            signals,
            key=lambda item: (
                item.runtime_risk_score,
                item.escalation_risk_score,
                item.sovereignty_risk_score,
                item.continuity_risk_score,
                -item.created_at_ms,
            ),
            reverse=True,
        )[0]

    def _telemetry_fusion(
        self,
        signals: Sequence[
            StrategicSynthesisSignal
        ],
    ) -> Dict[str, Any]:

        return {
            "signal_count": len(
                signals
            ),
            "source_engines": sorted(
                {
                    s.source_engine
                    for s in signals
                }
            ),
            "tenants": sorted(
                {
                    s.tenant_id
                    for s in signals
                    if s.tenant_id
                }
            ),
            "missions": sorted(
                {
                    s.mission_id
                    for s in signals
                    if s.mission_id
                }
            ),
        }

    def _confidence(
        self,
        signals: Sequence[
            StrategicSynthesisSignal
        ],
    ) -> float:

        if not signals:
            return 0.0

        return self._clamp_probability(
            statistics.mean(
                [
                    s.confidence
                    for s in signals
                ]
            )
        )

    def _explainability_score(
        self,
        signals: Sequence[
            StrategicSynthesisSignal
        ],
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

        return self._clamp_score(
            (
                explained
                / (len(signals) * 3)
            )
            * 100.0
        )

    @staticmethod
    def _rationale(
        *,
        strategic_state: str,
        trajectory: str,
        recommended_action: str,
        strategic_risk_score: float,
        recovery_probability: float,
        systemic_risk_probability: float,
    ) -> str:

        return (
            f"Sovereign strategic "
            f"synthesis completed. "
            f"Strategic state "
            f"{strategic_state}; "
            f"trajectory "
            f"{trajectory}; "
            f"recommended action "
            f"{recommended_action}; "
            f"strategic risk score "
            f"{strategic_risk_score:.2f}; "
            f"recovery probability "
            f"{recovery_probability:.2f}; "
            f"systemic risk probability "
            f"{systemic_risk_probability:.2f}."
        )

    @staticmethod
    def _safe_severity(
        value: Any,
    ) -> str:

        value = str(
            value
            or StrategicSeverity.INFO.value
        ).upper()

        valid = {
            item.value
            for item in StrategicSeverity
        }

        return (
            value
            if value in valid
            else StrategicSeverity.INFO.value
        )

    @staticmethod
    def _clamp_score(
        value: Any,
    ) -> float:

        try:

            score = float(value)

        except Exception:

            score = 0.0

        return max(
            0.0,
            min(100.0, score),
        )

    @staticmethod
    def _clamp_probability(
        value: Any,
    ) -> float:

        try:

            score = float(value)

        except Exception:

            score = 0.0

        return max(
            0.0,
            min(1.0, score),
        )

    def _avg_score(
        self,
        values: Sequence[float],
        *,
        default: float = 0.0,
    ) -> float:

        if not values:
            return default

        return self._clamp_score(
            statistics.mean(values)
        )


def build_sovereign_strategic_synthesis_engine(
    *,
    event_bus: Optional[Any] = None,
    global_risk_forecasting_engine: Optional[
        Any
    ] = None,
    global_command_integrator: Optional[
        Any
    ] = None,
    geopolitical_resilience_engine: Optional[
        Any
    ] = None,
    ecosystem_resilience_engine: Optional[
        Any
    ] = None,
    mesh_autonomy_engine: Optional[
        Any
    ] = None,
    sovereignty_assurance_engine: Optional[
        Any
    ] = None,
    operational_memory_engine: Optional[
        Any
    ] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[
        Any
    ] = None,
) -> (
    SovereignStrategicSynthesisEngine
):

    return (
        SovereignStrategicSynthesisEngine(
            event_bus=event_bus,
            global_risk_forecasting_engine=(
                global_risk_forecasting_engine
            ),
            global_command_integrator=(
                global_command_integrator
            ),
            geopolitical_resilience_engine=(
                geopolitical_resilience_engine
            ),
            ecosystem_resilience_engine=(
                ecosystem_resilience_engine
            ),
            mesh_autonomy_engine=(
                mesh_autonomy_engine
            ),
            sovereignty_assurance_engine=(
                sovereignty_assurance_engine
            ),
            operational_memory_engine=(
                operational_memory_engine
            ),
            lineage_engine=lineage_engine,
            fedramp_evidence_lineage_engine=(
                fedramp_evidence_lineage_engine
            ),
        )
    )