"""
core/runtime/sovereign_autonomous_campaign_engine.py

Sovereign Autonomous Campaign Engine

Coordinated adversarial campaign cognition layer.

This subsystem models:
- coordinated attack campaigns
- persistent adversarial behavior
- multi-stage attack evolution
- campaign survivability
- distributed attack coordination
- adaptive attacker behavior
- mission degradation under campaign pressure
- resilience exhaustion
- campaign replay intelligence
- adversarial campaign forecasting

IMPORTANT:
This subsystem DOES NOT:
- attack systems
- exploit infrastructure
- execute malware
- scan networks
- perform offensive actions
- mutate infrastructure

It ONLY:
- models adversarial campaign behavior
- simulates cyber campaign evolution
- evaluates mission survivability
- forecasts campaign escalation
- records replayable campaign lineage/evidence
"""

from __future__ import annotations

import statistics
import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


DEFAULT_ENGINE_NAME = (
    "sovereign_autonomous_campaign_engine"
)

DEFAULT_CAMPAIGN_DEPTH = 8


CAMPAIGN_STATE_STABLE = "STABLE"
CAMPAIGN_STATE_RECONNAISSANCE = "RECONNAISSANCE"
CAMPAIGN_STATE_INITIAL_COMPROMISE = (
    "INITIAL_COMPROMISE"
)
CAMPAIGN_STATE_LATERAL_MOVEMENT = (
    "LATERAL_MOVEMENT"
)
CAMPAIGN_STATE_PERSISTENCE = "PERSISTENCE"
CAMPAIGN_STATE_ESCALATION = "ESCALATION"
CAMPAIGN_STATE_MISSION_IMPACT = (
    "MISSION_IMPACT"
)
CAMPAIGN_STATE_RECOVERY_STRESS = (
    "RECOVERY_STRESS"
)
CAMPAIGN_STATE_SYSTEMIC_RISK = (
    "SYSTEMIC_RISK"
)

CAMPAIGN_OUTCOME_CONTAINED = (
    "CONTAINED"
)
CAMPAIGN_OUTCOME_CONTESTED = (
    "CONTESTED"
)
CAMPAIGN_OUTCOME_DEGRADED = (
    "DEGRADED"
)
CAMPAIGN_OUTCOME_PERSISTENT = (
    "PERSISTENT"
)
CAMPAIGN_OUTCOME_SYSTEMIC_RISK = (
    "SYSTEMIC_RISK"
)

RECOMMENDATION_MONITOR = "MONITOR"
RECOMMENDATION_DEFENSE_REVIEW = (
    "DEFENSE_REVIEW"
)
RECOMMENDATION_CAMPAIGN_ESCALATION = (
    "CAMPAIGN_ESCALATION"
)
RECOMMENDATION_MISSION_CONTINUITY = (
    "MISSION_CONTINUITY"
)
RECOMMENDATION_RESILIENCE_REVIEW = (
    "RESILIENCE_REVIEW"
)
RECOMMENDATION_GOVERNANCE_ESCALATION = (
    "GOVERNANCE_ESCALATION"
)
RECOMMENDATION_COORDINATED_RESPONSE = (
    "COORDINATED_RESPONSE"
)


class CampaignSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CampaignDomain(str, Enum):
    ENDPOINT = "ENDPOINT"
    NETWORK = "NETWORK"
    CLOUD = "CLOUD"
    IDENTITY = "IDENTITY"
    EMAIL = "EMAIL"
    DATA = "DATA"
    MISSION = "MISSION"
    GOVERNANCE = "GOVERNANCE"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    GLOBAL = "GLOBAL"
    UNKNOWN = "UNKNOWN"


