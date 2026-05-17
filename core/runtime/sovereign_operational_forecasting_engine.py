"""
core/runtime/sovereign_operational_forecasting_engine.py

Sovereign Operational Forecasting Engine

Long-horizon sovereign operational forecasting cognition layer.

This subsystem forecasts:
- operational evolution
- survivability degradation
- governance saturation
- mission degradation
- autonomy destabilization
- resilience trajectories
- infrastructure instability
- strategic operational drift
- recovery sustainability
- branching future trajectories

IMPORTANT:
This subsystem DOES NOT:
- execute runtime actions
- mutate infrastructure
- trigger containment
- enforce governance
- initiate failovers

It ONLY:
- forecasts operational futures
- evaluates trajectory evolution
- projects probabilistic outcomes
- models strategic uncertainty
- records replayable forecast lineage/evidence
"""

from __future__ import annotations

import math
import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


DEFAULT_ENGINE_NAME = (
    "sovereign_operational_forecasting_engine"
)

FORECAST_STATE_STABLE = "STABLE"
FORECAST_STATE_DEGRADED = "DEGRADED"
FORECAST_STATE_AT_RISK = "AT_RISK"
FORECAST_STATE_CRITICAL = "CRITICAL"
FORECAST_STATE_COLLAPSE = "COLLAPSE"

FORECAST_OUTCOME_STABLE = "STABLE"
FORECAST_OUTCOME_VOLATILE = "VOLATILE"
FORECAST_OUTCOME_DEGRADING = "DEGRADING"
FORECAST_OUTCOME_COLLAPSE_RISK = "COLLAPSE_RISK"
FORECAST_OUTCOME_RECOVERING = "RECOVERING"

FORECAST_MODE_OPERATIONAL = "OPERATIONAL"
FORECAST_MODE_GOVERNANCE = "GOVERNANCE"
FORECAST_MODE_MISSION = "MISSION"
FORECAST_MODE_RESILIENCE = "RESILIENCE"
FORECAST_MODE_BRANCHING = "BRANCHING"

DEFAULT_FORECAST_HORIZON = 12


class ForecastSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ForecastDomain(str, Enum):
    GOVERNANCE = "GOVERNANCE"
    EXECUTION = "EXECUTION"
    AUTONOMY = "AUTONOMY"
    RESILIENCE = "RESILIENCE"
    TELEMETRY = "TELEMETRY"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    MISSION = "MISSION"
    SIMULATION = "SIMULATION"
    GLOBAL = "GLOBAL"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ForecastSignal:
    """
    Forecasting input signal.
    """

    forecast_signal_id: str

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

    operational_pressure_score: float = 0.0
    governance_pressure_score: float = 0.0
    survivability_score: float = 100.0
    mission_risk_score: float = 0.0
    resilience_score: float = 100.0
    autonomy_destabilization_score: float = 0.0
    infrastructure_instability_score: float = 0.0
    recovery_sustainability_score: float = 100.0
    uncertainty_score: float = 0.0

    payload: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(
        default_factory=lambda: int(time.time() * 1000)
    )


@dataclass(frozen=True)
class ForecastBranch:
    """
    Branching future trajectory.
    """

    branch_id: str

    branch_name: str

    projected_state: str
    projected_outcome: str

    collapse_probability: float
    survivability_probability: float
    recovery_probability: float
    governance_stability_probability: float

    trajectory_score: float

    rationale: str

    metadata: Dict[str, Any] = field(default_factory=dict)

    created_at_ms: int = field(
        default_factory=lambda: int(time.time() * 1000)
    )


