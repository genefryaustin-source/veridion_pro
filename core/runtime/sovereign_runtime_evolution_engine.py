"""
core/runtime/sovereign_runtime_evolution_engine.py

Sovereign Runtime Evolution Engine

Autonomous sovereign runtime evolution cognition layer.

This subsystem evolves:
- governance posture
- survivability posture
- resilience posture
- mission posture
- operational topology
- autonomy coordination
- strategic operational behavior
- execution alignment posture
- adaptive cognition maturity

IMPORTANT:
This subsystem DOES NOT:
- directly mutate infrastructure
- execute containment
- enforce governance
- trigger failover actions
- autonomously execute runtime operations

It ONLY:
- evaluates evolution trajectories
- adapts strategic posture recommendations
- learns from operational history
- models maturity evolution
- records replayable evolution lineage/evidence
"""

from __future__ import annotations

import statistics
import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


DEFAULT_ENGINE_NAME = (
    "sovereign_runtime_evolution_engine"
)

EVOLUTION_STATE_STABLE = "STABLE"
EVOLUTION_STATE_ADAPTING = "ADAPTING"
EVOLUTION_STATE_EVOLVING = "EVOLVING"
EVOLUTION_STATE_TRANSFORMING = "TRANSFORMING"
EVOLUTION_STATE_DEGRADING = "DEGRADING"

EVOLUTION_OUTCOME_OPTIMIZING = "OPTIMIZING"
EVOLUTION_OUTCOME_RESILIENT = "RESILIENT"
EVOLUTION_OUTCOME_VOLATILE = "VOLATILE"
EVOLUTION_OUTCOME_DEGRADING = "DEGRADING"
EVOLUTION_OUTCOME_COLLAPSE_RISK = "COLLAPSE_RISK"

MATURITY_LEVEL_INITIAL = "INITIAL"
MATURITY_LEVEL_EMERGING = "EMERGING"
MATURITY_LEVEL_ADAPTIVE = "ADAPTIVE"
MATURITY_LEVEL_AUTONOMOUS = "AUTONOMOUS"
MATURITY_LEVEL_SOVEREIGN = "SOVEREIGN"

DEFAULT_EVOLUTION_WINDOW = 10


class EvolutionSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EvolutionDomain(str, Enum):
    GOVERNANCE = "GOVERNANCE"
    EXECUTION = "EXECUTION"
    AUTONOMY = "AUTONOMY"
    RESILIENCE = "RESILIENCE"
    MISSION = "MISSION"
    FORECASTING = "FORECASTING"
    SIMULATION = "SIMULATION"
    TELEMETRY = "TELEMETRY"
    GLOBAL = "GLOBAL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class EvolutionSignal:
    """
    Runtime evolution input signal.
    """

    evolution_signal_id: str

    signal_type: str
    domain: str
    source_engine: str

    severity: str
    confidence: float

    summary: str

    mission_id: Optional[str] = None
    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    governance_maturity_score: float = 0.0
    survivability_maturity_score: float = 0.0
    resilience_maturity_score: float = 0.0
    autonomy_maturity_score: float = 0.0
    mission_maturity_score: float = 0.0
    operational_maturity_score: float = 0.0

    adaptability_score: float = 0.0
    learning_velocity_score: float = 0.0
    strategic_alignment_score: float = 0.0
    operational_stability_score: float = 100.0
    volatility_score: float = 0.0
    uncertainty_score: float = 0.0

    payload: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(
        default_factory=lambda: int(time.time() * 1000)
    )


@dataclass(frozen=True)
class EvolutionTrajectory:
    """
    Runtime evolution trajectory.
    """

    trajectory_id: str

    trajectory_name: str

    projected_state: str
    projected_outcome: str
    projected_maturity_level: str

    maturity_growth_probability: float
    resilience_evolution_probability: float
    survivability_evolution_probability: float
    governance_evolution_probability: float
    collapse_probability: float

    trajectory_score: float

    rationale: str

    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(
        default_factory=lambda: int(time.time() * 1000)
    )


@dataclass(frozen=True)
class EvolutionStep:
    """
    Runtime evolution step.
    """

    step_id: str

    step_index: int

    projected_state: str
    projected_outcome: str
    projected_maturity_level: str

    governance_maturity_score: float
    survivability_maturity_score: float
    resilience_maturity_score: float
    autonomy_maturity_score: float
    mission_maturity_score: float
    operational_maturity_score: float

    adaptability_score: float
    learning_velocity_score: float
    strategic_alignment_score: float
    operational_stability_score: float
    volatility_score: float
    uncertainty_score: float

    maturity_growth_probability: float
    resilience_evolution_probability: float
    survivability_evolution_probability: float
    governance_evolution_probability: float
    collapse_probability: float

    trajectory_score: float

    trajectories: List[EvolutionTrajectory] = field(
        default_factory=list
    )

    rationale: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at_ms: int = field(
        default_factory=lambda: int(time.time() * 1000)
    )


@dataclass(frozen=True)
class SovereignRuntimeEvolutionAssessment:
    """
    Sovereign runtime evolution assessment.
    """

    assessment_id: str

    evolution_state: str
    projected_outcome: str
    maturity_level: str

    maturity_growth_probability: float
    resilience_evolution_probability: float
    survivability_evolution_probability: float
    governance_evolution_probability: float
    collapse_probability: float

    governance_maturity_score: float
    survivability_maturity_score: float
    resilience_maturity_score: float
    autonomy_maturity_score: float
    mission_maturity_score: float
    operational_maturity_score: float

    adaptability_score: float
    learning_velocity_score: float
    strategic_alignment_score: float
    operational_stability_score: float
    volatility_score: float
    uncertainty_score: float

    evolution_confidence: float
    explainability_score: float
    strategic_visibility_score: float

    selected_signal_id: Optional[str]
    selected_signal_type: Optional[str]

    severity: str
    confidence: float

    evolution_window: int

    mission_id: Optional[str]

    tenant_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    evolution_steps: List[EvolutionStep]

    recommended_actions: List[Dict[str, Any]]

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at_ms: int = field(
        default_factory=lambda: int(time.time() * 1000)
    )


