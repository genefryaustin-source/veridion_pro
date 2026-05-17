"""
core/runtime/sovereign_geopolitical_resilience_engine.py

Sovereign Geopolitical Resilience Engine

Geopolitical-scale sovereign operational cognition layer.

Models:
- geopolitical operational pressure
- regional instability exposure
- cross-border continuity risk
- strategic infrastructure dependencies
- sovereign operational zones
- international resilience posture
- geopolitical survivability futures

IMPORTANT:
This subsystem DOES NOT:
- perform geopolitical operations
- conduct offensive actions
- bypass governance
- manipulate infrastructure
- violate sovereignty boundaries

It ONLY:
- model geopolitical resilience posture
- simulate geopolitical degradation
- evaluate strategic infrastructure survivability
- project continuity restoration futures
- produce replayable geopolitical lineage/evidence
"""

from __future__ import annotations

import statistics
import time
import uuid

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


DEFAULT_ENGINE_NAME = (
    "sovereign_geopolitical_resilience_engine"
)

DEFAULT_SIMULATION_DEPTH = 12


GEOPOLITICAL_STATE_STABLE = "STABLE"

GEOPOLITICAL_STATE_REGIONAL_PRESSURE = (
    "REGIONAL_PRESSURE"
)

GEOPOLITICAL_STATE_INFRASTRUCTURE_STRESS = (
    "INFRASTRUCTURE_STRESS"
)

GEOPOLITICAL_STATE_CONTINUITY_DEGRADATION = (
    "CONTINUITY_DEGRADATION"
)

GEOPOLITICAL_STATE_SOVEREIGNTY_PRESSURE = (
    "SOVEREIGNTY_PRESSURE"
)

GEOPOLITICAL_STATE_CROSS_BORDER_DISRUPTION = (
    "CROSS_BORDER_DISRUPTION"
)

GEOPOLITICAL_STATE_ESCALATION_RISK = (
    "ESCALATION_RISK"
)

GEOPOLITICAL_STATE_GLOBAL_CRITICAL = (
    "GLOBAL_CRITICAL"
)

PROJECTION_STABLE = "STABLE"

PROJECTION_REGIONAL_RECOVERY = (
    "REGIONAL_RECOVERY"
)

PROJECTION_INFRASTRUCTURE_HARDENING = (
    "INFRASTRUCTURE_HARDENING"
)

PROJECTION_CONTINUITY_RESTORATION = (
    "CONTINUITY_RESTORATION"
)

PROJECTION_SOVEREIGN_STABILIZATION = (
    "SOVEREIGN_STABILIZATION"
)

PROJECTION_GLOBAL_RESILIENCE = (
    "GLOBAL_RESILIENCE"
)

PROJECTION_SYSTEMIC_COLLAPSE = (
    "SYSTEMIC_COLLAPSE"
)

ACTION_MONITOR = "MONITOR"

ACTION_HARDEN_INFRASTRUCTURE = (
    "HARDEN_INFRASTRUCTURE"
)

ACTION_REBALANCE_CONTINUITY = (
    "REBALANCE_CONTINUITY"
)

ACTION_REINFORCE_SOVEREIGNTY = (
    "REINFORCE_SOVEREIGNTY"
)

ACTION_CONTAIN_ESCALATION = (
    "CONTAIN_ESCALATION"
)

ACTION_GLOBAL_RESILIENCE_SURGE = (
    "GLOBAL_RESILIENCE_SURGE"
)


class GeopoliticalSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class StrategicInfrastructureNode:
    infrastructure_id: str

    infrastructure_name: str
    infrastructure_type: str

    region: str
    sovereign_zone: str

    tenant_id: Optional[str] = None

    survivability_score: float = (
        100.0
    )

    continuity_score: float = (
        100.0
    )

    sovereignty_score: float = (
        100.0
    )

    resilience_score: float = (
        100.0
    )

    geopolitical_pressure_score: float = (
        0.0
    )

    criticality_score: float = (
        0.0
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class GeopoliticalSignal:
    signal_id: str

    source_engine: str

    severity: str
    confidence: float

    summary: str

    tenant_id: Optional[str] = None
    mission_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    geopolitical_pressure_score: float = (
        0.0
    )

    regional_instability_score: float = (
        0.0
    )

    continuity_risk_score: float = (
        0.0
    )

    sovereignty_risk_score: float = (
        0.0
    )

    infrastructure_risk_score: float = (
        0.0
    )

    cross_border_risk_score: float = (
        0.0
    )

    escalation_risk_score: float = (
        0.0
    )

    uncertainty_score: float = (
        0.0
    )

    infrastructure_nodes: List[
        StrategicInfrastructureNode
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
class GeopoliticalProjection:
    projection_id: str

    projected_state: str

    geopolitical_projection_score: float
    continuity_projection_score: float
    sovereignty_projection_score: float
    infrastructure_projection_score: float
    escalation_projection_score: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class GeopoliticalSimulationStep:
    step_id: str

    step_index: int

    projected_state: str

    survivability_score: float
    continuity_score: float
    sovereignty_score: float
    resilience_score: float

    geopolitical_pressure_score: float
    escalation_risk_score: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class GeopoliticalDirective:
    directive_id: str

    directive_name: str

    action_type: str
    priority: str

    expected_survivability_gain: float
    expected_continuity_gain: float
    expected_sovereignty_gain: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class SovereignGeopoliticalAssessment:
    assessment_id: str

    geopolitical_state: str

    recommended_action: str

    geopolitical_pressure_score: float
    regional_instability_score: float
    continuity_risk_score: float
    sovereignty_risk_score: float
    infrastructure_risk_score: float
    cross_border_risk_score: float
    escalation_risk_score: float
    uncertainty_score: float

    survivability_score: float
    continuity_score: float
    sovereignty_score: float
    resilience_score: float

    geopolitical_risk_score: float

    confidence: float
    explainability_score: float

    infrastructure_count: int
    sovereign_zone_count: int
    region_count: int

    severity: str

    tenant_id: Optional[str]
    mission_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    strategic_projection: GeopoliticalProjection

    simulation_steps: List[
        GeopoliticalSimulationStep
    ]

    directives: List[
        GeopoliticalDirective
    ]

    geopolitical_topology: Dict[str, Any]

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


class SovereignGeopoliticalResilienceEngine:
    """
    Geopolitical-scale sovereign operational cognition.
    """

    def __init__(
        self,
        *,
        engine_name: str = (
            DEFAULT_ENGINE_NAME
        ),
        event_bus: Optional[Any] = None,
        ecosystem_resilience_engine: Optional[
            Any
        ] = None,
        mesh_autonomy_engine: Optional[
            Any
        ] = None,
        distributed_runtime_fabric: Optional[
            Any
        ] = None,
        sovereignty_assurance_engine: Optional[
            Any
        ] = None,
        operational_governor: Optional[
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

        self.ecosystem_resilience_engine = (
            ecosystem_resilience_engine
        )

        self.mesh_autonomy_engine = (
            mesh_autonomy_engine
        )

        self.distributed_runtime_fabric = (
            distributed_runtime_fabric
        )

        self.sovereignty_assurance_engine = (
            sovereignty_assurance_engine
        )

        self.operational_governor = (
            operational_governor
        )

        self.operational_memory_engine = (
            operational_memory_engine
        )

        self.lineage_engine = lineage_engine

        self.fedramp_evidence_lineage_engine = (
            fedramp_evidence_lineage_engine
        )

        self._assessments: List[
            SovereignGeopoliticalAssessment
        ] = []

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def evaluate(
        self,
        signals: Sequence[
            GeopoliticalSignal
            | Dict[str, Any]
        ],
        *,
        simulation_depth: int = (
            DEFAULT_SIMULATION_DEPTH
        ),
        tenant_id: Optional[str] = None,
        mission_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> (
        SovereignGeopoliticalAssessment
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

        infrastructure_nodes = (
            self._collect_nodes(
                normalized
            )
        )

        selected = normalized[0]

        geopolitical_pressure = (
            self._avg_score(
                [
                    s
                    .geopolitical_pressure_score
                    for s in normalized
                ]
            )
        )

        regional_instability = (
            self._avg_score(
                [
                    s
                    .regional_instability_score
                    for s in normalized
                ]
            )
        )

        continuity_risk = (
            self._avg_score(
                [
                    s
                    .continuity_risk_score
                    for s in normalized
                ]
            )
        )

        sovereignty_risk = (
            self._avg_score(
                [
                    s
                    .sovereignty_risk_score
                    for s in normalized
                ]
            )
        )

        infrastructure_risk = (
            self._avg_score(
                [
                    s
                    .infrastructure_risk_score
                    for s in normalized
                ]
            )
        )

        cross_border_risk = (
            self._avg_score(
                [
                    s
                    .cross_border_risk_score
                    for s in normalized
                ]
            )
        )

        escalation_risk = (
            self._avg_score(
                [
                    s
                    .escalation_risk_score
                    for s in normalized
                ]
            )
        )

        uncertainty = (
            self._avg_score(
                [
                    s
                    .uncertainty_score
                    for s in normalized
                ]
            )
        )

        survivability = (
            self._avg_score(
                [
                    n
                    .survivability_score
                    for n in infrastructure_nodes
                ],
                default=100.0,
            )
        )

        continuity = (
            self._avg_score(
                [
                    n.continuity_score
                    for n in infrastructure_nodes
                ],
                default=100.0,
            )
        )

        sovereignty = (
            self._avg_score(
                [
                    n.sovereignty_score
                    for n in infrastructure_nodes
                ],
                default=100.0,
            )
        )

        resilience = (
            self._avg_score(
                [
                    n.resilience_score
                    for n in infrastructure_nodes
                ],
                default=100.0,
            )
        )

        geopolitical_risk = (
            self._geopolitical_risk_score(
                geopolitical_pressure_score=(
                    geopolitical_pressure
                ),
                regional_instability_score=(
                    regional_instability
                ),
                continuity_risk_score=(
                    continuity_risk
                ),
                sovereignty_risk_score=(
                    sovereignty_risk
                ),
                infrastructure_risk_score=(
                    infrastructure_risk
                ),
                cross_border_risk_score=(
                    cross_border_risk
                ),
                escalation_risk_score=(
                    escalation_risk
                ),
                uncertainty_score=(
                    uncertainty
                ),
                survivability_score=(
                    survivability
                ),
                continuity_score=(
                    continuity
                ),
                sovereignty_score=(
                    sovereignty
                ),
            )
        )

        geopolitical_state = (
            self._geopolitical_state(
                geopolitical_risk_score=(
                    geopolitical_risk
                ),
                survivability_score=(
                    survivability
                ),
                continuity_score=(
                    continuity
                ),
                sovereignty_score=(
                    sovereignty
                ),
                escalation_risk_score=(
                    escalation_risk
                ),
            )
        )

        recommended_action = (
            self._recommended_action(
                geopolitical_state=(
                    geopolitical_state
                ),
                escalation_risk_score=(
                    escalation_risk
                ),
                sovereignty_risk_score=(
                    sovereignty_risk
                ),
                continuity_risk_score=(
                    continuity_risk
                ),
            )
        )

        projection = (
            self._projection(
                geopolitical_state=(
                    geopolitical_state
                ),
                geopolitical_pressure_score=(
                    geopolitical_pressure
                ),
                continuity_score=(
                    continuity
                ),
                sovereignty_score=(
                    sovereignty
                ),
                infrastructure_risk_score=(
                    infrastructure_risk
                ),
                escalation_risk_score=(
                    escalation_risk
                ),
            )
        )

        directives = (
            self._directives(
                recommended_action=(
                    recommended_action
                ),
                survivability_score=(
                    survivability
                ),
                continuity_score=(
                    continuity
                ),
                sovereignty_score=(
                    sovereignty
                ),
            )
        )

        steps = (
            self._simulation_steps(
                geopolitical_state=(
                    geopolitical_state
                ),
                survivability_score=(
                    survivability
                ),
                continuity_score=(
                    continuity
                ),
                sovereignty_score=(
                    sovereignty
                ),
                resilience_score=(
                    resilience
                ),
                geopolitical_pressure_score=(
                    geopolitical_pressure
                ),
                escalation_risk_score=(
                    escalation_risk
                ),
                depth=simulation_depth,
            )
        )

        assessment = (
            SovereignGeopoliticalAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                geopolitical_state=(
                    geopolitical_state
                ),
                recommended_action=(
                    recommended_action
                ),
                geopolitical_pressure_score=(
                    geopolitical_pressure
                ),
                regional_instability_score=(
                    regional_instability
                ),
                continuity_risk_score=(
                    continuity_risk
                ),
                sovereignty_risk_score=(
                    sovereignty_risk
                ),
                infrastructure_risk_score=(
                    infrastructure_risk
                ),
                cross_border_risk_score=(
                    cross_border_risk
                ),
                escalation_risk_score=(
                    escalation_risk
                ),
                uncertainty_score=(
                    uncertainty
                ),
                survivability_score=(
                    survivability
                ),
                continuity_score=(
                    continuity
                ),
                sovereignty_score=(
                    sovereignty
                ),
                resilience_score=(
                    resilience
                ),
                geopolitical_risk_score=(
                    geopolitical_risk
                ),
                confidence=(
                    self._confidence(
                        normalized
                    )
                ),
                explainability_score=(
                    self
                    ._explainability_score(
                        normalized,
                        infrastructure_nodes,
                    )
                ),
                infrastructure_count=len(
                    infrastructure_nodes
                ),
                sovereign_zone_count=len(
                    {
                        n.sovereign_zone
                        for n in infrastructure_nodes
                    }
                ),
                region_count=len(
                    {
                        n.region
                        for n in infrastructure_nodes
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
                simulation_steps=(
                    steps
                ),
                directives=(
                    directives
                ),
                geopolitical_topology=(
                    self
                    ._geopolitical_topology(
                        infrastructure_nodes
                    )
                ),
                telemetry_fusion=(
                    self._telemetry_fusion(
                        normalized
                    )
                ),
                rationale=(
                    self._rationale(
                        geopolitical_state=(
                            geopolitical_state
                        ),
                        recommended_action=(
                            recommended_action
                        ),
                        geopolitical_risk_score=(
                            geopolitical_risk
                        ),
                    )
                ),
                metadata={
                    "regions": sorted(
                        {
                            n.region
                            for n in infrastructure_nodes
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
    # STATES
    # ==========================================================

    @staticmethod
    def _geopolitical_state(
        *,
        geopolitical_risk_score: float,
        survivability_score: float,
        continuity_score: float,
        sovereignty_score: float,
        escalation_risk_score: float,
    ) -> str:

        if (
            geopolitical_risk_score >= 85
            or survivability_score <= 30
        ):
            return (
                GEOPOLITICAL_STATE_GLOBAL_CRITICAL
            )

        if escalation_risk_score >= 75:
            return (
                GEOPOLITICAL_STATE_ESCALATION_RISK
            )

        if sovereignty_score <= 45:
            return (
                GEOPOLITICAL_STATE_SOVEREIGNTY_PRESSURE
            )

        if continuity_score <= 45:
            return (
                GEOPOLITICAL_STATE_CONTINUITY_DEGRADATION
            )

        if geopolitical_risk_score >= 60:
            return (
                GEOPOLITICAL_STATE_CROSS_BORDER_DISRUPTION
            )

        if geopolitical_risk_score >= 40:
            return (
                GEOPOLITICAL_STATE_INFRASTRUCTURE_STRESS
            )

        if geopolitical_risk_score >= 20:
            return (
                GEOPOLITICAL_STATE_REGIONAL_PRESSURE
            )

        return GEOPOLITICAL_STATE_STABLE

    # ==========================================================
    # ACTIONS
    # ==========================================================

    @staticmethod
    def _recommended_action(
        *,
        geopolitical_state: str,
        escalation_risk_score: float,
        sovereignty_risk_score: float,
        continuity_risk_score: float,
    ) -> str:

        if (
            geopolitical_state
            == GEOPOLITICAL_STATE_GLOBAL_CRITICAL
        ):
            return (
                ACTION_GLOBAL_RESILIENCE_SURGE
            )

        if escalation_risk_score >= 70:
            return (
                ACTION_CONTAIN_ESCALATION
            )

        if sovereignty_risk_score >= 60:
            return (
                ACTION_REINFORCE_SOVEREIGNTY
            )

        if continuity_risk_score >= 60:
            return (
                ACTION_REBALANCE_CONTINUITY
            )

        if (
            geopolitical_state
            == GEOPOLITICAL_STATE_INFRASTRUCTURE_STRESS
        ):
            return (
                ACTION_HARDEN_INFRASTRUCTURE
            )

        return ACTION_MONITOR

    # ==========================================================
    # PROJECTION
    # ==========================================================

    def _projection(
        self,
        *,
        geopolitical_state: str,
        geopolitical_pressure_score: float,
        continuity_score: float,
        sovereignty_score: float,
        infrastructure_risk_score: float,
        escalation_risk_score: float,
    ) -> GeopoliticalProjection:

        state = PROJECTION_STABLE

        if (
            geopolitical_state
            == GEOPOLITICAL_STATE_GLOBAL_CRITICAL
        ):
            state = (
                PROJECTION_SYSTEMIC_COLLAPSE
            )

        elif escalation_risk_score >= 70:
            state = (
                PROJECTION_GLOBAL_RESILIENCE
            )

        elif sovereignty_score <= 50:
            state = (
                PROJECTION_SOVEREIGN_STABILIZATION
            )

        elif continuity_score <= 50:
            state = (
                PROJECTION_CONTINUITY_RESTORATION
            )

        elif infrastructure_risk_score >= 40:
            state = (
                PROJECTION_INFRASTRUCTURE_HARDENING
            )

        elif geopolitical_pressure_score >= 25:
            state = (
                PROJECTION_REGIONAL_RECOVERY
            )

        return GeopoliticalProjection(
            projection_id=str(
                uuid.uuid4()
            ),
            projected_state=state,
            geopolitical_projection_score=(
                geopolitical_pressure_score
            ),
            continuity_projection_score=(
                continuity_score
            ),
            sovereignty_projection_score=(
                sovereignty_score
            ),
            infrastructure_projection_score=(
                infrastructure_risk_score
            ),
            escalation_projection_score=(
                escalation_risk_score
            ),
            rationale=(
                f"Geopolitical projection "
                f"state {state}."
            ),
        )

    # ==========================================================
    # DIRECTIVES
    # ==========================================================

    def _directives(
        self,
        *,
        recommended_action: str,
        survivability_score: float,
        continuity_score: float,
        sovereignty_score: float,
    ) -> List[
        GeopoliticalDirective
    ]:

        return [
            GeopoliticalDirective(
                directive_id=str(
                    uuid.uuid4()
                ),
                directive_name=(
                    recommended_action.lower()
                ),
                action_type=(
                    recommended_action
                ),
                priority=(
                    "HIGH"
                    if recommended_action
                    != ACTION_MONITOR
                    else "LOW"
                ),
                expected_survivability_gain=(
                    max(
                        0.0,
                        100.0
                        - survivability_score,
                    )
                    * 0.25
                ),
                expected_continuity_gain=(
                    max(
                        0.0,
                        100.0
                        - continuity_score,
                    )
                    * 0.25
                ),
                expected_sovereignty_gain=(
                    max(
                        0.0,
                        100.0
                        - sovereignty_score,
                    )
                    * 0.25
                ),
                rationale=(
                    f"Recommended geopolitical "
                    f"action "
                    f"{recommended_action}."
                ),
            )
        ]

    # ==========================================================
    # SIMULATION
    # ==========================================================

    def _simulation_steps(
        self,
        *,
        geopolitical_state: str,
        survivability_score: float,
        continuity_score: float,
        sovereignty_score: float,
        resilience_score: float,
        geopolitical_pressure_score: float,
        escalation_risk_score: float,
        depth: int,
    ) -> List[
        GeopoliticalSimulationStep
    ]:

        steps = []

        for idx in range(max(1, depth)):

            steps.append(
                GeopoliticalSimulationStep(
                    step_id=str(
                        uuid.uuid4()
                    ),
                    step_index=idx,
                    projected_state=(
                        geopolitical_state
                    ),
                    survivability_score=(
                        survivability_score
                    ),
                    continuity_score=(
                        continuity_score
                    ),
                    sovereignty_score=(
                        sovereignty_score
                    ),
                    resilience_score=(
                        resilience_score
                    ),
                    geopolitical_pressure_score=(
                        geopolitical_pressure_score
                    ),
                    escalation_risk_score=(
                        escalation_risk_score
                    ),
                    rationale=(
                        f"Geopolitical "
                        f"simulation step "
                        f"{idx}."
                    ),
                )
            )

            survivability_score = (
                self._clamp_score(
                    survivability_score
                    + 1.0
                )
            )

            continuity_score = (
                self._clamp_score(
                    continuity_score
                    + 1.0
                )
            )

            sovereignty_score = (
                self._clamp_score(
                    sovereignty_score
                    + 0.8
                )
            )

            resilience_score = (
                self._clamp_score(
                    resilience_score
                    + 0.8
                )
            )

            geopolitical_pressure_score = (
                self._clamp_score(
                    geopolitical_pressure_score
                    - 1.0
                )
            )

            escalation_risk_score = (
                self._clamp_score(
                    escalation_risk_score
                    - 1.0
                )
            )

        return steps

    # ==========================================================
    # TOPOLOGY
    # ==========================================================

    def _geopolitical_topology(
        self,
        infrastructure_nodes: Sequence[
            StrategicInfrastructureNode
        ],
    ) -> Dict[str, Any]:

        return {
            "infrastructure_count": len(
                infrastructure_nodes
            ),
            "regions": sorted(
                {
                    n.region
                    for n in infrastructure_nodes
                }
            ),
            "sovereign_zones": sorted(
                {
                    n.sovereign_zone
                    for n in infrastructure_nodes
                }
            ),
        }

    def _telemetry_fusion(
        self,
        signals: Sequence[
            GeopoliticalSignal
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
        }

    # ==========================================================
    # RECORDING
    # ==========================================================

    def _record_assessment(
        self,
        assessment: (
            SovereignGeopoliticalAssessment
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

        try:

            if (
                self
                .operational_memory_engine
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
                f"⚠️ Geopolitical "
                f"memory write failed: "
                f"{exc}"
            )

    # ==========================================================
    # HELPERS
    # ==========================================================

    def _collect_nodes(
        self,
        signals: Sequence[
            GeopoliticalSignal
        ],
    ) -> List[
        StrategicInfrastructureNode
    ]:

        nodes = []

        for signal in signals:
            nodes.extend(
                signal.infrastructure_nodes
            )

        return nodes

    def _geopolitical_risk_score(
        self,
        *,
        geopolitical_pressure_score: float,
        regional_instability_score: float,
        continuity_risk_score: float,
        sovereignty_risk_score: float,
        infrastructure_risk_score: float,
        cross_border_risk_score: float,
        escalation_risk_score: float,
        uncertainty_score: float,
        survivability_score: float,
        continuity_score: float,
        sovereignty_score: float,
    ) -> float:

        risk = (
            geopolitical_pressure_score
            + regional_instability_score
            + continuity_risk_score
            + sovereignty_risk_score
            + infrastructure_risk_score
            + cross_border_risk_score
            + escalation_risk_score
            + uncertainty_score
            + (
                100.0
                - survivability_score
            )
            + (
                100.0
                - continuity_score
            )
            + (
                100.0
                - sovereignty_score
            )
        ) / 11.0

        return self._clamp_score(
            risk
        )

    def _normalize_signal(
        self,
        item: (
            GeopoliticalSignal
            | Dict[str, Any]
        ),
        *,
        tenant_id: Optional[str],
        mission_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> GeopoliticalSignal:

        if isinstance(
            item,
            GeopoliticalSignal,
        ):
            return item

        nodes = []

        for node in (
            item.get(
                "infrastructure_nodes",
                [],
            )
            or []
        ):

            nodes.append(
                StrategicInfrastructureNode(
                    infrastructure_id=str(
                        node.get(
                            "infrastructure_id"
                        )
                        or uuid.uuid4()
                    ),
                    infrastructure_name=str(
                        node.get(
                            "infrastructure_name",
                            "unknown",
                        )
                    ),
                    infrastructure_type=str(
                        node.get(
                            "infrastructure_type",
                            "runtime",
                        )
                    ),
                    region=str(
                        node.get(
                            "region",
                            "global",
                        )
                    ),
                    sovereign_zone=str(
                        node.get(
                            "sovereign_zone",
                            "default",
                        )
                    ),
                    tenant_id=(
                        tenant_id
                        or node.get(
                            "tenant_id"
                        )
                    ),
                    survivability_score=self._clamp_score(
                        node.get(
                            "survivability_score",
                            100.0,
                        )
                    ),
                    continuity_score=self._clamp_score(
                        node.get(
                            "continuity_score",
                            100.0,
                        )
                    ),
                    sovereignty_score=self._clamp_score(
                        node.get(
                            "sovereignty_score",
                            100.0,
                        )
                    ),
                    resilience_score=self._clamp_score(
                        node.get(
                            "resilience_score",
                            100.0,
                        )
                    ),
                    geopolitical_pressure_score=self._clamp_score(
                        node.get(
                            "geopolitical_pressure_score",
                            0.0,
                        )
                    ),
                    criticality_score=self._clamp_score(
                        node.get(
                            "criticality_score",
                            0.0,
                        )
                    ),
                )
            )

        return GeopoliticalSignal(
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
            severity=str(
                item.get(
                    "severity",
                    "INFO",
                )
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
            geopolitical_pressure_score=self._clamp_score(
                item.get(
                    "geopolitical_pressure_score",
                    0.0,
                )
            ),
            regional_instability_score=self._clamp_score(
                item.get(
                    "regional_instability_score",
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
            infrastructure_risk_score=self._clamp_score(
                item.get(
                    "infrastructure_risk_score",
                    0.0,
                )
            ),
            cross_border_risk_score=self._clamp_score(
                item.get(
                    "cross_border_risk_score",
                    0.0,
                )
            ),
            escalation_risk_score=self._clamp_score(
                item.get(
                    "escalation_risk_score",
                    0.0,
                )
            ),
            uncertainty_score=self._clamp_score(
                item.get(
                    "uncertainty_score",
                    0.0,
                )
            ),
            infrastructure_nodes=nodes,
            payload=dict(
                item.get(
                    "payload",
                    {},
                )
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
        SovereignGeopoliticalAssessment
    ):

        projection = (
            GeopoliticalProjection(
                projection_id=str(
                    uuid.uuid4()
                ),
                projected_state=(
                    PROJECTION_STABLE
                ),
                geopolitical_projection_score=0.0,
                continuity_projection_score=100.0,
                sovereignty_projection_score=100.0,
                infrastructure_projection_score=0.0,
                escalation_projection_score=0.0,
                rationale=(
                    "No geopolitical "
                    "signals submitted."
                ),
            )
        )

        return (
            SovereignGeopoliticalAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                geopolitical_state=(
                    GEOPOLITICAL_STATE_STABLE
                ),
                recommended_action=(
                    ACTION_MONITOR
                ),
                geopolitical_pressure_score=0.0,
                regional_instability_score=0.0,
                continuity_risk_score=0.0,
                sovereignty_risk_score=0.0,
                infrastructure_risk_score=0.0,
                cross_border_risk_score=0.0,
                escalation_risk_score=0.0,
                uncertainty_score=0.0,
                survivability_score=100.0,
                continuity_score=100.0,
                sovereignty_score=100.0,
                resilience_score=100.0,
                geopolitical_risk_score=0.0,
                confidence=1.0,
                explainability_score=100.0,
                infrastructure_count=0,
                sovereign_zone_count=0,
                region_count=0,
                severity="INFO",
                tenant_id=tenant_id,
                mission_id=mission_id,
                case_id=case_id,
                correlation_id=(
                    correlation_id
                ),
                strategic_projection=(
                    projection
                ),
                simulation_steps=[],
                directives=[],
                geopolitical_topology={},
                telemetry_fusion={},
                rationale=(
                    "No geopolitical "
                    "signals submitted."
                ),
            )
        )

    def _confidence(
        self,
        signals: Sequence[
            GeopoliticalSignal
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
            GeopoliticalSignal
        ],
        nodes: Sequence[
            StrategicInfrastructureNode
        ],
    ) -> float:

        explained = 0

        for signal in signals:

            if signal.summary:
                explained += 1

            if signal.source_engine:
                explained += 1

            if signal.infrastructure_nodes:
                explained += 1

        base = (
            explained
            / max(
                1,
                len(signals) * 3,
            )
        ) * 100.0

        node_bonus = min(
            10.0,
            len(nodes) * 0.5,
        )

        return self._clamp_score(
            base + node_bonus
        )

    @staticmethod
    def _rationale(
        *,
        geopolitical_state: str,
        recommended_action: str,
        geopolitical_risk_score: float,
    ) -> str:

        return (
            f"Sovereign geopolitical "
            f"evaluation completed. "
            f"Geopolitical state "
            f"{geopolitical_state}; "
            f"recommended action "
            f"{recommended_action}; "
            f"geopolitical risk score "
            f"{geopolitical_risk_score:.2f}."
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


def build_sovereign_geopolitical_resilience_engine(
    *,
    event_bus: Optional[Any] = None,
    ecosystem_resilience_engine: Optional[
        Any
    ] = None,
    mesh_autonomy_engine: Optional[
        Any
    ] = None,
    distributed_runtime_fabric: Optional[
        Any
    ] = None,
    sovereignty_assurance_engine: Optional[
        Any
    ] = None,
    operational_governor: Optional[
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
    SovereignGeopoliticalResilienceEngine
):

    return (
        SovereignGeopoliticalResilienceEngine(
            event_bus=event_bus,
            ecosystem_resilience_engine=(
                ecosystem_resilience_engine
            ),
            mesh_autonomy_engine=(
                mesh_autonomy_engine
            ),
            distributed_runtime_fabric=(
                distributed_runtime_fabric
            ),
            sovereignty_assurance_engine=(
                sovereignty_assurance_engine
            ),
            operational_governor=(
                operational_governor
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