"""
core/runtime/sovereign_operational_simulation_engine.py

Sovereign Operational Simulation Engine

Coordinated sovereign operational simulation orchestration layer.

This subsystem orchestrates:
- digital twin simulations
- chained operational simulations
- survivability simulations
- governance simulations
- failover simulations
- recovery simulations
- containment simulations
- future-state branching simulations
- what-if operational scenarios

IMPORTANT:
This subsystem DOES NOT:
- directly execute runtime actions
- directly mutate infrastructure
- directly perform containment
- directly trigger failovers

It ONLY:
- orchestrates simulation scenarios
- coordinates future-state modeling
- models alternate operational futures
- evaluates survivability strategies
- records replayable simulation lineage/evidence
"""

from __future__ import annotations

import copy
import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


# ============================================================
# CONSTANTS
# ============================================================

DEFAULT_ENGINE_NAME = (
    "sovereign_operational_simulation_engine"
)

SCENARIO_STABLE = "STABLE"
SCENARIO_DEGRADED = "DEGRADED"
SCENARIO_UNSTABLE = "UNSTABLE"
SCENARIO_COLLAPSE = "COLLAPSE"
SCENARIO_RECOVERY = "RECOVERY"

SIMULATION_SUCCESS = "SUCCESS"
SIMULATION_PARTIAL = "PARTIAL"
SIMULATION_FAILURE = "FAILURE"

SIMULATION_TYPE_GOVERNANCE = (
    "GOVERNANCE"
)
SIMULATION_TYPE_FAILOVER = (
    "FAILOVER"
)
SIMULATION_TYPE_RECOVERY = (
    "RECOVERY"
)
SIMULATION_TYPE_SURVIVABILITY = (
    "SURVIVABILITY"
)
SIMULATION_TYPE_CONTAINMENT = (
    "CONTAINMENT"
)
SIMULATION_TYPE_AUTONOMY = (
    "AUTONOMY"
)
SIMULATION_TYPE_RUNTIME = (
    "RUNTIME"
)

DEFAULT_SCENARIO_DEPTH = 5


# ============================================================
# ENUMS
# ============================================================

class SimulationSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SimulationDomain(str, Enum):
    GOVERNANCE = "GOVERNANCE"
    EXECUTION = "EXECUTION"
    AUTONOMY = "AUTONOMY"
    RESILIENCE = "RESILIENCE"
    TELEMETRY = "TELEMETRY"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    CONNECTOR = "CONNECTOR"
    TENANT = "TENANT"
    GLOBAL = "GLOBAL"
    UNKNOWN = "UNKNOWN"


# ============================================================
# DATA MODELS
# ============================================================

@dataclass(frozen=True)
class OperationalSimulationSignal:
    """
    Input simulation signal.
    """

    simulation_signal_id: str

    signal_type: str
    simulation_type: str
    domain: str

    source_engine: str

    severity: str
    confidence: float

    summary: str

    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    governance_pressure_score: float = 0.0
    survivability_risk_score: float = 0.0
    collapse_risk_score: float = 0.0
    resilience_score: float = 100.0

    execution_instability_score: float = 0.0
    telemetry_instability_score: float = 0.0
    infrastructure_instability_score: (
        float
    ) = 0.0
    autonomy_destabilization_score: (
        float
    ) = 0.0

    failover_pressure_score: float = 0.0
    rollback_pressure_score: float = 0.0
    verification_risk_score: float = 0.0

    payload: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


