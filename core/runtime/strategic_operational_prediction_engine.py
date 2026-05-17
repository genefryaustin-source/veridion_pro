"""
core/runtime/strategic_operational_prediction_engine.py

Strategic Operational Prediction Engine

Predictive sovereign operational cognition layer.

This subsystem predicts:
- runtime destabilization
- infrastructure degradation
- survivability decline
- governance saturation
- failover amplification
- retry storms
- verification collapse
- autonomy destabilization
- recovery probability
- tenant operational risk evolution

IMPORTANT:
This subsystem DOES NOT:
- directly mutate runtime state
- directly execute infrastructure actions
- directly downgrade autonomy
- directly quarantine connectors/tenants
- directly trigger failovers

It ONLY:
- predicts operational outcomes
- evaluates future risk trajectories
- models destabilization probability
- models survivability probability
- models governance overload probability
- emits replayable predictive lineage/evidence
"""

from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence


# ============================================================
# CONSTANTS
# ============================================================

DEFAULT_ENGINE_NAME = (
    "strategic_operational_prediction_engine"
)

PREDICTION_STATE_STABLE = "STABLE"
PREDICTION_STATE_ELEVATED = "ELEVATED"
PREDICTION_STATE_DEGRADED = "DEGRADED"
PREDICTION_STATE_CRITICAL = "CRITICAL"
PREDICTION_STATE_COLLAPSE_RISK = (
    "COLLAPSE_RISK"
)

RECOVERY_FORECAST_LIKELY = "LIKELY"
RECOVERY_FORECAST_UNCERTAIN = (
    "UNCERTAIN"
)
RECOVERY_FORECAST_UNLIKELY = (
    "UNLIKELY"
)
RECOVERY_FORECAST_FAILED = "FAILED"

RECOMMENDATION_NONE = "NONE"
RECOMMENDATION_PREDICTIVE_REVIEW = (
    "PREDICTIVE_REVIEW"
)
RECOMMENDATION_AUTONOMY_REDUCTION = (
    "AUTONOMY_REDUCTION"
)
RECOMMENDATION_STABILIZATION_PREP = (
    "STABILIZATION_PREP"
)
RECOMMENDATION_GOVERNANCE_PREP = (
    "GOVERNANCE_PREP"
)
RECOMMENDATION_FAILOVER_PREP = (
    "FAILOVER_PREP"
)
RECOMMENDATION_TENANT_ISOLATION = (
    "TENANT_ISOLATION"
)
RECOMMENDATION_INFRASTRUCTURE_ESCALATION = (
    "INFRASTRUCTURE_ESCALATION"
)

AUTONOMY_MANUAL = "MANUAL"
AUTONOMY_ASSISTED = "ASSISTED"
AUTONOMY_SUPERVISED_AUTONOMY = (
    "SUPERVISED_AUTONOMY"
)
AUTONOMY_FULL_AUTONOMY = (
    "FULL_AUTONOMY"
)
AUTONOMY_LOCKDOWN = "LOCKDOWN"


# ============================================================
# ENUMS
# ============================================================

class PredictionSignalType(str, Enum):
    RUNTIME_DESTABILIZATION = (
        "RUNTIME_DESTABILIZATION"
    )
    FAILOVER_AMPLIFICATION = (
        "FAILOVER_AMPLIFICATION"
    )
    GOVERNANCE_SATURATION = (
        "GOVERNANCE_SATURATION"
    )
    SURVIVABILITY_DECLINE = (
        "SURVIVABILITY_DECLINE"
    )
    RECOVERY_DEGRADATION = (
        "RECOVERY_DEGRADATION"
    )
    AUTONOMY_DESTABILIZATION = (
        "AUTONOMY_DESTABILIZATION"
    )
    CONNECTOR_COLLAPSE = (
        "CONNECTOR_COLLAPSE"
    )
    RETRY_STORM = "RETRY_STORM"
    VERIFICATION_COLLAPSE = (
        "VERIFICATION_COLLAPSE"
    )
    TENANT_INSTABILITY = (
        "TENANT_INSTABILITY"
    )
    NETWORK_DEGRADATION = (
        "NETWORK_DEGRADATION"
    )
    INFRASTRUCTURE_COLLAPSE = (
        "INFRASTRUCTURE_COLLAPSE"
    )
    UNKNOWN = "UNKNOWN"


