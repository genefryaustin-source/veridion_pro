"""
core/runtime/sovereign_operational_digital_twin.py

Sovereign Operational Digital Twin

Live sovereign operational simulation cognition layer.

This subsystem models:
- runtime operational topology
- governance posture
- survivability posture
- autonomy posture
- execution posture
- infrastructure posture
- telemetry posture
- operational futures
- instability propagation
- failover propagation
- recovery modeling

IMPORTANT:
This subsystem DOES NOT:
- directly mutate runtime infrastructure
- directly execute containment
- directly trigger failovers
- directly execute governance actions

It ONLY:
- simulates operational futures
- models runtime state evolution
- models survivability outcomes
- models governance outcomes
- models adaptation outcomes
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
    "sovereign_operational_digital_twin"
)

SIMULATION_STABLE = "STABLE"
SIMULATION_DEGRADED = "DEGRADED"
SIMULATION_UNSTABLE = "UNSTABLE"
SIMULATION_COLLAPSE = "COLLAPSE"
SIMULATION_RECOVERY = "RECOVERY"

OUTCOME_SUCCESS = "SUCCESS"
OUTCOME_PARTIAL = "PARTIAL"
OUTCOME_FAILURE = "FAILURE"

RECOMMENDATION_NONE = "NONE"
RECOMMENDATION_STABILIZE = (
    "STABILIZE_RUNTIME"
)
RECOMMENDATION_RESTRICT_AUTONOMY = (
    "RESTRICT_AUTONOMY"
)
RECOMMENDATION_PREPARE_FAILOVER = (
    "PREPARE_FAILOVER"
)
RECOMMENDATION_ENABLE_SURVIVABILITY = (
    "ENABLE_SURVIVABILITY_MODE"
)
RECOMMENDATION_LOCKDOWN = (
    "ENABLE_LOCKDOWN"
)
RECOMMENDATION_RECOVERY = (
    "RECOVERY_RECOMMENDED"
)

DEFAULT_SIMULATION_HORIZON = 5


# ============================================================
# ENUMS
# ============================================================

class TwinDomain(str, Enum):
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


class TwinSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ============================================================
# DATA MODELS
# ============================================================

@dataclass(frozen=True)
class OperationalTwinSignal:
    """
    Input operational signal for simulation.
    """

    twin_signal_id: str

    signal_type: str
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
class TwinSimulationStep:
    """
    Individual simulation step.
    """

    step_id: str

    step_index: int

    simulation_state: str

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

    projected_outcome: str

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
class SovereignOperationalTwinAssessment:
    """
    Digital twin assessment.
    """

    assessment_id: str

    simulation_state: str

    projected_outcome: str

    recommendation: str

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

    recovery_probability: float
    survivability_probability: float
    stabilization_probability: float

    projected_horizon_steps: int

    selected_signal_id: Optional[str]
    selected_signal_type: Optional[str]

    severity: str
    confidence: float

    tenant_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    simulation_steps: List[
        TwinSimulationStep
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
class SovereignOperationalDigitalTwinSnapshot:
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

class SovereignOperationalDigitalTwin:
    """
    Sovereign operational simulation cognition.
    """

    def __init__(
        self,
        *,
        engine_name: str = DEFAULT_ENGINE_NAME,
        event_bus: Optional[Any] = None,
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

        self.operational_memory_engine = (
            operational_memory_engine
        )

        self.lineage_engine = lineage_engine

        self.fedramp_evidence_lineage_engine = (
            fedramp_evidence_lineage_engine
        )

        self._signals_seen = 0

        self._assessments: List[
            SovereignOperationalTwinAssessment
        ] = []

    # ========================================================
    # PUBLIC API
    # ========================================================

    def evaluate(
        self,
        signals: Sequence[
            OperationalTwinSignal
            | Dict[str, Any]
        ],
        *,
        simulation_horizon: int = (
            DEFAULT_SIMULATION_HORIZON
        ),
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> (
        SovereignOperationalTwinAssessment
    ):
        """
        Simulate operational future states.
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

        recommendation = (
            self._recommendation(
                simulation_state=(
                    simulation_state
                ),
                projected_outcome=(
                    projected_outcome
                ),
                collapse_risk=(
                    collapse_risk
                ),
                survivability_risk=(
                    survivability_risk
                ),
            )
        )

        simulation_steps = (
            self._simulate_future_steps(
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
                horizon=simulation_horizon,
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

        assessment = (
            SovereignOperationalTwinAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                simulation_state=(
                    simulation_state
                ),
                projected_outcome=(
                    projected_outcome
                ),
                recommendation=(
                    recommendation
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
                recovery_probability=(
                    recovery_probability
                ),
                survivability_probability=(
                    survivability_probability
                ),
                stabilization_probability=(
                    stabilization_probability
                ),
                projected_horizon_steps=(
                    simulation_horizon
                ),
                selected_signal_id=(
                    selected
                    .twin_signal_id
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
                simulation_steps=(
                    simulation_steps
                ),
                recommended_controls=(
                    self
                    ._recommended_controls(
                        recommendation=(
                            recommendation
                        ),
                        simulation_state=(
                            simulation_state
                        ),
                    )
                ),
                recommended_actions=(
                    self._recommended_actions(
                        recommendation=(
                            recommendation
                        ),
                        simulation_state=(
                            simulation_state
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
                    recommendation=(
                        recommendation
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
                    systemic_pressure=(
                        systemic_pressure
                    ),
                    recovery_probability=(
                        recovery_probability
                    ),
                    survivability_probability=(
                        survivability_probability
                    ),
                    stabilization_probability=(
                        stabilization_probability
                    ),
                    horizon=(
                        simulation_horizon
                    ),
                    signal_count=len(
                        normalized
                    ),
                ),
                metadata={
                    "evaluated_signal_ids": [
                        item.twin_signal_id
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
            OperationalTwinSignal
            | Dict[str, Any]
        ],
        *,
        simulation_horizon: int = (
            DEFAULT_SIMULATION_HORIZON
        ),
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> (
        SovereignOperationalTwinAssessment
    ):

        return self.evaluate(
            signals,
            simulation_horizon=(
                simulation_horizon
            ),
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
        SovereignOperationalTwinAssessment
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
        SovereignOperationalDigitalTwinSnapshot
    ):

        latest = (
            self._assessments[-1]
            if self._assessments
            else None
        )

        return (
            SovereignOperationalDigitalTwinSnapshot(
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
    # SIMULATION
    # ========================================================

    def _simulate_future_steps(
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
        horizon: int,
    ) -> List[TwinSimulationStep]:

        steps: List[
            TwinSimulationStep
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
            max(1, horizon)
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

            simulation_state = (
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

            outcome = (
                self._projected_outcome(
                    simulation_state=(
                        simulation_state
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
                TwinSimulationStep(
                    step_id=str(
                        uuid.uuid4()
                    ),
                    step_index=idx,
                    simulation_state=(
                        simulation_state
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
                    projected_outcome=(
                        outcome
                    ),
                    rationale=(
                        f"Projected "
                        f"{simulation_state} "
                        f"runtime posture "
                        f"at simulation step "
                        f"{idx}."
                    ),
                )
            )

            state = self._evolve_state(
                state
            )

        return steps

    def _evolve_state(
        self,
        state: Dict[str, float],
    ) -> Dict[str, float]:

        evolved = copy.deepcopy(state)

        collapse_risk = evolved[
            "collapse_risk"
        ]

        survivability_risk = evolved[
            "survivability_risk"
        ]

        resilience = evolved[
            "resilience_score"
        ]

        pressure_factor = (
            collapse_risk
            + survivability_risk
        ) / 200.0

        evolved[
            "governance_pressure"
        ] = self._clamp_score(
            evolved[
                "governance_pressure"
            ]
            + (
                pressure_factor * 6.0
            )
        )

        evolved[
            "execution_instability"
        ] = self._clamp_score(
            evolved[
                "execution_instability"
            ]
            + (
                pressure_factor * 5.0
            )
        )

        evolved[
            "telemetry_instability"
        ] = self._clamp_score(
            evolved[
                "telemetry_instability"
            ]
            + (
                pressure_factor * 4.0
            )
        )

        evolved[
            "infrastructure_instability"
        ] = self._clamp_score(
            evolved[
                "infrastructure_instability"
            ]
            + (
                pressure_factor * 5.0
            )
        )

        evolved[
            "autonomy_destabilization"
        ] = self._clamp_score(
            evolved[
                "autonomy_destabilization"
            ]
            + (
                pressure_factor * 4.0
            )
        )

        evolved[
            "collapse_risk"
        ] = self._clamp_score(
            collapse_risk
            + (
                pressure_factor * 3.5
            )
        )

        evolved[
            "survivability_risk"
        ] = self._clamp_score(
            survivability_risk
            + (
                pressure_factor * 2.5
            )
        )

        evolved[
            "resilience_score"
        ] = self._clamp_score(
            resilience
            - (
                pressure_factor * 5.0
            )
        )

        return evolved

    # ========================================================
    # STATE
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
            return SIMULATION_COLLAPSE

        if (
            survivability_risk >= 75
            or systemic_pressure >= 75
        ):
            return SIMULATION_UNSTABLE

        if systemic_pressure >= 50:
            return SIMULATION_DEGRADED

        return SIMULATION_STABLE

    def _projected_outcome(
        self,
        *,
        simulation_state: str,
        collapse_risk: float,
        resilience_score: float,
    ) -> str:

        if (
            simulation_state
            == SIMULATION_COLLAPSE
        ):
            return OUTCOME_FAILURE

        if (
            collapse_risk >= 70
            or resilience_score <= 40
        ):
            return OUTCOME_PARTIAL

        return OUTCOME_SUCCESS

    def _recommendation(
        self,
        *,
        simulation_state: str,
        projected_outcome: str,
        collapse_risk: float,
        survivability_risk: float,
    ) -> str:

        if (
            simulation_state
            == SIMULATION_COLLAPSE
        ):
            return (
                RECOMMENDATION_LOCKDOWN
            )

        if (
            simulation_state
            == SIMULATION_UNSTABLE
        ):
            return (
                RECOMMENDATION_ENABLE_SURVIVABILITY
            )

        if collapse_risk >= 70:
            return (
                RECOMMENDATION_PREPARE_FAILOVER
            )

        if survivability_risk >= 60:
            return (
                RECOMMENDATION_STABILIZE
            )

        if (
            projected_outcome
            == OUTCOME_PARTIAL
        ):
            return (
                RECOMMENDATION_RECOVERY
            )

        return RECOMMENDATION_NONE

    # ========================================================
    # PROBABILITIES
    # ========================================================

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

    def _recommended_controls(
        self,
        *,
        recommendation: str,
        simulation_state: str,
    ) -> List[str]:

        controls = [
            "lineage_recording",
            "evidence_recording",
        ]

        if (
            simulation_state
            != SIMULATION_STABLE
        ):
            controls.append(
                "operator_review"
            )

        if recommendation in {
            RECOMMENDATION_LOCKDOWN,
            RECOMMENDATION_PREPARE_FAILOVER,
        }:
            controls.append(
                "governance_review"
            )

        return list(
            dict.fromkeys(controls)
        )

    def _recommended_actions(
        self,
        *,
        recommendation: str,
        simulation_state: str,
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
            recommendation
            != RECOMMENDATION_NONE
        ):
            actions.append(
                {
                    "action": (
                        "review_simulation_posture"
                    ),
                    "recommendation": (
                        recommendation
                    ),
                }
            )

        if (
            simulation_state
            == SIMULATION_UNSTABLE
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
            == SIMULATION_COLLAPSE
        ):
            actions.append(
                {
                    "action": (
                        "prepare_emergency_controls"
                    )
                }
            )

        return actions

    def _build_rationale(
        self,
        *,
        simulation_state: str,
        projected_outcome: str,
        recommendation: str,
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
        systemic_pressure: float,
        recovery_probability: float,
        survivability_probability: (
            float
        ),
        stabilization_probability: (
            float
        ),
        horizon: int,
        signal_count: int,
    ) -> str:

        return (
            f"Sovereign operational "
            f"digital twin simulated "
            f"{horizon} future runtime "
            f"step(s). "
            f"Simulation state "
            f"{simulation_state}; "
            f"projected outcome "
            f"{projected_outcome}; "
            f"recommendation "
            f"{recommendation}. "
            f"Governance pressure "
            f"{governance_pressure:.2f}; "
            f"survivability risk "
            f"{survivability_risk:.2f}; "
            f"collapse risk "
            f"{collapse_risk:.2f}; "
            f"resilience "
            f"{resilience_score:.2f}; "
            f"execution instability "
            f"{execution_instability:.2f}; "
            f"telemetry instability "
            f"{telemetry_instability:.2f}; "
            f"infrastructure instability "
            f"{infrastructure_instability:.2f}; "
            f"autonomy destabilization "
            f"{autonomy_destabilization:.2f}; "
            f"systemic pressure "
            f"{systemic_pressure:.2f}. "
            f"Recovery probability "
            f"{recovery_probability:.2f}; "
            f"survivability probability "
            f"{survivability_probability:.2f}; "
            f"stabilization probability "
            f"{stabilization_probability:.2f}. "
            f"Evaluated across "
            f"{signal_count} signal(s)."
        )

    def _record_assessment(
        self,
        assessment: (
            SovereignOperationalTwinAssessment
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

    # ========================================================
    # RECORDING
    # ========================================================

    def _write_to_memory(
        self,
        assessment: (
            SovereignOperationalTwinAssessment
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
                "SOVEREIGN_OPERATIONAL_DIGITAL_TWIN_ASSESSMENT"
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
                self
                .operational_memory_engine,
                "append_memory",
            ):
                self.operational_memory_engine.append_memory(
                    payload
                )

            elif hasattr(
                self
                .operational_memory_engine,
                "record",
            ):
                self.operational_memory_engine.record(
                    payload
                )

        except Exception as exc:
            print(
                f"⚠️ Twin memory write failed: {exc}"
            )

    def _write_to_lineage(
        self,
        assessment: (
            SovereignOperationalTwinAssessment
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
                "DIGITAL_TWIN"
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
                f"⚠️ Twin lineage write failed: {exc}"
            )

    def _write_to_evidence(
        self,
        assessment: (
            SovereignOperationalTwinAssessment
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
                "DIGITAL_TWIN"
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
                f"⚠️ Twin evidence write failed: {exc}"
            )

    def _emit_event(
        self,
        assessment: (
            SovereignOperationalTwinAssessment
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
                "SOVEREIGN_OPERATIONAL_DIGITAL_TWIN_ASSESSMENT"
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
                        "SOVEREIGN_OPERATIONAL_DIGITAL_TWIN_ASSESSMENT"
                    ),
                    payload,
                )

        except Exception as exc:
            print(
                f"⚠️ Twin event emit failed: {exc}"
            )

    # ========================================================
    # NORMALIZATION
    # ========================================================

    def _select_primary_signal(
        self,
        signals: Sequence[
            OperationalTwinSignal
        ],
    ) -> OperationalTwinSignal:

        return sorted(
            signals,
            key=lambda item: (
                item
                .collapse_risk_score,
                item
                .survivability_risk_score,
                item
                .governance_pressure_score,
                item
                .execution_instability_score,
                -item.created_at_ms,
            ),
            reverse=True,
        )[0]

    def _normalize_signal(
        self,
        item: (
            OperationalTwinSignal
            | Dict[str, Any]
        ),
        *,
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> OperationalTwinSignal:

        if isinstance(
            item,
            OperationalTwinSignal,
        ):
            return item

        return (
            OperationalTwinSignal(
                twin_signal_id=str(
                    item.get(
                        "twin_signal_id"
                    )
                    or uuid.uuid4()
                ),
                signal_type=str(
                    item.get(
                        "signal_type"
                    )
                    or "UNKNOWN"
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
        SovereignOperationalTwinAssessment
    ):

        return (
            SovereignOperationalTwinAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                simulation_state=(
                    SIMULATION_STABLE
                ),
                projected_outcome=(
                    OUTCOME_SUCCESS
                ),
                recommendation=(
                    RECOMMENDATION_NONE
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
                recovery_probability=1.0,
                survivability_probability=1.0,
                stabilization_probability=1.0,
                projected_horizon_steps=0,
                selected_signal_id=None,
                selected_signal_type=None,
                severity=(
                    TwinSeverity
                    .INFO.value
                ),
                confidence=1.0,
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=correlation_id,
                simulation_steps=[],
                recommended_controls=[
                    "lineage_recording",
                    "evidence_recording",
                ],
                recommended_actions=[
                    {
                        "action": (
                            "continue_runtime_operations"
                        )
                    }
                ],
                rationale=(
                    "No operational "
                    "twin signals submitted."
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
            or TwinDomain
            .UNKNOWN.value
        ).upper()

        valid = {
            item.value
            for item in TwinDomain
        }

        return (
            value
            if value in valid
            else TwinDomain
            .UNKNOWN.value
        )

    @staticmethod
    def _safe_severity(
        value: Any,
    ) -> str:

        value = str(
            value
            or TwinSeverity
            .INFO.value
        ).upper()

        valid = {
            item.value
            for item in TwinSeverity
        }

        return (
            value
            if value in valid
            else TwinSeverity
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


# ============================================================
# FACTORY
# ============================================================

def build_sovereign_operational_digital_twin(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[
        Any
    ] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: (
        Optional[Any]
    ) = None,
) -> SovereignOperationalDigitalTwin:
    """
    Factory for explicit dependency injection.
    """

    return (
        SovereignOperationalDigitalTwin(
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