@dataclass(frozen=True)
class SimulationBranch:
    """
    Branching future-state simulation path.
    """

    branch_id: str

    branch_name: str

    projected_state: str

    projected_outcome: str

    survivability_probability: float
    stabilization_probability: float
    recovery_probability: float

    systemic_pressure_score: float

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
class SimulationScenarioStep:
    """
    Individual coordinated simulation step.
    """

    step_id: str

    step_index: int

    simulation_type: str

    projected_state: str

    projected_outcome: str

    governance_pressure_score: float
    survivability_risk_score: float
    collapse_risk_score: float
    resilience_score: float

    execution_instability_score: float
    telemetry_instability_score: float
    infrastructure_instability_score: (
        float
    )
    autonomy_destabilization_score: (
        float
    )

    systemic_pressure_score: float

    branches: List[
        SimulationBranch
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
class SovereignOperationalSimulationAssessment:
    """
    Coordinated simulation assessment.
    """

    assessment_id: str

    simulation_state: str

    projected_outcome: str

    simulation_type: str

    governance_pressure_score: float
    survivability_risk_score: float
    collapse_risk_score: float
    resilience_score: float

    execution_instability_score: float
    telemetry_instability_score: float
    infrastructure_instability_score: (
        float
    )
    autonomy_destabilization_score: (
        float
    )

    systemic_pressure_score: float

    survivability_probability: float
    stabilization_probability: float
    recovery_probability: float

    scenario_depth: int

    selected_signal_id: Optional[str]
    selected_signal_type: Optional[str]

    severity: str
    confidence: float

    tenant_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    scenario_steps: List[
        SimulationScenarioStep
    ]

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
class SovereignOperationalSimulationSnapshot:
    """
    Lightweight diagnostics snapshot.
    """

    engine_name: str

    total_signals_seen: int
    total_assessments_created: int

    last_assessment_id: Optional[str]
    last_simulation_state: Optional[str]
    last_systemic_pressure_score: (
        Optional[float]
    )

    last_updated_ms: int


# ============================================================
# ENGINE
# ============================================================

class SovereignOperationalSimulationEngine:
    """
    Coordinated sovereign simulation orchestration cognition.
    """

    def __init__(
        self,
        *,
        engine_name: str = DEFAULT_ENGINE_NAME,
        event_bus: Optional[Any] = None,
        digital_twin: Optional[Any] = None,
        operational_memory_engine: Optional[
            Any
        ] = None,
        lineage_engine: Optional[Any] = None,
        fedramp_evidence_lineage_engine: (
            Optional[Any]
        ) = None,
    ) -> None:

        self.engine_name = engine_name

        self.event_bus = event_bus

        self.digital_twin = digital_twin

        self.operational_memory_engine = (
            operational_memory_engine
        )

        self.lineage_engine = lineage_engine

        self.fedramp_evidence_lineage_engine = (
            fedramp_evidence_lineage_engine
        )

        self._signals_seen = 0

        self._assessments: List[
            SovereignOperationalSimulationAssessment
        ] = []

    # ========================================================
    # PUBLIC API
    # ========================================================

    def evaluate(
        self,
        signals: Sequence[
            OperationalSimulationSignal
            | Dict[str, Any]
        ],
        *,
        scenario_depth: int = (
            DEFAULT_SCENARIO_DEPTH
        ),
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> (
        SovereignOperationalSimulationAssessment
    ):
        """
        Execute coordinated operational simulation orchestration.
        """

        normalized = [
            self._normalize_signal(
                item,
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=correlation_id,
            )
            for item in signals
        ]

        self._signals_seen += len(normalized)

        if not normalized:

            assessment = (
                self._empty_assessment(
                    tenant_id=tenant_id,
                    case_id=case_id,
                    correlation_id=correlation_id,
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

        governance_pressure = self._avg(
            [
                item
                .governance_pressure_score
                for item in normalized
            ]
        )

        survivability_risk = self._avg(
            [
                item
                .survivability_risk_score
                for item in normalized
            ]
        )

        collapse_risk = self._avg(
            [
                item.collapse_risk_score
                for item in normalized
            ]
        )

        resilience_score = self._avg(
            [
                item.resilience_score
                for item in normalized
            ]
        )

        execution_instability = self._avg(
            [
                item
                .execution_instability_score
                for item in normalized
            ]
        )

        telemetry_instability = self._avg(
            [
                item
                .telemetry_instability_score
                for item in normalized
            ]
        )

        infrastructure_instability = (
            self._avg(
                [
                    item
                    .infrastructure_instability_score
                    for item in normalized
                ]
            )
        )

        autonomy_destabilization = (
            self._avg(
                [
                    item
                    .autonomy_destabilization_score
                    for item in normalized
                ]
            )
        )

        systemic_pressure = (
            self._systemic_pressure(
                governance_pressure=(
                    governance_pressure
                ),
                survivability_risk=(
                    survivability_risk
                ),
                collapse_risk=(
                    collapse_risk
                ),
                execution_instability=(
                    execution_instability
                ),
                telemetry_instability=(
                    telemetry_instability
                ),
                infrastructure_instability=(
                    infrastructure_instability
                ),
                autonomy_destabilization=(
                    autonomy_destabilization
                ),
            )
        )

        simulation_state = (
            self._simulation_state(
                systemic_pressure=(
                    systemic_pressure
                ),
                collapse_risk=(
                    collapse_risk
                ),
                survivability_risk=(
                    survivability_risk
                ),
            )
        )

        projected_outcome = (
            self._projected_outcome(
                simulation_state=(
                    simulation_state
                ),
                collapse_risk=(
                    collapse_risk
                ),
                resilience_score=(
                    resilience_score
                ),
            )
        )

        scenario_steps = (
            self._build_scenario_chain(
                governance_pressure=(
                    governance_pressure
                ),
                survivability_risk=(
                    survivability_risk
                ),
                collapse_risk=(
                    collapse_risk
                ),
                resilience_score=(
                    resilience_score
                ),
                execution_instability=(
                    execution_instability
                ),
                telemetry_instability=(
                    telemetry_instability
                ),
                infrastructure_instability=(
                    infrastructure_instability
                ),
                autonomy_destabilization=(
                    autonomy_destabilization
                ),
                simulation_type=(
                    selected.simulation_type
                ),
                scenario_depth=(
                    scenario_depth
                ),
            )
        )

        survivability_probability = (
            self._survivability_probability(
                survivability_risk=(
                    survivability_risk
                ),
                collapse_risk=(
                    collapse_risk
                ),
            )
        )

        stabilization_probability = (
            self
            ._stabilization_probability(
                governance_pressure=(
                    governance_pressure
                ),
                execution_instability=(
                    execution_instability
                ),
                telemetry_instability=(
                    telemetry_instability
                ),
                infrastructure_instability=(
                    infrastructure_instability
                ),
            )
        )

        recovery_probability = (
            self._recovery_probability(
                resilience_score=(
                    resilience_score
                ),
                collapse_risk=(
                    collapse_risk
                ),
                survivability_risk=(
                    survivability_risk
                ),
            )
        )

        assessment = (
            SovereignOperationalSimulationAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                simulation_state=(
                    simulation_state
                ),
                projected_outcome=(
                    projected_outcome
                ),
                simulation_type=(
                    selected.simulation_type
                ),
                governance_pressure_score=(
                    governance_pressure
                ),
                survivability_risk_score=(
                    survivability_risk
                ),
                collapse_risk_score=(
                    collapse_risk
                ),
                resilience_score=(
                    resilience_score
                ),
                execution_instability_score=(
                    execution_instability
                ),
                telemetry_instability_score=(
                    telemetry_instability
                ),
                infrastructure_instability_score=(
                    infrastructure_instability
                ),
                autonomy_destabilization_score=(
                    autonomy_destabilization
                ),
                systemic_pressure_score=(
                    systemic_pressure
                ),
                survivability_probability=(
                    survivability_probability
                ),
                stabilization_probability=(
                    stabilization_probability
                ),
                recovery_probability=(
                    recovery_probability
                ),
                scenario_depth=(
                    scenario_depth
                ),
                selected_signal_id=(
                    selected
                    .simulation_signal_id
                ),
                selected_signal_type=(
                    selected.signal_type
                ),
                severity=selected.severity,
                confidence=selected.confidence,
                tenant_id=(
                    tenant_id
                    or selected.tenant_id
                ),
                case_id=(
                    case_id
                    or selected.case_id
                ),
                correlation_id=(
                    correlation_id
                    or selected.correlation_id
                ),
                scenario_steps=(
                    scenario_steps
                ),
                recommended_actions=(
                    self._recommended_actions(
                        simulation_state=(
                            simulation_state
                        ),
                        projected_outcome=(
                            projected_outcome
                        ),
                    )
                ),
                rationale=self._build_rationale(
                    simulation_state=(
                        simulation_state
                    ),
                    projected_outcome=(
                        projected_outcome
                    ),
                    systemic_pressure=(
                        systemic_pressure
                    ),
                    governance_pressure=(
                        governance_pressure
                    ),
                    survivability_risk=(
                        survivability_risk
                    ),
                    collapse_risk=(
                        collapse_risk
                    ),
                    resilience_score=(
                        resilience_score
                    ),
                    scenario_depth=(
                        scenario_depth
                    ),
                    signal_count=len(
                        normalized
                    ),
                ),
                metadata={
                    "evaluated_signal_ids": [
                        item
                        .simulation_signal_id
                        for item in normalized
                    ],
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
            OperationalSimulationSignal
            | Dict[str, Any]
        ],
        *,
        scenario_depth: int = (
            DEFAULT_SCENARIO_DEPTH
        ),
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> (
        SovereignOperationalSimulationAssessment
    ):

        return self.evaluate(
            signals,
            scenario_depth=scenario_depth,
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            context=context,
        )

    def get_recent_assessments(
        self,
        *,
        limit: int = 25,
    ) -> List[
        SovereignOperationalSimulationAssessment
    ]:

        limit = max(1, int(limit))

        return list(
            reversed(
                self._assessments[-limit:]
            )
        )

    def snapshot(
        self,
    ) -> (
        SovereignOperationalSimulationSnapshot
    ):

        latest = (
            self._assessments[-1]
            if self._assessments
            else None
        )

        return (
            SovereignOperationalSimulationSnapshot(
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
                last_simulation_state=(
                    latest.simulation_state
                    if latest
                    else None
                ),
                last_systemic_pressure_score=(
                    latest
                    .systemic_pressure_score
                    if latest
                    else None
                ),
                last_updated_ms=int(
                    time.time() * 1000
                ),
            )
        )

    # ========================================================
    # SCENARIO ORCHESTRATION
    # ========================================================

    def _build_scenario_chain(
        self,
        *,
        governance_pressure: float,
        survivability_risk: float,
        collapse_risk: float,
        resilience_score: float,
        execution_instability: float,
        telemetry_instability: float,
        infrastructure_instability: (
            float
        ),
        autonomy_destabilization: (
            float
        ),
        simulation_type: str,
        scenario_depth: int,
    ) -> List[SimulationScenarioStep]:

        steps: List[
            SimulationScenarioStep
        ] = []

        state = {
            "governance_pressure": (
                governance_pressure
            ),
            "survivability_risk": (
                survivability_risk
            ),
            "collapse_risk": (
                collapse_risk
            ),
            "resilience_score": (
                resilience_score
            ),
            "execution_instability": (
                execution_instability
            ),
            "telemetry_instability": (
                telemetry_instability
            ),
            "infrastructure_instability": (
                infrastructure_instability
            ),
            "autonomy_destabilization": (
                autonomy_destabilization
            ),
        }

        for idx in range(
            max(1, scenario_depth)
        ):

            projected_pressure = (
                self._systemic_pressure(
                    governance_pressure=(
                        state[
                            "governance_pressure"
                        ]
                    ),
                    survivability_risk=(
                        state[
                            "survivability_risk"
                        ]
                    ),
                    collapse_risk=(
                        state[
                            "collapse_risk"
                        ]
                    ),
                    execution_instability=(
                        state[
                            "execution_instability"
                        ]
                    ),
                    telemetry_instability=(
                        state[
                            "telemetry_instability"
                        ]
                    ),
                    infrastructure_instability=(
                        state[
                            "infrastructure_instability"
                        ]
                    ),
                    autonomy_destabilization=(
                        state[
                            "autonomy_destabilization"
                        ]
                    ),
                )
            )

            projected_state = (
                self._simulation_state(
                    systemic_pressure=(
                        projected_pressure
                    ),
                    collapse_risk=(
                        state[
                            "collapse_risk"
                        ]
                    ),
                    survivability_risk=(
                        state[
                            "survivability_risk"
                        ]
                    ),
                )
            )

            projected_outcome = (
                self._projected_outcome(
                    simulation_state=(
                        projected_state
                    ),
                    collapse_risk=(
                        state[
                            "collapse_risk"
                        ]
                    ),
                    resilience_score=(
                        state[
                            "resilience_score"
                        ]
                    ),
                )
            )

            branches = (
                self._build_future_branches(
                    projected_state=(
                        projected_state
                    ),
                    projected_pressure=(
                        projected_pressure
                    ),
                    survivability_risk=(
                        state[
                            "survivability_risk"
                        ]
                    ),
                    collapse_risk=(
                        state[
                            "collapse_risk"
                        ]
                    ),
                    resilience_score=(
                        state[
                            "resilience_score"
                        ]
                    ),
                )
            )

            steps.append(
                SimulationScenarioStep(
                    step_id=str(
                        uuid.uuid4()
                    ),
                    step_index=idx,
                    simulation_type=(
                        simulation_type
                    ),
                    projected_state=(
                        projected_state
                    ),
                    projected_outcome=(
                        projected_outcome
                    ),
                    governance_pressure_score=(
                        state[
                            "governance_pressure"
                        ]
                    ),
                    survivability_risk_score=(
                        state[
                            "survivability_risk"
                        ]
                    ),
                    collapse_risk_score=(
                        state[
                            "collapse_risk"
                        ]
                    ),
                    resilience_score=(
                        state[
                            "resilience_score"
                        ]
                    ),
                    execution_instability_score=(
                        state[
                            "execution_instability"
                        ]
                    ),
                    telemetry_instability_score=(
                        state[
                            "telemetry_instability"
                        ]
                    ),
                    infrastructure_instability_score=(
                        state[
                            "infrastructure_instability"
                        ]
                    ),
                    autonomy_destabilization_score=(
                        state[
                            "autonomy_destabilization"
                        ]
                    ),
                    systemic_pressure_score=(
                        projected_pressure
                    ),
                    branches=branches,
                    rationale=(
                        f"Coordinated "
                        f"{simulation_type} "
                        f"simulation step "
                        f"{idx} generated."
                    ),
                )
            )

            state = self._evolve_state(
                state
            )

        return steps

    def _build_future_branches(
        self,
        *,
        projected_state: str,
        projected_pressure: float,
        survivability_risk: float,
        collapse_risk: float,
        resilience_score: float,
    ) -> List[SimulationBranch]:

        return [
            SimulationBranch(
                branch_id=str(
                    uuid.uuid4()
                ),
                branch_name=(
                    "stabilization_path"
                ),
                projected_state=(
                    SCENARIO_RECOVERY
                    if projected_pressure
                    < 60
                    else projected_state
                ),
                projected_outcome=(
                    SIMULATION_SUCCESS
                    if resilience_score
                    > 60
                    else SIMULATION_PARTIAL
                ),
                survivability_probability=(
                    self
                    ._survivability_probability(
                        survivability_risk=(
                            survivability_risk
                        ),
                        collapse_risk=(
                            collapse_risk
                        ),
                    )
                ),
                stabilization_probability=(
                    self
                    ._stabilization_probability(
                        governance_pressure=(
                            projected_pressure
                        ),
                        execution_instability=(
                            projected_pressure
                        ),
                        telemetry_instability=(
                            projected_pressure
                        ),
                        infrastructure_instability=(
                            projected_pressure
                        ),
                    )
                ),
                recovery_probability=(
                    self._recovery_probability(
                        resilience_score=(
                            resilience_score
                        ),
                        collapse_risk=(
                            collapse_risk
                        ),
                        survivability_risk=(
                            survivability_risk
                        ),
                    )
                ),
                systemic_pressure_score=(
                    projected_pressure
                ),
                rationale=(
                    "Projected "
                    "stabilization branch."
                ),
            ),
            SimulationBranch(
                branch_id=str(
                    uuid.uuid4()
                ),
                branch_name=(
                    "collapse_path"
                ),
                projected_state=(
                    SCENARIO_COLLAPSE
                ),
                projected_outcome=(
                    SIMULATION_FAILURE
                ),
                survivability_probability=0.10,
                stabilization_probability=0.05,
                recovery_probability=0.15,
                systemic_pressure_score=(
                    min(
                        100.0,
                        projected_pressure
                        + 20.0,
                    )
                ),
                rationale=(
                    "Projected "
                    "collapse branch."
                ),
            ),
        ]

    def _evolve_state(
        self,
        state: Dict[str, float],
    ) -> Dict[str, float]:

        evolved = copy.deepcopy(state)

        pressure_factor = (
            evolved[
                "collapse_risk"
            ]
            + evolved[
                "survivability_risk"
            ]
        ) / 200.0

        evolved[
            "governance_pressure"
        ] = self._clamp_score(
            evolved[
                "governance_pressure"
            ]
            + (
                pressure_factor * 6
            )
        )

        evolved[
            "execution_instability"
        ] = self._clamp_score(
            evolved[
                "execution_instability"
            ]
            + (
                pressure_factor * 5
            )
        )

        evolved[
            "telemetry_instability"
        ] = self._clamp_score(
            evolved[
                "telemetry_instability"
            ]
            + (
                pressure_factor * 4
            )
        )

        evolved[
            "infrastructure_instability"
        ] = self._clamp_score(
            evolved[
                "infrastructure_instability"
            ]
            + (
                pressure_factor * 5
            )
        )

        evolved[
            "autonomy_destabilization"
        ] = self._clamp_score(
            evolved[
                "autonomy_destabilization"
            ]
            + (
                pressure_factor * 4
            )
        )

        evolved[
            "collapse_risk"
        ] = self._clamp_score(
            evolved[
                "collapse_risk"
            ]
            + (
                pressure_factor * 3
            )
        )

        evolved[
            "survivability_risk"
        ] = self._clamp_score(
            evolved[
                "survivability_risk"
            ]
            + (
                pressure_factor * 2
            )
        )

        evolved[
            "resilience_score"
        ] = self._clamp_score(
            evolved[
                "resilience_score"
            ]
            - (
                pressure_factor * 5
            )
        )

        return evolved

    # ========================================================
    # STATE + PROBABILITIES
    # ========================================================

    def _simulation_state(
        self,
        *,
        systemic_pressure: float,
        collapse_risk: float,
        survivability_risk: float,
    ) -> str:

        if (
            collapse_risk >= 85
            or systemic_pressure >= 90
        ):
            return SCENARIO_COLLAPSE

        if (
            survivability_risk >= 75
            or systemic_pressure >= 75
        ):
            return SCENARIO_UNSTABLE

        if systemic_pressure >= 50:
            return SCENARIO_DEGRADED

        return SCENARIO_STABLE

    def _projected_outcome(
        self,
        *,
        simulation_state: str,
        collapse_risk: float,
        resilience_score: float,
    ) -> str:

        if (
            simulation_state
            == SCENARIO_COLLAPSE
        ):
            return SIMULATION_FAILURE

        if (
            collapse_risk >= 70
            or resilience_score <= 40
        ):
            return SIMULATION_PARTIAL

        return SIMULATION_SUCCESS

    def _survivability_probability(
        self,
        *,
        survivability_risk: float,
        collapse_risk: float,
    ) -> float:

        return self._clamp_probability(
            (
                100
                - (
                    survivability_risk
                    + collapse_risk
                )
                / 2
            )
            / 100.0
        )

    def _stabilization_probability(
        self,
        *,
        governance_pressure: float,
        execution_instability: float,
        telemetry_instability: float,
        infrastructure_instability: (
            float
        ),
    ) -> float:

        avg = (
            governance_pressure
            + execution_instability
            + telemetry_instability
            + infrastructure_instability
        ) / 4.0

        return self._clamp_probability(
            (100 - avg) / 100.0
        )

    def _recovery_probability(
        self,
        *,
        resilience_score: float,
        collapse_risk: float,
        survivability_risk: float,
    ) -> float:

        return self._clamp_probability(
            (
                resilience_score
                - collapse_risk
                - survivability_risk
                + 100
            )
            / 200.0
        )

    # ========================================================
    # HELPERS
    # ========================================================

    def _systemic_pressure(
        self,
        *,
        governance_pressure: float,
        survivability_risk: float,
        collapse_risk: float,
        execution_instability: float,
        telemetry_instability: float,
        infrastructure_instability: (
            float
        ),
        autonomy_destabilization: (
            float
        ),
    ) -> float:

        return self._clamp_score(
            (
                governance_pressure
                + survivability_risk
                + collapse_risk
                + execution_instability
                + telemetry_instability
                + infrastructure_instability
                + autonomy_destabilization
            )
            / 7.0
        )

    def _recommended_actions(
        self,
        *,
        simulation_state: str,
        projected_outcome: str,
    ) -> List[Dict[str, Any]]:

        actions = [
            {
                "action": (
                    "record_simulation_lineage"
                )
            },
            {
                "action": (
                    "record_simulation_evidence"
                )
            },
        ]

        if (
            simulation_state
            == SCENARIO_UNSTABLE
        ):
            actions.append(
                {
                    "action": (
                        "prepare_runtime_stabilization"
                    )
                }
            )

        if (
            simulation_state
            == SCENARIO_COLLAPSE
        ):
            actions.append(
                {
                    "action": (
                        "prepare_emergency_failover"
                    )
                }
            )

        if (
            projected_outcome
            == SIMULATION_PARTIAL
        ):
            actions.append(
                {
                    "action": (
                        "prepare_recovery_strategy"
                    )
                }
            )

        return actions

    def _build_rationale(
        self,
        *,
        simulation_state: str,
        projected_outcome: str,
        systemic_pressure: float,
        governance_pressure: float,
        survivability_risk: float,
        collapse_risk: float,
        resilience_score: float,
        scenario_depth: int,
        signal_count: int,
    ) -> str:

        return (
            f"Sovereign operational "
            f"simulation orchestration "
            f"executed {scenario_depth} "
            f"scenario step(s). "
            f"Simulation state "
            f"{simulation_state}; "
            f"projected outcome "
            f"{projected_outcome}. "
            f"Systemic pressure "
            f"{systemic_pressure:.2f}; "
            f"governance pressure "
            f"{governance_pressure:.2f}; "
            f"survivability risk "
            f"{survivability_risk:.2f}; "
            f"collapse risk "
            f"{collapse_risk:.2f}; "
            f"resilience "
            f"{resilience_score:.2f}. "
            f"Evaluated across "
            f"{signal_count} signal(s)."
        )

    # ========================================================
    # RECORDING
    # ========================================================

    def _record_assessment(
        self,
        assessment: (
            SovereignOperationalSimulationAssessment
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
                    SovereignOperationalSimulationAssessment
            ),
            *,
            context: Optional[
                Dict[str, Any]
            ] = None,
    ) -> None:

        if self.operational_memory_engine is None:
            return

        payload = {
            "type": (
                "SOVEREIGN_OPERATIONAL_SIMULATION_ASSESSMENT"
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

            elif hasattr(
                    self.operational_memory_engine,
                    "record",
            ):
                self.operational_memory_engine.record(
                    payload
                )

        except Exception as exc:
            print(
                f"⚠️ Simulation memory write failed: {exc}"
            )

    def _write_to_lineage(
        self,
        assessment: (
            SovereignOperationalSimulationAssessment
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
                "OPERATIONAL_SIMULATION"
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
                f"⚠️ Simulation lineage write failed: {exc}"
            )

    def _write_to_evidence(
        self,
        assessment: (
            SovereignOperationalSimulationAssessment
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
                "OPERATIONAL_SIMULATION"
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
                f"⚠️ Simulation evidence write failed: {exc}"
            )

    def _emit_event(
        self,
        assessment: (
            SovereignOperationalSimulationAssessment
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
                "SOVEREIGN_OPERATIONAL_SIMULATION_ASSESSMENT"
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
                        "SOVEREIGN_OPERATIONAL_SIMULATION_ASSESSMENT"
                    ),
                    payload,
                )

        except Exception as exc:
            print(
                f"⚠️ Simulation event emit failed: {exc}"
            )

    # ========================================================
    # NORMALIZATION
    # ========================================================

    def _select_primary_signal(
        self,
        signals: Sequence[
            OperationalSimulationSignal
        ],
    ) -> (
        OperationalSimulationSignal
    ):

        return sorted(
            signals,
            key=lambda item: (
                item
                .collapse_risk_score,
                item
                .survivability_risk_score,
                item
                .governance_pressure_score,
                -item.created_at_ms,
            ),
            reverse=True,
        )[0]

    def _normalize_signal(
        self,
        item: (
            OperationalSimulationSignal
            | Dict[str, Any]
        ),
        *,
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> (
        OperationalSimulationSignal
    ):

        if isinstance(
            item,
            OperationalSimulationSignal,
        ):
            return item

        return (
            OperationalSimulationSignal(
                simulation_signal_id=str(
                    item.get(
                        "simulation_signal_id"
                    )
                    or uuid.uuid4()
                ),
                signal_type=str(
                    item.get(
                        "signal_type"
                    )
                    or "UNKNOWN"
                ),
                simulation_type=str(
                    item.get(
                        "simulation_type"
                    )
                    or SIMULATION_TYPE_RUNTIME
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
                    self._clamp_probability(
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
                governance_pressure_score=(
                    self._clamp_score(
                        item.get(
                            "governance_pressure_score",
                            0.0,
                        )
                    )
                ),
                survivability_risk_score=(
                    self._clamp_score(
                        item.get(
                            "survivability_risk_score",
                            0.0,
                        )
                    )
                ),
                collapse_risk_score=(
                    self._clamp_score(
                        item.get(
                            "collapse_risk_score",
                            0.0,
                        )
                    )
                ),
                resilience_score=(
                    self._clamp_score(
                        item.get(
                            "resilience_score",
                            100.0,
                        )
                    )
                ),
                execution_instability_score=(
                    self._clamp_score(
                        item.get(
                            "execution_instability_score",
                            0.0,
                        )
                    )
                ),
                telemetry_instability_score=(
                    self._clamp_score(
                        item.get(
                            "telemetry_instability_score",
                            0.0,
                        )
                    )
                ),
                infrastructure_instability_score=(
                    self._clamp_score(
                        item.get(
                            "infrastructure_instability_score",
                            0.0,
                        )
                    )
                ),
                autonomy_destabilization_score=(
                    self._clamp_score(
                        item.get(
                            "autonomy_destabilization_score",
                            0.0,
                        )
                    )
                ),
                failover_pressure_score=(
                    self._clamp_score(
                        item.get(
                            "failover_pressure_score",
                            0.0,
                        )
                    )
                ),
                rollback_pressure_score=(
                    self._clamp_score(
                        item.get(
                            "rollback_pressure_score",
                            0.0,
                        )
                    )
                ),
                verification_risk_score=(
                    self._clamp_score(
                        item.get(
                            "verification_risk_score",
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
        )

    def _empty_assessment(
        self,
        *,
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> (
        SovereignOperationalSimulationAssessment
    ):

        return (
            SovereignOperationalSimulationAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                simulation_state=(
                    SCENARIO_STABLE
                ),
                projected_outcome=(
                    SIMULATION_SUCCESS
                ),
                simulation_type=(
                    SIMULATION_TYPE_RUNTIME
                ),
                governance_pressure_score=0.0,
                survivability_risk_score=0.0,
                collapse_risk_score=0.0,
                resilience_score=100.0,
                execution_instability_score=0.0,
                telemetry_instability_score=0.0,
                infrastructure_instability_score=0.0,
                autonomy_destabilization_score=0.0,
                systemic_pressure_score=0.0,
                survivability_probability=1.0,
                stabilization_probability=1.0,
                recovery_probability=1.0,
                scenario_depth=0,
                selected_signal_id=None,
                selected_signal_type=None,
                severity=(
                    SimulationSeverity
                    .INFO.value
                ),
                confidence=1.0,
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=correlation_id,
                scenario_steps=[],
                recommended_actions=[
                    {
                        "action": (
                            "continue_runtime_operations"
                        )
                    }
                ],
                rationale=(
                    "No operational "
                    "simulation signals "
                    "submitted."
                ),
                metadata={},
            )
        )

    # ========================================================
    # SAFE HELPERS
    # ========================================================

    @staticmethod
    def _avg(
        values: Sequence[float],
    ) -> float:

        if not values:
            return 0.0

        return max(
            0.0,
            min(
                100.0,
                sum(values)
                / len(values),
            ),
        )

    @staticmethod
    def _safe_domain(
        value: Any,
    ) -> str:

        value = str(
            value
            or SimulationDomain
            .UNKNOWN.value
        ).upper()

        valid = {
            item.value
            for item in (
                SimulationDomain
            )
        }

        return (
            value
            if value in valid
            else (
                SimulationDomain
                .UNKNOWN.value
            )
        )

    @staticmethod
    def _safe_severity(
        value: Any,
    ) -> str:

        value = str(
            value
            or SimulationSeverity
            .INFO.value
        ).upper()

        valid = {
            item.value
            for item in (
                SimulationSeverity
            )
        }

        return (
            value
            if value in valid
            else (
                SimulationSeverity
                .INFO.value
            )
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


# ============================================================
# FACTORY
# ============================================================

def build_sovereign_operational_simulation_engine(
    *,
    event_bus: Optional[Any] = None,
    digital_twin: Optional[Any] = None,
    operational_memory_engine: Optional[
        Any
    ] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: (
        Optional[Any]
    ) = None,
) -> (
    SovereignOperationalSimulationEngine
):
    """
    Factory for explicit dependency injection.
    """

    return (
        SovereignOperationalSimulationEngine(
            event_bus=event_bus,
            digital_twin=digital_twin,
            operational_memory_engine=(
                operational_memory_engine
            ),
            lineage_engine=lineage_engine,
            fedramp_evidence_lineage_engine=(
                fedramp_evidence_lineage_engine
            ),
        )
    )