@dataclass(frozen=True)
class SovereignRuntimeEvolutionSnapshot:
    """
    Runtime evolution diagnostics snapshot.
    """

    engine_name: str

    total_signals_seen: int

    total_assessments_created: int

    last_assessment_id: Optional[str]

    last_evolution_state: Optional[str]

    last_maturity_level: Optional[str]

    last_updated_ms: int


class SovereignRuntimeEvolutionEngine:
    """
    Sovereign runtime evolution cognition engine.
    """

    def __init__(
        self,
        *,
        engine_name: str = DEFAULT_ENGINE_NAME,
        event_bus: Optional[Any] = None,
        operational_memory_engine: Optional[Any] = None,
        lineage_engine: Optional[Any] = None,
        fedramp_evidence_lineage_engine: Optional[Any] = None,
    ) -> None:

        self.engine_name = engine_name

        self.event_bus = event_bus

        self.operational_memory_engine = (
            operational_memory_engine
        )

        self.lineage_engine = lineage_engine

        self.fedramp_evidence_lineage_engine = (
            fedramp_evidence_lineage_engine
        )

        self._signals_seen = 0

        self._assessments: List[
            SovereignRuntimeEvolutionAssessment
        ] = []

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def evaluate(
        self,
        signals: Sequence[
            EvolutionSignal | Dict[str, Any]
        ],
        *,
        evolution_window: int = (
            DEFAULT_EVOLUTION_WINDOW
        ),
        mission_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> SovereignRuntimeEvolutionAssessment:

        normalized = [
            self._normalize_signal(
                item,
                mission_id=mission_id,
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=(
                    correlation_id
                ),
            )
            for item in signals
        ]

        self._signals_seen += len(
            normalized
        )

        if not normalized:

            assessment = (
                self._empty_assessment(
                    mission_id=mission_id,
                    tenant_id=tenant_id,
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

        selected = (
            self._select_primary_signal(
                normalized
            )
        )

        governance_maturity = (
            self._avg_score(
                [
                    item
                    .governance_maturity_score
                    for item in normalized
                ]
            )
        )

        survivability_maturity = (
            self._avg_score(
                [
                    item
                    .survivability_maturity_score
                    for item in normalized
                ]
            )
        )

        resilience_maturity = (
            self._avg_score(
                [
                    item
                    .resilience_maturity_score
                    for item in normalized
                ]
            )
        )

        autonomy_maturity = (
            self._avg_score(
                [
                    item
                    .autonomy_maturity_score
                    for item in normalized
                ]
            )
        )

        mission_maturity = (
            self._avg_score(
                [
                    item
                    .mission_maturity_score
                    for item in normalized
                ]
            )
        )

        operational_maturity = (
            self._avg_score(
                [
                    item
                    .operational_maturity_score
                    for item in normalized
                ]
            )
        )

        adaptability = (
            self._avg_score(
                [
                    item.adaptability_score
                    for item in normalized
                ]
            )
        )

        learning_velocity = (
            self._avg_score(
                [
                    item.learning_velocity_score
                    for item in normalized
                ]
            )
        )

        strategic_alignment = (
            self._avg_score(
                [
                    item
                    .strategic_alignment_score
                    for item in normalized
                ]
            )
        )

        operational_stability = (
            self._avg_score(
                [
                    item
                    .operational_stability_score
                    for item in normalized
                ]
            )
        )

        volatility = (
            self._avg_score(
                [
                    item.volatility_score
                    for item in normalized
                ]
            )
        )

        uncertainty = (
            self._avg_score(
                [
                    item.uncertainty_score
                    for item in normalized
                ]
            )
        )

        maturity_growth_probability = (
            self
            ._maturity_growth_probability(
                governance_maturity=(
                    governance_maturity
                ),
                survivability_maturity=(
                    survivability_maturity
                ),
                resilience_maturity=(
                    resilience_maturity
                ),
                autonomy_maturity=(
                    autonomy_maturity
                ),
                mission_maturity=(
                    mission_maturity
                ),
                operational_maturity=(
                    operational_maturity
                ),
                adaptability=(
                    adaptability
                ),
                learning_velocity=(
                    learning_velocity
                ),
            )
        )

        resilience_evolution_probability = (
            self
            ._resilience_evolution_probability(
                resilience_maturity=(
                    resilience_maturity
                ),
                operational_stability=(
                    operational_stability
                ),
                volatility=(
                    volatility
                ),
            )
        )

        survivability_evolution_probability = (
            self
            ._survivability_evolution_probability(
                survivability_maturity=(
                    survivability_maturity
                ),
                resilience_maturity=(
                    resilience_maturity
                ),
                uncertainty=(
                    uncertainty
                ),
            )
        )

        governance_evolution_probability = (
            self
            ._governance_evolution_probability(
                governance_maturity=(
                    governance_maturity
                ),
                strategic_alignment=(
                    strategic_alignment
                ),
                volatility=(
                    volatility
                ),
            )
        )

        collapse_probability = (
            self
            ._collapse_probability(
                operational_stability=(
                    operational_stability
                ),
                volatility=(
                    volatility
                ),
                uncertainty=(
                    uncertainty
                ),
                adaptability=(
                    adaptability
                ),
                resilience_maturity=(
                    resilience_maturity
                ),
            )
        )

        evolution_state = (
            self._evolution_state(
                maturity_growth_probability=(
                    maturity_growth_probability
                ),
                collapse_probability=(
                    collapse_probability
                ),
                volatility=(
                    volatility
                ),
            )
        )

        projected_outcome = (
            self._projected_outcome(
                evolution_state=(
                    evolution_state
                ),
                collapse_probability=(
                    collapse_probability
                ),
                resilience_evolution_probability=(
                    resilience_evolution_probability
                ),
            )
        )

        maturity_level = (
            self._maturity_level(
                governance_maturity=(
                    governance_maturity
                ),
                survivability_maturity=(
                    survivability_maturity
                ),
                resilience_maturity=(
                    resilience_maturity
                ),
                autonomy_maturity=(
                    autonomy_maturity
                ),
                mission_maturity=(
                    mission_maturity
                ),
                operational_maturity=(
                    operational_maturity
                ),
            )
        )

        evolution_steps = (
            self._build_evolution_steps(
                governance_maturity=(
                    governance_maturity
                ),
                survivability_maturity=(
                    survivability_maturity
                ),
                resilience_maturity=(
                    resilience_maturity
                ),
                autonomy_maturity=(
                    autonomy_maturity
                ),
                mission_maturity=(
                    mission_maturity
                ),
                operational_maturity=(
                    operational_maturity
                ),
                adaptability=(
                    adaptability
                ),
                learning_velocity=(
                    learning_velocity
                ),
                strategic_alignment=(
                    strategic_alignment
                ),
                operational_stability=(
                    operational_stability
                ),
                volatility=(
                    volatility
                ),
                uncertainty=(
                    uncertainty
                ),
                evolution_window=(
                    evolution_window
                ),
            )
        )

        evolution_confidence = (
            self._evolution_confidence(
                normalized
            )
        )

        explainability_score = (
            self._explainability_score(
                normalized
            )
        )

        strategic_visibility = (
            self
            ._strategic_visibility_score(
                normalized
            )
        )

        assessment = (
            SovereignRuntimeEvolutionAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                evolution_state=(
                    evolution_state
                ),
                projected_outcome=(
                    projected_outcome
                ),
                maturity_level=(
                    maturity_level
                ),
                maturity_growth_probability=(
                    maturity_growth_probability
                ),
                resilience_evolution_probability=(
                    resilience_evolution_probability
                ),
                survivability_evolution_probability=(
                    survivability_evolution_probability
                ),
                governance_evolution_probability=(
                    governance_evolution_probability
                ),
                collapse_probability=(
                    collapse_probability
                ),
                governance_maturity_score=(
                    governance_maturity
                ),
                survivability_maturity_score=(
                    survivability_maturity
                ),
                resilience_maturity_score=(
                    resilience_maturity
                ),
                autonomy_maturity_score=(
                    autonomy_maturity
                ),
                mission_maturity_score=(
                    mission_maturity
                ),
                operational_maturity_score=(
                    operational_maturity
                ),
                adaptability_score=(
                    adaptability
                ),
                learning_velocity_score=(
                    learning_velocity
                ),
                strategic_alignment_score=(
                    strategic_alignment
                ),
                operational_stability_score=(
                    operational_stability
                ),
                volatility_score=(
                    volatility
                ),
                uncertainty_score=(
                    uncertainty
                ),
                evolution_confidence=(
                    evolution_confidence
                ),
                explainability_score=(
                    explainability_score
                ),
                strategic_visibility_score=(
                    strategic_visibility
                ),
                selected_signal_id=(
                    selected
                    .evolution_signal_id
                ),
                selected_signal_type=(
                    selected.signal_type
                ),
                severity=(
                    selected.severity
                ),
                confidence=(
                    selected.confidence
                ),
                evolution_window=(
                    evolution_window
                ),
                mission_id=(
                    mission_id
                    or selected
                    .mission_id
                ),
                tenant_id=(
                    tenant_id
                    or selected
                    .tenant_id
                ),
                case_id=(
                    case_id
                    or selected
                    .case_id
                ),
                correlation_id=(
                    correlation_id
                    or selected
                    .correlation_id
                ),
                evolution_steps=(
                    evolution_steps
                ),
                recommended_actions=(
                    self
                    ._recommended_actions(
                        evolution_state=(
                            evolution_state
                        ),
                        maturity_level=(
                            maturity_level
                        ),
                    )
                ),
                rationale=self._build_rationale(
                    evolution_state=(
                        evolution_state
                    ),
                    projected_outcome=(
                        projected_outcome
                    ),
                    maturity_level=(
                        maturity_level
                    ),
                    maturity_growth_probability=(
                        maturity_growth_probability
                    ),
                    resilience_evolution_probability=(
                        resilience_evolution_probability
                    ),
                    collapse_probability=(
                        collapse_probability
                    ),
                    evolution_window=(
                        evolution_window
                    ),
                    signal_count=len(
                        normalized
                    ),
                ),
                metadata={
                    "source_engines": sorted(
                        {
                            item.source_engine
                            for item in normalized
                        }
                    ),
                },
            )
        )

        self._record_assessment(
            assessment,
            context=context,
        )

        return assessment

    def submit(
        self,
        signals: Sequence[
            EvolutionSignal | Dict[str, Any]
        ],
        *,
        evolution_window: int = (
            DEFAULT_EVOLUTION_WINDOW
        ),
        mission_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> SovereignRuntimeEvolutionAssessment:

        return self.evaluate(
            signals,
            evolution_window=(
                evolution_window
            ),
            mission_id=mission_id,
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=(
                correlation_id
            ),
            context=context,
        )

    def get_recent_assessments(
        self,
        *,
        limit: int = 25,
    ) -> List[
        SovereignRuntimeEvolutionAssessment
    ]:

        limit = max(1, int(limit))

        return list(
            reversed(
                self._assessments[-limit:]
            )
        )

    def snapshot(
        self,
    ) -> SovereignRuntimeEvolutionSnapshot:

        latest = (
            self._assessments[-1]
            if self._assessments
            else None
        )

        return (
            SovereignRuntimeEvolutionSnapshot(
                engine_name=self.engine_name,
                total_signals_seen=(
                    self._signals_seen
                ),
                total_assessments_created=len(
                    self._assessments
                ),
                last_assessment_id=(
                    latest.assessment_id
                    if latest
                    else None
                ),
                last_evolution_state=(
                    latest.evolution_state
                    if latest
                    else None
                ),
                last_maturity_level=(
                    latest.maturity_level
                    if latest
                    else None
                ),
                last_updated_ms=int(
                    time.time() * 1000
                ),
            )
        )

    # ==========================================================
    # EVOLUTION TRAJECTORY
    # ==========================================================

    def _build_evolution_steps(
        self,
        *,
        governance_maturity: float,
        survivability_maturity: float,
        resilience_maturity: float,
        autonomy_maturity: float,
        mission_maturity: float,
        operational_maturity: float,
        adaptability: float,
        learning_velocity: float,
        strategic_alignment: float,
        operational_stability: float,
        volatility: float,
        uncertainty: float,
        evolution_window: int,
    ) -> List[EvolutionStep]:

        steps: List[
            EvolutionStep
        ] = []

        for idx in range(
            max(
                1,
                int(evolution_window),
            )
        ):

            drift = (
                (idx + 1) * 1.5
            )

            governance_maturity = (
                self._clamp_score(
                    governance_maturity
                    + drift * 0.6
                )
            )

            survivability_maturity = (
                self._clamp_score(
                    survivability_maturity
                    + drift * 0.5
                )
            )

            resilience_maturity = (
                self._clamp_score(
                    resilience_maturity
                    + drift * 0.7
                )
            )

            autonomy_maturity = (
                self._clamp_score(
                    autonomy_maturity
                    + drift * 0.8
                )
            )

            mission_maturity = (
                self._clamp_score(
                    mission_maturity
                    + drift * 0.4
                )
            )

            operational_maturity = (
                self._clamp_score(
                    operational_maturity
                    + drift * 0.5
                )
            )

            adaptability = (
                self._clamp_score(
                    adaptability
                    + drift * 0.6
                )
            )

            learning_velocity = (
                self._clamp_score(
                    learning_velocity
                    + drift * 0.7
                )
            )

            strategic_alignment = (
                self._clamp_score(
                    strategic_alignment
                    + drift * 0.5
                )
            )

            operational_stability = (
                self._clamp_score(
                    operational_stability
                    - drift * 0.2
                )
            )

            volatility = (
                self._clamp_score(
                    volatility
                    + drift * 0.15
                )
            )

            uncertainty = (
                self._clamp_score(
                    uncertainty
                    + drift * 0.12
                )
            )

            maturity_growth_probability = (
                self
                ._maturity_growth_probability(
                    governance_maturity=(
                        governance_maturity
                    ),
                    survivability_maturity=(
                        survivability_maturity
                    ),
                    resilience_maturity=(
                        resilience_maturity
                    ),
                    autonomy_maturity=(
                        autonomy_maturity
                    ),
                    mission_maturity=(
                        mission_maturity
                    ),
                    operational_maturity=(
                        operational_maturity
                    ),
                    adaptability=(
                        adaptability
                    ),
                    learning_velocity=(
                        learning_velocity
                    ),
                )
            )

            resilience_evolution_probability = (
                self
                ._resilience_evolution_probability(
                    resilience_maturity=(
                        resilience_maturity
                    ),
                    operational_stability=(
                        operational_stability
                    ),
                    volatility=(
                        volatility
                    ),
                )
            )

            survivability_evolution_probability = (
                self
                ._survivability_evolution_probability(
                    survivability_maturity=(
                        survivability_maturity
                    ),
                    resilience_maturity=(
                        resilience_maturity
                    ),
                    uncertainty=(
                        uncertainty
                    ),
                )
            )

            governance_evolution_probability = (
                self
                ._governance_evolution_probability(
                    governance_maturity=(
                        governance_maturity
                    ),
                    strategic_alignment=(
                        strategic_alignment
                    ),
                    volatility=(
                        volatility
                    ),
                )
            )

            collapse_probability = (
                self
                ._collapse_probability(
                    operational_stability=(
                        operational_stability
                    ),
                    volatility=(
                        volatility
                    ),
                    uncertainty=(
                        uncertainty
                    ),
                    adaptability=(
                        adaptability
                    ),
                    resilience_maturity=(
                        resilience_maturity
                    ),
                )
            )

            state = self._evolution_state(
                maturity_growth_probability=(
                    maturity_growth_probability
                ),
                collapse_probability=(
                    collapse_probability
                ),
                volatility=(
                    volatility
                ),
            )

            outcome = self._projected_outcome(
                evolution_state=(
                    state
                ),
                collapse_probability=(
                    collapse_probability
                ),
                resilience_evolution_probability=(
                    resilience_evolution_probability
                ),
            )

            maturity_level = (
                self._maturity_level(
                    governance_maturity=(
                        governance_maturity
                    ),
                    survivability_maturity=(
                        survivability_maturity
                    ),
                    resilience_maturity=(
                        resilience_maturity
                    ),
                    autonomy_maturity=(
                        autonomy_maturity
                    ),
                    mission_maturity=(
                        mission_maturity
                    ),
                    operational_maturity=(
                        operational_maturity
                    ),
                )
            )

            trajectory_score = (
                statistics.mean(
                    [
                        governance_maturity,
                        survivability_maturity,
                        resilience_maturity,
                        autonomy_maturity,
                        mission_maturity,
                        operational_maturity,
                    ]
                )
            )

            trajectories = (
                self._build_trajectories(
                    state=state,
                    outcome=outcome,
                    maturity_level=(
                        maturity_level
                    ),
                    maturity_growth_probability=(
                        maturity_growth_probability
                    ),
                    resilience_evolution_probability=(
                        resilience_evolution_probability
                    ),
                    survivability_evolution_probability=(
                        survivability_evolution_probability
                    ),
                    governance_evolution_probability=(
                        governance_evolution_probability
                    ),
                    collapse_probability=(
                        collapse_probability
                    ),
                    trajectory_score=(
                        trajectory_score
                    ),
                )
            )

            steps.append(
                EvolutionStep(
                    step_id=str(
                        uuid.uuid4()
                    ),
                    step_index=idx,
                    projected_state=(
                        state
                    ),
                    projected_outcome=(
                        outcome
                    ),
                    projected_maturity_level=(
                        maturity_level
                    ),
                    governance_maturity_score=(
                        governance_maturity
                    ),
                    survivability_maturity_score=(
                        survivability_maturity
                    ),
                    resilience_maturity_score=(
                        resilience_maturity
                    ),
                    autonomy_maturity_score=(
                        autonomy_maturity
                    ),
                    mission_maturity_score=(
                        mission_maturity
                    ),
                    operational_maturity_score=(
                        operational_maturity
                    ),
                    adaptability_score=(
                        adaptability
                    ),
                    learning_velocity_score=(
                        learning_velocity
                    ),
                    strategic_alignment_score=(
                        strategic_alignment
                    ),
                    operational_stability_score=(
                        operational_stability
                    ),
                    volatility_score=(
                        volatility
                    ),
                    uncertainty_score=(
                        uncertainty
                    ),
                    maturity_growth_probability=(
                        maturity_growth_probability
                    ),
                    resilience_evolution_probability=(
                        resilience_evolution_probability
                    ),
                    survivability_evolution_probability=(
                        survivability_evolution_probability
                    ),
                    governance_evolution_probability=(
                        governance_evolution_probability
                    ),
                    collapse_probability=(
                        collapse_probability
                    ),
                    trajectory_score=(
                        trajectory_score
                    ),
                    trajectories=(
                        trajectories
                    ),
                    rationale=(
                        f"Evolution step "
                        f"{idx} projected "
                        f"{state}."
                    ),
                )
            )

        return steps

    def _build_trajectories(
        self,
        *,
        state: str,
        outcome: str,
        maturity_level: str,
        maturity_growth_probability: (
            float
        ),
        resilience_evolution_probability: (
            float
        ),
        survivability_evolution_probability: (
            float
        ),
        governance_evolution_probability: (
            float
        ),
        collapse_probability: float,
        trajectory_score: float,
    ) -> List[EvolutionTrajectory]:

        return [
            EvolutionTrajectory(
                trajectory_id=str(
                    uuid.uuid4()
                ),
                trajectory_name=(
                    "adaptive_growth_path"
                ),
                projected_state=(
                    EVOLUTION_STATE_EVOLVING
                ),
                projected_outcome=(
                    EVOLUTION_OUTCOME_OPTIMIZING
                ),
                projected_maturity_level=(
                    MATURITY_LEVEL_SOVEREIGN
                    if maturity_growth_probability
                    >= 0.8
                    else maturity_level
                ),
                maturity_growth_probability=(
                    self
                    ._clamp_probability(
                        maturity_growth_probability
                        + 0.15
                    )
                ),
                resilience_evolution_probability=(
                    self
                    ._clamp_probability(
                        resilience_evolution_probability
                        + 0.10
                    )
                ),
                survivability_evolution_probability=(
                    self
                    ._clamp_probability(
                        survivability_evolution_probability
                        + 0.10
                    )
                ),
                governance_evolution_probability=(
                    self
                    ._clamp_probability(
                        governance_evolution_probability
                        + 0.10
                    )
                ),
                collapse_probability=(
                    self
                    ._clamp_probability(
                        collapse_probability
                        - 0.15
                    )
                ),
                trajectory_score=(
                    self._clamp_score(
                        trajectory_score
                        + 12
                    )
                ),
                rationale=(
                    "Projected "
                    "adaptive "
                    "runtime growth."
                ),
            ),
            EvolutionTrajectory(
                trajectory_id=str(
                    uuid.uuid4()
                ),
                trajectory_name=(
                    "volatility_degradation_path"
                ),
                projected_state=(
                    EVOLUTION_STATE_DEGRADING
                ),
                projected_outcome=(
                    EVOLUTION_OUTCOME_DEGRADING
                ),
                projected_maturity_level=(
                    MATURITY_LEVEL_EMERGING
                ),
                maturity_growth_probability=(
                    self
                    ._clamp_probability(
                        maturity_growth_probability
                        - 0.25
                    )
                ),
                resilience_evolution_probability=(
                    self
                    ._clamp_probability(
                        resilience_evolution_probability
                        - 0.20
                    )
                ),
                survivability_evolution_probability=(
                    self
                    ._clamp_probability(
                        survivability_evolution_probability
                        - 0.20
                    )
                ),
                governance_evolution_probability=(
                    self
                    ._clamp_probability(
                        governance_evolution_probability
                        - 0.15
                    )
                ),
                collapse_probability=(
                    self
                    ._clamp_probability(
                        collapse_probability
                        + 0.20
                    )
                ),
                trajectory_score=(
                    self._clamp_score(
                        trajectory_score
                        - 20
                    )
                ),
                rationale=(
                    "Projected "
                    "runtime "
                    "degradation "
                    "trajectory."
                ),
            ),
        ]

    # ==========================================================
    # PROBABILITIES
    # ==========================================================

    def _maturity_growth_probability(
        self,
        *,
        governance_maturity: float,
        survivability_maturity: float,
        resilience_maturity: float,
        autonomy_maturity: float,
        mission_maturity: float,
        operational_maturity: float,
        adaptability: float,
        learning_velocity: float,
    ) -> float:

        score = (
            governance_maturity
            + survivability_maturity
            + resilience_maturity
            + autonomy_maturity
            + mission_maturity
            + operational_maturity
            + adaptability
            + learning_velocity
        ) / 800.0

        return self._clamp_probability(
            score
        )

    def _resilience_evolution_probability(
        self,
        *,
        resilience_maturity: float,
        operational_stability: float,
        volatility: float,
    ) -> float:

        score = (
            resilience_maturity
            + operational_stability
            + (100 - volatility)
        ) / 300.0

        return self._clamp_probability(
            score
        )

    def _survivability_evolution_probability(
        self,
        *,
        survivability_maturity: float,
        resilience_maturity: float,
        uncertainty: float,
    ) -> float:

        score = (
            survivability_maturity
            + resilience_maturity
            + (100 - uncertainty)
        ) / 300.0

        return self._clamp_probability(
            score
        )

    def _governance_evolution_probability(
        self,
        *,
        governance_maturity: float,
        strategic_alignment: float,
        volatility: float,
    ) -> float:

        score = (
            governance_maturity
            + strategic_alignment
            + (100 - volatility)
        ) / 300.0

        return self._clamp_probability(
            score
        )

    def _collapse_probability(
        self,
        *,
        operational_stability: float,
        volatility: float,
        uncertainty: float,
        adaptability: float,
        resilience_maturity: float,
    ) -> float:

        score = (
            (100 - operational_stability)
            + volatility
            + uncertainty
            + (100 - adaptability)
            + (100 - resilience_maturity)
        ) / 500.0

        return self._clamp_probability(
            score
        )

    # ==========================================================
    # STATES
    # ==========================================================

    @staticmethod
    def _evolution_state(
        *,
        maturity_growth_probability: (
            float
        ),
        collapse_probability: float,
        volatility: float,
    ) -> str:

        if collapse_probability >= 0.8:
            return EVOLUTION_STATE_DEGRADING

        if maturity_growth_probability >= 0.8:
            return EVOLUTION_STATE_TRANSFORMING

        if maturity_growth_probability >= 0.6:
            return EVOLUTION_STATE_EVOLVING

        if volatility >= 60:
            return EVOLUTION_STATE_ADAPTING

        return EVOLUTION_STATE_STABLE

    @staticmethod
    def _projected_outcome(
        *,
        evolution_state: str,
        collapse_probability: float,
        resilience_evolution_probability: (
            float
        ),
    ) -> str:

        if collapse_probability >= 0.8:
            return (
                EVOLUTION_OUTCOME_COLLAPSE_RISK
            )

        if (
            resilience_evolution_probability
            >= 0.8
        ):
            return (
                EVOLUTION_OUTCOME_RESILIENT
            )

        if (
            evolution_state
            == EVOLUTION_STATE_TRANSFORMING
        ):
            return (
                EVOLUTION_OUTCOME_OPTIMIZING
            )

        if (
            evolution_state
            == EVOLUTION_STATE_DEGRADING
        ):
            return (
                EVOLUTION_OUTCOME_DEGRADING
            )

        return (
            EVOLUTION_OUTCOME_VOLATILE
        )

    @staticmethod
    def _maturity_level(
        *,
        governance_maturity: float,
        survivability_maturity: float,
        resilience_maturity: float,
        autonomy_maturity: float,
        mission_maturity: float,
        operational_maturity: float,
    ) -> str:

        average = statistics.mean(
            [
                governance_maturity,
                survivability_maturity,
                resilience_maturity,
                autonomy_maturity,
                mission_maturity,
                operational_maturity,
            ]
        )

        if average >= 90:
            return MATURITY_LEVEL_SOVEREIGN

        if average >= 75:
            return MATURITY_LEVEL_AUTONOMOUS

        if average >= 60:
            return MATURITY_LEVEL_ADAPTIVE

        if average >= 40:
            return MATURITY_LEVEL_EMERGING

        return MATURITY_LEVEL_INITIAL

    # ==========================================================
    # SCORING
    # ==========================================================

    def _evolution_confidence(
        self,
        signals: Sequence[
            EvolutionSignal
        ],
    ) -> float:

        if not signals:
            return 0.0

        return self._clamp_probability(
            statistics.mean(
                [
                    item.confidence
                    for item in signals
                ]
            )
        )

    def _explainability_score(
        self,
        signals: Sequence[
            EvolutionSignal
        ],
    ) -> float:

        if not signals:
            return 0.0

        explained = 0

        for item in signals:

            if item.summary:
                explained += 1

            if item.signal_type:
                explained += 1

            if item.source_engine:
                explained += 1

        return self._clamp_score(
            (
                explained
                / (
                    len(signals) * 3
                )
            )
            * 100
        )

    def _strategic_visibility_score(
        self,
        signals: Sequence[
            EvolutionSignal
        ],
    ) -> float:

        if not signals:
            return 0.0

        visible = 0

        for item in signals:

            if item.mission_id:
                visible += 1

            if item.tenant_id:
                visible += 1

            if item.domain:
                visible += 1

        return self._clamp_score(
            (
                visible
                / (
                    len(signals) * 3
                )
            )
            * 100
        )

    # ==========================================================
    # ACTIONS
    # ==========================================================

    def _recommended_actions(
        self,
        *,
        evolution_state: str,
        maturity_level: str,
    ) -> List[Dict[str, Any]]:

        actions = [
            {
                "action": (
                    "record_runtime_evolution_lineage"
                )
            },
            {
                "action": (
                    "record_runtime_evolution_evidence"
                )
            },
        ]

        if (
            evolution_state
            == EVOLUTION_STATE_ADAPTING
        ):
            actions.append(
                {
                    "action": (
                        "review_adaptive_runtime_controls"
                    )
                }
            )

        if (
            evolution_state
            == EVOLUTION_STATE_DEGRADING
        ):
            actions.append(
                {
                    "action": (
                        "stabilize_runtime_posture"
                    )
                }
            )

        if (
            maturity_level
            == MATURITY_LEVEL_SOVEREIGN
        ):
            actions.append(
                {
                    "action": (
                        "optimize_sovereign_runtime_coordination"
                    )
                }
            )

        return actions

    # ==========================================================
    # RATIONALE
    # ==========================================================

    @staticmethod
    def _build_rationale(
        *,
        evolution_state: str,
        projected_outcome: str,
        maturity_level: str,
        maturity_growth_probability: (
            float
        ),
        resilience_evolution_probability: (
            float
        ),
        collapse_probability: float,
        evolution_window: int,
        signal_count: int,
    ) -> str:

        return (
            f"Sovereign runtime "
            f"evolution evaluated "
            f"{signal_count} signal(s) "
            f"across evolution window "
            f"{evolution_window}. "
            f"Evolution state "
            f"{evolution_state}; "
            f"projected outcome "
            f"{projected_outcome}; "
            f"maturity level "
            f"{maturity_level}. "
            f"Maturity growth probability "
            f"{maturity_growth_probability:.2f}; "
            f"resilience evolution probability "
            f"{resilience_evolution_probability:.2f}; "
            f"collapse probability "
            f"{collapse_probability:.2f}."
        )

    # ==========================================================
    # RECORDING
    # ==========================================================

    def _record_assessment(
        self,
        assessment: (
            SovereignRuntimeEvolutionAssessment
        ),
        *,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        self._assessments.append(
            assessment
        )

        self._write_to_memory(
            assessment,
            context=context,
        )

        self._write_to_lineage(
            assessment,
            context=context,
        )

        self._write_to_evidence(
            assessment,
            context=context,
        )

        self._emit_event(
            assessment,
            context=context,
        )

    def _write_to_memory(
        self,
        assessment: (
            SovereignRuntimeEvolutionAssessment
        ),
        *,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        if (
            self.operational_memory_engine
            is None
        ):
            return

        payload = {
            "type": (
                "SOVEREIGN_RUNTIME_EVOLUTION_ASSESSMENT"
            ),
            "assessment": asdict(
                assessment
            ),
            "context": (
                context or {}
            ),
        }

        try:

            if hasattr(
                self.operational_memory_engine,
                "append_memory",
            ):
                self.operational_memory_engine.append_memory(
                    payload
                )

        except Exception as exc:
            print(
                f"⚠️ Runtime evolution memory write failed: {exc}"
            )

    def _write_to_lineage(
        self,
        assessment: (
            SovereignRuntimeEvolutionAssessment
        ),
        *,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        if self.lineage_engine is None:
            return

        payload = {
            "lineage_type": (
                "RUNTIME_EVOLUTION"
            ),
            "source_engine": (
                self.engine_name
            ),
            "summary": (
                assessment.rationale
            ),
            "severity": (
                assessment.severity
            ),
            "confidence": (
                assessment.confidence
            ),
            "context": {
                "assessment": asdict(
                    assessment
                ),
                "context": (
                    context or {}
                ),
            },
        }

        try:

            if hasattr(
                self.lineage_engine,
                "record_lineage",
            ):
                self.lineage_engine.record_lineage(
                    payload
                )

        except Exception as exc:
            print(
                f"⚠️ Runtime evolution lineage write failed: {exc}"
            )

    def _write_to_evidence(
        self,
        assessment: (
            SovereignRuntimeEvolutionAssessment
        ),
        *,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        if (
            self
            .fedramp_evidence_lineage_engine
            is None
        ):
            return

        payload = {
            "evidence_type": (
                "RUNTIME_EVOLUTION"
            ),
            "source_engine": (
                self.engine_name
            ),
            "summary": (
                assessment.rationale
            ),
            "severity": (
                assessment.severity
            ),
            "confidence": (
                assessment.confidence
            ),
            "evidence_payload": {
                "assessment": asdict(
                    assessment
                ),
                "context": (
                    context or {}
                ),
            },
        }

        try:

            if hasattr(
                self
                .fedramp_evidence_lineage_engine,
                "record_evidence",
            ):
                self.fedramp_evidence_lineage_engine.record_evidence(
                    payload
                )

        except Exception as exc:
            print(
                f"⚠️ Runtime evolution evidence write failed: {exc}"
            )

    def _emit_event(
        self,
        assessment: (
            SovereignRuntimeEvolutionAssessment
        ),
        *,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        if self.event_bus is None:
            return

        payload = {
            "event_type": (
                "SOVEREIGN_RUNTIME_EVOLUTION_ASSESSMENT"
            ),
            "engine_name": (
                self.engine_name
            ),
            "assessment": asdict(
                assessment
            ),
            "context": (
                context or {}
            ),
        }

        try:

            if hasattr(
                self.event_bus,
                "emit",
            ):
                self.event_bus.emit(
                    (
                        "SOVEREIGN_RUNTIME_EVOLUTION_ASSESSMENT"
                    ),
                    payload,
                )

        except Exception as exc:
            print(
                f"⚠️ Runtime evolution event emit failed: {exc}"
            )

    # ==========================================================
    # NORMALIZATION
    # ==========================================================

    def _normalize_signal(
        self,
        item: (
            EvolutionSignal
            | Dict[str, Any]
        ),
        *,
        mission_id: Optional[str],
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> EvolutionSignal:

        if isinstance(
            item,
            EvolutionSignal,
        ):
            return item

        return EvolutionSignal(
            evolution_signal_id=str(
                item.get(
                    "evolution_signal_id"
                )
                or uuid.uuid4()
            ),
            signal_type=str(
                item.get(
                    "signal_type"
                )
                or "UNKNOWN"
            ).upper(),
            domain=self._safe_domain(
                item.get("domain")
            ),
            source_engine=str(
                item.get(
                    "source_engine"
                )
                or "unknown_engine"
            ),
            severity=self._safe_severity(
                item.get("severity")
            ),
            confidence=(
                self
                ._clamp_probability(
                    item.get(
                        "confidence",
                        0.0,
                    )
                )
            ),
            summary=str(
                item.get("summary")
                or ""
            ),
            mission_id=(
                mission_id
                or item.get(
                    "mission_id"
                )
            ),
            tenant_id=(
                tenant_id
                or item.get(
                    "tenant_id"
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
            governance_maturity_score=(
                self._clamp_score(
                    item.get(
                        "governance_maturity_score",
                        0.0,
                    )
                )
            ),
            survivability_maturity_score=(
                self._clamp_score(
                    item.get(
                        "survivability_maturity_score",
                        0.0,
                    )
                )
            ),
            resilience_maturity_score=(
                self._clamp_score(
                    item.get(
                        "resilience_maturity_score",
                        0.0,
                    )
                )
            ),
            autonomy_maturity_score=(
                self._clamp_score(
                    item.get(
                        "autonomy_maturity_score",
                        0.0,
                    )
                )
            ),
            mission_maturity_score=(
                self._clamp_score(
                    item.get(
                        "mission_maturity_score",
                        0.0,
                    )
                )
            ),
            operational_maturity_score=(
                self._clamp_score(
                    item.get(
                        "operational_maturity_score",
                        0.0,
                    )
                )
            ),
            adaptability_score=(
                self._clamp_score(
                    item.get(
                        "adaptability_score",
                        0.0,
                    )
                )
            ),
            learning_velocity_score=(
                self._clamp_score(
                    item.get(
                        "learning_velocity_score",
                        0.0,
                    )
                )
            ),
            strategic_alignment_score=(
                self._clamp_score(
                    item.get(
                        "strategic_alignment_score",
                        0.0,
                    )
                )
            ),
            operational_stability_score=(
                self._clamp_score(
                    item.get(
                        "operational_stability_score",
                        100.0,
                    )
                )
            ),
            volatility_score=(
                self._clamp_score(
                    item.get(
                        "volatility_score",
                        0.0,
                    )
                )
            ),
            uncertainty_score=(
                self._clamp_score(
                    item.get(
                        "uncertainty_score",
                        0.0,
                    )
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
        mission_id: Optional[str],
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> (
        SovereignRuntimeEvolutionAssessment
    ):

        return (
            SovereignRuntimeEvolutionAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                evolution_state=(
                    EVOLUTION_STATE_STABLE
                ),
                projected_outcome=(
                    EVOLUTION_OUTCOME_RESILIENT
                ),
                maturity_level=(
                    MATURITY_LEVEL_INITIAL
                ),
                maturity_growth_probability=0.0,
                resilience_evolution_probability=0.0,
                survivability_evolution_probability=0.0,
                governance_evolution_probability=0.0,
                collapse_probability=0.0,
                governance_maturity_score=0.0,
                survivability_maturity_score=0.0,
                resilience_maturity_score=0.0,
                autonomy_maturity_score=0.0,
                mission_maturity_score=0.0,
                operational_maturity_score=0.0,
                adaptability_score=0.0,
                learning_velocity_score=0.0,
                strategic_alignment_score=0.0,
                operational_stability_score=100.0,
                volatility_score=0.0,
                uncertainty_score=0.0,
                evolution_confidence=1.0,
                explainability_score=100.0,
                strategic_visibility_score=100.0,
                selected_signal_id=None,
                selected_signal_type=None,
                severity=(
                    EvolutionSeverity
                    .INFO.value
                ),
                confidence=1.0,
                evolution_window=0,
                mission_id=mission_id,
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=(
                    correlation_id
                ),
                evolution_steps=[],
                recommended_actions=[
                    {
                        "action": (
                            "continue_runtime_learning"
                        )
                    }
                ],
                rationale=(
                    "No runtime "
                    "evolution signals submitted."
                ),
                metadata={},
            )
        )

    def _select_primary_signal(
        self,
        signals: Sequence[
            EvolutionSignal
        ],
    ) -> EvolutionSignal:

        return sorted(
            signals,
            key=lambda item: (
                item
                .volatility_score,
                item
                .uncertainty_score,
                -item.created_at_ms,
            ),
            reverse=True,
        )[0]

    # ==========================================================
    # HELPERS
    # ==========================================================

    @staticmethod
    def _safe_domain(
        value: Any,
    ) -> str:

        value = str(
            value
            or EvolutionDomain
            .UNKNOWN.value
        ).upper()

        valid = {
            item.value
            for item in EvolutionDomain
        }

        return (
            value
            if value in valid
            else EvolutionDomain
            .UNKNOWN.value
        )

    @staticmethod
    def _safe_severity(
        value: Any,
    ) -> str:

        value = str(
            value
            or EvolutionSeverity
            .INFO.value
        ).upper()

        valid = {
            item.value
            for item in EvolutionSeverity
        }

        return (
            value
            if value in valid
            else EvolutionSeverity
            .INFO.value
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

    @staticmethod
    def _avg_score(
        values: Sequence[float],
    ) -> float:

        if not values:
            return 0.0

        return max(
            0.0,
            min(
                100.0,
                statistics.mean(values),
            ),
        )


def build_sovereign_runtime_evolution_engine(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: (
        Optional[Any]
    ) = None,
) -> SovereignRuntimeEvolutionEngine:

    return (
        SovereignRuntimeEvolutionEngine(
            event_bus=event_bus,
            operational_memory_engine=(
                operational_memory_engine
            ),
            lineage_engine=lineage_engine,
            fedramp_evidence_lineage_engine=(
                fedramp_evidence_lineage_engine
            ),
        )
    )