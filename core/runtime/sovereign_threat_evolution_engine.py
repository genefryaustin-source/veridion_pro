"""
core/runtime/sovereign_threat_evolution_engine.py

Sovereign Threat Evolution Engine

Autonomous adversarial evolution cognition layer.

This subsystem models:
- adversarial mutation trajectories
- operational threat evolution
- attack doctrine adaptation
- persistence evolution
- containment bypass evolution
- adversarial learning acceleration
- propagation mutation
- strategic escalation evolution

IMPORTANT:
This subsystem DOES NOT:
- generate malware
- generate exploits
- execute attacks
- mutate real infrastructure
- provide offensive cyber capability

It ONLY:
- models adversarial evolution
- forecasts mutation trajectories
- evaluates adaptive threat pressure
- simulates adversarial operational futures
- records replayable evolution lineage/evidence
"""

from __future__ import annotations

import statistics
import time
import uuid

from dataclasses import (
    asdict,
    dataclass,
    field,
)

from enum import Enum

from typing import (
    Any,
    Dict,
    List,
    Optional,
    Sequence,
)


DEFAULT_ENGINE_NAME = (
    "sovereign_threat_evolution_engine"
)

DEFAULT_EVOLUTION_DEPTH = 12


EVOLUTION_STATE_STABLE = "STABLE"
EVOLUTION_STATE_ADAPTIVE = "ADAPTIVE"
EVOLUTION_STATE_ESCALATING = (
    "ESCALATING"
)
EVOLUTION_STATE_MUTATING = (
    "MUTATING"
)
EVOLUTION_STATE_STRATEGIC_RISK = (
    "STRATEGIC_RISK"
)

EVOLUTION_OUTCOME_CONTAINED = (
    "CONTAINED"
)
EVOLUTION_OUTCOME_ADAPTIVE = (
    "ADAPTIVE"
)
EVOLUTION_OUTCOME_ESCALATED = (
    "ESCALATED"
)
EVOLUTION_OUTCOME_MUTATED = (
    "MUTATED"
)
EVOLUTION_OUTCOME_SYSTEMIC_RISK = (
    "SYSTEMIC_RISK"
)

RECOMMENDATION_MONITOR = "MONITOR"
RECOMMENDATION_COUNTER_ADAPTATION = (
    "COUNTER_ADAPTATION"
)
RECOMMENDATION_RESILIENCE_REINFORCEMENT = (
    "RESILIENCE_REINFORCEMENT"
)
RECOMMENDATION_ESCALATION_REVIEW = (
    "ESCALATION_REVIEW"
)
RECOMMENDATION_DOCTRINE_REALIGNMENT = (
    "DOCTRINE_REALIGNMENT"
)
RECOMMENDATION_MUTATION_CONTAINMENT = (
    "MUTATION_CONTAINMENT"
)


class ThreatSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ThreatDomain(str, Enum):
    ENDPOINT = "ENDPOINT"
    IDENTITY = "IDENTITY"
    CLOUD = "CLOUD"
    EMAIL = "EMAIL"
    NETWORK = "NETWORK"
    DATA = "DATA"
    GOVERNANCE = "GOVERNANCE"
    MISSION = "MISSION"
    GLOBAL = "GLOBAL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ThreatMutationNode:
    mutation_id: str

    mutation_name: str
    domain: str

    mutation_pressure_score: float
    adaptation_velocity_score: float
    stealth_evolution_score: float
    persistence_evolution_score: float

    active: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class ThreatEvolutionSignal:
    evolution_signal_id: str

    source_engine: str
    severity: str
    confidence: float

    summary: str

    mission_id: Optional[str] = None
    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    mutation_pressure_score: float = (
        0.0
    )

    adaptation_velocity_score: float = (
        0.0
    )

    containment_bypass_score: float = (
        0.0
    )

    persistence_evolution_score: float = (
        0.0
    )

    propagation_mutation_score: float = (
        0.0
    )

    adversarial_learning_score: float = (
        0.0
    )

    operational_escalation_score: float = (
        0.0
    )

    doctrine_sophistication_score: float = (
        0.0
    )

    survivability_evolution_score: float = (
        0.0
    )

    stealth_adaptation_score: float = (
        0.0
    )

    governance_exploitation_score: float = (
        0.0
    )

    strategic_risk_score: float = 0.0

    uncertainty_score: float = 0.0

    mutation_nodes: List[
        ThreatMutationNode
    ] = field(default_factory=list)

    payload: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


