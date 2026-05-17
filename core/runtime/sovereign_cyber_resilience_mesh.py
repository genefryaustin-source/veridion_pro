"""
core/runtime/sovereign_cyber_resilience_mesh.py

Sovereign Cyber Resilience Mesh

Autonomous sovereign survivability cognition layer.

This subsystem coordinates:
- distributed resilience nodes
- continuity mesh orchestration
- resilience redistribution
- stabilization routing
- recovery propagation
- survivability topology
- continuity preservation
- failover cognition

IMPORTANT:
This subsystem DOES NOT:
- execute infrastructure failover
- mutate production infrastructure
- manipulate cloud resources
- alter operational systems
- execute recovery actions

It ONLY:
- models resilience topology
- evaluates survivability conditions
- simulates recovery propagation
- coordinates resilience cognition
- records replayable resilience lineage/evidence
"""

from __future__ import annotations

import statistics
import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


DEFAULT_ENGINE_NAME = (
    "sovereign_cyber_resilience_mesh"
)

DEFAULT_RESILIENCE_DEPTH = 12


RESILIENCE_STATE_STABLE = "STABLE"
RESILIENCE_STATE_DEGRADED = "DEGRADED"
RESILIENCE_STATE_RECOVERING = "RECOVERING"
RESILIENCE_STATE_EXHAUSTED = "EXHAUSTED"
RESILIENCE_STATE_SYSTEMIC_RISK = (
    "SYSTEMIC_RISK"
)

RESILIENCE_OUTCOME_STABILIZED = (
    "STABILIZED"
)
RESILIENCE_OUTCOME_RECOVERING = (
    "RECOVERING"
)
RESILIENCE_OUTCOME_DEGRADED = (
    "DEGRADED"
)
RESILIENCE_OUTCOME_EXHAUSTED = (
    "EXHAUSTED"
)
RESILIENCE_OUTCOME_SYSTEMIC_RISK = (
    "SYSTEMIC_RISK"
)

RECOMMENDATION_MONITOR = "MONITOR"
RECOMMENDATION_RECOVERY_ROUTING = (
    "RECOVERY_ROUTING"
)
RECOMMENDATION_RESILIENCE_REALLOCATION = (
    "RESILIENCE_REALLOCATION"
)
RECOMMENDATION_CONTINUITY_ESCALATION = (
    "CONTINUITY_ESCALATION"
)
RECOMMENDATION_STABILIZATION_SURGE = (
    "STABILIZATION_SURGE"
)
RECOMMENDATION_FAILOVER_COORDINATION = (
    "FAILOVER_COORDINATION"
)


class ResilienceSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ResilienceDomain(str, Enum):
    ENDPOINT = "ENDPOINT"
    CLOUD = "CLOUD"
    NETWORK = "NETWORK"
    IDENTITY = "IDENTITY"
    EMAIL = "EMAIL"
    DATA = "DATA"
    GOVERNANCE = "GOVERNANCE"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    MISSION = "MISSION"
    GLOBAL = "GLOBAL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ResilienceNode:
    node_id: str

    node_name: str
    domain: str

    survivability_score: float
    recovery_capacity_score: float
    continuity_score: float
    stabilization_score: float

    active: bool = True

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class ResilienceSignal:
    resilience_signal_id: str

    source_engine: str
    severity: str
    confidence: float

    summary: str

    mission_id: Optional[str] = None
    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    resilience_pressure_score: float = (
        0.0
    )
    survivability_score: float = 100.0
    recovery_capacity_score: float = (
        100.0
    )
    stabilization_capacity_score: float = (
        100.0
    )
    continuity_mesh_score: float = (
        100.0
    )
    failover_readiness_score: float = (
        100.0
    )
    propagation_resilience_score: float = (
        100.0
    )
    operational_continuity_score: float = (
        100.0
    )
    recovery_velocity_score: float = (
        100.0
    )
    governance_stability_score: float = (
        100.0
    )
    resource_exhaustion_score: float = (
        0.0
    )
    systemic_risk_score: float = 0.0
    uncertainty_score: float = 0.0

    resilience_nodes: List[
        ResilienceNode
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
class ResilienceBranch:
    branch_id: str

    branch_name: str

    projected_state: str
    projected_outcome: str

    stabilization_probability: float
    survivability_probability: float
    continuity_probability: float
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
class ResilienceSimulationStep:
    step_id: str

    step_index: int

    projected_state: str
    projected_outcome: str

    resilience_pressure_score: float
    survivability_score: float
    recovery_capacity_score: float
    stabilization_capacity_score: float
    continuity_mesh_score: float
    failover_readiness_score: float
    propagation_resilience_score: float
    operational_continuity_score: float
    recovery_velocity_score: float
    governance_stability_score: float
    resource_exhaustion_score: float
    systemic_risk_score: float
    uncertainty_score: float

    stabilization_probability: float
    survivability_probability: float
    continuity_probability: float
    systemic_risk_probability: float

    resilience_risk_score: float

    branches: List[
        ResilienceBranch
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
class SovereignResilienceAssessment:
    assessment_id: str

    resilience_state: str
    projected_outcome: str
    recommendation: str

    resilience_pressure_score: float
    survivability_score: float
    recovery_capacity_score: float
    stabilization_capacity_score: float
    continuity_mesh_score: float
    failover_readiness_score: float
    propagation_resilience_score: float
    operational_continuity_score: float
    recovery_velocity_score: float
    governance_stability_score: float
    resource_exhaustion_score: float
    systemic_risk_score: float
    uncertainty_score: float

    stabilization_probability: float
    survivability_probability: float
    continuity_probability: float
    systemic_risk_probability: float

    resilience_risk_score: float

    explainability_score: float
    resilience_confidence: float

    selected_signal_id: Optional[str]

    severity: str
    confidence: float

    resilience_depth: int

    mission_id: Optional[str]
    tenant_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    simulation_steps: List[
        ResilienceSimulationStep
    ]

    resilience_topology: Dict[str, Any]

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


class SovereignCyberResilienceMesh:
    """
    Sovereign autonomous survivability cognition.
    """

    def __init__(
        self,
        *,
        engine_name: str = (
            DEFAULT_ENGINE_NAME
        ),
        event_bus: Optional[Any] = None,
        war_gaming_engine: Optional[Any] = None,
        battle_management_engine: Optional[
            Any
        ] = None,
        digital_twin_engine: Optional[Any] = None,
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

        self.battle_management_engine = (
            battle_management_engine
        )

        self.digital_twin_engine = (
            digital_twin_engine
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
            SovereignResilienceAssessment
        ] = []

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def evaluate(
        self,
        signals: Sequence[
            ResilienceSignal | Dict[str, Any]
        ],
        *,
        resilience_depth: int = (
            DEFAULT_RESILIENCE_DEPTH
        ),
        mission_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> SovereignResilienceAssessment:

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

        resilience_pressure = (
            self._avg_score(
                [
                    s
                    .resilience_pressure_score
                    for s in normalized
                ]
            )
        )

        survivability = (
            self._avg_score(
                [
                    s.survivability_score
                    for s in normalized
                ]
            )
        )

        recovery_capacity = (
            self._avg_score(
                [
                    s
                    .recovery_capacity_score
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

        continuity_mesh = (
            self._avg_score(
                [
                    s
                    .continuity_mesh_score
                    for s in normalized
                ]
            )
        )

        failover_readiness = (
            self._avg_score(
                [
                    s
                    .failover_readiness_score
                    for s in normalized
                ]
            )
        )

        propagation_resilience = (
            self._avg_score(
                [
                    s
                    .propagation_resilience_score
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

        recovery_velocity = (
            self._avg_score(
                [
                    s
                    .recovery_velocity_score
                    for s in normalized
                ]
            )
        )

        governance_stability = (
            self._avg_score(
                [
                    s
                    .governance_stability_score
                    for s in normalized
                ]
            )
        )

        resource_exhaustion = (
            self._avg_score(
                [
                    s
                    .resource_exhaustion_score
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
                survivability_score=(
                    survivability
                ),
                recovery_capacity_score=(
                    recovery_capacity
                ),
                stabilization_capacity_score=(
                    stabilization_capacity
                ),
                continuity_mesh_score=(
                    continuity_mesh
                ),
                operational_continuity_score=(
                    operational_continuity
                ),
                recovery_velocity_score=(
                    recovery_velocity
                ),
                resilience_pressure_score=(
                    resilience_pressure
                ),
                resource_exhaustion_score=(
                    resource_exhaustion
                ),
            )
        )

        survivability_probability = (
            self
            ._survivability_probability(
                survivability_score=(
                    survivability
                ),
                propagation_resilience_score=(
                    propagation_resilience
                ),
                governance_stability_score=(
                    governance_stability
                ),
                systemic_risk_score=(
                    systemic_risk
                ),
            )
        )

        continuity_probability = (
            self
            ._continuity_probability(
                continuity_mesh_score=(
                    continuity_mesh
                ),
                failover_readiness_score=(
                    failover_readiness
                ),
                operational_continuity_score=(
                    operational_continuity
                ),
                recovery_velocity_score=(
                    recovery_velocity
                ),
            )
        )

        systemic_risk_probability = (
            self
            ._systemic_risk_probability(
                resilience_pressure_score=(
                    resilience_pressure
                ),
                resource_exhaustion_score=(
                    resource_exhaustion
                ),
                systemic_risk_score=(
                    systemic_risk
                ),
                uncertainty_score=(
                    uncertainty
                ),
            )
        )

        resilience_risk = (
            self._resilience_risk_score(
                resilience_pressure_score=(
                    resilience_pressure
                ),
                resource_exhaustion_score=(
                    resource_exhaustion
                ),
                systemic_risk_score=(
                    systemic_risk
                ),
                stabilization_probability=(
                    stabilization_probability
                ),
                survivability_probability=(
                    survivability_probability
                ),
                continuity_probability=(
                    continuity_probability
                ),
                systemic_risk_probability=(
                    systemic_risk_probability
                ),
            )
        )

        resilience_state = (
            self._resilience_state(
                resilience_risk_score=(
                    resilience_risk
                ),
                stabilization_probability=(
                    stabilization_probability
                ),
                survivability_probability=(
                    survivability_probability
                ),
                continuity_probability=(
                    continuity_probability
                ),
                systemic_risk_probability=(
                    systemic_risk_probability
                ),
            )
        )

        projected_outcome = (
            self._projected_outcome(
                resilience_state=(
                    resilience_state
                ),
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
                resilience_state=(
                    resilience_state
                ),
                resource_exhaustion_score=(
                    resource_exhaustion
                ),
                continuity_mesh_score=(
                    continuity_mesh
                ),
                failover_readiness_score=(
                    failover_readiness
                ),
            )
        )

        topology = (
            self._build_topology(
                normalized
            )
        )

        steps = (
            self._build_resilience_steps(
                resilience_pressure_score=(
                    resilience_pressure
                ),
                survivability_score=(
                    survivability
                ),
                recovery_capacity_score=(
                    recovery_capacity
                ),
                stabilization_capacity_score=(
                    stabilization_capacity
                ),
                continuity_mesh_score=(
                    continuity_mesh
                ),
                failover_readiness_score=(
                    failover_readiness
                ),
                propagation_resilience_score=(
                    propagation_resilience
                ),
                operational_continuity_score=(
                    operational_continuity
                ),
                recovery_velocity_score=(
                    recovery_velocity
                ),
                governance_stability_score=(
                    governance_stability
                ),
                resource_exhaustion_score=(
                    resource_exhaustion
                ),
                systemic_risk_score=(
                    systemic_risk
                ),
                uncertainty_score=(
                    uncertainty
                ),
                resilience_depth=(
                    resilience_depth
                ),
            )
        )

        assessment = (
            SovereignResilienceAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                resilience_state=(
                    resilience_state
                ),
                projected_outcome=(
                    projected_outcome
                ),
                recommendation=(
                    recommendation
                ),
                resilience_pressure_score=(
                    resilience_pressure
                ),
                survivability_score=(
                    survivability
                ),
                recovery_capacity_score=(
                    recovery_capacity
                ),
                stabilization_capacity_score=(
                    stabilization_capacity
                ),
                continuity_mesh_score=(
                    continuity_mesh
                ),
                failover_readiness_score=(
                    failover_readiness
                ),
                propagation_resilience_score=(
                    propagation_resilience
                ),
                operational_continuity_score=(
                    operational_continuity
                ),
                recovery_velocity_score=(
                    recovery_velocity
                ),
                governance_stability_score=(
                    governance_stability
                ),
                resource_exhaustion_score=(
                    resource_exhaustion
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
                survivability_probability=(
                    survivability_probability
                ),
                continuity_probability=(
                    continuity_probability
                ),
                systemic_risk_probability=(
                    systemic_risk_probability
                ),
                resilience_risk_score=(
                    resilience_risk
                ),
                explainability_score=(
                    self
                    ._explainability_score(
                        normalized
                    )
                ),
                resilience_confidence=(
                    self
                    ._resilience_confidence(
                        normalized
                    )
                ),
                selected_signal_id=(
                    selected
                    .resilience_signal_id
                ),
                severity=(
                    selected.severity
                ),
                confidence=(
                    selected.confidence
                ),
                resilience_depth=(
                    resilience_depth
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
                resilience_topology=(
                    topology
                ),
                recommended_controls=(
                    self
                    ._recommended_controls(
                        resilience_state=(
                            resilience_state
                        ),
                        recommendation=(
                            recommendation
                        ),
                    )
                ),
                recommended_actions=(
                    self
                    ._recommended_actions(
                        resilience_state=(
                            resilience_state
                        ),
                        recommendation=(
                            recommendation
                        ),
                    )
                ),
                rationale=(
                    self._build_rationale(
                        resilience_state=(
                            resilience_state
                        ),
                        projected_outcome=(
                            projected_outcome
                        ),
                        recommendation=(
                            recommendation
                        ),
                        resilience_risk_score=(
                            resilience_risk
                        ),
                        stabilization_probability=(
                            stabilization_probability
                        ),
                        survivability_probability=(
                            survivability_probability
                        ),
                        continuity_probability=(
                            continuity_probability
                        ),
                        systemic_risk_probability=(
                            systemic_risk_probability
                        ),
                        signal_count=len(
                            normalized
                        ),
                        resilience_depth=(
                            resilience_depth
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
            ResilienceSignal
        ],
    ) -> Dict[str, Any]:

        nodes = []

        for signal in signals:
            for node in (
                signal.resilience_nodes
                or []
            ):
                nodes.append(
                    {
                        "node_id": (
                            node.node_id
                        ),
                        "node_name": (
                            node.node_name
                        ),
                        "domain": (
                            node.domain
                        ),
                        "survivability_score": (
                            node
                            .survivability_score
                        ),
                        "recovery_capacity_score": (
                            node
                            .recovery_capacity_score
                        ),
                        "continuity_score": (
                            node
                            .continuity_score
                        ),
                        "stabilization_score": (
                            node
                            .stabilization_score
                        ),
                        "active": (
                            node.active
                        ),
                    }
                )

        return {
            "node_count": len(nodes),
            "nodes": nodes,
            "mesh_state": (
                "CONNECTED"
                if nodes
                else "EMPTY"
            ),
        }

    # ==========================================================
    # SIMULATION
    # ==========================================================

    def _build_resilience_steps(
        self,
        *,
        resilience_pressure_score: float,
        survivability_score: float,
        recovery_capacity_score: float,
        stabilization_capacity_score: float,
        continuity_mesh_score: float,
        failover_readiness_score: float,
        propagation_resilience_score: float,
        operational_continuity_score: float,
        recovery_velocity_score: float,
        governance_stability_score: float,
        resource_exhaustion_score: float,
        systemic_risk_score: float,
        uncertainty_score: float,
        resilience_depth: int,
    ) -> List[ResilienceSimulationStep]:

        steps: List[
            ResilienceSimulationStep
        ] = []

        for idx in range(
            max(1, int(resilience_depth))
        ):

            stabilization_probability = (
                self
                ._stabilization_probability(
                    survivability_score=(
                        survivability_score
                    ),
                    recovery_capacity_score=(
                        recovery_capacity_score
                    ),
                    stabilization_capacity_score=(
                        stabilization_capacity_score
                    ),
                    continuity_mesh_score=(
                        continuity_mesh_score
                    ),
                    operational_continuity_score=(
                        operational_continuity_score
                    ),
                    recovery_velocity_score=(
                        recovery_velocity_score
                    ),
                    resilience_pressure_score=(
                        resilience_pressure_score
                    ),
                    resource_exhaustion_score=(
                        resource_exhaustion_score
                    ),
                )
            )

            survivability_probability = (
                self
                ._survivability_probability(
                    survivability_score=(
                        survivability_score
                    ),
                    propagation_resilience_score=(
                        propagation_resilience_score
                    ),
                    governance_stability_score=(
                        governance_stability_score
                    ),
                    systemic_risk_score=(
                        systemic_risk_score
                    ),
                )
            )

            continuity_probability = (
                self
                ._continuity_probability(
                    continuity_mesh_score=(
                        continuity_mesh_score
                    ),
                    failover_readiness_score=(
                        failover_readiness_score
                    ),
                    operational_continuity_score=(
                        operational_continuity_score
                    ),
                    recovery_velocity_score=(
                        recovery_velocity_score
                    ),
                )
            )

            systemic_risk_probability = (
                self
                ._systemic_risk_probability(
                    resilience_pressure_score=(
                        resilience_pressure_score
                    ),
                    resource_exhaustion_score=(
                        resource_exhaustion_score
                    ),
                    systemic_risk_score=(
                        systemic_risk_score
                    ),
                    uncertainty_score=(
                        uncertainty_score
                    ),
                )
            )

            resilience_risk = (
                self
                ._resilience_risk_score(
                    resilience_pressure_score=(
                        resilience_pressure_score
                    ),
                    resource_exhaustion_score=(
                        resource_exhaustion_score
                    ),
                    systemic_risk_score=(
                        systemic_risk_score
                    ),
                    stabilization_probability=(
                        stabilization_probability
                    ),
                    survivability_probability=(
                        survivability_probability
                    ),
                    continuity_probability=(
                        continuity_probability
                    ),
                    systemic_risk_probability=(
                        systemic_risk_probability
                    ),
                )
            )

            state = (
                self._resilience_state(
                    resilience_risk_score=(
                        resilience_risk
                    ),
                    stabilization_probability=(
                        stabilization_probability
                    ),
                    survivability_probability=(
                        survivability_probability
                    ),
                    continuity_probability=(
                        continuity_probability
                    ),
                    systemic_risk_probability=(
                        systemic_risk_probability
                    ),
                )
            )

            outcome = (
                self._projected_outcome(
                    resilience_state=(
                        state
                    ),
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
                    resilience_state=(
                        state
                    ),
                    stabilization_probability=(
                        stabilization_probability
                    ),
                    survivability_probability=(
                        survivability_probability
                    ),
                    continuity_probability=(
                        continuity_probability
                    ),
                    systemic_risk_probability=(
                        systemic_risk_probability
                    ),
                    resilience_risk_score=(
                        resilience_risk
                    ),
                )
            )

            steps.append(
                ResilienceSimulationStep(
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
                    resilience_pressure_score=(
                        resilience_pressure_score
                    ),
                    survivability_score=(
                        survivability_score
                    ),
                    recovery_capacity_score=(
                        recovery_capacity_score
                    ),
                    stabilization_capacity_score=(
                        stabilization_capacity_score
                    ),
                    continuity_mesh_score=(
                        continuity_mesh_score
                    ),
                    failover_readiness_score=(
                        failover_readiness_score
                    ),
                    propagation_resilience_score=(
                        propagation_resilience_score
                    ),
                    operational_continuity_score=(
                        operational_continuity_score
                    ),
                    recovery_velocity_score=(
                        recovery_velocity_score
                    ),
                    governance_stability_score=(
                        governance_stability_score
                    ),
                    resource_exhaustion_score=(
                        resource_exhaustion_score
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
                    survivability_probability=(
                        survivability_probability
                    ),
                    continuity_probability=(
                        continuity_probability
                    ),
                    systemic_risk_probability=(
                        systemic_risk_probability
                    ),
                    resilience_risk_score=(
                        resilience_risk
                    ),
                    branches=branches,
                    rationale=(
                        f"Resilience "
                        f"simulation step "
                        f"{idx} projected "
                        f"{state}."
                    ),
                )
            )

            resilience_pressure_score = (
                self._clamp_score(
                    resilience_pressure_score
                    + 2.0
                )
            )

            resource_exhaustion_score = (
                self._clamp_score(
                    resource_exhaustion_score
                    + 2.2
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

            survivability_score = (
                self._clamp_score(
                    survivability_score
                    - 1.8
                )
            )

            recovery_capacity_score = (
                self._clamp_score(
                    recovery_capacity_score
                    - 1.7
                )
            )

            stabilization_capacity_score = (
                self._clamp_score(
                    stabilization_capacity_score
                    - 1.6
                )
            )

            continuity_mesh_score = (
                self._clamp_score(
                    continuity_mesh_score
                    - 1.5
                )
            )

            failover_readiness_score = (
                self._clamp_score(
                    failover_readiness_score
                    - 1.4
                )
            )

            propagation_resilience_score = (
                self._clamp_score(
                    propagation_resilience_score
                    - 1.3
                )
            )

            operational_continuity_score = (
                self._clamp_score(
                    operational_continuity_score
                    - 1.2
                )
            )

            recovery_velocity_score = (
                self._clamp_score(
                    recovery_velocity_score
                    - 1.1
                )
            )

        return steps

    def _build_branches(
        self,
        *,
        resilience_state: str,
        stabilization_probability: float,
        survivability_probability: float,
        continuity_probability: float,
        systemic_risk_probability: float,
        resilience_risk_score: float,
    ) -> List[ResilienceBranch]:

        return [
            ResilienceBranch(
                branch_id=str(
                    uuid.uuid4()
                ),
                branch_name=(
                    "adaptive_recovery_path"
                ),
                projected_state=(
                    RESILIENCE_STATE_RECOVERING
                ),
                projected_outcome=(
                    RESILIENCE_OUTCOME_STABILIZED
                ),
                stabilization_probability=(
                    self
                    ._clamp_probability(
                        stabilization_probability
                        + 0.15
                    )
                ),
                survivability_probability=(
                    self
                    ._clamp_probability(
                        survivability_probability
                        + 0.15
                    )
                ),
                continuity_probability=(
                    self
                    ._clamp_probability(
                        continuity_probability
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
                        - resilience_risk_score
                        + 15.0
                    )
                ),
                rationale=(
                    "Projected "
                    "adaptive recovery path."
                ),
            ),
            ResilienceBranch(
                branch_id=str(
                    uuid.uuid4()
                ),
                branch_name=(
                    "continuity_collapse_path"
                ),
                projected_state=(
                    RESILIENCE_STATE_SYSTEMIC_RISK
                ),
                projected_outcome=(
                    RESILIENCE_OUTCOME_SYSTEMIC_RISK
                ),
                stabilization_probability=(
                    self
                    ._clamp_probability(
                        stabilization_probability
                        - 0.20
                    )
                ),
                survivability_probability=(
                    self
                    ._clamp_probability(
                        survivability_probability
                        - 0.20
                    )
                ),
                continuity_probability=(
                    self
                    ._clamp_probability(
                        continuity_probability
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
                        - resilience_risk_score
                        - 20.0
                    )
                ),
                rationale=(
                    "Projected "
                    "continuity collapse path."
                ),
            ),
        ]

    # ==========================================================
    # PROBABILITIES
    # ==========================================================

    def _stabilization_probability(
        self,
        *,
        survivability_score: float,
        recovery_capacity_score: float,
        stabilization_capacity_score: float,
        continuity_mesh_score: float,
        operational_continuity_score: float,
        recovery_velocity_score: float,
        resilience_pressure_score: float,
        resource_exhaustion_score: float,
    ) -> float:

        score = (
            survivability_score
            + recovery_capacity_score
            + stabilization_capacity_score
            + continuity_mesh_score
            + operational_continuity_score
            + recovery_velocity_score
            + (
                100.0
                - resilience_pressure_score
            )
            + (
                100.0
                - resource_exhaustion_score
            )
        ) / 800.0

        return self._clamp_probability(
            score
        )

    def _survivability_probability(
        self,
        *,
        survivability_score: float,
        propagation_resilience_score: float,
        governance_stability_score: float,
        systemic_risk_score: float,
    ) -> float:

        score = (
            survivability_score
            + propagation_resilience_score
            + governance_stability_score
            + (
                100.0
                - systemic_risk_score
            )
        ) / 400.0

        return self._clamp_probability(
            score
        )

    def _continuity_probability(
        self,
        *,
        continuity_mesh_score: float,
        failover_readiness_score: float,
        operational_continuity_score: float,
        recovery_velocity_score: float,
    ) -> float:

        score = (
            continuity_mesh_score
            + failover_readiness_score
            + operational_continuity_score
            + recovery_velocity_score
        ) / 400.0

        return self._clamp_probability(
            score
        )

    def _systemic_risk_probability(
        self,
        *,
        resilience_pressure_score: float,
        resource_exhaustion_score: float,
        systemic_risk_score: float,
        uncertainty_score: float,
    ) -> float:

        risk = (
            resilience_pressure_score
            + resource_exhaustion_score
            + systemic_risk_score
            + uncertainty_score
        ) / 400.0

        return self._clamp_probability(
            risk
        )

    # ==========================================================
    # RISK
    # ==========================================================

    def _resilience_risk_score(
        self,
        *,
        resilience_pressure_score: float,
        resource_exhaustion_score: float,
        systemic_risk_score: float,
        stabilization_probability: float,
        survivability_probability: float,
        continuity_probability: float,
        systemic_risk_probability: float,
    ) -> float:

        risk = (
            resilience_pressure_score
            + resource_exhaustion_score
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
                    - survivability_probability
                )
                * 100.0
            )
            + (
                (
                    1.0
                    - continuity_probability
                )
                * 100.0
            )
            + (
                systemic_risk_probability
                * 100.0
            )
        ) / 7.0

        return self._clamp_score(
            risk
        )

    # ==========================================================
    # STATES
    # ==========================================================

    @staticmethod
    def _resilience_state(
        *,
        resilience_risk_score: float,
        stabilization_probability: float,
        survivability_probability: float,
        continuity_probability: float,
        systemic_risk_probability: float,
    ) -> str:

        if systemic_risk_probability >= 0.8:
            return (
                RESILIENCE_STATE_SYSTEMIC_RISK
            )

        if (
            survivability_probability
            <= 0.35
        ):
            return (
                RESILIENCE_STATE_EXHAUSTED
            )

        if continuity_probability <= 0.40:
            return (
                RESILIENCE_STATE_DEGRADED
            )

        if stabilization_probability <= 0.45:
            return (
                RESILIENCE_STATE_RECOVERING
            )

        return (
            RESILIENCE_STATE_STABLE
        )

    @staticmethod
    def _projected_outcome(
        *,
        resilience_state: str,
        stabilization_probability: float,
        systemic_risk_probability: float,
    ) -> str:

        if (
            resilience_state
            == RESILIENCE_STATE_SYSTEMIC_RISK
        ):
            return (
                RESILIENCE_OUTCOME_SYSTEMIC_RISK
            )

        if stabilization_probability >= 0.75:
            return (
                RESILIENCE_OUTCOME_STABILIZED
            )

        if systemic_risk_probability >= 0.65:
            return (
                RESILIENCE_OUTCOME_EXHAUSTED
            )

        return (
            RESILIENCE_OUTCOME_RECOVERING
        )

    # ==========================================================
    # RECOMMENDATIONS
    # ==========================================================

    @staticmethod
    def _recommendation(
        *,
        resilience_state: str,
        resource_exhaustion_score: float,
        continuity_mesh_score: float,
        failover_readiness_score: float,
    ) -> str:

        if (
            resilience_state
            == RESILIENCE_STATE_SYSTEMIC_RISK
        ):
            return (
                RECOMMENDATION_CONTINUITY_ESCALATION
            )

        if resource_exhaustion_score >= 70:
            return (
                RECOMMENDATION_RESILIENCE_REALLOCATION
            )

        if continuity_mesh_score <= 45:
            return (
                RECOMMENDATION_STABILIZATION_SURGE
            )

        if failover_readiness_score <= 50:
            return (
                RECOMMENDATION_FAILOVER_COORDINATION
            )

        if resilience_state in {
            RESILIENCE_STATE_DEGRADED,
            RESILIENCE_STATE_EXHAUSTED,
        }:
            return (
                RECOMMENDATION_RECOVERY_ROUTING
            )

        return RECOMMENDATION_MONITOR

    @staticmethod
    def _recommended_controls(
        *,
        resilience_state: str,
        recommendation: str,
    ) -> List[str]:

        controls = [
            "resilience_lineage_recording",
            "resilience_evidence_recording",
        ]

        if (
            resilience_state
            != RESILIENCE_STATE_STABLE
        ):
            controls.append(
                "resilience_review"
            )

        if recommendation in {
            RECOMMENDATION_CONTINUITY_ESCALATION,
            RECOMMENDATION_FAILOVER_COORDINATION,
        }:
            controls.append(
                "continuity_review"
            )

        return list(
            dict.fromkeys(controls)
        )

    @staticmethod
    def _recommended_actions(
        *,
        resilience_state: str,
        recommendation: str,
    ) -> List[Dict[str, Any]]:

        return [
            {
                "action": (
                    "record_resilience_lineage"
                )
            },
            {
                "action": (
                    "record_resilience_evidence"
                )
            },
            {
                "action": (
                    "review_resilience_state"
                ),
                "resilience_state": (
                    resilience_state
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
        resilience_state: str,
        projected_outcome: str,
        recommendation: str,
        resilience_risk_score: float,
        stabilization_probability: float,
        survivability_probability: float,
        continuity_probability: float,
        systemic_risk_probability: float,
        signal_count: int,
        resilience_depth: int,
    ) -> str:

        return (
            f"Sovereign resilience mesh "
            f"evaluation processed "
            f"{signal_count} signal(s) "
            f"across resilience depth "
            f"{resilience_depth}. "
            f"Resilience state "
            f"{resilience_state}; "
            f"projected outcome "
            f"{projected_outcome}; "
            f"recommendation "
            f"{recommendation}. "
            f"Resilience risk "
            f"{resilience_risk_score:.2f}; "
            f"stabilization probability "
            f"{stabilization_probability:.2f}; "
            f"survivability probability "
            f"{survivability_probability:.2f}; "
            f"continuity probability "
            f"{continuity_probability:.2f}; "
            f"systemic risk probability "
            f"{systemic_risk_probability:.2f}."
        )

    # ==========================================================
    # RECORDING
    # ==========================================================

    def _record_assessment(
        self,
        assessment: (
            SovereignResilienceAssessment
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
            SovereignResilienceAssessment
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
                "SOVEREIGN_RESILIENCE_ASSESSMENT"
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
                f"⚠️ Resilience memory write failed: {exc}"
            )

    def _write_to_lineage(
        self,
        assessment: (
            SovereignResilienceAssessment
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
                "SOVEREIGN_RESILIENCE"
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
                f"⚠️ Resilience lineage write failed: {exc}"
            )

    def _write_to_evidence(
        self,
        assessment: (
            SovereignResilienceAssessment
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
                "SOVEREIGN_RESILIENCE"
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
                f"⚠️ Resilience evidence write failed: {exc}"
            )

    def _emit_event(
        self,
        assessment: (
            SovereignResilienceAssessment
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
                "SOVEREIGN_RESILIENCE_ASSESSMENT"
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
                        "SOVEREIGN_RESILIENCE_ASSESSMENT"
                    ),
                    payload,
                )

        except Exception as exc:
            print(
                f"⚠️ Resilience event emit failed: {exc}"
            )

    # ==========================================================
    # NORMALIZATION
    # ==========================================================

    def _normalize_signal(
        self,
        item: (
            ResilienceSignal
            | Dict[str, Any]
        ),
        *,
        mission_id: Optional[str],
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> ResilienceSignal:

        if isinstance(
            item,
            ResilienceSignal,
        ):
            return item

        nodes = []

        for node in (
            item.get(
                "resilience_nodes",
                [],
            )
            or []
        ):

            nodes.append(
                ResilienceNode(
                    node_id=str(
                        node.get(
                            "node_id"
                        )
                        or uuid.uuid4()
                    ),
                    node_name=str(
                        node.get(
                            "node_name"
                        )
                        or "unknown_node"
                    ),
                    domain=self._safe_domain(
                        node.get("domain")
                    ),
                    survivability_score=(
                        self._clamp_score(
                            node.get(
                                "survivability_score",
                                100.0,
                            )
                        )
                    ),
                    recovery_capacity_score=(
                        self._clamp_score(
                            node.get(
                                "recovery_capacity_score",
                                100.0,
                            )
                        )
                    ),
                    continuity_score=(
                        self._clamp_score(
                            node.get(
                                "continuity_score",
                                100.0,
                            )
                        )
                    ),
                    stabilization_score=(
                        self._clamp_score(
                            node.get(
                                "stabilization_score",
                                100.0,
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

        return ResilienceSignal(
            resilience_signal_id=str(
                item.get(
                    "resilience_signal_id"
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
            resilience_pressure_score=(
                self._clamp_score(
                    item.get(
                        "resilience_pressure_score",
                        0.0,
                    )
                )
            ),
            survivability_score=(
                self._clamp_score(
                    item.get(
                        "survivability_score",
                        100.0,
                    )
                )
            ),
            recovery_capacity_score=(
                self._clamp_score(
                    item.get(
                        "recovery_capacity_score",
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
            continuity_mesh_score=(
                self._clamp_score(
                    item.get(
                        "continuity_mesh_score",
                        100.0,
                    )
                )
            ),
            failover_readiness_score=(
                self._clamp_score(
                    item.get(
                        "failover_readiness_score",
                        100.0,
                    )
                )
            ),
            propagation_resilience_score=(
                self._clamp_score(
                    item.get(
                        "propagation_resilience_score",
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
            recovery_velocity_score=(
                self._clamp_score(
                    item.get(
                        "recovery_velocity_score",
                        100.0,
                    )
                )
            ),
            governance_stability_score=(
                self._clamp_score(
                    item.get(
                        "governance_stability_score",
                        100.0,
                    )
                )
            ),
            resource_exhaustion_score=(
                self._clamp_score(
                    item.get(
                        "resource_exhaustion_score",
                        0.0,
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
            resilience_nodes=nodes,
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
    ) -> SovereignResilienceAssessment:

        return (
            SovereignResilienceAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                resilience_state=(
                    RESILIENCE_STATE_STABLE
                ),
                projected_outcome=(
                    RESILIENCE_OUTCOME_STABILIZED
                ),
                recommendation=(
                    RECOMMENDATION_MONITOR
                ),
                resilience_pressure_score=0.0,
                survivability_score=100.0,
                recovery_capacity_score=100.0,
                stabilization_capacity_score=100.0,
                continuity_mesh_score=100.0,
                failover_readiness_score=100.0,
                propagation_resilience_score=100.0,
                operational_continuity_score=100.0,
                recovery_velocity_score=100.0,
                governance_stability_score=100.0,
                resource_exhaustion_score=0.0,
                systemic_risk_score=0.0,
                uncertainty_score=0.0,
                stabilization_probability=1.0,
                survivability_probability=1.0,
                continuity_probability=1.0,
                systemic_risk_probability=0.0,
                resilience_risk_score=0.0,
                explainability_score=100.0,
                resilience_confidence=1.0,
                selected_signal_id=None,
                severity=(
                    ResilienceSeverity
                    .INFO.value
                ),
                confidence=1.0,
                resilience_depth=0,
                mission_id=mission_id,
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=(
                    correlation_id
                ),
                simulation_steps=[],
                resilience_topology={
                    "node_count": 0,
                    "nodes": [],
                },
                recommended_controls=[
                    (
                        "resilience_lineage_recording"
                    )
                ],
                recommended_actions=[
                    {
                        "action": (
                            "continue_resilience_monitoring"
                        )
                    }
                ],
                rationale=(
                    "No resilience "
                    "signals submitted."
                ),
                metadata={},
            )
        )

    def _select_primary_signal(
        self,
        signals: Sequence[
            ResilienceSignal
        ],
    ) -> ResilienceSignal:

        return sorted(
            signals,
            key=lambda item: (
                item
                .resilience_pressure_score,
                item
                .resource_exhaustion_score,
                item
                .systemic_risk_score,
                -item.created_at_ms,
            ),
            reverse=True,
        )[0]

    # ==========================================================
    # HELPERS
    # ==========================================================

    def _resilience_confidence(
        self,
        signals: Sequence[
            ResilienceSignal
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
            ResilienceSignal
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

            if s.resilience_nodes:
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
            or ResilienceDomain
            .UNKNOWN.value
        ).upper()

        valid = {
            item.value
            for item in ResilienceDomain
        }

        return (
            value
            if value in valid
            else ResilienceDomain
            .UNKNOWN.value
        )

    @staticmethod
    def _safe_severity(
        value: Any,
    ) -> str:

        value = str(
            value
            or ResilienceSeverity
            .INFO.value
        ).upper()

        valid = {
            item.value
            for item in ResilienceSeverity
        }

        return (
            value
            if value in valid
            else ResilienceSeverity
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


def build_sovereign_cyber_resilience_mesh(
    *,
    event_bus: Optional[Any] = None,
    war_gaming_engine: Optional[Any] = None,
    battle_management_engine: Optional[
        Any
    ] = None,
    digital_twin_engine: Optional[Any] = None,
    operational_memory_engine: Optional[
        Any
    ] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[
        Any
    ] = None,
) -> SovereignCyberResilienceMesh:

    return (
        SovereignCyberResilienceMesh(
            event_bus=event_bus,
            war_gaming_engine=(
                war_gaming_engine
            ),
            battle_management_engine=(
                battle_management_engine
            ),
            digital_twin_engine=(
                digital_twin_engine
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