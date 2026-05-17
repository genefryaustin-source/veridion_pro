"""
core/runtime/sovereign_operational_war_gaming_engine.py

Sovereign Operational War-Gaming Engine

Strategic sovereign cyber operational war-gaming cognition layer.

This subsystem simulates:
- strategic cyber conflicts
- operational doctrines
- resilience allocation futures
- governance escalation futures
- long-duration operational campaigns
- adversarial adaptation cycles
- mission survivability futures
- strategic stabilization paths
- operational resource exhaustion

IMPORTANT:
This subsystem DOES NOT:
- execute cyber operations
- manipulate infrastructure
- perform offensive actions
- attack systems
- mutate production environments

It ONLY:
- simulates strategic operational futures
- evaluates doctrine survivability
- models resilience allocation outcomes
- forecasts operational conflict futures
- records replayable war-gaming lineage/evidence
"""

from __future__ import annotations

import statistics
import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


DEFAULT_ENGINE_NAME = (
    "sovereign_operational_war_gaming_engine"
)

DEFAULT_WAR_GAME_DEPTH = 12


WAR_STATE_STABLE = "STABLE"
WAR_STATE_CONTESTED = "CONTESTED"
WAR_STATE_ESCALATED = "ESCALATED"
WAR_STATE_RESOURCE_EXHAUSTION = (
    "RESOURCE_EXHAUSTION"
)
WAR_STATE_MISSION_CRITICAL = (
    "MISSION_CRITICAL"
)
WAR_STATE_SYSTEMIC_RISK = (
    "SYSTEMIC_RISK"
)

WAR_OUTCOME_STABILIZED = "STABILIZED"
WAR_OUTCOME_CONTESTED = "CONTESTED"
WAR_OUTCOME_DEGRADED = "DEGRADED"
WAR_OUTCOME_ESCALATED = "ESCALATED"
WAR_OUTCOME_SYSTEMIC_RISK = (
    "SYSTEMIC_RISK"
)

RECOMMENDATION_MONITOR = "MONITOR"
RECOMMENDATION_DOCTRINE_REALIGNMENT = (
    "DOCTRINE_REALIGNMENT"
)
RECOMMENDATION_RESILIENCE_REBALANCING = (
    "RESILIENCE_REBALANCING"
)
RECOMMENDATION_MISSION_PRESERVATION = (
    "MISSION_PRESERVATION"
)
RECOMMENDATION_STRATEGIC_ESCALATION = (
    "STRATEGIC_ESCALATION"
)
RECOMMENDATION_GOVERNANCE_INTERVENTION = (
    "GOVERNANCE_INTERVENTION"
)


class WarGameSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class WarDoctrine(str, Enum):
    AGGRESSIVE_CONTAINMENT = (
        "AGGRESSIVE_CONTAINMENT"
    )
    RESILIENCE_FIRST = (
        "RESILIENCE_FIRST"
    )
    GOVERNANCE_HEAVY = (
        "GOVERNANCE_HEAVY"
    )
    MISSION_PRESERVATION = (
        "MISSION_PRESERVATION"
    )
    DISTRIBUTED_DEFENSE = (
        "DISTRIBUTED_DEFENSE"
    )
    BALANCED_OPERATIONAL = (
        "BALANCED_OPERATIONAL"
    )
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class WarGameSignal:
    war_signal_id: str

    doctrine: str
    source_engine: str

    severity: str
    confidence: float

    summary: str

    mission_id: Optional[str] = None
    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    doctrine_pressure_score: float = 0.0
    resilience_exhaustion_score: float = 0.0
    operational_decay_score: float = 0.0
    governance_fatigue_score: float = 0.0
    adversarial_adaptation_score: float = (
        0.0
    )
    resource_saturation_score: float = (
        0.0
    )
    mission_survivability_score: float = (
        100.0
    )
    stabilization_capacity_score: float = (
        100.0
    )
    operational_continuity_score: float = (
        100.0
    )
    strategic_coordination_score: float = (
        100.0
    )
    systemic_risk_score: float = 0.0
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
class WarGameBranch:
    branch_id: str

    branch_name: str

    projected_state: str
    projected_outcome: str

    stabilization_probability: float
    doctrine_survivability_probability: (
        float
    )
    mission_survivability_probability: (
        float
    )
    systemic_risk_probability: float

    branch_score: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


@dataclass(frozen=True)
class WarGameSimulationStep:
    step_id: str

    step_index: int

    projected_state: str
    projected_outcome: str

    doctrine_pressure_score: float
    resilience_exhaustion_score: float
    operational_decay_score: float
    governance_fatigue_score: float
    adversarial_adaptation_score: float
    resource_saturation_score: float
    mission_survivability_score: float
    stabilization_capacity_score: float
    operational_continuity_score: float
    strategic_coordination_score: float
    systemic_risk_score: float
    uncertainty_score: float

    stabilization_probability: float
    doctrine_survivability_probability: (
        float
    )
    mission_survivability_probability: (
        float
    )
    systemic_risk_probability: float

    war_risk_score: float

    branches: List[
        WarGameBranch
    ] = field(default_factory=list)

    rationale: str = ""

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