@dataclass(frozen=True)
class ForecastStep:
    """
    Forecast trajectory step.
    """

    step_id: str

    step_index: int

    projected_state: str
    projected_outcome: str

    operational_pressure_score: float
    governance_pressure_score: float
    survivability_score: float
    mission_risk_score: float
    resilience_score: float
    autonomy_destabilization_score: float
    infrastructure_instability_score: float
    recovery_sustainability_score: float
    uncertainty_score: float

    collapse_probability: float
    survivability_probability: float
    recovery_probability: float
    volatility_probability: float

    trajectory_score: float

    branches: List[ForecastBranch] = field(
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
class SovereignOperationalForecastAssessment:
    """
    Sovereign operational forecast assessment.
    """

    assessment_id: str

    forecast_state: str
    projected_outcome: str
    forecast_mode: str

    collapse_probability: float
    survivability_probability: float
    recovery_probability: float
    governance_stability_probability: float
    volatility_probability: float

    operational_pressure_score: float
    governance_pressure_score: float
    survivability_score: float
    mission_risk_score: float
    resilience_score: float
    autonomy_destabilization_score: float
    infrastructure_instability_score: float
    recovery_sustainability_score: float
    uncertainty_score: float

    forecast_confidence: float
    explainability_score: float
    strategic_visibility_score: float

    selected_signal_id: Optional[str]
    selected_signal_type: Optional[str]

    severity: str
    confidence: float

    forecast_horizon: int

    mission_id: Optional[str]

    tenant_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    forecast_steps: List[ForecastStep]

    recommended_actions: List[
        Dict[str, Any]
    ]

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at_ms: int = field(
        default_factory=lambda: int(time.time() * 1000)
    )


@dataclass(frozen=True)
class SovereignOperationalForecastSnapshot:
    """
    Forecast engine diagnostics snapshot.
    """

    engine_name: str

    total_signals_seen: int

    total_assessments_created: int

    last_assessment_id: Optional[str]

    last_forecast_state: Optional[str]

    last_updated_ms: int


class SovereignOperationalForecastingEngine:
    """
    Sovereign forecasting cognition engine.
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
            SovereignOperationalForecastAssessment
        ] = []

    # =========================================================
    # PUBLIC API
    # =========================================================

    def evaluate(
        self,
        signals: Sequence[
            ForecastSignal | Dict[str, Any]
        ],
        *,
        forecast_mode: str = (
            FORECAST_MODE_OPERATIONAL
        ),
        forecast_horizon: int = (
            DEFAULT_FORECAST_HORIZON
        ),
        mission_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> (
        SovereignOperationalForecastAssessment
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
                    forecast_mode=(
                        forecast_mode
                    ),
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

        operational_pressure = (
            self._avg_score(
                [
                    item
                    .operational_pressure_score
                    for item in normalized
                ]
            )
        )

        governance_pressure = (
            self._avg_score(
                [
                    item
                    .governance_pressure_score
                    for item in normalized
                ]
            )
        )

        survivability = (
            self._avg_score(
                [
                    item
                    .survivability_score
                    for item in normalized
                ]
            )
        )

        mission_risk = (
            self._avg_score(
                [
                    item
                    .mission_risk_score
                    for item in normalized
                ]
            )
        )

        resilience = (
            self._avg_score(
                [
                    item
                    .resilience_score
                    for item in normalized
                ]
            )
        )

        autonomy_destabilization = (
            self._avg_score(
                [
                    item
                    .autonomy_destabilization_score
                    for item in normalized
                ]
            )
        )

        infrastructure_instability = (
            self._avg_score(
                [
                    item
                    .infrastructure_instability_score
                    for item in normalized
                ]
            )
        )

        recovery_sustainability = (
            self._avg_score(
                [
                    item
                    .recovery_sustainability_score
                    for item in normalized
                ]
            )
        )

        uncertainty = (
            self._avg_score(
                [
                    item
                    .uncertainty_score
                    for item in normalized
                ]
            )
        )

        collapse_probability = (
            self
            ._collapse_probability(
                operational_pressure=(
                    operational_pressure
                ),
                governance_pressure=(
                    governance_pressure
                ),
                survivability=(
                    survivability
                ),
                mission_risk=(
                    mission_risk
                ),
                resilience=(
                    resilience
                ),
                autonomy_destabilization=(
                    autonomy_destabilization
                ),
                infrastructure_instability=(
                    infrastructure_instability
                ),
                uncertainty=(
                    uncertainty
                ),
            )
        )

        survivability_probability = (
            self
            ._survivability_probability(
                survivability=(
                    survivability
                ),
                resilience=(
                    resilience
                ),
                mission_risk=(
                    mission_risk
                ),
            )
        )

        recovery_probability = (
            self
            ._recovery_probability(
                resilience=(
                    resilience
                ),
                recovery_sustainability=(
                    recovery_sustainability
                ),
                uncertainty=(
                    uncertainty
                ),
            )
        )

        governance_stability = (
            self
            ._governance_stability_probability(
                governance_pressure=(
                    governance_pressure
                ),
                uncertainty=(
                    uncertainty
                ),
            )
        )

        volatility_probability = (
            self
            ._volatility_probability(
                operational_pressure=(
                    operational_pressure
                ),
                autonomy_destabilization=(
                    autonomy_destabilization
                ),
                infrastructure_instability=(
                    infrastructure_instability
                ),
                uncertainty=(
                    uncertainty
                ),
            )
        )

        forecast_state = (
            self._forecast_state(
                collapse_probability=(
                    collapse_probability
                ),
                survivability_probability=(
                    survivability_probability
                ),
                volatility_probability=(
                    volatility_probability
                ),
            )
        )

        projected_outcome = (
            self._projected_outcome(
                forecast_state=(
                    forecast_state
                ),
                recovery_probability=(
                    recovery_probability
                ),
                volatility_probability=(
                    volatility_probability
                ),
            )
        )

        forecast_steps = (
            self._build_forecast_steps(
                operational_pressure=(
                    operational_pressure
                ),
                governance_pressure=(
                    governance_pressure
                ),
                survivability=(
                    survivability
                ),
                mission_risk=(
                    mission_risk
                ),
                resilience=(
                    resilience
                ),
                autonomy_destabilization=(
                    autonomy_destabilization
                ),
                infrastructure_instability=(
                    infrastructure_instability
                ),
                recovery_sustainability=(
                    recovery_sustainability
                ),
                uncertainty=(
                    uncertainty
                ),
                forecast_horizon=(
                    forecast_horizon
                ),
            )
        )

        forecast_confidence = (
            self
            ._forecast_confidence(
                normalized
            )
        )

        explainability_score = (
            self
            ._explainability_score(
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
            SovereignOperationalForecastAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                forecast_state=(
                    forecast_state
                ),
                projected_outcome=(
                    projected_outcome
                ),
                forecast_mode=(
                    forecast_mode
                ),
                collapse_probability=(
                    collapse_probability
                ),
                survivability_probability=(
                    survivability_probability
                ),
                recovery_probability=(
                    recovery_probability
                ),
                governance_stability_probability=(
                    governance_stability
                ),
                volatility_probability=(
                    volatility_probability
                ),
                operational_pressure_score=(
                    operational_pressure
                ),
                governance_pressure_score=(
                    governance_pressure
                ),
                survivability_score=(
                    survivability
                ),
                mission_risk_score=(
                    mission_risk
                ),
                resilience_score=(
                    resilience
                ),
                autonomy_destabilization_score=(
                    autonomy_destabilization
                ),
                infrastructure_instability_score=(
                    infrastructure_instability
                ),
                recovery_sustainability_score=(
                    recovery_sustainability
                ),
                uncertainty_score=(
                    uncertainty
                ),
                forecast_confidence=(
                    forecast_confidence
                ),
                explainability_score=(
                    explainability_score
                ),
                strategic_visibility_score=(
                    strategic_visibility
                ),
                selected_signal_id=(
                    selected
                    .forecast_signal_id
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
                forecast_horizon=(
                    forecast_horizon
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
                forecast_steps=(
                    forecast_steps
                ),
                recommended_actions=(
                    self
                    ._recommended_actions(
                        forecast_state=(
                            forecast_state
                        ),
                        projected_outcome=(
                            projected_outcome
                        ),
                    )
                ),
                rationale=self._build_rationale(
                    forecast_state=(
                        forecast_state
                    ),
                    projected_outcome=(
                        projected_outcome
                    ),
                    collapse_probability=(
                        collapse_probability
                    ),
                    survivability_probability=(
                        survivability_probability
                    ),
                    recovery_probability=(
                        recovery_probability
                    ),
                    volatility_probability=(
                        volatility_probability
                    ),
                    forecast_horizon=(
                        forecast_horizon
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
            ForecastSignal | Dict[str, Any]
        ],
        *,
        forecast_mode: str = (
            FORECAST_MODE_OPERATIONAL
        ),
        forecast_horizon: int = (
            DEFAULT_FORECAST_HORIZON
        ),
        mission_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> (
        SovereignOperationalForecastAssessment
    ):

        return self.evaluate(
            signals,
            forecast_mode=forecast_mode,
            forecast_horizon=(
                forecast_horizon
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
        SovereignOperationalForecastAssessment
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
        SovereignOperationalForecastSnapshot
    ):

        latest = (
            self._assessments[-1]
            if self._assessments
            else None
        )

        return (
            SovereignOperationalForecastSnapshot(
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
                last_forecast_state=(
                    latest.forecast_state
                    if latest
                    else None
                ),
                last_updated_ms=int(
                    time.time() * 1000
                ),
            )
        )

    # =========================================================
    # FORECAST TRAJECTORY
    # =========================================================

    def _build_forecast_steps(
        self,
        *,
        operational_pressure: float,
        governance_pressure: float,
        survivability: float,
        mission_risk: float,
        resilience: float,
        autonomy_destabilization: float,
        infrastructure_instability: (
            float
        ),
        recovery_sustainability: (
            float
        ),
        uncertainty: float,
        forecast_horizon: int,
    ) -> List[ForecastStep]:

        steps: List[
            ForecastStep
        ] = []

        for idx in range(
            max(
                1,
                int(forecast_horizon),
            )
        ):

            drift = math.log(
                idx + 2
            ) * 2.5

            operational_pressure = (
                self._clamp_score(
                    operational_pressure
                    + drift
                )
            )

            governance_pressure = (
                self._clamp_score(
                    governance_pressure
                    + drift * 0.8
                )
            )

            mission_risk = (
                self._clamp_score(
                    mission_risk
                    + drift * 1.1
                )
            )

            survivability = (
                self._clamp_score(
                    survivability
                    - drift * 0.9
                )
            )

            resilience = (
                self._clamp_score(
                    resilience
                    - drift * 0.7
                )
            )

            autonomy_destabilization = (
                self._clamp_score(
                    autonomy_destabilization
                    + drift * 0.6
                )
            )

            infrastructure_instability = (
                self._clamp_score(
                    infrastructure_instability
                    + drift * 0.75
                )
            )

            uncertainty = (
                self._clamp_score(
                    uncertainty
                    + drift * 0.5
                )
            )

            collapse_probability = (
                self
                ._collapse_probability(
                    operational_pressure=(
                        operational_pressure
                    ),
                    governance_pressure=(
                        governance_pressure
                    ),
                    survivability=(
                        survivability
                    ),
                    mission_risk=(
                        mission_risk
                    ),
                    resilience=(
                        resilience
                    ),
                    autonomy_destabilization=(
                        autonomy_destabilization
                    ),
                    infrastructure_instability=(
                        infrastructure_instability
                    ),
                    uncertainty=(
                        uncertainty
                    ),
                )
            )

            survivability_probability = (
                self
                ._survivability_probability(
                    survivability=(
                        survivability
                    ),
                    resilience=(
                        resilience
                    ),
                    mission_risk=(
                        mission_risk
                    ),
                )
            )

            recovery_probability = (
                self
                ._recovery_probability(
                    resilience=(
                        resilience
                    ),
                    recovery_sustainability=(
                        recovery_sustainability
                    ),
                    uncertainty=(
                        uncertainty
                    ),
                )
            )

            volatility_probability = (
                self
                ._volatility_probability(
                    operational_pressure=(
                        operational_pressure
                    ),
                    autonomy_destabilization=(
                        autonomy_destabilization
                    ),
                    infrastructure_instability=(
                        infrastructure_instability
                    ),
                    uncertainty=(
                        uncertainty
                    ),
                )
            )

            state = self._forecast_state(
                collapse_probability=(
                    collapse_probability
                ),
                survivability_probability=(
                    survivability_probability
                ),
                volatility_probability=(
                    volatility_probability
                ),
            )

            outcome = (
                self._projected_outcome(
                    forecast_state=(
                        state
                    ),
                    recovery_probability=(
                        recovery_probability
                    ),
                    volatility_probability=(
                        volatility_probability
                    ),
                )
            )

            trajectory_score = (
                self._trajectory_score(
                    survivability=(
                        survivability
                    ),
                    resilience=(
                        resilience
                    ),
                    collapse_probability=(
                        collapse_probability
                    ),
                    volatility_probability=(
                        volatility_probability
                    ),
                )
            )

            branches = (
                self._build_branches(
                    state=state,
                    outcome=outcome,
                    collapse_probability=(
                        collapse_probability
                    ),
                    survivability_probability=(
                        survivability_probability
                    ),
                    recovery_probability=(
                        recovery_probability
                    ),
                    governance_stability_probability=(
                        self
                        ._governance_stability_probability(
                            governance_pressure=(
                                governance_pressure
                            ),
                            uncertainty=(
                                uncertainty
                            ),
                        )
                    ),
                    trajectory_score=(
                        trajectory_score
                    ),
                )
            )

            steps.append(
                ForecastStep(
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
                    operational_pressure_score=(
                        operational_pressure
                    ),
                    governance_pressure_score=(
                        governance_pressure
                    ),
                    survivability_score=(
                        survivability
                    ),
                    mission_risk_score=(
                        mission_risk
                    ),
                    resilience_score=(
                        resilience
                    ),
                    autonomy_destabilization_score=(
                        autonomy_destabilization
                    ),
                    infrastructure_instability_score=(
                        infrastructure_instability
                    ),
                    recovery_sustainability_score=(
                        recovery_sustainability
                    ),
                    uncertainty_score=(
                        uncertainty
                    ),
                    collapse_probability=(
                        collapse_probability
                    ),
                    survivability_probability=(
                        survivability_probability
                    ),
                    recovery_probability=(
                        recovery_probability
                    ),
                    volatility_probability=(
                        volatility_probability
                    ),
                    trajectory_score=(
                        trajectory_score
                    ),
                    branches=branches,
                    rationale=(
                        f"Forecast step "
                        f"{idx} projected "
                        f"{state}."
                    ),
                )
            )

        return steps

    def _build_branches(
        self,
        *,
        state: str,
        outcome: str,
        collapse_probability: float,
        survivability_probability: (
            float
        ),
        recovery_probability: float,
        governance_stability_probability: (
            float
        ),
        trajectory_score: float,
    ) -> List[ForecastBranch]:

        return [
            ForecastBranch(
                branch_id=str(
                    uuid.uuid4()
                ),
                branch_name=(
                    "stabilization_path"
                ),
                projected_state=(
                    FORECAST_STATE_STABLE
                    if recovery_probability
                    > 0.7
                    else state
                ),
                projected_outcome=(
                    FORECAST_OUTCOME_RECOVERING
                ),
                collapse_probability=(
                    self
                    ._clamp_probability(
                        collapse_probability
                        * 0.5
                    )
                ),
                survivability_probability=(
                    self
                    ._clamp_probability(
                        survivability_probability
                        + 0.2
                    )
                ),
                recovery_probability=(
                    self
                    ._clamp_probability(
                        recovery_probability
                        + 0.2
                    )
                ),
                governance_stability_probability=(
                    self
                    ._clamp_probability(
                        governance_stability_probability
                        + 0.1
                    )
                ),
                trajectory_score=(
                    self._clamp_score(
                        trajectory_score
                        + 15
                    )
                ),
                rationale=(
                    "Projected "
                    "stabilization "
                    "trajectory."
                ),
            ),
            ForecastBranch(
                branch_id=str(
                    uuid.uuid4()
                ),
                branch_name=(
                    "collapse_path"
                ),
                projected_state=(
                    FORECAST_STATE_COLLAPSE
                ),
                projected_outcome=(
                    FORECAST_OUTCOME_COLLAPSE_RISK
                ),
                collapse_probability=(
                    self
                    ._clamp_probability(
                        collapse_probability
                        + 0.3
                    )
                ),
                survivability_probability=(
                    self
                    ._clamp_probability(
                        survivability_probability
                        - 0.3
                    )
                ),
                recovery_probability=(
                    self
                    ._clamp_probability(
                        recovery_probability
                        - 0.2
                    )
                ),
                governance_stability_probability=(
                    self
                    ._clamp_probability(
                        governance_stability_probability
                        - 0.2
                    )
                ),
                trajectory_score=(
                    self._clamp_score(
                        trajectory_score
                        - 25
                    )
                ),
                rationale=(
                    "Projected "
                    "collapse "
                    "trajectory."
                ),
            ),
        ]

    # =========================================================
    # PROBABILITIES
    # =========================================================

    def _collapse_probability(
        self,
        *,
        operational_pressure: float,
        governance_pressure: float,
        survivability: float,
        mission_risk: float,
        resilience: float,
        autonomy_destabilization: (
            float
        ),
        infrastructure_instability: (
            float
        ),
        uncertainty: float,
    ) -> float:

        risk = (
            operational_pressure
            + governance_pressure
            + mission_risk
            + autonomy_destabilization
            + infrastructure_instability
            + uncertainty
            + (100 - survivability)
            + (100 - resilience)
        ) / 800.0

        return self._clamp_probability(
            risk
        )

    def _survivability_probability(
        self,
        *,
        survivability: float,
        resilience: float,
        mission_risk: float,
    ) -> float:

        probability = (
            survivability
            + resilience
            + (100 - mission_risk)
        ) / 300.0

        return self._clamp_probability(
            probability
        )

    def _recovery_probability(
        self,
        *,
        resilience: float,
        recovery_sustainability: (
            float
        ),
        uncertainty: float,
    ) -> float:

        probability = (
            resilience
            + recovery_sustainability
            + (100 - uncertainty)
        ) / 300.0

        return self._clamp_probability(
            probability
        )

    def _governance_stability_probability(
        self,
        *,
        governance_pressure: float,
        uncertainty: float,
    ) -> float:

        probability = (
            (
                100
                - governance_pressure
            )
            + (
                100
                - uncertainty
            )
        ) / 200.0

        return self._clamp_probability(
            probability
        )

    def _volatility_probability(
        self,
        *,
        operational_pressure: float,
        autonomy_destabilization: (
            float
        ),
        infrastructure_instability: (
            float
        ),
        uncertainty: float,
    ) -> float:

        probability = (
            operational_pressure
            + autonomy_destabilization
            + infrastructure_instability
            + uncertainty
        ) / 400.0

        return self._clamp_probability(
            probability
        )

    # =========================================================
    # STATES
    # =========================================================

    @staticmethod
    def _forecast_state(
        *,
        collapse_probability: float,
        survivability_probability: (
            float
        ),
        volatility_probability: float,
    ) -> str:

        if collapse_probability >= 0.8:
            return FORECAST_STATE_COLLAPSE

        if (
            collapse_probability >= 0.6
            or survivability_probability
            <= 0.35
        ):
            return FORECAST_STATE_CRITICAL

        if volatility_probability >= 0.55:
            return FORECAST_STATE_AT_RISK

        if volatility_probability >= 0.35:
            return FORECAST_STATE_DEGRADED

        return FORECAST_STATE_STABLE

    @staticmethod
    def _projected_outcome(
        *,
        forecast_state: str,
        recovery_probability: float,
        volatility_probability: (
            float
        ),
    ) -> str:

        if (
            forecast_state
            == FORECAST_STATE_COLLAPSE
        ):
            return (
                FORECAST_OUTCOME_COLLAPSE_RISK
            )

        if recovery_probability >= 0.7:
            return (
                FORECAST_OUTCOME_RECOVERING
            )

        if volatility_probability >= 0.6:
            return (
                FORECAST_OUTCOME_VOLATILE
            )

        if volatility_probability >= 0.4:
            return (
                FORECAST_OUTCOME_DEGRADING
            )

        return FORECAST_OUTCOME_STABLE

    # =========================================================
    # SCORING
    # =========================================================

    def _trajectory_score(
        self,
        *,
        survivability: float,
        resilience: float,
        collapse_probability: float,
        volatility_probability: (
            float
        ),
    ) -> float:

        score = (
            survivability
            + resilience
            + (
                100
                - (
                    collapse_probability
                    * 100
                )
            )
            + (
                100
                - (
                    volatility_probability
                    * 100
                )
            )
        ) / 4.0

        return self._clamp_score(
            score
        )

    def _forecast_confidence(
        self,
        signals: Sequence[
            ForecastSignal
        ],
    ) -> float:

        if not signals:
            return 0.0

        return self._clamp_probability(
            sum(
                item.confidence
                for item in signals
            )
            / len(signals)
        )

    def _explainability_score(
        self,
        signals: Sequence[
            ForecastSignal
        ],
    ) -> float:

        if not signals:
            return 0.0

        explained = 0

        for item in signals:

            if item.summary:
                explained += 1

            if item.source_engine:
                explained += 1

            if item.signal_type:
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
            ForecastSignal
        ],
    ) -> float:

        if not signals:
            return 0.0

        scored = 0

        for item in signals:

            if item.mission_id:
                scored += 1

            if item.tenant_id:
                scored += 1

            if item.domain:
                scored += 1

        return self._clamp_score(
            (
                scored
                / (
                    len(signals) * 3
                )
            )
            * 100
        )

    # =========================================================
    # ACTIONS
    # =========================================================

    def _recommended_actions(
        self,
        *,
        forecast_state: str,
        projected_outcome: str,
    ) -> List[Dict[str, Any]]:

        actions = [
            {
                "action": (
                    "record_forecast_lineage"
                )
            },
            {
                "action": (
                    "record_forecast_evidence"
                )
            },
        ]

        if (
            forecast_state
            in {
                FORECAST_STATE_AT_RISK,
                FORECAST_STATE_CRITICAL,
            }
        ):
            actions.append(
                {
                    "action": (
                        "review_operational_trajectory"
                    )
                }
            )

        if (
            forecast_state
            == FORECAST_STATE_COLLAPSE
        ):
            actions.append(
                {
                    "action": (
                        "prepare_resilience_escalation"
                    )
                }
            )

        if (
            projected_outcome
            == FORECAST_OUTCOME_VOLATILE
        ):
            actions.append(
                {
                    "action": (
                        "stabilize_operational_volatility"
                    )
                }
            )

        return actions

    # =========================================================
    # RATIONALE
    # =========================================================

    @staticmethod
    def _build_rationale(
        *,
        forecast_state: str,
        projected_outcome: str,
        collapse_probability: float,
        survivability_probability: (
            float
        ),
        recovery_probability: float,
        volatility_probability: (
            float
        ),
        forecast_horizon: int,
        signal_count: int,
    ) -> str:

        return (
            f"Sovereign operational "
            f"forecast evaluated "
            f"{signal_count} signal(s) "
            f"across forecast horizon "
            f"{forecast_horizon}. "
            f"Forecast state "
            f"{forecast_state}; "
            f"projected outcome "
            f"{projected_outcome}. "
            f"Collapse probability "
            f"{collapse_probability:.2f}; "
            f"survivability probability "
            f"{survivability_probability:.2f}; "
            f"recovery probability "
            f"{recovery_probability:.2f}; "
            f"volatility probability "
            f"{volatility_probability:.2f}."
        )

    # =========================================================
    # RECORDING
    # =========================================================

    def _record_assessment(
        self,
        assessment: (
            SovereignOperationalForecastAssessment
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
            SovereignOperationalForecastAssessment
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
                "SOVEREIGN_OPERATIONAL_FORECAST_ASSESSMENT"
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
                f"⚠️ Forecast memory write failed: {exc}"
            )

    def _write_to_lineage(
        self,
        assessment: (
            SovereignOperationalForecastAssessment
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
                "OPERATIONAL_FORECAST"
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
                f"⚠️ Forecast lineage write failed: {exc}"
            )

    def _write_to_evidence(
        self,
        assessment: (
            SovereignOperationalForecastAssessment
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
                "OPERATIONAL_FORECAST"
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
                f"⚠️ Forecast evidence write failed: {exc}"
            )

    def _emit_event(
        self,
        assessment: (
            SovereignOperationalForecastAssessment
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
                "SOVEREIGN_OPERATIONAL_FORECAST_ASSESSMENT"
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
                        "SOVEREIGN_OPERATIONAL_FORECAST_ASSESSMENT"
                    ),
                    payload,
                )

        except Exception as exc:
            print(
                f"⚠️ Forecast event emit failed: {exc}"
            )

    # =========================================================
    # NORMALIZATION
    # =========================================================

    def _normalize_signal(
        self,
        item: ForecastSignal | Dict[str, Any],
        *,
        mission_id: Optional[str],
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> ForecastSignal:

        if isinstance(
            item,
            ForecastSignal,
        ):
            return item

        return ForecastSignal(
            forecast_signal_id=str(
                item.get(
                    "forecast_signal_id"
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
            operational_pressure_score=(
                self._clamp_score(
                    item.get(
                        "operational_pressure_score",
                        0.0,
                    )
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
            survivability_score=(
                self._clamp_score(
                    item.get(
                        "survivability_score",
                        100.0,
                    )
                )
            ),
            mission_risk_score=(
                self._clamp_score(
                    item.get(
                        "mission_risk_score",
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
            autonomy_destabilization_score=(
                self._clamp_score(
                    item.get(
                        "autonomy_destabilization_score",
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
            recovery_sustainability_score=(
                self._clamp_score(
                    item.get(
                        "recovery_sustainability_score",
                        100.0,
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
        forecast_mode: str,
        mission_id: Optional[str],
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> (
        SovereignOperationalForecastAssessment
    ):

        return (
            SovereignOperationalForecastAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                forecast_state=(
                    FORECAST_STATE_STABLE
                ),
                projected_outcome=(
                    FORECAST_OUTCOME_STABLE
                ),
                forecast_mode=(
                    forecast_mode
                ),
                collapse_probability=0.0,
                survivability_probability=1.0,
                recovery_probability=1.0,
                governance_stability_probability=1.0,
                volatility_probability=0.0,
                operational_pressure_score=0.0,
                governance_pressure_score=0.0,
                survivability_score=100.0,
                mission_risk_score=0.0,
                resilience_score=100.0,
                autonomy_destabilization_score=0.0,
                infrastructure_instability_score=0.0,
                recovery_sustainability_score=100.0,
                uncertainty_score=0.0,
                forecast_confidence=1.0,
                explainability_score=100.0,
                strategic_visibility_score=100.0,
                selected_signal_id=None,
                selected_signal_type=None,
                severity=(
                    ForecastSeverity
                    .INFO.value
                ),
                confidence=1.0,
                forecast_horizon=0,
                mission_id=mission_id,
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=(
                    correlation_id
                ),
                forecast_steps=[],
                recommended_actions=[
                    {
                        "action": (
                            "continue_operational_monitoring"
                        )
                    }
                ],
                rationale=(
                    "No forecast "
                    "signals submitted."
                ),
                metadata={},
            )
        )

    def _select_primary_signal(
        self,
        signals: Sequence[
            ForecastSignal
        ],
    ) -> ForecastSignal:

        return sorted(
            signals,
            key=lambda item: (
                item
                .mission_risk_score,
                item
                .operational_pressure_score,
                item
                .governance_pressure_score,
                -item.created_at_ms,
            ),
            reverse=True,
        )[0]

    # =========================================================
    # HELPERS
    # =========================================================

    @staticmethod
    def _safe_domain(
        value: Any,
    ) -> str:

        value = str(
            value
            or ForecastDomain
            .UNKNOWN.value
        ).upper()

        valid = {
            item.value
            for item in ForecastDomain
        }

        return (
            value
            if value in valid
            else ForecastDomain
            .UNKNOWN.value
        )

    @staticmethod
    def _safe_severity(
        value: Any,
    ) -> str:

        value = str(
            value
            or ForecastSeverity
            .INFO.value
        ).upper()

        valid = {
            item.value
            for item in ForecastSeverity
        }

        return (
            value
            if value in valid
            else ForecastSeverity
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
                sum(values)
                / len(values),
            ),
        )


def build_sovereign_operational_forecasting_engine(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[Any] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: (
        Optional[Any]
    ) = None,
) -> (
    SovereignOperationalForecastingEngine
):

    return (
        SovereignOperationalForecastingEngine(
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