class PredictionDomain(str, Enum):
    EXECUTION = "EXECUTION"
    GOVERNANCE = "GOVERNANCE"
    FAILOVER = "FAILOVER"
    VERIFICATION = "VERIFICATION"
    TELEMETRY = "TELEMETRY"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    NETWORK = "NETWORK"
    TENANT = "TENANT"
    AUTONOMY = "AUTONOMY"
    GLOBAL = "GLOBAL"
    UNKNOWN = "UNKNOWN"


class PredictionSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ============================================================
# DATA MODELS
# ============================================================

@dataclass(frozen=True)
class StrategicPredictionSignal:
    """
    Predictive operational telemetry signal.
    """

    prediction_signal_id: str

    signal_type: str
    domain: str

    source_engine: str
    source_system: str

    severity: str
    confidence: float

    summary: str

    tenant_id: Optional[str] = None
    case_id: Optional[str] = None
    correlation_id: Optional[str] = None

    connector_name: Optional[str] = None

    destabilization_probability: float = 0.0
    survivability_decline_probability: (
        float
    ) = 0.0
    governance_overload_probability: (
        float
    ) = 0.0
    failover_amplification_probability: (
        float
    ) = 0.0
    collapse_probability: float = 0.0
    recovery_probability: float = 100.0

    retry_count: int = 0
    failover_count: int = 0
    rollback_count: int = 0
    escalation_count: int = 0

    prediction_confidence_score: (
        float
    ) = 100.0

    current_autonomy_mode: str = (
        AUTONOMY_SUPERVISED_AUTONOMY
    )

    payload: Dict[str, Any] = field(
        default_factory=dict
    )

    created_at_ms: int = field(
        default_factory=lambda: int(
            time.time() * 1000
        )
    )


@dataclass(frozen=True)
class StrategicOperationalPredictionAssessment:
    """
    Deterministic predictive assessment.
    """

    assessment_id: str

    prediction_state: str
    recovery_forecast: str
    recommendation: str

    destabilization_probability: float
    survivability_decline_probability: (
        float
    )
    governance_overload_probability: (
        float
    )
    failover_amplification_probability: (
        float
    )
    collapse_probability: float
    recovery_probability: float

    prediction_confidence_score: (
        float
    )

    systemic_prediction_risk_score: (
        float
    )

    selected_signal_id: Optional[str]
    selected_signal_type: Optional[str]

    domain: str
    severity: str
    confidence: float

    tenant_id: Optional[str]
    case_id: Optional[str]
    correlation_id: Optional[str]

    current_autonomy_mode: str
    recommended_autonomy_mode: str

    recommended_actions: List[
        Dict[str, Any]
    ]

    required_controls: List[str]
    constraints: List[str]

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
class StrategicOperationalPredictionSnapshot:
    """
    Lightweight diagnostics snapshot.
    """

    engine_name: str

    total_signals_seen: int
    total_assessments_created: int

    last_assessment_id: Optional[str]
    last_prediction_state: Optional[str]
    last_prediction_risk_score: (
        Optional[float]
    )

    last_updated_ms: int


# ============================================================
# ENGINE
# ============================================================