@dataclass(frozen=True)
class SovereignWarGameAssessment:
    assessment_id: str

    war_state: str
    projected_outcome: str
    recommendation: str

    doctrine_pressure_score: float
    resilience_exhaustion_score: float
    operational_decay_score: float
    governance_fatigue_score: float
    adversarial_adaptation_score: float
    resource_saturation_score: float
    mission_survivability_score: float
    stabilization_capacity_score: float
    operational_continuity_score: float
    strategic_coordination_score: float
    systemic_risk_score: float
    uncertainty_score: float

    stabilization_probability: float
    doctrine_survivability_probability: (
        float
    )
    mission_survivability_probability: (
        float
    )
    systemic_risk_probability: float

    war_risk_score: float

    explainability_score: float
    war_confidence: float

    selected_signal_id: Optional[str]
    selected_doctrine: Optional[str]

    severity: str
    confidence: float

    war_game_depth: int

    mission_id: Optional[str]
    tenant_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    simulation_steps: List[
        WarGameSimulationStep
    ]

    recommended_controls: List[str]

    recommended_actions: List[
        Dict[str, Any]
    ]

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


class SovereignOperationalWarGamingEngine:
    """
    Sovereign strategic operational war-gaming cognition.
    """

    def __init__(
        self,
        *,
        engine_name: str = (
            DEFAULT_ENGINE_NAME
        ),
        event_bus: Optional[Any] = None,
        battle_management_engine: Optional[
            Any
        ] = None,
        campaign_engine: Optional[Any] = None,
        runtime_evolution_engine: Optional[
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

        self.battle_management_engine = (
            battle_management_engine
        )

        self.campaign_engine = (
            campaign_engine
        )

        self.runtime_evolution_engine = (
            runtime_evolution_engine
        )

        self.operational_memory_engine = (
            operational_memory_engine
        )

        self.lineage_engine = lineage_engine

        self.fedramp_evidence_lineage_engine = (
            fedramp_evidence_lineage_engine
        )

        self._signals_seen = 0

        self._assessments: List[
            SovereignWarGameAssessment
        ] = []

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def evaluate(
        self,
        signals: Sequence[
            WarGameSignal | Dict[str, Any]
        ],
        *,
        war_game_depth: int = (
            DEFAULT_WAR_GAME_DEPTH
        ),
        mission_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> SovereignWarGameAssessment:

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

        doctrine_pressure = (
            self._avg_score(
                [
                    s.doctrine_pressure_score
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

        operational_decay = (
            self._avg_score(
                [
                    s
                    .operational_decay_score
                    for s in normalized
                ]
            )
        )

        governance_fatigue = (
            self._avg_score(
                [
                    s
                    .governance_fatigue_score
                    for s in normalized
                ]
            )
        )

        adversarial_adaptation = (
            self._avg_score(
                [
                    s
                    .adversarial_adaptation_score
                    for s in normalized
                ]
            )
        )

        resource_saturation = (
            self._avg_score(
                [
                    s
                    .resource_saturation_score
                    for s in normalized
                ]
            )
        )

        mission_survivability = (
            self._avg_score(
                [
                    s
                    .mission_survivability_score
                    for s in normalized
                ]
            )
        )

        stabilization_capacity = (
            self._avg_score(
                [
                    s
                    .stabilization_capacity_score
                    for s in normalized
                ]
            )
        )

        operational_continuity = (
            self._avg_score(
                [
                    s
                    .operational_continuity_score
                    for s in normalized
                ]
            )
        )

        strategic_coordination = (
            self._avg_score(
                [
                    s
                    .strategic_coordination_score
                    for s in normalized
                ]
            )
        )

        systemic_risk = (
            self._avg_score(
                [
                    s.systemic_risk_score
                    for s in normalized
                ]
            )
        )

        uncertainty = (
            self._avg_score(
                [
                    s.uncertainty_score
                    for s in normalized
                ]
            )
        )

        stabilization_probability = (
            self
            ._stabilization_probability(
                stabilization_capacity_score=(
                    stabilization_capacity
                ),
                operational_continuity_score=(
                    operational_continuity
                ),
                strategic_coordination_score=(
                    strategic_coordination
                ),
                doctrine_pressure_score=(
                    doctrine_pressure
                ),
                resilience_exhaustion_score=(
                    resilience_exhaustion
                ),
                operational_decay_score=(
                    operational_decay
                ),
            )
        )

        doctrine_survivability = (
            self
            ._doctrine_survivability_probability(
                doctrine_pressure_score=(
                    doctrine_pressure
                ),
                governance_fatigue_score=(
                    governance_fatigue
                ),
                adversarial_adaptation_score=(
                    adversarial_adaptation
                ),
                strategic_coordination_score=(
                    strategic_coordination
                ),
            )
        )

        mission_survivability_probability = (
            self
            ._mission_survivability_probability(
                mission_survivability_score=(
                    mission_survivability
                ),
                operational_continuity_score=(
                    operational_continuity
                ),
                systemic_risk_score=(
                    systemic_risk
                ),
            )
        )

        systemic_risk_probability = (
            self
            ._systemic_risk_probability(
                resilience_exhaustion_score=(
                    resilience_exhaustion
                ),
                operational_decay_score=(
                    operational_decay
                ),
                governance_fatigue_score=(
                    governance_fatigue
                ),
                adversarial_adaptation_score=(
                    adversarial_adaptation
                ),
                resource_saturation_score=(
                    resource_saturation
                ),
                systemic_risk_score=(
                    systemic_risk
                ),
                uncertainty_score=(
                    uncertainty
                ),
            )
        )

        war_risk = (
            self._war_risk_score(
                doctrine_pressure_score=(
                    doctrine_pressure
                ),
                resilience_exhaustion_score=(
                    resilience_exhaustion
                ),
                operational_decay_score=(
                    operational_decay
                ),
                governance_fatigue_score=(
                    governance_fatigue
                ),
                adversarial_adaptation_score=(
                    adversarial_adaptation
                ),
                resource_saturation_score=(
                    resource_saturation
                ),
                systemic_risk_score=(
                    systemic_risk
                ),
                stabilization_probability=(
                    stabilization_probability
                ),
                doctrine_survivability_probability=(
                    doctrine_survivability
                ),
                mission_survivability_probability=(
                    mission_survivability_probability
                ),
                systemic_risk_probability=(
                    systemic_risk_probability
                ),
            )
        )

        war_state = self._war_state(
            war_risk_score=war_risk,
            stabilization_probability=(
                stabilization_probability
            ),
            mission_survivability_probability=(
                mission_survivability_probability
            ),
            systemic_risk_probability=(
                systemic_risk_probability
            ),
        )

        projected_outcome = (
            self._projected_outcome(
                war_state=war_state,
                stabilization_probability=(
                    stabilization_probability
                ),
                systemic_risk_probability=(
                    systemic_risk_probability
                ),
            )
        )

        recommendation = (
            self._recommendation(
                war_state=war_state,
                doctrine_pressure_score=(
                    doctrine_pressure
                ),
                resource_saturation_score=(
                    resource_saturation
                ),
                mission_survivability_score=(
                    mission_survivability
                ),
            )
        )

        steps = (
            self._build_war_game_steps(
                doctrine_pressure_score=(
                    doctrine_pressure
                ),
                resilience_exhaustion_score=(
                    resilience_exhaustion
                ),
                operational_decay_score=(
                    operational_decay
                ),
                governance_fatigue_score=(
                    governance_fatigue
                ),
                adversarial_adaptation_score=(
                    adversarial_adaptation
                ),
                resource_saturation_score=(
                    resource_saturation
                ),
                mission_survivability_score=(
                    mission_survivability
                ),
                stabilization_capacity_score=(
                    stabilization_capacity
                ),
                operational_continuity_score=(
                    operational_continuity
                ),
                strategic_coordination_score=(
                    strategic_coordination
                ),
                systemic_risk_score=(
                    systemic_risk
                ),
                uncertainty_score=(
                    uncertainty
                ),
                war_game_depth=(
                    war_game_depth
                ),
            )
        )

        assessment = (
            SovereignWarGameAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                war_state=war_state,
                projected_outcome=(
                    projected_outcome
                ),
                recommendation=(
                    recommendation
                ),
                doctrine_pressure_score=(
                    doctrine_pressure
                ),
                resilience_exhaustion_score=(
                    resilience_exhaustion
                ),
                operational_decay_score=(
                    operational_decay
                ),
                governance_fatigue_score=(
                    governance_fatigue
                ),
                adversarial_adaptation_score=(
                    adversarial_adaptation
                ),
                resource_saturation_score=(
                    resource_saturation
                ),
                mission_survivability_score=(
                    mission_survivability
                ),
                stabilization_capacity_score=(
                    stabilization_capacity
                ),
                operational_continuity_score=(
                    operational_continuity
                ),
                strategic_coordination_score=(
                    strategic_coordination
                ),
                systemic_risk_score=(
                    systemic_risk
                ),
                uncertainty_score=(
                    uncertainty
                ),
                stabilization_probability=(
                    stabilization_probability
                ),
                doctrine_survivability_probability=(
                    doctrine_survivability
                ),
                mission_survivability_probability=(
                    mission_survivability_probability
                ),
                systemic_risk_probability=(
                    systemic_risk_probability
                ),
                war_risk_score=(
                    war_risk
                ),
                explainability_score=(
                    self
                    ._explainability_score(
                        normalized
                    )
                ),
                war_confidence=(
                    self
                    ._war_confidence(
                        normalized
                    )
                ),
                selected_signal_id=(
                    selected.war_signal_id
                ),
                selected_doctrine=(
                    selected.doctrine
                ),
                severity=(
                    selected.severity
                ),
                confidence=(
                    selected.confidence
                ),
                war_game_depth=(
                    war_game_depth
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
                    or selected.case_id
                ),
                correlation_id=(
                    correlation_id
                    or selected
                    .correlation_id
                ),
                simulation_steps=steps,
                recommended_controls=(
                    self
                    ._recommended_controls(
                        war_state=war_state,
                        recommendation=(
                            recommendation
                        ),
                    )
                ),
                recommended_actions=(
                    self
                    ._recommended_actions(
                        war_state=war_state,
                        recommendation=(
                            recommendation
                        ),
                    )
                ),
                rationale=(
                    self._build_rationale(
                        war_state=war_state,
                        projected_outcome=(
                            projected_outcome
                        ),
                        recommendation=(
                            recommendation
                        ),
                        war_risk_score=(
                            war_risk
                        ),
                        stabilization_probability=(
                            stabilization_probability
                        ),
                        doctrine_survivability_probability=(
                            doctrine_survivability
                        ),
                        mission_survivability_probability=(
                            mission_survivability_probability
                        ),
                        systemic_risk_probability=(
                            systemic_risk_probability
                        ),
                        signal_count=len(
                            normalized
                        ),
                        war_game_depth=(
                            war_game_depth
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
    # WAR-GAME SIMULATION
    # ==========================================================

    def _build_war_game_steps(
        self,
        *,
        doctrine_pressure_score: float,
        resilience_exhaustion_score: float,
        operational_decay_score: float,
        governance_fatigue_score: float,
        adversarial_adaptation_score: float,
        resource_saturation_score: float,
        mission_survivability_score: float,
        stabilization_capacity_score: float,
        operational_continuity_score: float,
        strategic_coordination_score: float,
        systemic_risk_score: float,
        uncertainty_score: float,
        war_game_depth: int,
    ) -> List[WarGameSimulationStep]:

        steps: List[
            WarGameSimulationStep
        ] = []

        for idx in range(
            max(1, int(war_game_depth))
        ):

            stabilization_probability = (
                self
                ._stabilization_probability(
                    stabilization_capacity_score=(
                        stabilization_capacity_score
                    ),
                    operational_continuity_score=(
                        operational_continuity_score
                    ),
                    strategic_coordination_score=(
                        strategic_coordination_score
                    ),
                    doctrine_pressure_score=(
                        doctrine_pressure_score
                    ),
                    resilience_exhaustion_score=(
                        resilience_exhaustion_score
                    ),
                    operational_decay_score=(
                        operational_decay_score
                    ),
                )
            )

            doctrine_survivability = (
                self
                ._doctrine_survivability_probability(
                    doctrine_pressure_score=(
                        doctrine_pressure_score
                    ),
                    governance_fatigue_score=(
                        governance_fatigue_score
                    ),
                    adversarial_adaptation_score=(
                        adversarial_adaptation_score
                    ),
                    strategic_coordination_score=(
                        strategic_coordination_score
                    ),
                )
            )

            mission_survivability_probability = (
                self
                ._mission_survivability_probability(
                    mission_survivability_score=(
                        mission_survivability_score
                    ),
                    operational_continuity_score=(
                        operational_continuity_score
                    ),
                    systemic_risk_score=(
                        systemic_risk_score
                    ),
                )
            )

            systemic_risk_probability = (
                self
                ._systemic_risk_probability(
                    resilience_exhaustion_score=(
                        resilience_exhaustion_score
                    ),
                    operational_decay_score=(
                        operational_decay_score
                    ),
                    governance_fatigue_score=(
                        governance_fatigue_score
                    ),
                    adversarial_adaptation_score=(
                        adversarial_adaptation_score
                    ),
                    resource_saturation_score=(
                        resource_saturation_score
                    ),
                    systemic_risk_score=(
                        systemic_risk_score
                    ),
                    uncertainty_score=(
                        uncertainty_score
                    ),
                )
            )

            war_risk = (
                self._war_risk_score(
                    doctrine_pressure_score=(
                        doctrine_pressure_score
                    ),
                    resilience_exhaustion_score=(
                        resilience_exhaustion_score
                    ),
                    operational_decay_score=(
                        operational_decay_score
                    ),
                    governance_fatigue_score=(
                        governance_fatigue_score
                    ),
                    adversarial_adaptation_score=(
                        adversarial_adaptation_score
                    ),
                    resource_saturation_score=(
                        resource_saturation_score
                    ),
                    systemic_risk_score=(
                        systemic_risk_score
                    ),
                    stabilization_probability=(
                        stabilization_probability
                    ),
                    doctrine_survivability_probability=(
                        doctrine_survivability
                    ),
                    mission_survivability_probability=(
                        mission_survivability_probability
                    ),
                    systemic_risk_probability=(
                        systemic_risk_probability
                    ),
                )
            )

            state = self._war_state(
                war_risk_score=war_risk,
                stabilization_probability=(
                    stabilization_probability
                ),
                mission_survivability_probability=(
                    mission_survivability_probability
                ),
                systemic_risk_probability=(
                    systemic_risk_probability
                ),
            )

            outcome = (
                self._projected_outcome(
                    war_state=state,
                    stabilization_probability=(
                        stabilization_probability
                    ),
                    systemic_risk_probability=(
                        systemic_risk_probability
                    ),
                )
            )

            branches = (
                self._build_branches(
                    war_state=state,
                    stabilization_probability=(
                        stabilization_probability
                    ),
                    doctrine_survivability_probability=(
                        doctrine_survivability
                    ),
                    mission_survivability_probability=(
                        mission_survivability_probability
                    ),
                    systemic_risk_probability=(
                        systemic_risk_probability
                    ),
                    war_risk_score=(
                        war_risk
                    ),
                )
            )

            steps.append(
                WarGameSimulationStep(
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
                    doctrine_pressure_score=(
                        doctrine_pressure_score
                    ),
                    resilience_exhaustion_score=(
                        resilience_exhaustion_score
                    ),
                    operational_decay_score=(
                        operational_decay_score
                    ),
                    governance_fatigue_score=(
                        governance_fatigue_score
                    ),
                    adversarial_adaptation_score=(
                        adversarial_adaptation_score
                    ),
                    resource_saturation_score=(
                        resource_saturation_score
                    ),
                    mission_survivability_score=(
                        mission_survivability_score
                    ),
                    stabilization_capacity_score=(
                        stabilization_capacity_score
                    ),
                    operational_continuity_score=(
                        operational_continuity_score
                    ),
                    strategic_coordination_score=(
                        strategic_coordination_score
                    ),
                    systemic_risk_score=(
                        systemic_risk_score
                    ),
                    uncertainty_score=(
                        uncertainty_score
                    ),
                    stabilization_probability=(
                        stabilization_probability
                    ),
                    doctrine_survivability_probability=(
                        doctrine_survivability
                    ),
                    mission_survivability_probability=(
                        mission_survivability_probability
                    ),
                    systemic_risk_probability=(
                        systemic_risk_probability
                    ),
                    war_risk_score=(
                        war_risk
                    ),
                    branches=branches,
                    rationale=(
                        f"War-game "
                        f"simulation step "
                        f"{idx} projected "
                        f"{state}."
                    ),
                )
            )

            doctrine_pressure_score = (
                self._clamp_score(
                    doctrine_pressure_score
                    + 2.0
                )
            )

            resilience_exhaustion_score = (
                self._clamp_score(
                    resilience_exhaustion_score
                    + 2.2
                )
            )

            operational_decay_score = (
                self._clamp_score(
                    operational_decay_score
                    + 2.0
                )
            )

            governance_fatigue_score = (
                self._clamp_score(
                    governance_fatigue_score
                    + 1.8
                )
            )

            adversarial_adaptation_score = (
                self._clamp_score(
                    adversarial_adaptation_score
                    + 2.4
                )
            )

            resource_saturation_score = (
                self._clamp_score(
                    resource_saturation_score
                    + 2.3
                )
            )

            systemic_risk_score = (
                self._clamp_score(
                    systemic_risk_score
                    + 2.1
                )
            )

            uncertainty_score = (
                self._clamp_score(
                    uncertainty_score
                    + 1.0
                )
            )

            mission_survivability_score = (
                self._clamp_score(
                    mission_survivability_score
                    - 1.8
                )
            )

            stabilization_capacity_score = (
                self._clamp_score(
                    stabilization_capacity_score
                    - 1.9
                )
            )

            operational_continuity_score = (
                self._clamp_score(
                    operational_continuity_score
                    - 1.7
                )
            )

            strategic_coordination_score = (
                self._clamp_score(
                    strategic_coordination_score
                    - 1.5
                )
            )

        return steps

    def _build_branches(
        self,
        *,
        war_state: str,
        stabilization_probability: float,
        doctrine_survivability_probability: (
            float
        ),
        mission_survivability_probability: (
            float
        ),
        systemic_risk_probability: float,
        war_risk_score: float,
    ) -> List[WarGameBranch]:

        return [
            WarGameBranch(
                branch_id=str(
                    uuid.uuid4()
                ),
                branch_name=(
                    "strategic_stabilization_path"
                ),
                projected_state=(
                    WAR_STATE_CONTESTED
                ),
                projected_outcome=(
                    WAR_OUTCOME_STABILIZED
                ),
                stabilization_probability=(
                    self
                    ._clamp_probability(
                        stabilization_probability
                        + 0.15
                    )
                ),
                doctrine_survivability_probability=(
                    self
                    ._clamp_probability(
                        doctrine_survivability_probability
                        + 0.15
                    )
                ),
                mission_survivability_probability=(
                    self
                    ._clamp_probability(
                        mission_survivability_probability
                        + 0.15
                    )
                ),
                systemic_risk_probability=(
                    self
                    ._clamp_probability(
                        systemic_risk_probability
                        - 0.20
                    )
                ),
                branch_score=(
                    self._clamp_score(
                        100.0
                        - war_risk_score
                        + 15.0
                    )
                ),
                rationale=(
                    "Projected "
                    "strategic "
                    "stabilization path."
                ),
            ),
            WarGameBranch(
                branch_id=str(
                    uuid.uuid4()
                ),
                branch_name=(
                    "strategic_collapse_path"
                ),
                projected_state=(
                    WAR_STATE_SYSTEMIC_RISK
                ),
                projected_outcome=(
                    WAR_OUTCOME_SYSTEMIC_RISK
                ),
                stabilization_probability=(
                    self
                    ._clamp_probability(
                        stabilization_probability
                        - 0.20
                    )
                ),
                doctrine_survivability_probability=(
                    self
                    ._clamp_probability(
                        doctrine_survivability_probability
                        - 0.20
                    )
                ),
                mission_survivability_probability=(
                    self
                    ._clamp_probability(
                        mission_survivability_probability
                        - 0.20
                    )
                ),
                systemic_risk_probability=(
                    self
                    ._clamp_probability(
                        systemic_risk_probability
                        + 0.25
                    )
                ),
                branch_score=(
                    self._clamp_score(
                        100.0
                        - war_risk_score
                        - 20.0
                    )
                ),
                rationale=(
                    "Projected "
                    "strategic "
                    "collapse path."
                ),
            ),
        ]

    # ==========================================================
    # PROBABILITIES
    # ==========================================================

    def _stabilization_probability(
        self,
        *,
        stabilization_capacity_score: float,
        operational_continuity_score: float,
        strategic_coordination_score: float,
        doctrine_pressure_score: float,
        resilience_exhaustion_score: float,
        operational_decay_score: float,
    ) -> float:

        score = (
            stabilization_capacity_score
            + operational_continuity_score
            + strategic_coordination_score
            + (
                100.0
                - doctrine_pressure_score
            )
            + (
                100.0
                - resilience_exhaustion_score
            )
            + (
                100.0
                - operational_decay_score
            )
        ) / 600.0

        return self._clamp_probability(
            score
        )

    def _doctrine_survivability_probability(
        self,
        *,
        doctrine_pressure_score: float,
        governance_fatigue_score: float,
        adversarial_adaptation_score: float,
        strategic_coordination_score: float,
    ) -> float:

        score = (
            (
                100.0
                - doctrine_pressure_score
            )
            + (
                100.0
                - governance_fatigue_score
            )
            + (
                100.0
                - adversarial_adaptation_score
            )
            + strategic_coordination_score
        ) / 400.0

        return self._clamp_probability(
            score
        )

    def _mission_survivability_probability(
        self,
        *,
        mission_survivability_score: float,
        operational_continuity_score: float,
        systemic_risk_score: float,
    ) -> float:

        score = (
            mission_survivability_score
            + operational_continuity_score
            + (
                100.0
                - systemic_risk_score
            )
        ) / 300.0

        return self._clamp_probability(
            score
        )

    def _systemic_risk_probability(
        self,
        *,
        resilience_exhaustion_score: float,
        operational_decay_score: float,
        governance_fatigue_score: float,
        adversarial_adaptation_score: float,
        resource_saturation_score: float,
        systemic_risk_score: float,
        uncertainty_score: float,
    ) -> float:

        risk = (
            resilience_exhaustion_score
            + operational_decay_score
            + governance_fatigue_score
            + adversarial_adaptation_score
            + resource_saturation_score
            + systemic_risk_score
            + uncertainty_score
        ) / 700.0

        return self._clamp_probability(
            risk
        )

    # ==========================================================
    # RISK
    # ==========================================================

    def _war_risk_score(
        self,
        *,
        doctrine_pressure_score: float,
        resilience_exhaustion_score: float,
        operational_decay_score: float,
        governance_fatigue_score: float,
        adversarial_adaptation_score: float,
        resource_saturation_score: float,
        systemic_risk_score: float,
        stabilization_probability: float,
        doctrine_survivability_probability: (
            float
        ),
        mission_survivability_probability: (
            float
        ),
        systemic_risk_probability: float,
    ) -> float:

        risk = (
            doctrine_pressure_score
            + resilience_exhaustion_score
            + operational_decay_score
            + governance_fatigue_score
            + adversarial_adaptation_score
            + resource_saturation_score
            + systemic_risk_score
            + (
                (
                    1.0
                    - stabilization_probability
                )
                * 100.0
            )
            + (
                (
                    1.0
                    - doctrine_survivability_probability
                )
                * 100.0
            )
            + (
                (
                    1.0
                    - mission_survivability_probability
                )
                * 100.0
            )
            + (
                systemic_risk_probability
                * 100.0
            )
        ) / 11.0

        return self._clamp_score(
            risk
        )

    # ==========================================================
    # STATES
    # ==========================================================

    @staticmethod
    def _war_state(
        *,
        war_risk_score: float,
        stabilization_probability: float,
        mission_survivability_probability: (
            float
        ),
        systemic_risk_probability: float,
    ) -> str:

        if systemic_risk_probability >= 0.8:
            return (
                WAR_STATE_SYSTEMIC_RISK
            )

        if (
            mission_survivability_probability
            <= 0.35
        ):
            return (
                WAR_STATE_MISSION_CRITICAL
            )

        if stabilization_probability <= 0.30:
            return (
                WAR_STATE_ESCALATED
            )

        if war_risk_score >= 75:
            return (
                WAR_STATE_RESOURCE_EXHAUSTION
            )

        if war_risk_score >= 50:
            return (
                WAR_STATE_CONTESTED
            )

        return WAR_STATE_STABLE

    @staticmethod
    def _projected_outcome(
        *,
        war_state: str,
        stabilization_probability: float,
        systemic_risk_probability: float,
    ) -> str:

        if (
            war_state
            == WAR_STATE_SYSTEMIC_RISK
        ):
            return (
                WAR_OUTCOME_SYSTEMIC_RISK
            )

        if stabilization_probability >= 0.75:
            return (
                WAR_OUTCOME_STABILIZED
            )

        if systemic_risk_probability >= 0.65:
            return (
                WAR_OUTCOME_ESCALATED
            )

        return (
            WAR_OUTCOME_CONTESTED
        )

    # ==========================================================
    # RECOMMENDATIONS
    # ==========================================================

    @staticmethod
    def _recommendation(
        *,
        war_state: str,
        doctrine_pressure_score: float,
        resource_saturation_score: float,
        mission_survivability_score: float,
    ) -> str:

        if (
            war_state
            == WAR_STATE_SYSTEMIC_RISK
        ):
            return (
                RECOMMENDATION_GOVERNANCE_INTERVENTION
            )

        if doctrine_pressure_score >= 70:
            return (
                RECOMMENDATION_DOCTRINE_REALIGNMENT
            )

        if resource_saturation_score >= 70:
            return (
                RECOMMENDATION_RESILIENCE_REBALANCING
            )

        if mission_survivability_score <= 45:
            return (
                RECOMMENDATION_MISSION_PRESERVATION
            )

        if war_state in {
            WAR_STATE_ESCALATED,
            WAR_STATE_RESOURCE_EXHAUSTION,
        }:
            return (
                RECOMMENDATION_STRATEGIC_ESCALATION
            )

        return RECOMMENDATION_MONITOR

    @staticmethod
    def _recommended_controls(
        *,
        war_state: str,
        recommendation: str,
    ) -> List[str]:

        controls = [
            "war_game_lineage_recording",
            "war_game_evidence_recording",
        ]

        if war_state != WAR_STATE_STABLE:
            controls.append(
                "war_game_review"
            )

        if recommendation in {
            RECOMMENDATION_GOVERNANCE_INTERVENTION,
            RECOMMENDATION_STRATEGIC_ESCALATION,
        }:
            controls.append(
                "governance_review"
            )

        return list(
            dict.fromkeys(controls)
        )

    @staticmethod
    def _recommended_actions(
        *,
        war_state: str,
        recommendation: str,
    ) -> List[Dict[str, Any]]:

        return [
            {
                "action": (
                    "record_war_game_lineage"
                )
            },
            {
                "action": (
                    "record_war_game_evidence"
                )
            },
            {
                "action": (
                    "review_war_state"
                ),
                "war_state": war_state,
            },
            {
                "action": (
                    "review_recommendation"
                ),
                "recommendation": (
                    recommendation
                ),
            },
        ]

    # ==========================================================
    # RATIONALE
    # ==========================================================

    @staticmethod
    def _build_rationale(
        *,
        war_state: str,
        projected_outcome: str,
        recommendation: str,
        war_risk_score: float,
        stabilization_probability: float,
        doctrine_survivability_probability: (
            float
        ),
        mission_survivability_probability: (
            float
        ),
        systemic_risk_probability: float,
        signal_count: int,
        war_game_depth: int,
    ) -> str:

        return (
            f"Sovereign operational "
            f"war-game evaluation "
            f"processed "
            f"{signal_count} signal(s) "
            f"across war-game depth "
            f"{war_game_depth}. "
            f"War state {war_state}; "
            f"projected outcome "
            f"{projected_outcome}; "
            f"recommendation "
            f"{recommendation}. "
            f"War risk "
            f"{war_risk_score:.2f}; "
            f"stabilization probability "
            f"{stabilization_probability:.2f}; "
            f"doctrine survivability "
            f"{doctrine_survivability_probability:.2f}; "
            f"mission survivability "
            f"{mission_survivability_probability:.2f}; "
            f"systemic risk probability "
            f"{systemic_risk_probability:.2f}."
        )

    # ==========================================================
    # RECORDING
    # ==========================================================

    def _record_assessment(
        self,
        assessment: (
            SovereignWarGameAssessment
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
            SovereignWarGameAssessment
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
                "SOVEREIGN_WAR_GAME_ASSESSMENT"
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
                f"⚠️ War-game memory write failed: {exc}"
            )

    def _write_to_lineage(
        self,
        assessment: (
            SovereignWarGameAssessment
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
                "SOVEREIGN_WAR_GAME"
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
                f"⚠️ War-game lineage write failed: {exc}"
            )

    def _write_to_evidence(
        self,
        assessment: (
            SovereignWarGameAssessment
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
                "SOVEREIGN_WAR_GAME"
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
                f"⚠️ War-game evidence write failed: {exc}"
            )

    def _emit_event(
        self,
        assessment: (
            SovereignWarGameAssessment
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
                "SOVEREIGN_WAR_GAME_ASSESSMENT"
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
                        "SOVEREIGN_WAR_GAME_ASSESSMENT"
                    ),
                    payload,
                )

        except Exception as exc:
            print(
                f"⚠️ War-game event emit failed: {exc}"
            )

    # ==========================================================
    # NORMALIZATION
    # ==========================================================

    def _normalize_signal(
        self,
        item: (
            WarGameSignal
            | Dict[str, Any]
        ),
        *,
        mission_id: Optional[str],
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> WarGameSignal:

        if isinstance(
            item,
            WarGameSignal,
        ):
            return item

        return WarGameSignal(
            war_signal_id=str(
                item.get(
                    "war_signal_id"
                )
                or uuid.uuid4()
            ),
            doctrine=self._safe_doctrine(
                item.get("doctrine")
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
            doctrine_pressure_score=(
                self._clamp_score(
                    item.get(
                        "doctrine_pressure_score",
                        0.0,
                    )
                )
            ),
            resilience_exhaustion_score=(
                self._clamp_score(
                    item.get(
                        "resilience_exhaustion_score",
                        0.0,
                    )
                )
            ),
            operational_decay_score=(
                self._clamp_score(
                    item.get(
                        "operational_decay_score",
                        0.0,
                    )
                )
            ),
            governance_fatigue_score=(
                self._clamp_score(
                    item.get(
                        "governance_fatigue_score",
                        0.0,
                    )
                )
            ),
            adversarial_adaptation_score=(
                self._clamp_score(
                    item.get(
                        "adversarial_adaptation_score",
                        0.0,
                    )
                )
            ),
            resource_saturation_score=(
                self._clamp_score(
                    item.get(
                        "resource_saturation_score",
                        0.0,
                    )
                )
            ),
            mission_survivability_score=(
                self._clamp_score(
                    item.get(
                        "mission_survivability_score",
                        100.0,
                    )
                )
            ),
            stabilization_capacity_score=(
                self._clamp_score(
                    item.get(
                        "stabilization_capacity_score",
                        100.0,
                    )
                )
            ),
            operational_continuity_score=(
                self._clamp_score(
                    item.get(
                        "operational_continuity_score",
                        100.0,
                    )
                )
            ),
            strategic_coordination_score=(
                self._clamp_score(
                    item.get(
                        "strategic_coordination_score",
                        100.0,
                    )
                )
            ),
            systemic_risk_score=(
                self._clamp_score(
                    item.get(
                        "systemic_risk_score",
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
    ) -> SovereignWarGameAssessment:

        return (
            SovereignWarGameAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                war_state=WAR_STATE_STABLE,
                projected_outcome=(
                    WAR_OUTCOME_STABILIZED
                ),
                recommendation=(
                    RECOMMENDATION_MONITOR
                ),
                doctrine_pressure_score=0.0,
                resilience_exhaustion_score=0.0,
                operational_decay_score=0.0,
                governance_fatigue_score=0.0,
                adversarial_adaptation_score=0.0,
                resource_saturation_score=0.0,
                mission_survivability_score=100.0,
                stabilization_capacity_score=100.0,
                operational_continuity_score=100.0,
                strategic_coordination_score=100.0,
                systemic_risk_score=0.0,
                uncertainty_score=0.0,
                stabilization_probability=1.0,
                doctrine_survivability_probability=1.0,
                mission_survivability_probability=1.0,
                systemic_risk_probability=0.0,
                war_risk_score=0.0,
                explainability_score=100.0,
                war_confidence=1.0,
                selected_signal_id=None,
                selected_doctrine=None,
                severity=(
                    WarGameSeverity
                    .INFO.value
                ),
                confidence=1.0,
                war_game_depth=0,
                mission_id=mission_id,
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=(
                    correlation_id
                ),
                simulation_steps=[],
                recommended_controls=[
                    (
                        "war_game_lineage_recording"
                    )
                ],
                recommended_actions=[
                    {
                        "action": (
                            "continue_war_game_monitoring"
                        )
                    }
                ],
                rationale=(
                    "No war-game "
                    "signals submitted."
                ),
                metadata={},
            )
        )

    def _select_primary_signal(
        self,
        signals: Sequence[
            WarGameSignal
        ],
    ) -> WarGameSignal:

        return sorted(
            signals,
            key=lambda item: (
                item
                .doctrine_pressure_score,
                item
                .systemic_risk_score,
                item
                .resource_saturation_score,
                -item.created_at_ms,
            ),
            reverse=True,
        )[0]

    # ==========================================================
    # HELPERS
    # ==========================================================

    def _war_confidence(
        self,
        signals: Sequence[
            WarGameSignal
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
            WarGameSignal
        ],
    ) -> float:

        if not signals:
            return 0.0

        explained = 0

        for s in signals:

            if s.summary:
                explained += 1

            if s.source_engine:
                explained += 1

            if s.doctrine:
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

    @staticmethod
    def _safe_doctrine(
        value: Any,
    ) -> str:

        value = str(
            value
            or WarDoctrine
            .UNKNOWN.value
        ).upper()

        valid = {
            item.value
            for item in WarDoctrine
        }

        return (
            value
            if value in valid
            else WarDoctrine
            .UNKNOWN.value
        )

    @staticmethod
    def _safe_severity(
        value: Any,
    ) -> str:

        value = str(
            value
            or WarGameSeverity
            .INFO.value
        ).upper()

        valid = {
            item.value
            for item in WarGameSeverity
        }

        return (
            value
            if value in valid
            else WarGameSeverity
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


def build_sovereign_operational_war_gaming_engine(
    *,
    event_bus: Optional[Any] = None,
    battle_management_engine: Optional[
        Any
    ] = None,
    campaign_engine: Optional[Any] = None,
    runtime_evolution_engine: Optional[
        Any
    ] = None,
    operational_memory_engine: Optional[
        Any
    ] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[
        Any
    ] = None,
) -> SovereignOperationalWarGamingEngine:

    return (
        SovereignOperationalWarGamingEngine(
            event_bus=event_bus,
            battle_management_engine=(
                battle_management_engine
            ),
            campaign_engine=campaign_engine,
            runtime_evolution_engine=(
                runtime_evolution_engine
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