class CampaignStage(str, Enum):
    RECONNAISSANCE = "RECONNAISSANCE"
    INITIAL_ACCESS = "INITIAL_ACCESS"
    PERSISTENCE = "PERSISTENCE"
    LATERAL_MOVEMENT = "LATERAL_MOVEMENT"
    PRIVILEGE_ESCALATION = (
        "PRIVILEGE_ESCALATION"
    )
    COLLECTION = "COLLECTION"
    EXFILTRATION = "EXFILTRATION"
    DISRUPTION = "DISRUPTION"
    RECOVERY_INTERFERENCE = (
        "RECOVERY_INTERFERENCE"
    )
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class CampaignSignal:
    campaign_signal_id: str

    campaign_stage: str
    domain: str
    source_engine: str

    severity: str
    confidence: float

    summary: str

    mission_id: Optional[str] = None
    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    attack_coordination_score: float = 0.0
    propagation_pressure_score: float = 0.0
    persistence_pressure_score: float = 0.0
    lateral_movement_pressure_score: float = (
        0.0
    )
    privilege_escalation_pressure_score: float = (
        0.0
    )
    containment_stability_score: float = (
        100.0
    )
    defense_exhaustion_score: float = 0.0
    resilience_degradation_score: float = (
        0.0
    )
    governance_saturation_score: float = (
        0.0
    )
    mission_degradation_score: float = (
        0.0
    )
    operational_disruption_score: float = (
        0.0
    )
    recovery_interference_score: float = (
        0.0
    )
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
class CampaignBranch:
    branch_id: str

    branch_name: str

    projected_state: str
    projected_outcome: str

    systemic_risk_probability: float
    containment_probability: float
    mission_survivability_probability: (
        float
    )
    resilience_recovery_probability: (
        float
    )

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
class CampaignSimulationStep:
    step_id: str

    step_index: int

    projected_state: str
    projected_outcome: str

    attack_coordination_score: float
    propagation_pressure_score: float
    persistence_pressure_score: float
    lateral_movement_pressure_score: (
        float
    )
    privilege_escalation_pressure_score: (
        float
    )
    containment_stability_score: float
    defense_exhaustion_score: float
    resilience_degradation_score: float
    governance_saturation_score: float
    mission_degradation_score: float
    operational_disruption_score: float
    recovery_interference_score: float
    uncertainty_score: float

    systemic_risk_probability: float
    containment_probability: float
    mission_survivability_probability: (
        float
    )
    resilience_recovery_probability: (
        float
    )

    campaign_risk_score: float

    branches: List[CampaignBranch] = field(
        default_factory=list
    )

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
class SovereignCampaignAssessment:
    assessment_id: str

    campaign_state: str
    projected_outcome: str
    recommendation: str

    attack_coordination_score: float
    propagation_pressure_score: float
    persistence_pressure_score: float
    lateral_movement_pressure_score: (
        float
    )
    privilege_escalation_pressure_score: (
        float
    )
    containment_stability_score: float
    defense_exhaustion_score: float
    resilience_degradation_score: float
    governance_saturation_score: float
    mission_degradation_score: float
    operational_disruption_score: float
    recovery_interference_score: float
    uncertainty_score: float

    systemic_risk_probability: float
    containment_probability: float
    mission_survivability_probability: (
        float
    )
    resilience_recovery_probability: (
        float
    )

    campaign_risk_score: float

    explainability_score: float
    campaign_confidence: float

    selected_signal_id: Optional[str]
    selected_campaign_stage: Optional[
        str
    ]

    severity: str
    confidence: float

    campaign_depth: int

    mission_id: Optional[str]
    tenant_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    simulation_steps: List[
        CampaignSimulationStep
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


@dataclass(frozen=True)
class SovereignCampaignSnapshot:
    engine_name: str

    total_signals_seen: int
    total_assessments_created: int

    last_assessment_id: Optional[str]

    last_campaign_state: Optional[str]

    last_campaign_risk_score: Optional[
        float
    ]

    last_updated_ms: int


class SovereignAutonomousCampaignEngine:
    """
    Coordinated adversarial campaign cognition.
    """

    def __init__(
        self,
        *,
        engine_name: str = (
            DEFAULT_ENGINE_NAME
        ),
        event_bus: Optional[Any] = None,
        cyber_defense_simulation_mesh: Optional[
            Any
        ] = None,
        runtime_evolution_engine: Optional[
            Any
        ] = None,
        operational_forecasting_engine: Optional[
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

        self.cyber_defense_simulation_mesh = (
            cyber_defense_simulation_mesh
        )

        self.runtime_evolution_engine = (
            runtime_evolution_engine
        )

        self.operational_forecasting_engine = (
            operational_forecasting_engine
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
            SovereignCampaignAssessment
        ] = []

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def evaluate(
        self,
        signals: Sequence[
            CampaignSignal | Dict[str, Any]
        ],
        *,
        campaign_depth: int = (
            DEFAULT_CAMPAIGN_DEPTH
        ),
        mission_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> SovereignCampaignAssessment:

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

        attack_coordination = (
            self._avg_score(
                [
                    s.attack_coordination_score
                    for s in normalized
                ]
            )
        )

        propagation_pressure = (
            self._avg_score(
                [
                    s.propagation_pressure_score
                    for s in normalized
                ]
            )
        )

        persistence_pressure = (
            self._avg_score(
                [
                    s.persistence_pressure_score
                    for s in normalized
                ]
            )
        )

        lateral_pressure = (
            self._avg_score(
                [
                    s
                    .lateral_movement_pressure_score
                    for s in normalized
                ]
            )
        )

        privilege_pressure = (
            self._avg_score(
                [
                    s
                    .privilege_escalation_pressure_score
                    for s in normalized
                ]
            )
        )

        containment_stability = (
            self._avg_score(
                [
                    s
                    .containment_stability_score
                    for s in normalized
                ]
            )
        )

        defense_exhaustion = (
            self._avg_score(
                [
                    s
                    .defense_exhaustion_score
                    for s in normalized
                ]
            )
        )

        resilience_degradation = (
            self._avg_score(
                [
                    s
                    .resilience_degradation_score
                    for s in normalized
                ]
            )
        )

        governance_saturation = (
            self._avg_score(
                [
                    s
                    .governance_saturation_score
                    for s in normalized
                ]
            )
        )

        mission_degradation = (
            self._avg_score(
                [
                    s
                    .mission_degradation_score
                    for s in normalized
                ]
            )
        )

        operational_disruption = (
            self._avg_score(
                [
                    s
                    .operational_disruption_score
                    for s in normalized
                ]
            )
        )

        recovery_interference = (
            self._avg_score(
                [
                    s
                    .recovery_interference_score
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

        systemic_risk_probability = (
            self
            ._systemic_risk_probability(
                attack_coordination_score=(
                    attack_coordination
                ),
                propagation_pressure_score=(
                    propagation_pressure
                ),
                persistence_pressure_score=(
                    persistence_pressure
                ),
                lateral_movement_pressure_score=(
                    lateral_pressure
                ),
                privilege_escalation_pressure_score=(
                    privilege_pressure
                ),
                containment_stability_score=(
                    containment_stability
                ),
                defense_exhaustion_score=(
                    defense_exhaustion
                ),
                resilience_degradation_score=(
                    resilience_degradation
                ),
                governance_saturation_score=(
                    governance_saturation
                ),
                mission_degradation_score=(
                    mission_degradation
                ),
                operational_disruption_score=(
                    operational_disruption
                ),
                recovery_interference_score=(
                    recovery_interference
                ),
                uncertainty_score=(
                    uncertainty
                ),
            )
        )

        containment_probability = (
            self._containment_probability(
                containment_stability_score=(
                    containment_stability
                ),
                defense_exhaustion_score=(
                    defense_exhaustion
                ),
                attack_coordination_score=(
                    attack_coordination
                ),
                propagation_pressure_score=(
                    propagation_pressure
                ),
            )
        )

        mission_survivability = (
            self
            ._mission_survivability_probability(
                resilience_degradation_score=(
                    resilience_degradation
                ),
                mission_degradation_score=(
                    mission_degradation
                ),
                systemic_risk_probability=(
                    systemic_risk_probability
                ),
            )
        )

        resilience_recovery = (
            self
            ._resilience_recovery_probability(
                resilience_degradation_score=(
                    resilience_degradation
                ),
                recovery_interference_score=(
                    recovery_interference
                ),
                systemic_risk_probability=(
                    systemic_risk_probability
                ),
                uncertainty_score=(
                    uncertainty
                ),
            )
        )

        campaign_risk = (
            self._campaign_risk_score(
                attack_coordination_score=(
                    attack_coordination
                ),
                propagation_pressure_score=(
                    propagation_pressure
                ),
                persistence_pressure_score=(
                    persistence_pressure
                ),
                lateral_movement_pressure_score=(
                    lateral_pressure
                ),
                privilege_escalation_pressure_score=(
                    privilege_pressure
                ),
                defense_exhaustion_score=(
                    defense_exhaustion
                ),
                resilience_degradation_score=(
                    resilience_degradation
                ),
                governance_saturation_score=(
                    governance_saturation
                ),
                mission_degradation_score=(
                    mission_degradation
                ),
                operational_disruption_score=(
                    operational_disruption
                ),
                systemic_risk_probability=(
                    systemic_risk_probability
                ),
                containment_probability=(
                    containment_probability
                ),
                mission_survivability_probability=(
                    mission_survivability
                ),
                resilience_recovery_probability=(
                    resilience_recovery
                ),
            )
        )

        campaign_state = (
            self._campaign_state(
                campaign_risk_score=(
                    campaign_risk
                ),
                systemic_risk_probability=(
                    systemic_risk_probability
                ),
                containment_probability=(
                    containment_probability
                ),
                mission_survivability_probability=(
                    mission_survivability
                ),
            )
        )

        projected_outcome = (
            self._projected_outcome(
                campaign_state=(
                    campaign_state
                ),
                systemic_risk_probability=(
                    systemic_risk_probability
                ),
                containment_probability=(
                    containment_probability
                ),
            )
        )

        recommendation = (
            self._recommendation(
                campaign_state=(
                    campaign_state
                ),
                mission_degradation_score=(
                    mission_degradation
                ),
                governance_saturation_score=(
                    governance_saturation
                ),
                containment_probability=(
                    containment_probability
                ),
                resilience_recovery_probability=(
                    resilience_recovery
                ),
            )
        )

        steps = (
            self._build_campaign_steps(
                attack_coordination_score=(
                    attack_coordination
                ),
                propagation_pressure_score=(
                    propagation_pressure
                ),
                persistence_pressure_score=(
                    persistence_pressure
                ),
                lateral_movement_pressure_score=(
                    lateral_pressure
                ),
                privilege_escalation_pressure_score=(
                    privilege_pressure
                ),
                containment_stability_score=(
                    containment_stability
                ),
                defense_exhaustion_score=(
                    defense_exhaustion
                ),
                resilience_degradation_score=(
                    resilience_degradation
                ),
                governance_saturation_score=(
                    governance_saturation
                ),
                mission_degradation_score=(
                    mission_degradation
                ),
                operational_disruption_score=(
                    operational_disruption
                ),
                recovery_interference_score=(
                    recovery_interference
                ),
                uncertainty_score=(
                    uncertainty
                ),
                campaign_depth=(
                    campaign_depth
                ),
            )
        )

        assessment = (
            SovereignCampaignAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                campaign_state=(
                    campaign_state
                ),
                projected_outcome=(
                    projected_outcome
                ),
                recommendation=(
                    recommendation
                ),
                attack_coordination_score=(
                    attack_coordination
                ),
                propagation_pressure_score=(
                    propagation_pressure
                ),
                persistence_pressure_score=(
                    persistence_pressure
                ),
                lateral_movement_pressure_score=(
                    lateral_pressure
                ),
                privilege_escalation_pressure_score=(
                    privilege_pressure
                ),
                containment_stability_score=(
                    containment_stability
                ),
                defense_exhaustion_score=(
                    defense_exhaustion
                ),
                resilience_degradation_score=(
                    resilience_degradation
                ),
                governance_saturation_score=(
                    governance_saturation
                ),
                mission_degradation_score=(
                    mission_degradation
                ),
                operational_disruption_score=(
                    operational_disruption
                ),
                recovery_interference_score=(
                    recovery_interference
                ),
                uncertainty_score=(
                    uncertainty
                ),
                systemic_risk_probability=(
                    systemic_risk_probability
                ),
                containment_probability=(
                    containment_probability
                ),
                mission_survivability_probability=(
                    mission_survivability
                ),
                resilience_recovery_probability=(
                    resilience_recovery
                ),
                campaign_risk_score=(
                    campaign_risk
                ),
                explainability_score=(
                    self
                    ._explainability_score(
                        normalized
                    )
                ),
                campaign_confidence=(
                    self
                    ._campaign_confidence(
                        normalized
                    )
                ),
                selected_signal_id=(
                    selected
                    .campaign_signal_id
                ),
                selected_campaign_stage=(
                    selected
                    .campaign_stage
                ),
                severity=(
                    selected.severity
                ),
                confidence=(
                    selected.confidence
                ),
                campaign_depth=(
                    campaign_depth
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
                simulation_steps=steps,
                recommended_controls=(
                    self
                    ._recommended_controls(
                        campaign_state=(
                            campaign_state
                        ),
                        recommendation=(
                            recommendation
                        ),
                    )
                ),
                recommended_actions=(
                    self
                    ._recommended_actions(
                        campaign_state=(
                            campaign_state
                        ),
                        recommendation=(
                            recommendation
                        ),
                    )
                ),
                rationale=(
                    self._build_rationale(
                        campaign_state=(
                            campaign_state
                        ),
                        projected_outcome=(
                            projected_outcome
                        ),
                        recommendation=(
                            recommendation
                        ),
                        campaign_risk_score=(
                            campaign_risk
                        ),
                        systemic_risk_probability=(
                            systemic_risk_probability
                        ),
                        containment_probability=(
                            containment_probability
                        ),
                        mission_survivability_probability=(
                            mission_survivability
                        ),
                        resilience_recovery_probability=(
                            resilience_recovery
                        ),
                        signal_count=len(
                            normalized
                        ),
                        campaign_depth=(
                            campaign_depth
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
    # CAMPAIGN SIMULATION
    # ==========================================================

    def _build_campaign_steps(
        self,
        *,
        attack_coordination_score: float,
        propagation_pressure_score: float,
        persistence_pressure_score: float,
        lateral_movement_pressure_score: (
            float
        ),
        privilege_escalation_pressure_score: (
            float
        ),
        containment_stability_score: float,
        defense_exhaustion_score: float,
        resilience_degradation_score: float,
        governance_saturation_score: float,
        mission_degradation_score: float,
        operational_disruption_score: float,
        recovery_interference_score: float,
        uncertainty_score: float,
        campaign_depth: int,
    ) -> List[CampaignSimulationStep]:

        steps: List[
            CampaignSimulationStep
        ] = []

        for idx in range(
            max(
                1,
                int(campaign_depth),
            )
        ):

            systemic_risk = (
                self
                ._systemic_risk_probability(
                    attack_coordination_score=(
                        attack_coordination_score
                    ),
                    propagation_pressure_score=(
                        propagation_pressure_score
                    ),
                    persistence_pressure_score=(
                        persistence_pressure_score
                    ),
                    lateral_movement_pressure_score=(
                        lateral_movement_pressure_score
                    ),
                    privilege_escalation_pressure_score=(
                        privilege_escalation_pressure_score
                    ),
                    containment_stability_score=(
                        containment_stability_score
                    ),
                    defense_exhaustion_score=(
                        defense_exhaustion_score
                    ),
                    resilience_degradation_score=(
                        resilience_degradation_score
                    ),
                    governance_saturation_score=(
                        governance_saturation_score
                    ),
                    mission_degradation_score=(
                        mission_degradation_score
                    ),
                    operational_disruption_score=(
                        operational_disruption_score
                    ),
                    recovery_interference_score=(
                        recovery_interference_score
                    ),
                    uncertainty_score=(
                        uncertainty_score
                    ),
                )
            )

            containment_probability = (
                self
                ._containment_probability(
                    containment_stability_score=(
                        containment_stability_score
                    ),
                    defense_exhaustion_score=(
                        defense_exhaustion_score
                    ),
                    attack_coordination_score=(
                        attack_coordination_score
                    ),
                    propagation_pressure_score=(
                        propagation_pressure_score
                    ),
                )
            )

            mission_survivability = (
                self
                ._mission_survivability_probability(
                    resilience_degradation_score=(
                        resilience_degradation_score
                    ),
                    mission_degradation_score=(
                        mission_degradation_score
                    ),
                    systemic_risk_probability=(
                        systemic_risk
                    ),
                )
            )

            resilience_recovery = (
                self
                ._resilience_recovery_probability(
                    resilience_degradation_score=(
                        resilience_degradation_score
                    ),
                    recovery_interference_score=(
                        recovery_interference_score
                    ),
                    systemic_risk_probability=(
                        systemic_risk
                    ),
                    uncertainty_score=(
                        uncertainty_score
                    ),
                )
            )

            campaign_risk = (
                self._campaign_risk_score(
                    attack_coordination_score=(
                        attack_coordination_score
                    ),
                    propagation_pressure_score=(
                        propagation_pressure_score
                    ),
                    persistence_pressure_score=(
                        persistence_pressure_score
                    ),
                    lateral_movement_pressure_score=(
                        lateral_movement_pressure_score
                    ),
                    privilege_escalation_pressure_score=(
                        privilege_escalation_pressure_score
                    ),
                    defense_exhaustion_score=(
                        defense_exhaustion_score
                    ),
                    resilience_degradation_score=(
                        resilience_degradation_score
                    ),
                    governance_saturation_score=(
                        governance_saturation_score
                    ),
                    mission_degradation_score=(
                        mission_degradation_score
                    ),
                    operational_disruption_score=(
                        operational_disruption_score
                    ),
                    systemic_risk_probability=(
                        systemic_risk
                    ),
                    containment_probability=(
                        containment_probability
                    ),
                    mission_survivability_probability=(
                        mission_survivability
                    ),
                    resilience_recovery_probability=(
                        resilience_recovery
                    ),
                )
            )

            state = self._campaign_state(
                campaign_risk_score=(
                    campaign_risk
                ),
                systemic_risk_probability=(
                    systemic_risk
                ),
                containment_probability=(
                    containment_probability
                ),
                mission_survivability_probability=(
                    mission_survivability
                ),
            )

            outcome = (
                self._projected_outcome(
                    campaign_state=state,
                    systemic_risk_probability=(
                        systemic_risk
                    ),
                    containment_probability=(
                        containment_probability
                    ),
                )
            )

            branches = (
                self._build_branches(
                    campaign_state=state,
                    systemic_risk_probability=(
                        systemic_risk
                    ),
                    containment_probability=(
                        containment_probability
                    ),
                    mission_survivability_probability=(
                        mission_survivability
                    ),
                    resilience_recovery_probability=(
                        resilience_recovery
                    ),
                    campaign_risk_score=(
                        campaign_risk
                    ),
                )
            )

            steps.append(
                CampaignSimulationStep(
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
                    attack_coordination_score=(
                        attack_coordination_score
                    ),
                    propagation_pressure_score=(
                        propagation_pressure_score
                    ),
                    persistence_pressure_score=(
                        persistence_pressure_score
                    ),
                    lateral_movement_pressure_score=(
                        lateral_movement_pressure_score
                    ),
                    privilege_escalation_pressure_score=(
                        privilege_escalation_pressure_score
                    ),
                    containment_stability_score=(
                        containment_stability_score
                    ),
                    defense_exhaustion_score=(
                        defense_exhaustion_score
                    ),
                    resilience_degradation_score=(
                        resilience_degradation_score
                    ),
                    governance_saturation_score=(
                        governance_saturation_score
                    ),
                    mission_degradation_score=(
                        mission_degradation_score
                    ),
                    operational_disruption_score=(
                        operational_disruption_score
                    ),
                    recovery_interference_score=(
                        recovery_interference_score
                    ),
                    uncertainty_score=(
                        uncertainty_score
                    ),
                    systemic_risk_probability=(
                        systemic_risk
                    ),
                    containment_probability=(
                        containment_probability
                    ),
                    mission_survivability_probability=(
                        mission_survivability
                    ),
                    resilience_recovery_probability=(
                        resilience_recovery
                    ),
                    campaign_risk_score=(
                        campaign_risk
                    ),
                    branches=branches,
                    rationale=(
                        f"Campaign "
                        f"simulation step "
                        f"{idx} projected "
                        f"{state}."
                    ),
                )
            )

            attack_coordination_score = (
                self._clamp_score(
                    attack_coordination_score
                    + 3.0
                )
            )

            propagation_pressure_score = (
                self._clamp_score(
                    propagation_pressure_score
                    + 2.5
                )
            )

            persistence_pressure_score = (
                self._clamp_score(
                    persistence_pressure_score
                    + 2.0
                )
            )

            lateral_movement_pressure_score = (
                self._clamp_score(
                    lateral_movement_pressure_score
                    + 2.0
                )
            )

            privilege_escalation_pressure_score = (
                self._clamp_score(
                    privilege_escalation_pressure_score
                    + 2.0
                )
            )

            defense_exhaustion_score = (
                self._clamp_score(
                    defense_exhaustion_score
                    + 2.5
                )
            )

            resilience_degradation_score = (
                self._clamp_score(
                    resilience_degradation_score
                    + 2.0
                )
            )

            governance_saturation_score = (
                self._clamp_score(
                    governance_saturation_score
                    + 1.8
                )
            )

            mission_degradation_score = (
                self._clamp_score(
                    mission_degradation_score
                    + 2.3
                )
            )

            operational_disruption_score = (
                self._clamp_score(
                    operational_disruption_score
                    + 2.2
                )
            )

            recovery_interference_score = (
                self._clamp_score(
                    recovery_interference_score
                    + 1.8
                )
            )

            uncertainty_score = (
                self._clamp_score(
                    uncertainty_score
                    + 1.0
                )
            )

            containment_stability_score = (
                self._clamp_score(
                    containment_stability_score
                    - 2.5
                )
            )

        return steps

    def _build_branches(
        self,
        *,
        campaign_state: str,
        systemic_risk_probability: float,
        containment_probability: float,
        mission_survivability_probability: (
            float
        ),
        resilience_recovery_probability: (
            float
        ),
        campaign_risk_score: float,
    ) -> List[CampaignBranch]:

        return [
            CampaignBranch(
                branch_id=str(
                    uuid.uuid4()
                ),
                branch_name=(
                    "coordinated_defense_path"
                ),
                projected_state=(
                    CAMPAIGN_STATE_ESCALATION
                ),
                projected_outcome=(
                    CAMPAIGN_OUTCOME_CONTAINED
                ),
                systemic_risk_probability=(
                    self
                    ._clamp_probability(
                        systemic_risk_probability
                        - 0.20
                    )
                ),
                containment_probability=(
                    self
                    ._clamp_probability(
                        containment_probability
                        + 0.20
                    )
                ),
                mission_survivability_probability=(
                    self
                    ._clamp_probability(
                        mission_survivability_probability
                        + 0.15
                    )
                ),
                resilience_recovery_probability=(
                    self
                    ._clamp_probability(
                        resilience_recovery_probability
                        + 0.15
                    )
                ),
                branch_score=(
                    self._clamp_score(
                        100.0
                        - campaign_risk_score
                        + 15.0
                    )
                ),
                rationale=(
                    "Projected "
                    "coordinated "
                    "campaign "
                    "containment path."
                ),
            ),
            CampaignBranch(
                branch_id=str(
                    uuid.uuid4()
                ),
                branch_name=(
                    "persistent_adversary_path"
                ),
                projected_state=(
                    CAMPAIGN_STATE_SYSTEMIC_RISK
                ),
                projected_outcome=(
                    CAMPAIGN_OUTCOME_SYSTEMIC_RISK
                ),
                systemic_risk_probability=(
                    self
                    ._clamp_probability(
                        systemic_risk_probability
                        + 0.25
                    )
                ),
                containment_probability=(
                    self
                    ._clamp_probability(
                        containment_probability
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
                resilience_recovery_probability=(
                    self
                    ._clamp_probability(
                        resilience_recovery_probability
                        - 0.20
                    )
                ),
                branch_score=(
                    self._clamp_score(
                        100.0
                        - campaign_risk_score
                        - 20.0
                    )
                ),
                rationale=(
                    "Projected "
                    "persistent "
                    "adversarial "
                    "campaign path."
                ),
            ),
        ]

    # ==========================================================
    # PROBABILITIES
    # ==========================================================

    def _systemic_risk_probability(
        self,
        *,
        attack_coordination_score: float,
        propagation_pressure_score: float,
        persistence_pressure_score: float,
        lateral_movement_pressure_score: (
            float
        ),
        privilege_escalation_pressure_score: (
            float
        ),
        containment_stability_score: float,
        defense_exhaustion_score: float,
        resilience_degradation_score: float,
        governance_saturation_score: float,
        mission_degradation_score: float,
        operational_disruption_score: float,
        recovery_interference_score: float,
        uncertainty_score: float,
    ) -> float:

        risk = (
            attack_coordination_score
            + propagation_pressure_score
            + persistence_pressure_score
            + lateral_movement_pressure_score
            + privilege_escalation_pressure_score
            + defense_exhaustion_score
            + resilience_degradation_score
            + governance_saturation_score
            + mission_degradation_score
            + operational_disruption_score
            + recovery_interference_score
            + uncertainty_score
            + (
                100.0
                - containment_stability_score
            )
        ) / 1300.0

        return self._clamp_probability(
            risk
        )

    def _containment_probability(
        self,
        *,
        containment_stability_score: float,
        defense_exhaustion_score: float,
        attack_coordination_score: float,
        propagation_pressure_score: float,
    ) -> float:

        score = (
            containment_stability_score
            + (
                100.0
                - defense_exhaustion_score
            )
            + (
                100.0
                - attack_coordination_score
            )
            + (
                100.0
                - propagation_pressure_score
            )
        ) / 400.0

        return self._clamp_probability(
            score
        )

    def _mission_survivability_probability(
        self,
        *,
        resilience_degradation_score: float,
        mission_degradation_score: float,
        systemic_risk_probability: float,
    ) -> float:

        score = (
            (
                100.0
                - resilience_degradation_score
            )
            + (
                100.0
                - mission_degradation_score
            )
            + (
                100.0
                - (
                    systemic_risk_probability
                    * 100.0
                )
            )
        ) / 300.0

        return self._clamp_probability(
            score
        )

    def _resilience_recovery_probability(
        self,
        *,
        resilience_degradation_score: float,
        recovery_interference_score: float,
        systemic_risk_probability: float,
        uncertainty_score: float,
    ) -> float:

        score = (
            (
                100.0
                - resilience_degradation_score
            )
            + (
                100.0
                - recovery_interference_score
            )
            + (
                100.0
                - (
                    systemic_risk_probability
                    * 100.0
                )
            )
            + (
                100.0
                - uncertainty_score
            )
        ) / 400.0

        return self._clamp_probability(
            score
        )

    # ==========================================================
    # SCORING
    # ==========================================================

    def _campaign_risk_score(
        self,
        *,
        attack_coordination_score: float,
        propagation_pressure_score: float,
        persistence_pressure_score: float,
        lateral_movement_pressure_score: (
            float
        ),
        privilege_escalation_pressure_score: (
            float
        ),
        defense_exhaustion_score: float,
        resilience_degradation_score: float,
        governance_saturation_score: float,
        mission_degradation_score: float,
        operational_disruption_score: float,
        systemic_risk_probability: float,
        containment_probability: float,
        mission_survivability_probability: (
            float
        ),
        resilience_recovery_probability: (
            float
        ),
    ) -> float:

        risk = (
            attack_coordination_score
            + propagation_pressure_score
            + persistence_pressure_score
            + lateral_movement_pressure_score
            + privilege_escalation_pressure_score
            + defense_exhaustion_score
            + resilience_degradation_score
            + governance_saturation_score
            + mission_degradation_score
            + operational_disruption_score
            + (
                systemic_risk_probability
                * 100.0
            )
            + (
                (
                    1.0
                    - containment_probability
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
                (
                    1.0
                    - resilience_recovery_probability
                )
                * 100.0
            )
        ) / 14.0

        return self._clamp_score(
            risk
        )

    # ==========================================================
    # STATES
    # ==========================================================

    @staticmethod
    def _campaign_state(
        *,
        campaign_risk_score: float,
        systemic_risk_probability: float,
        containment_probability: float,
        mission_survivability_probability: (
            float
        ),
    ) -> str:

        if systemic_risk_probability >= 0.8:
            return (
                CAMPAIGN_STATE_SYSTEMIC_RISK
            )

        if containment_probability <= 0.25:
            return (
                CAMPAIGN_STATE_ESCALATION
            )

        if (
            mission_survivability_probability
            <= 0.35
        ):
            return (
                CAMPAIGN_STATE_MISSION_IMPACT
            )

        if campaign_risk_score >= 80:
            return (
                CAMPAIGN_STATE_RECOVERY_STRESS
            )

        if campaign_risk_score >= 65:
            return (
                CAMPAIGN_STATE_PERSISTENCE
            )

        if campaign_risk_score >= 50:
            return (
                CAMPAIGN_STATE_LATERAL_MOVEMENT
            )

        if campaign_risk_score >= 35:
            return (
                CAMPAIGN_STATE_INITIAL_COMPROMISE
            )

        return CAMPAIGN_STATE_STABLE

    @staticmethod
    def _projected_outcome(
        *,
        campaign_state: str,
        systemic_risk_probability: (
            float
        ),
        containment_probability: float,
    ) -> str:

        if (
            campaign_state
            == CAMPAIGN_STATE_SYSTEMIC_RISK
        ):
            return (
                CAMPAIGN_OUTCOME_SYSTEMIC_RISK
            )

        if systemic_risk_probability >= 0.7:
            return (
                CAMPAIGN_OUTCOME_PERSISTENT
            )

        if containment_probability >= 0.75:
            return (
                CAMPAIGN_OUTCOME_CONTAINED
            )

        if containment_probability <= 0.35:
            return (
                CAMPAIGN_OUTCOME_DEGRADED
            )

        return (
            CAMPAIGN_OUTCOME_CONTESTED
        )

    # ==========================================================
    # RECOMMENDATIONS
    # ==========================================================

    @staticmethod
    def _recommendation(
        *,
        campaign_state: str,
        mission_degradation_score: float,
        governance_saturation_score: float,
        containment_probability: float,
        resilience_recovery_probability: (
            float
        ),
    ) -> str:

        if (
            campaign_state
            == CAMPAIGN_STATE_SYSTEMIC_RISK
        ):
            return (
                RECOMMENDATION_GOVERNANCE_ESCALATION
            )

        if (
            mission_degradation_score
            >= 70
        ):
            return (
                RECOMMENDATION_MISSION_CONTINUITY
            )

        if (
            governance_saturation_score
            >= 70
        ):
            return (
                RECOMMENDATION_CAMPAIGN_ESCALATION
            )

        if (
            containment_probability
            <= 0.45
        ):
            return (
                RECOMMENDATION_COORDINATED_RESPONSE
            )

        if (
            resilience_recovery_probability
            <= 0.45
        ):
            return (
                RECOMMENDATION_RESILIENCE_REVIEW
            )

        if campaign_state in {
            CAMPAIGN_STATE_PERSISTENCE,
            CAMPAIGN_STATE_ESCALATION,
        }:
            return (
                RECOMMENDATION_DEFENSE_REVIEW
            )

        return RECOMMENDATION_MONITOR

    @staticmethod
    def _recommended_controls(
        *,
        campaign_state: str,
        recommendation: str,
    ) -> List[str]:

        controls = [
            "campaign_lineage_recording",
            "campaign_evidence_recording",
        ]

        if campaign_state != (
            CAMPAIGN_STATE_STABLE
        ):
            controls.append(
                "campaign_review"
            )

        if recommendation in {
            RECOMMENDATION_GOVERNANCE_ESCALATION,
            RECOMMENDATION_COORDINATED_RESPONSE,
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
        campaign_state: str,
        recommendation: str,
    ) -> List[Dict[str, Any]]:

        actions = [
            {
                "action": (
                    "record_campaign_lineage"
                )
            },
            {
                "action": (
                    "record_campaign_evidence"
                )
            },
        ]

        actions.append(
            {
                "action": (
                    "review_campaign_state"
                ),
                "campaign_state": (
                    campaign_state
                ),
            }
        )

        if recommendation:
            actions.append(
                {
                    "action": (
                        "review_campaign_recommendation"
                    ),
                    "recommendation": (
                        recommendation
                    ),
                }
            )

        return actions

    # ==========================================================
    # RATIONALE
    # ==========================================================

    @staticmethod
    def _build_rationale(
        *,
        campaign_state: str,
        projected_outcome: str,
        recommendation: str,
        campaign_risk_score: float,
        systemic_risk_probability: (
            float
        ),
        containment_probability: float,
        mission_survivability_probability: (
            float
        ),
        resilience_recovery_probability: (
            float
        ),
        signal_count: int,
        campaign_depth: int,
    ) -> str:

        return (
            f"Sovereign adversarial "
            f"campaign evaluation "
            f"processed "
            f"{signal_count} signal(s) "
            f"across campaign depth "
            f"{campaign_depth}. "
            f"Campaign state "
            f"{campaign_state}; "
            f"projected outcome "
            f"{projected_outcome}; "
            f"recommendation "
            f"{recommendation}. "
            f"Campaign risk "
            f"{campaign_risk_score:.2f}; "
            f"systemic risk probability "
            f"{systemic_risk_probability:.2f}; "
            f"containment probability "
            f"{containment_probability:.2f}; "
            f"mission survivability "
            f"{mission_survivability_probability:.2f}; "
            f"resilience recovery "
            f"{resilience_recovery_probability:.2f}."
        )

    # ==========================================================
    # RECORDING
    # ==========================================================

    def _record_assessment(
        self,
        assessment: (
            SovereignCampaignAssessment
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
            SovereignCampaignAssessment
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
                "SOVEREIGN_CAMPAIGN_ASSESSMENT"
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
                f"⚠️ Campaign memory write failed: {exc}"
            )

    def _write_to_lineage(
        self,
        assessment: (
            SovereignCampaignAssessment
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
                "SOVEREIGN_CAMPAIGN"
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
                f"⚠️ Campaign lineage write failed: {exc}"
            )

    def _write_to_evidence(
        self,
        assessment: (
            SovereignCampaignAssessment
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
                "SOVEREIGN_CAMPAIGN"
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
                f"⚠️ Campaign evidence write failed: {exc}"
            )

    def _emit_event(
        self,
        assessment: (
            SovereignCampaignAssessment
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
                "SOVEREIGN_CAMPAIGN_ASSESSMENT"
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
                        "SOVEREIGN_CAMPAIGN_ASSESSMENT"
                    ),
                    payload,
                )

        except Exception as exc:
            print(
                f"⚠️ Campaign event emit failed: {exc}"
            )

    # ==========================================================
    # NORMALIZATION
    # ==========================================================

    def _normalize_signal(
        self,
        item: (
            CampaignSignal
            | Dict[str, Any]
        ),
        *,
        mission_id: Optional[str],
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> CampaignSignal:

        if isinstance(
            item,
            CampaignSignal,
        ):
            return item

        return CampaignSignal(
            campaign_signal_id=str(
                item.get(
                    "campaign_signal_id"
                )
                or uuid.uuid4()
            ),
            campaign_stage=(
                self._safe_stage(
                    item.get(
                        "campaign_stage"
                    )
                )
            ),
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
            attack_coordination_score=(
                self._clamp_score(
                    item.get(
                        "attack_coordination_score",
                        0.0,
                    )
                )
            ),
            propagation_pressure_score=(
                self._clamp_score(
                    item.get(
                        "propagation_pressure_score",
                        0.0,
                    )
                )
            ),
            persistence_pressure_score=(
                self._clamp_score(
                    item.get(
                        "persistence_pressure_score",
                        0.0,
                    )
                )
            ),
            lateral_movement_pressure_score=(
                self._clamp_score(
                    item.get(
                        "lateral_movement_pressure_score",
                        0.0,
                    )
                )
            ),
            privilege_escalation_pressure_score=(
                self._clamp_score(
                    item.get(
                        "privilege_escalation_pressure_score",
                        0.0,
                    )
                )
            ),
            containment_stability_score=(
                self._clamp_score(
                    item.get(
                        "containment_stability_score",
                        100.0,
                    )
                )
            ),
            defense_exhaustion_score=(
                self._clamp_score(
                    item.get(
                        "defense_exhaustion_score",
                        0.0,
                    )
                )
            ),
            resilience_degradation_score=(
                self._clamp_score(
                    item.get(
                        "resilience_degradation_score",
                        0.0,
                    )
                )
            ),
            governance_saturation_score=(
                self._clamp_score(
                    item.get(
                        "governance_saturation_score",
                        0.0,
                    )
                )
            ),
            mission_degradation_score=(
                self._clamp_score(
                    item.get(
                        "mission_degradation_score",
                        0.0,
                    )
                )
            ),
            operational_disruption_score=(
                self._clamp_score(
                    item.get(
                        "operational_disruption_score",
                        0.0,
                    )
                )
            ),
            recovery_interference_score=(
                self._clamp_score(
                    item.get(
                        "recovery_interference_score",
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
    ) -> SovereignCampaignAssessment:

        return (
            SovereignCampaignAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                campaign_state=(
                    CAMPAIGN_STATE_STABLE
                ),
                projected_outcome=(
                    CAMPAIGN_OUTCOME_CONTAINED
                ),
                recommendation=(
                    RECOMMENDATION_MONITOR
                ),
                attack_coordination_score=0.0,
                propagation_pressure_score=0.0,
                persistence_pressure_score=0.0,
                lateral_movement_pressure_score=0.0,
                privilege_escalation_pressure_score=0.0,
                containment_stability_score=100.0,
                defense_exhaustion_score=0.0,
                resilience_degradation_score=0.0,
                governance_saturation_score=0.0,
                mission_degradation_score=0.0,
                operational_disruption_score=0.0,
                recovery_interference_score=0.0,
                uncertainty_score=0.0,
                systemic_risk_probability=0.0,
                containment_probability=1.0,
                mission_survivability_probability=1.0,
                resilience_recovery_probability=1.0,
                campaign_risk_score=0.0,
                explainability_score=100.0,
                campaign_confidence=1.0,
                selected_signal_id=None,
                selected_campaign_stage=None,
                severity=(
                    CampaignSeverity
                    .INFO.value
                ),
                confidence=1.0,
                campaign_depth=0,
                mission_id=mission_id,
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=(
                    correlation_id
                ),
                simulation_steps=[],
                recommended_controls=[
                    (
                        "campaign_lineage_recording"
                    )
                ],
                recommended_actions=[
                    {
                        "action": (
                            "continue_campaign_monitoring"
                        )
                    }
                ],
                rationale=(
                    "No campaign "
                    "signals submitted."
                ),
                metadata={},
            )
        )

    def _select_primary_signal(
        self,
        signals: Sequence[
            CampaignSignal
        ],
    ) -> CampaignSignal:

        return sorted(
            signals,
            key=lambda item: (
                item
                .attack_coordination_score,
                item
                .propagation_pressure_score,
                item
                .persistence_pressure_score,
                -item.created_at_ms,
            ),
            reverse=True,
        )[0]

    # ==========================================================
    # SCORING HELPERS
    # ==========================================================

    def _campaign_confidence(
        self,
        signals: Sequence[
            CampaignSignal
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
            CampaignSignal
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

            if s.campaign_stage:
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

    # ==========================================================
    # HELPERS
    # ==========================================================

    @staticmethod
    def _safe_stage(
        value: Any,
    ) -> str:

        value = str(
            value
            or CampaignStage
            .UNKNOWN.value
        ).upper()

        valid = {
            item.value
            for item in CampaignStage
        }

        return (
            value
            if value in valid
            else CampaignStage
            .UNKNOWN.value
        )

    @staticmethod
    def _safe_domain(
        value: Any,
    ) -> str:

        value = str(
            value
            or CampaignDomain
            .UNKNOWN.value
        ).upper()

        valid = {
            item.value
            for item in CampaignDomain
        }

        return (
            value
            if value in valid
            else CampaignDomain
            .UNKNOWN.value
        )

    @staticmethod
    def _safe_severity(
        value: Any,
    ) -> str:

        value = str(
            value
            or CampaignSeverity
            .INFO.value
        ).upper()

        valid = {
            item.value
            for item in CampaignSeverity
        }

        return (
            value
            if value in valid
            else CampaignSeverity
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


def build_sovereign_autonomous_campaign_engine(
    *,
    event_bus: Optional[Any] = None,
    cyber_defense_simulation_mesh: Optional[
        Any
    ] = None,
    runtime_evolution_engine: Optional[
        Any
    ] = None,
    operational_forecasting_engine: Optional[
        Any
    ] = None,
    operational_memory_engine: Optional[
        Any
    ] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[
        Any
    ] = None,
) -> SovereignAutonomousCampaignEngine:

    return (
        SovereignAutonomousCampaignEngine(
            event_bus=event_bus,
            cyber_defense_simulation_mesh=(
                cyber_defense_simulation_mesh
            ),
            runtime_evolution_engine=(
                runtime_evolution_engine
            ),
            operational_forecasting_engine=(
                operational_forecasting_engine
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