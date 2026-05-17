"""
core/runtime/sovereign_ecosystem_resilience_engine.py

Sovereign Ecosystem Resilience Engine

Ecosystem-scale sovereign operational resilience cognition.

Models:
- partner ecosystems
- supplier/runtime dependencies
- federated sovereignty boundaries
- ecosystem continuity posture
- cross-organization survivability
- trust-chain degradation
- resilience cascade modeling

IMPORTANT:
This subsystem DOES NOT:
- execute infrastructure changes
- bypass governance
- modify runtime boundaries
- perform offensive operations

It ONLY:
- model ecosystem resilience posture
- evaluate dependency survivability
- simulate resilience degradation
- project federated sovereignty futures
- produce replayable ecosystem lineage/evidence
"""

from __future__ import annotations

import statistics
import time
import uuid

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


DEFAULT_ENGINE_NAME = (
    "sovereign_ecosystem_resilience_engine"
)

DEFAULT_SIMULATION_DEPTH = 10


ECOSYSTEM_STATE_STABLE = "STABLE"

ECOSYSTEM_STATE_MONITORING = (
    "MONITORING"
)

ECOSYSTEM_STATE_DEPENDENCY_PRESSURE = (
    "DEPENDENCY_PRESSURE"
)

ECOSYSTEM_STATE_FEDERATED_RISK = (
    "FEDERATED_RISK"
)

ECOSYSTEM_STATE_CASCADE_RISK = (
    "CASCADE_RISK"
)

ECOSYSTEM_STATE_CONTINUITY_DEGRADATION = (
    "CONTINUITY_DEGRADATION"
)

ECOSYSTEM_STATE_SOVEREIGNTY_DEGRADATION = (
    "SOVEREIGNTY_DEGRADATION"
)

ECOSYSTEM_STATE_CRITICAL = (
    "CRITICAL"
)

PROJECTION_STABLE = "STABLE"

PROJECTION_DEPENDENCY_RECOVERY = (
    "DEPENDENCY_RECOVERY"
)

PROJECTION_CONTINUITY_SHIELD = (
    "CONTINUITY_SHIELD"
)

PROJECTION_FEDERATED_HARDENING = (
    "FEDERATED_HARDENING"
)

PROJECTION_CASCADE_SURVIVAL = (
    "CASCADE_SURVIVAL"
)

PROJECTION_SYSTEMIC_FAILURE = (
    "SYSTEMIC_FAILURE"
)

ACTION_MONITOR = "MONITOR"

ACTION_REBALANCE_DEPENDENCIES = (
    "REBALANCE_DEPENDENCIES"
)

ACTION_REINFORCE_SOVEREIGNTY = (
    "REINFORCE_SOVEREIGNTY"
)

ACTION_CONTINUITY_HARDENING = (
    "CONTINUITY_HARDENING"
)

ACTION_TRUST_CHAIN_REVIEW = (
    "TRUST_CHAIN_REVIEW"
)

ACTION_CASCADE_CONTAINMENT = (
    "CASCADE_CONTAINMENT"
)


class EcosystemSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class EcosystemDependency:
    dependency_id: str

    source_entity: str
    target_entity: str

    dependency_type: str

    tenant_id: Optional[str] = None
    region: Optional[str] = None

    trust_score: float = 100.0
    survivability_score: float = 100.0
    continuity_score: float = 100.0
    sovereignty_score: float = 100.0
    resilience_score: float = 100.0

    criticality_score: float = 0.0

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class EcosystemSignal:
    signal_id: str

    source_engine: str

    severity: str
    confidence: float

    summary: str

    tenant_id: Optional[str] = None
    mission_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    dependency_pressure_score: float = (
        0.0
    )

    continuity_risk_score: float = (
        0.0
    )

    resilience_risk_score: float = (
        0.0
    )

    sovereignty_risk_score: float = (
        0.0
    )

    federated_governance_risk_score: float = (
        0.0
    )

    trust_chain_risk_score: float = (
        0.0
    )

    cascade_risk_score: float = (
        0.0
    )

    uncertainty_score: float = (
        0.0
    )

    dependencies: List[
        EcosystemDependency
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
class EcosystemProjection:
    projection_id: str

    projected_state: str

    dependency_projection_score: float
    continuity_projection_score: float
    sovereignty_projection_score: float
    resilience_projection_score: float
    cascade_projection_score: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class EcosystemSimulationStep:
    step_id: str

    step_index: int

    projected_state: str

    survivability_score: float
    continuity_score: float
    sovereignty_score: float
    resilience_score: float

    dependency_pressure_score: float
    cascade_risk_score: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class EcosystemDirective:
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
class SovereignEcosystemAssessment:
    assessment_id: str

    ecosystem_state: str

    recommended_action: str

    dependency_pressure_score: float
    continuity_risk_score: float
    resilience_risk_score: float
    sovereignty_risk_score: float
    federated_governance_risk_score: float
    trust_chain_risk_score: float
    cascade_risk_score: float
    uncertainty_score: float

    survivability_score: float
    continuity_score: float
    sovereignty_score: float
    resilience_score: float

    ecosystem_risk_score: float

    confidence: float
    explainability_score: float

    dependency_count: int
    organization_count: int
    region_count: int

    severity: str

    tenant_id: Optional[str]
    mission_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    strategic_projection: EcosystemProjection

    simulation_steps: List[
        EcosystemSimulationStep
    ]

    directives: List[
        EcosystemDirective
    ]

    ecosystem_topology: Dict[str, Any]

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


class SovereignEcosystemResilienceEngine:
    """
    Ecosystem-scale sovereign resilience cognition.
    """

    def __init__(
        self,
        *,
        engine_name: str = (
            DEFAULT_ENGINE_NAME
        ),
        event_bus: Optional[Any] = None,
        distributed_runtime_fabric: Optional[
            Any
        ] = None,
        mesh_autonomy_engine: Optional[
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

        self.distributed_runtime_fabric = (
            distributed_runtime_fabric
        )

        self.mesh_autonomy_engine = (
            mesh_autonomy_engine
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
            SovereignEcosystemAssessment
        ] = []

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def evaluate(
        self,
        signals: Sequence[
            EcosystemSignal
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
    ) -> SovereignEcosystemAssessment:

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

        dependencies = (
            self._collect_dependencies(
                normalized
            )
        )

        selected = normalized[0]

        dependency_pressure = (
            self._avg_score(
                [
                    s
                    .dependency_pressure_score
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

        resilience_risk = (
            self._avg_score(
                [
                    s
                    .resilience_risk_score
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

        federated_risk = (
            self._avg_score(
                [
                    s
                    .federated_governance_risk_score
                    for s in normalized
                ]
            )
        )

        trust_chain_risk = (
            self._avg_score(
                [
                    s
                    .trust_chain_risk_score
                    for s in normalized
                ]
            )
        )

        cascade_risk = (
            self._avg_score(
                [
                    s
                    .cascade_risk_score
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
                    d
                    .survivability_score
                    for d in dependencies
                ],
                default=100.0,
            )
        )

        continuity = (
            self._avg_score(
                [
                    d.continuity_score
                    for d in dependencies
                ],
                default=100.0,
            )
        )

        sovereignty = (
            self._avg_score(
                [
                    d.sovereignty_score
                    for d in dependencies
                ],
                default=100.0,
            )
        )

        resilience = (
            self._avg_score(
                [
                    d.resilience_score
                    for d in dependencies
                ],
                default=100.0,
            )
        )

        ecosystem_risk = (
            self._ecosystem_risk_score(
                dependency_pressure_score=(
                    dependency_pressure
                ),
                continuity_risk_score=(
                    continuity_risk
                ),
                resilience_risk_score=(
                    resilience_risk
                ),
                sovereignty_risk_score=(
                    sovereignty_risk
                ),
                federated_governance_risk_score=(
                    federated_risk
                ),
                trust_chain_risk_score=(
                    trust_chain_risk
                ),
                cascade_risk_score=(
                    cascade_risk
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

        ecosystem_state = (
            self._ecosystem_state(
                ecosystem_risk_score=(
                    ecosystem_risk
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
                cascade_risk_score=(
                    cascade_risk
                ),
            )
        )

        recommended_action = (
            self._recommended_action(
                ecosystem_state=(
                    ecosystem_state
                ),
                cascade_risk_score=(
                    cascade_risk
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
                ecosystem_state=(
                    ecosystem_state
                ),
                dependency_pressure_score=(
                    dependency_pressure
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
                cascade_risk_score=(
                    cascade_risk
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
                ecosystem_state=(
                    ecosystem_state
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
                dependency_pressure_score=(
                    dependency_pressure
                ),
                cascade_risk_score=(
                    cascade_risk
                ),
                depth=simulation_depth,
            )
        )

        assessment = (
            SovereignEcosystemAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                ecosystem_state=(
                    ecosystem_state
                ),
                recommended_action=(
                    recommended_action
                ),
                dependency_pressure_score=(
                    dependency_pressure
                ),
                continuity_risk_score=(
                    continuity_risk
                ),
                resilience_risk_score=(
                    resilience_risk
                ),
                sovereignty_risk_score=(
                    sovereignty_risk
                ),
                federated_governance_risk_score=(
                    federated_risk
                ),
                trust_chain_risk_score=(
                    trust_chain_risk
                ),
                cascade_risk_score=(
                    cascade_risk
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
                ecosystem_risk_score=(
                    ecosystem_risk
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
                        dependencies,
                    )
                ),
                dependency_count=len(
                    dependencies
                ),
                organization_count=len(
                    {
                        d.source_entity
                        for d in dependencies
                    }
                ),
                region_count=len(
                    {
                        d.region
                        for d in dependencies
                        if d.region
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
                ecosystem_topology=(
                    self._ecosystem_topology(
                        dependencies
                    )
                ),
                telemetry_fusion=(
                    self._telemetry_fusion(
                        normalized
                    )
                ),
                rationale=(
                    self._rationale(
                        ecosystem_state=(
                            ecosystem_state
                        ),
                        recommended_action=(
                            recommended_action
                        ),
                        ecosystem_risk_score=(
                            ecosystem_risk
                        ),
                    )
                ),
                metadata={
                    "regions": sorted(
                        {
                            d.region
                            for d in dependencies
                            if d.region
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
    def _ecosystem_state(
        *,
        ecosystem_risk_score: float,
        survivability_score: float,
        continuity_score: float,
        sovereignty_score: float,
        cascade_risk_score: float,
    ) -> str:

        if (
            ecosystem_risk_score >= 85
            or survivability_score <= 30
        ):
            return (
                ECOSYSTEM_STATE_CRITICAL
            )

        if cascade_risk_score >= 75:
            return (
                ECOSYSTEM_STATE_CASCADE_RISK
            )

        if sovereignty_score <= 45:
            return (
                ECOSYSTEM_STATE_SOVEREIGNTY_DEGRADATION
            )

        if continuity_score <= 45:
            return (
                ECOSYSTEM_STATE_CONTINUITY_DEGRADATION
            )

        if ecosystem_risk_score >= 60:
            return (
                ECOSYSTEM_STATE_FEDERATED_RISK
            )

        if ecosystem_risk_score >= 40:
            return (
                ECOSYSTEM_STATE_DEPENDENCY_PRESSURE
            )

        if ecosystem_risk_score >= 20:
            return (
                ECOSYSTEM_STATE_MONITORING
            )

        return ECOSYSTEM_STATE_STABLE

    # ==========================================================
    # ACTIONS
    # ==========================================================

    @staticmethod
    def _recommended_action(
        *,
        ecosystem_state: str,
        cascade_risk_score: float,
        sovereignty_risk_score: float,
        continuity_risk_score: float,
    ) -> str:

        if (
            ecosystem_state
            == ECOSYSTEM_STATE_CRITICAL
        ):
            return (
                ACTION_CASCADE_CONTAINMENT
            )

        if cascade_risk_score >= 70:
            return (
                ACTION_CASCADE_CONTAINMENT
            )

        if sovereignty_risk_score >= 60:
            return (
                ACTION_REINFORCE_SOVEREIGNTY
            )

        if continuity_risk_score >= 60:
            return (
                ACTION_CONTINUITY_HARDENING
            )

        if (
            ecosystem_state
            == ECOSYSTEM_STATE_DEPENDENCY_PRESSURE
        ):
            return (
                ACTION_REBALANCE_DEPENDENCIES
            )

        if (
            ecosystem_state
            == ECOSYSTEM_STATE_FEDERATED_RISK
        ):
            return (
                ACTION_TRUST_CHAIN_REVIEW
            )

        return ACTION_MONITOR

    # ==========================================================
    # PROJECTION
    # ==========================================================

    def _projection(
        self,
        *,
        ecosystem_state: str,
        dependency_pressure_score: float,
        continuity_score: float,
        sovereignty_score: float,
        resilience_score: float,
        cascade_risk_score: float,
    ) -> EcosystemProjection:

        state = PROJECTION_STABLE

        if (
            ecosystem_state
            == ECOSYSTEM_STATE_CRITICAL
        ):
            state = (
                PROJECTION_SYSTEMIC_FAILURE
            )

        elif cascade_risk_score >= 70:
            state = (
                PROJECTION_CASCADE_SURVIVAL
            )

        elif sovereignty_score <= 50:
            state = (
                PROJECTION_FEDERATED_HARDENING
            )

        elif continuity_score <= 50:
            state = (
                PROJECTION_CONTINUITY_SHIELD
            )

        elif dependency_pressure_score >= 40:
            state = (
                PROJECTION_DEPENDENCY_RECOVERY
            )

        return EcosystemProjection(
            projection_id=str(
                uuid.uuid4()
            ),
            projected_state=state,
            dependency_projection_score=(
                dependency_pressure_score
            ),
            continuity_projection_score=(
                continuity_score
            ),
            sovereignty_projection_score=(
                sovereignty_score
            ),
            resilience_projection_score=(
                resilience_score
            ),
            cascade_projection_score=(
                cascade_risk_score
            ),
            rationale=(
                f"Ecosystem projection "
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
    ) -> List[EcosystemDirective]:

        return [
            EcosystemDirective(
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
                    f"Recommended action "
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
        ecosystem_state: str,
        survivability_score: float,
        continuity_score: float,
        sovereignty_score: float,
        resilience_score: float,
        dependency_pressure_score: float,
        cascade_risk_score: float,
        depth: int,
    ) -> List[
        EcosystemSimulationStep
    ]:

        steps = []

        for idx in range(max(1, depth)):

            steps.append(
                EcosystemSimulationStep(
                    step_id=str(
                        uuid.uuid4()
                    ),
                    step_index=idx,
                    projected_state=(
                        ecosystem_state
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
                    dependency_pressure_score=(
                        dependency_pressure_score
                    ),
                    cascade_risk_score=(
                        cascade_risk_score
                    ),
                    rationale=(
                        f"Ecosystem "
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

            dependency_pressure_score = (
                self._clamp_score(
                    dependency_pressure_score
                    - 1.0
                )
            )

            cascade_risk_score = (
                self._clamp_score(
                    cascade_risk_score
                    - 1.0
                )
            )

        return steps

    # ==========================================================
    # TOPOLOGY
    # ==========================================================

    def _ecosystem_topology(
        self,
        dependencies: Sequence[
            EcosystemDependency
        ],
    ) -> Dict[str, Any]:

        return {
            "dependency_count": len(
                dependencies
            ),
            "organizations": sorted(
                {
                    d.source_entity
                    for d in dependencies
                }
            ),
            "regions": sorted(
                {
                    d.region
                    for d in dependencies
                    if d.region
                }
            ),
        }

    def _telemetry_fusion(
        self,
        signals: Sequence[
            EcosystemSignal
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
            SovereignEcosystemAssessment
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
                f"⚠️ Ecosystem "
                f"memory write failed: "
                f"{exc}"
            )

    # ==========================================================
    # HELPERS
    # ==========================================================

    def _collect_dependencies(
        self,
        signals: Sequence[
            EcosystemSignal
        ],
    ) -> List[
        EcosystemDependency
    ]:

        dependencies = []

        for signal in signals:
            dependencies.extend(
                signal.dependencies
            )

        return dependencies

    def _ecosystem_risk_score(
        self,
        *,
        dependency_pressure_score: float,
        continuity_risk_score: float,
        resilience_risk_score: float,
        sovereignty_risk_score: float,
        federated_governance_risk_score: float,
        trust_chain_risk_score: float,
        cascade_risk_score: float,
        uncertainty_score: float,
        survivability_score: float,
        continuity_score: float,
        sovereignty_score: float,
    ) -> float:

        risk = (
            dependency_pressure_score
            + continuity_risk_score
            + resilience_risk_score
            + sovereignty_risk_score
            + federated_governance_risk_score
            + trust_chain_risk_score
            + cascade_risk_score
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
            EcosystemSignal
            | Dict[str, Any]
        ),
        *,
        tenant_id: Optional[str],
        mission_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> EcosystemSignal:

        if isinstance(
            item,
            EcosystemSignal,
        ):
            return item

        dependencies = []

        for dep in (
            item.get(
                "dependencies",
                [],
            )
            or []
        ):

            dependencies.append(
                EcosystemDependency(
                    dependency_id=str(
                        dep.get(
                            "dependency_id"
                        )
                        or uuid.uuid4()
                    ),
                    source_entity=str(
                        dep.get(
                            "source_entity",
                            "unknown",
                        )
                    ),
                    target_entity=str(
                        dep.get(
                            "target_entity",
                            "unknown",
                        )
                    ),
                    dependency_type=str(
                        dep.get(
                            "dependency_type",
                            "runtime",
                        )
                    ),
                    tenant_id=(
                        tenant_id
                        or dep.get(
                            "tenant_id"
                        )
                    ),
                    region=dep.get(
                        "region"
                    ),
                    trust_score=self._clamp_score(
                        dep.get(
                            "trust_score",
                            100.0,
                        )
                    ),
                    survivability_score=self._clamp_score(
                        dep.get(
                            "survivability_score",
                            100.0,
                        )
                    ),
                    continuity_score=self._clamp_score(
                        dep.get(
                            "continuity_score",
                            100.0,
                        )
                    ),
                    sovereignty_score=self._clamp_score(
                        dep.get(
                            "sovereignty_score",
                            100.0,
                        )
                    ),
                    resilience_score=self._clamp_score(
                        dep.get(
                            "resilience_score",
                            100.0,
                        )
                    ),
                    criticality_score=self._clamp_score(
                        dep.get(
                            "criticality_score",
                            0.0,
                        )
                    ),
                )
            )

        return EcosystemSignal(
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
            dependency_pressure_score=self._clamp_score(
                item.get(
                    "dependency_pressure_score",
                    0.0,
                )
            ),
            continuity_risk_score=self._clamp_score(
                item.get(
                    "continuity_risk_score",
                    0.0,
                )
            ),
            resilience_risk_score=self._clamp_score(
                item.get(
                    "resilience_risk_score",
                    0.0,
                )
            ),
            sovereignty_risk_score=self._clamp_score(
                item.get(
                    "sovereignty_risk_score",
                    0.0,
                )
            ),
            federated_governance_risk_score=self._clamp_score(
                item.get(
                    "federated_governance_risk_score",
                    0.0,
                )
            ),
            trust_chain_risk_score=self._clamp_score(
                item.get(
                    "trust_chain_risk_score",
                    0.0,
                )
            ),
            cascade_risk_score=self._clamp_score(
                item.get(
                    "cascade_risk_score",
                    0.0,
                )
            ),
            uncertainty_score=self._clamp_score(
                item.get(
                    "uncertainty_score",
                    0.0,
                )
            ),
            dependencies=dependencies,
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
    ) -> SovereignEcosystemAssessment:

        projection = (
            EcosystemProjection(
                projection_id=str(
                    uuid.uuid4()
                ),
                projected_state=(
                    PROJECTION_STABLE
                ),
                dependency_projection_score=0.0,
                continuity_projection_score=100.0,
                sovereignty_projection_score=100.0,
                resilience_projection_score=100.0,
                cascade_projection_score=0.0,
                rationale=(
                    "No ecosystem "
                    "signals submitted."
                ),
            )
        )

        return (
            SovereignEcosystemAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                ecosystem_state=(
                    ECOSYSTEM_STATE_STABLE
                ),
                recommended_action=(
                    ACTION_MONITOR
                ),
                dependency_pressure_score=0.0,
                continuity_risk_score=0.0,
                resilience_risk_score=0.0,
                sovereignty_risk_score=0.0,
                federated_governance_risk_score=0.0,
                trust_chain_risk_score=0.0,
                cascade_risk_score=0.0,
                uncertainty_score=0.0,
                survivability_score=100.0,
                continuity_score=100.0,
                sovereignty_score=100.0,
                resilience_score=100.0,
                ecosystem_risk_score=0.0,
                confidence=1.0,
                explainability_score=100.0,
                dependency_count=0,
                organization_count=0,
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
                ecosystem_topology={},
                telemetry_fusion={},
                rationale=(
                    "No ecosystem "
                    "signals submitted."
                ),
            )
        )

    def _confidence(
        self,
        signals: Sequence[
            EcosystemSignal
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
            EcosystemSignal
        ],
        dependencies: Sequence[
            EcosystemDependency
        ],
    ) -> float:

        explained = 0

        for signal in signals:

            if signal.summary:
                explained += 1

            if signal.source_engine:
                explained += 1

            if signal.dependencies:
                explained += 1

        base = (
            explained
            / max(
                1,
                len(signals) * 3,
            )
        ) * 100.0

        dep_bonus = min(
            10.0,
            len(dependencies)
            * 0.5,
        )

        return self._clamp_score(
            base + dep_bonus
        )

    @staticmethod
    def _rationale(
        *,
        ecosystem_state: str,
        recommended_action: str,
        ecosystem_risk_score: float,
    ) -> str:

        return (
            f"Sovereign ecosystem "
            f"evaluation completed. "
            f"Ecosystem state "
            f"{ecosystem_state}; "
            f"recommended action "
            f"{recommended_action}; "
            f"ecosystem risk score "
            f"{ecosystem_risk_score:.2f}."
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


def build_sovereign_ecosystem_resilience_engine(
    *,
    event_bus: Optional[Any] = None,
    distributed_runtime_fabric: Optional[
        Any
    ] = None,
    mesh_autonomy_engine: Optional[
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
    SovereignEcosystemResilienceEngine
):

    return (
        SovereignEcosystemResilienceEngine(
            event_bus=event_bus,
            distributed_runtime_fabric=(
                distributed_runtime_fabric
            ),
            mesh_autonomy_engine=(
                mesh_autonomy_engine
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