@dataclass(frozen=True)
class ThreatEvolutionBranch:
    branch_id: str

    branch_name: str

    projected_state: str
    projected_outcome: str

    containment_probability: float
    mutation_probability: float
    escalation_probability: float
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
class ThreatEvolutionSimulationStep:
    step_id: str

    step_index: int

    projected_state: str
    projected_outcome: str

    mutation_pressure_score: float
    adaptation_velocity_score: float
    containment_bypass_score: float
    persistence_evolution_score: float
    propagation_mutation_score: float
    adversarial_learning_score: float
    operational_escalation_score: float
    doctrine_sophistication_score: float
    survivability_evolution_score: float
    stealth_adaptation_score: float
    governance_exploitation_score: float
    strategic_risk_score: float
    uncertainty_score: float

    containment_probability: float
    mutation_probability: float
    escalation_probability: float
    systemic_risk_probability: float

    evolution_risk_score: float

    branches: List[
        ThreatEvolutionBranch
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
class SovereignThreatEvolutionAssessment:
    assessment_id: str

    evolution_state: str
    projected_outcome: str
    recommendation: str

    mutation_pressure_score: float
    adaptation_velocity_score: float
    containment_bypass_score: float
    persistence_evolution_score: float
    propagation_mutation_score: float
    adversarial_learning_score: float
    operational_escalation_score: float
    doctrine_sophistication_score: float
    survivability_evolution_score: float
    stealth_adaptation_score: float
    governance_exploitation_score: float
    strategic_risk_score: float
    uncertainty_score: float

    containment_probability: float
    mutation_probability: float
    escalation_probability: float
    systemic_risk_probability: float

    evolution_risk_score: float

    explainability_score: float
    evolution_confidence: float

    selected_signal_id: Optional[str]

    severity: str
    confidence: float

    evolution_depth: int

    mission_id: Optional[str]
    tenant_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    simulation_steps: List[
        ThreatEvolutionSimulationStep
    ]

    mutation_topology: Dict[str, Any]

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


class SovereignThreatEvolutionEngine:
    """
    Sovereign adversarial evolution cognition.
    """

    def __init__(
        self,
        *,
        engine_name: str = (
            DEFAULT_ENGINE_NAME
        ),
        event_bus: Optional[Any] = None,
        war_gaming_engine: Optional[Any] = None,
        resilience_mesh: Optional[Any] = None,
        battle_management_engine: Optional[
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

        self.war_gaming_engine = (
            war_gaming_engine
        )

        self.resilience_mesh = (
            resilience_mesh
        )

        self.battle_management_engine = (
            battle_management_engine
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
            SovereignThreatEvolutionAssessment
        ] = []

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def evaluate(
        self,
        signals: Sequence[
            ThreatEvolutionSignal
            | Dict[str, Any]
        ],
        *,
        evolution_depth: int = (
            DEFAULT_EVOLUTION_DEPTH
        ),
        mission_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> SovereignThreatEvolutionAssessment:

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

        mutation_pressure = (
            self._avg_score(
                [
                    s
                    .mutation_pressure_score
                    for s in normalized
                ]
            )
        )

        adaptation_velocity = (
            self._avg_score(
                [
                    s
                    .adaptation_velocity_score
                    for s in normalized
                ]
            )
        )

        containment_bypass = (
            self._avg_score(
                [
                    s
                    .containment_bypass_score
                    for s in normalized
                ]
            )
        )

        persistence_evolution = (
            self._avg_score(
                [
                    s
                    .persistence_evolution_score
                    for s in normalized
                ]
            )
        )

        propagation_mutation = (
            self._avg_score(
                [
                    s
                    .propagation_mutation_score
                    for s in normalized
                ]
            )
        )

        adversarial_learning = (
            self._avg_score(
                [
                    s
                    .adversarial_learning_score
                    for s in normalized
                ]
            )
        )

        operational_escalation = (
            self._avg_score(
                [
                    s
                    .operational_escalation_score
                    for s in normalized
                ]
            )
        )

        doctrine_sophistication = (
            self._avg_score(
                [
                    s
                    .doctrine_sophistication_score
                    for s in normalized
                ]
            )
        )

        survivability_evolution = (
            self._avg_score(
                [
                    s
                    .survivability_evolution_score
                    for s in normalized
                ]
            )
        )

        stealth_adaptation = (
            self._avg_score(
                [
                    s
                    .stealth_adaptation_score
                    for s in normalized
                ]
            )
        )

        governance_exploitation = (
            self._avg_score(
                [
                    s
                    .governance_exploitation_score
                    for s in normalized
                ]
            )
        )

        strategic_risk = (
            self._avg_score(
                [
                    s
                    .strategic_risk_score
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

        containment_probability = (
            self
            ._containment_probability(
                mutation_pressure_score=(
                    mutation_pressure
                ),
                containment_bypass_score=(
                    containment_bypass
                ),
                operational_escalation_score=(
                    operational_escalation
                ),
                strategic_risk_score=(
                    strategic_risk
                ),
            )
        )

        mutation_probability = (
            self._mutation_probability(
                adaptation_velocity_score=(
                    adaptation_velocity
                ),
                persistence_evolution_score=(
                    persistence_evolution
                ),
                propagation_mutation_score=(
                    propagation_mutation
                ),
                adversarial_learning_score=(
                    adversarial_learning
                ),
                survivability_evolution_score=(
                    survivability_evolution
                ),
            )
        )

        escalation_probability = (
            self
            ._escalation_probability(
                operational_escalation_score=(
                    operational_escalation
                ),
                doctrine_sophistication_score=(
                    doctrine_sophistication
                ),
                governance_exploitation_score=(
                    governance_exploitation
                ),
                strategic_risk_score=(
                    strategic_risk
                ),
            )
        )

        systemic_risk_probability = (
            self
            ._systemic_risk_probability(
                mutation_pressure_score=(
                    mutation_pressure
                ),
                containment_bypass_score=(
                    containment_bypass
                ),
                operational_escalation_score=(
                    operational_escalation
                ),
                governance_exploitation_score=(
                    governance_exploitation
                ),
                strategic_risk_score=(
                    strategic_risk
                ),
                uncertainty_score=(
                    uncertainty
                ),
            )
        )

        evolution_risk = (
            self._evolution_risk_score(
                mutation_pressure_score=(
                    mutation_pressure
                ),
                containment_bypass_score=(
                    containment_bypass
                ),
                operational_escalation_score=(
                    operational_escalation
                ),
                strategic_risk_score=(
                    strategic_risk
                ),
                containment_probability=(
                    containment_probability
                ),
                mutation_probability=(
                    mutation_probability
                ),
                escalation_probability=(
                    escalation_probability
                ),
                systemic_risk_probability=(
                    systemic_risk_probability
                ),
            )
        )

        evolution_state = (
            self._evolution_state(
                evolution_risk_score=(
                    evolution_risk
                ),
                mutation_probability=(
                    mutation_probability
                ),
                escalation_probability=(
                    escalation_probability
                ),
                systemic_risk_probability=(
                    systemic_risk_probability
                ),
            )
        )

        projected_outcome = (
            self._projected_outcome(
                evolution_state=(
                    evolution_state
                ),
                containment_probability=(
                    containment_probability
                ),
                systemic_risk_probability=(
                    systemic_risk_probability
                ),
            )
        )

        recommendation = (
            self._recommendation(
                evolution_state=(
                    evolution_state
                ),
                mutation_pressure_score=(
                    mutation_pressure
                ),
                containment_bypass_score=(
                    containment_bypass
                ),
                operational_escalation_score=(
                    operational_escalation
                ),
            )
        )

        topology = (
            self._build_topology(
                normalized
            )
        )

        steps = (
            self._build_evolution_steps(
                mutation_pressure_score=(
                    mutation_pressure
                ),
                adaptation_velocity_score=(
                    adaptation_velocity
                ),
                containment_bypass_score=(
                    containment_bypass
                ),
                persistence_evolution_score=(
                    persistence_evolution
                ),
                propagation_mutation_score=(
                    propagation_mutation
                ),
                adversarial_learning_score=(
                    adversarial_learning
                ),
                operational_escalation_score=(
                    operational_escalation
                ),
                doctrine_sophistication_score=(
                    doctrine_sophistication
                ),
                survivability_evolution_score=(
                    survivability_evolution
                ),
                stealth_adaptation_score=(
                    stealth_adaptation
                ),
                governance_exploitation_score=(
                    governance_exploitation
                ),
                strategic_risk_score=(
                    strategic_risk
                ),
                uncertainty_score=(
                    uncertainty
                ),
                evolution_depth=(
                    evolution_depth
                ),
            )
        )

        assessment = (
            SovereignThreatEvolutionAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                evolution_state=(
                    evolution_state
                ),
                projected_outcome=(
                    projected_outcome
                ),
                recommendation=(
                    recommendation
                ),
                mutation_pressure_score=(
                    mutation_pressure
                ),
                adaptation_velocity_score=(
                    adaptation_velocity
                ),
                containment_bypass_score=(
                    containment_bypass
                ),
                persistence_evolution_score=(
                    persistence_evolution
                ),
                propagation_mutation_score=(
                    propagation_mutation
                ),
                adversarial_learning_score=(
                    adversarial_learning
                ),
                operational_escalation_score=(
                    operational_escalation
                ),
                doctrine_sophistication_score=(
                    doctrine_sophistication
                ),
                survivability_evolution_score=(
                    survivability_evolution
                ),
                stealth_adaptation_score=(
                    stealth_adaptation
                ),
                governance_exploitation_score=(
                    governance_exploitation
                ),
                strategic_risk_score=(
                    strategic_risk
                ),
                uncertainty_score=(
                    uncertainty
                ),
                containment_probability=(
                    containment_probability
                ),
                mutation_probability=(
                    mutation_probability
                ),
                escalation_probability=(
                    escalation_probability
                ),
                systemic_risk_probability=(
                    systemic_risk_probability
                ),
                evolution_risk_score=(
                    evolution_risk
                ),
                explainability_score=(
                    self
                    ._explainability_score(
                        normalized
                    )
                ),
                evolution_confidence=(
                    self
                    ._evolution_confidence(
                        normalized
                    )
                ),
                selected_signal_id=(
                    selected
                    .evolution_signal_id
                ),
                severity=(
                    selected.severity
                ),
                confidence=(
                    selected.confidence
                ),
                evolution_depth=(
                    evolution_depth
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
                mutation_topology=(
                    topology
                ),
                recommended_controls=(
                    self
                    ._recommended_controls(
                        evolution_state=(
                            evolution_state
                        ),
                        recommendation=(
                            recommendation
                        ),
                    )
                ),
                recommended_actions=(
                    self
                    ._recommended_actions(
                        evolution_state=(
                            evolution_state
                        ),
                        recommendation=(
                            recommendation
                        ),
                    )
                ),
                rationale=(
                    self._build_rationale(
                        evolution_state=(
                            evolution_state
                        ),
                        projected_outcome=(
                            projected_outcome
                        ),
                        recommendation=(
                            recommendation
                        ),
                        evolution_risk_score=(
                            evolution_risk
                        ),
                        containment_probability=(
                            containment_probability
                        ),
                        mutation_probability=(
                            mutation_probability
                        ),
                        escalation_probability=(
                            escalation_probability
                        ),
                        systemic_risk_probability=(
                            systemic_risk_probability
                        ),
                        signal_count=len(
                            normalized
                        ),
                        evolution_depth=(
                            evolution_depth
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
    # TOPOLOGY
    # ==========================================================

    def _build_topology(
        self,
        signals: Sequence[
            ThreatEvolutionSignal
        ],
    ) -> Dict[str, Any]:

        nodes = []

        for signal in signals:
            for node in (
                signal.mutation_nodes
                or []
            ):
                nodes.append(
                    {
                        "mutation_id": (
                            node.mutation_id
                        ),
                        "mutation_name": (
                            node.mutation_name
                        ),
                        "domain": (
                            node.domain
                        ),
                        "mutation_pressure_score": (
                            node
                            .mutation_pressure_score
                        ),
                        "adaptation_velocity_score": (
                            node
                            .adaptation_velocity_score
                        ),
                        "stealth_evolution_score": (
                            node
                            .stealth_evolution_score
                        ),
                        "persistence_evolution_score": (
                            node
                            .persistence_evolution_score
                        ),
                        "active": (
                            node.active
                        ),
                    }
                )

        return {
            "node_count": len(nodes),
            "mutation_nodes": nodes,
            "topology_state": (
                "ACTIVE"
                if nodes
                else "EMPTY"
            ),
        }

    # ==========================================================
    # SIMULATION
    # ==========================================================

    def _build_evolution_steps(
        self,
        *,
        mutation_pressure_score: float,
        adaptation_velocity_score: float,
        containment_bypass_score: float,
        persistence_evolution_score: float,
        propagation_mutation_score: float,
        adversarial_learning_score: float,
        operational_escalation_score: float,
        doctrine_sophistication_score: float,
        survivability_evolution_score: float,
        stealth_adaptation_score: float,
        governance_exploitation_score: float,
        strategic_risk_score: float,
        uncertainty_score: float,
        evolution_depth: int,
    ) -> List[
        ThreatEvolutionSimulationStep
    ]:

        steps: List[
            ThreatEvolutionSimulationStep
        ] = []

        for idx in range(
            max(1, int(evolution_depth))
        ):

            containment_probability = (
                self
                ._containment_probability(
                    mutation_pressure_score=(
                        mutation_pressure_score
                    ),
                    containment_bypass_score=(
                        containment_bypass_score
                    ),
                    operational_escalation_score=(
                        operational_escalation_score
                    ),
                    strategic_risk_score=(
                        strategic_risk_score
                    ),
                )
            )

            mutation_probability = (
                self
                ._mutation_probability(
                    adaptation_velocity_score=(
                        adaptation_velocity_score
                    ),
                    persistence_evolution_score=(
                        persistence_evolution_score
                    ),
                    propagation_mutation_score=(
                        propagation_mutation_score
                    ),
                    adversarial_learning_score=(
                        adversarial_learning_score
                    ),
                    survivability_evolution_score=(
                        survivability_evolution_score
                    ),
                )
            )

            escalation_probability = (
                self
                ._escalation_probability(
                    operational_escalation_score=(
                        operational_escalation_score
                    ),
                    doctrine_sophistication_score=(
                        doctrine_sophistication_score
                    ),
                    governance_exploitation_score=(
                        governance_exploitation_score
                    ),
                    strategic_risk_score=(
                        strategic_risk_score
                    ),
                )
            )

            systemic_risk_probability = (
                self
                ._systemic_risk_probability(
                    mutation_pressure_score=(
                        mutation_pressure_score
                    ),
                    containment_bypass_score=(
                        containment_bypass_score
                    ),
                    operational_escalation_score=(
                        operational_escalation_score
                    ),
                    governance_exploitation_score=(
                        governance_exploitation_score
                    ),
                    strategic_risk_score=(
                        strategic_risk_score
                    ),
                    uncertainty_score=(
                        uncertainty_score
                    ),
                )
            )

            evolution_risk = (
                self._evolution_risk_score(
                    mutation_pressure_score=(
                        mutation_pressure_score
                    ),
                    containment_bypass_score=(
                        containment_bypass_score
                    ),
                    operational_escalation_score=(
                        operational_escalation_score
                    ),
                    strategic_risk_score=(
                        strategic_risk_score
                    ),
                    containment_probability=(
                        containment_probability
                    ),
                    mutation_probability=(
                        mutation_probability
                    ),
                    escalation_probability=(
                        escalation_probability
                    ),
                    systemic_risk_probability=(
                        systemic_risk_probability
                    ),
                )
            )

            state = (
                self._evolution_state(
                    evolution_risk_score=(
                        evolution_risk
                    ),
                    mutation_probability=(
                        mutation_probability
                    ),
                    escalation_probability=(
                        escalation_probability
                    ),
                    systemic_risk_probability=(
                        systemic_risk_probability
                    ),
                )
            )

            outcome = (
                self._projected_outcome(
                    evolution_state=state,
                    containment_probability=(
                        containment_probability
                    ),
                    systemic_risk_probability=(
                        systemic_risk_probability
                    ),
                )
            )

            branches = (
                self._build_branches(
                    evolution_state=state,
                    containment_probability=(
                        containment_probability
                    ),
                    mutation_probability=(
                        mutation_probability
                    ),
                    escalation_probability=(
                        escalation_probability
                    ),
                    systemic_risk_probability=(
                        systemic_risk_probability
                    ),
                    evolution_risk_score=(
                        evolution_risk
                    ),
                )
            )

            steps.append(
                ThreatEvolutionSimulationStep(
                    step_id=str(
                        uuid.uuid4()
                    ),
                    step_index=idx,
                    projected_state=state,
                    projected_outcome=(
                        outcome
                    ),
                    mutation_pressure_score=(
                        mutation_pressure_score
                    ),
                    adaptation_velocity_score=(
                        adaptation_velocity_score
                    ),
                    containment_bypass_score=(
                        containment_bypass_score
                    ),
                    persistence_evolution_score=(
                        persistence_evolution_score
                    ),
                    propagation_mutation_score=(
                        propagation_mutation_score
                    ),
                    adversarial_learning_score=(
                        adversarial_learning_score
                    ),
                    operational_escalation_score=(
                        operational_escalation_score
                    ),
                    doctrine_sophistication_score=(
                        doctrine_sophistication_score
                    ),
                    survivability_evolution_score=(
                        survivability_evolution_score
                    ),
                    stealth_adaptation_score=(
                        stealth_adaptation_score
                    ),
                    governance_exploitation_score=(
                        governance_exploitation_score
                    ),
                    strategic_risk_score=(
                        strategic_risk_score
                    ),
                    uncertainty_score=(
                        uncertainty_score
                    ),
                    containment_probability=(
                        containment_probability
                    ),
                    mutation_probability=(
                        mutation_probability
                    ),
                    escalation_probability=(
                        escalation_probability
                    ),
                    systemic_risk_probability=(
                        systemic_risk_probability
                    ),
                    evolution_risk_score=(
                        evolution_risk
                    ),
                    branches=branches,
                    rationale=(
                        f"Threat evolution "
                        f"simulation step "
                        f"{idx} projected "
                        f"{state}."
                    ),
                )
            )

            mutation_pressure_score = (
                self._clamp_score(
                    mutation_pressure_score
                    + 2.3
                )
            )

            adaptation_velocity_score = (
                self._clamp_score(
                    adaptation_velocity_score
                    + 2.1
                )
            )

            containment_bypass_score = (
                self._clamp_score(
                    containment_bypass_score
                    + 2.2
                )
            )

            persistence_evolution_score = (
                self._clamp_score(
                    persistence_evolution_score
                    + 2.0
                )
            )

            propagation_mutation_score = (
                self._clamp_score(
                    propagation_mutation_score
                    + 2.1
                )
            )

            adversarial_learning_score = (
                self._clamp_score(
                    adversarial_learning_score
                    + 2.4
                )
            )

            operational_escalation_score = (
                self._clamp_score(
                    operational_escalation_score
                    + 2.2
                )
            )

            doctrine_sophistication_score = (
                self._clamp_score(
                    doctrine_sophistication_score
                    + 2.0
                )
            )

            survivability_evolution_score = (
                self._clamp_score(
                    survivability_evolution_score
                    + 1.9
                )
            )

            stealth_adaptation_score = (
                self._clamp_score(
                    stealth_adaptation_score
                    + 2.0
                )
            )

            governance_exploitation_score = (
                self._clamp_score(
                    governance_exploitation_score
                    + 1.8
                )
            )

            strategic_risk_score = (
                self._clamp_score(
                    strategic_risk_score
                    + 2.3
                )
            )

            uncertainty_score = (
                self._clamp_score(
                    uncertainty_score
                    + 1.0
                )
            )

        return steps

    def _build_branches(
        self,
        *,
        evolution_state: str,
        containment_probability: float,
        mutation_probability: float,
        escalation_probability: float,
        systemic_risk_probability: float,
        evolution_risk_score: float,
    ) -> List[ThreatEvolutionBranch]:

        return [
            ThreatEvolutionBranch(
                branch_id=str(
                    uuid.uuid4()
                ),
                branch_name=(
                    "counter_adaptation_path"
                ),
                projected_state=(
                    EVOLUTION_STATE_ADAPTIVE
                ),
                projected_outcome=(
                    EVOLUTION_OUTCOME_CONTAINED
                ),
                containment_probability=(
                    self
                    ._clamp_probability(
                        containment_probability
                        + 0.15
                    )
                ),
                mutation_probability=(
                    self
                    ._clamp_probability(
                        mutation_probability
                        - 0.10
                    )
                ),
                escalation_probability=(
                    self
                    ._clamp_probability(
                        escalation_probability
                        - 0.10
                    )
                ),
                systemic_risk_probability=(
                    self
                    ._clamp_probability(
                        systemic_risk_probability
                        - 0.15
                    )
                ),
                branch_score=(
                    self._clamp_score(
                        100.0
                        - evolution_risk_score
                        + 15.0
                    )
                ),
                rationale=(
                    "Projected "
                    "counter-adaptation path."
                ),
            ),
            ThreatEvolutionBranch(
                branch_id=str(
                    uuid.uuid4()
                ),
                branch_name=(
                    "mutation_escalation_path"
                ),
                projected_state=(
                    EVOLUTION_STATE_MUTATING
                ),
                projected_outcome=(
                    EVOLUTION_OUTCOME_ESCALATED
                ),
                containment_probability=(
                    self
                    ._clamp_probability(
                        containment_probability
                        - 0.20
                    )
                ),
                mutation_probability=(
                    self
                    ._clamp_probability(
                        mutation_probability
                        + 0.20
                    )
                ),
                escalation_probability=(
                    self
                    ._clamp_probability(
                        escalation_probability
                        + 0.20
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
                        - evolution_risk_score
                        - 20.0
                    )
                ),
                rationale=(
                    "Projected "
                    "mutation escalation path."
                ),
            ),
        ]

    # ==========================================================
    # PROBABILITIES
    # ==========================================================

    def _containment_probability(
        self,
        *,
        mutation_pressure_score: float,
        containment_bypass_score: float,
        operational_escalation_score: float,
        strategic_risk_score: float,
    ) -> float:

        score = (
            (
                100.0
                - mutation_pressure_score
            )
            + (
                100.0
                - containment_bypass_score
            )
            + (
                100.0
                - operational_escalation_score
            )
            + (
                100.0
                - strategic_risk_score
            )
        ) / 400.0

        return self._clamp_probability(
            score
        )

    def _mutation_probability(
        self,
        *,
        adaptation_velocity_score: float,
        persistence_evolution_score: float,
        propagation_mutation_score: float,
        adversarial_learning_score: float,
        survivability_evolution_score: float,
    ) -> float:

        score = (
            adaptation_velocity_score
            + persistence_evolution_score
            + propagation_mutation_score
            + adversarial_learning_score
            + survivability_evolution_score
        ) / 500.0

        return self._clamp_probability(
            score
        )

    def _escalation_probability(
        self,
        *,
        operational_escalation_score: float,
        doctrine_sophistication_score: float,
        governance_exploitation_score: float,
        strategic_risk_score: float,
    ) -> float:

        score = (
            operational_escalation_score
            + doctrine_sophistication_score
            + governance_exploitation_score
            + strategic_risk_score
        ) / 400.0

        return self._clamp_probability(
            score
        )

    def _systemic_risk_probability(
        self,
        *,
        mutation_pressure_score: float,
        containment_bypass_score: float,
        operational_escalation_score: float,
        governance_exploitation_score: float,
        strategic_risk_score: float,
        uncertainty_score: float,
    ) -> float:

        score = (
            mutation_pressure_score
            + containment_bypass_score
            + operational_escalation_score
            + governance_exploitation_score
            + strategic_risk_score
            + uncertainty_score
        ) / 600.0

        return self._clamp_probability(
            score
        )

    # ==========================================================
    # RISK
    # ==========================================================

    def _evolution_risk_score(
        self,
        *,
        mutation_pressure_score: float,
        containment_bypass_score: float,
        operational_escalation_score: float,
        strategic_risk_score: float,
        containment_probability: float,
        mutation_probability: float,
        escalation_probability: float,
        systemic_risk_probability: float,
    ) -> float:

        risk = (
            mutation_pressure_score
            + containment_bypass_score
            + operational_escalation_score
            + strategic_risk_score
            + (
                (
                    1.0
                    - containment_probability
                )
                * 100.0
            )
            + (
                mutation_probability
                * 100.0
            )
            + (
                escalation_probability
                * 100.0
            )
            + (
                systemic_risk_probability
                * 100.0
            )
        ) / 8.0

        return self._clamp_score(
            risk
        )

    # ==========================================================
    # STATES
    # ==========================================================

    @staticmethod
    def _evolution_state(
        *,
        evolution_risk_score: float,
        mutation_probability: float,
        escalation_probability: float,
        systemic_risk_probability: float,
    ) -> str:

        if systemic_risk_probability >= 0.8:
            return (
                EVOLUTION_STATE_STRATEGIC_RISK
            )

        if mutation_probability >= 0.75:
            return (
                EVOLUTION_STATE_MUTATING
            )

        if escalation_probability >= 0.70:
            return (
                EVOLUTION_STATE_ESCALATING
            )

        if evolution_risk_score >= 50:
            return (
                EVOLUTION_STATE_ADAPTIVE
            )

        return EVOLUTION_STATE_STABLE

    @staticmethod
    def _projected_outcome(
        *,
        evolution_state: str,
        containment_probability: float,
        systemic_risk_probability: float,
    ) -> str:

        if (
            evolution_state
            == EVOLUTION_STATE_STRATEGIC_RISK
        ):
            return (
                EVOLUTION_OUTCOME_SYSTEMIC_RISK
            )

        if containment_probability >= 0.75:
            return (
                EVOLUTION_OUTCOME_CONTAINED
            )

        if systemic_risk_probability >= 0.65:
            return (
                EVOLUTION_OUTCOME_ESCALATED
            )

        return (
            EVOLUTION_OUTCOME_ADAPTIVE
        )

    # ==========================================================
    # RECOMMENDATIONS
    # ==========================================================

    @staticmethod
    def _recommendation(
        *,
        evolution_state: str,
        mutation_pressure_score: float,
        containment_bypass_score: float,
        operational_escalation_score: float,
    ) -> str:

        if (
            evolution_state
            == EVOLUTION_STATE_STRATEGIC_RISK
        ):
            return (
                RECOMMENDATION_ESCALATION_REVIEW
            )

        if mutation_pressure_score >= 70:
            return (
                RECOMMENDATION_MUTATION_CONTAINMENT
            )

        if containment_bypass_score >= 65:
            return (
                RECOMMENDATION_COUNTER_ADAPTATION
            )

        if operational_escalation_score >= 70:
            return (
                RECOMMENDATION_DOCTRINE_REALIGNMENT
            )

        if evolution_state in {
            EVOLUTION_STATE_MUTATING,
            EVOLUTION_STATE_ESCALATING,
        }:
            return (
                RECOMMENDATION_RESILIENCE_REINFORCEMENT
            )

        return RECOMMENDATION_MONITOR

    @staticmethod
    def _recommended_controls(
        *,
        evolution_state: str,
        recommendation: str,
    ) -> List[str]:

        controls = [
            "threat_evolution_lineage_recording",
            "threat_evolution_evidence_recording",
        ]

        if (
            evolution_state
            != EVOLUTION_STATE_STABLE
        ):
            controls.append(
                "threat_evolution_review"
            )

        if recommendation in {
            RECOMMENDATION_ESCALATION_REVIEW,
            RECOMMENDATION_DOCTRINE_REALIGNMENT,
        }:
            controls.append(
                "strategic_governance_review"
            )

        return list(
            dict.fromkeys(controls)
        )

    @staticmethod
    def _recommended_actions(
        *,
        evolution_state: str,
        recommendation: str,
    ) -> List[Dict[str, Any]]:

        return [
            {
                "action": (
                    "record_threat_evolution_lineage"
                )
            },
            {
                "action": (
                    "record_threat_evolution_evidence"
                )
            },
            {
                "action": (
                    "review_evolution_state"
                ),
                "evolution_state": (
                    evolution_state
                ),
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
        evolution_state: str,
        projected_outcome: str,
        recommendation: str,
        evolution_risk_score: float,
        containment_probability: float,
        mutation_probability: float,
        escalation_probability: float,
        systemic_risk_probability: float,
        signal_count: int,
        evolution_depth: int,
    ) -> str:

        return (
            f"Sovereign threat evolution "
            f"evaluation processed "
            f"{signal_count} signal(s) "
            f"across evolution depth "
            f"{evolution_depth}. "
            f"Evolution state "
            f"{evolution_state}; "
            f"projected outcome "
            f"{projected_outcome}; "
            f"recommendation "
            f"{recommendation}. "
            f"Evolution risk "
            f"{evolution_risk_score:.2f}; "
            f"containment probability "
            f"{containment_probability:.2f}; "
            f"mutation probability "
            f"{mutation_probability:.2f}; "
            f"escalation probability "
            f"{escalation_probability:.2f}; "
            f"systemic risk probability "
            f"{systemic_risk_probability:.2f}."
        )

    # ==========================================================
    # RECORDING
    # ==========================================================

    def _record_assessment(
        self,
        assessment: (
            SovereignThreatEvolutionAssessment
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
            SovereignThreatEvolutionAssessment
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
                "SOVEREIGN_THREAT_EVOLUTION"
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
                f"⚠️ Threat evolution memory write failed: {exc}"
            )

    def _write_to_lineage(
        self,
        assessment: (
            SovereignThreatEvolutionAssessment
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
                "SOVEREIGN_THREAT_EVOLUTION"
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
                f"⚠️ Threat evolution lineage write failed: {exc}"
            )

    def _write_to_evidence(
        self,
        assessment: (
            SovereignThreatEvolutionAssessment
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
                "SOVEREIGN_THREAT_EVOLUTION"
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
                f"⚠️ Threat evolution evidence write failed: {exc}"
            )

    def _emit_event(
        self,
        assessment: (
            SovereignThreatEvolutionAssessment
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
                "SOVEREIGN_THREAT_EVOLUTION"
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
                        "SOVEREIGN_THREAT_EVOLUTION"
                    ),
                    payload,
                )

        except Exception as exc:
            print(
                f"⚠️ Threat evolution event emit failed: {exc}"
            )

    # ==========================================================
    # NORMALIZATION
    # ==========================================================

    def _normalize_signal(
        self,
        item: (
            ThreatEvolutionSignal
            | Dict[str, Any]
        ),
        *,
        mission_id: Optional[str],
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> ThreatEvolutionSignal:

        if isinstance(
            item,
            ThreatEvolutionSignal,
        ):
            return item

        nodes = []

        for node in (
            item.get(
                "mutation_nodes",
                [],
            )
            or []
        ):

            nodes.append(
                ThreatMutationNode(
                    mutation_id=str(
                        node.get(
                            "mutation_id"
                        )
                        or uuid.uuid4()
                    ),
                    mutation_name=str(
                        node.get(
                            "mutation_name"
                        )
                        or "unknown_mutation"
                    ),
                    domain=self._safe_domain(
                        node.get("domain")
                    ),
                    mutation_pressure_score=(
                        self._clamp_score(
                            node.get(
                                "mutation_pressure_score",
                                0.0,
                            )
                        )
                    ),
                    adaptation_velocity_score=(
                        self._clamp_score(
                            node.get(
                                "adaptation_velocity_score",
                                0.0,
                            )
                        )
                    ),
                    stealth_evolution_score=(
                        self._clamp_score(
                            node.get(
                                "stealth_evolution_score",
                                0.0,
                            )
                        )
                    ),
                    persistence_evolution_score=(
                        self._clamp_score(
                            node.get(
                                "persistence_evolution_score",
                                0.0,
                            )
                        )
                    ),
                    active=bool(
                        node.get(
                            "active",
                            True,
                        )
                    ),
                    metadata=dict(
                        node.get(
                            "metadata",
                            {},
                        )
                        or {}
                    ),
                )
            )

        return ThreatEvolutionSignal(
            evolution_signal_id=str(
                item.get(
                    "evolution_signal_id"
                )
                or uuid.uuid4()
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
            mutation_pressure_score=(
                self._clamp_score(
                    item.get(
                        "mutation_pressure_score",
                        0.0,
                    )
                )
            ),
            adaptation_velocity_score=(
                self._clamp_score(
                    item.get(
                        "adaptation_velocity_score",
                        0.0,
                    )
                )
            ),
            containment_bypass_score=(
                self._clamp_score(
                    item.get(
                        "containment_bypass_score",
                        0.0,
                    )
                )
            ),
            persistence_evolution_score=(
                self._clamp_score(
                    item.get(
                        "persistence_evolution_score",
                        0.0,
                    )
                )
            ),
            propagation_mutation_score=(
                self._clamp_score(
                    item.get(
                        "propagation_mutation_score",
                        0.0,
                    )
                )
            ),
            adversarial_learning_score=(
                self._clamp_score(
                    item.get(
                        "adversarial_learning_score",
                        0.0,
                    )
                )
            ),
            operational_escalation_score=(
                self._clamp_score(
                    item.get(
                        "operational_escalation_score",
                        0.0,
                    )
                )
            ),
            doctrine_sophistication_score=(
                self._clamp_score(
                    item.get(
                        "doctrine_sophistication_score",
                        0.0,
                    )
                )
            ),
            survivability_evolution_score=(
                self._clamp_score(
                    item.get(
                        "survivability_evolution_score",
                        0.0,
                    )
                )
            ),
            stealth_adaptation_score=(
                self._clamp_score(
                    item.get(
                        "stealth_adaptation_score",
                        0.0,
                    )
                )
            ),
            governance_exploitation_score=(
                self._clamp_score(
                    item.get(
                        "governance_exploitation_score",
                        0.0,
                    )
                )
            ),
            strategic_risk_score=(
                self._clamp_score(
                    item.get(
                        "strategic_risk_score",
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
            mutation_nodes=nodes,
            payload=dict(
                item.get(
                    "payload",
                    {},
                )
                or {}
            ),
        )

    # ==========================================================
    # EMPTY / HELPERS
    # ==========================================================

    def _empty_assessment(
        self,
        *,
        mission_id: Optional[str],
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> SovereignThreatEvolutionAssessment:

        return (
            SovereignThreatEvolutionAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                evolution_state=(
                    EVOLUTION_STATE_STABLE
                ),
                projected_outcome=(
                    EVOLUTION_OUTCOME_CONTAINED
                ),
                recommendation=(
                    RECOMMENDATION_MONITOR
                ),
                mutation_pressure_score=0.0,
                adaptation_velocity_score=0.0,
                containment_bypass_score=0.0,
                persistence_evolution_score=0.0,
                propagation_mutation_score=0.0,
                adversarial_learning_score=0.0,
                operational_escalation_score=0.0,
                doctrine_sophistication_score=0.0,
                survivability_evolution_score=0.0,
                stealth_adaptation_score=0.0,
                governance_exploitation_score=0.0,
                strategic_risk_score=0.0,
                uncertainty_score=0.0,
                containment_probability=1.0,
                mutation_probability=0.0,
                escalation_probability=0.0,
                systemic_risk_probability=0.0,
                evolution_risk_score=0.0,
                explainability_score=100.0,
                evolution_confidence=1.0,
                selected_signal_id=None,
                severity=(
                    ThreatSeverity
                    .INFO.value
                ),
                confidence=1.0,
                evolution_depth=0,
                mission_id=mission_id,
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=(
                    correlation_id
                ),
                simulation_steps=[],
                mutation_topology={
                    "node_count": 0,
                    "mutation_nodes": [],
                },
                recommended_controls=[
                    (
                        "threat_evolution_lineage_recording"
                    )
                ],
                recommended_actions=[
                    {
                        "action": (
                            "continue_threat_evolution_monitoring"
                        )
                    }
                ],
                rationale=(
                    "No threat evolution "
                    "signals submitted."
                ),
                metadata={},
            )
        )

    def _select_primary_signal(
        self,
        signals: Sequence[
            ThreatEvolutionSignal
        ],
    ) -> ThreatEvolutionSignal:

        return sorted(
            signals,
            key=lambda item: (
                item
                .mutation_pressure_score,
                item
                .operational_escalation_score,
                item
                .strategic_risk_score,
                -item.created_at_ms,
            ),
            reverse=True,
        )[0]

    def _evolution_confidence(
        self,
        signals: Sequence[
            ThreatEvolutionSignal
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
            ThreatEvolutionSignal
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

            if s.mutation_nodes:
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
    def _safe_domain(
        value: Any,
    ) -> str:

        value = str(
            value
            or ThreatDomain
            .UNKNOWN.value
        ).upper()

        valid = {
            item.value
            for item in ThreatDomain
        }

        return (
            value
            if value in valid
            else ThreatDomain
            .UNKNOWN.value
        )

    @staticmethod
    def _safe_severity(
        value: Any,
    ) -> str:

        value = str(
            value
            or ThreatSeverity
            .INFO.value
        ).upper()

        valid = {
            item.value
            for item in ThreatSeverity
        }

        return (
            value
            if value in valid
            else ThreatSeverity
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


def build_sovereign_threat_evolution_engine(
    *,
    event_bus: Optional[Any] = None,
    war_gaming_engine: Optional[Any] = None,
    resilience_mesh: Optional[Any] = None,
    battle_management_engine: Optional[
        Any
    ] = None,
    operational_memory_engine: Optional[
        Any
    ] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[
        Any
    ] = None,
) -> SovereignThreatEvolutionEngine:

    return (
        SovereignThreatEvolutionEngine(
            event_bus=event_bus,
            war_gaming_engine=(
                war_gaming_engine
            ),
            resilience_mesh=resilience_mesh,
            battle_management_engine=(
                battle_management_engine
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