"""
core/runtime/sovereign_adaptive_learning_engine.py

Sovereign Adaptive Learning Engine

Adaptive sovereign operational cognition layer.

This subsystem:
- learns from orchestration outcomes
- learns from governance outcomes
- learns from verification outcomes
- learns from survivability outcomes
- learns from recovery outcomes
- learns from escalation outcomes
- adapts strategic priorities
- adapts orchestration sequencing
- adapts governance enforcement thresholds
- produces replayable adaptive learning lineage

IMPORTANT:
This subsystem DOES NOT:
- autonomously bypass governance
- autonomously mutate infrastructure
- autonomously override human approval
- autonomously execute destructive actions

It ONLY:
- adapt operational cognition
- optimize governance-safe execution
- optimize survivability-safe orchestration
- produce replayable learning rationale
"""

from __future__ import annotations

import statistics
import time
import uuid

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


DEFAULT_ENGINE_NAME = (
    "sovereign_adaptive_learning_engine"
)

DEFAULT_LEARNING_DEPTH = 10


LEARNING_STATE_OPTIMAL = "OPTIMAL"
LEARNING_STATE_STABLE = "STABLE"
LEARNING_STATE_ADAPTING = "ADAPTING"
LEARNING_STATE_RECALIBRATING = (
    "RECALIBRATING"
)
LEARNING_STATE_RESILIENCE_PRESSURE = (
    "RESILIENCE_PRESSURE"
)
LEARNING_STATE_GOVERNANCE_DRIFT = (
    "GOVERNANCE_DRIFT"
)
LEARNING_STATE_SURVIVABILITY_DEGRADATION = (
    "SURVIVABILITY_DEGRADATION"
)
LEARNING_STATE_CRITICAL_RETRAINING = (
    "CRITICAL_RETRAINING"
)


LEARNING_RESULT_OPTIMIZED = "OPTIMIZED"
LEARNING_RESULT_IMPROVING = "IMPROVING"
LEARNING_RESULT_DEGRADED = "DEGRADED"


class LearningSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class AdaptiveLearningSignal:
    signal_id: str

    source_engine: str

    severity: str
    confidence: float

    summary: str

    tenant_id: Optional[str] = None
    mission_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    orchestration_success_score: float = 100.0
    governance_success_score: float = 100.0
    verification_success_score: float = 100.0
    survivability_success_score: float = 100.0
    recovery_success_score: float = 100.0
    resilience_success_score: float = 100.0

    escalation_failure_score: float = 0.0
    continuity_fragmentation_score: float = 0.0
    sovereignty_pressure_score: float = 0.0
    governance_drift_score: float = 0.0

    blast_radius_score: float = 0.0
    autonomy_pressure_score: float = 0.0
    uncertainty_score: float = 0.0

    optimization_opportunity_score: float = 0.0

    payload: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


@dataclass(frozen=True)
class AdaptiveThreshold:
    threshold_id: str

    threshold_name: str

    previous_value: float
    adapted_value: float

    adaptation_delta: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class StrategicAdaptation:
    adaptation_id: str

    adaptation_name: str

    priority: str

    expected_improvement_score: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class AdaptiveProjection:
    projection_id: str

    projected_state: str

    learning_result: str

    governance_projection_score: float
    survivability_projection_score: float
    recovery_projection_score: float
    resilience_projection_score: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class AdaptiveForecastStep:
    step_id: str

    step_index: int

    learning_state: str

    learning_result: str

    optimization_score: float

    governance_score: float
    survivability_score: float
    recovery_score: float
    resilience_score: float

    rationale: str

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class SovereignAdaptiveLearningAssessment:
    assessment_id: str

    learning_state: str

    learning_result: str

    orchestration_success_score: float
    governance_success_score: float
    verification_success_score: float
    survivability_success_score: float
    recovery_success_score: float
    resilience_success_score: float

    escalation_failure_score: float
    continuity_fragmentation_score: float
    sovereignty_pressure_score: float
    governance_drift_score: float

    blast_radius_score: float
    autonomy_pressure_score: float
    uncertainty_score: float

    optimization_opportunity_score: float

    adaptive_optimization_score: float

    learning_confidence: float
    systemic_risk_probability: float

    confidence: float
    explainability_score: float

    signal_count: int
    engine_count: int

    severity: str

    tenant_id: Optional[str]
    mission_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    thresholds: List[
        AdaptiveThreshold
    ]

    strategic_adaptations: List[
        StrategicAdaptation
    ]

    strategic_projection: (
        AdaptiveProjection
    )

    forecast_steps: List[
        AdaptiveForecastStep
    ]

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


