"""
core/runtime/sovereign_adversarial_reasoning_engine.py

Sovereign Adversarial Reasoning Engine

Autonomous adversarial strategic reasoning cognition layer.

This subsystem models:
- adversarial intent inference
- strategic objective reasoning
- deception & misdirection cognition
- operational prioritization reasoning
- escalation incentive modeling
- targeting logic inference
- adversarial resource allocation reasoning
- strategic campaign decision pathways

IMPORTANT:
This subsystem DOES NOT:
- generate attacks
- provide exploit logic
- provide offensive cyber guidance
- automate offensive operations
- produce malicious payloads

It ONLY:
- reason about adversarial behavior
- infer strategic intent
- model adversarial operational priorities
- forecast adversarial decision pathways
- record replayable reasoning lineage/evidence
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
    "sovereign_adversarial_reasoning_engine"
)

DEFAULT_REASONING_DEPTH = 12


REASONING_STATE_STABLE = "STABLE"
REASONING_STATE_PROBING = "PROBING"
REASONING_STATE_ADAPTIVE = "ADAPTIVE"
REASONING_STATE_DECEPTIVE = "DECEPTIVE"
REASONING_STATE_ESCALATING = (
    "ESCALATING"
)
REASONING_STATE_STRATEGIC_RISK = (
    "STRATEGIC_RISK"
)

REASONING_OUTCOME_CONTAINED = (
    "CONTAINED"
)
REASONING_OUTCOME_PERSISTENT = (
    "PERSISTENT"
)
REASONING_OUTCOME_DECEPTIVE = (
    "DECEPTIVE"
)
REASONING_OUTCOME_ESCALATED = (
    "ESCALATED"
)
REASONING_OUTCOME_SYSTEMIC_RISK = (
    "SYSTEMIC_RISK"
)

RECOMMENDATION_MONITOR = "MONITOR"

RECOMMENDATION_COUNTER_DECEPTION = (
    "COUNTER_DECEPTION"
)

RECOMMENDATION_ESCALATION_REVIEW = (
    "ESCALATION_REVIEW"
)

RECOMMENDATION_RESILIENCE_REINFORCEMENT = (
    "RESILIENCE_REINFORCEMENT"
)

RECOMMENDATION_STRATEGIC_HARDENING = (
    "STRATEGIC_HARDENING"
)

RECOMMENDATION_OPERATIONAL_REALIGNMENT = (
    "OPERATIONAL_REALIGNMENT"
)


class AdversarialSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AdversarialDomain(str, Enum):
    ENDPOINT = "ENDPOINT"
    IDENTITY = "IDENTITY"
    CLOUD = "CLOUD"
    NETWORK = "NETWORK"
    EMAIL = "EMAIL"
    DATA = "DATA"
    GOVERNANCE = "GOVERNANCE"
    MISSION = "MISSION"
    GLOBAL = "GLOBAL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class AdversarialIntentNode:
    intent_id: str

    intent_name: str
    domain: str

    intent_confidence_score: float
    deception_probability_score: float
    escalation_pressure_score: float
    persistence_probability_score: float

    active: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class AdversarialReasoningSignal:
    reasoning_signal_id: str

    source_engine: str
    severity: str
    confidence: float

    summary: str

    mission_id: Optional[str] = None
    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    intent_confidence_score: float = (
        0.0
    )

    deception_probability_score: float = (
        0.0
    )

    escalation_pressure_score: float = (
        0.0
    )

    persistence_probability_score: float = (
        0.0
    )

    operational_priority_score: float = (
        0.0
    )

    targeting_focus_score: float = (
        0.0
    )

    survivability_focus_score: float = (
        0.0
    )

    governance_exploitation_score: float = (
        0.0
    )

    strategic_coordination_score: float = (
        0.0
    )

    resource_allocation_score: float = (
        0.0
    )

    campaign_sophistication_score: float = (
        0.0
    )

    adaptive_reasoning_score: float = (
        0.0
    )

    strategic_risk_score: float = 0.0

    uncertainty_score: float = 0.0

    intent_nodes: List[
        AdversarialIntentNode
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
class AdversarialReasoningBranch:
    branch_id: str

    branch_name: str

    projected_state: str
    projected_outcome: str

    containment_probability: float
    deception_probability: float
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
class AdversarialReasoningSimulationStep:
    step_id: str

    step_index: int

    projected_state: str
    projected_outcome: str

    intent_confidence_score: float
    deception_probability_score: float
    escalation_pressure_score: float
    persistence_probability_score: float
    operational_priority_score: float
    targeting_focus_score: float
    survivability_focus_score: float
    governance_exploitation_score: float
    strategic_coordination_score: float
    resource_allocation_score: float
    campaign_sophistication_score: float
    adaptive_reasoning_score: float
    strategic_risk_score: float
    uncertainty_score: float

    containment_probability: float
    deception_probability: float
    escalation_probability: float
    systemic_risk_probability: float

    reasoning_risk_score: float

    branches: List[
        AdversarialReasoningBranch
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
class SovereignAdversarialReasoningAssessment:
    assessment_id: str

    reasoning_state: str
    projected_outcome: str
    recommendation: str

    intent_confidence_score: float
    deception_probability_score: float
    escalation_pressure_score: float
    persistence_probability_score: float
    operational_priority_score: float
    targeting_focus_score: float
    survivability_focus_score: float
    governance_exploitation_score: float
    strategic_coordination_score: float
    resource_allocation_score: float
    campaign_sophistication_score: float
    adaptive_reasoning_score: float
    strategic_risk_score: float
    uncertainty_score: float

    containment_probability: float
    deception_probability: float
    escalation_probability: float
    systemic_risk_probability: float

    reasoning_risk_score: float

    explainability_score: float
    reasoning_confidence: float

    selected_signal_id: Optional[str]

    severity: str
    confidence: float

    reasoning_depth: int

    mission_id: Optional[str]
    tenant_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    simulation_steps: List[
        AdversarialReasoningSimulationStep
    ]

    reasoning_topology: Dict[str, Any]

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


class SovereignAdversarialReasoningEngine:
    """
    Sovereign adversarial strategic reasoning cognition.
    """

    def __init__(
        self,
        *,
        engine_name: str = (
            DEFAULT_ENGINE_NAME
        ),
        event_bus: Optional[Any] = None,
        threat_evolution_engine: Optional[
            Any
        ] = None,
        resilience_mesh: Optional[Any] = None,
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

        self.threat_evolution_engine = (
            threat_evolution_engine
        )

        self.resilience_mesh = (
            resilience_mesh
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
            SovereignAdversarialReasoningAssessment
        ] = []

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def evaluate(
        self,
        signals: Sequence[
            AdversarialReasoningSignal
            | Dict[str, Any]
        ],
        *,
        reasoning_depth: int = (
            DEFAULT_REASONING_DEPTH
        ),
        mission_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> (
        SovereignAdversarialReasoningAssessment
    ):

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

        intent_confidence = (
            self._avg_score(
                [
                    s
                    .intent_confidence_score
                    for s in normalized
                ]
            )
        )

        deception_probability_score = (
            self._avg_score(
                [
                    s
                    .deception_probability_score
                    for s in normalized
                ]
            )
        )

        escalation_pressure = (
            self._avg_score(
                [
                    s
                    .escalation_pressure_score
                    for s in normalized
                ]
            )
        )

        persistence_probability_score = (
            self._avg_score(
                [
                    s
                    .persistence_probability_score
                    for s in normalized
                ]
            )
        )

        operational_priority = (
            self._avg_score(
                [
                    s
                    .operational_priority_score
                    for s in normalized
                ]
            )
        )

        targeting_focus = (
            self._avg_score(
                [
                    s
                    .targeting_focus_score
                    for s in normalized
                ]
            )
        )

        survivability_focus = (
            self._avg_score(
                [
                    s
                    .survivability_focus_score
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

        strategic_coordination = (
            self._avg_score(
                [
                    s
                    .strategic_coordination_score
                    for s in normalized
                ]
            )
        )

        resource_allocation = (
            self._avg_score(
                [
                    s
                    .resource_allocation_score
                    for s in normalized
                ]
            )
        )

        campaign_sophistication = (
            self._avg_score(
                [
                    s
                    .campaign_sophistication_score
                    for s in normalized
                ]
            )
        )

        adaptive_reasoning = (
            self._avg_score(
                [
                    s
                    .adaptive_reasoning_score
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
                deception_probability_score=(
                    deception_probability_score
                ),
                escalation_pressure_score=(
                    escalation_pressure
                ),
                strategic_risk_score=(
                    strategic_risk
                ),
            )
        )

        deception_probability = (
            self
            ._deception_probability(
                deception_probability_score=(
                    deception_probability_score
                ),
                governance_exploitation_score=(
                    governance_exploitation
                ),
                adaptive_reasoning_score=(
                    adaptive_reasoning
                ),
            )
        )

        escalation_probability = (
            self
            ._escalation_probability(
                escalation_pressure_score=(
                    escalation_pressure
                ),
                operational_priority_score=(
                    operational_priority
                ),
                strategic_coordination_score=(
                    strategic_coordination
                ),
                campaign_sophistication_score=(
                    campaign_sophistication
                ),
            )
        )

        systemic_risk_probability = (
            self
            ._systemic_risk_probability(
                escalation_pressure_score=(
                    escalation_pressure
                ),
                governance_exploitation_score=(
                    governance_exploitation
                ),
                strategic_coordination_score=(
                    strategic_coordination
                ),
                strategic_risk_score=(
                    strategic_risk
                ),
                uncertainty_score=(
                    uncertainty
                ),
            )
        )

        reasoning_risk = (
            self._reasoning_risk_score(
                escalation_pressure_score=(
                    escalation_pressure
                ),
                deception_probability_score=(
                    deception_probability_score
                ),
                governance_exploitation_score=(
                    governance_exploitation
                ),
                strategic_risk_score=(
                    strategic_risk
                ),
                containment_probability=(
                    containment_probability
                ),
                deception_probability=(
                    deception_probability
                ),
                escalation_probability=(
                    escalation_probability
                ),
                systemic_risk_probability=(
                    systemic_risk_probability
                ),
            )
        )

        reasoning_state = (
            self._reasoning_state(
                reasoning_risk_score=(
                    reasoning_risk
                ),
                deception_probability=(
                    deception_probability
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
                reasoning_state=(
                    reasoning_state
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
                reasoning_state=(
                    reasoning_state
                ),
                deception_probability_score=(
                    deception_probability_score
                ),
                escalation_pressure_score=(
                    escalation_pressure
                ),
                governance_exploitation_score=(
                    governance_exploitation
                ),
            )
        )

        topology = (
            self._build_topology(
                normalized
            )
        )

        steps = (
            self._build_reasoning_steps(
                intent_confidence_score=(
                    intent_confidence
                ),
                deception_probability_score=(
                    deception_probability_score
                ),
                escalation_pressure_score=(
                    escalation_pressure
                ),
                persistence_probability_score=(
                    persistence_probability_score
                ),
                operational_priority_score=(
                    operational_priority
                ),
                targeting_focus_score=(
                    targeting_focus
                ),
                survivability_focus_score=(
                    survivability_focus
                ),
                governance_exploitation_score=(
                    governance_exploitation
                ),
                strategic_coordination_score=(
                    strategic_coordination
                ),
                resource_allocation_score=(
                    resource_allocation
                ),
                campaign_sophistication_score=(
                    campaign_sophistication
                ),
                adaptive_reasoning_score=(
                    adaptive_reasoning
                ),
                strategic_risk_score=(
                    strategic_risk
                ),
                uncertainty_score=(
                    uncertainty
                ),
                reasoning_depth=(
                    reasoning_depth
                ),
            )
        )

        assessment = (
            SovereignAdversarialReasoningAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                reasoning_state=(
                    reasoning_state
                ),
                projected_outcome=(
                    projected_outcome
                ),
                recommendation=(
                    recommendation
                ),
                intent_confidence_score=(
                    intent_confidence
                ),
                deception_probability_score=(
                    deception_probability_score
                ),
                escalation_pressure_score=(
                    escalation_pressure
                ),
                persistence_probability_score=(
                    persistence_probability_score
                ),
                operational_priority_score=(
                    operational_priority
                ),
                targeting_focus_score=(
                    targeting_focus
                ),
                survivability_focus_score=(
                    survivability_focus
                ),
                governance_exploitation_score=(
                    governance_exploitation
                ),
                strategic_coordination_score=(
                    strategic_coordination
                ),
                resource_allocation_score=(
                    resource_allocation
                ),
                campaign_sophistication_score=(
                    campaign_sophistication
                ),
                adaptive_reasoning_score=(
                    adaptive_reasoning
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
                deception_probability=(
                    deception_probability
                ),
                escalation_probability=(
                    escalation_probability
                ),
                systemic_risk_probability=(
                    systemic_risk_probability
                ),
                reasoning_risk_score=(
                    reasoning_risk
                ),
                explainability_score=(
                    self
                    ._explainability_score(
                        normalized
                    )
                ),
                reasoning_confidence=(
                    self
                    ._reasoning_confidence(
                        normalized
                    )
                ),
                selected_signal_id=(
                    selected
                    .reasoning_signal_id
                ),
                severity=(
                    selected.severity
                ),
                confidence=(
                    selected.confidence
                ),
                reasoning_depth=(
                    reasoning_depth
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
                reasoning_topology=(
                    topology
                ),
                recommended_controls=(
                    self
                    ._recommended_controls(
                        reasoning_state=(
                            reasoning_state
                        ),
                        recommendation=(
                            recommendation
                        ),
                    )
                ),
                recommended_actions=(
                    self
                    ._recommended_actions(
                        reasoning_state=(
                            reasoning_state
                        ),
                        recommendation=(
                            recommendation
                        ),
                    )
                ),
                rationale=(
                    self._build_rationale(
                        reasoning_state=(
                            reasoning_state
                        ),
                        projected_outcome=(
                            projected_outcome
                        ),
                        recommendation=(
                            recommendation
                        ),
                        reasoning_risk_score=(
                            reasoning_risk
                        ),
                        containment_probability=(
                            containment_probability
                        ),
                        deception_probability=(
                            deception_probability
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
                        reasoning_depth=(
                            reasoning_depth
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
    # REMAINING HELPERS/TRACKING/TOPOLOGY
    # ==========================================================

    def _build_topology(
        self,
        signals: Sequence[
            AdversarialReasoningSignal
        ],
    ) -> Dict[str, Any]:

        nodes = []

        for signal in signals:
            for node in (
                signal.intent_nodes or []
            ):

                nodes.append(
                    {
                        "intent_id": (
                            node.intent_id
                        ),
                        "intent_name": (
                            node.intent_name
                        ),
                        "domain": (
                            node.domain
                        ),
                        "intent_confidence_score": (
                            node
                            .intent_confidence_score
                        ),
                        "deception_probability_score": (
                            node
                            .deception_probability_score
                        ),
                        "escalation_pressure_score": (
                            node
                            .escalation_pressure_score
                        ),
                        "persistence_probability_score": (
                            node
                            .persistence_probability_score
                        ),
                        "active": (
                            node.active
                        ),
                    }
                )

        return {
            "node_count": len(nodes),
            "intent_nodes": nodes,
            "topology_state": (
                "ACTIVE"
                if nodes
                else "EMPTY"
            ),
        }

    # ==========================================================
    # PROBABILITIES
    # ==========================================================

    def _containment_probability(
        self,
        *,
        deception_probability_score: float,
        escalation_pressure_score: float,
        strategic_risk_score: float,
    ) -> float:

        score = (
            (
                100.0
                - deception_probability_score
            )
            + (
                100.0
                - escalation_pressure_score
            )
            + (
                100.0
                - strategic_risk_score
            )
        ) / 300.0

        return self._clamp_probability(
            score
        )

    def _deception_probability(
        self,
        *,
        deception_probability_score: float,
        governance_exploitation_score: float,
        adaptive_reasoning_score: float,
    ) -> float:

        score = (
            deception_probability_score
            + governance_exploitation_score
            + adaptive_reasoning_score
        ) / 300.0

        return self._clamp_probability(
            score
        )

    def _escalation_probability(
        self,
        *,
        escalation_pressure_score: float,
        operational_priority_score: float,
        strategic_coordination_score: float,
        campaign_sophistication_score: float,
    ) -> float:

        score = (
            escalation_pressure_score
            + operational_priority_score
            + strategic_coordination_score
            + campaign_sophistication_score
        ) / 400.0

        return self._clamp_probability(
            score
        )

    def _systemic_risk_probability(
        self,
        *,
        escalation_pressure_score: float,
        governance_exploitation_score: float,
        strategic_coordination_score: float,
        strategic_risk_score: float,
        uncertainty_score: float,
    ) -> float:

        score = (
            escalation_pressure_score
            + governance_exploitation_score
            + strategic_coordination_score
            + strategic_risk_score
            + uncertainty_score
        ) / 500.0

        return self._clamp_probability(
            score
        )

    # ==========================================================
    # RISK
    # ==========================================================

    def _reasoning_risk_score(
        self,
        *,
        escalation_pressure_score: float,
        deception_probability_score: float,
        governance_exploitation_score: float,
        strategic_risk_score: float,
        containment_probability: float,
        deception_probability: float,
        escalation_probability: float,
        systemic_risk_probability: float,
    ) -> float:

        risk = (
            escalation_pressure_score
            + deception_probability_score
            + governance_exploitation_score
            + strategic_risk_score
            + (
                (
                    1.0
                    - containment_probability
                )
                * 100.0
            )
            + (
                deception_probability
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
    def _reasoning_state(
        *,
        reasoning_risk_score: float,
        deception_probability: float,
        escalation_probability: float,
        systemic_risk_probability: float,
    ) -> str:

        if systemic_risk_probability >= 0.80:
            return (
                REASONING_STATE_STRATEGIC_RISK
            )

        if deception_probability >= 0.75:
            return (
                REASONING_STATE_DECEPTIVE
            )

        if escalation_probability >= 0.70:
            return (
                REASONING_STATE_ESCALATING
            )

        if reasoning_risk_score >= 50:
            return (
                REASONING_STATE_ADAPTIVE
            )

        return REASONING_STATE_STABLE

    @staticmethod
    def _projected_outcome(
        *,
        reasoning_state: str,
        containment_probability: float,
        systemic_risk_probability: float,
    ) -> str:

        if (
            reasoning_state
            == REASONING_STATE_STRATEGIC_RISK
        ):
            return (
                REASONING_OUTCOME_SYSTEMIC_RISK
            )

        if containment_probability >= 0.75:
            return (
                REASONING_OUTCOME_CONTAINED
            )

        if systemic_risk_probability >= 0.65:
            return (
                REASONING_OUTCOME_ESCALATED
            )

        return (
            REASONING_OUTCOME_PERSISTENT
        )

    # ==========================================================
    # RECOMMENDATIONS
    # ==========================================================

    @staticmethod
    def _recommendation(
        *,
        reasoning_state: str,
        deception_probability_score: float,
        escalation_pressure_score: float,
        governance_exploitation_score: float,
    ) -> str:

        if (
            reasoning_state
            == REASONING_STATE_STRATEGIC_RISK
        ):
            return (
                RECOMMENDATION_ESCALATION_REVIEW
            )

        if deception_probability_score >= 70:
            return (
                RECOMMENDATION_COUNTER_DECEPTION
            )

        if escalation_pressure_score >= 70:
            return (
                RECOMMENDATION_OPERATIONAL_REALIGNMENT
            )

        if governance_exploitation_score >= 65:
            return (
                RECOMMENDATION_STRATEGIC_HARDENING
            )

        if reasoning_state in {
            REASONING_STATE_ESCALATING,
            REASONING_STATE_DECEPTIVE,
        }:
            return (
                RECOMMENDATION_RESILIENCE_REINFORCEMENT
            )

        return RECOMMENDATION_MONITOR

    # ==========================================================
    # PLACEHOLDER METHODS
    # ==========================================================

    def _build_reasoning_steps(
        self,
        **kwargs: Any,
    ) -> List[
        AdversarialReasoningSimulationStep
    ]:

        return []

    def _recommended_controls(
        self,
        *,
        reasoning_state: str,
        recommendation: str,
    ) -> List[str]:

        return [
            "adversarial_reasoning_lineage_recording",
            "adversarial_reasoning_evidence_recording",
        ]

    def _recommended_actions(
        self,
        *,
        reasoning_state: str,
        recommendation: str,
    ) -> List[Dict[str, Any]]:

        return [
            {
                "action": (
                    "record_adversarial_reasoning"
                )
            }
        ]

    def _build_rationale(
        self,
        **kwargs: Any,
    ) -> str:

        return (
            "Sovereign adversarial reasoning "
            "assessment completed."
        )

    def _record_assessment(
        self,
        assessment: (
            SovereignAdversarialReasoningAssessment
        ),
        *,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        self._assessments.append(
            assessment
        )

    def _normalize_signal(
        self,
        item: (
            AdversarialReasoningSignal
            | Dict[str, Any]
        ),
        *,
        mission_id: Optional[str],
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> AdversarialReasoningSignal:

        if isinstance(
            item,
            AdversarialReasoningSignal,
        ):
            return item

        return AdversarialReasoningSignal(
            reasoning_signal_id=str(
                uuid.uuid4()
            ),
            source_engine=str(
                item.get(
                    "source_engine",
                    "unknown_engine",
                )
            ),
            severity=str(
                item.get(
                    "severity",
                    "INFO",
                )
            ),
            confidence=float(
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
            mission_id=mission_id,
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
        )

    def _empty_assessment(
        self,
        *,
        mission_id: Optional[str],
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> (
        SovereignAdversarialReasoningAssessment
    ):

        return (
            SovereignAdversarialReasoningAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                reasoning_state=(
                    REASONING_STATE_STABLE
                ),
                projected_outcome=(
                    REASONING_OUTCOME_CONTAINED
                ),
                recommendation=(
                    RECOMMENDATION_MONITOR
                ),
                intent_confidence_score=0.0,
                deception_probability_score=0.0,
                escalation_pressure_score=0.0,
                persistence_probability_score=0.0,
                operational_priority_score=0.0,
                targeting_focus_score=0.0,
                survivability_focus_score=0.0,
                governance_exploitation_score=0.0,
                strategic_coordination_score=0.0,
                resource_allocation_score=0.0,
                campaign_sophistication_score=0.0,
                adaptive_reasoning_score=0.0,
                strategic_risk_score=0.0,
                uncertainty_score=0.0,
                containment_probability=1.0,
                deception_probability=0.0,
                escalation_probability=0.0,
                systemic_risk_probability=0.0,
                reasoning_risk_score=0.0,
                explainability_score=100.0,
                reasoning_confidence=1.0,
                selected_signal_id=None,
                severity="INFO",
                confidence=1.0,
                reasoning_depth=0,
                mission_id=mission_id,
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=(
                    correlation_id
                ),
                simulation_steps=[],
                reasoning_topology={},
                recommended_controls=[],
                recommended_actions=[],
                rationale=(
                    "No adversarial reasoning "
                    "signals submitted."
                ),
                metadata={},
            )
        )

    def _select_primary_signal(
        self,
        signals: Sequence[
            AdversarialReasoningSignal
        ],
    ) -> AdversarialReasoningSignal:

        return signals[0]

    def _reasoning_confidence(
        self,
        signals: Sequence[
            AdversarialReasoningSignal
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
            AdversarialReasoningSignal
        ],
    ) -> float:

        return 100.0

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


def build_sovereign_adversarial_reasoning_engine(
    *,
    event_bus: Optional[Any] = None,
    threat_evolution_engine: Optional[
        Any
    ] = None,
    resilience_mesh: Optional[Any] = None,
    operational_memory_engine: Optional[
        Any
    ] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[
        Any
    ] = None,
) -> SovereignAdversarialReasoningEngine:

    return (
        SovereignAdversarialReasoningEngine(
            event_bus=event_bus,
            threat_evolution_engine=(
                threat_evolution_engine
            ),
            resilience_mesh=resilience_mesh,
            operational_memory_engine=(
                operational_memory_engine
            ),
            lineage_engine=lineage_engine,
            fedramp_evidence_lineage_engine=(
                fedramp_evidence_lineage_engine
            ),
        )
    )