class StrategicOperationalPredictionEngine:
    """
    Sovereign predictive operational cognition.
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
            StrategicOperationalPredictionAssessment
        ] = []

    # ========================================================
    # PUBLIC API
    # ========================================================

    def evaluate(
        self,
        signals: Sequence[
            StrategicPredictionSignal
            | Dict[str, Any]
        ],
        *,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        current_autonomy_mode: str = (
            AUTONOMY_SUPERVISED_AUTONOMY
        ),
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> (
        StrategicOperationalPredictionAssessment
    ):
        """
        Evaluate predictive operational posture.
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
                    current_autonomy_mode=(
                        current_autonomy_mode
                    ),
                )
            )

            self._record_assessment(
                assessment,
                context=context,
            )

            return assessment

        selected = (
            self._select_highest_risk_signal(
                normalized
            )
        )

        destabilization_probability = (
            self
            ._destabilization_probability(
                normalized
            )
        )

        survivability_decline_probability = (
            self
            ._survivability_decline_probability(
                normalized
            )
        )

        governance_overload_probability = (
            self
            ._governance_overload_probability(
                normalized
            )
        )

        failover_amplification_probability = (
            self
            ._failover_amplification_probability(
                normalized
            )
        )

        collapse_probability = (
            self._collapse_probability(
                normalized
            )
        )

        recovery_probability = (
            self._recovery_probability(
                normalized
            )
        )

        prediction_confidence_score = (
            self
            ._prediction_confidence_score(
                normalized
            )
        )

        systemic_prediction_risk_score = (
            self
            ._systemic_prediction_risk_score(
                normalized
            )
        )

        prediction_state = (
            self._determine_prediction_state(
                destabilization_probability=(
                    destabilization_probability
                ),
                collapse_probability=(
                    collapse_probability
                ),
                systemic_prediction_risk_score=(
                    systemic_prediction_risk_score
                ),
            )
        )

        recovery_forecast = (
            self._determine_recovery_forecast(
                recovery_probability
            )
        )

        recommendation = (
            self._determine_recommendation(
                selected=selected,
                prediction_state=(
                    prediction_state
                ),
                recovery_forecast=(
                    recovery_forecast
                ),
                systemic_prediction_risk_score=(
                    systemic_prediction_risk_score
                ),
            )
        )

        recommended_autonomy = (
            self._recommended_autonomy_mode(
                current_autonomy_mode,
                recommendation,
            )
        )

        assessment = (
            StrategicOperationalPredictionAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                prediction_state=(
                    prediction_state
                ),
                recovery_forecast=(
                    recovery_forecast
                ),
                recommendation=(
                    recommendation
                ),
                destabilization_probability=(
                    destabilization_probability
                ),
                survivability_decline_probability=(
                    survivability_decline_probability
                ),
                governance_overload_probability=(
                    governance_overload_probability
                ),
                failover_amplification_probability=(
                    failover_amplification_probability
                ),
                collapse_probability=(
                    collapse_probability
                ),
                recovery_probability=(
                    recovery_probability
                ),
                prediction_confidence_score=(
                    prediction_confidence_score
                ),
                systemic_prediction_risk_score=(
                    systemic_prediction_risk_score
                ),
                selected_signal_id=(
                    selected
                    .prediction_signal_id
                ),
                selected_signal_type=(
                    selected.signal_type
                ),
                domain=selected.domain,
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
                current_autonomy_mode=(
                    current_autonomy_mode
                ),
                recommended_autonomy_mode=(
                    recommended_autonomy
                ),
                recommended_actions=(
                    self._recommended_actions(
                        selected,
                        prediction_state,
                        recommendation,
                        recommended_autonomy,
                    )
                ),
                required_controls=(
                    self._required_controls(
                        prediction_state,
                        recommendation,
                    )
                ),
                constraints=self._constraints(
                    selected,
                    prediction_state,
                    recommendation,
                ),
                rationale=self._build_rationale(
                    selected=selected,
                    prediction_state=(
                        prediction_state
                    ),
                    recovery_forecast=(
                        recovery_forecast
                    ),
                    recommendation=(
                        recommendation
                    ),
                    destabilization_probability=(
                        destabilization_probability
                    ),
                    survivability_decline_probability=(
                        survivability_decline_probability
                    ),
                    governance_overload_probability=(
                        governance_overload_probability
                    ),
                    failover_amplification_probability=(
                        failover_amplification_probability
                    ),
                    collapse_probability=(
                        collapse_probability
                    ),
                    recovery_probability=(
                        recovery_probability
                    ),
                    prediction_confidence_score=(
                        prediction_confidence_score
                    ),
                    systemic_prediction_risk_score=(
                        systemic_prediction_risk_score
                    ),
                    signal_count=len(
                        normalized
                    ),
                    recommended_autonomy=(
                        recommended_autonomy
                    ),
                ),
                metadata={
                    "evaluated_signal_ids": [
                        item
                        .prediction_signal_id
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
            StrategicPredictionSignal
            | Dict[str, Any]
        ],
        *,
        tenant_id: Optional[str] = None,
        case_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        current_autonomy_mode: str = (
            AUTONOMY_SUPERVISED_AUTONOMY
        ),
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> (
        StrategicOperationalPredictionAssessment
    ):

        return self.evaluate(
            signals,
            tenant_id=tenant_id,
            case_id=case_id,
            correlation_id=correlation_id,
            current_autonomy_mode=(
                current_autonomy_mode
            ),
            context=context,
        )

    # ========================================================
    # SCORING
    # ========================================================

    def _destabilization_probability(
        self,
        signals: Sequence[
            StrategicPredictionSignal
        ],
    ) -> float:

        total = sum(
            item.destabilization_probability
            for item in signals
        )

        total += (
            sum(
                item.retry_count
                for item in signals
            )
            * 1.0
        )

        return self._clamp_score(
            total / max(1, len(signals))
        )

    def _survivability_decline_probability(
        self,
        signals: Sequence[
            StrategicPredictionSignal
        ],
    ) -> float:

        total = sum(
            item
            .survivability_decline_probability
            for item in signals
        )

        total += (
            sum(
                item.rollback_count
                for item in signals
            )
            * 1.5
        )

        return self._clamp_score(
            total / max(1, len(signals))
        )

    def _governance_overload_probability(
        self,
        signals: Sequence[
            StrategicPredictionSignal
        ],
    ) -> float:

        total = sum(
            item
            .governance_overload_probability
            for item in signals
        )

        total += (
            sum(
                item.escalation_count
                for item in signals
            )
            * 2
        )

        return self._clamp_score(
            total / max(1, len(signals))
        )

    def _failover_amplification_probability(
        self,
        signals: Sequence[
            StrategicPredictionSignal
        ],
    ) -> float:

        total = sum(
            item
            .failover_amplification_probability
            for item in signals
        )

        total += (
            sum(
                item.failover_count
                for item in signals
            )
            * 2
        )

        return self._clamp_score(
            total / max(1, len(signals))
        )

    def _collapse_probability(
        self,
        signals: Sequence[
            StrategicPredictionSignal
        ],
    ) -> float:

        total = sum(
            item.collapse_probability
            for item in signals
        )

        return self._clamp_score(
            total / max(1, len(signals))
        )

    def _recovery_probability(
        self,
        signals: Sequence[
            StrategicPredictionSignal
        ],
    ) -> float:

        total = sum(
            item.recovery_probability
            for item in signals
        )

        total -= (
            sum(
                item.rollback_count
                for item in signals
            )
            * 1.0
        )

        return self._clamp_score(
            total / max(1, len(signals))
        )

    def _prediction_confidence_score(
        self,
        signals: Sequence[
            StrategicPredictionSignal
        ],
    ) -> float:

        total = sum(
            item.prediction_confidence_score
            for item in signals
        )

        return self._clamp_score(
            total / max(1, len(signals))
        )

    def _systemic_prediction_risk_score(
        self,
        signals: Sequence[
            StrategicPredictionSignal
        ],
    ) -> float:

        total = 0.0

        for item in signals:

            total += (
                item.destabilization_probability
            )

            total += (
                item
                .survivability_decline_probability
            )

            total += (
                item
                .governance_overload_probability
            )

            total += (
                item
                .failover_amplification_probability
            )

            total += (
                item.collapse_probability
            )

        return self._clamp_score(
            total / (max(1, len(signals)) * 5)
        )

    # ========================================================
    # DECISIONING
    # ========================================================

    def _determine_prediction_state(
        self,
        *,
        destabilization_probability: float,
        collapse_probability: float,
        systemic_prediction_risk_score: (
            float
        ),
    ) -> str:

        if (
            collapse_probability >= 85
            or systemic_prediction_risk_score
            >= 85
        ):
            return (
                PREDICTION_STATE_COLLAPSE_RISK
            )

        if (
            destabilization_probability >= 70
        ):
            return (
                PREDICTION_STATE_CRITICAL
            )

        if (
            systemic_prediction_risk_score
            >= 60
        ):
            return (
                PREDICTION_STATE_DEGRADED
            )

        if (
            systemic_prediction_risk_score
            >= 30
        ):
            return (
                PREDICTION_STATE_ELEVATED
            )

        return PREDICTION_STATE_STABLE

    def _determine_recovery_forecast(
        self,
        recovery_probability: float,
    ) -> str:

        if recovery_probability >= 85:
            return (
                RECOVERY_FORECAST_LIKELY
            )

        if recovery_probability >= 60:
            return (
                RECOVERY_FORECAST_UNCERTAIN
            )

        if recovery_probability >= 30:
            return (
                RECOVERY_FORECAST_UNLIKELY
            )

        return RECOVERY_FORECAST_FAILED

    def _determine_recommendation(
        self,
        *,
        selected: StrategicPredictionSignal,
        prediction_state: str,
        recovery_forecast: str,
        systemic_prediction_risk_score: (
            float
        ),
    ) -> str:

        if (
            prediction_state
            == PREDICTION_STATE_COLLAPSE_RISK
        ):
            return (
                RECOMMENDATION_STABILIZATION_PREP
            )

        if (
            recovery_forecast
            == RECOVERY_FORECAST_FAILED
        ):
            return (
                RECOMMENDATION_INFRASTRUCTURE_ESCALATION
            )

        if (
            selected.signal_type
            == PredictionSignalType
            .AUTONOMY_DESTABILIZATION.value
        ):
            return (
                RECOMMENDATION_AUTONOMY_REDUCTION
            )

        if (
            selected.signal_type
            == PredictionSignalType
            .GOVERNANCE_SATURATION.value
        ):
            return (
                RECOMMENDATION_GOVERNANCE_PREP
            )

        if (
            selected.signal_type
            == PredictionSignalType
            .FAILOVER_AMPLIFICATION.value
        ):
            return (
                RECOMMENDATION_FAILOVER_PREP
            )

        if (
            selected.signal_type
            == PredictionSignalType
            .TENANT_INSTABILITY.value
        ):
            return (
                RECOMMENDATION_TENANT_ISOLATION
            )

        if systemic_prediction_risk_score >= 60:
            return (
                RECOMMENDATION_PREDICTIVE_REVIEW
            )

        return RECOMMENDATION_NONE

    def _recommended_autonomy_mode(
        self,
        current_autonomy_mode: str,
        recommendation: str,
    ) -> str:

        if recommendation in {
            RECOMMENDATION_STABILIZATION_PREP,
            RECOMMENDATION_INFRASTRUCTURE_ESCALATION,
        }:
            return AUTONOMY_MANUAL

        if recommendation in {
            RECOMMENDATION_AUTONOMY_REDUCTION,
            RECOMMENDATION_PREDICTIVE_REVIEW,
        }:
            return self._reduce_autonomy(
                current_autonomy_mode
            )

        return current_autonomy_mode

    # ========================================================
    # OUTPUT BUILDERS
    # ========================================================

    def _recommended_actions(
        self,
        selected: StrategicPredictionSignal,
        prediction_state: str,
        recommendation: str,
        recommended_autonomy: str,
    ) -> List[Dict[str, Any]]:

        actions: List[
            Dict[str, Any]
        ] = []

        if (
            recommendation
            == RECOMMENDATION_AUTONOMY_REDUCTION
        ):
            actions.append(
                {
                    "action": (
                        "recommend_autonomy_change"
                    ),
                    "to": (
                        recommended_autonomy
                    ),
                }
            )

        if (
            recommendation
            == RECOMMENDATION_STABILIZATION_PREP
        ):
            actions.append(
                {
                    "action": (
                        "prepare_runtime_stabilization"
                    ),
                }
            )

        if (
            recommendation
            == RECOMMENDATION_FAILOVER_PREP
        ):
            actions.append(
                {
                    "action": (
                        "prepare_failover_capacity"
                    ),
                }
            )

        if (
            recommendation
            == RECOMMENDATION_GOVERNANCE_PREP
        ):
            actions.append(
                {
                    "action": (
                        "prepare_governance_capacity"
                    ),
                }
            )

        actions.append(
            {
                "action": (
                    "record_prediction_lineage"
                ),
            }
        )

        actions.append(
            {
                "action": (
                    "record_prediction_evidence"
                ),
            }
        )

        return actions

    def _required_controls(
        self,
        prediction_state: str,
        recommendation: str,
    ) -> List[str]:

        controls: List[str] = []

        if (
            prediction_state
            != PREDICTION_STATE_STABLE
        ):
            controls.append(
                "predictive_review"
            )

        if recommendation in {
            RECOMMENDATION_STABILIZATION_PREP,
            RECOMMENDATION_INFRASTRUCTURE_ESCALATION,
        }:
            controls.append(
                "governance_review"
            )

        controls.append(
            "lineage_recording"
        )

        controls.append(
            "evidence_recording"
        )

        return list(
            dict.fromkeys(controls)
        )

    def _constraints(
        self,
        selected: StrategicPredictionSignal,
        prediction_state: str,
        recommendation: str,
    ) -> List[str]:

        constraints: List[
            str
        ] = []

        constraints.append(
            f"prediction_state_{prediction_state.lower()}"
        )

        if (
            recommendation
            != RECOMMENDATION_NONE
        ):
            constraints.append(
                f"prediction_recommendation_{recommendation.lower()}"
            )

        if (
            selected.failover_count > 10
        ):
            constraints.append(
                "predicted_failover_storm"
            )

        if (
            selected.retry_count > 25
        ):
            constraints.append(
                "predicted_retry_amplification"
            )

        return list(
            dict.fromkeys(constraints)
        )

    def _build_rationale(
        self,
        *,
        selected: StrategicPredictionSignal,
        prediction_state: str,
        recovery_forecast: str,
        recommendation: str,
        destabilization_probability: float,
        survivability_decline_probability: (
            float
        ),
        governance_overload_probability: (
            float
        ),
        failover_amplification_probability: (
            float
        ),
        collapse_probability: float,
        recovery_probability: float,
        prediction_confidence_score: (
            float
        ),
        systemic_prediction_risk_score: (
            float
        ),
        signal_count: int,
        recommended_autonomy: str,
    ) -> str:

        return (
            f"Strategic operational prediction "
            f"assessment. Selected signal "
            f"{selected.signal_type} from "
            f"{selected.source_engine}. "
            f"Destabilization probability "
            f"{destabilization_probability:.2f}; "
            f"survivability decline probability "
            f"{survivability_decline_probability:.2f}; "
            f"governance overload probability "
            f"{governance_overload_probability:.2f}; "
            f"failover amplification probability "
            f"{failover_amplification_probability:.2f}; "
            f"collapse probability "
            f"{collapse_probability:.2f}; "
            f"recovery probability "
            f"{recovery_probability:.2f}; "
            f"prediction confidence "
            f"{prediction_confidence_score:.2f}; "
            f"systemic prediction risk "
            f"{systemic_prediction_risk_score:.2f}. "
            f"Prediction state "
            f"{prediction_state}; "
            f"recovery forecast "
            f"{recovery_forecast}; "
            f"recommendation "
            f"{recommendation}; "
            f"recommended autonomy "
            f"{recommended_autonomy}. "
            f"Evaluated across "
            f"{signal_count} signal(s)."
        )

    # ========================================================
    # RECORDING
    # ========================================================

    def _record_assessment(
        self,
        assessment: (
            StrategicOperationalPredictionAssessment
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
            StrategicOperationalPredictionAssessment
        ),
        *,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        memory = (
            self.operational_memory_engine
        )

        if memory is None:
            return

        payload = {
            "type": (
                "STRATEGIC_OPERATIONAL_PREDICTION_ASSESSMENT"
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
                memory,
                "append_memory",
            ):
                memory.append_memory(
                    payload
                )

            elif hasattr(
                memory,
                "record",
            ):
                memory.record(
                    payload
                )

        except Exception as exc:
            print(
                f"⚠️ Prediction memory write failed: {exc}"
            )

    def _write_to_lineage(
        self,
        assessment: (
            StrategicOperationalPredictionAssessment
        ),
        *,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        lineage = self.lineage_engine

        if lineage is None:
            return

        payload = {
            "lineage_type": (
                "PREDICTION"
            ),
            "lineage_status": (
                "RECORDED"
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
            "tenant_id": (
                assessment.tenant_id
            ),
            "case_id": (
                assessment.case_id
            ),
            "correlation_id": (
                assessment.correlation_id
            ),
            "constraints": list(
                assessment.constraints
            ),
            "context": {
                "type": (
                    "STRATEGIC_OPERATIONAL_PREDICTION_ASSESSMENT"
                ),
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
                lineage,
                "record_lineage",
            ):
                lineage.record_lineage(
                    payload
                )

        except Exception as exc:
            print(
                f"⚠️ Prediction lineage write failed: {exc}"
            )

    def _write_to_evidence(
        self,
        assessment: (
            StrategicOperationalPredictionAssessment
        ),
        *,
        context: Optional[
            Dict[str, Any]
        ] = None,
    ) -> None:

        evidence = (
            self
            .fedramp_evidence_lineage_engine
        )

        if evidence is None:
            return

        payload = {
            "evidence_type": (
                "STRATEGIC_PREDICTION"
            ),
            "evidence_status": (
                "RECORDED"
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
            "tenant_id": (
                assessment.tenant_id
            ),
            "case_id": (
                assessment.case_id
            ),
            "correlation_id": (
                assessment.correlation_id
            ),
            "evidence_payload": {
                "type": (
                    "STRATEGIC_OPERATIONAL_PREDICTION_ASSESSMENT"
                ),
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
                evidence,
                "record_evidence",
            ):
                evidence.record_evidence(
                    payload
                )

        except Exception as exc:
            print(
                f"⚠️ Prediction evidence write failed: {exc}"
            )

    def _emit_event(
        self,
        assessment: (
            StrategicOperationalPredictionAssessment
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
                "STRATEGIC_OPERATIONAL_PREDICTION_ASSESSMENT"
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
                        "STRATEGIC_OPERATIONAL_PREDICTION_ASSESSMENT"
                    ),
                    payload,
                )

        except Exception as exc:
            print(
                f"⚠️ Prediction event emit failed: {exc}"
            )

    # ========================================================
    # HELPERS
    # ========================================================

    def _select_highest_risk_signal(
        self,
        signals: Sequence[
            StrategicPredictionSignal
        ],
    ) -> StrategicPredictionSignal:

        return sorted(
            signals,
            key=lambda item: (
                self._severity_weight(
                    item.severity
                ),
                item.collapse_probability,
                item
                .destabilization_probability,
                item
                .governance_overload_probability,
                item
                .failover_amplification_probability,
                -item.created_at_ms,
            ),
            reverse=True,
        )[0]

    def _normalize_signal(
        self,
        item: (
            StrategicPredictionSignal
            | Dict[str, Any]
        ),
        *,
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
    ) -> StrategicPredictionSignal:

        if isinstance(
            item,
            StrategicPredictionSignal,
        ):
            return item

        return StrategicPredictionSignal(
            prediction_signal_id=str(
                item.get(
                    "prediction_signal_id"
                )
                or uuid.uuid4()
            ),
            signal_type=(
                self._safe_signal_type(
                    item.get(
                        "signal_type"
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
            source_system=str(
                item.get(
                    "source_system"
                )
                or "unknown_system"
            ),
            severity=(
                self._safe_severity(
                    item.get(
                        "severity"
                    )
                )
            ),
            confidence=(
                self._clamp_confidence(
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
            connector_name=item.get(
                "connector_name"
            ),
            destabilization_probability=(
                self._clamp_score(
                    item.get(
                        "destabilization_probability",
                        0.0,
                    )
                )
            ),
            survivability_decline_probability=(
                self._clamp_score(
                    item.get(
                        "survivability_decline_probability",
                        0.0,
                    )
                )
            ),
            governance_overload_probability=(
                self._clamp_score(
                    item.get(
                        "governance_overload_probability",
                        0.0,
                    )
                )
            ),
            failover_amplification_probability=(
                self._clamp_score(
                    item.get(
                        "failover_amplification_probability",
                        0.0,
                    )
                )
            ),
            collapse_probability=(
                self._clamp_score(
                    item.get(
                        "collapse_probability",
                        0.0,
                    )
                )
            ),
            recovery_probability=(
                self._clamp_score(
                    item.get(
                        "recovery_probability",
                        100.0,
                    )
                )
            ),
            retry_count=max(
                0,
                int(
                    item.get(
                        "retry_count",
                        0,
                    )
                    or 0
                ),
            ),
            failover_count=max(
                0,
                int(
                    item.get(
                        "failover_count",
                        0,
                    )
                    or 0
                ),
            ),
            rollback_count=max(
                0,
                int(
                    item.get(
                        "rollback_count",
                        0,
                    )
                    or 0
                ),
            ),
            escalation_count=max(
                0,
                int(
                    item.get(
                        "escalation_count",
                        0,
                    )
                    or 0
                ),
            ),
            prediction_confidence_score=(
                self._clamp_score(
                    item.get(
                        "prediction_confidence_score",
                        100.0,
                    )
                )
            ),
            current_autonomy_mode=(
                self._safe_autonomy_mode(
                    item.get(
                        "current_autonomy_mode"
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
        tenant_id: Optional[str],
        case_id: Optional[str],
        correlation_id: Optional[str],
        current_autonomy_mode: str,
    ) -> (
        StrategicOperationalPredictionAssessment
    ):

        return (
            StrategicOperationalPredictionAssessment(
                assessment_id=str(
                    uuid.uuid4()
                ),
                prediction_state=(
                    PREDICTION_STATE_STABLE
                ),
                recovery_forecast=(
                    RECOVERY_FORECAST_LIKELY
                ),
                recommendation=(
                    RECOMMENDATION_NONE
                ),
                destabilization_probability=0.0,
                survivability_decline_probability=0.0,
                governance_overload_probability=0.0,
                failover_amplification_probability=0.0,
                collapse_probability=0.0,
                recovery_probability=100.0,
                prediction_confidence_score=100.0,
                systemic_prediction_risk_score=0.0,
                selected_signal_id=None,
                selected_signal_type=None,
                domain=(
                    PredictionDomain
                    .UNKNOWN.value
                ),
                severity=(
                    PredictionSeverity
                    .INFO.value
                ),
                confidence=1.0,
                tenant_id=tenant_id,
                case_id=case_id,
                correlation_id=correlation_id,
                current_autonomy_mode=(
                    current_autonomy_mode
                ),
                recommended_autonomy_mode=(
                    current_autonomy_mode
                ),
                recommended_actions=[
                    {
                        "action": (
                            "continue_runtime_operations"
                        ),
                    }
                ],
                required_controls=[
                    "lineage_recording",
                    "evidence_recording",
                ],
                constraints=[],
                rationale=(
                    "No predictive signals were submitted."
                ),
                metadata={},
            )
        )

    @staticmethod
    def _safe_signal_type(
        value: Any,
    ) -> str:

        value = str(
            value
            or PredictionSignalType
            .UNKNOWN.value
        ).upper()

        valid = {
            item.value
            for item in (
                PredictionSignalType
            )
        }

        return (
            value
            if value in valid
            else (
                PredictionSignalType
                .UNKNOWN.value
            )
        )

    @staticmethod
    def _safe_domain(
        value: Any,
    ) -> str:

        value = str(
            value
            or PredictionDomain
            .UNKNOWN.value
        ).upper()

        valid = {
            item.value
            for item in (
                PredictionDomain
            )
        }

        return (
            value
            if value in valid
            else (
                PredictionDomain
                .UNKNOWN.value
            )
        )

    @staticmethod
    def _safe_severity(
        value: Any,
    ) -> str:

        value = str(
            value
            or PredictionSeverity
            .INFO.value
        ).upper()

        valid = {
            item.value
            for item in (
                PredictionSeverity
            )
        }

        return (
            value
            if value in valid
            else (
                PredictionSeverity
                .INFO.value
            )
        )

    @staticmethod
    def _safe_autonomy_mode(
        value: Any,
    ) -> str:

        value = str(
            value
            or AUTONOMY_SUPERVISED_AUTONOMY
        ).upper()

        valid = {
            AUTONOMY_MANUAL,
            AUTONOMY_ASSISTED,
            AUTONOMY_SUPERVISED_AUTONOMY,
            AUTONOMY_FULL_AUTONOMY,
            AUTONOMY_LOCKDOWN,
        }

        return (
            value
            if value in valid
            else AUTONOMY_SUPERVISED_AUTONOMY
        )

    @staticmethod
    def _clamp_confidence(
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
    def _severity_weight(
        severity: str,
    ) -> int:

        return {
            PredictionSeverity
            .INFO.value: 0,
            PredictionSeverity
            .LOW.value: 1,
            PredictionSeverity
            .MEDIUM.value: 2,
            PredictionSeverity
            .HIGH.value: 3,
            PredictionSeverity
            .CRITICAL.value: 4,
        }.get(
            str(severity).upper(),
            0,
        )

    @staticmethod
    def _reduce_autonomy(
        current: str,
    ) -> str:

        current = str(
            current
            or AUTONOMY_SUPERVISED_AUTONOMY
        ).upper()

        order = [
            AUTONOMY_LOCKDOWN,
            AUTONOMY_MANUAL,
            AUTONOMY_ASSISTED,
            AUTONOMY_SUPERVISED_AUTONOMY,
            AUTONOMY_FULL_AUTONOMY,
        ]

        if current not in order:
            return AUTONOMY_ASSISTED

        idx = order.index(current)

        return order[
            max(0, idx - 1)
        ]


# ============================================================
# FACTORY
# ============================================================

def build_strategic_operational_prediction_engine(
    *,
    event_bus: Optional[Any] = None,
    operational_memory_engine: Optional[
        Any
    ] = None,
    lineage_engine: Optional[Any] = None,
    fedramp_evidence_lineage_engine: (
        Optional[Any]
    ) = None,
) -> StrategicOperationalPredictionEngine:
    """
    Factory for explicit dependency injection.
    """

    return (
        StrategicOperationalPredictionEngine(
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