class SovereignAdaptiveLearningEngine:
    """
    Sovereign adaptive operational cognition.
    """

    def __init__(
        self,
        *,
        engine_name: str = (
            DEFAULT_ENGINE_NAME
        ),
        event_bus: Optional[Any] = None,
        execution_verification_engine: Optional[
            Any
        ] = None,
        execution_governance_engine: Optional[
            Any
        ] = None,
        orchestration_engine: Optional[
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

        self.execution_verification_engine = (
            execution_verification_engine
        )

        self.execution_governance_engine = (
            execution_governance_engine
        )

        self.orchestration_engine = (
            orchestration_engine
        )

        self.operational_memory_engine = (
            operational_memory_engine
        )

        self.lineage_engine = lineage_engine

        self.fedramp_evidence_lineage_engine = (
            fedramp_evidence_lineage_engine
        )

        self._assessments: List[
            SovereignAdaptiveLearningAssessment
        ] = []

    # ==========================================================
    # PUBLIC API
    # ==========================================================

    def evaluate(
        self,
        signals: Sequence[
            AdaptiveLearningSignal
            | Dict[str, Any]
        ],
        *,
        learning_depth: int = (
            DEFAULT_LEARNING_DEPTH
        ),
        tenant_id: Optional[str] = None,
        mission_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> (
        SovereignAdaptiveLearningAssessment
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

        selected = self._select_primary_signal(
            normalized
        )

        orchestration_success = (
            self._avg_score(
                [
                    s
                    .orchestration_success_score
                    for s in normalized
                ]
            )
        )

        governance_success = (
            self._avg_score(
                [
                    s
                    .governance_success_score
                    for s in normalized
                ]
            )
        )

        verification_success = (
            self._avg_score(
                [
                    s
                    .verification_success_score
                    for s in normalized
                ]
            )
        )

        survivability_success = (
            self._avg_score(
                [
                    s
                    .survivability_success_score
                    for s in normalized
                ]
            )
        )

        recovery_success = (
            self._avg_score(
                [
                    s
                    .recovery_success_score
                    for s in normalized
                ]
            )
        )

        resilience_success = (
            self._avg_score(
                [
                    s
                    .resilience_success_score
                    for s in normalized
                ]
            )
        )

        escalation_failure = (
            self._avg_score(
                [
                    s
                    .escalation_failure_score
                    for s in normalized
                ]
            )
        )

        continuity_fragmentation = (
            self._avg_score(
                [
                    s
                    .continuity_fragmentation_score
                    for s in normalized
                ]
            )
        )

        sovereignty_pressure = (
            self._avg_score(
                [
                    s
                    .sovereignty_pressure_score
                    for s in normalized
                ]
            )
        )

        governance_drift = (
            self._avg_score(
                [
                    s
                    .governance_drift_score
                    for s in normalized
                ]
            )
        )

        blast_radius = self._avg_score(
            [
                s.blast_radius_score
                for s in normalized
            ]
        )

        autonomy_pressure = (
            self._avg_score(
                [
                    s
                    .autonomy_pressure_score
                    for s in normalized
                ]
            )
        )

        uncertainty = self._avg_score(
            [
                s.uncertainty_score
                for s in normalized
            ]
        )

        optimization_opportunity = (
            self._avg_score(
                [
                    s
                    .optimization_opportunity_score
                    for s in normalized
                ]
            )
        )

        adaptive_optimization = (
            self._adaptive_optimization_score(
                orchestration_success_score=(
                    orchestration_success
                ),
                governance_success_score=(
                    governance_success
                ),
                verification_success_score=(
                    verification_success
                ),
                survivability_success_score=(
                    survivability_success
                ),
                recovery_success_score=(
                    recovery_success
                ),
                resilience_success_score=(
                    resilience_success
                ),
                escalation_failure_score=(
                    escalation_failure
                ),
                continuity_fragmentation_score=(
                    continuity_fragmentation
                ),
                sovereignty_pressure_score=(
                    sovereignty_pressure
                ),
                governance_drift_score=(
                    governance_drift
                ),
                optimization_opportunity_score=(
                    optimization_opportunity
                ),
            )
        )

        systemic_risk_probability = (
            self
            ._systemic_risk_probability(
                escalation_failure_score=(
                    escalation_failure
                ),
                continuity_fragmentation_score=(
                    continuity_fragmentation
                ),
                sovereignty_pressure_score=(
                    sovereignty_pressure
                ),
                governance_drift_score=(
                    governance_drift
                ),
                blast_radius_score=(
                    blast_radius
                ),
                autonomy_pressure_score=(
                    autonomy_pressure
                ),
                uncertainty_score=(
                    uncertainty
                ),
            )
        )

        learning_state = (
            self._learning_state(
                adaptive_optimization_score=(
                    adaptive_optimization
                ),
                survivability_success_score=(
                    survivability_success
                ),
                governance_success_score=(
                    governance_success
                ),
                resilience_success_score=(
                    resilience_success
                ),
                governance_drift_score=(
                    governance_drift
                ),
            )
        )

        learning_result = (
            self._learning_result(
                learning_state=(
                    learning_state
                ),
                adaptive_optimization_score=(
                    adaptive_optimization
                ),
            )
        )

        thresholds = self._thresholds(
            governance_drift_score=(
                governance_drift
            ),
            sovereignty_pressure_score=(
                sovereignty_pressure
            ),
            continuity_fragmentation_score=(
                continuity_fragmentation
            ),
            escalation_failure_score=(
                escalation_failure
            ),
        )

        strategic_adaptations = (
            self._strategic_adaptations(
                learning_state=(
                    learning_state
                ),
                optimization_opportunity_score=(
                    optimization_opportunity
                ),
            )
        )

        projection = self._projection(
            learning_state=(
                learning_state
            ),
            learning_result=(
                learning_result
            ),
            governance_success_score=(
                governance_success
            ),
            survivability_success_score=(
                survivability_success
            ),
            recovery_success_score=(
                recovery_success
            ),
            resilience_success_score=(
                resilience_success
            ),
        )

        forecast_steps = (
            self._forecast_steps(
                learning_state=(
                    learning_state
                ),
                learning_result=(
                    learning_result
                ),
                adaptive_optimization_score=(
                    adaptive_optimization
                ),
                governance_success_score=(
                    governance_success
                ),
                survivability_success_score=(
                    survivability_success
                ),
                recovery_success_score=(
                    recovery_success
                ),
                resilience_success_score=(
                    resilience_success
                ),
                depth=learning_depth,
            )
        )

        assessment = (
            SovereignAdaptiveLearningAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                learning_state=(
                    learning_state
                ),
                learning_result=(
                    learning_result
                ),
                orchestration_success_score=(
                    orchestration_success
                ),
                governance_success_score=(
                    governance_success
                ),
                verification_success_score=(
                    verification_success
                ),
                survivability_success_score=(
                    survivability_success
                ),
                recovery_success_score=(
                    recovery_success
                ),
                resilience_success_score=(
                    resilience_success
                ),
                escalation_failure_score=(
                    escalation_failure
                ),
                continuity_fragmentation_score=(
                    continuity_fragmentation
                ),
                sovereignty_pressure_score=(
                    sovereignty_pressure
                ),
                governance_drift_score=(
                    governance_drift
                ),
                blast_radius_score=(
                    blast_radius
                ),
                autonomy_pressure_score=(
                    autonomy_pressure
                ),
                uncertainty_score=(
                    uncertainty
                ),
                optimization_opportunity_score=(
                    optimization_opportunity
                ),
                adaptive_optimization_score=(
                    adaptive_optimization
                ),
                learning_confidence=(
                    self._confidence(
                        normalized
                    )
                ),
                systemic_risk_probability=(
                    systemic_risk_probability
                ),
                confidence=(
                    self._confidence(
                        normalized
                    )
                ),
                explainability_score=(
                    self
                    ._explainability_score(
                        normalized
                    )
                ),
                signal_count=len(
                    normalized
                ),
                engine_count=len(
                    {
                        s.source_engine
                        for s in normalized
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
                thresholds=thresholds,
                strategic_adaptations=(
                    strategic_adaptations
                ),
                strategic_projection=(
                    projection
                ),
                forecast_steps=(
                    forecast_steps
                ),
                telemetry_fusion=(
                    self._telemetry_fusion(
                        normalized
                    )
                ),
                rationale=(
                    self._rationale(
                        learning_state=(
                            learning_state
                        ),
                        learning_result=(
                            learning_result
                        ),
                        adaptive_optimization_score=(
                            adaptive_optimization
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
    # OPTIMIZATION
    # ==========================================================

    def _adaptive_optimization_score(
        self,
        *,
        orchestration_success_score: float,
        governance_success_score: float,
        verification_success_score: float,
        survivability_success_score: float,
        recovery_success_score: float,
        resilience_success_score: float,
        escalation_failure_score: float,
        continuity_fragmentation_score: float,
        sovereignty_pressure_score: float,
        governance_drift_score: float,
        optimization_opportunity_score: float,
    ) -> float:

        score = (
            orchestration_success_score
            + governance_success_score
            + verification_success_score
            + survivability_success_score
            + recovery_success_score
            + resilience_success_score
            + (
                100.0
                - escalation_failure_score
            )
            + (
                100.0
                - continuity_fragmentation_score
            )
            + (
                100.0
                - sovereignty_pressure_score
            )
            + (
                100.0
                - governance_drift_score
            )
            + optimization_opportunity_score
        ) / 11.0

        return self._clamp_score(
            score
        )

    def _systemic_risk_probability(
        self,
        *,
        escalation_failure_score: float,
        continuity_fragmentation_score: float,
        sovereignty_pressure_score: float,
        governance_drift_score: float,
        blast_radius_score: float,
        autonomy_pressure_score: float,
        uncertainty_score: float,
    ) -> float:

        value = (
            escalation_failure_score
            + continuity_fragmentation_score
            + sovereignty_pressure_score
            + governance_drift_score
            + blast_radius_score
            + autonomy_pressure_score
            + uncertainty_score
        ) / 700.0

        return self._clamp_probability(
            value
        )

    # ==========================================================
    # STATE
    # ==========================================================

    @staticmethod
    def _learning_state(
        *,
        adaptive_optimization_score: float,
        survivability_success_score: float,
        governance_success_score: float,
        resilience_success_score: float,
        governance_drift_score: float,
    ) -> str:

        if (
            adaptive_optimization_score
            < 40
        ):
            return (
                LEARNING_STATE_CRITICAL_RETRAINING
            )

        if (
            survivability_success_score
            < 60
        ):
            return (
                LEARNING_STATE_SURVIVABILITY_DEGRADATION
            )

        if governance_drift_score > 50:
            return (
                LEARNING_STATE_GOVERNANCE_DRIFT
            )

        if resilience_success_score < 70:
            return (
                LEARNING_STATE_RESILIENCE_PRESSURE
            )

        if governance_success_score < 75:
            return (
                LEARNING_STATE_RECALIBRATING
            )

        if (
            adaptive_optimization_score
            < 80
        ):
            return (
                LEARNING_STATE_ADAPTING
            )

        if (
            adaptive_optimization_score
            < 90
        ):
            return (
                LEARNING_STATE_STABLE
            )

        return LEARNING_STATE_OPTIMAL

    @staticmethod
    def _learning_result(
        *,
        learning_state: str,
        adaptive_optimization_score: float,
    ) -> str:

        if learning_state in {
            LEARNING_STATE_CRITICAL_RETRAINING,
            LEARNING_STATE_SURVIVABILITY_DEGRADATION,
        }:
            return (
                LEARNING_RESULT_DEGRADED
            )

        if (
            adaptive_optimization_score
            < 85
        ):
            return (
                LEARNING_RESULT_IMPROVING
            )

        return (
            LEARNING_RESULT_OPTIMIZED
        )

    # ==========================================================
    # THRESHOLDS
    # ==========================================================

    def _thresholds(
        self,
        *,
        governance_drift_score: float,
        sovereignty_pressure_score: float,
        continuity_fragmentation_score: float,
        escalation_failure_score: float,
    ) -> List[
        AdaptiveThreshold
    ]:

        threshold_map = {
            "governance_threshold": (
                governance_drift_score
            ),
            "sovereignty_threshold": (
                sovereignty_pressure_score
            ),
            "continuity_threshold": (
                continuity_fragmentation_score
            ),
            "escalation_threshold": (
                escalation_failure_score
            ),
        }

        thresholds = []

        for (
            name,
            score,
        ) in threshold_map.items():

            previous = 75.0

            adapted = max(
                40.0,
                min(
                    95.0,
                    previous
                    - (score * 0.10),
                ),
            )

            thresholds.append(
                AdaptiveThreshold(
                    threshold_id=str(
                        uuid.uuid4()
                    ),
                    threshold_name=name,
                    previous_value=(
                        previous
                    ),
                    adapted_value=(
                        adapted
                    ),
                    adaptation_delta=(
                        adapted
                        - previous
                    ),
                    rationale=(
                        f"Adaptive "
                        f"threshold "
                        f"{name} recalibrated."
                    ),
                )
            )

        return thresholds

    # ==========================================================
    # STRATEGIC ADAPTATIONS
    # ==========================================================

    def _strategic_adaptations(
        self,
        *,
        learning_state: str,
        optimization_opportunity_score: float,
    ) -> List[
        StrategicAdaptation
    ]:

        adaptations = []

        if learning_state in {
            LEARNING_STATE_ADAPTING,
            LEARNING_STATE_RECALIBRATING,
        }:

            adaptations.append(
                StrategicAdaptation(
                    adaptation_id=str(
                        uuid.uuid4()
                    ),
                    adaptation_name=(
                        "RECALIBRATE_ORCHESTRATION"
                    ),
                    priority="HIGH",
                    expected_improvement_score=(
                        optimization_opportunity_score
                    ),
                    rationale=(
                        "Adaptive "
                        "orchestration "
                        "recalibration required."
                    ),
                )
            )

        if learning_state in {
            LEARNING_STATE_RESILIENCE_PRESSURE,
            LEARNING_STATE_SURVIVABILITY_DEGRADATION,
        }:

            adaptations.append(
                StrategicAdaptation(
                    adaptation_id=str(
                        uuid.uuid4()
                    ),
                    adaptation_name=(
                        "INCREASE_RESILIENCE_PRIORITY"
                    ),
                    priority="CRITICAL",
                    expected_improvement_score=90.0,
                    rationale=(
                        "Resilience "
                        "prioritization required."
                    ),
                )
            )

        if not adaptations:

            adaptations.append(
                StrategicAdaptation(
                    adaptation_id=str(
                        uuid.uuid4()
                    ),
                    adaptation_name=(
                        "MAINTAIN_OPTIMAL_STRATEGY"
                    ),
                    priority="LOW",
                    expected_improvement_score=95.0,
                    rationale=(
                        "Operational "
                        "optimization stable."
                    ),
                )
            )

        return adaptations

    # ==========================================================
    # PROJECTION
    # ==========================================================

    def _projection(
        self,
        *,
        learning_state: str,
        learning_result: str,
        governance_success_score: float,
        survivability_success_score: float,
        recovery_success_score: float,
        resilience_success_score: float,
    ) -> AdaptiveProjection:

        return AdaptiveProjection(
            projection_id=str(
                uuid.uuid4()
            ),
            projected_state=(
                learning_state
            ),
            learning_result=(
                learning_result
            ),
            governance_projection_score=(
                governance_success_score
            ),
            survivability_projection_score=(
                survivability_success_score
            ),
            recovery_projection_score=(
                recovery_success_score
            ),
            resilience_projection_score=(
                resilience_success_score
            ),
            rationale=(
                "Adaptive learning "
                "projection generated."
            ),
        )

    # ==========================================================
    # FORECAST
    # ==========================================================

    def _forecast_steps(
        self,
        *,
        learning_state: str,
        learning_result: str,
        adaptive_optimization_score: float,
        governance_success_score: float,
        survivability_success_score: float,
        recovery_success_score: float,
        resilience_success_score: float,
        depth: int,
    ) -> List[
        AdaptiveForecastStep
    ]:

        steps = []

        for idx in range(
            max(1, int(depth))
        ):

            steps.append(
                AdaptiveForecastStep(
                    step_id=str(
                        uuid.uuid4()
                    ),
                    step_index=idx,
                    learning_state=(
                        learning_state
                    ),
                    learning_result=(
                        learning_result
                    ),
                    optimization_score=(
                        adaptive_optimization_score
                    ),
                    governance_score=(
                        governance_success_score
                    ),
                    survivability_score=(
                        survivability_success_score
                    ),
                    recovery_score=(
                        recovery_success_score
                    ),
                    resilience_score=(
                        resilience_success_score
                    ),
                    rationale=(
                        f"Adaptive "
                        f"forecast step "
                        f"{idx}."
                    ),
                )
            )

            adaptive_optimization_score = (
                self._clamp_score(
                    adaptive_optimization_score
                    + 0.5
                )
            )

            governance_success_score = (
                self._clamp_score(
                    governance_success_score
                    + 0.5
                )
            )

            survivability_success_score = (
                self._clamp_score(
                    survivability_success_score
                    + 0.5
                )
            )

            recovery_success_score = (
                self._clamp_score(
                    recovery_success_score
                    + 0.5
                )
            )

            resilience_success_score = (
                self._clamp_score(
                    resilience_success_score
                    + 0.5
                )
            )

        return steps

    # ==========================================================
    # RECORDING
    # ==========================================================

    def _record_assessment(
        self,
        assessment: (
            SovereignAdaptiveLearningAssessment
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
            "type": (
                "SOVEREIGN_ADAPTIVE_LEARNING"
            ),
            "assessment": asdict(
                assessment
            ),
            "context": (
                context or {}
            ),
        }

        self._write_memory(payload)

        self._write_lineage(payload)

        self._write_evidence(payload)

        self._emit_event(payload)

    def _write_memory(
        self,
        payload: Dict[str, Any],
    ) -> None:

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
                f"⚠️ Adaptive "
                f"memory write failed: "
                f"{exc}"
            )

    def _write_lineage(
        self,
        payload: Dict[str, Any],
    ) -> None:

        try:

            if (
                self.lineage_engine
                and hasattr(
                    self.lineage_engine,
                    "record_lineage",
                )
            ):
                self.lineage_engine.record_lineage(
                    payload
                )

        except Exception as exc:

            print(
                f"⚠️ Adaptive "
                f"lineage write failed: "
                f"{exc}"
            )

    def _write_evidence(
        self,
        payload: Dict[str, Any],
    ) -> None:

        try:

            if (
                self.fedramp_evidence_lineage_engine
                and hasattr(
                    self
                    .fedramp_evidence_lineage_engine,
                    "record_evidence",
                )
            ):
                self.fedramp_evidence_lineage_engine.record_evidence(
                    payload
                )

        except Exception as exc:

            print(
                f"⚠️ Adaptive "
                f"evidence write failed: "
                f"{exc}"
            )

    def _emit_event(
        self,
        payload: Dict[str, Any],
    ) -> None:

        try:

            if (
                self.event_bus
                and hasattr(
                    self.event_bus,
                    "emit",
                )
            ):
                self.event_bus.emit(
                    "SOVEREIGN_ADAPTIVE_LEARNING",
                    payload,
                )

        except Exception as exc:

            print(
                f"⚠️ Adaptive "
                f"event emit failed: "
                f"{exc}"
            )

    # ==========================================================
    # HELPERS
    # ==========================================================

    def _normalize_signal(
        self,
        item: (
            AdaptiveLearningSignal
            | Dict[str, Any]
        ),
        *,
        tenant_id: Optional[str],
        mission_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> AdaptiveLearningSignal:

        if isinstance(
            item,
            AdaptiveLearningSignal,
        ):
            return item

        return AdaptiveLearningSignal(
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
            severity=self._safe_severity(
                item.get("severity")
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
            orchestration_success_score=self._clamp_score(
                item.get(
                    "orchestration_success_score",
                    100.0,
                )
            ),
            governance_success_score=self._clamp_score(
                item.get(
                    "governance_success_score",
                    100.0,
                )
            ),
            verification_success_score=self._clamp_score(
                item.get(
                    "verification_success_score",
                    100.0,
                )
            ),
            survivability_success_score=self._clamp_score(
                item.get(
                    "survivability_success_score",
                    100.0,
                )
            ),
            recovery_success_score=self._clamp_score(
                item.get(
                    "recovery_success_score",
                    100.0,
                )
            ),
            resilience_success_score=self._clamp_score(
                item.get(
                    "resilience_success_score",
                    100.0,
                )
            ),
            escalation_failure_score=self._clamp_score(
                item.get(
                    "escalation_failure_score",
                    0.0,
                )
            ),
            continuity_fragmentation_score=self._clamp_score(
                item.get(
                    "continuity_fragmentation_score",
                    0.0,
                )
            ),
            sovereignty_pressure_score=self._clamp_score(
                item.get(
                    "sovereignty_pressure_score",
                    0.0,
                )
            ),
            governance_drift_score=self._clamp_score(
                item.get(
                    "governance_drift_score",
                    0.0,
                )
            ),
            blast_radius_score=self._clamp_score(
                item.get(
                    "blast_radius_score",
                    0.0,
                )
            ),
            autonomy_pressure_score=self._clamp_score(
                item.get(
                    "autonomy_pressure_score",
                    0.0,
                )
            ),
            uncertainty_score=self._clamp_score(
                item.get(
                    "uncertainty_score",
                    0.0,
                )
            ),
            optimization_opportunity_score=self._clamp_score(
                item.get(
                    "optimization_opportunity_score",
                    0.0,
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
        tenant_id: Optional[str],
        mission_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> (
        SovereignAdaptiveLearningAssessment
    ):

        projection = (
            AdaptiveProjection(
                projection_id=str(
                    uuid.uuid4()
                ),
                projected_state=(
                    LEARNING_STATE_OPTIMAL
                ),
                learning_result=(
                    LEARNING_RESULT_OPTIMIZED
                ),
                governance_projection_score=100.0,
                survivability_projection_score=100.0,
                recovery_projection_score=100.0,
                resilience_projection_score=100.0,
                rationale=(
                    "No adaptive "
                    "signals submitted."
                ),
            )
        )

        return (
            SovereignAdaptiveLearningAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                learning_state=(
                    LEARNING_STATE_OPTIMAL
                ),
                learning_result=(
                    LEARNING_RESULT_OPTIMIZED
                ),
                orchestration_success_score=100.0,
                governance_success_score=100.0,
                verification_success_score=100.0,
                survivability_success_score=100.0,
                recovery_success_score=100.0,
                resilience_success_score=100.0,
                escalation_failure_score=0.0,
                continuity_fragmentation_score=0.0,
                sovereignty_pressure_score=0.0,
                governance_drift_score=0.0,
                blast_radius_score=0.0,
                autonomy_pressure_score=0.0,
                uncertainty_score=0.0,
                optimization_opportunity_score=100.0,
                adaptive_optimization_score=100.0,
                learning_confidence=1.0,
                systemic_risk_probability=0.0,
                confidence=1.0,
                explainability_score=100.0,
                signal_count=0,
                engine_count=0,
                severity=(
                    LearningSeverity.INFO.value
                ),
                tenant_id=tenant_id,
                mission_id=mission_id,
                case_id=case_id,
                correlation_id=(
                    correlation_id
                ),
                thresholds=[],
                strategic_adaptations=[],
                strategic_projection=(
                    projection
                ),
                forecast_steps=[],
                telemetry_fusion={},
                rationale=(
                    "No adaptive "
                    "signals submitted."
                ),
                metadata={},
            )
        )

    def _select_primary_signal(
        self,
        signals: Sequence[
            AdaptiveLearningSignal
        ],
    ) -> AdaptiveLearningSignal:

        return sorted(
            signals,
            key=lambda item: (
                item
                .optimization_opportunity_score,
                item
                .governance_drift_score,
                item
                .sovereignty_pressure_score,
                -item.created_at_ms,
            ),
            reverse=True,
        )[0]

    def _telemetry_fusion(
        self,
        signals: Sequence[
            AdaptiveLearningSignal
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

    def _confidence(
        self,
        signals: Sequence[
            AdaptiveLearningSignal
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
            AdaptiveLearningSignal
        ],
    ) -> float:

        if not signals:
            return 0.0

        explained = 0

        for signal in signals:

            if signal.summary:
                explained += 1

            if signal.source_engine:
                explained += 1

            if signal.payload:
                explained += 1

        return self._clamp_score(
            (
                explained
                / (len(signals) * 3)
            )
            * 100.0
        )

    @staticmethod
    def _rationale(
        *,
        learning_state: str,
        learning_result: str,
        adaptive_optimization_score: float,
    ) -> str:

        return (
            f"Sovereign adaptive "
            f"learning completed. "
            f"Learning state "
            f"{learning_state}; "
            f"learning result "
            f"{learning_result}; "
            f"optimization score "
            f"{adaptive_optimization_score:.2f}."
        )

    @staticmethod
    def _safe_severity(
        value: Any,
    ) -> str:

        value = str(
            value
            or LearningSeverity.INFO.value
        ).upper()

        valid = {
            item.value
            for item in LearningSeverity
        }

        return (
            value
            if value in valid
            else LearningSeverity.INFO.value
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


def build_sovereign_adaptive_learning_engine(
    *,
    event_bus: Optional[Any] = None,
    execution_verification_engine: Optional[
        Any
    ] = None,
    execution_governance_engine: Optional[
        Any
    ] = None,
    orchestration_engine: Optional[Any] = None,
    operational_memory_engine: Optional[
        Any
    ] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: Optional[
        Any
    ] = None,
) -> (
    SovereignAdaptiveLearningEngine
):

    return (
        SovereignAdaptiveLearningEngine(
            event_bus=event_bus,
            execution_verification_engine=(
                execution_verification_engine
            ),
            execution_governance_engine=(
                execution_governance_engine
            ),
            orchestration_engine=(
                orchestration_engine
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